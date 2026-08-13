import csv
import json
from pathlib import Path

from harness.literature_verification.canonical import CanonicalDocument

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "artifacts/literature_gold_final"
PAPER_DATA = ROOT / "artifacts/data/paper-extraction"


def _ids(path):
    with path.open(encoding="utf-8-sig") as stream:
        return [row["paper_id"] for row in csv.DictReader(stream)]


def test_same_pdf_parser_inputs_and_canonical_outputs():
    data = json.loads((PAPER_DATA / "mineru_opendataloader_same_pdf_benchmark.json").read_text(encoding="utf-8"))
    assert data["sample_count"] == 5
    assert data["same_pdf_hashes_verified"] is True
    for row in data["rows"]:
        assert row["same_pdf_hash"] is True
        assert Path(row["mineru"]["raw_output"]).is_dir()
        assert Path(row["opendataloader"]["raw_json"]).is_file()
        for parser in ("mineru", "opendataloader"):
            path = ROOT / "artifacts/parser_canonical_same_pdf" / f"{Path(row['pdf_path']).stem}.{parser}.canonical.json"
            doc = CanonicalDocument.model_validate_json(path.read_text(encoding="utf-8"))
            assert doc.text.strip()
            assert doc.source_pdf_sha256 == row["pdf_sha256"]


def test_final_ready_contract_and_identity_routing():
    manifest = json.loads((FINAL / "paper_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest) == 54
    for paper in manifest:
        if paper["final_state"] == "READY":
            assert paper["identity_status"] == "VERIFIED"
            assert Path(paper["local_path"]).is_file()
            assert Path(paper["canonical_document"]).is_file()
            assert Path(paper["parser_markdown"]).read_text(encoding="utf-8", errors="replace").strip()
        elif paper["identity_status"] in {"PROBABLE", "REVIEW_REQUIRED", "INSUFFICIENT_METADATA"}:
            assert paper["final_state"] == "IDENTITY_REVIEW"


def test_ab_overlap_and_no_machine_label_leakage():
    assert _ids(FINAL / "annotator_A.csv") == _ids(FINAL / "annotator_B.csv")
    forbidden = {"machine verdict", "machine eligibility", "machine judge score", "metadata tier prediction", "hidden reason codes", "machine_score", "reason_codes"}
    for name in ("annotator_A.csv", "annotator_B.csv"):
        text = (FINAL / name).read_text(encoding="utf-8-sig").casefold()
        assert not any(term in text for term in forbidden)
        with (FINAL / name).open(encoding="utf-8-sig") as stream:
            for row in csv.DictReader(stream):
                for field in ("identity_correct", "publication_type", "host_relation", "product_role",
                              "implemented_engineering_present", "measured_production_present", "final_eligibility"):
                    assert not row[field]


def test_paths_and_queues_are_complete():
    manifest = json.loads((FINAL / "paper_manifest.json").read_text(encoding="utf-8"))
    ready = sum(x["final_state"] == "READY" for x in manifest)
    review = sum(x["final_state"] == "IDENTITY_REVIEW" for x in manifest)
    missing = sum(x["final_state"] == "FULLTEXT_MISSING" for x in manifest)
    assert len(_ids(FINAL / "annotator_A.csv")) == ready
    assert len(_ids(FINAL / "identity_review_queue.csv")) == review
    assert len(_ids(FINAL / "unresolved_fulltext_queue.csv")) == missing
    assert ready + review + missing == 54
