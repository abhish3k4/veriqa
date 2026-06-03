"""Statistical hypothesis tests for measurement distributions.

The hard part of testing quantum code is that outputs are samples from a
distribution, so you cannot do ``assert counts == expected``. You must ask:
"are these observed counts statistically consistent with the expected
distribution, given only ``shots`` samples?" That is a goodness-of-fit test.

v0.1 ships Pearson's chi-squared GOF. Future tests (G-test, exact multinomial,
Bayesian) drop in here as new functions with the same return contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping

from scipy import stats


@dataclass
class GofResult:
    passed: bool
    p_value: float
    statistic: float
    dof: int


def chi_square_gof(
    observed: Mapping[str, int],
    expected: Mapping[str, float],
    alpha: float = 0.05,
    floor: float = 1e-9,
) -> GofResult:
    """Pearson chi-squared goodness-of-fit.

    H0: observed counts are drawn from ``expected``. We *reject* H0 (i.e. the
    assertion FAILS) when ``p_value < alpha``.

    Notes
    -----
    * Outcomes seen in ``observed`` but absent from ``expected`` are strong
      evidence against H0. We assign them a tiny floored probability rather
      than dividing by zero, then renormalise. This is a documented v0.1
      heuristic; an exact-test path is on the roadmap.
    """
    total = sum(observed.values())
    if total == 0:
        raise ValueError("Empty counts: nothing was measured.")

    obs = {k.replace(" ", ""): v for k, v in observed.items()}
    exp_raw = {k.replace(" ", ""): v for k, v in expected.items()}
    keys = sorted(set(obs) | set(exp_raw))

    exp = {k: max(exp_raw.get(k, 0.0), floor) for k in keys}
    z = sum(exp.values())
    exp = {k: v / z for k in exp for v in [exp[k]]}  # renormalise to sum 1

    statistic = 0.0
    for k in keys:
        e = total * exp[k]
        o = obs.get(k, 0)
        statistic += (o - e) ** 2 / e

    dof = max(len(keys) - 1, 1)
    p_value = float(stats.chi2.sf(statistic, dof))
    return GofResult(passed=p_value >= alpha, p_value=p_value, statistic=float(statistic), dof=dof)
