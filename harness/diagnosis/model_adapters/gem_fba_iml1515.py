"""Real larger-GEM adapter using the repository's legacy-named model asset.

The file is named ``iML1515.xml`` but its SBML model id and contents are
actually iJO1366 (1367 genes / 2583 reactions).  Runtime identity is the
scientific authority; the adapter keeps its legacy registry name for API
compatibility but must never report this asset as iML1515.

The model asset
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
    model_name = "iJO1366 (E. coli K-12 MG1655 genome-scale reconstruction; legacy file name iML1515.xml)"
    model_version = "iJO1366"

    def _get_model(self) -> Any:
        return _load_model()

    def _reproducibility_ref(self) -> dict[str, Any]:
        return {
            "cobra_version": _CACHE.get("cobra_version", "unknown"), "model_id": "iJO1366",
            "legacy_asset_name": "iML1515.xml",
            "model_file_hash": "9c772d44ca43350e40dc7ee86c7aa148796856be1eea45e5406c6df8f7dcde28",
        }

    def detect_capability(self) -> CapabilityStatus:
        try:
            import cobra  # noqa: F401
        except ImportError as e:
            return CapabilityStatus(available=False, reason=f"cobrapy not installed: {e}")
        if not Path(_MODEL_PATH).is_file():
            return CapabilityStatus(available=False, reason=f"legacy-named iJO1366 model file not found at {_MODEL_PATH}")
        try:
            _load_model()
        except Exception as e:  # noqa: BLE001
            return CapabilityStatus(available=False, reason=f"failed to load iJO1366 SBML model: {e}")
        return CapabilityStatus(available=True, reason="cobrapy + iJO1366 SBML model available (legacy filename iML1515.xml)")
