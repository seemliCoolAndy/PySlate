# PySlate 0.1.0 交付报告

> 源码快照说明：安装包、测试报告、截图、PNG 原稿、交付校验清单及完整历史归档属于原始交付资料，未随本仓库提供。相关路径仅用于标识历史文件；本文保留的测试结果是原交付记录，不表示本次发布重新执行。当前可编辑源码位于仓库根目录。

日期：2026-10-20（Asia/Shanghai）。本报告依据交付目录中的实际产物、JSON测试记录、构建日志和原生截图整理。它区分模拟器与实体设备、安装包解包验证与干净系统安装验证，不以生成代码或截图代替运行。

## 已交付内容

PySlate提供两个离线模式：中文Python学习，以及管理真实Python文件的自由编程资料库。无账户、会员、广告、在线AI API、云数据库或持续付费服务器依赖。安装后阅读、编辑、运行与项目管理可断网使用。

| 内容 | 位置 | 说明 |
|---|---|---|
| Windows x64安装程序 | PySlate-0.1.0-windows-x64-setup.exe（历史交付路径：`../windows/PySlate-0.1.0-windows-x64-setup.exe`） | 内置CPython与完整WebView2离线再分发安装器 |
| Windows便携包 | PySlate-0.1.0-windows-x64-portable.zip（历史交付路径：`../windows/PySlate-0.1.0-windows-x64-portable.zip`） | 解压后运行PySlate.exe，保留完整目录 |
| Android安装包 | PySlate-0.1.0-android.apk（历史交付路径：`../android/PySlate-0.1.0-android.apk`） | arm64-v8a与x86_64，当前为开发签名 |
| 完整应用源码 | [仓库源码](../) | Web界面、平台外壳、运行服务、课程、构建与测试脚本 |
| 中文课程 | [course.json](../course/course.json) | 50个知识主题＋8个项目，共58课；示例和答案均实际执行 |
| 教学图 | [course-assets](../web/course-assets/) | 57张原创SVG＋1张实际生成的AI概念PNG，共58张；58课逐课至少1张 |
| 用户说明 | [USER_GUIDE.md](USER_GUIDE.md) | 安装、学习、编程、交换项目与数据备份 |
| 调查与许可 | [技术调查](OPEN_SOURCE_RESEARCH.md)、[licenses](../licenses/) | 采用与未采用方案、来源和第三方原文 |
| 验证证据 | test-reports（历史交付路径：`../test-reports/`） | 真实输出、JSON、日志、原生截图及历史失败记录 |

最终二进制校验值分别以 Windows SHA256SUMS.txt（历史交付路径：`../windows/SHA256SUMS.txt`） 和 Android SHA256SUMS.txt（历史交付路径：`../android/SHA256SUMS.txt`） 为准。本报告不固定重打包前的旧校验值。源码压缩副本的实际文件名及校验见交付目录的最终清单；当前仓库根目录保留可编辑源文件。

## 功能完成情况

学习模式包含学习目标、原创中文概念解释、执行过程、可运行代码、动手练习、完整答案、具体常见错误与总结。按用户补充要求，全部58课各有至少1张独立教学图，并支持轻点放大；图示对应本课概念、执行流程、数据结构或项目模块。主题从第一条print、input、变量与控制流开始，逐步覆盖容器、函数、模块、文件、JSON/CSV、异常、类与继承、迭代、生成器、装饰器、上下文管理、类型提示、算法和测试。八个项目为猜数字、计算器、成绩统计、待办、文本分析、CSV分析、记账本和真实多文件CLI。具体路线和前置关系见[课程说明](COURSE.md)。

自由编程提供项目新建、名称与封面颜色、分类、搜索、最近使用、复制、重命名、软删除、多文件编辑、资源文件、自动保存与标准ZIP交换。资料库中的项目对应正常目录和`.py`文件，课程资源、学习草稿、用户项目与应用运行数据分别存储。项目在Windows和Android之间真实双向导入、执行通过；没有云同步。

共享界面使用CodeMirror编辑器、明暗主题和响应式布局。Windows及平板采用课程/编辑器分栏，可调整阅读比例；手机使用“读课程”和“写代码/运行”切换及符号输入栏。控制台显示真实Python输出与traceback，input通过输入桥接收用户文字。运行有停止、超时和输出限制，耗时程序放在独立进程中。

## 实际技术方案

| 部分 | 最终实现 |
|---|---|
| 界面 | 本地HTML/CSS/JavaScript；CodeMirror 6、Marked、DOMPurify；资源随包提供 |
| Windows | WinForms＋WebView2；私有CPython 3.13.16嵌入式发行版；本地回环桥接与独立子进程 |
| Android | 系统WebView＋Chaquopy 17.1.0；CPython 3.14.8；独立`:runner`服务进程与输入输出桥 |
| 持久化 | 普通项目目录、UTF-8文件、原子JSON索引、历史版本与项目回收站 |
| 执行控制 | Windows Job Object；Android主进程watchdog与运行服务终止；每次运行30秒、输出256KiB |
| 项目交换 | 标准ZIP，路径、体积、重复名称、链接等检查；不引入私有代码格式 |

没有采用Flutter路线，原因与候选组件比较记录在[开源技术调查](OPEN_SOURCE_RESEARCH.md)。软件没有重新实现Python解释器或代码编辑器。

## 已执行的测试

下表计数取自对应JSON中的实际结果。不同测试套件存在覆盖重叠，不把这些数字相加宣传为独立功能总数。

| 范围 | 结果 | 实际证据 |
|---|---|---|
| Windows真实运行、文件、ZIP、停止与恢复 | 22/22通过 | windows-runtime.json（历史交付路径：`../test-reports/windows-runtime.json`） |
| Windows EXE工作区安装、随包Python、卸载保留数据 | 7/7通过 | windows-installer.json（历史交付路径：`../test-reports/windows-installer.json`） |
| 最终Windows原生窗口六场景 | 6/6通过 | windows-native.json（历史交付路径：`../test-reports/windows-native.json`）及同前缀PNG、DOM与日志 |
| 共享Web界面最终自动化 | 20/20通过 | ui-tests.json（历史交付路径：`../test-reports/ui-tests.json`），真实本地CPython桥接 |
| Windows删除回滚、junction与输入事件预算回归 | 4/4通过 | windows-regressions.json（历史交付路径：`../test-reports/windows-regressions.json`） |
| 随Windows包解释器＋真实worker运行课程 | 142/142通过 | windows-course.json（历史交付路径：`../test-reports/windows-course.json`） |
| 独立普通CPython 3.12课程执行 | 142/142通过 | course.json（历史交付路径：`../test-reports/course.json`） |
| 独立嵌入CPython 3.13.16＋worker课程执行 | 142/142通过 | course-embedded313.json（历史交付路径：`../test-reports/course-embedded313.json`） |
| 同一解释器连续示例→答案→示例 | 3/3通过 | course-repeat-run.json（历史交付路径：`../test-reports/course-repeat-run.json`） |
| Android真实解释器、Binder、文件与运行控制 | 13/13通过 | android-smoke.json（历史交付路径：`../test-reports/android-smoke.json`） |
| Android全部课程 | 142/142通过，共144次程序执行 | android-course.json（历史交付路径：`../test-reports/android-course.json`） |
| Android手机竖屏WebView交互 | 7/7通过 | android-phone-ui-smoke.json（历史交付路径：`../test-reports/android-phone-ui-smoke.json`） |
| Android平板横屏WebView交互 | 7/7通过 | android-tablet-ui-smoke.json（历史交付路径：`../test-reports/android-tablet-ui-smoke.json`） |
| Android中文路径、ZIP、复制与文件操作 | 5/5通过 | android-native-extra.json（历史交付路径：`../test-reports/android-native-extra.json`） |
| 每课教学图覆盖与真实离线载入 | 58/58课各1张；57张SVG文字画布越界为0 | 图片覆盖（历史交付路径：`../test-reports/diagram-coverage.json`）、真实图片渲染（历史交付路径：`../test-reports/diagram-rendering.json`） |
| 编辑器实际键盘缩进 | Enter、Tab、Shift+Tab均为4空格 | keyboard.json（历史交付路径：`../test-reports/keyboard.json`） |
| Windows导出→Android导入并执行 | 通过 | windows-to-android-result.json（历史交付路径：`../test-reports/windows-to-android-result.json`） |
| Android导出→Windows导入并执行 | 通过 | windows-import-android.json（历史交付路径：`../test-reports/windows-import-android.json`） |

共享Web界面最终20项自动化均通过，覆盖课程、真实输入与报错、草稿持久化、项目ZIP，以及导航、保存次序、旧运行事件与二进制资源等边界。逐条结果保留在ui-tests.json（历史交付路径：`../test-reports/ui-tests.json`），与原生安装和设备测试分开核对。重打包后的源码/资源一致性另见Windows完整性报告（历史交付路径：`../test-reports/windows-integrity.json`）与Android资源一致性报告（历史交付路径：`../test-reports/android-asset-consistency.json`）。没有把较早一次浏览器结果扩写成后续所有界面修改均已通过。

Windows截图来自实际交付EXE中的WebView2，覆盖目录、课程、资料库、编辑、交互输入、报错。已查看学习分栏（历史交付路径：`../test-reports/windows-native-lesson.png`）、资料库（历史交付路径：`../test-reports/windows-native-library.png`）、真实输入（历史交付路径：`../test-reports/windows-native-input.png`）与真实traceback（历史交付路径：`../test-reports/windows-native-error.png`）。Android截图来自API35 x86_64模拟器及其真实WebView，已检查手机阅读（历史交付路径：`../test-reports/android-phone-reader.png`）、手机深色（历史交付路径：`../test-reports/android-phone-dark.png`）、平板交互课程（历史交付路径：`../test-reports/android-tablet-lesson.png`）与平板深色（历史交付路径：`../test-reports/android-tablet-dark.png`）。这些是实际渲染证据，不是另画的效果稿。

## 已修复问题与历史记录

Android首轮课程135个非p08用例通过，7个p08失败，原因是Chaquopy没有可用于启动CPython的`sys.executable`。原始结果保留在android-course-before-p08-fix.json（历史交付路径：`../test-reports/android-course-before-p08-fix.json`）。p08已改为同进程`runpy`执行真实多文件入口，并设置搜索路径和恢复模块缓存；7项补测（历史交付路径：`../test-reports/android-course-p08.json`）全部通过。其余135个用例的可执行字段确认未变，最终汇总明确记录这次合并，不将首轮失败删除。

Windows早期裸嵌入解释器执行也暴露过p08模块搜索路径问题；最终课程报告来自修复后随包解释器和真实worker的重新执行。该早期Windows失败JSON未单独保留下来，因此不把它描述为可供下载的历史证据。课程另修复了文件替换遇到瞬时占用、空时长列表及连续运行的模块缓存问题。

运行服务审阅发现并修复了损坏主索引覆盖唯一有效备份、删除移动回退跟随junction、恢复元数据与用户文件重名、删除失败回滚及零字节输入事件无预算的问题；相应故障与回归检查记录在Windows运行时及专项报告。界面调试留下的失败截图（历史交付路径：`../test-reports/ui-failure.png`）也予以保留；最终界面状态以对应修复后的逐条复测为准。

## 权限、许可与隐私边界

**Windows执行不是安全沙箱。** CPython拥有当前Windows用户权限，能够访问项目外文件、网络及系统程序。Job Object提供进程树、时间与资源控制，不能限制文件权限。信任提示、项目API的相对路径检查和ZIP校验，不会把任意Python程序变成安全代码。

**Android运行服务与UI共享应用UID。** 它能访问本应用私有数据；进程隔离用于停止和清理状态，不是抵御恶意代码的文件安全沙箱。应用未申请INTERNET和外部存储权限，导入导出通过系统文档选择器。只运行自己理解并信任的程序。终止程序不会撤销此前已写入的文件。

PySlate原创源码采用MIT；CPython、Chaquopy、CodeMirror、Marked、DOMPurify和随运行时组件分别遵循自己的许可。具体原文见[licenses](../licenses/)、[npm逐包清单](../licenses/npm-dependencies.json)和[Android第三方归属](../licenses/Android-Third-Party-NOTICES.md)。开发工具不混同为随包运行依赖。

Windows的**Microsoft WebView2 Runtime是免费可再分发的专有组件**，适用Microsoft条款；它与WebView2 SDK的许可不能混为一谈。安装包附完整离线安装器和许可，检测到合适版本时复用。共享组件自身可能自动更新、发送诊断或SmartScreen信息，详见[随附条款](../licenses/WebView2-Runtime-LICENSE.txt)。PySlate核心离线可用，不代表系统显示组件永不联网。Android使用设备提供的系统WebView，其更新由系统与应用商店管理。

## 未完成或未验证的范围

- Android只在API35 x86_64模拟器执行，手机和平板是同一模拟器的不同尺寸配置；没有实体手机、实体平板或ARM64执行结果。arm64-v8a运行库已打包，不能据此声称ARM64已测试。最低API26、所有厂商WebView、输入法与实体键盘组合未覆盖。
- Windows实测来自当前开发主机。无WebView2的干净系统安装分支未执行；普通用户快捷方式与注册表登记分支未执行。不能把7项工作区安装器测试称为所有Windows首次安装场景已通过。
- Windows安装器与应用未做商业代码签名，可能显示未知发布者或SmartScreen提示。Android APK使用开发签名，尚未建立应用商店发布签名及长期升级流程。
- Windows仅交付x64；Windows ARM64、x86、多显示器、全部DPI、企业策略与杀毒环境未形成完整矩阵。
- 未承诺任意pip包、桌面GUI库、原生科学计算扩展、系统命令或multiprocessing在两端通用。Windows嵌入包不含pip、Tk/IDLE；Android没有常规桌面进程环境。第三方生态需逐包构建与验证。
- 运行时限制为教学和小型脚本服务；没有无限时长后台任务、云同步、iOS、图形化历史恢复页、完整审计账本、全面CVE/供应链审计或长期压力测试。

## 建议的后续顺序

1. 使用独立测试设备完成干净Windows10/11安装，以及Android ARM64实体手机和平板测试。
2. 建立正式签名、发布渠道、升级兼容和用户数据恢复演练。
3. 扩大输入法、硬件键盘、屏幕缩放、低内存与系统WebView版本覆盖。
4. 增加可操作的历史版本/回收站恢复页，并为长期运行、额外标准库和第三方包逐项定义支持范围。

构建入口和复测命令见[源码README](../README.md)、[Windows维护说明](WINDOWS_ARCHITECTURE.md)与[Android维护说明](ANDROID.md)。
