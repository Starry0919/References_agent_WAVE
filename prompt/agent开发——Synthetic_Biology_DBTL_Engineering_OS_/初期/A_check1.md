# Synthetic Biology Agent V4 全面架构审查 Prompt

你现在不是开发者，而是一个 **Senior AI System Architect + Synthetic Biology Expert + Code Reviewer**。

请对当前代码库进行一次全面、严格、批判性的架构审查。

目标：

判断当前 Synthetic Biology Agent 是否真正达到了：

> "一个能够模拟合成生物学专家设计逻辑的 Engineering Design Agent"

而不是：

> "一个调用 LLM 生成文本的聊天机器人"

请不要默认当前实现正确。
请主动寻找缺陷、遗漏、架构问题。

---

# 一、审查原则

请遵循以下原则：

## 1. 不看页面效果优先看系统能力

不要只检查：

- UI 是否漂亮
- API 是否能运行
- 页面是否展示结果

重点检查：

Agent 是否真的具备：

- 专家workflow
- 生物工程推理
- 证据约束
- 工程设计能力
- 自动评价能力


---

## 2. 对照真实合成生物专家思考流程

一个优秀的代谢工程专家面对问题时，不会直接回答：

"敲除某基因，提高产量"

而应该按照：

```

生产目标定义

↓

宿主/底盘分析

↓

目标产物路径解析

↓

代谢网络分析

↓

限制因素识别

↓

工程策略设计

↓

证据验证

↓

风险评估

↓

实验验证方案

↓

最终设计报告

```

请检查当前 Agent 是否真正实现。


---

# 二、核心架构检查

## Check 1:
## 是否存在明确 Phase Workflow？

检查：

当前 Agent 是否存在类似：

```

Phase 0:
Problem Definition

Phase 1:
Pathway Analysis

Phase 2:
Bottleneck Identification

Phase 3:
Engineering Design

Phase 4:
Evidence Evaluation

Phase 5:
Validation Planning

Phase 6:
Final Report

```

要求：

每个 Phase 必须：

- 有明确输入
- 有明确输出
- 有状态记录
- 有失败处理


请回答：

1. 是否存在？
2. 实现在哪里？
3. 是否只是前端展示？
4. 后端是否真的执行？
5. 如果没有，如何补。


---

# 三、Synthetic Biology Expert Reasoning 检查


## Check 2:
## Agent是否真正理解生物工程问题？

检查是否存在：

### Host chassis analysis

例如：

输入：

E.coli K-12

Agent是否考虑：

- strain background
- growth characteristics
- metabolic capacity


---

### Pathway analysis

是否自动分析：

- precursor supply
- pathway enzymes
- competing pathways
- regulation
- transport
- feedback inhibition


---

### Bottleneck diagnosis

是否能够判断：

为什么产量低？

例如：

不是简单：

"overexpress gene A"

而是：

```

问题:
PEP供应不足

↓

原因:
glycolysis竞争

↓

证据:
paper/database

↓

策略:
increase precursor supply

```


检查当前系统。


---

# 四、Evidence体系检查（重点）


## Check 3:
## 是否达到老师版本 Evidence System？

必须检查。


每一个 Engineering Action 是否具有：


```

Engineering Action

↓

Trigger

↓

Biological Reason

↓

Evidence

↓

Expected Effect

↓

Validation Method

```


例如：

错误：

```

knockout gene A

```


正确：

```

Action:
delete gene A

Trigger:
carbon flux diverted away

Evidence:
Paper XXX demonstrated

Expected effect:
increase precursor availability

Validation:
13C flux analysis

```


---

检查当前：

1. 是否所有设计都有Evidence？
2. Evidence来源是什么？
3. 是否区分：

```

Hard Evidence

Soft Evidence

Hypothesis

```


要求：

如果没有，请指出。


---

# 五、Knowledge Base检查


## Check 4:

当前知识库是否支持真正工程设计？

检查是否存在：

## Literature layer

论文：

```

paper
DOI
organism
engineering strategy
result

```


---

## DDR layer

Design Decision Record:

```

Problem

Cause

Action

Evidence

Result

```


---

## Engineering Action Library


是否存在：

例如：

```

gene knockout

gene overexpression

promoter engineering

RBS optimization

transport engineering

enzyme engineering

feedback resistance mutation

heterologous pathway introduction

```


---

## Rule layer


是否存在：

例如：

```

If:
precursor limitation

Then:
increase upstream flux

```


---

判断：

当前Knowledge Base是否只是文献数据库？

还是：

真正支持推理。


---

# 六、Evaluator机制检查（重点）


## Check 5:

当前是否存在独立Evaluator？


要求：

Agent不能自己评价自己。


应该：

```

Designer Agent

↓

Evaluator Agent

↓

Revision

↓

Final Design

```


Evaluator需要检查：


## 1.
Essential gene risk

例如：

删除必需基因。


---

## 2.
Evidence validity


没有证据：

降低confidence。


---

## 3.
Biological consistency


例如：

同时：

increase pathway A

又delete pathway A


发现冲突。


---

## 4.
Engineering feasibility


例如：

理论有效：

但是实验不可执行。


---

检查：

当前是否实现。


---

# 七、Tool-grounded Reasoning检查


## Check 6:

Agent是否：

"能调用工具就不用猜"


检查：

是否支持：

## 必须：

### KEGG

用途：

pathway


---

### UniProt

用途：

protein/gene


---

### Essential gene database

用途：

gene deletion risk


---

### FBA / COBRApy

用途：

flux prediction


---

### Literature retrieval

用途：

evidence


---

检查：

1.
工具是否真实存在？

2.
是否被workflow调用？

3.
还是只是写在代码里？


---

# 八、Engineering Design页面检查


检查Frontend是否符合：

Synthetic Biology Design Studio


不是聊天页面。


---

要求：

## 1.
不要一次展示所有内容


Engineering Design应该：

顶部：

```

Design Summary

```


展示：

- target
- pathway
- major bottleneck
- top strategies


下面：

Accordion展开：

每个engineering action。


---

每个Action展示：


```

Problem

↓

Biological reasoning

↓

Engineering intervention

↓

Evidence

↓

Expected effect

↓

Validation

```


---

# 九、Final Report检查


检查最终报告是否像：

科研设计报告。


应该包含：


## Project Overview


## Metabolic Strategy


## Engineering Modification Table


## Evidence Summary


## Risk Assessment


## Validation Plan


## Limitations


如果只是：

列表输出

判定为失败。


---

# 十、3D Cell Model检查


检查：

当前模型是否符合：

E.coli。


要求：

不能只是：

随机细胞球。


至少应该体现：

- rod-shaped E.coli morphology
- membrane
- cytoplasm
- chromosome region
- engineering targets


如果没有：

提出优化方案。


---

# 十一、代码层检查


检查：

## Backend

包括：

- agent controller
- workflow engine
- tools
- knowledge retrieval
- database


检查：

是否：

模块化。


---

## Frontend

检查：

- state management
- workflow visualization
- result rendering


---

# 十二、最终输出格式


请输出：

---

# Synthetic Biology Agent V4 Audit Report


## 1. Overall Score

满分100：

分别评分：

- Workflow:
- Biological reasoning:
- Evidence:
- Knowledge Base:
- Evaluator:
- Tools:
- Frontend:
- Report:


---

## 2. Critical Missing Features

列出：

必须修复。


格式：

```

问题:

影响:

代码位置:

修改方案:

```


---

## 3. Architecture Gap Compared With Expert Agent


列出：

当前系统距离真正Synthetic Biology Expert Agent还有哪些差距。


---

## 4. V4 Upgrade Priority


分：

P0:
必须完成


P1:
重要优化


P2:
未来增强


---

## 5. 是否达到Production Level


最后回答：

当前版本：

A.
科研demo

B.
可用prototype

C.
接近专家Agent

D.
Production级


并解释原因。


