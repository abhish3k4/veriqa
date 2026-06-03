"""Veriqa's own test suite.

Demonstrates the contract: correct circuits PASS, broken circuits FAIL.
Run with:  pytest -v
"""

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate

import veriqa as vq
from veriqa import QuantumAssertionError

vq.configure(seed=1234, shots=8192)
vq.reset_backends()


def bell() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


# ---- distribution_close ----------------------------------------------------

def test_distribution_close_passes_for_correct_bell():
    res = vq.assert_distribution_close(bell(), {"00": 0.5, "11": 0.5}, raises=False)
    assert res.passed
    assert res.metrics["tvd"] < 0.05


def test_distribution_close_fails_for_wrong_expectation():
    # A Bell state never produces "01"/"10"; claiming uniform must fail.
    with pytest.raises(QuantumAssertionError):
        vq.assert_distribution_close(
            bell(), {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25}
        )


def test_distribution_close_accepts_reference_circuit():
    res = vq.assert_distribution_close(bell(), bell(), raises=False)
    assert res.passed


def test_distribution_tvd_method():
    res = vq.assert_distribution_close(
        bell(), {"00": 0.5, "11": 0.5}, method="tvd", tvd_threshold=0.05, raises=False
    )
    assert res.passed


# ---- state_equal -----------------------------------------------------------

def test_state_equal_up_to_global_phase():
    qc = QuantumCircuit(1)
    qc.x(0)
    # |1> with a global phase of -1 is physically the same state.
    res = vq.assert_state_equal(qc, np.array([0, -1]), raises=False)
    assert res.passed
    assert res.metrics["fidelity"] == pytest.approx(1.0, abs=1e-9)


def test_state_equal_fails_for_wrong_state():
    qc = QuantumCircuit(1)
    qc.x(0)  # prepares |1>
    with pytest.raises(QuantumAssertionError):
        vq.assert_state_equal(qc, np.array([1, 0]))  # |0>


# ---- unitary_equal / circuits_equivalent ----------------------------------

def test_unitary_equal_hadamard():
    qc = QuantumCircuit(1)
    qc.h(0)
    h = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]])
    res = vq.assert_unitary_equal(qc, h, raises=False)
    assert res.passed


def test_circuits_equivalent_detects_optimisation_preserving_behaviour():
    a = QuantumCircuit(1)
    a.x(0)
    a.x(0)            # X X == identity
    b = QuantumCircuit(1)  # empty == identity
    res = vq.assert_circuits_equivalent(a, b, raises=False)
    assert res.passed


def test_circuits_equivalent_catches_behaviour_change():
    good = bell()
    broken = QuantumCircuit(2)
    broken.h(0)       # missing the CX -> different unitary
    with pytest.raises(QuantumAssertionError):
        vq.assert_circuits_equivalent(good, broken)


def test_qft_roundtrip_is_identity():
    n = 3
    qc = QuantumCircuit(n)
    qc.append(QFTGate(n), range(n))
    qc.append(QFTGate(n).inverse(), range(n))
    identity = QuantumCircuit(n)
    res = vq.assert_circuits_equivalent(qc, identity, raises=False)
    assert res.passed


# ---- deterministic ---------------------------------------------------------

def test_deterministic_for_classical_circuit():
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.x(1)  # always 11
    res = vq.assert_deterministic(qc, expected_outcome="11", raises=False)
    assert res.passed


def test_deterministic_fails_for_superposition():
    qc = QuantumCircuit(1)
    qc.h(0)  # 50/50, not deterministic
    with pytest.raises(QuantumAssertionError):
        vq.assert_deterministic(qc)
