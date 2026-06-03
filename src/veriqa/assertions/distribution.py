"""assert_distribution_close - the headline check.

Verifies that a circuit's measured output distribution is consistent with an
expected distribution, accounting for shot noise. This is what catches a circuit
that is *silently wrong*: it runs, it returns counts, but the distribution is
off because a gate is missing/misplaced or the circuit was miscompiled.
"""

from __future__ import annotations

from typing import Optional, Union

from qiskit import QuantumCircuit

from ..backends import Backend, get_backend
from ..core.config import config
from ..core.result import AssertionResult
from ..stats.distances import total_variation_distance
from ..stats.tests import chi_square_gof
from ._convert import ExpectedProbs, to_probabilities


def assert_distribution_close(
    circuit: QuantumCircuit,
    expected: ExpectedProbs,
    *,
    shots: Optional[int] = None,
    method: str = "chi2",
    alpha: Optional[float] = None,
    tvd_threshold: Optional[float] = None,
    backend: Optional[Union[str, Backend]] = None,
    raises: bool = True,
) -> AssertionResult:
    """Assert the circuit's output distribution matches ``expected``.

    Parameters
    ----------
    expected:
        A ``{bitstring: probability}`` dict, or a reference ``QuantumCircuit``
        whose ideal distribution is used as the expectation.
    method:
        ``"chi2"`` (default) runs a goodness-of-fit hypothesis test that is
        robust to shot noise. ``"tvd"`` simply checks total-variation distance
        against ``tvd_threshold`` (deterministic, easy to reason about).
    raises:
        If True (default), failure raises QuantumAssertionError so it behaves
        like a normal assertion in pytest. Set False to get the result object.
    """
    bk = get_backend(backend)
    shots = shots or config.shots
    exp = to_probabilities(expected, bk)
    observed = bk.run_counts(circuit, shots)

    tvd = total_variation_distance(observed, exp)

    if method == "chi2":
        a = config.alpha if alpha is None else alpha
        gof = chi_square_gof(observed, exp, alpha=a)
        passed = gof.passed
        msg = (
            "output distribution consistent with expected"
            if passed
            else "output distribution differs from expected"
        )
        metrics = {
            "p_value": round(gof.p_value, 6),
            "alpha": a,
            "tvd": round(tvd, 4),
            "shots": shots,
        }
    elif method == "tvd":
        thr = config.tvd_threshold if tvd_threshold is None else tvd_threshold
        passed = tvd <= thr
        msg = f"TVD {tvd:.4f} {'<=' if passed else '>'} threshold {thr}"
        metrics = {"tvd": round(tvd, 4), "threshold": thr, "shots": shots}
    else:
        raise ValueError(f"Unknown method {method!r}; use 'chi2' or 'tvd'.")

    result = AssertionResult(passed=passed, check="distribution_close", message=msg, metrics=metrics)
    return result.raise_if_failed() if raises else result
