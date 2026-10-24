"""Validate actual EXE setup/uninstall inside a workspace, without registration.

The --portable-test flag prevents Start Menu/Desktop/HKCU changes. The runtime
is already installed on this development host, so its missing-runtime branch
is inspected but deliberately not executed against this host's installation.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--installer", type=Path, required=True)
parser.add_argument("--report", type=Path, required=True)
args = parser.parse_args()
target = Path.cwd() / "work" / ("windows-install-" + str(time.time_ns()))
records = []

def record(name, condition, detail=None):
    records.append({"name": name, "passed": bool(condition), "detail": detail})
    print("PASS" if condition else "FAIL", name, flush=True)
    if not condition:
        raise AssertionError(name)

try:
    process = subprocess.run([str(args.installer.resolve()), "--silent", "--target", str(target), "--no-shortcuts", "--portable-test", "--accept-webview2-license", "--report", str(target.parent / "windows-installer-error.txt")], timeout=180)
    record("EXE installs actual payload and guides into workspace with no registration", process.returncode == 0 and (target / "PySlate.exe").is_file() and (target / "install-manifest.txt").is_file() and (target / "README.txt").is_file() and (target / "docs/WINDOWS_GUIDE.md").is_file() and (target / "docs/developer/WINDOWS_ARCHITECTURE.md").is_file(), str(target))
    runtime = target / "python/python.exe"
    env = dict(os.environ)
    env["PATH"] = os.environ.get("SystemRoot", "C:\\Windows") + "\\System32"
    version = subprocess.check_output([str(runtime), "-c", "import sys;print(sys.version.split()[0])"], env=env, text=True, timeout=10).strip()
    record("installed runtime runs with all system Python paths removed", version == "3.13.16", version)
    record("full offline WebView2 redistributable included", (target / "redist/MicrosoftEdgeWebView2RuntimeInstallerX64.exe").stat().st_size == 214156024)
    record("Microsoft runtime license included", (target / "licenses/WebView2-Runtime-LICENSE.txt").is_file())
    data = target.parent / (target.name + "-data")
    server = subprocess.Popen([str(runtime), "-u", str(target / "runtime/server.py"), "--root", str(target), "--data", str(data)], stdout=subprocess.PIPE, text=True)
    try:
        url = json.loads(server.stdout.readline())["url"]
        api = url.rsplit("/", 1)[0] + "/api"
        request = urllib.request.Request(api, b'{"action":"bootstrap"}', {"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=10) as response:
            bootstrap = json.load(response)
        record("installed offline course and Python bridge load", bootstrap["python"] == "3.13.16" and len(bootstrap["course"].get("chapters", [])) > 0)
    finally:
        server.kill()
        server.wait(timeout=10)
    (target / "my-unlisted-note.txt").write_text("preserve this user file", "utf-8")
    (data / "keep-project-data.txt").write_text("user project data", "utf-8")
    subprocess.run([str(target / "Uninstall.exe"), "--silent", "--portable-test"], timeout=15)
    began = time.monotonic()
    while (target / "install-manifest.txt").exists() and time.monotonic() - began < 30:
        time.sleep(0.1)
    record("uninstaller removes only manifest-listed application files", not (target / "PySlate.exe").exists() and not (target / "install-manifest.txt").exists() and (target / "my-unlisted-note.txt").exists())
    record("uninstaller preserves independent project data", (data / "keep-project-data.txt").read_text("utf-8") == "user project data")
finally:
    report = {"installer": str(args.installer.resolve()), "testDirectory": str(target), "results": records, "passed": sum(r["passed"] for r in records), "failed": sum(not r["passed"] for r in records),
              "unexecuted": ["Clean OS without WebView2: physical/VM image not available; existing shared runtime was not removed.", "Normal-user shortcut and registry registration branch was not executed to avoid modifying the developer's environment."]}
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), "utf-8")
