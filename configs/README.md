# 配置

`bm25.json` 固定本轮开发默认值：k1=1.5、b=0.75、正值 IDF、统一 Unicode 分词、查询词去重和 top_k=5。参数尚未调优或用于正式测试。

`occt_excerpt_selection.json` 固定 OCCT 提交及人工辅助选择的原文行范围，构建脚本据此生成 25 个片段。修改行范围必须核对完整段落和限定条件；修改后重新构建、校验和保存新运行。

后续仍按 K、V、H、H+T、H+R、H+T+R 六组设计实施。向量模型、RRF 和关系参数尚未确定。正式冻结副本及哈希放入 `experiments/protocols/`。
