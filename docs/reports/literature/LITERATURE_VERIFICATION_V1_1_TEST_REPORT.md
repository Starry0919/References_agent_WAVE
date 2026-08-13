# Literature Verification v1.1 Test Report

Target tests覆盖canonical headings/anchors、References/future硬规则、measured vs cited、identity score breakdown、wrong PDF、review/adjacent product及既有router。

命令：`python -m pytest tests/literature_discovery tests/literature_verification tests/paper_extraction tests/evidence_retrieval -q`。最终：220 passed，1个既有FastAPI TestClient弃用warning，16.57s。

首轮为219 passed/1 failed：Methods evidence context跨section读到Discussion的`future`，使implemented被误降级。已把context window裁剪到来源section，重跑全绿。外部parser安装失败不计production regression。
