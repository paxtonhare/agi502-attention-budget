"""Run tests, the fixed sweep, charts and optional second-interpreter replay."""
import os
import subprocess
import sys
from importlib.metadata import version

from hyperon import MeTTa

from src.reasoner import ROOT
from src.report import report
from src.sweep import RESULTS, sweep

OUTPUTS = ROOT / "outputs"


def capture(name, args, **kwargs):
    with (OUTPUTS / f"{name}.txt").open("w") as file:
        subprocess.run(args, cwd=ROOT, stdout=file, stderr=subprocess.STDOUT, check=True, **kwargs)
    print(f"See outputs/{name}.txt")


def metta_tests(replay=False):
    suites = (("chainer", RESULTS / "replay.metta"),) if replay else tuple(
        (name, ROOT / f"tests/{name}.metta") for name in ("chainer", "economy")
    )
    print(f"Hyperon {version('hyperon')}, Python {sys.version.split()[0]}")
    for name, path in suites:
        source = (ROOT / f"src/{name}.metta").read_text() + path.read_text()
        outputs = MeTTa().run(source)
        if len(outputs) != source.count("!(") or any(str(row) != "[()]" for row in outputs):
            raise AssertionError(f"{path.name} failed: {[row for row in outputs if str(row) != '[()]']}")
        print(f"{path.name}: {source.count('!(assertEqual ')} assertEqual passed ({len(outputs)} unit results)")


def main():
    OUTPUTS.mkdir(exist_ok=True)
    capture("python-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    capture("hyperon-tests", [sys.executable, __file__, "--metta-tests"])
    capture("sweep", [sys.executable, "-u", __file__, "--sweep"])
    capture("hyperon-replay", [sys.executable, __file__, "--replay"])
    if os.environ.get("PYMETTA_PYTHON"):
        capture("second-interpreter-run", ["bash", "scripts/second_interpreter.sh", RESULTS / "replay.metta"])
        capture("pymetta-full-replay", [os.environ["PYMETTA_PYTHON"], "scripts/pymetta_replay.py"])
    else:
        print("Set PYMETTA_PYTHON to also regenerate the independent PyMeTTa log.")


if __name__ == "__main__":
    if sys.argv[1:] == ["--metta-tests"]:
        metta_tests()
    elif sys.argv[1:] == ["--replay"]:
        metta_tests(replay=True)
    elif sys.argv[1:] == ["--sweep"]:
        sweep()
        report()
    elif not sys.argv[1:]:
        main()
    else:
        sys.exit("Unknown argument. Use python run_all.py for the full experiment.")
