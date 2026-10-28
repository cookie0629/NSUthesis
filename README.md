# 面向 NURBS 曲面建模与恢复的本体增强知识检索

论文题目：**Разработка средств поддержки онтологически обогащенного поиска знаний для моделирования и восстановления NURBS-поверхностей**

中文工作译名：面向 NURBS 曲面建模与恢复的本体增强知识检索支持工具开发。

本目录是论文项目的工作根目录。代码、研究资料、数据、实验、论文及阶段汇报均在这里维护。2026-10-22 已完成第一轮 BM25 原型：Python 3.13.17、六个 OCCT 来源、25 个可追溯片段、十道英文开发题，以及俄文绪论和汇报草稿。16 项测试通过，尚无正式比较实验结论。实际进度以 [项目状态](docs/project_status.md) 为准。

当前完成的是 **2026 年 9—12 月阶段项目**，同时为后续毕业论文积累材料。

## 从这里开始

| 文件 | 用途 |
| --- | --- |
| [现有材料阅读结论](docs/00_context_review_zh.md) | 前置条件、原始材料、发现的缺口 |
| [目录使用约定](docs/05_workspace_guide_zh.md) | 文件放在哪里、命名及工作流程 |
| [项目状态与下一步](docs/project_status.md) | 已完成事项、待办与阶段验收 |
| [安装、运行与复现](docs/06_running_zh.md) | 环境、validate/search/demo 命令、算法与限制 |
| [本轮演示证据](reports/demos/README.md) | 成功、失败与无匹配案例，以及测试和重复运行记录 |
| [研究与实施计划](docs/01_research_plan_zh.md) | 研究范围、日程、交付标准和风险处理 |
| [每周执行与学习指南](docs/02_execution_guide_zh.md) | 第一步怎么做、每周如何推进、验收条件 |
| [检索实验规范](docs/03_evaluation_protocol_zh.md) | 对照组、测试集、指标、避免数据泄漏 |
| [来源登记与语料规范](docs/04_corpus_protocol_zh.md) | 文档许可、版本、切分、引用和候选来源 |
| [研究数据说明](data/README.md) | 首批开发语料、来源依据及人工复核状态 |
| [论文入口](thesis/README.md) | 俄文提纲、正文与导出位置 |
| [汇报入口](reports/README.md) | 周报、阶段报告、讲稿、幻灯片与演示 |
| [决策记录](docs/decisions.md) | 已采用的安排与仍需确认的事项 |

执行原则：先让资料可追溯、检索可评估，再加入术语扩展、关系检索和引用式回答。允许得到负面实验结果，不以改动测试集换取提升。

## 工作目录

```text
orders-client/
├── docs/                       研究规范、项目状态、决策和使用说明
├── references/                 学校要求、文献书目、阅读笔记
├── src/nurbs_knowledge/        Python 数据校验、BM25 与命令入口
├── scripts/                    数据处理、实验与检查的命令入口
├── configs/                    BM25 开发配置和原文选段范围
├── tests/                      算法、来源校验和命令测试
├── data/                       来源登记、原始资料、片段、本体、开发问题
├── experiments/                实验协议快照、运行结果、人工标注与图表
├── thesis/                     论文提纲、章节草稿、插图、最终导出
└── reports/                    周报、阶段报告、汇报讲稿、幻灯片、演示记录
```

从本目录直接运行：

```powershell
& .\.venv\Scripts\python.exe -B -m nurbs_knowledge validate
& .\.venv\Scripts\python.exe -B -m nurbs_knowledge search --query "knot multiplicity continuity"
& .\.venv\Scripts\python.exe -B -m nurbs_knowledge demo
```

下一步是复核、文献精读，以及向量与混合基线。本轮没有付费 API 调用，不把开发演示当作独立测试。
