# Android 构建、执行与数据说明

> 源码快照说明：安装包、测试报告、截图、PNG 原稿、交付校验清单及完整历史归档属于原始交付资料，未随本仓库提供。相关路径仅用于标识历史文件；本文保留的测试结果是原交付记录，不表示本次发布重新执行。当前可编辑源码位于仓库根目录。

应用包名 `org.pyslate.app`，版本0.3.0，最低 Android8.0 / API26。APK包含 arm64-v8a 与 x86_64 的真实 CPython3.14。设备自带的系统 WebView 需要支持现代 JavaScript；推荐更新系统 WebView。应用界面、课程、CodeMirror编辑器与本地配图均打包到 assets，不请求外部CDN。

## 构建

使用 JDK17或兼容版本、Gradle8.11.1、Android SDK35和build-tools35.0.0；本次实际使用JDK23.0.2构建。Chaquopy17.1.0与Android Gradle Plugin8.9.2从官方Maven仓库解析。构建机需Python3.14（major/minor与Android解释器一致）。

```powershell
./build.ps1 -AndroidSdk C:/Android/sdk -Gradle C:/tools/gradle-8.11.1/bin/gradle.bat -BuildPython C:/Python314/python.exe -WithDeviceTests
```

在 `android/` 执行，脚本仅生成本地SDK定位文件、使用当前进程环境。前端资产由 `syncSharedAssets` 从仓库根目录的 `web/`、`course/` 与 `licenses/` 同步；不要手动编辑生成的 assets。应用APK位于 `app/build/outputs/apk/debug/app-debug.apk`，设备测试APK位于 `app/build/outputs/apk/androidTest/debug/`。原交付曾将用户发行包另存并记录 SHA256；本仓库只包含构建源码。

首次构建会下载Gradle/Maven/Python运行时组件；安装后的App执行课程不需要下载Python或连接服务器。当前交付采用开发签名，不能冒称应用商店正式签名发行。后续公开发行应建立稳定私有签名钥匙与版本升级流程，不把密钥提交到源代码。

## 运行服务

界面通过 `PySlateNative.call` 访问主进程。文件操作在WebView bridge线程完成，Python在独立`:runner`进程中的后台线程执行。每次运行后整个worker退出，下一次重新创建。Messenger承载输入/输出/退出事件；Python stdin为可等待输入行的真实流，stdout/stderr内容来自解释器。输入框发送的行自动加换行；空行合法，输入首尾空格原样保留；原生桥支持EOF。默认累计执行预算30秒，在真实stdin读取等待期间暂停计时，每次输入最多等待5分钟；达到任一预算由主进程终止worker并给出结束原因。输出最多256KiB、事件最多4096项。单行输入限制64KiB，每次读取只接受一条匹配请求的提交，拒绝重复提交、过期请求与夹带换行的多行文本。输出小写入合并后再发往UI，避免Binder消息洪泛。

每个运行的输入请求编号从1递增。`input`事件包含`requestId`，`input_end`确认该次读取结束；`events`快照包含`waiting`、`inputRequestId`和单调递增的`stateRevision`，前端只在真实等待时启用输入。`read(0)`与`readline(0)`立即返回空串，部分读取保留剩余文本。软键盘出现时，原生容器根据IME与系统栏insets缩小WebView可用高度，使输入框和发送按钮保持可见。

实际项目目录设为 cwd，并加入sys.path，多文件import和项目相对路径有效。程序异常使用Python标准traceback。停止按钮与watchdog由主进程控制OS进程终止，遇到Python无限循环也能结束。终止不会回滚程序此前已经写入的文件。运行期间编辑器可以原子自动保存，重命名/删除文件需先停止运行。

Android系统返回键先调用前端导航：对话框先取消，课程返回学习目录，项目返回资料库，设置返回学习目录；根页面再询问退出。页面导航等待最后一次编辑保存，确认退出也等待 `pyslateFlush()` 完成后才关闭Activity。保存失败会保留页面并显示错误。切入后台时也会触发保存。

## 边界与数据

应用不申请 INTERNET、外部存储或“所有文件访问”权限。用户通过Android系统文档选择器导入和导出ZIP。项目、元数据、历史版本、回收站分别保存在应用私有 `files/pyslate/`，课程位于只读安装资源，升级通常保留私有数据。**卸载应用会删除私有数据**，卸载前请导出项目。

`:runner`与UI共享App UID。它有进程生命周期隔离，拥有访问本应用私有数据的能力；它不是抵御恶意Python代码的文件安全沙箱。只运行自己理解和信任的代码。Windows权限范围更大，应阅读Windows说明。Python黑名单不构成安全隔离。

文本编辑限制1MiB。ZIP压缩文件限制20MiB、展开上限100MiB、最多2000项，检查路径遍历、重复路径和异常压缩率。ZIP条目只写成普通文件，不创建Unix符号链接。主进程API不允许 `..`、绝对路径或反斜杠逃逸。Python程序自身仍受共享UID权限边界约束。

课程交互覆盖print/input、分支循环、函数、内置容器、模块/包、多文件与文件读写等标准Python语义。Android不提供桌面tkinter/turtle/curses，不能承诺任意pip二进制包、系统命令或常规multiprocessing；课程在相关章节标明平台范围。第三方包扩展需重新构建并逐项验证。

## 实测与复现

安装应用及测试APK后可执行：

```powershell
adb install -r app-debug.apk
adb install -r app-debug-androidTest.apk
adb shell am instrument -w org.pyslate.app.test/org.pyslate.app.SmokeInstrumentation
adb shell run-as org.pyslate.app cat files/android-smoke.json
```

全课程测试包需另用 `build.ps1 -CourseTests` 或 Gradle 参数 `-PpyslateTestRunner=org.pyslate.app.CourseInstrumentation assembleDebugAndroidTest` 构建。安装这个测试包后运行：

```powershell
adb shell am instrument -w org.pyslate.app.test/org.pyslate.app.CourseInstrumentation
adb shell run-as org.pyslate.app cat files/android-course.json
```

输入专项测试包使用 `-PpyslateTestRunner=org.pyslate.app.InputInstrumentation` 构建，运行同名Instrumentation并读取`files/android-input-v020.json`。其中短预算只通过包内测试构造器注入，正式界面始终使用30秒执行/300秒等待。课程v2验收直接遍历174个难度单元的完整`testCases`，不重复追加基线；顺序应用`replacements`，缺少匹配文字即失败，随后附加`assertions`并在真实Python中执行。报告记录打包课程SHA256；图注或配图变更后另比较全部执行字段，不能仅凭主题数量宣称代码一致。

设备smoke测试使用实际解释器、Binder与文件系统，覆盖交互input、双文件import、文件持久化、SyntaxError、循环函数、主动停止、输出限制、30秒超时、ZIP交换、目录逃逸/符号链接拒绝和状态重载。course模式逐个执行本地打包课程中的示例、答案与边界用例，输入按stdin供给，真实stdout逐字匹配expectedOutput。两者创建隐藏测试项目并移入回收站；不应在用户重要数据上运行内部验收包。具体执行结果与环境以 `test-reports/android*` 为准，构建成功本身不等于设备测试通过，模拟器通过也不等于真机通过。
