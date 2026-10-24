param(
  [string]$OutputDirectory = (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'windows'),
  [string]$WorkDirectory = (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'work\windows-build'),
  [switch]$SkipDownload
)
$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path $PSScriptRoot -Parent
$outputRoot = [IO.Path]::GetFullPath($OutputDirectory)
$buildWork = [IO.Path]::GetFullPath($WorkDirectory)
New-Item -ItemType Directory -Force -Path $outputRoot,$buildWork | Out-Null
$downloads = Join-Path $buildWork 'downloads'
New-Item -ItemType Directory -Force -Path $downloads | Out-Null
$dependencies = @(
  @{Name='python.zip'; Uri='https://www.python.org/ftp/python/3.13.16/python-3.13.16-embed-amd64.zip'; Hash='97dae5274cc54867065e8d5a3226e48c35017ed332a0fdb0e27d5b5821961297'},
  @{Name='webview2.zip'; Uri='https://api.nuget.org/v3-flatcontainer/microsoft.web.webview2/1.0.4191.47/microsoft.web.webview2.1.0.4191.47.nupkg'; Hash='f492bbf547d0da329553b6727435b677579b1e9f91cc9e4a1ad029366d5f23d0'},
  @{Name='MicrosoftEdgeWebView2RuntimeInstallerX64.exe'; Uri='https://msedge.sf.dl.delivery.mp.microsoft.com/filestreamingservice/files/35871e19-d11b-432d-9d1e-7be0ff286540/MicrosoftEdgeWebView2RuntimeInstallerX64.exe'; Hash='0625fb5c1e75be58a164e14f95aa58a3e5badb859b3d17c952385f3e4a9ff3e8'}
)
foreach ($dependency in $dependencies) {
  $archive = Join-Path $downloads $dependency.Name
  if (!(Test-Path -LiteralPath $archive)) {
    if ($SkipDownload) { throw "Missing dependency: $archive" }
    Invoke-WebRequest -Uri $dependency.Uri -OutFile $archive
  }
  if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $dependency.Hash) { throw "Dependency hash mismatch: $archive" }
}
$pythonDir = Join-Path $buildWork 'python'
$webviewDir = Join-Path $buildWork 'webview2'
Expand-Archive -LiteralPath (Join-Path $downloads 'python.zip') -DestinationPath $pythonDir -Force
Expand-Archive -LiteralPath (Join-Path $downloads 'webview2.zip') -DestinationPath $webviewDir -Force
$package = Join-Path $outputRoot 'PySlate'
$packageMarker = Join-Path $package '.pyslate-build-output'
if (Test-Path -LiteralPath $package) {
  $resolvedPackage = [IO.Path]::GetFullPath($package)
  if (!$resolvedPackage.StartsWith($outputRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetFileName($resolvedPackage) -ne 'PySlate') { throw 'Unsafe package clean path' }
  $recognized = (Test-Path -LiteralPath (Join-Path $package 'PySlate.exe')) -or ((Test-Path -LiteralPath $packageMarker) -and ((Get-Content -LiteralPath $packageMarker -Raw).Trim() -eq 'PySlate generated package'))
  if (!$recognized) { throw 'Refusing to clean an unrecognized output folder' }
  Remove-Item -LiteralPath $resolvedPackage -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $package | Out-Null
'PySlate generated package' | Set-Content -LiteralPath $packageMarker -Encoding ascii
Copy-Item -LiteralPath $pythonDir -Destination (Join-Path $package 'python') -Recurse
foreach ($folder in @('runtime','web','course')) {
  Copy-Item -LiteralPath (Join-Path $sourceRoot $folder) -Destination (Join-Path $package $folder) -Recurse
}
$packageDocs = Join-Path $package 'docs'
New-Item -ItemType Directory -Force -Path $packageDocs | Out-Null
$userDocs = Join-Path $sourceRoot 'docs'
if (Test-Path -LiteralPath $userDocs) {
  Get-ChildItem -LiteralPath $userDocs -File | Where-Object { $_.Name -in @('USER_GUIDE.md','WINDOWS_GUIDE.md','ANDROID_GUIDE.md') -and $_.Name -notlike 'RELEASE_REPORT*.md' } | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $packageDocs -Force }
}
if (Test-Path -LiteralPath (Join-Path $sourceRoot 'docs')) {
  $developerDocs = Join-Path $packageDocs 'developer'
  New-Item -ItemType Directory -Force -Path $developerDocs | Out-Null
  Get-ChildItem -LiteralPath (Join-Path $sourceRoot 'docs') -File | Where-Object { $_.Name -notlike 'RELEASE_REPORT*.md' } | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $developerDocs -Force }
}
@'
PySlate 0.3.0 - Windows x64

Open PySlate.exe. Keep all files and subfolders together.
CPython 3.13.16 is included; no separate Python installation is needed.

Chinese user guide: docs/WINDOWS_GUIDE.md
Technical notes: docs/developer/WINDOWS_ARCHITECTURE.md
Microsoft and Python terms: licenses/
If WebView2 is missing, use the bundled setup EXE or the full offline
runtime installer in redist/. Read and accept its Microsoft license first.

Projects and learning records: %LOCALAPPDATA%/PySlate/Data
Uninstalling the application preserves this independent data folder.
Python programs run with your Windows account permissions. Run trusted
code only; process limits do not provide a filesystem security sandbox.
'@ | Set-Content -LiteralPath (Join-Path $package 'README.txt') -Encoding utf8
foreach ($cache in @(Get-ChildItem -LiteralPath $package -Directory -Filter '__pycache__' -Recurse)) {
  $cachePath = [IO.Path]::GetFullPath($cache.FullName)
  if (!$cachePath.StartsWith($package + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetFileName($cachePath) -ne '__pycache__') { throw 'Unsafe generated cache path' }
  Remove-Item -LiteralPath $cachePath -Recurse -Force
}
$licenseDir = Join-Path $package 'licenses'
New-Item -ItemType Directory -Force -Path $licenseDir | Out-Null
$deliveryLicenses = Join-Path $sourceRoot 'licenses'
if (!(Test-Path -LiteralPath $deliveryLicenses)) { $deliveryLicenses = Join-Path $PSScriptRoot 'third-party' }
if (Test-Path -LiteralPath $deliveryLicenses) { Copy-Item -Path (Join-Path $deliveryLicenses '*') -Destination $licenseDir -Recurse -Force }
Copy-Item -LiteralPath (Join-Path $pythonDir 'LICENSE.txt') -Destination (Join-Path $licenseDir 'Python-LICENSE.txt') -Force
Copy-Item -LiteralPath (Join-Path $webviewDir 'LICENSE.txt') -Destination (Join-Path $licenseDir 'WebView2-LICENSE.txt') -Force
Copy-Item -LiteralPath (Join-Path $webviewDir 'NOTICE.txt') -Destination (Join-Path $licenseDir 'WebView2-NOTICE.txt') -Force
$redist = Join-Path $package 'redist'
New-Item -ItemType Directory -Force -Path $redist | Out-Null
Copy-Item -LiteralPath (Join-Path $downloads 'MicrosoftEdgeWebView2RuntimeInstallerX64.exe') -Destination $redist
Copy-Item -LiteralPath (Join-Path $webviewDir 'lib\net462\Microsoft.Web.WebView2.Core.dll'),(Join-Path $webviewDir 'lib\net462\Microsoft.Web.WebView2.WinForms.dll'),(Join-Path $webviewDir 'runtimes\win-x64\native\WebView2Loader.dll') -Destination $package -Force
$csc = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (!(Test-Path -LiteralPath $csc)) { throw '.NET Framework C# compiler is required (Windows .NET Framework 4.8).' }
$common = @('/nologo','/target:winexe','/platform:x64','/utf8output',('/win32manifest:' + (Join-Path $PSScriptRoot 'app.manifest')))
if (!(Test-Path -LiteralPath (Join-Path $PSScriptRoot 'PySlate.ico'))) { & (Join-Path $PSScriptRoot 'make-icon.ps1') }
$common += ('/win32icon:' + (Join-Path $PSScriptRoot 'PySlate.ico'))
$assemblyInfo = Join-Path $PSScriptRoot 'AssemblyInfo.cs'
& $csc @common ('/out:' + (Join-Path $package 'PySlate.exe')) /r:System.Windows.Forms.dll /r:System.Drawing.dll /r:System.Web.Extensions.dll ('/r:' + (Join-Path $package 'Microsoft.Web.WebView2.Core.dll')) ('/r:' + (Join-Path $package 'Microsoft.Web.WebView2.WinForms.dll')) (Join-Path $PSScriptRoot 'PySlate.cs') $assemblyInfo
if ($LASTEXITCODE -ne 0) { throw 'Host compilation failed' }
& $csc @common ('/out:' + (Join-Path $package 'Uninstall.exe')) /r:System.Windows.Forms.dll /r:System.Core.dll /r:Microsoft.CSharp.dll (Join-Path $PSScriptRoot 'Uninstall.cs') $assemblyInfo
if ($LASTEXITCODE -ne 0) { throw 'Uninstaller compilation failed' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'PySlate.exe.config') -Destination $package
'PySlate 0.3.0 | CPython 3.13.16 x64 | WebView2 SDK 1.0.4191.47' | Set-Content -LiteralPath (Join-Path $package 'VERSION.txt') -Encoding utf8
$sourceHashes = @()
foreach ($folder in @('windows','runtime','web','course','docs')) {
  $sourceHashes += Get-ChildItem -LiteralPath (Join-Path $sourceRoot $folder) -Recurse -File | Where-Object { $_.FullName -notmatch '[\\/]__pycache__[\\/]' } | ForEach-Object {
    @{path=$_.FullName.Substring($sourceRoot.Length + 1).Replace('\','/'); sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
  }
}
$packageHashes = @(Get-ChildItem -LiteralPath $package -Recurse -File | ForEach-Object {
  @{path=$_.FullName.Substring($package.Length + 1).Replace('\','/'); sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
})
@{version='0.3.0'; python='3.13.16'; platform='windows-x64'; builtAtUtc=[DateTimeOffset]::UtcNow.ToString('o'); dependencies=$dependencies; sources=$sourceHashes; files=$packageHashes} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $package 'BUILD-MANIFEST.json') -Encoding utf8
$payload = Join-Path $buildWork ('payload-' + [Guid]::NewGuid().ToString('N') + '.zip')
Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::CreateFromDirectory($package, $payload, [IO.Compression.CompressionLevel]::Optimal, $false)
$installer = Join-Path $outputRoot 'PySlate-0.3.0-windows-x64-setup.exe'
& $csc @common ('/out:' + $installer) ('/resource:' + $payload + ',PySlate.payload.zip') ('/resource:' + (Join-Path $deliveryLicenses 'WebView2-Runtime-LICENSE.txt') + ',PySlate.WebView2License.txt') /r:System.Windows.Forms.dll /r:System.Drawing.dll /r:System.Core.dll /r:System.IO.Compression.dll /r:System.IO.Compression.FileSystem.dll /r:Microsoft.CSharp.dll (Join-Path $PSScriptRoot 'Installer.cs') $assemblyInfo
if ($LASTEXITCODE -ne 0) { throw 'Installer compilation failed' }
$portable = Join-Path $outputRoot 'PySlate-0.3.0-windows-x64-portable.zip'
Copy-Item -LiteralPath $payload -Destination $portable -Force
Get-FileHash -LiteralPath $installer,$portable -Algorithm SHA256 | ForEach-Object { "$($_.Hash.ToLowerInvariant())  $([IO.Path]::GetFileName($_.Path))" } | Set-Content -LiteralPath (Join-Path $outputRoot 'SHA256SUMS.txt') -Encoding ascii
Write-Output "Built $installer"
Write-Output "Built $portable"
