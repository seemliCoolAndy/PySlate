param(
    [string]$AndroidSdk = $env:ANDROID_SDK_ROOT,
    [string]$Gradle = 'gradle',
    [string]$BuildPython = '',
    [switch]$WithDeviceTests,
    [switch]$CourseTests
)
$ErrorActionPreference = 'Stop'
if (!$AndroidSdk -or !(Test-Path -LiteralPath $AndroidSdk)) { throw '请使用 -AndroidSdk 指定 Android SDK 路径。' }
$sdkPath = (Resolve-Path -LiteralPath $AndroidSdk).Path.Replace('\','/')
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'local.properties'), "sdk.dir=$sdkPath`n", [Text.UTF8Encoding]::new($false))
if ($BuildPython) { $env:PYSLATE_BUILD_PYTHON = $BuildPython }
$tasks = @('assembleDebug')
if ($WithDeviceTests -or $CourseTests) { $tasks += 'assembleDebugAndroidTest' }
if ($CourseTests) { $tasks += '-PpyslateTestRunner=org.pyslate.app.CourseInstrumentation' }
& $Gradle -p $PSScriptRoot @tasks
if ($LASTEXITCODE -ne 0) { throw "Gradle 构建失败：$LASTEXITCODE" }
Write-Host (Join-Path $PSScriptRoot 'app\build\outputs\apk\debug\app-debug.apk')
