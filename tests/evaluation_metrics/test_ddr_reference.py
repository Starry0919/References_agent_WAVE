from __future__ import annotations

from harness.evaluation_metrics import ddr_reference


def test_load_reference_targets_from_tryptophan_ddr():
    genes = ddr_reference.load_reference_targets(["DDR-001"])
    assert genes
    assert "ptsg, pykf (候选)" in genes
    assert "arog, aroh (候选过表达)" in genes


def test_load_reference_targets_dedupes_and_lowercases_across_ids():
    genes_one = ddr_reference.load_reference_targets(["DDR-001"])
    genes_two = ddr_reference.load_reference_targets(["DDR-001", "DDR-001"])
    assert genes_one == genes_two


def test_unknown_ddr_id_is_skipped_not_raised():
    genes = ddr_reference.load_reference_targets(["DDR-does-not-exist"])
    assert genes == set()


def test_empty_input_returns_empty_set():
    assert ddr_reference.load_reference_targets([]) == set()
