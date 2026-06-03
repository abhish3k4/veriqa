"""Exceptions for Veriqa.

QuantumAssertionError subclasses AssertionError on purpose: that way it behaves
like a normal failed assertion inside pytest / unittest, so users get familiar
red output and tracebacks without any special integration.
"""

from __future__ import annotations


class VeriqaError(Exception):
    """Base class for all Veriqa errors that are NOT assertion failures."""


class QuantumAssertionError(AssertionError):
    """Raised when a quantum assertion fails.

    Carries the full ``AssertionResult`` on ``.result`` so test runners and
    dashboards can inspect the metrics, not just the message.
    """

    def __init__(self, result):  # result: AssertionResult
        self.result = result
        super().__init__(str(result))


class BackendError(VeriqaError):
    """Raised when a backend cannot fulfil a request (e.g. statevector on hardware)."""
