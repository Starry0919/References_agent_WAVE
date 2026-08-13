# Literature Verification v1.1 Hardening Audit

现状Skill05已保留Markdown、section map、figure/table/reference map、parser provenance；Skill06有clean JSON与段落映射；Skill08 anchor使用paragraph/figure/table ID。替换parser会破坏这些坐标，因此本轮只增parser-neutral adapter。

主要v1风险：identity title比较脆弱；verifier整段regex不排除References；future/intervention与measured/cited区分不足；gold batch为空。v1.1已实现多信号identity、section硬规则、稳定quote-hash anchor、57篇真实待标注batch与pending runner。未改Skill07/08/DDR，未写knowledge。
