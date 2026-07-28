import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL08 = Path(__file__).resolve().parents[1]
SKILLS = SKILL08.parent
if str(SKILLS) not in sys.path:
    sys.path.insert(0, str(SKILLS))

from skill07_experiment_extraction import ExperimentalDesignExtractor


def fixed_clock():
    return datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


def clean_artifact(section_paragraphs, figures=None):
    sections, paragraphs = [], []
    for section_index, (title, texts) in enumerate(section_paragraphs, 1):
        section_id = f"section_{section_index}"
        sections.append({"id": section_id, "title": title, "level": 1, "content": "\n\n".join(texts)})
        for paragraph_index, text in enumerate(texts, 1):
            paragraphs.append({
                "paragraph_id": f"{section_id}_p{paragraph_index:03d}",
                "text": text, "section": section_id
            })
    return {
        "document_metadata": {"paper_id": "paper:test", "title": "Test", "clean_markdown_sha256": "a" * 64},
        "structure_map": {"sections": sections, "paragraphs": paragraphs},
        "figure_map": {"figures": figures or []},
        "table_map": {"tables": []}, "citation_map": {"citations": []}
    }


BASE = clean_artifact([
    ("Abstract", ["We investigated whether pta deletion improves succinate production in Escherichia coli."]),
    ("Materials and Methods", [
        "Escherichia coli MG1655 carrying Δpta was constructed by gene knockout.",
        "The WT served as a control and the mutant was the experimental group.",
        "Cells were cultured in M9 medium at 37°C for 12 h at 220 rpm.",
        "Experiments used three biological replicates.",
        "Succinate was measured by HPLC and analyzed using ANOVA."
    ]),
    ("Results", ["Succinate production increased significantly in the mutant."])
])


def skill07_output(artifact=BASE):
    result = ExperimentalDesignExtractor(logger=lambda e: None, clock=fixed_clock).execute({"clean_document_artifact": artifact})
    return result["output"]

