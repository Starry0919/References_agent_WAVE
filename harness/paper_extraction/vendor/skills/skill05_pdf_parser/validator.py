from pathlib import Path

try:
    from .schema import sha256_file
except ImportError:
    from schema import sha256_file


def validate_input_artifact(artifact):
    if artifact.get("processing_status") != "verified":
        return False, "input_not_verified"
    file_info = artifact.get("file_information", {})
    path = Path(file_info.get("path", ""))
    expected = artifact.get("integrity", {}).get("checksum_value")
    if not path.is_file() or not expected:
        return False, "pdf_unreadable"
    if sha256_file(path) != expected:
        return False, "checksum_mismatch"
    return True, None


def quality_report(markdown, sections, figures, tables, content_list):
    text_length = len(markdown.strip())
    major = {"abstract", "introduction", "results", "discussion", "methods", "materials and methods", "references"}
    found = {v["title"].casefold() for v in sections}
    major_count = len(major & found)
    content_items = len(content_list or [])
    blank_ratio = markdown.count("\n\n\n") / max(1, markdown.count("\n"))
    missing = []
    if major_count == 0:
        missing.append("major_sections_unrecognized")
    if text_length < 100:
        missing.append("very_low_text_volume")
    return {
        "text_extraction_quality": round(min(1.0, text_length / 5000) * max(0.0, 1.0 - blank_ratio), 4),
        "table_quality": 1.0 if all(v["markdown_preserved"] for v in tables) else (0.5 if tables else 1.0),
        "figure_quality": 1.0 if all(v["caption"] != "unknown" for v in figures) else (0.5 if figures else 1.0),
        "structure_quality": round(min(1.0, major_count / 4), 4),
        "content_items_detected": content_items,
        "missing_content": missing
    }
