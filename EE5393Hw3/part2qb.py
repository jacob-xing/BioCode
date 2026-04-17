"""
Algorithm 2 (Tree-Style): Synthesize a circuit of AND gates and inverters
that generates a required binary fraction probability from S = {0.5}.

Based on: "The Synthesis of Combinational Logic to Generate Probabilities"
Qian, Riedel, Bazargan, Lilja — ICCAD 2009

KEY DIFFERENCE FROM LINEAR VERSION
====================================
Previously the circuit was a single left-growing chain:

    CONST(0) -> AND(INPUT(0.5)) -> NOT(AND(NOT(...), INPUT(0.5))) -> ... -> OUT

Every AND gate had the accumulator chain on the LEFT and a bare INPUT(0.5)
leaf on the RIGHT. This is the same shape as the old Algorithm 1 problem.

Now both branches of every AND gate are independent sub-circuits:

    bit=0 :  AND( INPUT(0.5),  synth(rest_of_bits) )

                 INPUT(0.5) ──┐
                               AND ──> 0.5 * z_rest
    synth(rest) ──────────────┘

    bit=1 :  NOT( AND( NOT(synth(rest_of_bits)),  INPUT(0.5) ) )

    synth(rest) ──> NOT ──┐
                           AND ──> NOT ──> 0.5*(1 + z_rest)
         INPUT(0.5) ──────┘

Each INPUT(0.5) is a fresh independent source at its own level of the tree.

RECURSIVE STRUCTURE
====================
For binary fraction  z = 0.b₁ b₂ … bₘ  (bᵢ ∈ {0,1}):

    synth("")       = CONST(0)           ← base: empty suffix has value 0

    synth("0" + rest):
        z = 0.5 * (0.rest)               ← prepending a 0-bit halves the value
        => AND( INPUT(0.5),  synth(rest) )
        because  0.5 * synth_prob(rest) = 0.0rest  ✓

    synth("1" + rest):
        z = 0.5 + 0.5 * (0.rest)         ← prepending a 1-bit adds 0.5
          = 0.5 * (1 + synth_prob(rest))
        => NOT( AND( NOT(synth(rest)),  INPUT(0.5) ) )
        because  1 − (1 − x)·0.5 = 0.5·(1 + x)  ✓

This gives a RIGHT-RECURSIVE tree: each AND has a fresh INPUT(0.5) on one
branch and the recursively-synthesised sub-circuit for the remaining bits
on the other. Every INPUT(0.5) in the final tree is an independent source.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Circuit node classes
# ---------------------------------------------------------------------------

class InputNode:
    """Primary input — a fixed-probability random source (always 0.5 here)."""
    def __init__(self, p: float):
        self._p = p
    def prob(self) -> float:
        return self._p
    def __repr__(self):
        return f"INPUT({self._p})"


class ConstantNode:
    """
    Degenerate tie-to-rail constant (GND = 0.0 or VDD = 1.0).
    Used only as the base-case seed at the deepest level of the tree.
    """
    def __init__(self, value: float):
        assert value in (0.0, 1.0), "ConstantNode must be exactly 0 or 1"
        self._v = value
    def prob(self) -> float:
        return self._v
    def __repr__(self):
        return f"CONST({'1' if self._v else '0'})"


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
def INPUT(p):         return InputNode(p)
def CONST(v):         return ConstantNode(v)
def NOT(child):       return InverterNode(child)
def AND(left, right): return AndNode(left, right)


# ---------------------------------------------------------------------------
# Binary fraction parser
# ---------------------------------------------------------------------------

def parse_binary_fraction(s: str) -> tuple[str, float]:
    """
    Parse a string like "0.1011111" or "0.10111112" (trailing '2' = base-2).

    Returns (bit_string, decimal_value), e.g. ("1011111", 0.7421875).
    """
    s = s.strip().rstrip("2_")
    if "." not in s:
        raise ValueError(f"Expected a fractional binary number, got: {s!r}")
    _, frac = s.split(".", 1)
    if not all(c in "01" for c in frac):
        raise ValueError(f"Non-binary digit in fractional part: {frac!r}")
    decimal = sum(int(b) * (0.5 ** (i + 1)) for i, b in enumerate(frac))
    return frac, decimal


# ---------------------------------------------------------------------------
# Algorithm 2: recursive tree synthesis
# ---------------------------------------------------------------------------

def synth(bits: str) -> ConstantNode | InputNode | InverterNode | AndNode:
    """
    Recursively build a parallel AND/NOT tree for the binary fraction 0.bits.

    Both branches of every AND gate are independent sub-circuit trees —
    there are no "fixed" leaves except InputNode(0.5) and the single
    ConstantNode(0) at the very bottom.

    Parameters
    ----------
    bits : binary digit string, e.g. "1011111" for 0.1011111₂

    Returns
    -------
    Root node of the synthesised circuit tree.
    """
    # Base case: no more bits → value is 0 (tie to GND)
    if not bits:
        return CONST(0.0)

    b, rest = bits[0], bits[1:]
    sub = synth(rest)          # independent sub-circuit for remaining bits

    if b == "0":
        # 0.0rest = 0.5 × 0.rest
        # => AND( INPUT(0.5),  sub )
        return AND(INPUT(0.5), sub)

    else:  # b == "1"
        # 0.1rest = 0.5 × (1 + 0.rest)
        # => NOT( AND( NOT(sub),  INPUT(0.5) ) )
        return NOT(AND(NOT(sub), INPUT(0.5)))


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def synthesize_binary(binary_str: str):
    """
    Synthesize a circuit tree for the given binary fraction string.

    Returns (root_node, achieved_prob, bit_string, expected_prob).
    """
    bits, expected = parse_binary_fraction(binary_str)
    root = synth(bits)
    return root, root.prob(), bits, expected


# ---------------------------------------------------------------------------
# Utilities: print, count gates, depth
# ---------------------------------------------------------------------------

def print_circuit(node, prefix: str = "", connector: str = "",
                  label: str = "OUT") -> None:
    """
    Prints the circuit as a Unicode box-drawing tree, e.g.:

    OUT: NOT    p=0.7421875
        └── in: AND    p=0.2578125
            ├── L: NOT    p=0.5156250
            │   └── in: AND    p=0.4843750
            │       ├── L: INPUT  p=0.5000
            │       └── R: NOT    p=0.9687500
            │           └── ...
            └── R: INPUT  p=0.5000
    """
    if isinstance(node, ConstantNode):
        print(f"{prefix}{connector}{label}: CONST  p={node.prob():.1f}")
    elif isinstance(node, InputNode):
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


def count_gates(node) -> dict:
    c = {"AND": 0, "NOT": 0, "INPUT": 0, "CONST": 0}
    def walk(n):
        if   isinstance(n, ConstantNode):  c["CONST"] += 1
        elif isinstance(n, InputNode):     c["INPUT"] += 1
        elif isinstance(n, InverterNode):  c["NOT"]   += 1; walk(n.child)
        elif isinstance(n, AndNode):       c["AND"]   += 1; walk(n.left); walk(n.right)
    walk(node)
    return c


def circuit_depth(node) -> int:
    if isinstance(node, (InputNode, ConstantNode)): return 0
    if isinstance(node, InverterNode): return 1 + circuit_depth(node.child)
    if isinstance(node, AndNode):
        return 1 + max(circuit_depth(node.left), circuit_depth(node.right))
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TARGET_BINARIES = [
    "0.10111112",   # i.
    "0.11011112",   # ii.
    "0.10101112",   # iii.
]

if __name__ == "__main__":
    print("=" * 70)
    print("  Algorithm 2 — Tree-Style Binary Fraction Circuit Synthesis")
    print("  Source set S = {0.5}   Gates: AND, NOT only")
    print("  Both inputs of every AND gate are independent sub-circuits")
    print("=" * 70)
    print()
    print("  Recursive structure:")
    print("    synth(\"\")        = CONST(0)           ← base case")
    print("    synth(\"0\" + rest) = AND( INPUT(0.5),  synth(rest) )")
    print("    synth(\"1\" + rest) = NOT( AND( NOT(synth(rest)),  INPUT(0.5) ) )")

    for idx, bstr in enumerate(TARGET_BINARIES, start=1):
        circuit, achieved, bits, expected = synthesize_binary(bstr)
        error = abs(achieved - expected)
        g     = count_gates(circuit)
        d     = circuit_depth(circuit)
        n_ones  = bits.count("1")
        n_zeros = bits.count("0")

        print(f"\n{'─' * 70}")
        print(f"  ({idx})  Target : 0.{bits}₂")
        print(f"{'─' * 70}")
        print(f"  Decimal value        : {expected:.10f}")
        print(f"  As fraction          : {int(bits,2)}/2^{len(bits)} = {int(bits,2)}/{2**len(bits)}")
        print(f"  Achieved probability : {achieved:.10f}")
        print(f"  Absolute error       : {error:.2e}")
        print()
        print(f"  Bit breakdown  : {len(bits)} bits  "
              f"({n_ones} ones → NOT-wrap steps,  "
              f"{n_zeros} zeros → plain AND steps)")
        print(f"  Gate counts    : AND={g['AND']}  NOT={g['NOT']}  "
              f"INPUT={g['INPUT']}  CONST(0)={g['CONST']}")
        print(f"  Circuit depth  : {d}")
        print()
        print("  Circuit tree (output → inputs):")
        print_circuit(circuit)

    print(f"\n{'=' * 70}")
    print()
    print("  Summary table:")
    print(f"  {'Binary':^18}  {'Fraction':^12}  {'AND':^5}  {'NOT':^5}  "
          f"{'INPUT':^7}  {'Depth':^7}")
    print(f"  {'─'*18}  {'─'*12}  {'─'*5}  {'─'*5}  {'─'*7}  {'─'*7}")
    for bstr in TARGET_BINARIES:
        circuit, achieved, bits, expected = synthesize_binary(bstr)
        g = count_gates(circuit)
        d = circuit_depth(circuit)
        frac = f"{int(bits,2)}/{2**len(bits)}"
        print(f"  {'0.'+bits+'₂':^18}  {frac:^12}  {g['AND']:^5}  "
              f"{g['NOT']:^5}  {g['INPUT']:^7}  {d:^7}")
    print()
    print("  For an m-bit binary fraction with k one-bits:")
    print("    AND gates = m        (one per bit)")
    print("    NOT gates = 2k       (each '1' bit wraps its sub-tree with NOT…NOT)")
    print("    INPUT(0.5)= m        (one fresh independent source per AND gate)")
    print("    Depth     = m + 2k   (right-recursive chain depth)")
    print(f"\n{'=' * 70}\n")