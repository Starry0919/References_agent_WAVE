---
name: literature-search
description: 学术文献检索。本机默认走 OpenAlex + CrossRef（纯标准库、无需 API key），返回结构化 JSON（单个数组，title/authors/year/venue/abstract/citations/DOI/BibTeX）。可选 arXiv 源码下载。Semantic Scholar / arXiv 搜索 / 自动 merge 需另装 deep-research skill（本机未装）。用于找论文、查相关工作、凑书目；可作为 paper-writing-workflow「01-sources」步骤的发现引擎。触发：'文献检索'/'找论文'/'search literature'/'查相关工作'/给一个检索词说要找文献。
argument-hint: [search-query]
---

# Literature Search（step 01-sources · .json 输出）

跨学术数据库发现相关论文，拿到 DOI 与书目元数据。本 skill 是 paper-writing-workflow **步骤 01-sources 的发现引擎**，脚本就在本步 `scripts/` 下。

> **输出格式**：单个 JSON 数组（`json.dump(..., indent=2)`）——契合本 workflow「机器消费的产物用 JSON」的约定（同 `papers.json` / `cards.json`）。
> **边界**：它只替你干 01 的「发现」机械活（广撒网 + 拿 DOI/书目）；按 claim 挑强相关、核验覆盖缺口、套引用资格规则仍由人主导（见文末「接入 paper-writing-workflow」）。

> **环境说明（本机）**
> - 本 skill 自带、且**无需 API key、纯 Python 标准库**就能跑的脚本只有三个：`scripts/search_openalex.py`、`scripts/search_crossref.py`、`scripts/download_arxiv_source.py`。
> - **Semantic Scholar 搜索、arXiv 搜索、自动 merge、bibtex_manager 依赖 `deep-research` skill，本机未安装** → 那几条命令在装上 deep-research 之前跑不了，下面已标注为「可选」。
> - 命令里的路径**相对本 skill 目录**。若已安装到 `~/.claude/commands/literature-search/`，把 `scripts/` 换成该绝对路径即可。用系统 `python`（脚本只用标准库，任何 Python 3 均可）。
> - **Windows 编码**：`search_openalex.py` 已修为按 UTF-8 写盘（作者名带 ø/å 等不再崩，无需设 `PYTHONUTF8`）。crossref / arxiv 脚本本就 UTF-8 安全。已联网实测 OpenAlex 与 CrossRef 均正常返回。

## Input
- `$ARGUMENTS` —— 检索词（自然语言）

---

## 主力脚本（本机可直接用，无 key）

### OpenAlex —— 覆盖最广、免费、无 key（生物/组学首选）
```bash
python scripts/search_openalex.py \
  --query "QUERY" --max-results 50 --year-range 2018-2026 \
  --sort relevance_score:desc -o results_openalex.json
```
参数：`--query`(必填) · `--max-results`(默认50) · `--min-citations`(默认0) · `--year-range`(如 2018-2026) · `--type`(article / proceedings-article) · `--sort`(默认 `cited_by_count:desc`) · `--output/-o`(默认 stdout)。

> **实测要点（本机已联网验证）**：
> - **claim 定向检索请用 `--sort relevance_score:desc`**。默认的 `cited_by_count:desc` 会返回「高引但松散相关」的大综述（曾实测返回癌症/阿尔茨海默等无关高引文）；换成 relevance 后返回的全是切题论文 + 真实 DOI。
> - 也别叠太狠的 `--min-citations`（会滤掉新近的切题论文）；新文献交给 `--year-range` 控。
> - 输出字段名：引用数是 `citationCount`、年份是 `year`、链接是 `url`/`pdf_url`（不是 `cited_by_count`）。

### CrossRef —— DOI 基检索、类型覆盖最广、可直接出 BibTeX、无 key
```bash
python scripts/search_crossref.py \
  --query "QUERY" --rows 20 -o results_crossref.json
# 直接要 .bib：加 --bibtex 并把 -o 换成 .bib
```
参数：`--query`(必填) · `--rows`(默认10) · `--output/-o`(.json 或 .bib) · `--bibtex` · `--timeout`(默认30)。

### arXiv 源码下载（可选工具）—— 按标题/ID 取 .tex 源码
```bash
python scripts/download_arxiv_source.py \
  --title "Paper Title" --output-dir arxiv_papers/ --metadata
# 或直接给 ID：--arxiv-id 1706.03762
```
> 注意：这是**下载某篇 arXiv 源码**，不是关键词检索。生命科学论文多在期刊/bioRxiv，这条用得少。

---

## 可选脚本（需另装 `deep-research` skill，本机当前不可用）

装好 deep-research 后才可用；否则跳过，用 OpenAlex/CrossRef 即可。

```bash
# Semantic Scholar（偏 ML/AI，自带 BibTeX；需 deep-research + 可选 S2 key）
python ~/.claude/.../deep-research/scripts/search_semantic_scholar.py \
  --query "QUERY" --max-results 20 --year-range 2022-2026 -o results_s2.jsonl
#   如有 S2 key，通过环境变量传入：--api-key "$S2_API_KEY"（不要硬编码任何本地路径）

# arXiv 关键词搜索（最新预印本）
python ~/.claude/.../deep-research/scripts/search_arxiv.py --query "QUERY" --max-results 10 -o results_arxiv.jsonl

# 自动 merge + 去重 / BibTeX 生成
python ~/.claude/.../deep-research/scripts/paper_db.py merge --inputs *.jsonl --output merged.jsonl
python ~/.claude/.../deep-research/scripts/bibtex_manager.py --jsonl merged.jsonl --output references.bib
```

---

## 合并去重（本机无 merge 脚本时）

本机没有 `paper_db.py`。把多个 JSON 数组合并去重的两条可行路径：
1. **让 Claude 合并**：读入各 `results_*.json`（数组），先按 **DOI（小写）**判重，再按**归一化标题**判重，输出一份候选表。
2. **交给下游 workflow 的去重器**：把候选直接喂给 paper-writing-workflow 的 `01-sources/build_papers.py`，它有现成三道去重闸（DOI / 归一化标题 / 别名表），`--check` 校验。

---

## Workflow（通用）

1. 把用户的检索词扩成 2–4 条互补 query；
2. 跑 OpenAlex（主力，覆盖最广）；
3. 跑 CrossRef 补类型覆盖、拿 DOI/BibTeX；
4. （可选）装了 deep-research 再加 Semantic Scholar / arXiv；
5. 合并去重（见上）；
6. **排序按 citations + recency + relevance 为主，venue 只作背景标记**（见下）；
7. 输出结构化候选表 + 标注预印本状态。

## Venue 提示（生物/组学口径 · 仅作标记，不主导排序）

> ⚠️ 不要用 venue tier 当主排序权重——会把强势专业刊误判。**主排序 = citations + relevance + recency**；venue 只用来给读者一个背景印象。

- **旗舰**：Nature, Science, Cell, Nature Methods, Nature Biotechnology, Nature Genetics, Nature Cell Biology, Cell Systems
- **强势专业刊**：Nature Communications, PNAS, eLife, Genome Biology, Genome Research, Molecular Systems Biology, Nucleic Acids Research, Bioinformatics, Cell Reports
- **预印本**：bioRxiv / medRxiv / arXiv —— 一律标 `(preprint)`

## Output Format
候选以表格 + 详条（含 DOI / BibTeX key）呈现，**始终标注预印本状态**。

---

## 接入 paper-writing-workflow（step 01-sources）

本 skill 只替你干 **01 的「发现」机械活**（广撒网找候选 + 拿 DOI/书目）。**它不替代 01 的核心判断**——按 claim 路线图挑强相关、由人核验覆盖缺口与漏掉的奠基文献。把发现结果接进 01 的流程：

1. **先看 claim 路线图**：读 `00-context/evidence-questions.md`，按其中固定的 ClaimID/AxisID 组织检索词（一条 claim 一组 query），别漫无目的地搜。
2. **跑 OpenAlex + CrossRef** 得到候选 JSON（数组），合并去重。
3. **落进 01 的 schema**（不是直接用检索 JSON）：把保留的篇目手动写进 `sources.md`，并登记进 `papers.json` 的字段——`citation_key` / `argument_group` / `thesis_axes`(claim 路由键) / `role` / `doi` / `verification.meta_flag` / `provenance`。
4. **给每篇挂 ClaimID/axis**：对齐 `evidence-questions.md`，标明这篇是哪条论点的弹药（支持/反方/背景）。
5. **去重**：跑 `python 01-sources/build_papers.py` 重建 + `--check` 校验三道闸，确认没和已有篇目撞库。
6. **套引用资格规则**：预印本/editorial/会议素材按项目的引用资格规则处理（能否正式引用、是否只作 motivation），CrossRef/OpenAlex 的 type 与预印本标记可辅助判断。
7. **交给 step 02**：把核验过的 DOI 列表喂给 `论文下载` skill 批量下 PDF。

> 迭代补料同理：这正是 `07-iteration/SKILL.md` Step 3「必要时补语料」里的发现环节——新 source 走「01 登记 → 02→05 只跑增量 → cards.json 追加 → 记 changelog」。

## Related Skills
- 下游（同 deep-research 生态，若安装）：citation-management、literature-review、related-work-writing
- 本仓库 workflow 衔接：`02-pdfs/SKILL.md`（论文下载）、`05-distilled/SKILL.md`（精练 4.0）
