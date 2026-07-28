# Tests

- Normal：完整研究请求生成合法 ResearchIntent 和布尔检索式。
- Missing information：缺少生物和菌株时输出 null/unknown，不推断为 E. coli。
- Invalid input：空请求返回 `EDX-VAL-001`。
- Failure recovery：日志组件失败不影响解析，重复输入产生稳定输出。

运行：`python -m unittest discover -s tests -v`

