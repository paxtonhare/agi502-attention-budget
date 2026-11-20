"""Run every fixed condition and capture one raw CSV per paired seed."""
import csv
from collections import Counter
from time import perf_counter

from src.design import BUDGETS, SEEDS, corpus, questions
from src.pickers import ARMS, Picker, lexical_index, overlap
from src.reasoner import ROOT, Reasoner

RESULTS = ROOT / "results"
FIELDS = ("seed", "k", "arm", "question", "block", "topic", "goal", "subject", "correct",
          "proof", "focus", "runtime_us")


def sweep(arms=ARMS):
    kb = corpus()
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "kb.metta").write_text("\n".join(kb.atoms) + "\n")
    index = lexical_index(kb.atoms)
    print(f"KB: {len(kb.atoms)} entries across {len(kb.topics)} topics")
    print("Entry kinds:", dict(Counter(atom.split()[0][1:] for atom in kb.atoms)))
    print("Unique subject proof lengths:", dict(sorted(Counter(map(len, kb.proofs.values())).items())))
    cases = {}
    checked = 0
    for seed in SEEDS:
        stream = list(questions(kb.topics, seed))
        with (RESULTS / f"raw-{seed}.csv").open("w", newline="") as file:
            writer = csv.DictWriter(file, FIELDS)
            writer.writeheader()
            for k in BUDGETS:
                for arm in arms:
                    picker = Picker(arm, seed, len(kb.atoms))
                    reasoner = Reasoner(kb.atoms)
                    for now, (block, topic, goal, subject) in enumerate(stream):
                        start = perf_counter()
                        chosen = picker.pick(k, overlap(index, goal, subject), now)
                        proof = reasoner.prove(chosen, goal, subject)
                        picker.update(chosen, proof, now)
                        elapsed = (perf_counter() - start) * 1_000_000
                        expected = kb.proofs[subject]
                        oracle = expected if set(expected).issubset(chosen) else ()
                        if proof != oracle:
                            raise AssertionError((seed, k, arm, now, proof, oracle))
                        checked += 1
                        focus = tuple(sorted(chosen))
                        writer.writerow(dict(seed=seed, k=k, arm=arm, question=now, block=block,
                                             topic=topic, goal=goal, subject=subject, correct=int(bool(proof)),
                                             proof=" ".join(f"e{i:03d}" for i in proof),
                                             focus=" ".join(f"e{i:03d}" for i in focus),
                                             runtime_us=f"{elapsed:.1f}"))
                        # Reuse the first recorded case for each arm, budget, proof length and outcome.
                        cases.setdefault((k, arm, len(expected), bool(proof)), (focus, goal, subject, proof))
        print(f"Seed {seed}: {len(stream)} questions per condition", flush=True)
    print(f"MeTTa proofs checked against planted proof membership: {checked}")
    replay(kb.atoms, cases.values())


def replay(atoms, cases):
    with (RESULTS / "replay.metta").open("w") as file:
        previous = set()
        for chosen, goal, subject, proof in cases:
            for i in sorted(previous - set(chosen)):
                print(f"!(remove-atom &self {atoms[i]})", file=file)
            for i in sorted(set(chosen) - previous):
                print(f"!(add-atom &self {atoms[i]})", file=file)
            for length in (2, 3):
                expected = "(" + " ".join(f"e{i:03d}" for i in proof) + ")"
                expected = f"({expected})" if len(proof) == length else "()"
                print(f"!(assertEqual (collapse (chain{length} {goal} {subject})) {expected})", file=file)
            previous = set(chosen)
    print(f"Generated replay selections: {len(cases)}")