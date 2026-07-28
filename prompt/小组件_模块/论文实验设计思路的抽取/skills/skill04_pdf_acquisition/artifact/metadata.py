def paper_identity(candidate):
    return {
        "paper_id": candidate.get("paper_id"),
        "title": candidate.get("title"),
        "doi": candidate.get("identifiers", {}).get("doi"),
        "authors": list(candidate.get("authors", [])),
        "journal": candidate.get("journal"),
        "year": candidate.get("year")
    }

