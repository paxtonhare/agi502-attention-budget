import unittest
from collections import Counter

from src.harness import HARNESS_ECAN_ARMS
from src.pickers import Picker


class HarnessEcanTests(unittest.TestCase):
    def test_cold_start_stimulates_the_harness_top_k(self):
        for arm in HARNESS_ECAN_ARMS:
            with self.subTest(arm=arm):
                hybrid = Picker(arm, 11, 5)
                harness = Picker("harness", 11, 5)
                hits = Counter({0: 3, 1: 2, 2: 2, 3: 1})
                expected = harness.pick(2, hits, 0)
                self.assertEqual(hybrid.pick(2, hits, 0), expected)
                self.assertEqual(hybrid.sti, [0.25 if i in expected else 0 for i in range(5)])

    def test_nominations_use_focus_exposure_but_sti_selects_the_focus(self):
        for arm in HARNESS_ECAN_ARMS:
            with self.subTest(arm=arm):
                picker = Picker(arm, 11, 3)
                picker.priority = [0, 1, 2]
                self.assertEqual(picker.pick(1, Counter({1: 1}), 0), [1])
                picker.update([1], (), 0)
                picker.sti[2] = 1.0
                self.assertEqual(picker.pick(1, Counter({0: 1, 1: 1}), 1), [2])
                self.assertEqual(picker.sti, [0, 0.85 * 0.25 + 0.25, 1.0])
                picker.update([2], (), 1)
                self.assertEqual(picker.seen, {1: 0, 2: 1})

    def test_no_feedback_ignores_proofs_in_economy_and_retrieval(self):
        control = Picker("harness_ecan_nofeedback", 11, 3)
        no_proof = Picker("harness_ecan_nofeedback", 11, 3)
        full = Picker("harness_ecan", 11, 3)
        for picker in (control, no_proof, full):
            picker.sti[0] = 4.0
            picker.update([0, 1], () if picker is no_proof else (0, 1), 0)
            self.assertEqual(picker.seen, {0: 0, 1: 0})
            self.assertEqual(picker.used, {})
        self.assertEqual(control.sti, [3.4, 0, 0])
        self.assertEqual(control.links, {})
        self.assertEqual(full.links, {0: {1: 1}, 1: {0: 1}})
        self.assertAlmostEqual(full.sti[0], 6.06)
        self.assertAlmostEqual(full.sti[1], 3.34)
        hits = Counter({1: 1, 2: 1})
        self.assertEqual(control.pick(1, hits, 1), no_proof.pick(1, hits, 1))
        self.assertEqual(control.sti, no_proof.sti)
