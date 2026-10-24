# Windows 使用说明

> 源码快照说明：安装包、测试报告、截图、PNG 原稿、交付校验清单及完整历史归档属于原始交付资料，未随本仓库提供。相关路径仅用于标识历史文件；本文保留的测试结果是原交付记录，不表示本次发布重新执行。当前可编辑源码位于仓库根目录。

PySlate 0.3.0 支持 Windows 10 22H2 / Windows 11 的 x64 电脑。内置 CPython 3.13.16，无需另外安装 Python。

## 安装与打开

运行 `windows/PySlate-0.3.0-windows-x64-setup.exe`，阅读随附 Microsoft WebView2 许可条款并勾选同意，选择安装位置后点击安装。默认仅安装到当前用户的 `%LOCALAPPDATA%/Programs/PySlate`，无需管理员权限。可以选择创建桌面和开始菜单快捷方式。

安装包已包含完整 WebView2 离线安装器。检测到电脑已有合适版本时直接复用；缺失时才运行随附组件安装器，不需要在线下载。Microsoft WebView2 本身可能自动更新及发送诊断或 SmartScreen 信息，详见 `licenses/WebView2-Runtime-LICENSE.txt`。PySlate 课程、编辑器、项目与 Python 执行均可断网使用，无登录、会员或 AI 服务。

安装后打开“PySlate”。也可解压 portable ZIP 后打开整个目录中的 `PySlate.exe`。请保留全部 `python/`、`runtime/`、`web/`、`course/` 及 DLL，不能只复制一个 EXE。portable 方式若电脑没有 WebView2，请先运行随附 `redist/MicrosoftEdgeWebView2RuntimeInstallerX64.exe`。

安装程序尚未做商业代码签名，因此 Windows 可能显示“未知发布者”。核对交付目录 `SHA256SUMS.txt` 中的哈希后再决定运行。

## 学习与编程

“Python 学习”包含 58 个主题、174 个学习单元，每个主题可切换初级、中级、高级，各层有独立讲解、配图、示例、练习、代码草稿及完成标记。选择课程后，在右侧修改代码并点击“运行”。程序调用 `input()` 时，控制台下方的输入框会亮起；输入后按 Enter 或点击发送，空行也可发送。程序真实运行于随附 CPython，错误会显示原始 Python 信息。

“我的项目”管理普通 Python 项目。可以创建、分类、复制、重命名、增加代码与资源文件；使用 ZIP 将项目在 Windows 与 Android 之间手动交换。ZIP 包保留正常的目录和真实 `.py` 文件，能在普通 Python 开发环境中使用。

默认自动保存。`Ctrl+S` 立即保存，`Ctrl+Enter` 运行，`Tab` 缩进，`Ctrl+F` 搜索代码。窗口关闭时会先等待最后编辑写入；若保存失败会提示继续编辑，建议返回并重试保存。

## 运行边界

每次程序累计执行预算为 30 秒；等待 `input()` 或文本标准输入时暂停该预算，每次等待最多 5 分钟。提交一行后恢复执行计时，多次输入不会重置已用的执行预算。空行是合法输入；同一次提问只能提交一份，过期或重复输入会被拒绝。最多显示 256 KiB 输出，最多 256 次输入请求和 8192 条事件。可以随时点击停止。Windows 通过 Job Object 停止入口及其后代进程，并设置 512 MiB 内存和最多 16 个进程的限制，避免常见失控程序拖住界面。

Windows 版不是文件系统安全沙箱。Python 拥有当前 Windows 用户的权限，可以访问项目之外的文件、网络和系统程序。第一次运行前请仔细阅读信任提示，只运行可信代码。不可信程序应在独立系统账户或虚拟机中处理。

CPython 的标准库可离线使用，包括 JSON、CSV、pathlib、statistics、unittest 和 SQLite。没有预装第三方包、pip、Tk/IDLE；不要把桌面图形库、科学计算包或平台专属扩展视为已支持。

## 备份与升级

用户数据位于 `%LOCALAPPDATA%/PySlate/Data`，与安装目录分开。升级或卸载应用会保留该目录。需要迁移整份学习记录时，请退出应用后备份整个 Data 文件夹；单个项目也可导出 ZIP。

升级前退出所有 PySlate 窗口，运行新版安装包并选择原安装目录。0.2 兼容现有 0.1 安装标记；旧版课程草稿、完成标记和练习项目继续属于对应主题的初级，中高级使用独立记录，不覆盖原练习。整份学习记录通过备份 Data 迁移，项目 ZIP 只交换单个项目文件。

删除项目采用软删除，位于 `Data/trash/`，旁边同前缀的 `.recovery.json` 记录项目原名称。历史文件版本在 `Data/backups/<项目ID>/`，每项目保留最近 100 版。0.2 版尚无图形恢复页，可从普通文件夹手动取回代码。`catalog.previous.json` 是上一次索引备份，正常情况下由应用自动用于故障恢复。同一份资料库同时只允许一个 PySlate 窗口写入，第二次打开会提示返回现有窗口。

从 Windows“已安装的应用”卸载，或运行安装目录中的 `Uninstall.exe`。卸载只移除安装清单列出的应用文件，保留独立 Data 数据；也会保留安装目录里没有列入清单的用户自建文件。共享 WebView2 Runtime 不随 PySlate 卸载，避免影响其他软件。

## 排障与已知限制

若打不开界面，确认 .NET Framework 4.8、x64 Windows 和完整应用文件存在；不要从 ZIP 的预览窗口直接运行。WebView2 安装若被组织策略阻止，请由系统管理员按组织规则处理，PySlate 不会绕过策略。

导入 ZIP 上限 20 MiB，解压后总量 50 MiB，最多 1000 条目；不接受链接、加密文件、设备路径、路径穿越或异常高压缩比。编辑器仅打开 <=1 MiB 的 UTF-8 文本，图片等二进制资源可通过 ZIP 保留，但不能在文本编辑器中直接修改。

开发验证运行于一台 Windows 主机。尚未对全新无 WebView2 机器、全部 DPI/多显示器组合、企业安装策略及每种杀毒环境完成覆盖，详见 `test-reports/windows-installer.json` 和 `docs/WINDOWS_ARCHITECTURE.md`。
