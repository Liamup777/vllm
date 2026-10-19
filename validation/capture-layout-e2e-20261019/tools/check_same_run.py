"""Compare same-forward raw router decisions, per-worker capture, and API data.

Reference reconstruction uses transported row labels, never capture_layout,
source_ranges, shard_sizes, or the production capture implementation.
"""
import argparse
from collections import defaultdict, Counter
import json
from pathlib import Path

import numpy as np


def reconstruct(metadata, archives, target_tp):
    """Prefer this worker's raw rows; use sibling TP rows only for missing IDs."""
    target = archives[target_tp]['captured']
    rows, layers, topk = target.shape
    if rows != metadata[target_tp]['boundaries'][-1]:
        raise ValueError('Capture snapshot row count differs from actual input batch')
    expected = np.full((rows, layers, topk), -1, dtype=np.int32)
    seen = np.zeros((rows, layers), dtype=bool)
    owner = metadata[target_tp]['dp'] + 1
    for rank in [target_tp] + sorted(set(archives) - {target_tp}):
        for i, slot in enumerate(metadata[rank]['slots']):
            layer = slot['layer']
            tags = archives[rank][f'tags_{i}']
            raw = archives[rank][f'raw_{i}']
            if tags.shape != (len(raw), 3) or raw.shape[1] != topk:
                raise ValueError('Raw row labels / top-k shape mismatch')
            if not np.all(tags == np.round(tags)):
                raise ValueError('Row labels lost integer precision')
            tags = tags.astype(np.int64)
            for physical, tag in enumerate(tags):
                if tag[0] != owner or tag[1] <= 0 or tag[2] <= 0:
                    continue
                logical = (tag[1] - 1) * 64 + tag[2] - 1
                if logical < rows and not seen[logical, layer]:
                    expected[logical, layer] = raw[physical]
                    seen[logical, layer] = True
    if not seen.all():
        missing = np.argwhere(~seen)
        raise ValueError(f'Missing {len(missing)} raw token/layer rows; first={missing[:5].tolist()}')
    return expected


def compare(run):
    failures, worker_checks, api_checks = [], [], []
    groups = defaultdict(dict)
    for path in sorted((run / 'raw-router').glob('*.json')):
        meta = json.loads(path.read_text())
        groups[(meta['dp'], meta['step'])][meta['tp']] = (meta, path.with_suffix('.npz'))
    by_request = defaultdict(dict)
    methods = Counter()
    uneven_shards = internal_padding = False
    for key, workers in groups.items():
        metadata = {rank: pair[0] for rank, pair in workers.items()}
        archives = {rank: np.load(pair[1], allow_pickle=False) for rank, pair in workers.items()}
        try:
            wanted = metadata[next(iter(metadata))]['tp_size']
            if set(workers) != set(range(wanted)):
                raise ValueError(f'Missing TP workers: {sorted(workers)}, expected={wanted}')
            for layer in range(archives[next(iter(archives))]['captured'].shape[1]):
                lengths, labels = [], []
                method = None
                for rank in sorted(archives):
                    choices = [(i, s) for i, s in enumerate(metadata[rank]['slots']) if s['layer'] == layer]
                    if len(choices) != 1:
                        raise ValueError(f'Expected one active raw capture for layer {layer}, TP{rank}')
                    i, slot = choices[0]
                    method = slot['method']
                    lengths.append(len(archives[rank][f'raw_{i}']))
                    labels.append(archives[rank][f'tags_{i}'])
                uneven_shards |= len(set(lengths)) > 1
                if method in {'MC2', 'FUSED_MC2'}:
                    joined = np.concatenate(labels).astype(np.int64)
                    logical = (joined[:, 1]-1)*64 + joined[:, 2]-1
                    n = metadata[0]['boundaries'][-1]
                    valid = (joined[:, 0] == key[0]+1) & (joined[:, 1] > 0) & (joined[:, 2] > 0) & (logical < n)
                    positions = np.flatnonzero(valid)
                    internal_padding |= bool(np.any(np.diff(positions) > 1))
            for rank, archive in archives.items():
                meta = metadata[rank]
                if any((m['request_ids'], m['starts'], m['boundaries']) !=
                       (meta['request_ids'], meta['starts'], meta['boundaries']) for m in metadata.values()):
                    raise ValueError('TP workers disagree on batch request identities')
                expected = reconstruct(metadata, archives, rank)
                actual = archive['captured']
                mismatch = np.argwhere(expected != actual)
                check = dict(dp=key[0], step=key[1], tp=rank, elements=int(actual.size),
                             status='PASS' if not len(mismatch) else 'FAIL')
                if len(mismatch):
                    at = tuple(mismatch[0])
                    check.update(mismatches=len(mismatch), first=list(map(int, at)),
                                 router=int(expected[at]), captured=int(actual[at]))
                    failures.append(f'worker {key}, TP{rank}: {len(mismatch)} different elements')
                worker_checks.append(check)
                methods.update(slot['method'] for slot in meta['slots'])
                if rank != 0:
                    continue
                for rid, start, a, b in zip(meta['request_ids'], meta['starts'], meta['boundaries'], meta['boundaries'][1:]):
                    for position, row in enumerate(expected[a:b], start):
                        previous = by_request[rid].get(position)
                        if previous is not None and not np.array_equal(previous, row):
                            raise ValueError(f'Conflicting raw reference for {rid}, position={position}')
                        by_request[rid][position] = row.copy()
        except Exception as exc:
            failures.append(f'forward {key}: {exc}')
        finally:
            for archive in archives.values():
                archive.close()
    for response_path in sorted((run / 'verification').glob('*.response.json')):
        case = response_path.name.removesuffix('.response.json')
        try:
            response = json.loads(response_path.read_text())
            rid = response['id']
            matches = [key for key in by_request if key == rid or key.startswith(rid + '-')]
            if len(matches) != 1:
                raise ValueError(f'Cannot uniquely match API {rid} to raw request IDs: {matches}')
            actual = np.load(response_path.with_name(case + '.npy'), allow_pickle=False)
            expected_rows = response['usage']['prompt_tokens'] + len(response['choices'][0]['token_ids']) - 1
            if len(actual) != expected_rows:
                raise ValueError(f'API token rows {len(actual)} != expected {expected_rows}')
            reference_rows = by_request[matches[0]]
            absent = [position for position in range(len(actual)) if position not in reference_rows]
            if absent:
                raise ValueError(f'Missing raw reference token positions: {absent[:10]}')
            expected = np.stack([reference_rows[position] for position in range(len(actual))])
            if actual.shape != expected.shape:
                raise ValueError(f'API shape {actual.shape} != raw reference {expected.shape}')
            mismatch = np.argwhere(expected != actual)
            check = dict(case=case, request_id=rid, shape=list(actual.shape), elements=int(actual.size),
                         status='PASS' if not len(mismatch) else 'FAIL')
            check['samples'] = [dict(token_position=position, layer=layer,
                                      router=expected[position, layer].tolist(),
                                      returned=actual[position, layer].tolist())
                                for position, layer in [(0, 0), (len(actual)-1, actual.shape[1]-1)]]
            if len(mismatch):
                at = tuple(mismatch[0])
                check.update(mismatches=len(mismatch), first=list(map(int, at)),
                             router=int(expected[at]), returned=int(actual[at]))
                failures.append(f'API {case}: {len(mismatch)} different elements')
            api_checks.append(check)
        except Exception as exc:
            failures.append(f'API {case}: {exc}')
    invariants = run / 'verification/report.json'
    if invariants.exists():
        structural = json.loads(invariants.read_text())
        for record in structural.get('requests', []):
            if not record.get('response_validated'):
                failures.append(f'Unvalidated response: {record.get("case")}')
    if not api_checks or not worker_checks:
        failures.append('No complete worker/API comparisons')
    requests = list((run / 'verification').glob('*.response.json'))
    if len(api_checks) != len(requests):
        failures.append(f'Only {len(api_checks)}/{len(requests)} API responses compared')
    report = dict(status='FAIL' if failures else 'PASS', scope='same-forward raw router -> per-worker capture -> final API',
                  worker_checks=worker_checks, api_checks=api_checks, methods=dict(methods), failures=failures,
                  uneven_tp_shards_observed=uneven_shards, internal_padding_observed=internal_padding,
                  worker_elements=sum(c['elements'] for c in worker_checks), api_elements=sum(c['elements'] for c in api_checks))
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    report = compare(args.run)
    (args.run / 'same-run-report.json').write_text(json.dumps(report, indent=2))
    lines = [f'# Same-run capture: {report["status"]}', '',
             f'Worker comparisons: {len(report["worker_checks"])}; elements: {report["worker_elements"]}',
             f'API comparisons: {len(report["api_checks"])}; elements: {report["api_elements"]}', '',
             '| Request | Shape | Elements compared | Result |', '|---|---|---:|---|']
    for check in report['api_checks']:
        lines.append(f'| {check["case"]} | {check["shape"]} | {check["elements"]} | {check["status"]} |')
    sample_case = next((check for check in report['api_checks'] if check['case']=='short-5'), None)
    if sample_case is not None:
        lines += ['', 'Example from the fully compared arrays:', '', '```json',
                  json.dumps({'case':'short-5','samples':sample_case['samples']},indent=2), '```']
    lines += ['', f'Uneven TP shards observed: {report["uneven_tp_shards_observed"]}',
              f'Internal padding observed: {report["internal_padding_observed"]}',
              '', 'Failures:', *report['failures']]
    (args.run / 'same-run-report.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines), flush=True)
    raise SystemExit(bool(report['failures']))


if __name__ == '__main__':
    main()
