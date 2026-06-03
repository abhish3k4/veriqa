"""Backend interface.

THE key extension point. To support a new execution target later
(PennyLane, Cirq, IBM real hardware, AWS Braket, a noise-simulated device),
subclass ``Backend`` and implement the three methods, then register it in
``backends/__init__.py``. Nothing else in the codebase needs to change.

Real hardware can't return a statevector or unitary, so those backends override
``supports_statevector``/``supports_unitary`` to return False and the relevant
assertions will raise a clear BackendError instead of silently lying.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

import numpy as np
from qiskit import QuantumCircuit


class Backend(ABC):
    """Abstract execution backend."""

    #: short, stable key used in the registry and config (e.g. "aer").
    name: str = "base"

    @abstractmethod
    def run_counts(self, circuit: QuantumCircuit, shots: int) -> Dict[str, int]:
        """Sample the circuit and return measurement counts {bitstring: int}."""

    @abstractmethod
    def statevector(self, circuit: QuantumCircuit) -> np.ndarray:
        """Return the ideal output statevector (measurement-free circuits)."""

    @abstractmethod
    def unitary(self, circuit: QuantumCircuit) -> np.ndarray:
        """Return the circuit's unitary matrix (measurement-free circuits)."""

    def supports_statevector(self) -> bool:
        return True

    def supports_unitary(self) -> bool:
        return True
