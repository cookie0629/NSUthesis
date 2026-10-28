# RAG 阅读笔记

状态：NeurIPS 官方书目与摘要已核实；全文精读尚未完成。核实日期：2026-10-22。

文献：Patrick Lewis 等，*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. Advances in Neural Information Processing Systems, 33, 9459–9474, 2020。完整作者见统一 BibTeX，引用键 `lewis2020rag`。

依据：[NeurIPS 官方页面](https://papers.nips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html)及本地 `references/literature/verification/rag_neurips.html`。arXiv 抓取因证书校验失败，保留失败记录后改用官方会议页面，没有关闭 TLS 验证。

摘要描述将预训练 seq2seq 参数记忆与通过神经检索器访问的 Wikipedia 稠密索引结合，并比较整段生成共享检索证据与逐 token 使用不同片段的两类形式。论文中的训练方案和开放域问答结果，不能直接等同于本项目未来的提示式引用回答。

本课题先评价检索，再分析答案是否由证据支持。RAG 的存在不保证引用正确，也不证明领域本体有用。当前原型只输出检索片段，没有生成答案，正式答辩必须区分二者。

汇报要点：本轮先保证“找到了什么、从哪里找到、是否足够”的可核查性；回答层将在检索基线之后实现。
