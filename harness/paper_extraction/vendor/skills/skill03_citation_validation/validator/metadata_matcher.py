import re
from difflib import SequenceMatcher


def _normalize(value):
    text = re.sub(r"[^\w]+", " ", str(value or "").casefold())
    return re.sub(r"\s+", " ", text).strip()


def _surname(author):
    parts = _normalize(author).split()
    return parts[-1] if parts else ""


class MetadataMatcher:
    def compare(self, candidate, database):
        title_score = SequenceMatcher(None, _normalize(candidate.get("title")), _normalize(database.get("title"))).ratio()
        candidate_authors = {_surname(v) for v in candidate.get("authors", []) if _surname(v)}
        database_authors = {_surname(v) for v in database.get("authors", []) if _surname(v)}
        first_author_match = bool(candidate_authors and database_authors) and _surname(candidate["authors"][0]) == _surname(database["authors"][0])
        overlap = len(candidate_authors & database_authors) / max(1, len(candidate_authors))
        journal_score = SequenceMatcher(None, _normalize(candidate.get("journal")), _normalize(database.get("journal"))).ratio()
        candidate_year, database_year = candidate.get("year"), database.get("year")
        year_difference = abs(int(candidate_year) - int(database_year)) if candidate_year and database_year else None
        report = {
            "title_match": title_score >= 0.88, "title_similarity": round(title_score, 4),
            "author_match": first_author_match and overlap >= 0.5, "first_author_match": first_author_match,
            "author_overlap": round(overlap, 4),
            "journal_match": journal_score >= 0.72, "journal_similarity": round(journal_score, 4),
            "year_match": year_difference is not None and year_difference <= 1,
            "year_difference": year_difference
        }
        report["all_core_match"] = all(report[k] for k in ("title_match", "author_match", "journal_match", "year_match"))
        report["has_unknown"] = any([
            not candidate.get("authors") or not database.get("authors"),
            not candidate.get("journal") or not database.get("journal"),
            not candidate.get("year") or not database.get("year")
        ])
        return report

