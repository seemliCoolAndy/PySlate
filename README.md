# PySlate

**A free, offline-first Python learning and coding environment for Windows and Android.**

PySlate combines a structured Chinese Python curriculum with a real code editor and local Python execution. It is designed for learners who want to study, experiment, and manage small multi-file projects without an account, cloud service, or runtime AI API.

- **Version:** 0.3.0 source snapshot
- **Platforms:** Windows x64 and Android 8.0+ (API 26+)
- **License:** MIT for PySlate code; third-party components retain their own licenses.

[简体中文](#简体中文) · [User guide](docs/USER_GUIDE.md) · [Windows build guide](docs/WINDOWS_GUIDE.md) · [Android build guide](docs/ANDROID.md)

> This is a source-only repository. Windows installers, portable packages, Android APKs, original PNG artwork masters, and detailed test-report archives are not included in this source snapshot. If release binaries are published, they will be listed on the repository's Releases page.

## Features

- **58 learning topics, three levels each:** 174 learning units from beginner to advanced.
- **Offline illustrations:** 174 locally bundled WebP teaching illustrations.
- **Real Python execution:** Windows uses bundled CPython 3.13.16; Android integrates CPython 3.14.8 through Chaquopy.
- **Code editing:** CodeMirror-based editor, syntax highlighting, examples, and reference answers.
- **Interactive input/output:** run code, provide input, view output and errors, and stop supported runs.
- **Project files:** manage standard Python files and multi-file projects; import/export projects as ZIP.
- **Local-first design:** no account, cloud server, or runtime AI API is required.
- **Shared interface:** HTML/CSS/JavaScript hosted by a Windows WebView2 shell and Android WebView.

## Security note

**PySlate is a learning tool, not a security sandbox.** Python programs run with the permissions available to the application/user. On Windows, code execution uses the current Windows user's permissions. On Android, the Python runner uses a separate process but shares the app UID; this is not an isolated security sandbox. Only run code you trust.

## Quick start: shared web UI

Requires Node.js and npm. From the repository root:

```bash
npm ci
npm run build:web
```

This rebuilds the bundled web editor dependencies. It does not by itself build the Windows application or Android APK. The checked-in `web/vendor.js` allows the existing UI bundle to be used without running npm at normal runtime.

## Build on Windows

See [Windows guide](docs/WINDOWS_GUIDE.md) and [Windows architecture notes](docs/WINDOWS_ARCHITECTURE.md).

Requirements include Windows x64, PowerShell, the .NET Framework 4.8 C# compiler, and network access for the first download of pinned official CPython/WebView2 build dependencies. From the repository root:

```powershell
.\windows\build.ps1
```

The script places managed build outputs outside the source tree by default. Read the script help and Windows guide before building, and use explicit output/work directories if needed.

## Build on Android

See [Android build guide](docs/ANDROID.md). The documented build environment uses JDK, Android SDK 35/build-tools 35.0.0, Gradle 8.11.1, and build-time Python 3.14. Replace the example SDK/Gradle/Python paths with paths that exist on your machine:

```powershell
.\android\build.ps1 -AndroidSdk C:/Android/sdk -Gradle C:/tools/gradle-8.11.1/bin/gradle.bat -BuildPython C:/Python314/python.exe
```

Add `-WithDeviceTests` only when a suitable test device or emulator is connected and configured. A successful build is not the same as a real-device compatibility test.

## Tests

Run the course examples with a compatible CPython interpreter:

```bash
python tools/test_course.py --report test-reports/course.json
```

For a targeted smoke test:

```bash
python tools/test_course.py --topic l01 --tier beginner --report test-reports/course-smoke.json
```

The test harness executes course code in temporary working directories. This is test-file isolation, **not** an operating-system security sandbox. Additional Windows, Android, UI, installer, and runtime tests are documented in `tools/` and the platform guides; some require their target operating system, build tools, or a device.

## Documentation

- [User guide](docs/USER_GUIDE.md)
- [Windows build and runtime architecture](docs/WINDOWS_ARCHITECTURE.md)
- [Android build and runtime](docs/ANDROID.md)
- [Bridge API](docs/BRIDGE.md)
- [Course structure](docs/COURSE.md)
- [Design notes](docs/DESIGN.md)
- [Open-source and dependency research](docs/OPEN_SOURCE_RESEARCH.md)
- [Image-generation provenance](docs/IMAGE_GENERATION.md)
- [Release report and validation boundaries](docs/RELEASE_REPORT.md)
- [Third-party notices](licenses/Android-Third-Party-NOTICES.md) and the other files under `licenses/`

## License

PySlate's own source code is licensed under the [MIT License](LICENSE). Third-party dependencies and bundled runtime components may have separate terms; see `licenses/` and `windows/third-party/`.

**MIT permits commercial use, redistribution, and modified forks**, subject to its notice requirements. This license does not require downstream forks to remain free or non-commercial. If you need a different policy, resolve the licensing choice before publishing the repository.

---

## 简体中文

PySlate 是一款面向 Windows 和 Android 的免费、离线优先 Python 学习与编程软件。它把中文 Python 课程、真实代码编辑器、本地 Python 执行环境和多文件项目管理整合在一起，无需账号、云服务器或运行时 AI API。

### 主要功能

- 58 个主题，每个主题分初级、中级、高级，共 174 个学习单元。
- 174 张离线教学 WebP 图片。
- Windows 使用随包 CPython 3.13.16；Android 通过 Chaquopy 集成 CPython 3.14.8。
- 支持代码编辑、运行、输入输出、错误查看及多文件项目管理。
- 支持 ZIP 项目导入与导出。
- Windows 使用 C# / WebView2 宿主；Android 使用 Java / WebView。

### 重要安全说明

PySlate **不是安全沙箱**。Windows 上运行的 Python 代码拥有当前 Windows 用户可用的权限；Android 运行服务虽然使用独立进程，但与应用共享 UID，并非隔离安全沙箱。只运行你信任的代码。

### 开源说明

本仓库包含源码及必要的离线 Web 资源，不包含 Windows 安装包、便携包、Android APK、原始 PNG 美术归档或完整测试报告归档。PySlate 自身源码采用 MIT 许可证，第三方依赖遵循各自许可。MIT 允许商业使用及再分发；如希望禁止衍生版本商业化，需要在发布前重新确定许可证策略。
