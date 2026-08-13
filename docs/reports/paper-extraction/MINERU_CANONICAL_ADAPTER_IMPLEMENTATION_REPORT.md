# MinerU Canonical Adapter Implementation

`from_skill06()` maps real Skill06 clean JSON directly: paper/parser/version metadata, ordered section IDs/headings/content, tables, figures and source checksum into CanonicalDocument without flattening before structure extraction. Skill05 owns source PDF/parser provenance; Skill06 owns clean sections/paragraph-compatible text and maps. Existing contracts are unmodified.
