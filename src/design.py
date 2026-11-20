"""Fixed synthetic corpus and paired question streams (see PLAN.md)."""
from dataclasses import dataclass
from random import Random

TOPICS = (
    ("trail", "permit", "reported", "review", "verified", "note", "photo"),
    ("garden", "grant", "registered", "inspection", "certified", "map", "label"),
    ("archive", "loan", "catalogued", "request", "approved", "scan", "receipt"),
    ("market", "stall", "licensed", "application", "cleared", "invoice", "listing"),
    ("harbor", "berth", "assigned", "screening", "qualified", "log", "survey"),
)
SEEDS = (11, 23, 37, 47, 59)
BUDGETS = (10, 20, 30, 40, 60, 80, 100)
BLOCK_SIZE = 40


@dataclass(frozen=True)
class Corpus:
    atoms: tuple[str, ...]
    topics: tuple[tuple[str, str, tuple[str, ...]], ...]
    proofs: dict[str, tuple[int, ...]]


def corpus():
    rows, topics, templates = [], [], {}
    for topic, *names in TOPICS:
        goal, direct, pending, verified, note, photo = (f"{topic}_{name}" for name in names)
        subjects = tuple(f"{topic}_site_{n:02d}" for n in range(12))
        topics.append((topic, goal, subjects))
        direct_rule = ("edge", direct, goal)
        pending_rule = ("edge", pending, verified)
        verified_rule = ("edge", verified, goal)
        rows.extend((direct_rule, pending_rule, verified_rule, ("edge", note, f"{topic}_archived")))
        for n, subject in enumerate(subjects):
            observation = ("obs", direct if n % 2 == 0 else pending, subject)
            rows.extend((observation, ("obs", note, subject), ("obs", photo, subject)))
            templates[subject] = (observation, direct_rule) if n % 2 == 0 else (
                observation, pending_rule, verified_rule
            )
    Random(502).shuffle(rows)
    ids = {row: i for i, row in enumerate(rows)}
    atoms = tuple(f"({kind} e{i:03d} {a} {b})" for i, (kind, a, b) in enumerate(rows))
    proofs = {subject: tuple(ids[row] for row in proof) for subject, proof in templates.items()}
    return Corpus(atoms, tuple(topics), proofs)


def questions(topics, seed):
    rng = Random(seed)
    decks = [[] for _ in topics]
    for block in range(len(topics)):
        for offset in range(BLOCK_SIZE):
            t = block - 1 if block and offset < 8 and offset % 2 == 0 else block
            topic, goal, subjects = topics[t]
            if not decks[t]:
                decks[t].extend(subjects)
                rng.shuffle(decks[t])
            yield block, topic, goal, decks[t].pop()
