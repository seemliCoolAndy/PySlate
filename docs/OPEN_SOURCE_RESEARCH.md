# PySlate 开源技术调查

> 源码快照说明：安装包、测试报告、截图、PNG 原稿、交付校验清单及完整历史归档属于原始交付资料，未随本仓库提供。相关路径仅用于标识历史文件；本文保留的测试结果是原交付记录，不表示本次发布重新执行。当前可编辑源码位于仓库根目录。

调查日期：2026-10-20（Asia/Shanghai）。本文件区分**官方资料核查**、**本机检查**与**产品实测**；仓库声明不等于集成成功。具体构建及设备结果由 `ANDROID.md` 和交付测试报告补充。

## 决策

采用同一套离线 HTML/CSS/JavaScript 产品界面与 CodeMirror 6 编辑器；Windows 使用本地 WebView2 外壳与随包 CPython 子进程，Android 使用系统 WebView 与 Chaquopy 的独立 `:runner` Service 进程。实际文件由主进程管理，ZIP 交换标准项目。界面、运行服务、课程资源各自解耦。

Flutter + re_editor 同样可行，未选择的原因是当前机器缺 Flutter/Dart 和 Windows C++ 构建工具，而共享 Web UI 可在既有运行时上较快完成真正安装验证。这是本次实施判断，不代表 Flutter 的跨平台能力不足。

## 候选比较与许可

| 候选 | 已核查许可 / 平台 | 维护证据与本项目判断 |
|---|---|---|
| [Chaquopy](https://github.com/chaquo/chaquopy) | [MIT](https://github.com/chaquo/chaquopy/blob/master/LICENSE.txt)；Android | 采用。官方 [17.1.0 changelog](https://chaquo.com/chaquopy/doc/current/changelog.html) 日期 2026-10-12；预编译 CPython 和标准 Gradle 集成减少自编译风险。保留版权与 MIT 原文。 |
| [python-for-android](https://github.com/kivy/python-for-android) | [MIT](https://raw.githubusercontent.com/kivy/python-for-android/develop/LICENSE)；Android | [2026.05.09 release](https://github.com/kivy/python-for-android/releases/tag/v2026.05.09) 可核查。[官方入门](https://python-for-android.readthedocs.io/en/latest/quickstart.html) 支持 SDL/WebView/service bootstrap，但 Windows 构建需 Linux VM 等额外环境，并依赖 SDK/NDK 与 recipe。此次不采用，未做运行验证。 |
| [Flutter](https://github.com/flutter/flutter) | [BSD-3-Clause](https://github.com/flutter/flutter/blob/master/LICENSE)；Android / Windows | 候选可行。[官方 Windows 安装要求](https://docs.flutter.dev/platform-integration/windows/setup) 涉及 Visual Studio C++ 工具链。此次未安装 Flutter，未实测其编辑器。 |
| [re_editor](https://github.com/reqable/re-editor) | [MIT](https://pub.dev/packages/re_editor/license)；Android / Windows 等 | [包 changelog](https://pub.dev/packages/re_editor/changelog) 当前 0.10.0，含持续更新；Flutter 路线优先候选，提供成熟编辑行为与高亮。需要连同 isolate_manager、re_highlight 的实际锁定版本审计，不能仅以顶层 MIT 覆盖依赖。未集成。 |
| [flutter_code_editor](https://github.com/akvelon/flutter-code-editor) | [Apache-2.0](https://github.com/akvelon/flutter-code-editor/blob/main/LICENSE)；Android / Windows | [pub.dev](https://pub.dev/packages/flutter_code_editor) 当前 0.3.5，约12个月前发布。Python 折叠、只读片段适合教学；分析器接口仍标实验。保存应取 fullText，text 可能遗漏折叠内容。维护及依赖风险相对更高，未选择。 |
| [CodeMirror 6](https://github.com/codemirror/dev) | [MIT](https://raw.githubusercontent.com/codemirror/dev/main/LICENSE)；浏览器 / WebView | 采用 npm 分包、本地打包。GitHub dev 于 2026-04-15 归档，README 明确迁至 [新官方仓库](https://code.haverbeke.berlin/codemirror/dev)，不能据归档误判整个项目停更。最终版本以 package-lock 与实际保留的各包许可证为准。 |
| [CPython](https://github.com/python/cpython) | [PSF 与历史兼容许可及第三方 notices](https://github.com/python/cpython/blob/main/LICENSE)；Windows / Chaquopy Android | 采用真实 CPython。Python 本体许可不替代 OpenSSL、SQLite、libffi 等随包组件要求；随官方运行时完整保留 LICENSE 与 notices。 |
| [SQLite](https://www.sqlite.org/) | [核心 public domain 声明](https://www.sqlite.org/copyright.html) | 可选元数据方案。第一版使用原子 JSON + 标准目录，以减少依赖；课程数据处理可使用 CPython sqlite3，实际兼容由示例测试确认。 |
| [Inno Setup](https://jrsoftware.org/isinfo.php) | [自有 Inno Setup License](https://github.com/jrsoftware/issrc/blob/main/license.txt)，不是 MIT | 候选 EXE 安装器。许可允许商业用途与修改再分发，保留原版权与来源、不冒充原版；官网请求商业用户购买商业许可，需区分请求与许可证条件。本项目永久免费，不采购。是否最终采用见发布报告。 |
| Android SDK / Gradle | Android SDK 为 Google SDK 协议，Gradle 核心 Apache-2.0 | 构建工具不视作产品 MIT 依赖。仅在 work/ 下载工具链，未写入系统 PATH。Android 系统 WebView 由设备提供，不打包整个 Chromium。 |
| Microsoft WebView2 | [官方分发文档](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution)；Microsoft Runtime 许可 | Windows 候选外壳。系统运行时存在不能替代干净机器验证；若安装程序不打包离线 Runtime，应如实声明首次安装前置条件，不能承诺所有 Windows 离线安装成功。 |

## Android CPython 集成重点

[官方版本表](https://chaquo.com/chaquopy/doc/current/versions.html) 给出 Chaquopy 17.1 支持 Python 3.10–3.15、AGP 7.3–9.4、最低 Android API24。此次应用因使用 Java NIO 文件 API 取 minSdk26。arm64-v8a 与 x86_64 各增加解释器体积，具体 APK 字节数由产物测量，不预估性能指标。

[Gradle / 标准库文档](https://chaquo.com/chaquopy/doc/current/android.html) 明确默认 stdin 总是 EOF，因此 input() 不能直接工作：需自行提供阻塞输入流与 UI 输入桥；stdout/stderr 也需接到真实控制台。Android 不能承诺 tkinter/turtle/curses 或常规 multiprocessing。第三方 native wheel 必须逐包验证；第一版以标准库课程为交集。

[官方 FAQ](https://chaquo.com/chaquopy/doc/current/faq.html) 明确 Python 默认在应用进程内，线程取消需代码自行配合或异步异常；后者不能作为所有 native 扩展的可靠强制停止方案。此次将解释器放到 `android:process=":runner"`，输入/输出经 Messenger，主进程 watchdog 控制累计30秒执行（0.2版在真实输入等待时暂停计时、每次等待最多300秒）、256KiB输出、用户终止。运行完成后丢弃整个 worker，避免模块、线程与全局状态污染。

[Android Service 文档](https://developer.android.com/guide/topics/manifest/service-element) 区分普通 process 和 isolatedProcess；后者无自有权限。[Process.killProcess](https://developer.android.com/reference/android/os/Process#killProcess(int)) 受内核权限约束，适用于本应用子进程。普通 `:runner` 与 UI 共享 UID，能访问应用私有数据，因此本实现只能称进程生命期隔离，不能称恶意代码安全沙箱。isolatedProcess 下 Chaquopy 提取资源与项目文件访问尚未验证，不虚构支持。应用不申请 INTERNET / 外部存储权限；用户以系统文件选择器显式导入导出。信任提示应说明本应用数据访问边界。

## Windows 运行与安装重点

[官方嵌入式发行版说明](https://docs.python.org/3/using/windows.html#the-embeddable-package) 允许应用安装包携带私有 CPython。它包含解释器与压缩标准库，不含 pip/Tcl/Tk；通过 ._pth 明确模块路径。课程多文件 import 必须显式加入项目路径，不能假定 embeddable 自动采用 cwd。产品运行应固定随包解释器路径，而非用户 PATH 的 python。

[subprocess 官方文档](https://docs.python.org/3/library/subprocess.html) 支持管道连接 stdin/stdout/stderr；不得在 UI 线程阻塞 communicate 或无限累积输出。每次执行独立进程，持续读取两个输出流、UTF-8、按需发送输入、保留 traceback。[Windows Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) 可用于对子进程树实施生命周期与资源限制；单纯 kill 主 PID 不能宣称终止整个进程树。两者都不自动提供文件系统沙箱，普通 Windows 子进程拥有当前用户权限。

## 本机实际检查与证据边界

2026-10-20 初始 `Get-Command` 检查未找到 flutter、dart、adb、gradle、iscc、makensis；常见 Android SDK/Flutter/Inno 目录不存在。`py -0p` 实际列出 CPython3.14，`java -version` 实际为 Java23.0.2；dotnet 有可执行文件但 `--list-sdks` 无 SDK。该结论只覆盖 PATH 与列出的常见目录，不等于全盘扫描。

随后实际下载官方 Android commandlinetools、Gradle8.11.1，安装 SDK35/build-tools35/platform-tools 于 work/android-toolchain。SDK zip SHA256 实测 `90ae805d20434428bffcb699c290860f19bb5f66a67e6b330067e3de801fb04a` 与 [官方下载表](https://developer.android.com/studio?authuser=104) 一致。AGP8.9.2 / Gradle8.11.1 / SDK35 的对应关系核查 [官方 AGP8.9 说明](https://developer.android.com/build/releases/agp-8-9-0-release-notes?hl=en)。实际 Gradle 构建日志、APK 安装和运行测试仍须分别记录，以上文档核查不能代替它们。

## 发布审计要求

最终报告以实际锁文件、发行版与二进制为准列依赖。MIT/BSD 保留版权与免责声明；Apache-2.0 保留 LICENSE、实际提供的 NOTICE 及修改说明。课程自写中文解释，不复制商业中文教程。SVG 原创图与 AI 图像记录单列。不要宣称未执行 CVE 全面扫描、原生 wheel 兼容测试、真机测试或干净机器安装已通过。所有源代码改动、锁文件与安装包应来自相同交付版本并记录 SHA256。

## 本轮实际验证回填

Android共享WebView + Chaquopy方案已真实构建并在Android35 x86_64模拟器安装运行，13项原生验收通过；142项最终课程用例经真实解释器执行通过。实测暴露p08不能用subprocess启动CPython，课程已改用runpy并复测通过。Windows↔Android标准ZIP项目在两端分别真实导入并执行，含多文件import、JSON资源和中文文件名。平板/手机真实WebView交互与深浅主题完成渲染检查。Android最终APK资源59项逐文件SHA256与源码一致，签名及16KiB页ZIP对齐通过。具体记录在 `test-reports/ANDROID_TEST_REPORT.md`，仍未执行Android实体设备或ARM64设备验证。
