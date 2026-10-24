# Windows 实现与维护

> 源码快照说明：安装包、测试报告、截图、PNG 原稿、交付校验清单及完整历史归档属于原始交付资料，未随本仓库提供。相关路径仅用于标识历史文件；本文保留的测试结果是原交付记录，不表示本次发布重新执行。当前可编辑源码位于仓库根目录。

日期：2026-10-20。目标：Windows 10 22H2 / Windows 11，x64，.NET Framework 4.8。没有使用系统 Python、收费 API、开发服务器或在线课程。

## 技术选择及来源

| 模块 | 采用方案 | 许可与来源 | 实际验证与取舍 |
| --- | --- | --- | --- |
| Python | 官方 CPython 3.13.16 Windows embedded x64 | PSF-2.0 及随附第三方条款；[发布页](https://www.python.org/downloads/release/python-31316/)、[嵌入包文档](https://docs.python.org/3.13/using/windows.html#the-embeddable-package) | 真实子进程执行、中文输入、多文件导入、SQLite 3.50.4、标准库通过；不是重新实现解释器。嵌入包不提供 pip、Tk/IDLE 或普通完整安装环境。 |
| 窗口 | Windows Forms + Microsoft WebView2 SDK 1.0.4191.47 | SDK 包中的 BSD 风格 Microsoft 许可及 NOTICE；[官方入门](https://learn.microsoft.com/en-us/microsoft-edge/webview2/get-started/winforms) | 使用现成 HTML/CSS/CodeMirror 界面；本机没有 dotnet SDK，使用系统 .NET Framework C# 编译器构建真实 x64 EXE。 |
| 显示运行时 | Microsoft WebView2 Evergreen Standalone x64 | 专有、免费可再分发，不能描述为 MIT 或全开源；[官方分发指南](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution)、[官方许可资源](https://developer.microsoft.com/microsoft-edge/api/eula/webview2?locale=en-us) | 打包 214,156,024 字节完整离线安装器；Microsoft Authenticode 签名验证为 Valid。仅检测不到 >=110 版本时调用随附 `/silent /install`。没有使用联网 bootstrapper。未在无 WebView2 的全新系统实际测试。 |
| 存储 | CPython 标准库 pathlib/json/os/zipfile | 同 CPython；[ZIP 安全说明](https://docs.python.org/3.13/library/zipfile.html#decompression-pitfalls) | 普通项目目录及真实 .py/资源文件。atomic replace JSON 索引、前一版索引、每项目最近 100 个文件版本、软删项目。避免引入额外数据库依赖。 |
| 执行控制 | 标准库 subprocess + Windows Job Object | Python 与 Windows API；[subprocess](https://docs.python.org/3.13/library/subprocess.html)、[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) | 子进程在 stdin 握手前加入 Job，整树停止、关闭时清理、累计执行预算 30 秒、每次文本输入等待 300 秒、256 KiB 输出、512 MiB 提交内存与 16 个进程上限。真实后代进程终止测试通过。 |
| 安装器 | .NET ZIP 解包、当前用户安装、标准 HKCU 卸载项和 WSH 快捷方式 | PySlate 自有源码；依赖 Windows/.NET 系统组件 | 生成真实 EXE。源文件不足 20 KiB，无额外安装器引擎。工作区中测试安装/卸载及用户数据保留。快捷方式和注册表分支没有在开发者账户执行。 |

CPython 固定到同分支 3.13.16，纳入 2026-09-30 官方维护版的 ZIP 解压、TLS、tarfile 等修复，而不依赖开发者系统中的 Python。嵌入包的 SHA256 与官方发布页一致，最终运行与课程测试使用该实际解释器。

## 构建

在 Windows PowerShell 中运行 `windows/build.ps1`。无需 Visual Studio 或 dotnet SDK；需要 .NET Framework 4.8 的系统编译器。首次构建会下载免费官方依赖，之后可使用 `-SkipDownload`。所有依赖校验固定 SHA256；WebView2 的下载源为本次官方重定向得到的固定 Microsoft CDN 文件地址。将来文件下线时应重新核查来源、签名、许可和哈希后更新，不能直接关闭校验。

默认中间文件写入仓库同级的 `work/windows-build`，产物写入仓库同级的 `windows/`，均位于源码树之外；可通过 `-OutputDirectory` 和 `-WorkDirectory` 指定其他位置。安装包和 portable ZIP 都包含同一版 web/course/runtime/解释器。重新构建前须退出正在使用产物目录的 PySlate。`windows/third-party/` 保留 Windows 必需许可证，构建会合并仓库根目录 `licenses/` 的第三方许可证。开发文档不打包历史 `RELEASE_REPORT*.md`。

测试：

```powershell
python tools/test_runtime.py --package ../windows/PySlate --report test-reports/windows-runtime.json
python tools/test_windows_installer.py --installer ../windows/PySlate-0.3.0-windows-x64-setup.exe --report test-reports/windows-installer.json
```

测试脚本从指定 package 启动其中的 `python/python.exe`；调用它们的 Python 仅作为测试驱动，不构成最终产品依赖。安装器测试明确使用 workspace 路径、`--no-shortcuts --portable-test --accept-webview2-license`，不修改开发者桌面、开始菜单或 HKCU 卸载项。

## 数据与恢复

正式数据目录为 `%LOCALAPPDATA%/PySlate/Data`，包含 `catalog.json`、`catalog.previous.json`、`projects/<随机ID>/`、`backups/<项目ID>/` 与 `trash/`。项目显示名称和目录随机 ID 分离，中文项目及文件名可跨平台交换。用户代码及资源仍是普通文件；导出 ZIP 不夹带 PySlate 私有索引。

`catalog.previous.json` 是上次成功写入的索引。当前索引损坏时自动读取备份；两个文件都损坏时保留原数据并报错。只将解析及结构验证成功的主索引更新到备份，损坏主索引不会覆盖唯一有效备份。旧代码在 `backups/<项目ID>/`，带时间戳与原文件名，每项目最多保留 100 版。删除项目移到 `trash/<ID>-<时间戳>/`，同前缀的 `.recovery.json` 旁置文件记录原名称，不覆写任何项目文件。删除采用同卷重命名，失败保留项目，不跟随目录链接复制；索引保存失败时回滚目录和内存索引。当前尚无图形化恢复页，可从普通目录手动恢复。安装/卸载保留独立 Data 目录，卸载只删除安装清单中的应用文件。

每份 Data 目录由 Windows 文件锁限制同时只运行一个服务，避免两个窗口各持一份旧索引而互相覆盖；退出或进程结束自动释放。相同资料库第二次启动会提示返回现有窗口。

## 执行与安全边界

Windows **不是安全沙箱**。项目目录是工作目录，文件操作桥接与 ZIP 导入严格限定相对路径，但实际 CPython 与当前用户有相同文件和网络权限。用户代码可越出项目目录读写、访问网络或调用系统程序。Job Object 只控制进程生命周期及资源，不能提供文件系统隔离。没有通过 Python 关键字、模块黑名单冒充沙箱。首次运行必须明确确认信任提示，只运行可信代码；不可信代码应在单独 Windows 账户、虚拟机或其他系统隔离中运行。

本地 HTTP 服务仅绑定 `127.0.0.1` 随机端口，每次生成 256 位随机 URL 能力令牌。校验 Host、Origin、Sec-Fetch-Site、JSON Content-Type 和请求长度；不返回 CORS 放行头。静态资源限定 web/course 目录。CSP 仅允许本地资源连接，宿主阻止任意页面跳转和应用权限请求，外部官方 Python HTTPS 链接仅在用户操作后交给系统浏览器。

ZIP 限制压缩文件 20 MiB、展开总量 50 MiB、1000 条目、单文件 10 MiB及过高压缩比。只接受跨平台通用的 Stored/Deflate 压缩，拒绝高内存 BZIP/LZMA 等方式。拒绝相对穿越、绝对路径、Windows ADS/设备名、反斜线路径、重复大小写路径、文件与目录冲突、符号链接、特殊文件和加密归档。编辑器只接受 <=1 MiB UTF-8 文本。

输入、输出、等待与执行都在后台线程/独立进程中。stdin 使用有界队列，避免未读取输入的程序阻塞本地服务。每次运行另限制 256 个输入请求与 8192 条事件，防止程序重定向 stdin 后制造不计 stdout 字节的输入事件洪水。停止及超限通过 Job Object 终止整棵子进程树。停止后返回时等待 exit 最多三秒。窗口关闭通过 WebView2 WebMessage 确认 `pyslateFlush()` 完成，最多五秒；失败时留窗提示用户避免静默丢失最后编辑。

0.2 修复了 0.1 将用户思考时间计入固定 30 秒壁钟超时的问题。真实旧版复现中，输入提示出现于 0.094 秒，29.997 秒时进程被终止，晚提交返回“程序已结束”。新监视器分别累计活动时间与每次输入等待时间：真实桥接文本 stdin 等待暂停 30 秒执行预算，每次等待最多 300 秒，消费后恢复且不清零已用执行时间。`events` 总是返回 `waiting`、`inputRequestId` 和单调 `stateRevision`；`input` / `input_end` 携带同一整数请求编号。已提交但尚未消费时不再要求用户回复，避免重发；带编号的重复、过期与多行提交明确拒绝，空字符串会发送合法空行。无编号接口仅为旧客户端和原始 stdin 写入兼容，新 UI 总是使用编号。

worker 的 `input-v2` 参数启用带结束确认的控制帧和文本 stdin 代理，覆盖 `input()`、`read()`、`readline()`、迭代与 EOF，`size=0` 不等待。重定向到 StringIO 的输入仍计入 256 次配额，但不暂停执行预算或制造 UI 等待；二进制 `stdin.buffer` 与原始 `sys.__stdin__` 绕过文本控制协议，其阻塞仍计入执行预算。独立课程工具不传 `input-v2` 时保留旧 worker 参数接口。

`windows-input-before-v020.json` 保留旧版真实故障；`windows-input-v020.json` 的 15 项全部通过，包含真实等待 31.224 秒后成功提交、退出 0。`windows-runtime-v020.json` 的原 22 项安全与可靠性检查全部通过，使用发行内同一 CPython 3.13.16 加新运行时源码，未借测试重建发行包。`windows-state-v020.json` 核对 `lessonTiers`、旧 beginner 键和分级键同时保存并重启读回。

## 离线与隐私说明

PySlate 的课程、编辑器、项目存储与 CPython 执行完全使用随附文件；没有 AI API、账户、云数据库、广告或应用服务器依赖。Microsoft WebView2 是共享系统组件，其自身可能自动更新，并按 Microsoft 条款发送诊断或 SmartScreen 信息。随安装器提供完整 Microsoft 许可、数据和 SmartScreen 告知及同意选项。断网仍可运行核心功能；不能把“核心离线可用”扩大为“系统显示组件绝不会联网”。

## 已验证与尚未覆盖

0.2 开发阶段已完成以下增量验证，最终发行包将在内容冻结后独立重建；这些结果不代表旧 0.1 安装包已经包含新修复。

| 验证 | 结果 | 证据 |
| --- | --- | --- |
| 原输入问题复现 | 已确认 30 秒壁钟包含用户等待 | `test-reports/windows-input-before-v020.json` |
| 输入请求、空行、连续输入、EOF、停止与两种超时预算 | 15 / 15 | `test-reports/windows-input-v020.json` |
| 新运行时保留原安全与可靠性行为 | 22 / 22 | `test-reports/windows-runtime-v020.json` |
| 三层选择及旧/新草稿键重启保存 | 通过 | `test-reports/windows-state-v020.json` |
| 真实 Windows WebView2 三层存档、Ctrl+Enter、等待31秒、IME、重复提交及换文件保留输入 | 12 / 12，页面异常0 | `test-reports/windows-native-v020/windows-native-v020.json` 与同目录截图 |
| 八个项目新增中高级内容、真实文件集和答案产物 | 16 单元，68 / 68 用例 | `test-reports/windows-project-tiers-v020.json`，实际 embedded CPython + worker |

开发包的原生12项通过CDP连接真实WinForms/WebView2窗口，未另开Edge。关闭前保存得到WebMessage确认；三张页面截图已目视核查。Playwright断开后的宿主自动截图有正常像素，但该次宿主DOM元数据返回null，原报告如实保留；视口可见性、输入控件边界与无横向溢出使用连接期间的实际DOM断言验证。最终发行视觉验收另用原生capture-script路径收集DOM。

以下是 0.1 交付包的历史验收记录，测试读取当时 `windows/PySlate` 内真实解释器、worker、课程和原生 EXE；保留作为升级前证据。

| 验证 | 结果 | 证据 |
| --- | --- | --- |
| 运行时与本机桥接 | 22 / 22 | `test-reports/windows-runtime.json` |
| EXE 实际安装、独立 Python、卸载保留数据 | 7 / 7 | `test-reports/windows-installer.json` |
| 原生 WebView2 实际渲染、中文 input、真实 traceback、关闭前保存 | 6 / 6 | `test-reports/windows-native.json` 及同前缀 PNG / DOM JSON / 日志 |
| 输入洪水、junction 与删除回滚专项 | 4 / 4 | `test-reports/windows-regressions.json` |
| 58 课示例、答案、文件及输入边界 | 142 / 142 | `test-reports/windows-course.json`，执行模式为打包 Python + PySlate worker |
| Windows 导出后 Android 原生导入执行 | 通过 | `test-reports/windows-to-android-result.json` |
| Android 原生导出后 Windows 导入执行 | 通过 | `test-reports/windows-import-android.json` |
| 源码与包内容 SHA256 | 逐文件零差异，数量记录于报告 | `test-reports/windows-integrity.json`、包内 `BUILD-MANIFEST.json` |

原生截图使用最终 EXE 的真实 WebView2 CDP 截图，不是网页设计稿。此机器 250% DPI 下应用视口为 1192 × 661 CSS 像素，截图为 2980 × 1653 实际像素；检查无横向溢出、无损坏图片，课程页实际显示离线 1536 × 1024 插图。较早调试中的一次资料库截图遇到 WebView2 图形接口超时，重试成功；最终统一构建后的六项验收均一次通过。

`test-reports/windows-runtime.json` 是真实 embedded 运行时黑盒结果；`windows-installer.json` 是实际 EXE 在工作区安装/卸载结果。清洁 Windows 10/11 虚拟机、没有 .NET4.8/WebView2 的机器、系统不同 DPI、多显示器、杀毒软件/企业安装策略、ARM64/x86 没有全面覆盖。安装器未签名，Windows SmartScreen 可能提示发布者未知。Windows 发行版仅提供 x64 安装包。
