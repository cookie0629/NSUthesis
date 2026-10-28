# 研究数据

更新：2026-10-22。当前为首批开发语料，尚未冻结，不是完成的正式实验数据集。

| 路径 | 内容 |
| --- | --- |
| `sources/registry.jsonl` | 六个 OCCT 7.9.0 官方头文件文档来源，含许可、版本、提交、原文与哈希 |
| `raw/occt-7.9.0/` | 六份完整原文件及许可/例外文本；默认不纳入 Git |
| `processed/chunks.jsonl` | 25 个完整段落或 API 注释片段，带固定提交的原文行号 |
| `evaluation/dev_questions.jsonl` | 十道英文合成开发题，五类各两题，待人工复核 |
| `ontology/seed.json` | 仍为 `empty_scaffold`；未建立审核过的概念或关系 |
| `interim/`、`indexes/` | 尚无持久化产物；BM25 目前在内存中构建 |

来源依据及限制见[语料核查](../docs/07_first_corpus_review_zh.md)，数据重建与命令见[运行说明](../docs/06_running_zh.md)。每个片段可对应固定文件中的行范围；文本只移除注释标记，保留原句和限定条件。当前只支持源码行号定位，未实现 PDF 或网页的通用抽取。

来源 `approved` 表示助手依据文件明确许可完成了本地使用检查，详细依据保存在记录中；没有独立人工审核。正式分享前仍应按拟分享范围核对许可义务。所有开发问题 `origin=synthetic`、`review_status=pending_human_review`，不伪装成真实企业任务或专家标签。

独立测试题仍由评估负责人另行管理，本轮没有创建或读取。原语料规范继续有效；英文开发题不是对俄语正式评估方案的替换。
