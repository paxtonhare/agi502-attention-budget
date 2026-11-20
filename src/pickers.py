"""Selection and post-question state. Only the proof, not the oracle, is fed back."""
from collections import Counter, defaultdict
from itertools import permutations
from random import Random

ARMS = (
    "ecan", "harness", "random", "ecan_no_feedback", "ecan_no_stimulus", "ecan_neither",
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


def recency(now, last):
    return 0.0 if last is None else 2.0 ** (1 + last - now)


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
            scores = [hits[i] + (0.5 * recency(now, self.used.get(i))
                                 + 0.25 * recency(now, self.seen.get(i))) for i in self.ids]
        else:
            if self.arm in ("ecan", "ecan_no_feedback"):
                for i, count in hits.items():
                    self.sti[i] += 0.25 * count
            scores = self.sti
        return sorted(self.ids, key=lambda i: (-scores[i], self.priority[i]))[:k]

    def update(self, chosen, proof, now):
        if self.arm == "harness":
            self.seen.update(dict.fromkeys(chosen, now))
            self.used.update(dict.fromkeys(proof, now))
        elif self.arm != "random":
            self.sti = [0.85 * value for value in self.sti]
            if self.arm in ("ecan", "ecan_no_stimulus"):
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