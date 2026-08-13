# Literature Verification Calibration Report

## Status

`GOLD_PENDING_HUMAN_ANNOTATION`

目前没有双人独立且已裁决的人类金标准，因此没有报告虚假的 precision、recall、F1、nDCG 或 calibration error。

## Bootstrap evidence

工程回归集覆盖 exact K-12、显式 derivative、未解析 E. coli、错误宿主、相邻产品、review、实际 intervention、future proposal、定量结果、model-only 和 enzyme-only。它只能防回归，不能估计真实语料性能。

Evaluator 已实现 missing-label gate、confusion matrix、binary metrics、Precision@5/10/20 和 nDCG@10/20。下一步从既有 92 candidates 分层抽 50–100 篇，A/B 独立标注并 adjudicate 后，再运行 threshold sweep、reliability bins 和 error slices。
