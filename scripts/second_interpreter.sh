#!/usr/bin/env bash
# Run the unchanged fixtures and, optionally, a sweep-generated replay on PyMeTTa.
set -euo pipefail
if (( $# > 1 )); then
    printf 'Usage: PYMETTA_PYTHON=path/to/python %s [replay.metta]\n' "$0" >&2
    exit 2
fi
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
python=${PYMETTA_PYTHON:-python3}
if (( $# )) && [[ ! -r $1 ]]; then
    printf 'Cannot read replay: %s\n' "$1" >&2
    exit 2
fi
printf 'PyMeTTa %s\n' "$("$python" -c 'from importlib.metadata import version; print(version("PyMeTTa"))')"
"$python" --version

program=$(mktemp)
trap 'rm -f -- "$program"' EXIT
check() {
    local label=$1 file expected
    shift
    { for file; do tee <"$file"; printf '\n'; done; } >"$program"
    # Shared fixtures and the replay generator put each assertion on its own line.
    expected=$(grep -Ec '^[[:space:]]*!\(assertEqual[[:space:]]' "$program")
    "$python" -m metta run --json=wire - <"$program" | "$python" -c '
import json
import re
import sys

label, expected = sys.argv[1], int(sys.argv[2])
passed = 0
for line in sys.stdin:
    group = json.loads(line)
    if "error" in group:
        sys.exit(label + ": " + group["error"])
    directive = re.match(r"^\((assertEqual|add-atom|remove-atom)\s", group["query"])
    if directive and group["answers"] != [["b", "true"]]:
        sys.exit(f"{label}: unexpected directive result: {group}")
    if directive and directive[1] == "assertEqual":
        passed += 1
if passed != expected:
    sys.exit(f"{label}: observed {passed} passing assertions, expected {expected}")
print(f"{label}: {passed}/{expected} assertions passed")
' "$label" "$expected"
}

check chainer "$root/src/chainer.metta" "$root/tests/chainer.metta"
check economy "$root/src/economy.metta" "$root/tests/economy.metta"
if (( $# )); then
    check replay "$root/src/chainer.metta" "$1"
fi
