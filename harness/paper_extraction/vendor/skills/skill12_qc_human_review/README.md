# Skill12：AI 质量控制与人工治理

面向 Skill01–11 Artifact 的治理层，执行通用及 Skill-specific QC，生成复核任务、统一 governance、继续运行策略和不可覆盖的审计事件。

## 状态

- `PASS`：继续。
- `WARNING`：继续并记录。
- `REVIEW_REQUIRED`：继续，但标记为待人工复核。
- `BLOCKED`：仅阻断当前 Artifact。

待审不会阻塞流水线。只有明确的 Schema 破坏、AI 伪造人工审批、未标记的高风险 AI 工程建议等阻断性问题才返回 `BLOCKED`。

## 人工操作

可通过 `review_action` 提交 approve、reject、modify、comment。审批类操作要求 `actor_type: human`。Modify 必须携带 before、after 和 reason，但不会覆盖原 Artifact；事件以追加方式记录。禁止修改 evidence 事实。

## 检查

通用检查包括 Schema、provenance、evidence、完整性、逻辑、幻觉与来源隔离。Skill11 额外检查 AI suggestion level、证据、uncertainty 和 approval。错误码为 GOV001–GOV005。
