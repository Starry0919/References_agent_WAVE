# Literature Entity Resolution v3 Report

Resolution precedence is exact DOI, shared PMID/PMCID/OpenAlex ID, normalized title plus year/author agreement, then conservative fuzzy title matching. All source records remain attached to the canonical candidate.

SAME_DOI_DIFFERENT_TITLE, TITLE_MATCH_DIFFERENT_YEAR, AUTHOR_CONFLICT, and IDENTIFIER_CONFLICT are represented as merge conflicts. Identifier conflicts split records instead of silently merging them.

