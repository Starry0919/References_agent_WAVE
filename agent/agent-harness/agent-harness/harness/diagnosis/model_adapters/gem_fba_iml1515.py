"""Real larger-GEM adapter: iML1515 (Monk et al. 2017), the standard
genome-scale reconstruction of E. coli K-12 MG1655 - 1516 genes / 2712
reactions / 1877 metabolites (verified during Phase D's audit by actually
loading and solving it: `cobra.io.read_sbml_model` succeeds in ~3.6s,
baseline FBA solves optimal at growth=0.877/h). The model asset
(`knowledge/models/iML1515.xml`, sha256
9c772d44ca43350e40dc7ee86c7aa148796856be1eea45e5406c6df8f7dcde28) is a
real SBML file found in this repository (a separate, earlier prototype
checkout at `workflow/design/JH/agent-harness-v1/.../data_ext/iML1515.xml`)
and copied here unmodified - not downloaded, not fabricated, not
regenerated from scratch.

Reuses `_cobrapy_fba_base.CobrapyFbaAdapterMixin` - the SAME execution
logic `gem_fba.py`'s `e_coli_core` adapter uses, not a second FBA stack
(prompt §6.7: "不得删除或重复实现现有 core FBA adapter").
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.config import PROJECT_ROOT
from harness.diagnosis.model_adapters._cobrapy_fba_base import CobrapyFbaAdapterMixin
from harness.diagnosis.model_adapters.base import CapabilityStatus, ModelAdapter

_MODEL_PATH = PROJECT_ROOT / "knowledge" / "models" / "iML1515.xml"
_CACHE: dict[str, Any] = {}


def _load_model() -> Any:
    if "model" not in _CACHE:
        import cobra

        _CACHE["model"] = cobra.io.read_sbml_model(str(_MODEL_PATH))
        _CACHE["cobra_version"] = cobra.__version__
    return _CACHE["model"]


class GemFbaLargeAdapter(CobrapyFbaAdapterMixin, ModelAdapter):
    name = "gem_fba_iml1515"
    model_name = "iML1515 (E. coli K-12 MG1655 genome-scale reconstruction, Monk et al. 2017)"
    model_version = "iML1515"

    def _get_model(self) -> Any:
        return _load_model()

    def _reproducibility_ref(self) -> dict[str, Any]:
        return {
            "cobra_version": _CACHE.get("cobra_version", "unknown"), "model_id": "iML1515",
            "model_file_hash": "9c772d44ca43350e40dc7ee86c7aa148796856be1eea45e5406c6df8f7dcde28",
        }

    def detect_capability(self) -> CapabilityStatus:
        try:
            import cobra  # noqa: F401
        except ImportError as e:
            return CapabilityStatus(available=False, reason=f"cobrapy not installed: {e}")
        if not Path(_MODEL_PATH).is_file():
            return CapabilityStatus(available=False, reason=f"iML1515 model file not found at {_MODEL_PATH}")
        try:
            _load_model()
        except Exception as e:  # noqa: BLE001
            return CapabilityStatus(available=False, reason=f"failed to load iML1515 SBML model: {e}")
        return CapabilityStatus(available=True, reason="cobrapy + iML1515 SBML model file available")
