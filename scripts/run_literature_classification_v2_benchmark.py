from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "artifacts/data/literature"
REPORTS = ROOT / "docs/reports/literature"
sys.path.insert(0, str(ROOT))

from harness.literature_discovery.classification import classify
from harness.literature_discovery.models import PaperCandidate
from harness.literature_discovery.readiness import literature_readiness
from harness.literature_discovery.routing import ranking_score, route
from harness.literature_discovery.taxonomy import TAXONOMY


def values(c, axis): return [x.value for x in getattr(c, axis).labels]


def main():
    source = json.loads((DATA / "literature_discovery_benchmark_k12_tryptophan.json").read_text(encoding="utf-8"))
    recovery_path = ROOT / "artifacts/data/gold/gold_final_fulltext_recovery.json"
    recovery = json.loads(recovery_path.read_text(encoding="utf-8")) if recovery_path.exists() else {"rows": []}
    paths = {x["paper_id"]: x["local_path"] for x in recovery["rows"] if x.get("local_path")}
    rows, distributions = [], {x: Counter() for x in ["publication_form", "research_design", "engineering_modes", "evidence_modalities", "knowledge_contributions", "evidence_strength", "route"]}
    reviews = []
    for raw in source["candidates"]:
        candidate = PaperCandidate.model_validate(raw)
        metadata = classify(candidate)
        fulltext = None
        if candidate.candidate_id in paths and Path(paths[candidate.candidate_id]).is_file():
            try:
                reader = PdfReader(paths[candidate.candidate_id])
                fulltext = "\n".join((p.extract_text() or "") for p in reader.pages)
            except Exception:
                fulltext = None
        final = classify(candidate, fulltext, metadata) if fulltext else metadata
        candidate.metadata_classification = metadata.model_dump()
        candidate.fulltext_classification = final.model_dump() if fulltext else None
        candidate.final_classification = final.model_dump()
        candidate.route = route(final); candidate.route_confidence = candidate.route["confidence"]
        candidate.ranking_score_v2 = ranking_score(candidate)
        axes = {a: values(final, a) for a in distributions if a != "route"}
        for axis, labels in axes.items(): distributions[axis].update(labels)
        distributions["route"].update([candidate.route["value"]])
        row = {"paper_id": candidate.candidate_id, "doi": candidate.doi, "title": candidate.canonical_title,
               "metadata_classification": metadata.model_dump(), "fulltext_classification": final.model_dump() if fulltext else None,
               "final_classification": final.model_dump(), "route": candidate.route,
               "ranking_score_v2": candidate.ranking_score_v2, "fulltext_refined": bool(fulltext),
               "classification_conflict": final.classification_conflict}
        rows.append(row)
        if candidate.route["value"] == "REVIEW_SYNTHESIS_ROUTE" or any("REVIEW" in x or x == "META_ANALYSIS" for x in axes["publication_form"]):
            reviews.append({"paper_id": candidate.candidate_id, "title": candidate.canonical_title, "doi": candidate.doi,
                            "metadata_signals": values(metadata, "publication_form"), "abstract_available": bool(candidate.abstract),
                            "fulltext_signals": values(final, "publication_form") if fulltext else [],
                            "final_review_subtype": axes["publication_form"],
                            "confidence": final.publication_form.labels[0].confidence, "route": candidate.route["value"],
                            "conflict": final.classification_conflict})
    rows.sort(key=lambda x: x["ranking_score_v2"], reverse=True)
    output = {"contract_version": "literature-classification-benchmark/2.0", "request": source.get("request") or source.get("configuration"),
              "raw_candidates": source.get("statistics", {}).get("raw_hits", sum(x.get("raw_hits", 0) for x in source.get("source_runs", []))),
              "deduplicated_candidates": len(rows), "classified_candidates": len(rows),
              "classification_coverage": sum(bool(x["final_classification"]) for x in rows) / max(1, len(rows)),
              "classification_conflicts": sum(x["classification_conflict"] for x in rows),
              "fulltext_refined": sum(x["fulltext_refined"] for x in rows),
              "distributions": {k: dict(v) for k,v in distributions.items()}, "rows": rows}
    (DATA / "literature_k12_tryptophan_classification_benchmark_v2.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "literature_taxonomy_v2.json").write_text(json.dumps(TAXONOMY, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "literature_readiness_v2.json").write_text(json.dumps(literature_readiness(False), ensure_ascii=False, indent=2), encoding="utf-8")
    report = ["# K-12 / L-Tryptophan Classification Benchmark v2", "", f"- Raw source hits: {output['raw_candidates']}", f"- Deduplicated/classified: {len(rows)}", f"- Coverage: {output['classification_coverage']:.1%}", f"- Full-text refined: {output['fulltext_refined']}", f"- Conflicts exposed: {output['classification_conflicts']}", "", "## Distributions", ""]
    report += [f"- {axis}: {dict(counts)}" for axis,counts in distributions.items()]
    (REPORTS / "LITERATURE_K12_TRYPTOPHAN_CLASSIFICATION_BENCHMARK_V2.md").write_text("\n".join(report)+"\n", encoding="utf-8")
    review_lines = ["# Literature Review Classification Audit", "", f"Review-like records: {len(reviews)}", "", "| Title | DOI | Metadata signals | Fulltext signals | Final subtype | Confidence | Route | Conflict |", "|---|---|---|---|---|---|---|---|"]
    for x in reviews: review_lines.append(f"| {x['title'].replace('|','/')} | {x['doi'] or ''} | {', '.join(x['metadata_signals'])} | {', '.join(x['fulltext_signals'])} | {', '.join(x['final_review_subtype'])} | {x['confidence']} | {x['route']} | {x['conflict']} |")
    review_lines += ["", "False-review and missed-review inspection is deterministic and provenance-visible; generic REVIEW is retained when a subtype is not explicit.", "Citation expansion is documented as P1 because normalized reference identifiers are not uniformly present in the current discovery records."]
    (REPORTS / "LITERATURE_REVIEW_CLASSIFICATION_AUDIT.md").write_text("\n".join(review_lines)+"\n", encoding="utf-8")
    print(json.dumps({k: output[k] for k in ["raw_candidates", "deduplicated_candidates", "classified_candidates", "classification_conflicts", "fulltext_refined"]}, indent=2))


if __name__ == "__main__": main()
