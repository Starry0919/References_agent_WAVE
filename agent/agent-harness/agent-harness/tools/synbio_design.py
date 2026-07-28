# =============================================================================
# Agent 工具:synbio_design —— 调用 V0.1 合成生物学理性设计工作流
# =============================================================================
#
# 这个工具是一个薄封装:真正的流程逻辑在 workflows/synbio_v01/ 下,按顺序执行
# 任务理解 -> 文献逆向(DDR) -> 通路分析 -> 竞争通路分析 -> 关键节点分析 ->
# 基因改造设计(含优先级排序) -> 证据评估 -> Evaluator(接受/拒绝/预警) ->
# 报告生成。工具本身只负责把工作流接入 agent-harness 的 tool-calling 循环,
# 方便对话中的 Agent 直接调用整条链路。
#
# 底盘固定为 E. coli K-12(不从输入中解析,由 task_parser 自动注入)。
# V0.1 使用的是小型 mock 知识库,不连接真实文献库或数据库,且每条证据都
# 明确标注为 "mock knowledge base, not verified" —— 详见
# workflow/design/V0.1_20260720/V0.1.md。
# =============================================================================

from harness.tools import tool
from workflows.synbio_v01.workflow import run as run_synbio_workflow


@tool
def synbio_design(request: str) -> str:
    """Run the V0.1 rational metabolic engineering design workflow for E. coli K-12.

    Takes a natural-language engineering request (target product, substrate,
    engineering objective, optional constraints - in English or Chinese) and
    runs it through task understanding, literature-derived Design Decision
    Records (observation -> hypothesis -> evidence -> engineering action ->
    expected effect -> validation), pathway and competing-pathway analysis,
    key-node identification, a ranked (primary/secondary/optional) genetic
    engineering strategy, and an evaluator that accepts, rejects, or flags
    each design. Returns a structured 9-section design report explaining WHY
    each modification was chosen, not just a list of genes to change. The
    host chassis is always E. coli K-12 (fixed, not parsed from the request).
    V0.1 uses a small mock literature/pathway/competition knowledge base
    rather than live databases - see workflow/design/V0.1_20260720/V0.1.md.

    Args:
        request: Natural language design request, e.g. "Design an E. coli
            K-12 strain for improved tryptophan production from glucose" or
            "提高E.coli K-12利用葡萄糖生产色氨酸的能力,请分析限制因素并提出改造策略"。
    """
    state = run_synbio_workflow(request)
    return state.final_report
