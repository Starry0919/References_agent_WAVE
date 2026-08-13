# Canonical Document v1.1 Implementation Report

新增 `harness/literature_verification/canonical.py`，提供 parser-neutral `CanonicalDocument`：document/paper/parser/version/source SHA、pages、sections、tables、figures、anchors、text。Markdown adapter识别 Abstract/Introduction/Methods/Results/Discussion/Conclusion/Supplement/References。

稳定 anchor由 `paper_id + section_id + normalized quote hash` 构成，同时保留 local char start/end；重新解析后可先按 quote hash+section/page对齐，不只依赖绝对 offset。该层是 additive adapter，不改 Skill05/06 contract；未来 MinerU/OpenDataLoader/MegaParse只需各自 adapter。
