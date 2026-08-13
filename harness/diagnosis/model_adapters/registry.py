"""Model Adapter Registry (doc03 4.7): the single place capability
detection and adapter dispatch happen.
"""
from __future__ import annotations

from harness.diagnosis.model_adapters.base import CapabilityStatus, ModelAdapter
from harness.diagnosis.model_adapters.gem_fba import GemFbaAdapter
from harness.diagnosis.model_adapters.gem_fba_iml1515 import GemFbaLargeAdapter
from harness.diagnosis.model_adapters.kinetic import KineticResourceAdapter
from harness.diagnosis.model_adapters.vecoli import VEcoliAdapter

_ADAPTERS: dict[str, ModelAdapter] = {
    "gem_fba": GemFbaAdapter(),
    "gem_fba_iml1515": GemFbaLargeAdapter(),
    "vecoli": VEcoliAdapter(),
    "kinetic_resource": KineticResourceAdapter(),
}


def get_adapter(name: str) -> ModelAdapter:
    if name not in _ADAPTERS:
        raise KeyError(f"unknown model adapter {name!r}; available: {list(_ADAPTERS)}")
    return _ADAPTERS[name]


def list_adapters() -> list[str]:
    return list(_ADAPTERS)


def detect_all_capabilities() -> dict[str, CapabilityStatus]:
    return {name: adapter.detect_capability() for name, adapter in _ADAPTERS.items()}
