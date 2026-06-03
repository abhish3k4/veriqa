"""Global, overridable defaults.

Set once at the top of a test session::

    import veriqa
    veriqa.configure(shots=8192, seed=42)

Every assertion reads these defaults but lets you override per-call. Keeping
defaults here (not hard-coded in each assertion) means adding a new global knob
later is a one-line change that every assertion picks up for free.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    shots: int = 4096
    seed: Optional[int] = None
    alpha: float = 0.05          # significance level for statistical tests
    tvd_threshold: float = 0.10  # default total-variation-distance tolerance
    atol: float = 1e-6           # absolute tolerance for state/unitary checks
    backend_name: str = "aer"    # default backend key (see backends registry)


# Module-level singleton. Assertions read from this when a kwarg is None.
config = Config()


def configure(**kwargs) -> Config:
    """Update global defaults. Unknown keys raise immediately."""
    for key, value in kwargs.items():
        if not hasattr(config, key):
            raise AttributeError(f"Unknown config option: {key!r}")
        setattr(config, key, value)
    return config
