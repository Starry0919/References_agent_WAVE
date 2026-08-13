# Supplement Pipeline Specification

Supported intake types are PDF, DOCX, XLS/XLSX, CSV/TSV, TXT and ZIP. Every artifact records paper, source reference, original filename, SHA-256, type, parser version, storage reference and status. CSV/TSV preserve header/row/column structure; original spreadsheets are retained to preserve workbook/sheet structure.

ZIP ingestion rejects traversal/absolute paths, executables, excessive member counts, excessive expanded size and suspicious compression ratios; contents are never executed. Missing states are `SUPPLEMENT_NOT_FOUND`, `SUPPLEMENT_LINK_UNAVAILABLE` and `SUPPLEMENT_ACCESS_FAILED`. URLs are never invented.

This is additive storage only. `skill07_supplement_injection = DISABLED_BY_DEFAULT`; no supplement changes current production Skill07 input.
