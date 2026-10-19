import json
import numpy as np
import pytest
from check_same_run import compare, reconstruct


def fixture(run):
    raw = run / 'raw-router'
    api = run / 'verification'
    raw.mkdir()
    api.mkdir()
    expected = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dtype=np.int32)
    for rank in range(2):
        stem = raw / f'dp0-tp{rank}-step000001'
        meta = dict(dp=0, tp=rank, tp_size=2, step=1, request_ids=['cmpl-test-0'],
                    starts=[0], boundaries=[0, 2],
                    slots=[dict(layer=i, method='ALLTOALL') for i in range(2)])
        stem.with_suffix('.json').write_text(json.dumps(meta))
        arrays = {'captured': expected.copy()}
        for layer in range(2):
            arrays[f'raw_{layer}'] = expected[rank:rank+1, layer]
            arrays[f'tags_{layer}'] = np.array([[1, 1, rank+1]])
        np.savez(stem.with_suffix('.npz'), **arrays)
    (api / 'case.response.json').write_text(json.dumps(dict(id='cmpl-test', usage={'prompt_tokens':1}, choices=[{'token_ids':[10,11]}])))
    np.save(api / 'case.npy', expected)
    return expected


def test_sharded_router_to_capture_and_api(tmp_path):
    fixture(tmp_path)
    report = compare(tmp_path)
    assert report['status'] == 'PASS'
    assert report['api_elements'] == 8
    assert report['worker_elements'] == 16


def test_capture_row_swap_is_detected(tmp_path):
    fixture(tmp_path)
    path = tmp_path / 'raw-router/dp0-tp0-step000001.npz'
    with np.load(path) as old:
        arrays = dict(old)
    arrays['captured'] = arrays['captured'][::-1]
    np.savez(path, **arrays)
    report = compare(tmp_path)
    assert report['status'] == 'FAIL'
    assert any('different elements' in f for f in report['failures'])


def test_final_api_wrong_expert_is_detected(tmp_path):
    expected = fixture(tmp_path)
    expected[1, 1, 1] = 99
    np.save(tmp_path / 'verification/case.npy', expected)
    report = compare(tmp_path)
    assert report['status'] == 'FAIL'
    assert report['api_checks'][0]['first'] == [1, 1, 1]


def test_wrong_dp_token_ownership_is_detected(tmp_path):
    fixture(tmp_path)
    path = tmp_path / 'raw-router/dp0-tp1-step000001.npz'
    with np.load(path) as old:
        arrays = dict(old)
    arrays['tags_0'][0, 0] = 2
    np.savez(path, **arrays)
    report = compare(tmp_path)
    assert report['status'] == 'FAIL'
    assert any('Missing 1 raw token/layer rows' in f for f in report['failures'])


def test_missing_tp_cannot_pass(tmp_path):
    fixture(tmp_path)
    (tmp_path / 'raw-router/dp0-tp1-step000001.json').unlink()
    report = compare(tmp_path)
    assert report['status'] == 'FAIL'
    assert any('Missing TP workers' in f for f in report['failures'])


def test_truncated_api_is_detected(tmp_path):
    expected = fixture(tmp_path)
    np.save(tmp_path / 'verification/case.npy', expected[:1])
    report = compare(tmp_path)
    assert report['status'] == 'FAIL'
    assert any('API token rows 1 != expected 2' in f for f in report['failures'])


def test_internal_padding_is_excluded_using_transported_row_labels(tmp_path):
    fixture(tmp_path)
    for rank in range(2):
        path = tmp_path / f'raw-router/dp0-tp{rank}-step000001'
        meta = json.loads(path.with_suffix('.json').read_text())
        for slot in meta['slots']:
            slot['method'] = 'MC2'
        path.with_suffix('.json').write_text(json.dumps(meta))
        with np.load(path.with_suffix('.npz')) as archive:
            arrays = dict(archive)
        for layer in range(2):
            arrays[f'raw_{layer}'] = np.concatenate([arrays[f'raw_{layer}'], np.full((2, 2), -999)])
            arrays[f'tags_{layer}'] = np.concatenate([arrays[f'tags_{layer}'], np.zeros((2, 3))])
        np.savez(path.with_suffix('.npz'), **arrays)
    report = compare(tmp_path)
    assert report['status'] == 'PASS'
    assert report['internal_padding_observed'] is True
