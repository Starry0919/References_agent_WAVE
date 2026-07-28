from datetime import datetime, timezone


def fixed_clock():
    return datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


def clean_artifact(section_paragraphs, figures=None, tables=None):
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
        "document_metadata": {
            "paper_id": "paper:test", "title": "Experimental paper",
            "parser": "MinerU", "clean_markdown_sha256": "abc"
        },
        "clean_json_path": None,
        "structure_map": {"sections": sections, "paragraphs": paragraphs},
        "figure_map": {"figures": figures or []},
        "table_map": {"tables": tables or []},
        "citation_map": {"citations": []}
    }


COMPLETE = clean_artifact([
    ("Abstract", [
        "We investigated whether pta deletion improves succinate production in Escherichia coli."
    ]),
    ("Materials and Methods", [
        "Escherichia coli K-12 MG1655 carrying Δpta was constructed by gene knockout.",
        "The WT served as a control and the mutant was the experimental group.",
        "Cells were cultured in M9 medium with glucose at 37°C for 12 h in 50 mL volume at 220 rpm until OD600 = 0.8.",
        "IPTG 0.1 mM was added and experiments were performed with three biological replicates.",
        "Succinate was measured by HPLC and data were analyzed using ANOVA."
    ]),
    ("Results", [
        "Succinate production increased significantly in the mutant.",
        "These results demonstrate that pta deletion improved succinate production."
    ])
])

