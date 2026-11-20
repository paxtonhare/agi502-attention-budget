import csv
from collections import Counter
from pathlib import Path
from time import perf_counter
from metta import MeTTa, parse

root = Path.cwd()
results = root / 'results'
chainer = (root / 'src/chainer.metta').read_text()
kb = {line.split()[1]: parse(line) for line in (results / 'kb.metta').read_text().splitlines()}
cases = {}
rows = 0
for data in sorted(results.glob('raw-*.csv')):
    with data.open(newline='') as f:
        for r in csv.DictReader(f):
            key = (tuple(r['focus'].split()), r['goal'], r['subject'])
            expected = tuple(r['proof'].split())
            if cases.setdefault(key, expected) != expected:
                raise ValueError(f'Conflicting recorded proofs: {key}')
            rows += 1

m = MeTTa()
m.run(chainer)
prev = set()
counts = Counter()
start = perf_counter()
for (focus, goal, subject), proof in cases.items():
    chosen = set(focus)
    removed = tuple(kb[i] for i in sorted(prev - chosen))
    if removed and m.remove(*removed) != (True if len(removed) == 1 else len(removed)):
        raise AssertionError(f'Failed to remove {removed}')
    added = tuple(kb[i] for i in sorted(chosen - prev))
    if added:
        m.add(*added)
    prev = chosen
    answer_sets = m.run(f'!(chain2 {goal} {subject})\n!(chain3 {goal} {subject})')
    actual = [[format(term, 'sexp') for term in group] for group in answer_sets]
    expected = [[f'({" ".join(proof)})'] if len(proof) == n else [] for n in (2, 3)]
    if actual != expected:
        raise AssertionError((focus, goal, subject, actual, expected))
    counts[len(proof)] += 1
print(f'Rows: {rows}; unique focus/goal/subject cases: {len(cases)}; matched exact chain2/chain3 answers in {perf_counter() - start:.2f}s')
print(f'Cases by outcome: none={counts[0]}, direct={counts[2]}, two rules={counts[3]}')
