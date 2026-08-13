import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "artifacts/data/literature"
d = json.loads((DATA / "literature_discovery_benchmark_k12_tryptophan.json").read_text(encoding="utf-8"))
tiers = ["tier_2_supporting_engineering", "tier_3_mechanistic", "background", "exclude"]
chosen = []
for tier, count in zip(tiers, [20, 20, 15, 5]):
    chosen += [x for x in d["candidates"] if (x.get("relevance") or {}).get("decision") == tier][:count]
rows = []
for x in chosen:
    acq = x.get("acquisition") or {}
    rows.append({"paper_id": x["candidate_id"], "doi": x.get("doi"), "title": x["canonical_title"], "metadata_tier": (x.get("relevance") or {}).get("decision"), "reason_codes": (x.get("relevance") or {}).get("reason_codes", []), "host_relation_machine_hidden": (x.get("relevance") or {}).get("host_relation"), "acquisition_status": acq.get("state"), "pdf_path": acq.get("local_path"), "fulltext_available": bool(acq.get("local_path")), "machine_verdict_hidden": None, "sampling_stratum": (x.get("relevance") or {}).get("decision"), "annotator_A": None, "annotator_B": None, "adjudicated": None})
out = {"status": "GOLD_PENDING_HUMAN_ANNOTATION", "schema_version": "literature-gold-batch/1.1", "count": len(rows), "papers": rows}
(DATA / "literature_verification_gold_batch_v1.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
fields = ["paper_id", "doi", "title", "metadata_tier", "acquisition_status", "pdf_path", "sampling_stratum", "annotator", "identity_correct", "host_relation", "target_product_correct", "primary_research", "engineering_intervention_present", "experimental_validation_present", "eligibility_label", "relevance_grade", "annotation_confidence", "notes"]
with (DATA / "literature_verification_gold_batch_v1.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader()
    for row in rows:
        for annotator in ("A", "B"):
            writer.writerow({k: row.get(k) for k in fields} | {"annotator": annotator})
print(len(rows))
