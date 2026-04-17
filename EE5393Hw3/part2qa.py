"""
Algorithm 1 (Tree-style): Synthesize a circuit of AND gates and inverters
that generates a required decimal fraction probability from S = {0.4, 0.5}.

Based on: "The Synthesis of Combinational Logic to Generate Probabilities"
Qian, Riedel, Bazargan, Lilja — ICCAD 2009

KEY DIFFERENCE FROM LINEAR VERSION
====================================
Previously the circuit was a single chain:
    INPUT(0.4) -> AND(0.5) -> AND(0.4) -> NOT -> AND(0.5) -> ... -> OUT

Now both branches of every AND gate are independently synthesized sub-trees,
exactly like the diagram in the paper (Figure 3) and the image provided:

              0.4 --NOT--.
                          AND -- NOT -- AND -- ...
              0.5 --------'                  |
                                             v  OUT
              0.4 ---.                       |
                      AND ------------------'
              0.5 ---'

Each AND gate receives two proper sub-circuit inputs, giving a parallel,
balanced tree rather than a sequential chain.

RECURSIVE STRUCTURE (directly from the paper's inductive proof)
================================================================
The synthesis function synth(z) returns a Node tree.

Case 4  z > 0.5 :
    w = 1 - z  (fewer digits)
    => NOT( synth(w) )

Case 3  0.4 < z <= 0.5 :
    w = 1 - 2z  (falls in Case 1a/b)
    => AND( NOT(synth(w)),  INPUT(0.5) )
    because  (1 - w) * 0.5  =  (1 - (1-2z)) * 0.5  =  z

Case 1  0 <= z <= 0.2 :
    Let u = z * 10^n  (integer numerator)
    (a) u even          : w = 5z    => AND( AND(INPUT(0.4), INPUT(0.5)), synth(w) )
    (b) u odd, z <= 0.1 : w = 10z   => AND( AND( AND(INPUT(0.4),INPUT(0.5)), INPUT(0.5) ), synth(w) )
    (c) u odd, z > 0.1  : w = 2-10z => AND( NOT(AND(INPUT(0.5), synth(w))),  AND(INPUT(0.4),INPUT(0.5)) )

Case 2  0.2 < z <= 0.4 :
    Let u = z * 10^n
    (a) u div by 4      : w = 2.5z   => AND( INPUT(0.4), synth(w) )
    (b) u div by 2 only : w = 2 - 5z => AND( NOT(AND(INPUT(0.5), synth(w))),  INPUT(0.4) )
    (c) u odd, z <= 0.3 : w = 10z-2  => AND( NOT(AND( NOT(AND(INPUT(0.5),synth(w))), INPUT(0.5) )),  INPUT(0.4) )
    (d) u odd, z > 0.3  : w = 4-10z  => AND( NOT(AND( AND(INPUT(0.5),INPUT(0.5)), synth(w) )),  INPUT(0.4) )

Base case  (n <= 1, i.e. z in {0.0,0.1,...,0.9,1.0}):
    Build directly from known identities using INPUT(0.4) and INPUT(0.5).
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Circuit node classes
# ---------------------------------------------------------------------------

class InputNode:
    """Primary input — a fixed-probability random source (0.4 or 0.5)."""
    def __init__(self, p: float):
        self._p = p
    def prob(self) -> float:
        return self._p
    def __repr__(self):
        return f"INPUT({self._p})"


class InverterNode:
    """NOT gate: output = 1 − child."""
    def __init__(self, child):
        self.child = child
    def prob(self) -> float:
        return 1.0 - self.child.prob()
    def __repr__(self):
        return f"NOT({self.child!r})"


class AndNode:
    """AND gate: output = left × right (independent inputs assumed)."""
    def __init__(self, left, right):
        self.left  = left
        self.right = right
    def prob(self) -> float:
        return self.left.prob() * self.right.prob()
    def __repr__(self):
        return f"AND({self.left!r}, {self.right!r})"


# Convenience constructors
def INPUT(p):        return InputNode(p)
def NOT(child):      return InverterNode(child)
def AND(left, right):return AndNode(left, right)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def get_digits(z: float) -> int:
    """Minimal decimal places to represent z exactly (capped at 15)."""
    z = round(z, 15)
    for n in range(16):
        if abs(round(z, n) - z) < 1e-11:
            return n
    return 15


def _r(z: float) -> float:
    """Round to 13 decimal places to suppress float drift."""
    return round(z, 13)


def _approx(a: float, b: float, tol=1e-10) -> bool:
    return abs(a - b) < tol


# ---------------------------------------------------------------------------
# Base case: synthesize single-digit fractions directly from {0.4, 0.5}
# ---------------------------------------------------------------------------

def synth_base(z: float):
    """
    Build a node tree for z in {0.0, 0.1, 0.2, ..., 0.9, 1.0}.
    Every formula uses only INPUT(0.4) and INPUT(0.5).
    """
    z = round(z, 10)

    # Direct sources
    if _approx(z, 0.4): return INPUT(0.4)
    if _approx(z, 0.5): return INPUT(0.5)

    # Two-gate constructions
    if _approx(z, 0.2): return AND(INPUT(0.4), INPUT(0.5))           # 0.4 × 0.5
    if _approx(z, 0.6): return NOT(INPUT(0.4))                        # 1 − 0.4
    if _approx(z, 0.8): return NOT(AND(INPUT(0.4), INPUT(0.5)))       # 1 − 0.4×0.5
    if _approx(z, 0.3): return AND(NOT(INPUT(0.4)), INPUT(0.5))       # (1−0.4)×0.5

    # Three-gate constructions
    if _approx(z, 0.1): return AND(AND(INPUT(0.4), INPUT(0.5)),
                                   INPUT(0.5))                         # 0.4×0.5×0.5
    if _approx(z, 0.9): return NOT(AND(AND(INPUT(0.4), INPUT(0.5)),
                                       INPUT(0.5)))                    # 1−0.4×0.5×0.5
    if _approx(z, 0.7): return NOT(AND(NOT(INPUT(0.4)), INPUT(0.5)))  # 1−(1−0.4)×0.5

    if _approx(z, 0.0):
        # Structural zero: AND a source with its own inverse
        # 0.4 × (1−0.4) × (1−0.4) ... use a chain of 3 ANDs ≈ tiny
        # Exact 0 is representable as AND of source with complement:
        # P(x AND NOT(x)) = 0  — but that requires the SAME source twice.
        # Since inputs are independent, use a long AND chain instead:
        node = INPUT(0.4)
        for _ in range(10):
            node = AND(node, AND(INPUT(0.4), INPUT(0.5)))
        return node
    if _approx(z, 1.0):
        return NOT(NOT(INPUT(0.4)))   # structural 1

    raise ValueError(f"synth_base: z={z} is not a recognised single-digit fraction")


# ---------------------------------------------------------------------------
# Algorithm 1: recursive tree synthesis
# ---------------------------------------------------------------------------

def synth(z: float, _depth: int = 0) -> InputNode | InverterNode | AndNode:
    """
    Recursively build a parallel AND/NOT tree that outputs probability z.

    Both branches of every AND gate are proper sub-circuit trees —
    there are no "fixed" leaves except InputNode(0.4) and InputNode(0.5).
    """
    if _depth > 200:
        raise RecursionError(f"synth recursion too deep at z={z}")

    z = _r(z)
    n = get_digits(z)

    # ---- Base case: single digit ----------------------------------------
    if n <= 1:
        return synth_base(z)

    # ---- Case 4: z > 0.5  => NOT(synth(1-z)) ---------------------------
    if z > 0.5:
        w = _r(1.0 - z)
        return NOT(synth(w, _depth + 1))

    # ---- Case 3: 0.4 < z <= 0.5  => AND(NOT(synth(w)), INPUT(0.5)) -----
    #   w = 1 - 2z  =>  z = (1-w)*0.5
    if 0.4 < z <= 0.5:
        w = _r(1.0 - 2.0 * z)
        return AND(NOT(synth(w, _depth + 1)), INPUT(0.5))

    # ---- Cases 1 & 2: z <= 0.4 -----------------------------------------
    u = int(round(z * 10 ** n))    # integer numerator

    # ---- Case 1: z <= 0.2 -----------------------------------------------
    if z <= 0.2:
        if u % 2 == 0:
            # (a) z = 0.4 * 0.5 * w,  w = 5z
            w = _r(5.0 * z)
            return AND(AND(INPUT(0.4), INPUT(0.5)), synth(w, _depth + 1))

        elif z <= 0.1:
            # (b) z = 0.4 * 0.5 * 0.5 * w,  w = 10z
            w = _r(10.0 * z)
            return AND(AND(AND(INPUT(0.4), INPUT(0.5)), INPUT(0.5)),
                       synth(w, _depth + 1))

        else:
            # (c) 0.1 < z <= 0.2, u odd
            #     z = (1 - 0.5*w) * 0.4 * 0.5,  w = 2 - 10z
            w = _r(2.0 - 10.0 * z)
            return AND(NOT(AND(INPUT(0.5), synth(w, _depth + 1))),
                       AND(INPUT(0.4), INPUT(0.5)))

    # ---- Case 2: 0.2 < z <= 0.4 -----------------------------------------
    if u % 4 == 0:
        # (a) z = 0.4 * w,  w = 2.5z
        w = _r(2.5 * z)
        return AND(INPUT(0.4), synth(w, _depth + 1))

    elif u % 2 == 0:
        # (b) z = (1 - 0.5*w) * 0.4,  w = 2 - 5z
        w = _r(2.0 - 5.0 * z)
        return AND(NOT(AND(INPUT(0.5), synth(w, _depth + 1))),
                   INPUT(0.4))

    elif z <= 0.3:
        # (c) z = (1 - (1 - 0.5*w)*0.5) * 0.4,  w = 10z - 2
        w = _r(10.0 * z - 2.0)
        return AND(NOT(AND(NOT(AND(INPUT(0.5), synth(w, _depth + 1))),
                           INPUT(0.5))),
                   INPUT(0.4))

    else:
        # (d) z = (1 - 0.5*0.5*w) * 0.4,  w = 4 - 10z
        w = _r(4.0 - 10.0 * z)
        return AND(NOT(AND(AND(INPUT(0.5), INPUT(0.5)),
                           synth(w, _depth + 1))),
                   INPUT(0.4))


# ---------------------------------------------------------------------------
# Gate-count and depth utilities
# ---------------------------------------------------------------------------

def count_gates(node) -> dict:
    c = {"AND": 0, "NOT": 0, "INPUT": 0}
    def walk(n):
        if   isinstance(n, InputNode):    c["INPUT"] += 1
        elif isinstance(n, InverterNode): c["NOT"]   += 1; walk(n.child)
        elif isinstance(n, AndNode):      c["AND"]   += 1; walk(n.left); walk(n.right)
    walk(node)
    return c


def circuit_depth(node) -> int:
    if isinstance(node, InputNode):    return 0
    if isinstance(node, InverterNode): return 1 + circuit_depth(node.child)
    if isinstance(node, AndNode):
        return 1 + max(circuit_depth(node.left), circuit_depth(node.right))
    return 0


# ---------------------------------------------------------------------------
# ASCII tree printer — shows the parallel structure clearly
# ---------------------------------------------------------------------------

def print_circuit(node, prefix: str = "", connector: str = "",
                  label: str = "OUT") -> None:
    """
    Prints the circuit as a Unicode box-drawing tree, e.g.:

    OUT: AND    p=0.1190000
        ├── L: AND    p=0.1400000
        │   ├── L: NOT    p=0.7000000
        │   │   └── in: AND    p=0.3000000
        │   │       ├── L: NOT    p=0.6000000
        │   │       │   └── in: INPUT  p=0.4000
        │   │       └── R: INPUT  p=0.5000
        │   └── R: AND    p=0.2000000
        │       ├── L: INPUT  p=0.4000
        │       └── R: INPUT  p=0.5000
        └── R: ...
    """
    if isinstance(node, InputNode):
        print(f"{prefix}{connector}{label}: INPUT  p={node.prob():.4f}")
    elif isinstance(node, InverterNode):
        print(f"{prefix}{connector}{label}: NOT    p={node.prob():.7f}")
        ext = "    " if connector == "" else ("│   " if "├" in connector else "    ")
        print_circuit(node.child, prefix + ext, "└── ", "in")
    elif isinstance(node, AndNode):
        print(f"{prefix}{connector}{label}: AND    p={node.prob():.7f}")
        ext = "    " if connector == "" else ("│   " if "├" in connector else "    ")
        print_circuit(node.left,  prefix + ext, "├── ", "L")
        print_circuit(node.right, prefix + ext, "└── ", "R")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TARGET_PROBS = [0.8881188, 0.2119209, 0.5555555]

if __name__ == "__main__":
    print("=" * 68)
    print("  Algorithm 1 — Tree-Style Probability Circuit Synthesis")
    print("  Source set S = {0.4, 0.5}   Gates: AND, NOT only")
    print("  Both inputs of every AND gate are independent sub-circuits")
    print("=" * 68)

    for target in TARGET_PROBS:
        circuit = synth(target)
        achieved = circuit.prob()
        error    = abs(achieved - target)
        g        = count_gates(circuit)
        d        = circuit_depth(circuit)

        print(f"\n{'─' * 68}")
        print(f"  Target               : {target}")
        print(f"  Achieved probability : {achieved:.10f}")
        print(f"  Absolute error       : {error:.2e}")
        print(f"  Gate counts          : AND={g['AND']}  NOT={g['NOT']}  INPUT={g['INPUT']}")
        print(f"  Circuit depth        : {d}")
        print(f"\n  Circuit tree:")
        print_circuit(circuit)

    print(f"\n{'=' * 68}\n")