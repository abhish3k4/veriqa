"""Distance / similarity metrics.

These are pure functions with no quantum dependencies beyond numpy, so they are
trivially unit-testable and reusable by the monitoring layer (e.g. trending TVD
of a circuit's output against a golden baseline over time).
"""

from __future__ import annotations

from typing import Dict, Mapping

import numpy as np


def _normalize_counts(counts: Mapping[str, int]) -> Dict[str, float]:
    total = sum(counts.values())
    if total == 0:
        raise ValueError("Empty counts: nothing was measured.")
    return {k.replace(" ", ""): v / total for k, v in counts.items()}


def total_variation_distance(
    observed: Mapping[str, int], expected: Mapping[str, float]
) -> float:
    """TVD in [0, 1]. 0 = identical, 1 = disjoint support.

    ``observed`` is raw integer counts; ``expected`` is a probability dict.
    """
    obs = _normalize_counts(observed)
    exp = {k.replace(" ", ""): v for k, v in expected.items()}
    keys = set(obs) | set(exp)
    return 0.5 * sum(abs(obs.get(k, 0.0) - exp.get(k, 0.0)) for k in keys)


def hellinger_distance(
    observed: Mapping[str, int], expected: Mapping[str, float]
) -> float:
    """Hellinger distance in [0, 1]; more sensitive to small-probability bins."""
    obs = _normalize_counts(observed)
    exp = {k.replace(" ", ""): v for k, v in expected.items()}
    keys = set(obs) | set(exp)
    s = sum((np.sqrt(obs.get(k, 0.0)) - np.sqrt(exp.get(k, 0.0))) ** 2 for k in keys)
    return float(np.sqrt(s / 2.0))


def state_fidelity(a: np.ndarray, b: np.ndarray) -> float:
    """Pure-state fidelity |<a|b>|^2, invariant to global phase. In [0, 1]."""
    a = np.asarray(a, dtype=complex).ravel()
    b = np.asarray(b, dtype=complex).ravel()
    if a.shape != b.shape:
        raise ValueError(f"Statevector dim mismatch: {a.shape} vs {b.shape}")
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.abs(np.vdot(a, b)) ** 2)
