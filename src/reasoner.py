"""Hyperon adapter. The full corpus is parsed but never inserted into this space."""
from pathlib import Path

from hyperon import MeTTa

ROOT = Path(__file__).resolve().parents[1]


class Reasoner:
    def __init__(self, atoms):
        self.metta = MeTTa()
        self.metta.run((ROOT / "src/chainer.metta").read_text())
        self.space = self.metta.space()
        self.atoms = tuple(map(self.metta.parse_single, atoms))
        self.current = set()

    def prove(self, chosen, goal, subject):
        focus = set(chosen)
        for i in sorted(self.current - focus):
            self.space.remove_atom(self.atoms[i])
        for i in sorted(focus - self.current):
            self.space.add_atom(self.atoms[i])
        self.current = focus
        for depth in (2, 3):
            proofs, = self.metta.run(f"!(chain{depth} {goal} {subject})")
            if proofs:
                return min(tuple(int(str(atom)[1:]) for atom in proof.get_children())
                           for proof in proofs)
        return ()