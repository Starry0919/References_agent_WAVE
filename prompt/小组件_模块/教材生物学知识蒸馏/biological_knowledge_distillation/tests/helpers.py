import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
MODULE_ROOT = PACKAGE_ROOT.parent
for p in (str(MODULE_ROOT), str(PACKAGE_ROOT / "skills")):
    if p not in sys.path:
        sys.path.insert(0, p)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def read_fixture(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


def source(raw_text, **biblio_overrides):
    biblio = {
        "title": "Principles of Metabolic Engineering (Synthetic Fixture Edition)",
        "authors_or_editors": ["A. Tester"],
        "publisher": "Fixture Press",
        "publication_year": 2020,
        "isbn": ["000-0-00-000000-0"],
        "edition": "1st",
        "chapter": "7",
        "source_type": "textbook",
    }
    biblio.update(biblio_overrides)
    return {"source_ref_type": "text", "raw_text": raw_text, "bibliographic": biblio}


def request(sources, **overrides):
    base = {
        "task_id": "test-task",
        "user_request": "Distill engineering-relevant biological knowledge from this excerpt.",
        "input_sources": sources,
        "target_domain": ["metabolic engineering"],
        "target_organism": [],
        "target_strain": [],
        "target_engineering_goal": ["increase pathway flux"],
        "requested_output_level": ["level3_engineering_distillation"],
        "source_languages": [],
        "output_languages": ["zh", "en"],
        "quality_requirement": "",
        "requires_cross_source_fusion": False,
        "requires_paper_case_linking": False,
        "requires_frontend_adapter": False,
        "mode": {"automatic": True, "human_review": True},
    }
    base.update(overrides)
    return base
