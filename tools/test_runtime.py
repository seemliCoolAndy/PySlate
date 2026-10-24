"""Black-box acceptance tests against the DISTRIBUTED embedded CPython runtime.

Usage: python test_runtime.py --package outputs/windows/PySlate --report ...json
All test data is confined to a temporary workspace, never the user's library.
"""
import argparse
import base64
import io
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.error
import urllib.request
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument("--package", type=Path, required=True)
parser.add_argument("--report", type=Path, required=True)
parser.add_argument("--runtime-source", type=Path, help="Use updated runtime sources with the distributed embedded Python; do not rebuild release files")
args = parser.parse_args()
package = args.package.resolve()
runtime_source = (args.runtime_source or package / "runtime").resolve()
workspace = Path(tempfile.mkdtemp(prefix="pyslate-runtime-", dir=Path.cwd() / "work"))
data = workspace / "Data"
results = []
backend = None

def start():
    global backend, api_url, page_url
    backend = subprocess.Popen([str(package / "python/python.exe"), "-u", "-X", "utf8", str(runtime_source / "server.py"), "--root", str(package), "--data", str(data)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    line = backend.stdout.readline()
    if not line:
        raise RuntimeError("Backend failed: " + backend.stderr.read())
    ready = json.loads(line)
    page_url = ready["url"]
    api_url = page_url.rsplit("/", 1)[0] + "/api"

def call(action, **values):
    request = urllib.request.Request(api_url, json.dumps({"action": action, **values}).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        result = json.load(error)
    if "error" in result:
        raise ValueError(result["error"])
    return result

def rejects(action, **values):
    try:
        call(action, **values)
    except (ValueError, urllib.error.HTTPError):
        return
    raise AssertionError("unsafe request was accepted: " + action)

def test(name, function):
    began = time.monotonic()
    try:
        detail = function()
        results.append({"name": name, "passed": True, "seconds": round(time.monotonic() - began, 3), "detail": detail})
        print("PASS", name, flush=True)
    except Exception:
        results.append({"name": name, "passed": False, "seconds": round(time.monotonic() - began, 3), "error": traceback.format_exc()})
        print("FAIL", name, traceback.format_exc(), flush=True)

def write(content, path="main.py", project=None):
    call("file.write", id=project or project_id, path=path, content=content)

def wait_run(run_id, timeout=8, input_text=None):
    began, cursor, events = time.monotonic(), 0, []
    sent = False
    while time.monotonic() - began < timeout:
        result = call("events", runId=run_id, cursor=cursor)
        cursor = result["cursor"]
        events.extend(result["events"])
        if input_text is not None and not sent and any(e["type"] == "input" for e in events):
            call("input", runId=run_id, text=input_text)
            sent = True
        if not result["running"]:
            return events
        time.sleep(0.04)
    call("stop", runId=run_id)
    raise AssertionError("Run timed out in test")

def run(content, timeout=8, input_text=None):
    write(content)
    run_id = call("run", id=project_id, entry="main.py")["runId"]
    events = wait_run(run_id, timeout, input_text)
    stdout = "".join(e["text"] for e in events if e["type"] == "stdout")
    stderr = "".join(e["text"] for e in events if e["type"] == "stderr")
    return stdout, stderr, events

def check(condition, message="assertion failed"):
    if not condition:
        raise AssertionError(message)

def zipped(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries:
            archive.writestr(name, content)
    return base64.b64encode(buffer.getvalue()).decode()

try:
    start()
    test("embedded Python version and offline course bootstrap", lambda: check(call("bootstrap")["python"] == "3.13.16" and bool(call("bootstrap")["course"])))
    def test_library_lock():
        second = subprocess.run([str(package / "python/python.exe"), "-u", "-X", "utf8", str(runtime_source / "server.py"), "--root", str(package), "--data", str(data)], capture_output=True, text=True, encoding="utf-8", timeout=5)
        check(second.returncode != 0 and "其他 PySlate 窗口" in second.stderr and not second.stdout)
    test("second server cannot concurrently overwrite the same library", test_library_lock)
    project_id = call("project.create", name="中文测试项目", color="#c0ffee", category="验收")["project"]["id"]
    test("trust acceptance required before executing", lambda: rejects("run", id=project_id))
    call("state.patch", patch={"trusted": True})
    test("real print, loops and functions", lambda: check(run("def twice(n):\n    return n*2\nprint([twice(i) for i in range(4)])\n")[0].strip() == "[0, 2, 4, 6]"))
    def test_input():
        stdout, stderr, events = run("name = input('你的名字：')\nprint('你好，' + name)\n", input_text="小明")
        check("你好，小明" in stdout and any(e["type"] == "input" for e in events) and not stderr, (stdout, stderr))
    test("interactive input prompt and UTF-8 stdin", test_input)
    def test_error():
        stdout, stderr, events = run("def broken(:\n    pass\n")
        check("SyntaxError" in stderr and "main.py" in stderr and events[-1]["code"] != 0)
    test("authentic Python syntax error traceback", test_error)
    def test_import():
        write("def greeting():\n    return '模块成功'\n", "模块.py")
        check(run("import 模块\nprint(模块.greeting())\n")[0].strip() == "模块成功")
    test("multiple files and Chinese module import", test_import)
    def test_nested_entry():
        write("answer = 42\n", "nested/helpers.py")
        write("import helpers\nprint(helpers.answer)\n", "nested/start.py")
        events = wait_run(call("run", id=project_id, entry="nested/start.py")["runId"])
        check("".join(e["text"] for e in events if e["type"] == "stdout").strip() == "42")
    test("nested entry imports sibling Python modules", test_nested_entry)
    def test_file_io():
        stdout, stderr, events = run("from pathlib import Path\np=Path('assets/数据.txt')\np.parent.mkdir(exist_ok=True)\np.write_text('本地文件', encoding='utf-8')\nprint(p.read_text(encoding='utf-8'))\n")
        check(stdout.strip() == "本地文件" and call("file.read", id=project_id, path="assets/数据.txt")["content"] == "本地文件")
    test("relative resource file reading and writing", test_file_io)
    def test_stop():
        write("while True:\n    pass\n")
        run_id = call("run", id=project_id)["runId"]
        began = time.monotonic()
        call("stop", runId=run_id)
        events = wait_run(run_id)
        check(time.monotonic() - began < 3 and events[-1]["code"] != 0)
    test("responsive HTTP and forced stop of infinite loop", test_stop)
    def test_input_queue():
        write("import time\ntime.sleep(100)\n")
        run_id = call("run", id=project_id)["runId"]
        began = time.monotonic()
        call("input", runId=run_id, text="x" * 65536)
        write("print('next run')\n")
        call("stop", runId=run_id)
        check(time.monotonic() - began < 3, "unread input blocked the HTTP bridge")
    test("unread large stdin and edits keep HTTP service responsive", test_input_queue)
    def test_timeout():
        stdout, stderr, events = run("import time\ntime.sleep(100)\n", timeout=35)
        check("30 秒" in stderr and events[-1]["code"] != 0)
    test("30 second execution timeout", test_timeout)
    def test_output():
        stdout, stderr, events = run("while True:\n    print('x'*4096)\n")
        check(len(stdout.encode()) <= 256 * 1024 and "256 KiB" in stderr and events[-1]["code"] != 0)
    test("output flood is bounded and terminated", test_output)
    def test_input_flood():
        stdout, stderr, events = run("import io, sys\nsys.stdin = io.StringIO('\\n' * 10000)\nfor _ in range(10000):\n    input()\n")
        check(sum(e["type"] == "input" for e in events) <= 256 and len(events) <= 260 and "256 次" in stderr)
    test("synthetic input event flood is bounded and terminated", test_input_flood)
    def test_tree():
        marker = workspace / "descendant-was-not-killed.txt"
        code = "import subprocess, sys, time\nsubprocess.Popen([sys.executable,'-c'," + repr("import time;time.sleep(3);open(" + repr(str(marker)) + ",'w').write('escaped')") + "])\nprint('child started',flush=True)\ntime.sleep(100)\n"
        write(code)
        run_id = call("run", id=project_id)["runId"]
        began = time.monotonic()
        while "child started" not in str(call("events", runId=run_id)) and time.monotonic() - began < 5:
            time.sleep(0.04)
        call("stop", runId=run_id)
        wait_run(run_id)
        time.sleep(3.2)
        check(not marker.exists(), "descendant escaped Job Object termination")
    test("Windows Job Object terminates descendants", test_tree)
    def test_versions():
        write("version 1", "notes.txt")
        write("version 2", "notes.txt")
        call("file.rename", id=project_id, path="notes.txt", newPath="资料/笔记.txt")
        check(call("file.read", id=project_id, path="资料/笔记.txt")["content"] == "version 2")
        call("file.delete", id=project_id, path="资料/笔记.txt")
        versions = list((data / "backups" / project_id).glob("*"))
        check(any(p.read_text("utf-8") == "version 1" for p in versions) and any(p.read_text("utf-8") == "version 2" for p in versions))
    test("atomic saves, rename and recoverable file versions", test_versions)
    def test_paths():
        for path in ("../escape.py", "/outside.py", "C:/outside.py", "a\\b.py", "CON.py", "COM¹.txt", "LPT².txt", "NUL .txt", "a.py:stream", "dir/../bad.py", "foo./x.py"):
            rejects("file.write", id=project_id, path=path, content="x")
    test("path traversal and Windows special-path rejection", test_paths)
    def test_archives():
        for entries in ([('../escape.py', 'x')], [('C:/evil.py', 'x')], [('a.py', 'x'), ('A.py', 'y')], [('a', 'x'), ('a/b.py', 'y')], [('bomb.txt', '0'*(2*1024*1024))]):
            rejects("project.import", filename="unsafe.zip", base64=zipped(entries))
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            info = zipfile.ZipInfo("link")
            info.create_system = 3
            info.external_attr = (0o120777 << 16)
            archive.writestr(info, "../outside")
        rejects("project.import", filename="symlink.zip", base64=base64.b64encode(buffer.getvalue()).decode())
    test("ZIP traversal, case collision, bomb and symlink rejection", test_archives)
    def test_exchange():
        write("print('迁移成功')\n")
        exported = call("project.export", id=project_id)
        imported = call("project.import", **exported)["project"]
        check(call("file.read", id=imported["id"], path="main.py")["content"] == "print('迁移成功')\n")
        duplicate = call("project.duplicate", id=imported["id"])["project"]
        call("project.delete", id=duplicate["id"])
        check(any((data / "trash").glob(duplicate["id"] + "-*")))
    test("standard ZIP exchange, duplicate and soft-deleted project", test_exchange)
    def test_http():
        for headers in ({"Origin": "https://evil.example"}, {"Host": "evil.example"}, {"Sec-Fetch-Site": "cross-site"}):
            request = urllib.request.Request(api_url, b'{"action":"bootstrap"}', {"Content-Type": "application/json", **headers})
            try:
                urllib.request.urlopen(request, timeout=5)
            except urllib.error.HTTPError as error:
                check(error.code == 400)
            else:
                raise AssertionError("cross origin request accepted")
        with urllib.request.urlopen(page_url, timeout=5) as response:
            check(response.headers["Referrer-Policy"] == "no-referrer" and response.headers["X-Content-Type-Options"] == "nosniff")
        try:
            urllib.request.urlopen(page_url.replace(api_url.split('/')[-2], 'wrong-token'), timeout=5)
        except urllib.error.HTTPError as error:
            check(error.code == 404)
        else:
            raise AssertionError("wrong token accepted")
    test("token capability, Host and Origin protection", test_http)
    def test_persistence():
        call("state.patch", patch={"progress": {"l01": True}, "drafts": {"l01": "print('保存')"}, "theme": "dark"})
        backend.kill()
        backend.wait()
        start()
        state = call("bootstrap")["state"]
        check(state["progress"]["l01"] and state["drafts"]["l01"] == "print('保存')" and state["theme"] == "dark")
        check(any(p["id"] == project_id for p in call("bootstrap")["projects"]))
    test("restart preserves projects, progress and lesson drafts", test_persistence)
    def test_corrupt_index_backup():
        backend.kill()
        backend.wait()
        primary = data / "catalog.json"
        previous = data / "catalog.previous.json"
        previous.write_bytes(primary.read_bytes())
        primary.write_text("{broken", "utf-8")
        start()
        check(any(p["id"] == project_id for p in call("bootstrap")["projects"]))
        try:
            primary.chmod(stat.S_IREAD)
            rejects("state.patch", patch={"theme": "light"})
            check(any(p["id"] == project_id for p in json.loads(previous.read_text("utf-8"))["projects"]))
        finally:
            primary.chmod(stat.S_IREAD | stat.S_IWRITE)
            backend.kill()
            backend.wait()
        start()
        check(any(p["id"] == project_id for p in call("bootstrap")["projects"]))
        call("state.patch", patch={"theme": "light"})
        check(json.loads(primary.read_text("utf-8"))["state"]["theme"] == "light")
    test("corrupt index recovery preserves last good backup after a failed save", test_corrupt_index_backup)
finally:
    if backend and backend.poll() is None:
        backend.kill()
        backend.wait(timeout=5)
    report = {"platform": "Windows x64", "runtime": "CPython 3.13.16 official embeddable", "package": str(package), "runtimeSource":str(runtime_source), "testData": str(workspace),
              "passed": sum(r["passed"] for r in results), "failed": sum(not r["passed"] for r in results), "results": results,
              "limitations": ["Job Object process management is not a filesystem/network security sandbox.", "No physical clean Windows installation was available; tests ran on the development Windows host."]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), "utf-8")
sys.exit(1 if report["failed"] else 0)
