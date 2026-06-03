"""Veriqa demo: a circuit that is *silently wrong*.

Story:
  We build a correct 3-qubit GHZ state, then inject a single-gate bug (we delete
  one CX -- exactly the kind of mistake a 'mutation testing' tool simulates).

  A NAIVE check ("is '000' still a frequent outcome?") PASSES the broken circuit,
  because the bug only shows up in the *correlations* between qubits, not the
  marginal you happened to eyeball.

  Veriqa's distribution + equivalence assertions CATCH it.

Run:  python examples/mutation_demo.py
"""

from qiskit import QuantumCircuit

import veriqa as vq

vq.configure(seed=7, shots=8192)
vq.reset_backends()


def ghz() -> QuantumCircuit:
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    return qc


def delete_gate(circuit: QuantumCircuit, index: int) -> QuantumCircuit:
    """Return a copy of the circuit with the gate at `index` removed (a mutation)."""
    mutant = circuit.copy_empty_like()
    for i, instr in enumerate(circuit.data):
        if i != index:
            mutant.append(instr.operation, instr.qubits, instr.clbits)
    return mutant


def naive_check(circuit: QuantumCircuit, label: str) -> bool:
    """What many devs actually do: glance at one marginal and call it good."""
    counts = vq.get_backend().run_counts(circuit, 8192)
    total = sum(counts.values())
    p_000 = counts.get("000", 0) / total
    ok = p_000 > 0.40  # "looks about half, good enough"
    print(f"  naive_check({label}): P('000') = {p_000:.3f} -> "
          f"{'PASS (looks fine)' if ok else 'FAIL'}")
    return ok


def veriqa_check(circuit: QuantumCircuit, label: str) -> bool:
    ideal = {"000": 0.5, "111": 0.5}
    res = vq.assert_distribution_close(circuit, ideal, raises=False)
    print(f"  veriqa.assert_distribution_close({label}): {res}")
    return res.passed


def main() -> None:
    correct = ghz()
    # index 2 is the second CX (h=0, cx=1, cx=2); deleting it breaks entanglement.
    mutant = delete_gate(correct, index=2)

    print("=" * 70)
    print("CORRECT GHZ circuit")
    print("=" * 70)
    naive_check(correct, "correct")
    veriqa_check(correct, "correct")

    print("\n" + "=" * 70)
    print("MUTANT circuit (one CX silently deleted)")
    print("=" * 70)
    naive_passes = naive_check(mutant, "mutant")
    veriqa_passes = veriqa_check(mutant, "mutant")

    print("\n" + "=" * 70)
    print("Regression check: is the mutant equivalent to the original?")
    print("=" * 70)
    eq = vq.assert_circuits_equivalent(correct, mutant, raises=False)
    print(f"  veriqa.assert_circuits_equivalent(correct, mutant): {eq}")

    print("\n" + "-" * 70)
    print("RESULT")
    print("-" * 70)
    print(f"  Naive check let the bug through : {naive_passes}  (bug survived)")
    print(f"  Veriqa caught the bug           : {not veriqa_passes and not eq.passed}")
    print("-" * 70)


if __name__ == "__main__":
    main()
