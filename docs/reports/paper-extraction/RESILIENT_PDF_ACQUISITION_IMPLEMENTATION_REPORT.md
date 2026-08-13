# Resilient PDF Acquisition Implementation Report

## Router

`harness/literature_discovery/resolvers.py` 实现 DOI URL encode 和优先路由：local cache → NCBI PMCID/PMC → Europe PMC → configured Unpaywall → OpenAlex → Semantic Scholar → Crossref explicit PDF links。来源 URL 去重，resolver 单独失败不终止主流程；Unpaywall 未配置时返回 `CONFIG_REQUIRED`，没有假邮箱。

`acquisition.py` 保持串行尝试、流式临时文件、50 MiB 上限、timeout、原子提交、确定性文件名和 SHA-256。合法来源全部失败时输出 `PAYWALL_OR_NO_LEGAL_FULLTEXT` 并进入 `manual_acquisition_queue.json`。未加入 Sci-Hub、LibGen、cloudscraper、TLS 关闭、登录绕过或私有 PDF URL 猜测。

## PDF identity

`pdf_identity.py` 用 pypdf 检查 expected/found DOI、题名相似度、首作者、venue、年份、页数和 SHA-256，输出 VERIFIED/PROBABLE/MISMATCH/INSUFFICIENT_METADATA。MISMATCH 文件被删除，不能进入 verifier。已有 cache 也重新核验身份。

## Live API smoke

对 `10.1007/s00449-021-02630-7` 与 `10.1186/1475-2859-11-30`：NCBI 成功解析 PMCID；OpenAlex 返回 OA location；Crossref 正常返回 metadata/links；Semantic Scholar 受限失败但主流程继续；Unpaywall 因未配置 email 明确降级。

## Acquisition benchmark

10 篇批量命令在前台等待时触及 304 秒工具上限，但采用逐篇持久 manifest，因此已完成的状态没有丢失；随后用短预算恢复未决项并重验 cache identity。最终 10 篇：5 acquired/cache success、3 NOT_PDF、1 HTTP_ERROR、1 PAYWALL_OR_NO_LEGAL_FULLTEXT；2 篇身份 VERIFIED，3 篇为 INSUFFICIENT_METADATA，均未冒充 verified。机器制品为 `resilient_acquisition_benchmark_k12_tryptophan.json`；5 个失败项在 `manual_acquisition_queue.json`。

当前身份 verified 数低于下载数，说明“合法 PDF”仍不等于“身份已充分证明”；PROBABLE/INSUFFICIENT 必须在进入知识链前复核。
