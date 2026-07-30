"""Real GEM/FBA adapter using cobrapy against its bundled `e_coli_core`
model - a genuine, small, well-known E. coli core-metabolism genome-scale
model shipped inside the `cobra` package itself (verified during this
round's audit: `cobra==0.31.1` installed, `cobra.io.load_model("textbook")`
loads and optimizes offline with no network or extra data files). This is
the one real "controlled case" doc03 Phase 3 requires when a real GEM is
already available in the environment - not a stub.

Execution logic (`validate_input`/`run`) lives in
`_cobrapy_fba_base.CobrapyFbaAdapterMixin`, shared with
`gem_fba_iml1515.py`'s larger-model adapter (Phase D) - this file only
supplies the `e_coli_core`-specific loader/cache. `_load_model`/`_CACHE`
stay module-level functions (not folded into the class) because
`harness/virtual_cell/compiler.py` imports `_load_model` directly - moving
it would be a breaking rename, not a refactor.
"""
from __future__ import annotations

from typing import Any

from harness.diagnosis.model_adapters._cobrapy_fba_base import CobrapyFbaAdapterMixin
from harness.diagnosis.model_adapters.base import CapabilityStatus, ModelAdapter

_CACHE: dict[str, Any] = {}

# Curated, narrow: only genes whose knockout/overexpression is a well-known
# bound change on cobrapy's bundled e_coli_core textbook model. Single
# source of truth shared by every caller that needs to turn one of this
# repo's own gene-level engineering decisions into a real FBA input instead
# of re-deriving (or duplicating) the mapping per caller -
# `harness.engineering_design.counterfactual_service` and
# `harness.workflow.synbio_stages` both import this rather than keeping
# their own copy.
GENE_TO_REACTION_BOUND_HINT: dict[str, dict[str, Any]] = {
    "pykF": {"reaction": "PYK", "knockout": {"lower": 0, "upper": 0}, "overexpression": {"lower": 0, "upper": 1000}},
    "ptsG": {"reaction": "GLCpts", "knockout": {"lower": 0, "upper": 0}},
    "ppc": {"reaction": "PPC", "overexpression": {"lower": 0, "upper": 1000}},
}
# Verified against cobrapy's bundled "textbook" e_coli_core model.
BIOMASS_OBJECTIVE_ECOLI_CORE = "Biomass_Ecoli_core"


def _load_model() -> Any:
    if "model" not in _CACHE:
        import cobra
        from cobra.io import load_model

        _CACHE["model"] = load_model("textbook")
        _CACHE["cobra_version"] = cobra.__version__
    return _CACHE["model"]


class GemFbaAdapter(CobrapyFbaAdapterMixin, ModelAdapter):
    name = "gem_fba"
    model_name = "e_coli_core (cobrapy bundled textbook model)"
    model_version = "e_coli_core"

    def _get_model(self) -> Any:
        return _load_model()

    def _reproducibility_ref(self) -> dict[str, Any]:
        return {"cobra_version": _CACHE.get("cobra_version", "unknown"), "model_id": "e_coli_core"}

    def detect_capability(self) -> CapabilityStatus:
        try:
            import cobra  # noqa: F401
        except ImportError as e:
            return CapabilityStatus(available=False, reason=f"cobrapy not installed: {e}")
        try:
            _load_model()
        except Exception as e:  # noqa: BLE001
            return CapabilityStatus(available=False, reason=f"failed to load bundled e_coli_core model: {e}")
        return CapabilityStatus(available=True, reason="cobrapy + bundled e_coli_core model available")
