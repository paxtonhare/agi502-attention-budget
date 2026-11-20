# AGI 502: Attention under a premise budget

Can an ECAN-style picker give a MeTTa reasoner better premises than lexical retrieval plus recency? See the [fixed protocol](PLAN.md) and [results](RESULTS.md).

## Reproduce

Reference platform: Linux x86-64, CPython 3.11.2 for Hyperon and plots, CPython 3.12.16 for PyMeTTa. Create the environments once:

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
python3.12 -m venv .venv/pymetta
.venv/pymetta/bin/python -m pip install -r requirements-pymetta.txt
```

Then run the whole experiment with one command:

```sh
PYMETTA_PYTHON="$PWD/.venv/pymetta/bin/python" .venv/bin/python run_all.py
```

Omit `PYMETTA_PYTHON` to run Hyperon only. The separate [PyMeTTa environment](outputs/second-interpreter-investigation.txt) avoids mixing engine runtimes. The upstream checks are historical comparisons, not experiment dependencies.

- [`src/`](src): seeded corpus and stream generator, MeTTa bounded joins, scalar MeTTa economy specs and Python orchestration.
- [`tests/`](tests): shared MeTTa `assertEqual` fixtures and Python integration tests.
- [`results/`](results): generated MeTTa KB, five raw CSVs with full focus IDs and proofs, block and overall summary, charts. The ignored `replay.metta` is regenerated from the first observed case of each arm × K × planted proof length × outcome.
- [`outputs/`](outputs): interpreter, test, sweep and upstream logs. Accuracies, focus sets and proof IDs are deterministic. Runtime and chart metadata can vary by machine.
