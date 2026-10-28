# 第一轮原型：安装、运行与复现

版本：2026-10-22。已实测 Windows、Python 3.13.17；业务代码与测试仅使用标准库。当前为 BM25 开发原型，不包含向量模型、LLM 或 OCCT 几何算法执行环境。

## 环境

当前可直接使用项目内 `.venv\Scripts\python.exe`，无需激活。它基于 `.runtime\nuget-python313\tools\python.exe`，来源为 Python 官方 NuGet 分发包。下载地址、时间和 SHA-256 见 `references/literature/verification/python_runtime.json`。

Python Launcher 中原有 3.13 注册路径无法启动。曾尝试官方签名安装器并显式指定项目目录，但安装器日志显示沿用了旧安装记录，返回 0 后项目目标仍没有解释器，因此该尝试不作为成功安装。没有继续修复系统注册项；改用直接解包的运行时。不要使用 `py -3.13` 作为本次复现命令。

如需重建 `.venv`，先确保项目中的 NuGet 运行时存在，再从项目根目录运行：

```powershell
& .\scripts\setup_environment.ps1
```

脚本用 Python 3.13 创建本地虚拟环境，并在其 site-packages 中添加指向本项目 `src` 的 `.pth` 文件。此注册方式不需要下载打包依赖；移动整个项目后需重新运行脚本。项目不依赖全局 `PYTHONPATH`。如果本地运行时不存在，脚本尝试已安装的 `py -3.13`，无法运行时明确失败。

重新获取运行时可从 [Python 官方 Windows 说明](https://docs.python.org/3.13/using/windows.html#the-nuget-org-packages)确认 NuGet 分发方式，下载 `python` 包 3.13.17 并解包到上述目录。运行时及安装包被 `.gitignore` 排除，不能只复制项目源码就假定环境已经存在。

## 日常命令

以下命令均在 `F:\thesis` 执行：

```powershell
& .\.venv\Scripts\python.exe -B -m nurbs_knowledge validate
& .\.venv\Scripts\python.exe -B -m nurbs_knowledge search --query "knot multiplicity continuity" --top-k 5
& .\.venv\Scripts\python.exe -B -m nurbs_knowledge search --query "surface tolerance" --output reports/demos/my_search.json
& .\.venv\Scripts\python.exe -B -m nurbs_knowledge demo
& .\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

`search` 输出 JSON，包含原始问题、排名、原文、得分、来源标题、链接和行号；`--output` 拒绝覆盖已有文件。`demo` 使用十道英文开发题，每次创建独立目录，保存 manifest、逐问题结果与词项匹配数量。该数量不是准确率、召回率或相关性判断。

退出码：0 表示命令正常完成（包括无匹配）；1 表示语料或问题校验失败；2 表示参数、配置、输出文件等错误。空问题或纯标点问题报错；无共同词项的有效问题返回 `no_match` 和空列表。

## 数据重建

原始下载默认不进入 Git，完整原文目前保存在 `data/raw/occt-7.9.0/`。若缺失，可联网重新获取：

```powershell
& .\.venv\Scripts\python.exe -B scripts/fetch_research_sources.py
& .\.venv\Scripts\python.exe -B scripts/build_occt_corpus.py
& .\.venv\Scripts\python.exe -B -m nurbs_knowledge validate
```

下载脚本保留成功和失败状态，不绕过 HTTPS 证书校验。构建脚本要求下载提交与片段选择中的固定提交一致；核对原始文件及许可哈希后才写出来源登记和片段。已有运行目录不会被重建命令修改。重新下载会更新工作区的获取时间和书目核验清单，应保留需要比较的旧清单副本。

当前校验器针对本轮数据支持固定 GitHub URL 加 `#Lstart-Lend` 的源码注释定位，并逐字比对原文。网页锚点、PDF 页码等是后续扩展，不能直接混入现有格式。

## 排序与限制

每个片段的正文单独参与 BM25；标题是定位元数据，本轮不参与打分。文档与查询均执行 NFKC、casefold 和 Unicode `\w+` 分词，保留下划线；不做停用词过滤、词干化、翻译或术语扩展。原文仅移除 `//!` 标记并统一换行和 NFC，以保留引用内容。

采用 `idf = log(1 + (N - df + 0.5)/(df + 0.5))`，`k1=1.5`，`b=0.75`。查询词去重，文档长度以本程序词项数计算，不能等同于嵌入模型 token 数。按得分降序、片段 ID 升序排序，仅保留正分结果。参数是初始默认值，未调优。

计时分别记录启动后的校验/索引构建时间与查询分词/打分时间；不包含完整进程启动时间。这里只保存开发演示，不进行正式三次预热效率比较，也不输出 nDCG 等需要人工标签的指标。
