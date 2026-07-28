import tempfile
from pathlib import Path

from helpers import document_artifact
from skill import ScientificMarkdownCleaner


def test_same_source_and_rules_reuse_immutable_artifact():
    markdown = "# Results\n\nFigure 1: Production increased.\n"
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first = ScientificMarkdownCleaner(output_root=root).execute(
            {"document_artifact": document_artifact(markdown)}
        )
        second = ScientificMarkdownCleaner(output_root=root).execute(
            {"document_artifact": document_artifact(markdown)}
        )
        assert first["status"] in {"succeeded", "succeeded_with_warnings"}
        assert second["status"] in {"succeeded", "succeeded_with_warnings"}
        assert first["artifacts"] == second["artifacts"]
