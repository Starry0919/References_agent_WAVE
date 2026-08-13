# Literature Verification and Acquisition Audit

## Current WAVE state

上一轮 `harness/literature_discovery` 已有 OpenAlex/Crossref discovery、六类 query、canonical candidates、metadata tiering、OA MVP 和 upload handoff。复核确认 acquisition 仅在缺 OA URL 时查 OpenAlex，PDF 校验只验证格式；没有正式 resolver provenance、身份 record 或全文 eligibility gate。Skill05 输出 Markdown/document artifact；Skill06 输出 clean JSON/maps；Skill07 抽取；Skill08 对 Skill07 claims 做不可变 evidence binding。新 gate 必须位于 Skill07/08 之前，不能替代它们。

## Third-party repository assessment

| Repo / audited HEAD | License | Core problem | Decision | Findings |
|---|---|---|---|---|
| `mohuishou/PaperDownload` `9a0ab31` | NOASSERTION | 2017 Go CNKI/万方爬取下载 | REJECT/STUDY_ONLY | 年代久、中文站点/爬虫导向、无可确认复用许可，不适合英文生物医学 OA；未复制代码 |
| `vict0rsch/PaperMemory` `f9ebed4` | MIT | 浏览器端 paper memory、venue/preprint matching、direct-download UX | STUDY_ONLY | preprint→published identity 与本地复用思想有价值；浏览器 DOM、站点规则、Puppeteer/扩展架构不适合后端；项目列有 Sci-Hub 支持，生产拒绝 |
| `dr-dumpling/paper-search-cli` `d202649` | MIT | agent-friendly TypeScript CLI search/download | ADAPT_PATTERN | CLI orchestration、cache、identifier/search separation值得借鉴；不引入 Node CLI dependency，不复制源码 |
| `j3soon/arxiv-utils` `7eaae30` | MIT | 浏览器扩展改善 arXiv 标签/文件名/搜索 | STUDY_ONLY | arXiv identity/确定性文件名思路可借鉴；Selenium/VNC 测试 workaround、浏览器扩展不适合 backend acquisition |

GitHub 元数据/API 与仓库 README/结构均实际检查；`PaperDownload` 浅克隆并查看 Go 目录。没有直接复用第三方代码，因此无需引入其许可证 notice 或依赖。用户提到的 `(1).zip` 在 Desktop 当前搜索范围未找到；此前仓库内无 `(1)` 后缀版本，但已有 `论文下载.zip`/`literature-search.zip` 已在上一轮逐脚本审计。

## Official API assessment

- Crossref `/works/{encoded DOI}`：identity/publisher/license/link metadata，绝不假定必有 PDF。
- OpenAlex `/works/doi:{encoded DOI}`：OA locations；匿名调用当前可用，但失败可降级。
- Semantic Scholar Graph：补充 OA hint；live smoke 受限失败，已隔离。
- Unpaywall：只从 `UNPAYWALL_EMAIL` 读取；未配置即 CONFIG_REQUIRED。
- NCBI ID converter：DOI→PMCID/PMID；live 两例成功。

## Architecture decision

新增 `resolvers.py`、`pdf_identity.py` 与独立 `harness/literature_verification`。这是 coarse-to-fine：metadata filter → 只获取 promising candidate → deterministic span prefilter/judge → 后续必要时 Skill07/08。缓存键由 candidate/document SHA/verifier version 可稳定构造，避免同 PDF 重复验证。

## Rejected approaches

拒绝未授权镜像、paywall/DRM 绕过、cloudscraper、TLS verification disabling、出版商私有 URL 猜测、无界并发、把 metadata availability 当 relevance、把 verifier 输出当 human gold，以及直接 shadow 写 DDR。
