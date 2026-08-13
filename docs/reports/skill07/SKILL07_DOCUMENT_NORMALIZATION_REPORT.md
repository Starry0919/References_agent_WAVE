# Skill07 Document Normalization Report

Date: 2026-08-12

## Canonical presentation layer

The new human-facing document layer sits between parser artifacts and both review surfaces:

`PDF → Parser → Canonical Document Representation → Scientific Literature View → Human Review / Agent Detail`

Normalization includes:

- OCR-style headings such as `a_b_s_t_r_a_c_t` → `Abstract`.
- Numbered result/method headings → semantic section labels with paper-specific subtitles.
- Markdown image syntax and image hashes removed from readable paragraphs.
- HTML tags such as `<sup>` removed.
- Internal paragraph IDs replaced by `Paragraph N`; raw locators and fingerprints remain nested provenance.
- Figure and table captions exposed as readable scientific source blocks.
- Source file paths and paragraph ID inventories removed from the Human Gold workspace payload.

## P01/P02 audit

- GOLD-P01 title: recovered from source; 160 readable paragraphs, 5 figure captions, 1 table caption.
- GOLD-P02 title: recovered from source; 115 readable paragraphs, 8 figure captions, 4 table captions.
- No `![](`, `<sup>`, or `images/` leakage was detected in canonical paragraph text.
- DOI is omitted because it is not reliably present in current clean metadata.
- GOLD-P02 has no reliably identified Abstract in the source representation; the UI reports it unavailable rather than fabricating an engineering goal.
