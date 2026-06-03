"""Qiskit Aer backend (the v0.1 default).

Forgiving by design: if you hand ``run_counts`` a circuit with no measurements,
it measures all qubits for you. ``statevector``/``unitary`` strip any final
measurements so the same circuit object works for every assertion type.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator, Statevector
from qiskit_aer import AerSimulator

from .base import Backend


class AerBackend(Backend):
    name = "aer"

    def __init__(self, seed: int | None = None):
        self._sim = AerSimulator()
        self._seed = seed

    def run_counts(self, circuit: QuantumCircuit, shots: int) -> Dict[str, int]:
        qc = circuit
        # Auto-add measurements if the user gave us a bare state-prep circuit.
        if qc.num_clbits == 0:
            qc = qc.copy()
            qc.measure_all()
        compiled = transpile(qc, self._sim)
        run_kwargs = {"shots": shots}
        if self._seed is not None:
            run_kwargs["seed_simulator"] = self._seed
        result = self._sim.run(compiled, **run_kwargs).result()
        return dict(result.get_counts())

    def statevector(self, circuit: QuantumCircuit) -> np.ndarray:
        qc = circuit.remove_final_measurements(inplace=False)
        return np.asarray(Statevector(qc).data, dtype=complex)

    def unitary(self, circuit: QuantumCircuit) -> np.ndarray:
        qc = circuit.remove_final_measurements(inplace=False)
        return np.asarray(Operator(qc).data, dtype=complex)
