from datetime import datetime, timezone


def fixed_clock():
    return datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


def document_artifact(markdown):
    return {
        "document_metadata": {
            "paper_id": "paper:test", "title": "Test paper",
            "parser": "MinerU", "parser_version": "3.4.4"
        },
        "markdown_artifact": {
            "markdown_path": "unused.md", "markdown_content": markdown
        },
        "structure_map": {"sections": []},
        "figure_map": {"figures": []},
        "table_map": {"tables": []},
        "reference_map": {"references": [], "citation_links": [], "supplements": []}
    }

