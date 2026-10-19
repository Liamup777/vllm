import json
import unittest

from capture_expectations import LAYOUT, SELECTION, audit_expectations, expected_layout, expected_method


class AcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.plan = dict(dp=1, tp=2, sp=False, ep=False, ep_world=2, lora=False,
                         fused=0, policy="FUSED_OR_CAPACITY", capacity=16, experts=128, topk=8)

    def trace(self, method="ALLGATHER", ranges=None):
        lines = []
        for rank in (0, 1):
            selection = dict(dp=0, tp=rank, policy=self.plan["policy"], tokens=5, capacity=16,
                             ep=False, ep_world=2, lora=False, fused=0, method=method, draft=False)
            layout = dict(dp=0, tp=rank, sp=False, method=method,
                          prepare="PrepareAndFinalizeWithAllGather", layer="model.layers.0.mlp.experts",
                          before_rows=5, router_rows=5, dp_tokens=[5], dp_local_sizes=None,
                          padded_rows=6, shards=[], ranges=ranges or [[0, 5]], gather=False, graph="NONE")
            lines.extend([SELECTION + json.dumps(selection), LAYOUT + json.dumps(layout)])
        return "\n".join(lines)

    def test_allgather_without_ep_passes_independent_rules(self):
        result = audit_expectations(self.trace(), self.plan)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["coverage_missing"], [])
        self.assertEqual(result["layout_events"], 2)

    def test_wrong_selection_fails_even_if_requested_branch_observed(self):
        self.assertTrue(audit_expectations(self.trace(method="MC2"), self.plan)["errors"])

    def test_wrong_range_fails_even_if_capture_would_agree(self):
        self.assertTrue(audit_expectations(self.trace(ranges=[[0, 4]]), self.plan)["errors"])

    def test_runtime_configuration_mismatch_fails(self):
        plan = dict(self.plan, ep=True)
        self.assertTrue(audit_expectations(self.trace(), plan)["errors"])

    def test_threshold_inclusive_and_above(self):
        plan = dict(self.plan, ep=True)
        self.assertEqual([expected_method(plan, n, 16) for n in (15, 16, 17)], ["MC2", "MC2", "ALLTOALL"])

    def test_a3_fused_policy_overrides_capacity_on_small_ep_group(self):
        plan = dict(self.plan, ep=True, fused=1)
        self.assertEqual([expected_method(plan, n, 16) for n in (15, 16, 2049)],
                         ["FUSED_MC2", "FUSED_MC2", "FUSED_MC2"])

    def test_uneven_alltoall_shards(self):
        event = dict(method="ALLTOALL", tp=1, dp=0, dp_tokens=[5], before_rows=5)
        self.assertEqual(expected_layout(event, self.plan),
                         ("PrepareAndFinalizeWithAll2All", 2, [3, 2], [[0, 5]]))

    def test_mc2_padding_and_sp_internal_gap(self):
        event = dict(method="MC2", tp=1, dp=0, dp_tokens=[5, 13], before_rows=3, padded_rows=14)
        self.assertEqual(expected_layout(event, dict(self.plan, dp=2, sp=True)),
                         ("PrepareAndFinalizeWithMC2", 7, [7, 7], [[0, 3], [7, 2]]))
        event.update(before_rows=5)
        self.assertEqual(expected_layout(event, dict(self.plan, dp=2)),
                         ("PrepareAndFinalizeWithMC2", 7, [7, 7], [[0, 5]]))

    def test_allgather_dp_offset(self):
        event = dict(method="ALLGATHER", tp=0, dp=1, dp_tokens=[5, 3], before_rows=3)
        self.assertEqual(expected_layout(event, dict(self.plan, dp=2)),
                         ("PrepareAndFinalizeWithAllGather", 10, [], [[5, 3]]))

    def test_missing_trace_and_boundary_never_pass(self):
        self.assertTrue(audit_expectations("", self.plan)["coverage_missing"])
        plan = dict(self.plan, required_selector_tokens=[16])
        self.assertTrue(audit_expectations(self.trace(), plan)["coverage_missing"])

    def test_incomplete_forward_is_not_accepted_as_full_layer_coverage(self):
        plan = dict(self.plan, layers=2)
        result = audit_expectations(self.trace(), plan)
        self.assertTrue(any("Final forward log incomplete" in item for item in result["coverage_missing"]))


if __name__ == "__main__":
    unittest.main()
