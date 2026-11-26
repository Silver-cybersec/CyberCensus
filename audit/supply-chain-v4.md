# 供应链补查 v4

审计基准仍是上游 https://github.com/Zerdon-me/CyberCensus `1192f64ec542244d2e06c12be2bdd93097ef1a4e`（2026-11-26 10:15:02 香港时间）。本文件只补 `audit/supply-chain.md` 里标成未核实或未展开的部分，不改该基准。  
查询窗口：2026-11-26 11:32–11:34 香港时间（Asia/Hong_Kong，UTC+8）。带 `Z` 的上游时间已换算为香港时间。  
未安装依赖，未解包，未拉镜像层，未下载 `tools/` 二进制或校验和文件正文，未运行仓库脚本。

## 八项结论

| 项 | 结论 | 证据要点 |
|---|---|---|
| 1 清单与 lockfile，含间接依赖 | 已确认 | 仓库无 lockfile。直接依赖只有最低版本。查询当日最新版的依赖图来自 deps.dev，不是本仓库锁定的安装结果 |
| 2 版本钉、校验和、git／URL 直装 | 已确认 | 清单与 CI 均无 `==`、无 `--hash`、无 `git+`。二进制更新不核对上游校验和 |
| 3 仿冒包名、安装钩子、非官方源 | 未核实 | 清单中的精确包名与抽样邻近名已查；第三方 sdist 的安装钩子未解包，故不把本项写成未发现问题 |
| 4 容器镜像 | 未发现问题 | 基准树无 Dockerfile、compose 或 `image:` |
| 5 子模块、下载脚本、运行时远程工具 | 已确认 | 无子模块、无 `curl\|bash`。更新器与 CI 跟踪 GitHub `latest`／`main`，并跳过名为 checksum 的资产 |
| 6 CI：Action SHA、密钥、危险触发 | 已确认 | 三个 Action 都是浮动主版本标签。工作流无 `secrets.*`、无 `pull_request_target`、无 `workflow_run` |
| 7 恶意包库与已知漏洞 | 已确认 | 已查精确包名无 `MAL-` 记录。`cryptography>=3.4`、`dnspython>=2.1` 的下限落在已公开漏洞的影响区间内；查询当日最新版返回 0 条 |
| 8 主要依赖维护状态 | 未发现问题 | 直接依赖的上游仓库均未归档。发布日期见第 8 节 |

## 1. 依赖清单与 lockfile

结论：**已确认**。仓库不能复现一次安装的间接依赖。

- 直接依赖：`requirements.txt` 第 2–6 行、`requirements-cli.txt` 第 2–4 行。构建另写在 `.github/workflows/build.yml` 第 27 行。上轮已记录，见 `audit/supply-chain.md`「依赖是否恶意」首条。
- 本轮按文件名检索：无 `Pipfile`、`poetry.lock`、`requirements.lock`、`pyproject.toml`、`setup.py`、`constraints.txt`。
- 间接依赖未安装。2026-11-26 11:32 香港时间用 deps.dev 读取**查询当时 PyPI 最新版**的依赖图（`https://api.deps.dev/v3/systems/pypi/packages/{name}/versions/{version}:dependencies`）。这不是 lockfile：

  | 包 @ 查询当时最新版 | 图中的其他包 |
  |---|---|
  | cryptography 50.0.2 | cffi 2.1.1，pycparser 3.12.0 |
  | dnspython 2.9.2 | 无（默认安装；`requires_dist` 均为 extra） |
  | pypinyin 0.55.0 | 无 |
  | customtkinter 6.0.0 | darkdetect 0.8.0，packaging 26.3.0 |
  | pyinstaller 6.22.3 | altgraph 0.17.5，packaging 26.3.0，pyinstaller-hooks-contrib 2026.10.0，setuptools 84.2.1 |
  | wafw00f 2.4.2 | requests 2.34.2，以及 certifi 2026.10.23、charset-normalizer 3.5.2、idna 3.20.0、PySocks 1.7.1、urllib3 2.8.0 |

- `pyinstaller` 在 Windows 上的 `pefile`、`pywin32-ctypes` 没有出现在上述默认图里。另查 PyPI 最新版：pefile 2024.8.26、pywin32-ctypes 0.2.3（同一查询窗口内的后续请求，11:34 香港时间）。这仍不是本仓库的锁定结果。

## 2. 版本钉、校验和、git／URL 直装

结论：**已确认**。版本只写下限，没有校验和，也没有 git／URL 直装。

- `>=` 见 `requirements.txt` 第 2–6 行。全树检索无 `--hash`、无 `git+`、无直接的 wheel URL。
- 二进制侧不核对上游校验和：`tool_updater.py` 第 102 行跳过文件名含 `checksum` 的资产；校验手段是执行 `-version`（第 254–256 行）。细节已写在 `audit/supply-chain.md`「第三方二进制与更新器」。
- 本轮只读 GitHub Release 元数据（2026-11-26 11:33 香港时间，`GET /repos/projectdiscovery/{subfinder,httpx,nuclei}/releases/latest`）：当时最新 tag 为 subfinder v2.17.0（2026-10-08 15:09 香港时间）、httpx v1.12.0（2026-09-08 21:36 香港时间）、nuclei v3.11.1（2026-08-08 20:21 香港时间）。三个发布都有 `*_checksums.txt`，资产对象带 `digest` 字段。未下载 zip 或校验和正文，没有比对摘要。

## 3. 仿冒或可疑包名、安装钩子、非官方源

结论：**未核实**。清单里的包名和索引来源没有看到仿冒；第三方包的安装钩子没有解包，不能写成未发现问题。

- 精确包名的 PyPI 项目地址见 `audit/supply-chain.md` 第 17–25 行。本轮 11:32 香港时间复查仍指向 pyca/cryptography、rthalley/dnspython、mozillazg/python-pinyin、customtkinter 官网、pyinstaller.org、EnableSecurity/wafw00f。
- 清单与工作流无 `--extra-index-url`、无私有源。非官方来源在二进制镜像，不在 PyPI 索引：`tool_updater.py` 第 34 行的 `gh-proxy.com` 与 `ghproxy.net`（归入第 5 项）。
- 本仓库无 `setup.py`、`pyproject.toml`、`package.json`，没有自身的 postinstall 字段。`启动界面.bat` 第 12 行会调用 `pip install`，那是启动脚本，不是依赖包里的钩子。
- 抽样邻近名（PyPI JSON，11:32 香港时间）：`cryptograpy` 0.0.0（摘要为 “Did you mean cryptography”）、`python-cryptography` 0.0.3、`python-pinyin` 0.1.0 存在；`cryptographyy`、`dnspythons`、`customtkinterr`、`pyinstaleler`、`wafwoof` 返回 404。这些名字都不在 `requirements*.txt` 或 `build.yml` 第 27 行。OSV 对这三个现存邻近名的当前版本返回 0 条，恶意包目录亦无条目（第 7 节）。
- 未下载任何 sdist／wheel，安装时的 setuptools 命令未阅读。

## 4. 容器镜像

结论：**未发现问题**。基准树里没有可审的镜像来源、tag 或 digest。

- 本轮检索无 Dockerfile、compose 文件，工作流与打包脚本无 `image:`。上轮已记录，见 `audit/supply-chain.md`「镜像、Actions、子模块、容器」。
- 未拉取镜像层。此项只说明仓库没有容器定义。

## 5. 子模块、下载脚本、运行时远程工具

结论：**已确认**。运行时和发布流程会拉取未钉版本的第三方程序，并且不使用上游校验和。

- 无 `.gitmodules`。`build.yml` 第 99–106 行的 `curl` 把 GitHub API 与 zip 写到文件再解压，没有接到 shell。
- `tools/*.exe` 不在本提交中（`.gitignore` 第 49–51 行；目录内只有 `tools/README.txt`）。来源与校验方式见 `tool_updater.py` 第 27–34、94–106、254–256、305–319 行，以及 `build.yml` 第 42–50、60、98–106、118–124 行。上轮结论不变。
- 本轮补上的元数据：上述三个引擎的 latest 发布含 `*_checksums.txt`；nuclei-templates 另有 tag v10.5.2（2026-11-12 13:28 香港时间）和 `nuclei-templates-10.5.2_checksums.txt`，而 `build.yml` 第 60 与 120 行固定下载 `refs/heads/main`。未下载这些文件。
- 未发现模型仓库或插件市场地址。nuclei 模板是远程模板，不是模型权重。
- 未下载的二进制与模板正文，其内容是否恶意仍为未核实，不写成安全。

## 6. CI 工作流

结论：**已确认**。Action 没有钉到提交 SHA。

- 使用处：`actions/checkout@v4`、`actions/setup-python@v5`（`build.yml` 第 19–21、88–92 行；`tests.yml` 第 23–27 行）、`softprops/action-gh-release@v2`（`build.yml` 第 76、130 行）。文件里没有 40 位 SHA。
- 查询当日（11:34 香港时间）浮动标签解析到的提交，只说明那一刻的指向，工作流并未钉住：checkout `11d5960a326750d5838078e36cf38b85af677262`（提交时间 2026-07-17 03:43 香港时间），setup-python `a26af69be951a213d495a4c3e4e4022e16d87065`（2025-04-24 10:42 香港时间），action-gh-release `3bb12739c298aeb8a4eeaf626c5b8d85266b0e65`（2026-04-12 11:31 香港时间）。同一窗口内这两个仓库较新的补丁标签为 checkout v4.4.0、setup-python v5.6.0、action-gh-release v2.6.2。OSV（ecosystem `GitHub Actions`，版本 `4.4.0`／`5.6.0`／`2.6.2`）返回 0 条。空结果不表示浮动标签之后仍无通告。
- 触发：`build.yml` 第 4–7 行仅为 tag `v*`；`tests.yml` 第 3–7 行为 `push`（master/main）、`pull_request`、`workflow_dispatch`。全树无 `pull_request_target`、无 `workflow_run`。
- 权限：`build.yml` 第 9–10 行 `contents: write`；`tests.yml` 第 9–10 行 `contents: read`。两个文件都没有 `${{ secrets.* }}`。
- `pip install` 仍无版本与哈希（`build.yml` 第 27 行，`tests.yml` 第 31–32 行）。

## 7. 公开漏洞库与恶意包库

查询：OSV `querybatch`，2026-11-26 11:33 香港时间，`https://api.osv.dev/v1/querybatch`。恶意包目录：`https://api.github.com/repos/ossf/malicious-packages/contents/osv/malicious/pypi/{name}`，11:34 香港时间。阳性对照 `0requests` 返回 200 且含 `MAL-2026-15859.json`，说明路径有效。

### 依赖是否恶意

结论：**未发现问题**（仅限下面这些精确包名的目录查询，以及已解析版本的 OSV 结果）。未下载的二进制、模板和未解包的 wheel 仍为未核实。

- 目录 404、OSV 结果中无 `MAL-`：cryptography、dnspython、pypinyin、customtkinter、pyinstaller、wafw00f、cffi、pycparser、darkdetect、packaging、altgraph、pyinstaller-hooks-contrib、setuptools、certifi、charset-normalizer、idna、PySocks、requests、urllib3、pefile、pywin32-ctypes，以及抽样名 cryptograpy、python-cryptography、python-pinyin。
- 没有对每个包的全部历史版本做恶意通告枚举。

### 已知漏洞

结论：**已确认**。下限允许的旧版本落在公开漏洞区间内。查询当日最新版返回 0 条，不能代替锁定版本。

OSV 对 cryptography 50.0.2、dnspython 2.9.2、pypinyin 0.55.0、customtkinter 6.0.0、pyinstaller 6.22.3、wafw00f 2.4.2，以及第 1 节依赖图中的版本，返回 0 条。pypinyin 0.49.0、customtkinter 5.2.0、wafw00f 2.4.2 同样为 0。

`cryptography@3.4` 返回的通告（PYSEC 与 GHSA 为同一条的只留一行；区间取 OSV `introduced`／`fixed`）：

| 编号 | 影响 cryptography 的区间 |
|---|---|
| GHSA-w7pp-m8wf-vj6r / CVE-2023-23931 | 1.8 起，修复于 39.0.1 |
| GHSA-x4qr-2fvf-3mr5 / CVE-2023-0286 | 0.8.1 起，修复于 39.0.1 |
| GHSA-5cpq-8wj7-hf2v | 0.5 起，修复于 41.0.0 |
| GHSA-jm77-qphf-c4w8 | 0.8 起，修复于 41.0.3 |
| GHSA-v8gr-m533-ghj9 | 2.5 起，修复于 41.0.4 |
| GHSA-jfhm-5ghh-2f97 / CVE-2023-49083 | 3.1 起，修复于 41.0.6 |
| GHSA-3ww4-gg4f-jr7f / CVE-2023-50782 | 0 起，修复于 42.0.0 |
| GHSA-9v9h-cgj8-h64p / CVE-2024-0727 | 0 起，修复于 42.0.2 |
| PYSEC-2024-225 / CVE-2024-26130 / GHSA-6vqw-3v5j-54x4 | 38.0.0 起，修复于 42.0.4 |
| GHSA-r6ph-v2qm-q3c2 / CVE-2026-26007 | 0 起，修复于 46.0.5 |
| GHSA-m959-cc7f-wv43 / CVE-2026-34073 | 0 起，修复于 46.0.6 |
| GHSA-537c-gmf6-5ccf | 0.5.0 起，修复于 48.0.1 |
| PYSEC-2026-3553 / CVE-2026-69249 | 0 起，修复于 49.0.0 |
| PYSEC-2026-3554 / CVE-2026-69248 | 0 起，修复于 49.0.0 |

`dnspython@2.1.0`：GHSA-3rq5-2g8h-59hc / CVE-2023-29483，修复于 2.6.1；GHSA-45c3-73f7-pv4m / CVE-2026-114605，修复于 2.9.0；GHSA-vvf4-9x63-8xvv / CVE-2026-128089，修复于 2.9.2。OSV 对 2.9.2 返回 0 条。

这些是漏洞通告，不是恶意包通告。仓库没有把版本钉在修复版之上。

## 8. 主要依赖的维护状态

结论：**未发现问题**。直接依赖的上游仓库都没有归档或停用标记。

GitHub `GET /repos/{owner}/{repo}` 与 PyPI 上传时间，查询 2026-11-26 11:33 香港时间：

| 包 | 仓库归档 | 最近推送（香港时间） | 最近发布（香港时间） |
|---|---|---|---|
| cryptography 50.0.2 | 否 | 2026-11-25 20:29 | PyPI 上传 2026-09-30 23:30；GitHub Releases latest 返回 404 |
| dnspython 2.9.2 | 否 | 2026-11-23 03:54 | tag v2.9.2，2026-11-04 08:02 |
| pypinyin 0.55.0 | 否 | 2026-11-22 21:40 | tag v0.55.0，2025-07-20 20:11；PyPI 同日 20:01 |
| customtkinter 6.0.0 | 否 | 2026-11-15 19:23 | GitHub Releases latest 返回 404；PyPI 上传 2026-06-25 04:14 |
| pyinstaller 6.22.3 | 否 | 2026-11-23 00:51 | tag v6.22.3，2026-09-13 05:55 |
| wafw00f 2.4.2 | 否 | 2026-04-19 20:47 | tag v2.4.2，2026-01-27 04:03 |

相邻事实，不改变本项结论：customtkinter 未钉版本地依赖 darkdetect。PyPI 最新 0.8.0 上传于 2022-12-16 22:14 香港时间；`albertosottile/darkdetect` 未归档，最后推送 2024-03-11 14:48 香港时间。OSV 对该版本返回 0 条。

引擎仓库 projectdiscovery/subfinder、httpx、nuclei、nuclei-templates 在 11:33 香港时间的查询中均未归档，最后推送落在 2026-11-25 至 2026-11-26。这只说明仓库仍在更新，不说明本仓库拉取的字节已核对。
