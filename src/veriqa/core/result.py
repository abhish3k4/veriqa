"""The single result object every assertion returns.

Why this exists: every current and *future* assertion (distribution, state,
unitary, tomography, metamorphic, ...) returns the same ``AssertionResult``.
That means the monitoring layer, CI reporters, and dashboards you build later
only ever have to understand ONE shape. Don't return raw bools from assertions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AssertionResult:
    """Outcome of a single quantum assertion.

    Attributes
    ----------
    passed:
        Whether the assertion held.
    check:
        Short name of the check that ran, e.g. ``"distribution_close"``.
        Used as a stable key by reporters/dashboards.
    message:
        Human-readable explanation (shown on failure).
    metrics:
        Numeric evidence (p-values, distances, fidelities, shots, ...).
        This is what a time-series/monitoring layer will store and trend.
    """

    passed: bool
    check: str
    message: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        metric_str = ", ".join(f"{k}={v}" for k, v in self.metrics.items())
        base = f"[{status}] {self.check}"
        if self.message:
            base += f": {self.message}"
        if metric_str:
            base += f" ({metric_str})"
        return base

    def raise_if_failed(self) -> "AssertionResult":
        """Raise QuantumAssertionError if this result failed; else return self."""
        if not self.passed:
            from ..exceptions import QuantumAssertionError  # local import avoids cycle

            raise QuantumAssertionError(self)
        return self
