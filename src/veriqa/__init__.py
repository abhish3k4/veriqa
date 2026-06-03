"""Veriqa - catch silently-wrong quantum circuits.

Quantum programs output probability distributions, so you can't write
``assert result == expected``. A circuit can run fine and still be wrong.
Veriqa gives you assertions, statistical checks, and regression tests that
actually catch those silent failures.

Quick start
-----------
    from qiskit import QuantumCircuit
    import veriqa as vq

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)            # Bell state

    # Expected ideal distribution:
    vq.assert_distribution_close(qc, {"00": 0.5, "11": 0.5})

    # Regression test: did an "optimised" version change behaviour?
    vq.assert_circuits_equivalent(qc, my_optimised_qc)
"""

from __future__ import annotations

from .assertions import (
    REGISTRY,
    assert_circuits_equivalent,
    assert_deterministic,
    assert_distribution_close,
    assert_state_equal,
    assert_unitary_equal,
)
from .backends import get_backend, register_backend, reset_backends
from .core import AssertionResult, config, configure
from .exceptions import BackendError, QuantumAssertionError, VeriqaError

__version__ = "0.1.0"

__all__ = [
    # assertions
    "assert_distribution_close",
    "assert_state_equal",
    "assert_unitary_equal",
    "assert_circuits_equivalent",
    "assert_deterministic",
    "REGISTRY",
    # config
    "configure",
    "config",
    "AssertionResult",
    # backends
    "get_backend",
    "register_backend",
    "reset_backends",
    # exceptions
    "QuantumAssertionError",
    "BackendError",
    "VeriqaError",
    "__version__",
]
