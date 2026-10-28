# Sentence-BERT 阅读笔记

状态：书目、官方 BibTeX 与公开摘要已核实；全文精读尚未完成。核实日期：2026-10-22。

文献：Nils Reimers and Iryna Gurevych. *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP-IJCNLP 2019, pp. 3982–3992. DOI：[10.18653/v1/D19-1410](https://doi.org/10.18653/v1/D19-1410)。引用键：`reimers-gurevych-2019-sentence`。

依据：[ACL Anthology](https://aclanthology.org/D19-1410/)页面和官方 BibTeX 已保存到 `references/literature/verification/`。

摘要描述了使用孪生和三元组网络结构获得句向量，并以余弦相似度比较，从而避免对大量句子对逐一进行联合编码。原文摘要中的性能数字具有其特定实验条件，本项目不引用为本机速度或 CAD 检索效果。

与本课题的关系：支持后续构建向量基线的技术背景，但该论文不能直接证明指定多语言模型在俄英 NURBS 文档上的效果。Sentence-BERT 方法论文与 `multilingual-e5-small` 模型也不是同一个来源；后续使用 E5 必须另外核查其论文、模型卡、许可、版本和输入要求。

汇报要点：向量检索允许基于表示相似度搜索，但仍会误匹配。当前只完成 BM25，不应称已经实现语义搜索。
