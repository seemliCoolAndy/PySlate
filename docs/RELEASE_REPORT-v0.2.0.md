# PySlate 0.2.0 发布报告

> 源码快照说明：安装包、测试报告、截图、PNG 原稿、交付校验清单及完整历史归档属于原始交付资料，未随本仓库提供。相关路径仅用于标识历史文件；本文保留的测试结果是原交付记录，不表示本次发布重新执行。当前可编辑源码位于仓库根目录。

日期：2026-10-20（Asia/Shanghai）。本报告依据最终安装文件、真实运行记录与文件SHA核对整理；旧版0.1.0报告和安装包另行保留。

## 本次更新

PySlate继续提供离线中文Python学习与真实文件项目编程。0.2.0将50个知识主题、8个项目全部扩展为初级、中级、高级，共174个完整学习单元；每单元有独立概念图、示例、练习和答案。另一项重点是修复交互输入：思考等待不再消耗30秒执行预算，空行、连续输入、中文输入法和手机键盘场景均有真实运行证据。应用无账户、广告、在线AI接口或云同步依赖。

## 交付清单与追溯

以下为实际生成的0.2.0产物；完整文件清单与校验见DELIVERY.json（历史交付路径：`../DELIVERY.json`）及SHA256SUMS.txt（历史交付路径：`../SHA256SUMS.txt`）。

| 产物 | 最终路径 |
|---|---|
| Windows x64安装程序 | PySlate-0.2.0-windows-x64-setup.exe（历史交付路径：`../windows/PySlate-0.2.0-windows-x64-setup.exe`） |
| Windows便携包 | PySlate-0.2.0-windows-x64-portable.zip（历史交付路径：`../windows/PySlate-0.2.0-windows-x64-portable.zip`） |
| Android开发签名APK | PySlate-0.2.0-android.apk（历史交付路径：`../android/PySlate-0.2.0-android.apk`） |
| 源码、Git历史、测试记录 | source.zip（历史交付路径：`../PySlate-0.2.0-source.zip`）、history.bundle（历史交付路径：`../PySlate-0.2.0-history.bundle`）、test-reports.zip（历史交付路径：`../PySlate-0.2.0-test-reports.zip`） |
| 可编辑源码、图片原稿 | [仓库源码](../)、artwork/masters（历史交付路径：`../artwork/masters/`） |

二进制SHA256以Windows清单（历史交付路径：`../windows/SHA256SUMS.txt`）和Android清单（历史交付路径：`../android/SHA256SUMS.txt`）为准，不在本文固定重打包前的旧值。174张原稿均经实际图像生成工具独立生成并目视检查，审批绑定当前原稿SHA；应用使用同图编码的WebP以减小体积。[提示词](IMAGE_GENERATION_V2.json)、原稿与应用图映射（历史交付路径：`../artwork/image-manifest.json`）、完整审批（历史交付路径：`../test-reports/visual-audit-v020.json`）可供追溯。错误草图与重生记录保留，最终审批只认当前匹配SHA的图。

## 学习内容与存档

初级保留原主题路线与完整基础内容；中级增加组合应用和边界处理；高级讲授状态推理、数据契约、调试、重构和有约束任务。例如字符串高级处理隐藏字符与有界单行预览，循环高级推导欧几里得算法的终止性，JSON高级涉及版本迁移与严格解码。项目增加Decimal计算与表达式解析、稳定待办ID、CSV幂等导入、账本冲销和真实多文件报表。中高级使用不同代码与完整解答，各另有至少两项边界或性质测试；图表达执行路径、结构或状态变化。细节见[课程说明](COURSE.md)。零基础可先完成初级主线，再按前置关系深化，无需先闯过开篇高级。

三个层级的草稿、练习文件和完成标记独立保存，重启保留所选层级。旧版主题键继续归初级，中高级使用独立单元键，已有项目不随难度变化。共享界面测试（历史交付路径：`../test-reports/v020-learning-ui-release/learning-v2.json`）与Android层级测试（历史交付路径：`../test-reports/android-v020-learning-ui.json`）覆盖旧进度、独立草稿及杀进程后恢复；Windows存档核查（历史交付路径：`../test-reports/windows-state-v020.json`）确认旧键与新键可同时保存。

## 输入故障根因与修复

旧版以启动后的壁钟时间计30秒，导致等待输入时被终止；Windows实测约29.997秒退出，Android同样复现。Android还出现零长度读取错误等待。原始记录保留于Windows旧版复现（历史交付路径：`../test-reports/windows-input-before-v020.json`）与Android旧版复现（历史交付路径：`../test-reports/android-input-before-v020.json`）。

新版分别累计执行时间与每次文本输入等待：执行累计最多30秒，真实等待期间暂停，每次最多等待5分钟，恢复后继续累计。输入请求带编号及状态版本，拒绝重复、过期和多行提交；空字符串仍是合法空行。零长度读取立即返回，部分读取保留余文。界面避免旧快照重新开启已消费请求，输入法选字时不提前发送，换文件保留等待和未发送文字，软键盘弹出后缩小可用区域。保存流程同时固定旧层级归属，防止切换尚未完成时将编辑写入新层级。复测包含真实等待超过31秒后成功提交；5分钟截止使用缩短的测试预算验证，并未宣称实等5分钟。

## 已完成验证

数字来自对应JSON，不将相互重叠的套件相加。课程示例、答案和断言均在真实Python执行，逐项比较输出、退出码，必要时检查产物文件及后续运行。

| 范围 | 已核对结果 | 证据 |
|---|---|---|
| 普通CPython 3.12.14课程 | 612/612 | course-v2.json（历史交付路径：`../test-reports/course-v2.json`） |
| 嵌入CPython 3.13.16＋真实worker课程 | 612/612 | course-v2-embedded313.json（历史交付路径：`../test-reports/course-v2-embedded313.json`） |
| Android课程174单元 | 612/612，基线614次程序执行 | android-v020-course.json（历史交付路径：`../test-reports/android-v020-course.json`） |
| 共享界面层级、保存与输入专项 | 12/12 | learning-v2.json（历史交付路径：`../test-reports/v020-learning-ui-release/learning-v2.json`） |
| Windows新输入专项 | 15/15，发行解释器＋新运行源码 | windows-input-v020.json（历史交付路径：`../test-reports/windows-input-v020.json`） |
| Android层级／输入／手机输入界面 | 10/10、9/9、8/8 | 层级（历史交付路径：`../test-reports/android-v020-learning-ui.json`）、输入（历史交付路径：`../test-reports/android-input-v020.json`）、手机（历史交付路径：`../test-reports/android-v020-input-ui.json`） |
| Android运行、文件与ZIP smoke | 13/13 | android-v020-smoke.json（历史交付路径：`../test-reports/android-v020-smoke.json`） |
| 独立图生成及最终SHA审批 | 174/174 | visual-audit-v020.json（历史交付路径：`../test-reports/visual-audit-v020.json`） |
| 最终Windows真实WebView2 | 13/13，174/174图解码，关闭前保存通过 | 原生报告（历史交付路径：`../test-reports/windows-native-v020-final/windows-native-v020.json`）、图解码（历史交付路径：`../test-reports/windows-native-v020-final/native-image-decode.json`） |
| 最终Windows运行／安装 | 22/22、7/7 | 运行（历史交付路径：`../test-reports/windows-v020-runtime.json`）、安装（历史交付路径：`../test-reports/windows-v020-installer.json`） |
| 实际0.1→0.2升级／Windows完整性 | 9/9；282源、351包文件与352ZIP条目匹配 | 升级（历史交付路径：`../test-reports/windows-v020-upgrade.json`）、完整性（历史交付路径：`../test-reports/windows-v020-integrity.json`） |
| 最终APK安装、174图解码与资源一致性 | 通过；295共享资源逐字一致 | 原生图片（历史交付路径：`../test-reports/android-v020-images.json`）、APK一致性（历史交付路径：`../test-reports/android-v020-delivery.json`） |
| 全174单元共享界面离线图片与手机放大 | 174/174，无坏图 | 真实浏览器解码（历史交付路径：`../test-reports/v020-diagram-ui/diagrams-v2.json`）、覆盖（历史交付路径：`../test-reports/diagram-coverage-v2.json`） |

Android课程汇总保留完整基线（历史交付路径：`../test-reports/android-v020-course-base.json`），其614次程序执行包含后续运行。逐单元比较全部执行字段后，仅l02、l05、l06高级有变化，另行补测4项（历史交付路径：`../test-reports/android-v020-course-l02-advanced.json`）、4项（历史交付路径：`../test-reports/android-v020-course-l05-advanced.json`）、4项（历史交付路径：`../test-reports/android-v020-course-l06-advanced.json`），用这12项替换汇总对应结果；不把补测冒称最终课程又完整重跑一次。最终课程SHA为 `6ee9efd7b28fbb6a8c1a8f5dd6276dac37b2705c09f3db3231e3c8d22fc53b78`。

## 实际边界

Android只在API35 x86_64模拟器执行，手机与平板为尺寸配置，未测实体设备或ARM64；打包arm64-v8a不等于已验证。Windows仅在当前开发主机测试，无WebView2的干净系统安装、普通用户快捷方式与注册表登记分支未测。Windows EXE未代码签名；APK为开发签名，尚非正式商店发布签名。

Windows Python拥有当前用户权限；Android运行服务与界面共享应用UID。独立进程、停止和ZIP路径检查都不构成文件安全沙箱，停止不会撤销已写文件。只运行可信程序。课程使用标准库，不承诺任意pip包、桌面GUI、原生扩展或系统子进程两端通用。

Microsoft WebView2 Runtime是按其条款免费再分发的专有组件，可能自行更新并发送诊断；Android系统WebView也由系统更新。核心离线不代表系统组件从不联网。第三方许可见[licenses](../licenses/)，构建和复测入口见[源码README](../README.md)。

## 版本一致性与保留记录

源码提交为 `42996af42222a32970e6d1ab5368976d1db018ce`（本地标签v0.2.0）。最终资源冻结后只修正了一行Windows升级测试对CRLF的规范化；重打包记录（历史交付路径：`../test-reports/windows-v020-repack.json`）逐项证明351个应用文件保持原字节，最终安装和升级已用正式修正脚本重新通过。首次测试误判仍保留，未作为产品故障或最终结果。

174张PNG原稿共327396699字节，应用WebP共18507572字节，编码保留各图原尺寸。最终APK经干净重建去除增量打包空洞，再重新核对安装、资源和签名；不采用先前较大草稿的校验值。源码ZIP含逐文件清单，Git bundle保留完整历史，最终跨平台资源核对见最终完整性（历史交付路径：`../test-reports/final-integrity-v020.json`）。

## 主要开源组件与许可

| 组件 | 用途与许可记录 |
|---|---|
| CodeMirror 6、Marked 18.1.1 | 编辑器及Markdown，MIT |
| DOMPurify 3.4.17 | HTML清理，MPL-2.0或Apache-2.0双许可 |
| CPython 3.13.16／3.14.8 | Windows／Android真实解释器，PSF及发行版附属许可 |
| Chaquopy 17.1.0 | Android解释器集成，MIT |
| sharp 0.35.5 | 仅开发期图片编码，Apache-2.0；不作为应用运行依赖 |
| WebView2 SDK／Runtime | SDK附属原文与Runtime Microsoft再分发条款分别保留 |

逐包版本、来源和原文见[npm清单](../licenses/npm-dependencies.json)、[Android原生组件归属](../licenses/Android-Third-Party-NOTICES.md)、[开源调查](OPEN_SOURCE_RESEARCH.md)及[许可证目录](../licenses/)。PySlate原创代码采用MIT。没有完成全面CVE审计、实体设备矩阵、正式发布签名、图形化历史恢复页或长期压力测试。

## 最终二进制SHA256

- `555f4777bd353c2502abaef878cc560cdc139da911fa5ca49885c55e08a84b0e`  PySlate-0.2.0-windows-x64-setup.exe（历史交付路径：`../windows/PySlate-0.2.0-windows-x64-setup.exe`）
- `0c854a2cd68b129f5c547da28139062f489e0819d13501b7b7439827eb8b24ba`  PySlate-0.2.0-windows-x64-portable.zip（历史交付路径：`../windows/PySlate-0.2.0-windows-x64-portable.zip`）
- `ec1e248d7ece361093a2c37de2c95486aca91c99dd9acf05586d57b07495762f`  PySlate-0.2.0-android.apk（历史交付路径：`../android/PySlate-0.2.0-android.apk`）
