# =============================================================================
# Agent 工具:synbio_design_v1 —— 调用 V1 证据落地的合成生物学设计工作流
# =============================================================================
#
# 与 tools/synbio_design.py(V0.1,基于内置 mock 知识库)不同,V1 的推理
# 完全基于磁盘上的真实 DDR 知识库(knowledge/ddr_database/*.json):检索 ->
# 生物学诊断 -> 工程设计 -> 证据落地,全部内容来自匹配到的 DDR 记录本身,
# 不允许伪造论文、作者、DOI 或实验结果(详见
# workflows/synbio_v1/modules/evidence.py)。两个工具都保留,互不覆盖。
#
# 详见 workflow/design/V0.1_20260720/V1.md。
# =============================================================================

from harness.tools import tool
from workflows.synbio_v1.workflow import run as run_synbio_v1_workflow


@tool
def synbio_design_v1(request: str) -> str:
    """Run the V1 evidence-grounded synthetic biology design workflow.

    Takes a natural-language engineering request (target product, host,
    substrate, goal - English or Chinese) and runs it through task
    understanding, DDR knowledge retrieval (from a real, on-disk knowledge
    base of literature-derived Design Decision Records), biological
    diagnosis, engineering design, and evidence grounding. Returns a
    structured 8-section report. Every recommendation traces back to a
    specific cited DDR (author/journal/year/DOI); if no DDR matches the
    problem, the tool honestly reports no evidence rather than inventing a
    citation or a design. V1's knowledge base currently covers three
    products: L-tryptophan, 1,4-butanediol, and isoprene - see
    workflow/design/V0.1_20260720/V1.md.

    Args:
        request: Natural language design request, e.g. "Design an E. coli
            K-12 strain for improved L-tryptophan production."
    """
    state = run_synbio_v1_workflow(request)
    return state.final_report
