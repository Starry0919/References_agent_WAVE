# 论文清洗 2.0 — 配置指南

清洗 MinerU 生成的论文 Markdown 文件：移除图片链接、整理 Figure 描述到文末、标准化文档结构。**免费，无需 API Key。**

---

## 1. 前置条件

- 已安装 [Claude Code](https://claude.ai/code)（CLI 版）
- 论文 `.md` 文件由 [MinerU](https://github.com/opendatalab/MinerU) 转换生成

无需注册任何额外服务。

---

## 2. 安装技能

将技能文件放到 Claude Code 的 commands 目录：

```bash
# 创建目录（如果不存在）
mkdir -p ~/.claude/commands/论文清洗2.0

# 复制技能文件
cp 论文清洗2.0.md ~/.claude/commands/论文清洗2.0/SKILL.md
```

---

## 3. 在 CLAUDE.md 中注册技能（推荐）

在你的项目 `CLAUDE.md` 或全局 `~/.claude/CLAUDE.md` 中添加：

```markdown
## 可用技能
- 论文清洗2.0：清洗 MinerU 生成的论文 MD 文件
```

---

## 4. 测试

重启 Claude Code 后，直接说：

```
帮我用2.0清洗这篇论文：/path/to/your/paper.md
```

或者：

```
论文清洗2.0 /path/to/your/paper.md
```

---

## 使用示例

```
论文清洗2.0 ~/Downloads/nature_paper.md
用新版清洗MD ~/Desktop/arxiv2024.md
帮我用2.0清洗这篇论文 /Users/你的用户名/papers/cell_paper.md
```

---

## 清洗后的文档结构

```
标题
Abstract / SUMMARY
Introduction
... 正文各 section ...
Acknowledgements（若有）
References
## Authors（作者名 + 机构 + 通讯作者 + DOI）
## Figure Descriptions
```

---

## 输出规则

| 项目 | 说明 |
|------|------|
| 原文件 | **不修改**，保持原样 |
| 输出文件 | 原文件名 + `_cleaned.md` 后缀，同目录 |
| 图片链接 | 全部删除（含前置编码数字） |
| Figure 描述 | 从正文移除，汇总到文末 `## Figure Descriptions` |
| 作者/机构信息 | 从文档开头移至文末 References 之后 |
| 正文内容 | 一字不改，只做结构整理 |

---

## 常见问题

**Q: 支持哪些 Markdown 文件？**  
A: 主要针对 MinerU 转换的论文 MD，其他工具生成的 MD 也可尝试，但效果可能有差异。

**Q: 会丢失内容吗？**  
A: 不会。所有修改都在 `_cleaned.md` 上进行，原文件不触碰。Figure 描述只是搬移到文末，不删除。

**Q: HTML 标签（`<sup>`、`<sub>`）会被乱改吗？**  
A: 不会。技能有硬性约束：原文有的标签原样保留，绝不凭空新增。

**Q: 处理完需要多久？**  
A: 取决于论文长度，一般 1–3 分钟。Claude 会逐步操作并报告进度。

**Q: 可以处理中文论文吗？**  
A: 可以，技能对中英文均适用。
