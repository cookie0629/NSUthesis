# 脚本入口

从项目根目录运行，完整步骤见[运行说明](../docs/06_running_zh.md)。

- `setup_environment.ps1`：使用本地官方 Python 3.13 运行时创建 `.venv`，注册本项目源码路径。
- `fetch_research_sources.py`：联网获取固定标签解析后的 OCCT 资料、许可和公开书目核验材料，记录下载成功或失败。
- `build_occt_corpus.py`：离线核验原文件与许可哈希，按固定提交和行范围重建来源表及片段。

日常数据校验、单次检索、批量演示使用 `python -m nurbs_knowledge validate/search/demo`。下载及构建脚本会更新工作区材料，已有演示目录不会被修改；需要保留旧数据快照时先归档，不在正式测试冻结后随意重建。
