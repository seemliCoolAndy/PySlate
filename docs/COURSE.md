# PySlate 离线 Python 课程

v2包含 **50 个知识主题与 8 个项目主题，共58个主题、174个完整学习单元**。每个主题都提供初级、中级、高级：各有目标、概念说明、执行推演、可运行示例、练习、完整答案、常见错误、总结、独立图示引用与执行案例。教材面向从未编程的学习者，也提供处理边界、推理调试和设计重构的进阶路线。学完不代表掌握所有第三方生态或专业领域。

教材由 PySlate 自行组织与编写。Python 官方教程和标准库文档用于事实核查、API 参考与延伸阅读，未批量复制外部中文教程。每课可选的 `sources` 链接明确列出参考来源；离线学习不需要访问这些链接。

## 学习路线

| 阶段 | 课程 | 主要能力 |
|---|---|---|
| 01 从一行程序开始 | l01–l08 | 程序与解释器、输出、注释、变量、数字、字符串、输入、转换、布尔比较 |
| 02 决策与重复 | l09–l16 | 逻辑、分支、for、range、while、break/continue、嵌套、状态追踪与调试 |
| 03 组织一组数据 | l17–l24 | 字符串清洗、列表、修改与筛选、切片与浅复制、元组、字典、集合、推导式 |
| 04 拆成清楚的部件 | l25–l32 | 函数与返回、参数、作用域、模块、包、异常、UTF-8文件、pathlib |
| 05 数据处理与可靠计算 | l33–l40 | JSON、CSV、math/random、datetime/Decimal、collections、排序、复杂度、断言测试 |
| 06 独立开发工具 | l41–l50 | 类与继承、迭代器、生成器、装饰器、上下文管理、类型提示、unittest、环境与依赖、模块职责 |
| 07 综合实战 | p01–p08 | 完整输入协议、边界验证、错误恢复、真实持久化、报表与多文件项目 |

建议先读目标和正文，自己预测示例输出，再运行验证。改动一个变量后重跑，观察差别。练习先独立完成，再查看答案。运行错误时先看 traceback 的最后一行与文件行号，缩小到可以手算的输入；不要只复制答案。

初级沿用完整基础内容，中级加入组合应用与边界处理，高级加入协议设计、状态不变量、算法推理、故障注入或有约束的真实任务。例如字符串高级研究隐藏字符与有界单行预览；循环高级用欧几里得算法说明正确性与终止；集合高级用集合加列表实现稳定高效去重；JSON高级讨论版本迁移与严格解码。三个层级使用不同示例和答案，新中高级还各有至少两个额外边界或性质测试。

`minutes`是阅读、运行与练习的建议分钟数。`prerequisites`保存真实主题ID：基础主题按顺序衔接；个别开篇高级单元明确建议先学循环、函数或异常，再回头深化。无需先完成某主题的高级才能继续下一个主题。先完成初级主线，再按兴趣进入中高级，是适合零基础的路线。不要为了进度数字跳过实际练习。

## 八个项目

| ID | 项目 | 交互与数据 | 验证重点 |
|---|---|---|---|
| p01 | 猜数字 | 输入整数，5次有效机会 | 非法输入不扣次数、越界、命中与失败；固定种子便于复现 |
| p02 | 四则计算器 | 一行数字、运算符、数字 | 格式错误、除零、非有限数值、结果溢出；答案增加有界乘方 |
| p03 | 成绩统计器 | 姓名:分数，以逗号分隔 | 空输入、重复姓名、0至100范围；答案增加稳定排名 |
| p04 | 待办清单 | add/done/list/quit；JSON | 稳定编号、读回、损坏文件不覆盖；答案增加delete |
| p05 | 文本分析器 | UTF-8英文样本；词频报告 | 清洗口径、空行、大小写、同频排序；答案写JSON报告 |
| p06 | CSV销售分析 | 课程生成的CSV；Decimal汇总 | 内含逗号字段、坏行号码、金额验证；答案导出CSV |
| p07 | 本地记账本 | income/expense/summary/quit；CSV | 精度、有限正金额、重新读取、文件保护；答案增加undo |
| p08 | 多文件学习时间CLI | main.py + studytools包 | 真正跨文件import、入口启动、负数验证；答案跨文件增加中位数 |

上表描述初级项目。中高级新增的工作包含猜数字会话状态和二分策略、Decimal运算及表达式语法解析、带坏行定位的成绩导入与加权排名、待办稳定ID及存档迁移、文本检索与TF-IDF、CSV幂等订单导入、账本预算与不可变冲销流水、多文件筛选报表与可迁移JSON产物。每个项目层级都给出可实际运行的完整代码，p08的两层进阶均同时提供真实多文件映射。

p04和p07会保留项目内的数据。首次演示输出以新项目、无旧数据为前提，再次运行出现旧记录是设计行为。它们使用同目录临时文件写完后替换，适合单人学习练习；不提供完整断电事务、并发写入、审计或生产财务保证。待办编号保留现有项身份，但删除最高编号后重启可能复用该编号，需要永久身份时应单独保存计数器或使用UUID。

p05按空白切分英文并去掉有限首尾标点，不能声称是中文分词器。p06报告被跳过的坏行，不声称坏行已修复。p07明确拒绝多于两位小数的输入，而不是悄悄舍入。各项目的范围和限制在对应正文说明。

## 内容和资源格式

`course/course.json`是运行时唯一课程数据入口，schema版本为2。`course/build_course.py`保留原始主题与初级正文，并调用独立作者模块重新生成JSON。`author_tiers_foundation.py`、`author_tiers_data.py`、`author_tiers_packages.py`、`author_tiers_design.py`、`author_tiers_projects.py`保存原创中高级内容；`tier_helpers.py`只统一结构，不批量制造通用讲解。`author_tiers.py`组装层级和基础图示语义；`visual_overrides.py`若存在，仅承载逐张图片复核后的caption/alt修订。页面逻辑与教材分离。

顶层包含`version:2`、`tierOrder`与`chapters`；每章含`id/title/level/description/lessons`。主题原有ID与学习字段继续保留兼容旧端；新增`tiers`固定为beginner、intermediate、advanced。每个层级为完整学习单元，包含：

- `id`为层级ID，`topicId`为原主题ID，`unitId`为例如`l20:advanced`的稳定单元标识，`label`为初级/中级/高级；另有`title/minutes/prerequisites/objectives`。
- `body`：概念解释与具体执行过程，Markdown。
- `code/stdin/expectedOutput`：可载入示例、预置输入及完整期望输出。
- `exercise/solution/solutionExpectedOutput`：动手任务、完整参考答案及答案期望输出。
- `commonMistakes/summary`：具体错误原因及知识总结。
- `diagram`为`course-assets/tier-{topicId}-{id}.webp`；`visual`包含`kind/caption/alt/stages`，描述执行路径、数据关系或状态变化；`sources`提供官方延伸阅读。
- `testCases`是完整执行列表，已经包含example与answer两个基线，不能再自动重复追加。另有输入、文件、边界和性质案例。
- `files/solutionFiles`是可选的相对路径到源代码映射；包主题l29及项目p08提供可直接载入的真实多文件工程。

`stdin` 同时适用于本课示例和答案。`expectedOutput` 只包含程序写出的标准输出，不人为添加终端输入回显。运行界面可能把用户输入单独展示，因此视觉上的控制台文字与该字段不必完全相同。`unittest`正常把详细结果写入标准错误，本课同时检查进程退出状态与标准输出。

全部174单元引用各自独立的教学图，图示说明执行路径、容器关系、资源生命周期或项目架构。v2图片使用逐单元AI生成的原始PNG并转换为应用WebP，同一画面压缩以控制安装体积；原始画稿、生成提示与转换证据由图片流程单独交付。图片完成数、资源实载和手机可读性应以最终图片验收报告为准；课程执行脚本不把图片存在与否算成Python代码通过。应用图文件位于`web/course-assets`，不依赖远程图片服务。

每个case通过`field`选择code或solution，`stdin/expectedOutput`约定输入与精确输出。`replacements:[{find,replace}]`按顺序全局替换选中源码，find不存在必须报测试错误；随后将`assertions`字符串追加到源码，失败即用例失败。`initialFiles/expectedFiles`写入夹具并核对产物；`followupStdin/followupExpectedOutput`在同一工作目录重新启动，验证持久化；`fileSet`选择files或solutionFiles并以`entrypoint`（默认main.py）直接启动。基线和额外案例使用相同退出码与完整输出规则。

## 执行验证与兼容范围

所有`code`、`solution`和变体案例都使用真实CPython批量执行。当前v2共有612个执行案例；最终通过数、课程哈希和运行时版本请直接核对`test-reports/course-v2.json`、`course-v2-embedded313.json`及两端实际运行报告，不能沿用旧142案例版本的结论。`tools/test_course.py`为每个案例建立新临时目录，并检查Python3.11语法、完整元数据、层级顺序、单元ID、前置主题存在性、图示语义与路径模式。临时目录是文件整理措施，不是操作系统安全沙箱。

从源码根目录运行：

```powershell
python course/build_course.py
python tools/test_course.py --report ../test-reports/course-v2.json
```

也可以用 `--python` 指定已准备好的真实 CPython 路径。测试随应用分发的Windows嵌入解释器时，增加 `--worker runtime/worker.py`，使用应用实际的搜索路径设置与input握手协议。报告以 `executionMode` 与 `worker` 明确区分裸解释器和应用worker模式，不能把裸嵌入解释器默认不搜索项目目录误报成应用支持import。JSON报告还记录解释器版本、平台、课程SHA256、每个进程的标准输出/错误、文件清单及用例结果，同时生成便于阅读的Markdown报告。更新课程后必须重新执行，不能沿用旧哈希的测试报告。

作者调试可使用`--topic l29`（可重复）或`--tier advanced`缩小执行范围，报告selection明确记录选择。`--partial`只允许临时不完整教材，不可用于最终验收；正式全量报告不得带筛选或partial。完整报告应为58主题、174单元、612案例、0个schema问题。

兼容目标为 Python 3.11+，教材不使用第三方依赖、不发网络请求。实际执行版本以报告为准；语法兼容检查不等于在所有解释器版本上逐一验证。Windows嵌入解释器的 `._pth` 默认可能不搜索项目目录，因此p08自举显式设置搜索路径，并通过标准库runpy在当前解释器执行入口；正常应用执行由worker设置路径。自举演示无需subprocess或独立 `sys.executable`，可使用Android的输入与输出桥；也可以载入 `files` 项目直接运行 `main.py`。Android不承诺支持pip、venv或第三方原生扩展。应用和设备上的验收与本课程CPython测试应分别报告。

## 官方参考

- [Python 3.11 教程](https://docs.python.org/3.11/tutorial/)：语法、数据结构、模块、异常、类与迭代。
- [输入输出](https://docs.python.org/3.11/tutorial/inputoutput.html)：格式化、UTF-8文件与资源关闭。
- [pathlib](https://docs.python.org/3.11/library/pathlib.html)：可移植路径及文件操作。
- [json](https://docs.python.org/3.11/library/json.html)、[csv](https://docs.python.org/3.11/library/csv.html)：结构化文本格式。
- [decimal](https://docs.python.org/3.11/library/decimal.html)、[collections](https://docs.python.org/3.11/library/collections.html)：精度规则与常用容器。
- [排序指南](https://docs.python.org/3.11/howto/sorting.html)：比较键、原地排序与稳定性。
- [contextlib](https://docs.python.org/3.11/library/contextlib.html)、[functools](https://docs.python.org/3.11/library/functools.html)、[typing](https://docs.python.org/3.11/library/typing.html)：进阶语言工具。
- [unittest](https://docs.python.org/3.11/library/unittest.html)：测试发现、断言与运行结果。
- [环境与依赖](https://docs.python.org/3.11/tutorial/venv.html)、[PEP 8](https://peps.python.org/pep-0008/)：依赖隔离、风格与项目可读性。

查阅日期：2026-10-20。以上链接提供事实依据与延伸阅读，离线包没有复制整套外部文档。
