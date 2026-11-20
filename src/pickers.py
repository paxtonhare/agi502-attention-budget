"""Selection and post-question state. Only the proof, not the oracle, is fed back."""
from collections import Counter, defaultdict
from itertools import permutations
from random import Random

from src.harness import HARNESS_ECAN_ARMS, KEYWORD_STIMULUS, harness_rank, rank, stimulate_from_harness

ARMS = (
    "ecan", "harness", "random", "ecan_no_feedback", "ecan_no_stimulus", "ecan_neither",
    *HARNESS_ECAN_ARMS,
)


def tokens(*names):
    return frozenset(part for name in names for part in name.casefold().split("_"))


def lexical_index(atoms):
    postings = defaultdict(set)
    for i, atom in enumerate(atoms):
        for word in tokens(*atom[1:-1].split()[2:]):
            postings[word].add(i)
    return postings


def overlap(index, goal, subject):
    return Counter(i for word in tokens(goal, subject) for i in index.get(word, ()))


class Picker:
    def __init__(self, arm, seed, size):
        self.arm = arm
        self.rng = Random(seed + 10_000)
        self.priority = Random(seed + 20_000).sample(range(size), size)
        self.ids = range(size)
        self.sti = [0.0] * size
        self.links = defaultdict(Counter)
        self.seen, self.used = {}, {}

    def pick(self, k, hits, now):
        if self.arm == "random":
            return self.rng.sample(self.ids, k)
        if self.arm == "harness":
            return harness_rank(self.ids, hits, now, self.seen, self.used, self.priority, k)
        if self.arm in HARNESS_ECAN_ARMS:
            stimulate_from_harness(self.sti, self.ids, hits, now, self.seen, self.priority, k)
        elif self.arm in ("ecan", "ecan_no_feedback"):
            for i, count in hits.items():
                self.sti[i] += KEYWORD_STIMULUS * count
        return rank(self.ids, self.sti, self.priority, k)

    def update(self, chosen, proof, now):
        if self.arm == "harness" or self.arm in HARNESS_ECAN_ARMS:
            self.seen.update(dict.fromkeys(chosen, now))
        if self.arm == "harness":
            self.used.update(dict.fromkeys(proof, now))
        elif self.arm != "random":
            self.sti = [0.85 * value for value in self.sti]
            if self.arm in ("ecan", "ecan_no_stimulus", "harness_ecan"):
                for i in proof:
                    self.sti[i] += 3.0
                for i, j in permutations(dict.fromkeys(proof), 2):
                    self.links[i][j] += 1
            balance = self.sti.copy()
            for i, neighbors in self.links.items():
                outgoing = 0.10 * balance[i]
                self.sti[i] -= outgoing
                total = sum(neighbors.values())
                for j, weight in neighbors.items():
                    self.sti[j] += outgoing * weight / total