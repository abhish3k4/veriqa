"""Input coercion helpers.

Assertions accept flexible "expected" arguments (a dict, another circuit, a raw
numpy array, or a Qiskit Statevector/Operator). Centralising the coercion here
keeps each assertion short and means new accepted types are added in one place.
"""

from __future__ import annotations

from typing import Dict, Union

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

from ..backends.base import Backend

ExpectedProbs = Union[Dict[str, float], QuantumCircuit]
ExpectedState = Union[np.ndarray, list, QuantumCircuit, Statevector]
ExpectedUnitary = Union[np.ndarray, QuantumCircuit, Operator]


def to_probabilities(expected: ExpectedProbs, backend: Backend) -> Dict[str, float]:
    """Coerce ``expected`` into a {bitstring: probability} dict."""
    if isinstance(expected, QuantumCircuit):
        qc = expected.remove_final_measurements(inplace=False)
        return {k.replace(" ", ""): float(v)
                for k, v in Statevector(qc).probabilities_dict().items()}
    if isinstance(expected, dict):
        return {k.replace(" ", ""): float(v) for k, v in expected.items()}
    raise TypeError(
        "expected must be a {bitstring: prob} dict or a QuantumCircuit, "
        f"got {type(expected).__name__}"
    )


def to_statevector(expected: ExpectedState) -> np.ndarray:
    if isinstance(expected, QuantumCircuit):
        qc = expected.remove_final_measurements(inplace=False)
        return np.asarray(Statevector(qc).data, dtype=complex)
    if isinstance(expected, Statevector):
        return np.asarray(expected.data, dtype=complex)
    return np.asarray(expected, dtype=complex).ravel()


def to_unitary(expected: ExpectedUnitary) -> np.ndarray:
    if isinstance(expected, QuantumCircuit):
        qc = expected.remove_final_measurements(inplace=False)
        return np.asarray(Operator(qc).data, dtype=complex)
    if isinstance(expected, Operator):
        return np.asarray(expected.data, dtype=complex)
    return np.asarray(expected, dtype=complex)
