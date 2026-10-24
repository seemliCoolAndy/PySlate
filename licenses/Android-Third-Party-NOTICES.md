# Android 原生运行时归属

PySlate Android使用Chaquopy17.1.0（MIT）与官方Maven目标包 `com.chaquo.python:target:3.14.8-0`，包含arm64-v8a和x86_64两个ABI。Chaquopy原文许可见 `Chaquopy-LICENSE.txt`；CPython核心许可见 `Python-3.14.8-LICENSE.txt`。交付同时保留Python官方发行版的完整 `Python-LICENSE.txt`，其中含随发行版第三方组件说明。

根据 [Chaquopy17.1.0构建脚本](https://github.com/chaquo/chaquopy/blob/17.1.0/target/python/build.sh)，Python3.13以上使用CPython官方Android构建脚本。实际Python3.14.8的 [Android/android.py](https://github.com/python/cpython/blob/v3.14.8/Android/android.py) 固定原生依赖如下：

| 组件 | 上游版本 | 许可 / 本地原文 |
|---|---|---|
| OpenSSL | 3.5.9 | Apache-2.0；`OpenSSL-3.5.9-LICENSE.txt` |
| libffi | 3.4.4 | MIT；`libffi-3.4.4-LICENSE.txt` |
| bzip2 | 1.0.8 | 宽松bzip2许可；`bzip2-1.0.8-LICENSE.txt` |
| SQLite | 3.53.4 | [核心public domain声明](https://www.sqlite.org/copyright.html) |
| liblzma / XZ | 5.4.6 | liblzma核心public domain；`xz-5.4.6-COPYING.txt`说明各组件边界。App没有打包XZ命令行脚本与工具。 |
| Zstandard | 1.5.7 | 采用BSD许可选项；`zstd-1.5.7-LICENSE.txt` |
| LLVM libc++ / libc++abi | Android工具链运行时代码 | Apache-2.0 with LLVM exception；`LLVM-libcxx-LICENSE.txt`、`LLVM-libcxxabi-LICENSE.txt` |

本说明依据所用上游构建脚本和实际解析的Maven版本，不声称完成逐符号来源取证或全面供应链/CVE审计。系统WebView由Android系统提供。Android SDK、模拟器、系统镜像、Gradle和JDK是开发测试工具，没有作为用户安装包的独立工具随包分发。

Web端组件的逐包许可证另见本目录对应子目录及 `npm-dependencies.json`。PySlate源码自身为MIT，保留的第三方组件遵循各自许可。
