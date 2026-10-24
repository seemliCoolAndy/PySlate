# PySlate 0.3.0 检查与更新报告

> 源码快照说明：安装包、测试报告、截图、PNG 原稿、交付校验清单及完整历史归档属于原始交付资料，未随本仓库提供。相关路径仅用于标识历史文件；本文保留的测试结果是原交付记录，不表示本次发布重新执行。当前可编辑源码位于仓库根目录。

日期：2026-10-23（Asia/Shanghai）。本轮按“检查并直接修复、适当加强难度、提升审美”的反馈完成。原始交付源码提交 `7465ec9842d85b9545564d97571979e754a3073c`，原工作区本地标签 `v0.3.0`；这不是本公开仓库的提交或已发布标签。旧版0.1/0.2安装文件与报告保留。

## 可安装文件与预览

| 内容 | 文件 |
|---|---|
| Windows x64安装包 | PySlate-0.3.0-windows-x64-setup.exe（历史交付路径：`../windows/PySlate-0.3.0-windows-x64-setup.exe`） |
| Windows便携包 | PySlate-0.3.0-windows-x64-portable.zip（历史交付路径：`../windows/PySlate-0.3.0-windows-x64-portable.zip`） |
| Android APK | PySlate-0.3.0-android.apk（历史交付路径：`../android/PySlate-0.3.0-android.apk`） |
| 源码与完整版本历史 | 源码ZIP（历史交付路径：`../PySlate-0.3.0-source.zip`）、Git bundle（历史交付路径：`../PySlate-0.3.0-history.bundle`） |
| 测试与修复证据 | 报告ZIP（历史交付路径：`../PySlate-0.3.0-test-reports.zip`）、逐文件校验（历史交付路径：`../SOURCE-MANIFEST.json`） |
| 界面截图 | 浅色桌面（历史交付路径：`../previews/PySlate-0.3-desktop.png`）、深色桌面（历史交付路径：`../previews/PySlate-0.3-dark.png`）、手机阅读（历史交付路径：`../previews/PySlate-0.3-phone.png`） |

程序仍然免费、离线、无需账户，无广告或运行时AI服务。测试创建的项目只存在于隔离资料中，不作为首次安装的假数据。

## 修复的实际问题

1. **保存失败造成状态不一致。** 两端在校验或索引写盘失败后保留原元数据与文件，避免虚假进度、幽灵项目、孤儿目录，以及文件已被改动却仍显示失败。界面只在写入成功后确认状态。
2. **新建文件覆盖已有代码。** Windows旧版能用 `MAIN.py` 绕过界面精确判重并覆盖 `main.py`。改用后端独占创建，两端拒绝同名和大小写别名，创建期间的竞争也不会覆盖。
3. **快速操作与输入状态。** 停止后迟到的事件不能重新开启输入；手机项目文件页切换到宽屏会恢复编辑器。重命名期间锁住编辑器与手机符号栏，避免自动保存把旧路径重新创建。
4. **答案载入与页面切换。** 独立审查复现了等待来源保存时切页造成空编辑器异常和来源/草稿不一致。现按顺序完成操作，来源与代码一起保存；失败保留原状态。
5. **Windows安装与卸载。** 实测修复文件被占用时的半更新；安装器在写入前拒绝目录链接，卸载器只清理安装清单及其必要父目录，保留未列入清单的文件夹和链接。
6. **Android项目整理。** 复制保留分类、封面和练习属性；修复ZIP导入清理与大小写冲突、无效默认封面颜色和深色主题系统栏不同步。
7. **教材参考实现。** 修复嵌套可变对象污染历史快照、重复内容时缩容失效、负矩阵尺寸静默变空、v2存档done类型及重复ID校验五个问题。

旧版复现、故障注入和修复后结果分别保存，不把未运行的路径记作通过。新增快速操作修复由独立审查（历史交付路径：`../test-reports/v030-independent-review.json`）核对；课程旧/新断言对比见课程回归（历史交付路径：`../test-reports/v030-course-regressions.json`）。

## 课程难度与图片

58个主题仍有初、中、高三级，共174个完整单元。全量审阅分层任务后，增强 **33个单元（10个中级、23个高级）**，其中19个单元的示例或参考程序实质修改。保留58个初级单元作为零基础入口。中高级新增严格输入契约、逐步不变量、反例、往返性质、独立算法对照以及失败不改原数据等要求。

例如：固定加减升级为逐笔库存流水；颜色转换增加严格RGB解析与格式化；单次最大值升级为一次扫描两个不同最大值；切片求和升级为滚动窗口；默认值填充升级为配置覆盖、未知键拒绝和来源追踪。具体33项及174单元的保留/增强依据见[课程审阅说明](CURRICULUM_REVIEW_V030.md)和逐单元记录（历史交付路径：`../test-reports/v030-curriculum-review.json`）。

所有174张独立生成图均保留，仍解释相应概念的状态、过程或结构；本轮没有将复用图片称为新生图。原图与生成记录见artwork及源码IMAGE_GENERATION_V2.json。新课程SHA为 `01285b531fad45de0faf3e30374ffee559cd135c07fe62a533539825e491f39e`，覆盖与唯一性检查174/174。原始图的既有审批按SHA关联，本轮检查实际两端加载及课程关联。

多文件课程现在直接展示/编辑真正的main.py，并可展开阅读辅助模块。载入示例或答案会准备对应模块并记住所选来源；两种练习目录分别保存，修改或重启后仍可运行。普通项目继续使用标准Python目录与文件。

## 界面调整

统一暖白、墨绿与少量暖色的配色；深色模式使用对应层次。调整标题、正文、练习区、章节进度与图片留白，手机保留独立阅读和编程页。首页新增主题/层级/进度概览，课程搜索匹配主题与知识点，“继续学习”返回上次层级。关键文字对比度、320/390像素、平板和桌面检查通过；不宣称完整无障碍认证。独立审查实际查看21张稳定/过渡截图，最终原生截图也单独核对。

## 验证结果

以下套件有重叠，不能把所有数字相加当成独立功能数量。

| 范围 | 结果 | 证据 |
|---|---|---|
| 普通CPython课程 | 639/639 | 课程（历史交付路径：`../test-reports/v030-course.json`） |
| Windows随包CPython3.13.16＋worker课程 | 639/639 | 嵌入课程（历史交付路径：`../test-reports/v030-course-embedded313.json`） |
| Android CPython3.14.8课程 | 639/639，641次程序执行含后续启动 | Android课程（历史交付路径：`../test-reports/android-v030-course.json`） |
| Windows存储／输入专项 | 16/16、15/15 | 存储（历史交付路径：`../test-reports/windows-storage-v030.json`）、输入（历史交付路径：`../test-reports/windows-input-v030.json`） |
| 最终Windows运行／安装／0.2→0.3升级 | 22/22、7/7、9/9 | 运行（历史交付路径：`../test-reports/windows-v030-runtime-final.json`）、安装（历史交付路径：`../test-reports/windows-v030-installer-final.json`）、升级（历史交付路径：`../test-reports/windows-v030-upgrade-final.json`） |
| 最终Windows原生WebView2 | 13/13、174图解码、关闭前保存通过 | 原生（历史交付路径：`../test-reports/windows-native-v030-final/windows-native-v030.json`） |
| 最终Windows安装失败回滚、安装/卸载链接保护 | 均通过 | 回滚（历史交付路径：`../test-reports/windows-v030-rollback-final.json`）、安装链接（历史交付路径：`../test-reports/windows-v030-installer-link-final.json`）、卸载链接（历史交付路径：`../test-reports/windows-v030-uninstaller-link-final.json`） |
| 共享界面主流程／新增快速操作回归／多文件答案 | 20/20、8/8、5/5 | 主流程（历史交付路径：`../test-reports/v030-ui-r2/ui-tests.json`）、回归（历史交付路径：`../test-reports/v030-ui-regressions-r2/review-v3.json`）、多文件（历史交付路径：`../test-reports/v030-companion-r2/companion-files-v3.json`） |
| 外观搜索与响应式／共享图片实际加载 | 5/5、174/174 | 外观（历史交付路径：`../test-reports/v030-design-final/design-v3.json`）、图片（历史交付路径：`../test-reports/v030-diagrams-final/diagrams-v2.json`） |
| Android存储审查／运行文件／输入专项 | 43/43、13/13、9/9 | 审查（历史交付路径：`../test-reports/android-v030-audit.json`）、运行文件（历史交付路径：`../test-reports/android-v030-smoke.json`）、输入（历史交付路径：`../test-reports/android-v030-input.json`） |
| 最终Android层级保存／手机输入／原生主题 | 10/10、8/8、6/6 | 层级（历史交付路径：`../test-reports/android-v030-learning-ui.json`）、手机输入（历史交付路径：`../test-reports/android-v030-input-ui.json`）、主题（历史交付路径：`../test-reports/android-v030-native-theme.json`） |
| 最终Android多文件示例／答案与重启恢复 | 8/8 | 配套模块（历史交付路径：`../test-reports/android-v030-companion-ui.json`） |
| 最终APK资源与图片 | 297共享资源逐字相符、174图解码 | 交付证明（历史交付路径：`../test-reports/android-v030-delivery.json`） |

Android课程及原生存储/输入套件在最后一次界面微调前执行；最终构建逐项证明课程和所有相关原生输入仍为同一SHA。最终APK重新安装并验证界面、图片、中文输入、主文件及配套模块，详细沿用范围见构建追溯（历史交付路径：`../test-reports/android-v030-build-provenance.json`）。没有把沿用结果说成全课程又跑了一遍。Windows安装包嵌入的ZIP与便携包完全相同。

## 已知验证边界

Android为API35 x86_64专用模拟器，未验证实体手机、实体平板或ARM64执行；arm64-v8a虽已打包，不代表真机验证。Windows仅当前开发主机，未覆盖缺少WebView2的干净系统以及普通快捷方式/注册表登记分支。Windows EXE未签名，Android使用开发签名。测试中出现的模拟器启动器弹窗与首次图片点击时序问题保留诊断记录，修正测试等待后通过，未当成产品缺陷。

本轮是实际功能、保存/升级、课程正确性与视觉检查，不是穷尽性安全审计或长期压力测试。Windows Python使用当前账户权限，Android运行服务共享应用UID；进程时间和输出限制不是文件安全沙箱。核心运行离线，系统WebView组件仍可能按其自身规则更新。其他兼容限制与使用方法见[用户指南](USER_GUIDE.md)。

## 最终校验

- Windows安装包：`d58cecc70e69735757a19af32450a86e5a6365ed57de54159ad90ff9cc815483`
- Windows便携包：`b6ece693babbe86e81d8426425d054051cae6740980df6f8b29e995e2190a558`
- Android APK：`73634b945bd84aee1e0ca6d4bfb7f5b22ef193035c3bf5ac5c205432200e7cc5`

完整源码/测试归档校验见SHA256SUMS.txt（历史交付路径：`../SHA256SUMS.txt`），整体资源一致性见最终检查（历史交付路径：`../test-reports/final-integrity-v030.json`）。
