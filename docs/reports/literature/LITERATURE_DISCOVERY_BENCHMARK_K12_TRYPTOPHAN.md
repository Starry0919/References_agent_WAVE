# Benchmark: E. coli K-12 / L-tryptophan Literature Discovery

执行日期：2026-08-12。机器可读原始结果：`literature_discovery_benchmark_k12_tryptophan.json`。

## Configuration

```yaml
host:
  species: Escherichia coli
  lineage: K-12
  derivative aliases: [MG1655, W3110, BW25113]
target: L-tryptophan
goal: increase production
domains: [metabolic engineering, synthetic biology, fermentation engineering]
sources: [OpenAlex, Crossref]
query_families: 6
queries_per_source: 6
results_per_query: 10
acquisition_budget: top 5 Tier 1/2
```

K-12 与三个 derivative aliases 分开记录；没有把它们声明为完全等价。没有设置近期年份下限，以免漏掉奠基工程论文。

## Queries

六类 query 为 exact objective、metabolic engineering、strain lineage、pathway intervention、fermentation/bioprocess、recall expansion。每类分别编译到 OpenAlex 与 Crossref，共 12 条。完整 query text、ID、rationale、target source 与 timestamp 在 JSON artifact 的 `queries` 中。

## Retrieval statistics

| Metric | Result |
|---|---:|
| Query count | 12 |
| Source count | 2 |
| OpenAlex raw hits/errors | 60 / 0 |
| Crossref raw hits/errors | 60 / 0 |
| Raw/normalized source records | 120 |
| Deduplicated canonical candidates | 92 |
| Dedup reduction | 28 records / 23.3% |

首轮运行 Crossref 因不支持的 `subtype` select 字段返回 400；adapter 修正并增加回归测试后重跑，以上是最终无来源错误结果。

## Relevance distribution

| Decision | Count |
|---|---:|
| Tier 1 direct engineering | 0 |
| Tier 2 supporting engineering | 18 |
| Tier 3 mechanistic/supporting | 32 |
| Background | 38 |
| Exclude | 4 |

没有 Tier 1 是保守且符合定义的结果：metadata 中很少同时证明 K-12/derivative、目标产品、实际工程干预和定量生产结果。缺 PDF 不会降低 scientific relevance；availability 单独记分。

## Top-15 spot check

| # | Title | DOI | Year | Tier | Host evidence | Acquisition |
|---:|---|---|---:|---|---|---|
| 1 | Development of L-tryptophan production strains by defined genetic modification in E. coli | 10.1007/s10295-011-0978-8 | 2011 | Tier 2 | related E. coli；metadata 未确认 K-12 | HTTP_ERROR |
| 2 | Metabolic control analysis of L-tryptophan producing E. coli applying targeted perturbation with shikimate | 10.1007/s00449-021-02630-7 | 2021 | Tier 2 | related E. coli；targeted perturbation/flux/fermentation evidence | ALREADY_PRESENT |
| 3 | Improvement of L-Tryptophan Production in E. coli Using Biosensor-Based Screening and Metabolic Engineering | 10.3390/fermentation11050267 | 2025 | Tier 2 | related E. coli；direct screening/engineering/production | NOT_PDF |
| 4 | Distribution and Function of Genes Concerned with Aromatic Biosynthesis in E. coli | 10.1128/jb.91.4.1494-1508.1966 | 1966 | Tier 3 | K-12 evidence in metadata；mechanistic, not direct production | not planned |
| 5 | Temporal gene-expression in E. coli K-12 biofilms | 10.1111/j.1462-2920.2006.01143.x | 2006 | Tier 3 | exact K-12 but biofilm topic | not planned |
| 6 | Metabolic Engineering and Fermentation Process Strategies for L-Tryptophan Production by E. coli | 10.3390/pr7040213 | 2019 | Tier 2 | direct topic；review/primary type still needs full verification | NOT_PDF |
| 7 | Metabolic engineering for improving L-tryptophan production in E. coli | 10.1007/s10295-018-2106-5 | 2018 | Tier 2 | direct engineering topic；strain unresolved | HTTP_ERROR |
| 8 | Tryptophan attenuator inactivation and promoter swapping to improve L-tryptophan production | 10.1186/1475-2859-11-30 | 2012 | Tier 2 | intervention and target production explicit | not planned |
| 9 | Engineering Improves Enzymatic Synthesis of L-Tryptophan by Tryptophan Synthase from E. coli | 10.3390/microorganisms8040519 | 2020 | Tier 2 | enzyme/biocatalysis evidence, not necessarily strain engineering | not planned |
| 10 | Formation of Aromatic Amino Acid Pools in E. coli K-12 | 10.1128/jb.104.1.177-188.1970 | 1970 | Tier 3 | exact K-12; mechanistic pool study | not planned |
| 11 | Tunable switch mediated shikimate biosynthesis in engineered E. coli | 10.1038/srep29745 | 2016 | Background | derivative evidence, but target is shikimate | not planned |
| 12 | Deletion of pgi alters tryptophan biosynthesis in engineered E. coli | 10.1128/aem.57.10.2995-2999.1991 | 1991 | Tier 2 | intervention/product evidence; strain unresolved | not planned |
| 13 | Laboratory evolution and rational engineering of GalP/Glk-dependent E. coli for L-tryptophan | 10.1016/j.mec.2021.e00167 | 2021 | Tier 2 | evolution/engineering/yield/productivity explicit | not planned |
| 14 | Acetate pathway modification and cell recycling to increase L-tryptophan production | 10.1371/journal.pone.0179240 | 2017 | Tier 2 | pathway + process intervention explicit | not planned |
| 15 | Feed-forward regulation used in metabolic engineering for tryptophan bioproduction | 10.1016/j.ymben.2018.05.001 | 2018 | Tier 2 | regulation/engineering/bioproduction explicit | not planned |

“why relevant”、各分项分数、reason codes、source records 和 raw provenance 均保存在 JSON，不以本表的人工摘要替代机器记录。

## False-positive analysis

live spot check 发现并处理：

- K-12 biofilm 和基础芳香族代谢论文：初版误进 Tier 2；收紧 title product/engineering gate 后降至 Tier 3，仍应在后续模型/人工精排进一步下调 biofilm 论文。
- 5-hydroxytryptophan 工程论文：substring 会误认 tryptophan；现在标记 `OTHER_PRODUCT_TARGET` 并降为 Background。
- indole production 论文：tryptophan 是底物而非目标产品；现在标记 `OTHER_PRODUCT_TARGET` 并降为 Background。
- shikimate production：有 K-12 derivative/工程/生产信号，但目标不同，保持 Background。
- enzymatic synthesis：与目标产物相关，但不一定是细胞工厂 strain engineering；保留 Tier 2 supporting 而非 Tier 1。

尚存风险：metadata 中 review 类型不完整、摘要包含引用/背景词、Unicode K-12 连接号变体，以及“related E. coli”无法替代全文 strain identification。

## Acquisition results

| Metric/state | Count |
|---|---:|
| Selected | 5 |
| Success/reused valid PDF | 1 |
| HTTP_ERROR | 2 |
| NOT_PDF | 2 |
| NO_OA_SOURCE | 0（OpenAlex DOI resolver 找到 URL） |

成功制品：DOI `10.1007/s00449-021-02630-7`，本地 23 页，SHA-256 为 `7e250d0e1a550109c0516084a62f062aa9b82c58a5a5320a78c2865391d5afb9`。人工/规则 spot validation 在前三页找到 DOI，并命中标题核心词 `metabolic/control/tryptophan/shikimate`。最终运行状态为 `already_present`，因为前一轮已合法获取且幂等复用；这计作 1 个 PDF success，不是重复下载。

两个 MDPI URL 返回的内容未通过 PDF 检查，明确记录 `NOT_PDF`，没有把 landing/challenge HTML 保存为论文。两个 OUP/Springer 相关地址返回 HTTP 错误。没有使用 Sci-Hub 或反爬绕过。

## Handoff

JSON artifact 的 `handoff` 包含 1 篇 ready paper、identity、relevance、source provenance、local PDF、SHA-256，以及现有 `source_type=upload` 管线可直接接受的 payload。benchmark 没有自动触发 Skill07/DDR，防止未经复核的 live 候选成为生产知识。

## Limitations

- 这不是人工金标准，不能据此宣称 Recall@K/nDCG；
- 只使用 OpenAlex + Crossref，尚未接 PubMed/Europe PMC 到新 canonical layer；
- metadata tier 不是全文 eligibility；
- acquisition 仅 5 篇小样本，不能代表总体 OA 成功率；
- benchmark 是一次时间点结果，不得写死为生产知识。
