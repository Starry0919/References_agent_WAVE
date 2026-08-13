# Literature Gold Annotation Workbench

1. Annotator A使用CSV中A行独立标注，禁止查看`machine_*_hidden`。
2. Annotator B独立标注B行，不查看A。
3. 导回JSON对应annotator_A/B；runner计算分歧与agreement。
4. Adjudicator仅在A/B完成后查看分歧并填`adjudicated`。
5. 只有adjudicated记录进入gold metrics；unknown/null不强迫判断。

Batch共57篇，按Tier2 20、Tier3 20、background 15、exclude最多5（实际来源数量决定）分层，包含reason codes、acquisition/fulltext状态及隐藏机器字段。文件：`literature_verification_gold_batch_v1.json/.csv`。
