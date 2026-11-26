# 供应链

基准：上游 https://github.com/Zerdon-me/CyberCensus `1192f64ec542244d2e06c12be2bdd93097ef1a4e`（2026-11-26 10:15:02 香港时间）。  
只读查询时间：2026-11-26 10:24–10:28 香港时间（Asia/Hong_Kong）。PyPI 与 OSV 的「最新版」是这一窗口的解析结果，不是仓库里写下的日期。

## 结论

直接声明的 PyPI 包名指向各项目公开的上游仓库，OSV 对 2026-11-26 查询到的最新版返回 0 条漏洞，返回结果里没有 `MAL-` 编号。这不能写成「依赖无恶意」或「安装结果安全」：版本只写了最低限，没有锁文件和哈希；`tools/` 下的第三方二进制不在本提交里，本次也没有下载，不能确认其内容。

## 依赖是否恶意

结论：按精确包名核对，未见这些名字被替换成仿冒项目，也未见 OSV 把它们标成恶意包。未安装、未解包，传递依赖和未入库二进制的恶意性未核实。

- 声明位置：`requirements.txt`、`requirements-cli.txt`（`dnspython>=2.1`、`cryptography>=3.4`、`pypinyin>=0.49`，GUI 另加 `customtkinter>=5.2`）。构建工作流另装 `pyinstaller`、`wafw00f`，无版本约束（`.github/workflows/build.yml` 第 27 行）。
- 无 `requirements.lock`、`pip-tools` 哈希、Poetry/Pipenv、`constraints.txt`。无 git 依赖、无 `--extra-index-url`、无私有源。
- 2026-11-26 10:24–10:28 香港时间只读查询 PyPI JSON，精确包名解析结果：

  | 包名 | 当时最新版 | 项目地址（PyPI project_urls / home_page） |
  |---|---|---|
  | cryptography | 50.0.2 | https://github.com/pyca/cryptography |
  | dnspython | 2.9.2 | https://github.com/rthalley/dnspython |
  | pypinyin | 0.55.0 | https://github.com/mozillazg/python-pinyin |
  | customtkinter | 6.0.0 | https://customtkinter.tomschimansky.com |
  | pyinstaller | 6.22.3 | https://pyinstaller.org |
  | wafw00f | 2.4.2 | https://github.com/enablesecurity/wafw00f |

- 包名与 `THIRD_PARTY_NOTICES.md` 所列上游一致。未对相近拼写做全网搜索，只核对了清单中的精确名字。
- OSV `querybatch`（同一查询窗口）对上表最新版均返回 0 条。对下限 `cryptography@3.4` 返回 21 条（GHSA/PYSEC，含旧 wheel 捆绑 OpenSSL 的 GHSA-x4qr-2fvf-3mr5，以及 GHSA-w7pp-m8wf-vj6r / CVE-2023-23931）。对 `dnspython@2.1.0` 返回 4 条：GHSA-3rq5-2g8h-59hc（CVE-2023-29483）、GHSA-45c3-73f7-pv4m（CVE-2026-114605）、GHSA-vvf4-9x63-8xvv（CVE-2026-128089）、PYSEC-2026-1307。这些是漏洞通告，不是恶意包通告。`pypinyin@0.49.0`、`customtkinter@5.2.0`、`pyinstaller@6.0.0`、`wafw00f@2.4.2` 返回 0 条。
- 上述返回 ID 中没有 `MAL-` 前缀。未把「最新版 0 条」延伸成「任意中间版本无漏洞」。受影响区间的每一条修复边界未逐条打开。
- 安装钩子：源码树没有 `setup.py` / `pyproject.toml`。风险在调用方：`启动界面.bat` 第 8–13 行在缺少 GUI 库时执行 `pip install customtkinter`；`packaging/pack_linux.py` 第 50–58 行生成的 `install.sh` 对 `requirements-cli.txt` 做无哈希安装。未执行这些脚本。
- 传递依赖：未创建虚拟环境，未解析。标未核实。

## 第三方二进制与更新器

结论：本提交不包含 subfinder、httpx、nuclei、wafw00f 的二进制。更新器和发布工作流都从浮动的 GitHub latest 取包，执行前不核对上游校验和。未下载的文件不能写成已确认安全。

- `.gitignore` 第 49–51 行忽略 `tools/*`，只保留 `tools/README.txt`。工作区该目录只有这份说明，没有 exe。
- `tool_updater.py` 第 27–34 行：仓库固定为 `projectdiscovery/subfinder`、`projectdiscovery/httpx`、`projectdiscovery/nuclei`；镜像前缀为直连、`https://gh-proxy.com/`、`https://ghproxy.net/`。wafw00f 不自动替换，冻结版本字符串 `2.4.2`（第 33 行），与查询当日 PyPI 最新版相同。
- `select_asset`（第 94–106 行）要求 zip、文件名含 windows 与 amd64/x86_64、含工具名，并跳过带 `checksum` 的文件。`install_tool`（第 215–292 行）下载后解压到临时目录的固定 exe 名，再执行 `-version`。`update_templates`（第 305–319 行）执行 `nuclei -update-templates`。
- 发布工作流 `.github/workflows/build.yml` 第 37–67 行与第 94–124 行：`releases/latest` 与 `nuclei-templates` 的 `refs/heads/main`，无校验和。`packaging/pack_release.py` 第 118–132 行事后计算本包 SHA256。
- 官方项目名与 `THIRD_PARTY_NOTICES.md` 一致。二进制字节、签名和模板内容未拉取，恶意性未核实。

## 镜像、Actions、子模块、容器

结论：无 Docker、无子模块、无锁文件。Actions 使用浮动主版本标签。

- 本树无 Dockerfile、compose、基础镜像。未拉取镜像层，不存在「已确认安全的镜像」。
- 无 `.gitmodules`。
- Dependabot（`.github/dependabot.yml`）按月检查 pip 与 github-actions，不能弥补无哈希和二进制不校验。
- Actions：`actions/checkout@v4`、`actions/setup-python@v5`、`softprops/action-gh-release@v2`（`build.yml` 第 19、21、76、130 行）。未把标签解析成 commit SHA，也未查询这些 Action 的 GHSA 明细。标未核实。
- 源码中的 `curl` 出现在 `build.yml` 第 99–120 行，对象是 GitHub API 与 codeload，没有管道进 shell 执行远程安装脚本。

## 与发现的对应

- CC-01 更新器下载后执行，镜像与校验和。
- CC-06 发布工作流浮动 latest 与无哈希 pip。
- CC-08 启动脚本与 Linux `install.sh` 的无哈希安装。
