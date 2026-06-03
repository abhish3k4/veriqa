"""Backend registry and resolution.

Register a new backend by adding one line to ``_REGISTRY``. ``get_backend``
resolves, in order: an explicit Backend instance, a name string, or the global
default from config.
"""

from __future__ import annotations

from typing import Dict, Optional, Type, Union

from ..core.config import config
from .base import Backend
from .qiskit_aer import AerBackend

# name -> Backend subclass. Add future backends here:
#   "pennylane": PennyLaneBackend,
#   "ibm":       IBMHardwareBackend,
#   "braket":    BraketBackend,
_REGISTRY: Dict[str, Type[Backend]] = {
    "aer": AerBackend,
}

# Cache instantiated singletons so we don't rebuild simulators every assertion.
_INSTANCES: Dict[str, Backend] = {}


def register_backend(name: str, cls: Type[Backend]) -> None:
    """Register a custom backend at runtime (useful for plugins/tests)."""
    _REGISTRY[name] = cls
    _INSTANCES.pop(name, None)


def get_backend(backend: Optional[Union[str, Backend]] = None) -> Backend:
    if isinstance(backend, Backend):
        return backend
    name = backend or config.backend_name
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown backend {name!r}. Registered: {sorted(_REGISTRY)}"
        )
    if name not in _INSTANCES:
        kwargs = {}
        if name == "aer":
            kwargs["seed"] = config.seed
        _INSTANCES[name] = _REGISTRY[name](**kwargs)
    return _INSTANCES[name]


def reset_backends() -> None:
    """Drop cached backend instances (call after changing config.seed)."""
    _INSTANCES.clear()


__all__ = ["Backend", "AerBackend", "get_backend", "register_backend", "reset_backends"]
