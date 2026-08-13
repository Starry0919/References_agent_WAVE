"""Case 1 (Knowledge & Evidence Layer audit, 老师 §Phase2): an empty/
whitespace query against the local DDR knowledge base must return the
full corpus (browse), never an empty result - `LocalDDRAdapter` is a
decision-record corpus, not a search box that stays blank until typed
into.
"""
from __future__ import annotations

import json

from harness.evidence_retrieval.local_ddr_adapter import LocalDDRAdapter


def _write_ddr(ddr_dir, ddr_id: str, *, organism: str = "Escherichia coli", target_product: str = "L-tryptophan") -> None:
    ddr_dir.mkdir(parents=True, exist_ok=True)
    (ddr_dir / f"{ddr_id}_test.json").write_text(
        json.dumps({
            "ddr_id": ddr_id,
            "schema_version": "2.0",
            "metadata": {"organism": organism, "host": "E. coli", "target_product": target_product, "title": f"paper about {ddr_id}"},
            "decision_chain": [],
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_empty_query_returns_every_ddr_record(tmp_path):
    ddr_dir = tmp_path / "ddr_database"
    _write_ddr(ddr_dir, "DDR-101")
    _write_ddr(ddr_dir, "DDR-102")
    _write_ddr(ddr_dir, "DDR-103")

    adapter = LocalDDRAdapter(ddr_dir=ddr_dir)
    result = adapter.search("", {}, {})

    assert result.total_available == 3
    assert {d.source_id for d in result.documents} == {"DDR-101", "DDR-102", "DDR-103"}


def test_whitespace_only_query_also_browses_everything(tmp_path):
    ddr_dir = tmp_path / "ddr_database"
    _write_ddr(ddr_dir, "DDR-201")

    adapter = LocalDDRAdapter(ddr_dir=ddr_dir)
    result = adapter.search("   ", {}, {})

    assert result.total_available == 1
    assert result.documents[0].source_id == "DDR-201"


def test_empty_knowledge_base_returns_empty_not_an_error(tmp_path):
    ddr_dir = tmp_path / "ddr_database"
    ddr_dir.mkdir()

    adapter = LocalDDRAdapter(ddr_dir=ddr_dir)
    result = adapter.search("", {}, {})

    assert result.total_available == 0
    assert result.documents == []


def test_nonempty_query_still_filters_as_before(tmp_path):
    ddr_dir = tmp_path / "ddr_database"
    _write_ddr(ddr_dir, "DDR-301", target_product="L-tryptophan")
    _write_ddr(ddr_dir, "DDR-302", target_product="1,4-butanediol")

    adapter = LocalDDRAdapter(ddr_dir=ddr_dir)
    result = adapter.search("tryptophan", {}, {})

    assert [d.source_id for d in result.documents] == ["DDR-301"]
