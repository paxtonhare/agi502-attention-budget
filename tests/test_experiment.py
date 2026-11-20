import unittest
from collections import Counter

from src.design import corpus, questions
from src.pickers import ARMS, Picker, lexical_index, overlap
from src.reasoner import Reasoner


class ExperimentTests(unittest.TestCase):
    def test_every_planted_proof_is_unique_and_necessary(self):
        kb = corpus()
        reasoner = Reasoner(kb.atoms)
        self.assertEqual(len(set(kb.atoms)), 200)
        self.assertEqual(Counter(map(len, kb.proofs.values())), {2: 30, 3: 30})
        for _, goal, subjects in kb.topics:
            for subject in subjects:
                proof = kb.proofs[subject]
                self.assertEqual(reasoner.prove(range(200), goal, subject), proof)
                self.assertEqual(reasoner.prove(proof, goal, subject), proof)
                for entry in proof:
                    self.assertEqual(reasoner.prove(set(proof) - {entry}, goal, subject), ())

    def test_stream_drift_and_matching(self):
        kb = corpus()
        stream = list(questions(kb.topics, 11))
        self.assertEqual(len(stream), 200)
        self.assertEqual(len({q[3] for q in stream[:12]}), 12)
        self.assertEqual([q[1] for q in stream[40:49]], ["trail", "garden"] * 4 + ["garden"])
        _, _, goal, subject = stream[0]
        hits = overlap(lexical_index(kb.atoms), goal, subject)
        obs, *_ = kb.proofs[subject]
        self.assertEqual(sum(v == hits[obs] for v in hits.values()), 3)

    def test_all_pickers_respect_budget_and_reset(self):
        for arm in ARMS:
            a, b = Picker(arm, 11, 20), Picker(arm, 11, 20)
            chosen = a.pick(10, Counter({1: 2, 2: 1}), 0)
            self.assertEqual(chosen, b.pick(10, Counter({1: 2, 2: 1}), 0))
            self.assertEqual(len(set(chosen)), 10)

    def test_harness_prefers_recent_uses_but_not_over_an_extra_keyword(self):
        picker = Picker("harness", 11, 4)
        picker.update([0, 1], [1], 0)
        self.assertEqual(picker.pick(3, Counter({0: 1, 1: 1, 2: 2}), 1), [2, 1, 0])

    def test_feedback_and_snapshot_diffusion(self):
        full = Picker("ecan", 11, 3)
        no_feedback = Picker("ecan_no_feedback", 11, 3)
        for picker in (full, no_feedback):
            picker.sti = [20, 0, 0]
            picker.update([0, 1], [0, 1], 0)
        self.assertEqual(no_feedback.sti, [17, 0, 0])
        self.assertEqual(dict(no_feedback.links), {})
        self.assertEqual(full.links, {0: {1: 1}, 1: {0: 1}})
        self.assertAlmostEqual(full.sti[0], 18.3)
        self.assertAlmostEqual(full.sti[1], 4.7)
        self.assertAlmostEqual(sum(full.sti), 23.0)