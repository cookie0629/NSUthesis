# 研究数据

当前所有数据容器为空，没有已收集语料、审核过的本体或开发题。以下路径已建立：

| 路径 | 状态与后续用途 |
| --- | --- |
| `sources/registry.jsonl` | 空文件；每行一个来源，字段遵守语料规范 |
| `raw/` | 空目录；保存获准下载的原始材料 |
| `interim/` | 空目录；保存抽取、清洗中间产物 |
| `processed/chunks.jsonl` | 空文件；每行一个有定位与来源的证据片段 |
| `indexes/` | 空目录；保存可重建的索引 |
| `ontology/seed.json` | 空概念与关系列表，状态 `empty_scaffold` |
| `evaluation/dev_questions.jsonl` | 空文件；以后仅放开发题，不是独立测试集 |

来源和片段字段见 [语料规范](../docs/04_corpus_protocol_zh.md)。空文件表示零条记录，不放会被程序误当作真实记录的占位对象。

开发题拟至少记录 `query_id`、`family_id`、`language`、`category`、`question`、`evidence_need`、`origin`、`source_note`、`review_status`；该结构待首轮校验程序实现时落实。`origin` 区分真实任务与合成场景，人工判断与助手辅助方式必须披露。

正式独立测试题由评估负责人管理，冻结前不放入开发流程。数据来源不得包含未经允许使用的实习内部资料。来源许可未确认、关系证据不足或标注未经人工核验时，均不得冒充正式研究数据。
