"""Public assertion API + registry.

To add a new assertion later:
  1. write it in its own module returning an AssertionResult,
  2. import it here,
  3. add it to ``__all__`` and ``REGISTRY``.

The REGISTRY (name -> callable) is what a future CLI, pytest plugin, or
auto-discovery layer iterates over, so registered checks get tooling for free.
"""

from __future__ import annotations

from .distribution import assert_distribution_close
from .properties import assert_deterministic
from .state import assert_state_equal
from .unitary import assert_circuits_equivalent, assert_unitary_equal

REGISTRY = {
    "distribution_close": assert_distribution_close,
    "state_equal": assert_state_equal,
    "unitary_equal": assert_unitary_equal,
    "circuits_equivalent": assert_circuits_equivalent,
    "deterministic": assert_deterministic,
}

__all__ = [
    "assert_distribution_close",
    "assert_state_equal",
    "assert_unitary_equal",
    "assert_circuits_equivalent",
    "assert_deterministic",
    "REGISTRY",
]
