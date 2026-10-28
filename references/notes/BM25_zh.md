# BM25 阅读笔记

状态：书目信息与公开摘要已核实；不是全文精读记录。核实日期：2026-10-22。

文献：Stephen Robertson and Hugo Zaragoza. *The Probabilistic Relevance Framework: BM25 and Beyond*. Foundations and Trends in Information Retrieval, 4(1–2), 1–174, 2009. DOI：[10.1561/1500000019](https://doi.org/10.1561/1500000019)。引用键：`robertson2009bm25`。

依据：Crossref DOI 响应已保存到 `references/literature/verification/bm25_crossref.json`，含作者、题名、日期、卷期、页码和摘要。未下载或导入全文作为检索语料。

摘要将 BM25 放在概率相关性框架中讨论，并覆盖 BM25F、参数优化和非文本特征。对本课题而言，BM25 提供易解释的词项基线：共同词项、词频饱和和长度归一化参与排序。

本轮实现选择正值 IDF 变体，明确记录公式及 `k1=1.5, b=0.75`。这些是项目默认参数，不是从论文摘要得到的最优参数；本实现不等同于复制论文的全部检索模型。

局限：没有共同词项时不能凭语义或翻译建立关联；词形变化、同义词和短 API 注释可能影响排序。词项匹配结果也不自动表示证据足够。

汇报要点：BM25 的作用是提供一个能解释、能复现的比较起点。现在证明的是程序按选定公式运行，尚未证明本体增强有收益。

后续精读任务：核对原文 BM25 公式和 IDF 变体的关系，整理参数和文档长度归一化的推导；完成前不填页码级理论引文。
