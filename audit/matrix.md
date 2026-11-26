# 验收矩阵

审计对象：上游 https://github.com/Zerdon-me/CyberCensus ，分支 `main`，基准提交 `1192f64ec542244d2e06c12be2bdd93097ef1a4e`。  
本机检出与该 SHA 一致（作者日期 2026-11-26 10:15:02 +08:00，即香港时间）。  
只读查询时间：2026-11-26 10:24–10:28 香港时间（Asia/Hong_Kong，UTC+8）。GitHub API 返回的提交时间 `2026-11-26T02:15:02Z` 已换算为同一香港时间。  
方法：阅读该提交的源码树，并对 PyPI / OSV / GitHub 提交接口做只读查询。未运行产品代码，未安装依赖，未下载 `tools/` 二进制。

| ID | 需求 | 检查项 | 证据 | 结论 | 未覆盖 |
|---|---|---|---|---|---|
| R1 | 对本仓固定 SHA 做只读静态审计 | 记录 URL、分支、SHA、提交时间（香港时间） | 本机 `git log -1`：`1192f64ec542244d2e06c12be2bdd93097ef1a4e`，作者 `asm-tool <asm-tool@local>`，`2026-11-26T10:15:02+08:00`，说明「feat: v0.11.0 资产范围过滤…」。GitHub API（2026-11-26 10:24–10:28 香港时间）对上游与 fork `Silver-cybersec/CyberCensus` 返回同一 SHA，时间字段 `2026-11-26T02:15:02Z`（= 10:15:02 香港时间）。API 未解析出 GitHub 登录名 | 已覆盖。审计树就是该 SHA | SHA 已检出，此项无未覆盖 |
| R2 | 代码安全 | 工具能力与真实风险分开；危险执行、二进制下载执行、凭据存储、外传、暴露面；高／中／低分级 | `tool_updater.py`、`cybercensus.py`、`asm_gui.pyw`、`providers.py`、`启动界面.bat`、`run.bat`、`.github/workflows/build.yml`。条目见 `audit/findings.json` | 已覆盖已读源码。高 2、中 6、低 2，均标已确认（静态） | 未运行 GUI/CLI/更新器，故默认行为未做动态确认。仓库内无 `tools/*.exe`，发布包二进制未读。HTML 报告未做完整污点证明 |
| R3 | 架构 | 组件、信任边界、数据与权限流 | `cybercensus.py` 流水线 `run_pipeline`（约 7461–7653 行）、`providers.py`、`asm_gui.pyw` `build_args`、`tool_updater.py` | 已覆盖源码中的 CLI、GUI、平台适配、更新器、定时任务、打包脚本 | 冻结后的 `CyberCensus.exe` 不在本树，其内部打包内容未读。无容器/编排文件 |
| R4 | 供应链，单列「依赖是否恶意」 | requirements、`tools/` 二进制与 tool_updater 下载源、校验和、版本固定、仿冒包、非官方源、OSV／GHSA；未下载的二进制不得写成已确认安全 | `requirements.txt`、`requirements-cli.txt`、`tool_updater.py`、`build.yml`、`packaging/`。OSV querybatch 与 PyPI JSON，查询时间见上 | 直接依赖包名与官方上游一致，最新版查询未见漏洞；下限过旧的版本有历史漏洞。未发现这些精确包名被标为恶意包。二进制未入库、未下载，不能写成已确认安全 | 未安装，传递依赖未解析。未下载 subfinder/httpx/nuclei/wafw00f 与 nuclei 模板。未逐个核验 OSV 受影响版本区间的每一条修复边界。gh-proxy 镜像当前是否投毒未探测 |
| R5 | 精练中文报告 | 每节先结论再短分条 | `audit/RERUN-20261126.md`、`audit/matrix.md`、`audit/findings.json`、`audit/supply-chain.md` | 已覆盖。四份文件只新增审计材料 | — |
| R6 | 功能与使用（未实测） | README 宣称→实现 文件:行号→一致／部分／不符／未找到；入口命令、关键配置、典型工作流 | `README.md`、`SECURITY.md`、`CHANGELOG.md`、`cybercensus.py` `build_parser`、`asm_gui.pyw` | 已做静态对照，全部标未实测。端口扫描与 nuclei 默认关闭与文档一致；「默认被动」和界面默认「标准」+ 敏感路径开关为部分一致；工具查找顺序与「四平台」表述为不符 | 未实际点选界面或执行命令。Releases 体积（约 138MB / 37MB）在本树中无对应产物，未核实 |
| R7 | 编译与部署要求（未实测） | 构建／打包方式、Python 与依赖版本、外部服务与 API、硬件、外网依赖、文档与代码不符 | `README.md` 环境要求、`requirements*.txt`、`packaging/pack_release.py`、`packaging/pack_linux.py`、`.github/workflows/build.yml`、`启动界面.bat` | 已读构建与依赖声明，全部标未实测。本树无 Dockerfile、无锁文件 | 文档未写 CPU、内存、磁盘硬件需求，该项未覆盖。未执行 PyInstaller、未跑 Actions、未安装依赖 |
| R8 | 不建私库、不改产品代码、不把静态阅读写成已运行验证 | 检查交付物与表述 | 本分支相对 `1192f64e` 仅新增 `audit/` | 已遵守。报告中的「已确认」均指读到源码或只读查询结果，运行与部署标未实测 | — |

本单未启用、故未单列产出：拓扑全表、部署方案、性能、许可证／来源深挖、私库留存。
