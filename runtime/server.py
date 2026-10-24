"""Offline PySlate bridge. Only trusted local Python should be executed.

The HTTP bridge validates capability URL, Host, Origin, lengths and paths.
Windows Job Objects manage child lifetimes; they are NOT filesystem isolation.
"""
from __future__ import annotations
import argparse
import base64
import codecs
import copy
from contextlib import contextmanager
import ctypes
import hashlib
import io
import json
import mimetypes
import os
import queue
from pathlib import Path, PurePosixPath
import re
import secrets
import shutil
import stat
import subprocess
import sys
import threading
import time
import traceback
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

VERSION = "0.3.0"
TEXT_LIMIT = 1024 * 1024
ZIP_LIMIT = 20 * 1024 * 1024
EXPANDED_LIMIT = 50 * 1024 * 1024
OUTPUT_LIMIT = 256 * 1024
EVENT_LIMIT = 8192
INPUT_LIMIT = 256
RUN_TIMEOUT = 30
INPUT_WAIT_TIMEOUT = 300
RESERVED = re.compile(r"^(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])$", re.I)

def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or len(relative) > 240:
        raise ValueError("文件路径无效或过长")
    if "\\" in relative or relative.startswith("/") or "\x00" in relative:
        raise ValueError("只接受项目内相对路径")
    parts = relative.split("/")
    for part in parts:
        if not part or part in (".", "..") or part.endswith((" ", ".")) or RESERVED.fullmatch(part.split(".", 1)[0].rstrip(" .")):
            raise ValueError("文件名包含不允许的路径片段")
        if any(ord(c) < 32 or c in '<>:"|?*' for c in part):
            raise ValueError("文件名包含不兼容字符")
    root = Path(root).resolve()
    target = root.joinpath(*parts)
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink() or (current.exists() and getattr(current.stat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("不支持符号链接或重解析点")
    if not target.resolve().is_relative_to(root):
        raise ValueError("路径超出项目目录")
    return target

def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        # Windows antivirus/indexers may briefly open a target without delete
        # sharing. Keep the replacement atomic and retry the transient lock.
        for attempt in range(8):
            try:
                os.replace(temporary, path)
                break
            except PermissionError:
                if attempt == 7:
                    raise
                time.sleep(min(0.02 * (2 ** attempt), 0.25))
    finally:
        temporary.unlink(missing_ok=True)

def rename_directory(source, destination):
    for attempt in range(8):
        try:
            Path(source).rename(destination)
            return
        except PermissionError:
            if attempt == 7:
                raise ValueError("项目目录暂时被占用，已保留项目，请关闭占用程序后重试")
            time.sleep(min(0.02 * (2 ** attempt), 0.25))

def label(value, fallback="新项目"):
    value = str(value or fallback).strip()
    if not value or len(value) > 100 or any(ord(c) < 32 for c in value):
        raise ValueError("名称须为 1–100 个可见字符")
    return value

def validate_catalog(value):
    if not isinstance(value, dict) or not isinstance(value.get("state"), dict) or not isinstance(value.get("projects"), list) or not isinstance(value.get("categories"), list):
        raise ValueError("项目索引结构无效")
    seen = set()
    for project in value["projects"]:
        if not isinstance(project, dict) or not re.fullmatch(r"[0-9a-f]{32}", str(project.get("id", ""))) or not isinstance(project.get("name"), str) or project["id"] in seen:
            raise ValueError("项目索引条目无效")
        seen.add(project["id"])
    if not all(isinstance(category, str) for category in value["categories"]):
        raise ValueError("分类索引无效")
    return value

class DataLock:
    """One server per data directory, preventing last-writer-wins catalog loss."""
    def __init__(self, directory):
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.file = (Path(directory) / "pyslate.lock").open("a+b")
        if self.file.tell() == 0:
            self.file.write(b"\0")
            self.file.flush()
        self.file.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.file.close()
            raise RuntimeError("此资料库已在其他 PySlate 窗口中打开，请返回现有窗口；若窗口已关闭，请稍后重试")

    def close(self):
        if self.file.closed:
            return
        self.file.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
        self.file.close()

class WindowsJob:
    """Kill-on-close process tree with a 512 MiB aggregate committed-memory cap."""
    def __init__(self, process):
        self.handle = None
        if os.name != "nt":
            return
        from ctypes import wintypes as w
        class BASIC(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", w.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", w.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", w.DWORD), ("SchedulingClass", w.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount", "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]
        class EXTENDED(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", BASIC), ("IoInfo", IO), ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
        kernel.CreateJobObjectW.restype = w.HANDLE
        kernel.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
        kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        kernel.TerminateJobObject.argtypes = [w.HANDLE, w.UINT]
        kernel.CloseHandle.argtypes = [w.HANDLE]
        handle = kernel.CreateJobObjectW(None, None)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = EXTENDED()
        limits.BasicLimitInformation.LimitFlags = 0x2000 | 0x200 | 0x8
        limits.BasicLimitInformation.ActiveProcessLimit = 16
        limits.JobMemoryLimit = 512 * 1024 * 1024
        if not kernel.SetInformationJobObject(handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)) or not kernel.AssignProcessToJobObject(handle, int(process._handle)):
            error = ctypes.get_last_error()
            kernel.CloseHandle(handle)
            raise ctypes.WinError(error)
        self.handle, self.kernel = handle, kernel

    def terminate(self):
        if self.handle:
            self.kernel.TerminateJobObject(self.handle, 137)

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None

class Run:
    def __init__(self, executable, worker, directory, entry, timeout=RUN_TIMEOUT, input_timeout=INPUT_WAIT_TIMEOUT):
        self.id = uuid.uuid4().hex
        self.events = []
        self.lock = threading.RLock()
        self.bytes = 0
        self.input_count = 0
        self.running = True
        self.done = threading.Event()
        self.reason = None
        self.waiting = False
        self.input_request_id = None
        self.input_submitted = False
        self.stdin_closed = False
        self.state_revision = 0
        self.active_seconds = 0.0
        self.accounted_at = time.monotonic()
        self.wait_started = None
        self.timeout = float(timeout)
        self.input_timeout = float(input_timeout)
        if self.timeout <= 0 or self.input_timeout <= 0:
            raise ValueError("运行与输入等待预算必须大于零")
        self.marker = "\x1ePYSLATE_" + secrets.token_hex(16) + "\x1f"
        handshake = secrets.token_hex(16)
        environment = {k: v for k, v in os.environ.items() if not k.upper().startswith("PYTHON")}
        environment.update(PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        self.process = subprocess.Popen([str(executable), "-u", "-X", "utf8", str(worker), str(entry), self.marker, handshake, "input-v2"], cwd=directory,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            self.job = WindowsJob(self.process)
        except Exception:
            self.process.kill()
            self.process.wait()
            raise RuntimeError("无法建立 Windows 进程组，已取消执行")
        self.readers = [threading.Thread(target=self.read, args=(stream, kind), daemon=True)
                        for stream, kind in ((self.process.stdout, "stdout"), (self.process.stderr, "stderr"))]
        for thread in self.readers:
            thread.start()
        self.process.stdin.write((handshake + "\n").encode())
        self.process.stdin.flush()
        self.input_queue = queue.Queue(maxsize=8)
        threading.Thread(target=self.write_input, daemon=True).start()
        threading.Thread(target=self.monitor, daemon=True).start()

    def write_input(self):
        while self.running:
            try:
                value = self.input_queue.get(timeout=0.25)
            except queue.Empty:
                continue
            try:
                if value is None:
                    self.process.stdin.close()
                    return
                self.process.stdin.write(value)
                self.process.stdin.flush()
            except (OSError, ValueError):
                return

    def _account_locked(self, now=None):
        now = time.monotonic() if now is None else now
        if not self.waiting:
            self.active_seconds += now - self.accounted_at
        self.accounted_at = now

    def _state_locked(self):
        alive = self.running and not self.reason and self.process.poll() is None
        waiting = bool(alive and self.waiting and not self.input_submitted)
        return {"runId": self.id, "waiting": waiting,
                "inputRequestId": self.input_request_id if waiting else None,
                "stateRevision": self.state_revision}

    def _finish_input_locked(self, cancelled=False):
        if self.waiting:
            request_id = self.input_request_id
            self._account_locked()
            self.waiting = False
            self.wait_started = None
            self.input_request_id = None
            self.input_submitted = False
            self.state_revision += 1
            self.emit("input_end", requestId=request_id, cancelled=cancelled, force=True)

    def send_input(self, text=None, request_id=None):
        with self.lock:
            if not self.running or self.reason or self.process.poll() is not None:
                raise ValueError("程序已结束")
            if self.stdin_closed:
                raise ValueError("标准输入已关闭")
            if request_id is not None:
                if type(request_id) is not int or request_id <= 0:
                    raise ValueError("输入请求编号无效")
                if not self.waiting or request_id != self.input_request_id:
                    raise ValueError("输入请求已变化，请等待当前输入提示")
                if text is not None and ("\n" in text or "\r" in text):
                    raise ValueError("每次只提交一行输入")
            if self.waiting and self.input_submitted:
                raise ValueError("这次输入已提交，请等待程序继续")
            accepted_id = self.input_request_id if self.waiting else None
            try:
                self.input_queue.put_nowait(None if text is None else (text + "\n").encode("utf-8"))
            except queue.Full:
                raise ValueError("输入等待队列已满，请等待程序读取后再发送")
            if self.waiting:
                # The worker keeps its execution budget paused until read() has
                # actually consumed the line; the UI no longer needs a reply.
                self.input_submitted = True
            if text is None:
                self.stdin_closed = True
            self.state_revision += 1
            return {"ok": True, "acceptedRequestId": accepted_id, **self._state_locked()}

    def emit(self, kind, text="", code=None, force=False, **fields):
        with self.lock:
            if len(self.events) >= EVENT_LIMIT and not force:
                self.stop("运行事件超过 8192 条，程序已终止。")
                return
            event = {"seq": len(self.events) + 1, "type": kind, "text": text}
            if code is not None:
                event["code"] = code
            event.update(fields)
            self.events.append(event)

    def output(self, kind, text):
        if not text:
            return
        with self.lock:
            available = OUTPUT_LIMIT - self.bytes
            raw = text.encode("utf-8")
            if available > 0:
                shown = raw[:available].decode("utf-8", "ignore")
                self.bytes += len(shown.encode("utf-8"))
                self.emit(kind, shown)
            if len(raw) > available and not self.reason:
                self.reason = "输出超过 256 KiB，程序已终止。"
                self.job.terminate()
                if self.process.poll() is None:
                    self.process.kill()

    def input_frame(self, frame):
        if not isinstance(frame, dict) or type(frame.get("requestId")) is not int or frame["requestId"] <= 0:
            return False
        kind, request_id = frame.get("type"), frame["requestId"]
        if kind not in ("input", "input_end"):
            return False
        with self.lock:
            if kind == "input":
                if type(frame.get("waiting")) is not bool:
                    return False
                self.input_count += 1
                if self.input_count > INPUT_LIMIT:
                    self.stop("输入请求超过 256 次，程序已终止。")
                elif frame["waiting"] and self.running and not self.reason and self.process.poll() is None:
                    if self.waiting:
                        self.stop("输入协议出现重叠请求，程序已终止。")
                    else:
                        self._account_locked()
                        self.waiting = True
                        self.wait_started = time.monotonic()
                        self.input_request_id = request_id
                        self.input_submitted = False
                        self.state_revision += 1
                        self.emit("input", requestId=request_id)
            elif self.waiting and request_id == self.input_request_id:
                self._finish_input_locked()
        return True

    def read(self, stream, kind):
        decoder = codecs.getincrementaldecoder("utf-8")("replace")
        pending = ""
        try:
            while chunk := os.read(stream.fileno(), 4096):
                text = decoder.decode(chunk)
                if kind != "stderr":
                    self.output(kind, text)
                    continue
                pending += text
                while pending:
                    start = pending.find(self.marker)
                    if start < 0:
                        keep = 0
                        for length in range(min(len(self.marker) - 1, len(pending)), 0, -1):
                            if pending.endswith(self.marker[:length]):
                                keep = length
                                break
                        self.output(kind, pending[:-keep] if keep else pending)
                        pending = pending[-keep:] if keep else ""
                        break
                    self.output(kind, pending[:start])
                    pending = pending[start:]
                    end = pending.find("\n", len(self.marker))
                    if end < 0:
                        if len(pending) <= len(self.marker) + 512:
                            break  # Control frame or its newline may span reads.
                        self.output(kind, pending[:len(self.marker)])
                        pending = pending[len(self.marker):]
                        continue
                    raw, pending = pending[:end + 1], pending[end + 1:]
                    try:
                        frame = json.loads(raw[len(self.marker):].strip())
                    except (ValueError, TypeError):
                        self.output(kind, raw)
                    else:
                        if not self.input_frame(frame):
                            self.output(kind, raw)
            self.output(kind, pending + decoder.decode(b"", final=True))
        finally:
            stream.close()

    def monitor(self):
        code = None
        while code is None:
            reason = None
            with self.lock:
                now = time.monotonic()
                self._account_locked(now)
                if not self.reason:
                    if self.waiting and now - self.wait_started >= self.input_timeout:
                        duration = (f"{self.input_timeout / 60:g} 分钟" if self.input_timeout >= 60
                                    else f"{self.input_timeout:g} 秒")
                        reason = "等待输入超过 " + duration + "，程序已终止。"
                    elif not self.waiting and self.active_seconds >= self.timeout:
                        reason = f"累计执行超过 {self.timeout:g} 秒，程序已终止。"
            if reason:
                self.stop(reason)
            try:
                code = self.process.wait(timeout=0.05)
            except subprocess.TimeoutExpired:
                pass
        self.job.close()  # Also kill descendants when the entry program exits.
        for reader in self.readers:
            reader.join(timeout=3)
        with self.lock:
            self._finish_input_locked(cancelled=True)
            if self.reason:
                self.emit("stderr", "\n" + self.reason + "\n", force=True)
            self.running = False
            self.state_revision += 1
            self.emit("exit", code=code, force=True)
            self.done.set()
        try:
            self.process.stdin.close()
        except (OSError, ValueError):
            pass

    def stop(self, reason="用户已停止程序。"):
        with self.lock:
            if self.running:
                self.reason = self.reason or reason
                self._finish_input_locked(cancelled=True)
                self.state_revision += 1
                self.job.terminate()
                if self.process.poll() is None:
                    self.process.kill()

    def poll(self, cursor):
        with self.lock:
            return {"events": [e for e in self.events if e["seq"] > cursor], "cursor": len(self.events), "running": self.running,
                    **self._state_locked()}

class Store:
    def __init__(self, root, data, executable=None):
        self.root, self.data = Path(root).resolve(), Path(data).resolve()
        self.projects_dir, self.trash, self.backups = [self.data / p for p in ("projects", "trash", "backups")]
        for path in (self.projects_dir, self.trash, self.backups):
            path.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.catalog_file = self.data / "catalog.json"
        default = {"state": {"theme": "light", "progress": {}, "drafts": {}, "lastLesson": "l01", "split": 0.5, "trusted": False}, "projects": [], "categories": ["未分类"]}
        if self.catalog_file.exists():
            try:
                self.catalog = validate_catalog(json.loads(self.catalog_file.read_text("utf-8")))
            except (OSError, ValueError):
                backup = self.data / "catalog.previous.json"
                if not backup.exists():
                    raise RuntimeError("项目索引损坏；原文件已保留，请从备份恢复")
                try:
                    self.catalog = validate_catalog(json.loads(backup.read_text("utf-8")))
                except (OSError, ValueError):
                    raise RuntimeError("项目索引与备份均损坏；原文件和项目目录已保留，请手动恢复")
        else:
            self.catalog = default
            self.save()
        self.executable = Path(executable or sys.executable)
        self.runs = {}

    def save(self):
        if self.catalog_file.exists():
            previous = self.catalog_file.read_bytes()
            try:
                validate_catalog(json.loads(previous.decode("utf-8")))
            except (ValueError, UnicodeError):
                pass  # Never replace the last good backup with a known corrupt index.
            else:
                atomic_write(self.data / "catalog.previous.json", previous)
        validate_catalog(self.catalog)
        atomic_write(self.catalog_file, json.dumps(self.catalog, ensure_ascii=False, indent=2).encode("utf-8"))

    def project(self, project_id):
        for project in self.catalog["projects"]:
            if project["id"] == project_id:
                return project
        raise ValueError("项目不存在")

    @contextmanager
    def catalog_change(self):
        """Commit a private catalog only after the durable write succeeds.

        A failed request must not silently affect later requests or get saved
        by an unrelated successful action. Filesystem work is staged separately.
        """
        original = self.catalog
        self.catalog = copy.deepcopy(original)
        try:
            yield
            self.save()
        except Exception:
            self.catalog = original
            raise

    def directory(self, project_id):
        self.project(project_id)
        return safe_path(self.projects_dir, project_id)

    def touch(self, project_id):
        with self.catalog_change():
            self.project(project_id)["updated"] = int(time.time() * 1000)

    def backup(self, project_id, path):
        if path.is_file():
            target = self.backups / project_id / (str(time.time_ns()) + "-" + path.name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            # Bounded history: 100 latest versions per project, max source size 1 MiB each.
            for expired in sorted(target.parent.iterdir(), key=lambda p: p.name, reverse=True)[100:]:
                expired.unlink()

    def new_project(self, request, starter=True, publish=True):
        project_id = uuid.uuid4().hex
        project = {"id": project_id, "name": label(request.get("name")), "color": str(request.get("color", "#dbb572"))[:32],
                   "category": label(request.get("category"), "未分类"), "updated": int(time.time() * 1000), "practice": bool(request.get("practice", False))}
        directory = self.projects_dir / project_id
        directory.mkdir()
        try:
            if starter:
                atomic_write(directory / "main.py", '# 在这里开始你的 Python 项目\nprint("你好，PySlate！")\n'.encode())
            if publish:
                self.publish(project)
        except Exception:
            shutil.rmtree(directory)
            raise
        return project

    def publish(self, project):
        with self.catalog_change():
            self.catalog["projects"].append(project)
            if project["category"] not in self.catalog["categories"]:
                self.catalog["categories"].append(project["category"])

    def files(self, project_id, enforce_limit=True):
        directory = self.directory(project_id)
        result = []
        for current, dirs, files in os.walk(directory, followlinks=False):
            for name in dirs:
                safe_path(directory, (Path(current) / name).relative_to(directory).as_posix())
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for filename in files:
                path = Path(current) / filename
                relative = path.relative_to(directory).as_posix()
                safe_path(directory, relative)
                result.append({"path": relative, "size": path.stat().st_size})
                if enforce_limit and len(result) > 1000:
                    raise ValueError("项目文件超过 1000 个")
        return sorted(result, key=lambda item: item["path"])

    def dispatch(self, request):
        with self.lock:
            return self._dispatch(request)

    def _dispatch(self, r):
        action = r.get("action")
        if action == "bootstrap":
            course_path = self.root / "course" / "course.json"
            return {"platform": "windows", "version": VERSION, "python": sys.version.split()[0], "dataPath": str(self.data), **self.catalog,
                    "course": json.loads(course_path.read_text("utf-8")) if course_path.exists() else {"chapters": []}}
        if action == "state.patch":
            patch = r["patch"]
            if not isinstance(patch, dict) or len(json.dumps(patch)) > 4 * TEXT_LIMIT:
                raise ValueError("状态数据过大或格式错误")
            with self.catalog_change():
                self.catalog["state"].update(patch)
            return {"ok": True}
        if action == "category.create":
            name = label(r.get("name"))
            if name not in self.catalog["categories"]:
                with self.catalog_change():
                    self.catalog["categories"].append(name)
            return {"categories": self.catalog["categories"]}
        if action == "project.create":
            return {"project": self.new_project(r)}
        if action == "project.update":
            changes = {key: label(r[key]) for key in ("name", "category", "color") if key in r}
            with self.catalog_change():
                project = self.project(r["id"])
                project.update(changes)
                if project["category"] not in self.catalog["categories"]:
                    self.catalog["categories"].append(project["category"])
                project["updated"] = int(time.time() * 1000)
            return {"project": project}
        if action == "project.files":
            return {"files": self.files(r["id"])}
        if action in ("file.read", "file.write", "file.create", "file.rename", "file.delete"):
            directory = self.directory(r["id"])
            path = safe_path(directory, r["path"])
            if action == "file.read":
                if path.stat().st_size > TEXT_LIMIT:
                    raise ValueError("编辑器仅支持不超过 1 MiB 的文本文件")
                content = path.read_text("utf-8")
                if "\x00" in content:
                    raise ValueError("编辑器不支持二进制文件")
                return {"content": content}
            if action not in ("file.write", "file.create") and self.active_for(r["id"]):
                raise ValueError("请先停止程序，再修改项目文件")
            if action in ("file.write", "file.create"):
                data = r["content"].encode("utf-8")
                if len(data) > TEXT_LIMIT:
                    raise ValueError("文本文件不能超过 1 MiB")
                if action == "file.create" and path.exists():
                    raise ValueError("目标文件已存在")
                if not path.exists() and len(self.files(r["id"])) >= 1000:
                    raise ValueError("项目文件不能超过 1000 个")
                if action == "file.write":
                    self.backup(r["id"], path)
                    # Save fallible metadata before changing a learner's file.
                    # If the later file operation fails, only its recency may
                    # change; content and the path still describe the old file.
                    self.touch(r["id"])
                    atomic_write(path, data)
                else:
                    self.touch(r["id"])
                    path.parent.mkdir(parents=True, exist_ok=True)
                    # Exclusive creation protects against case aliases and a
                    # file appearing between the initial check and this open.
                    created = False
                    try:
                        with path.open("xb") as stream:
                            created = True
                            stream.write(data)
                            stream.flush()
                            os.fsync(stream.fileno())
                    except Exception:
                        if created:
                            path.unlink(missing_ok=True)
                        raise
            elif action == "file.rename":
                target = safe_path(directory, r["newPath"])
                if target.exists():
                    raise ValueError("目标文件已存在")
                self.touch(r["id"])
                target.parent.mkdir(parents=True, exist_ok=True)
                path.rename(target)
            else:
                self.backup(r["id"], path)
                self.touch(r["id"])
                path.unlink()
            return {"ok": True}
        if action == "project.delete":
            if self.active_for(r["id"]):
                raise ValueError("请先停止程序，再删除项目")
            directory = self.directory(r["id"])
            self.files(r["id"], enforce_limit=False)  # Reject reparse points before mutation.
            destination = self.trash / (r["id"] + "-" + str(time.time_ns()))
            recovery = destination.with_name(destination.name + ".recovery.json")
            # Recovery metadata lives beside the deleted project, never overwrites
            # a learner's file that happens to have the same metadata filename.
            atomic_write(recovery, json.dumps(self.project(r["id"]), ensure_ascii=False).encode())
            original_projects = self.catalog["projects"]
            moved = False
            try:
                rename_directory(directory, destination)  # Never copy through links.
                moved = True
                self.catalog["projects"] = [p for p in original_projects if p["id"] != r["id"]]
                self.save()
            except Exception:
                self.catalog["projects"] = original_projects
                if moved:
                    try:
                        rename_directory(destination, directory)
                    except Exception:
                        raise RuntimeError("删除未完成；项目文件完整保留在 " + str(destination) + "，恢复信息位于 " + str(recovery))
                recovery.unlink(missing_ok=True)
                raise
            return {"ok": True}
        if action == "project.duplicate":
            original = self.project(r["id"])
            source = self.directory(r["id"])
            entries = self.files(r["id"])
            if sum(e["size"] for e in entries) > EXPANDED_LIMIT:
                raise ValueError("项目超过 50 MiB")
            project = self.new_project({**original, "name": original["name"] + " 副本"}, False, False)
            destination = self.projects_dir / project["id"]
            try:
                for item in entries:
                    target = safe_path(destination, item["path"])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(safe_path(source, item["path"]), target)
                self.publish(project)
            except Exception:
                shutil.rmtree(destination)
                raise
            return {"project": project}
        if action == "project.export":
            directory = self.directory(r["id"])
            files = self.files(r["id"])
            if sum(f["size"] for f in files) > EXPANDED_LIMIT:
                raise ValueError("导出项目不能超过 50 MiB")
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                for item in files:
                    archive.write(safe_path(directory, item["path"]), item["path"])
            if buffer.tell() > ZIP_LIMIT:
                raise ValueError("压缩文件不能超过 20 MiB")
            name = re.sub(r'[<>:"/\\|?*]', "_", self.project(r["id"])["name"])
            return {"filename": name + ".zip", "base64": base64.b64encode(buffer.getvalue()).decode()}
        if action == "project.import":
            raw = base64.b64decode(r["base64"], validate=True)
            if len(raw) > ZIP_LIMIT:
                raise ValueError("ZIP 文件不能超过 20 MiB")
            prepared = []
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                if len(archive.infolist()) > 1000:
                    raise ValueError("ZIP 文件不能包含超过 1000 个条目")
                total, seen = 0, set()
                for info in archive.infolist():
                    if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                        raise ValueError("仅支持跨平台通用的 ZIP Stored/Deflate 压缩方式")
                    name = info.filename.rstrip("/") if info.is_dir() else info.filename
                    safe_path(self.projects_dir / "import-check", name)
                    key = name.casefold()
                    if key in seen:
                        raise ValueError("ZIP 包含重复或大小写冲突路径")
                    seen.add(key)
                    mode = info.external_attr >> 16
                    if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)) or info.flag_bits & 1:
                        raise ValueError("不支持链接、特殊文件或加密 ZIP")
                    total += info.file_size
                    if info.file_size > 10 * TEXT_LIMIT or total > EXPANDED_LIMIT or (info.file_size > TEXT_LIMIT and info.file_size > max(1, info.compress_size) * 200):
                        raise ValueError("ZIP 解压体积或压缩比超过限制")
                    if not info.is_dir():
                        prepared.append((name, archive.read(info)))
            file_names = {name.casefold() for name, _ in prepared}
            for name, _ in prepared:
                parent = PurePosixPath(name).parent
                while str(parent) != ".":
                    if str(parent).casefold() in file_names:
                        raise ValueError("ZIP 文件与目录路径冲突")
                    parent = parent.parent
            name = Path(str(r.get("filename", "导入项目.zip"))).stem
            # Stage all bytes before exposing the new project in the catalog.
            stage = self.data / ("import-" + uuid.uuid4().hex)
            stage.mkdir()
            project = None
            try:
                for relative, data in prepared:
                    atomic_write(safe_path(stage, relative), data)
                project = self.new_project({"name": name, "category": "导入项目", "color": "#a1c9b8"}, False, False)
                directory = self.projects_dir / project["id"]
                for relative, _ in prepared:
                    destination = safe_path(directory, relative)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(safe_path(stage, relative), destination)
                self.publish(project)
            except Exception:
                if project:
                    shutil.rmtree(self.projects_dir / project["id"], ignore_errors=True)
                raise
            finally:
                if stage.exists():
                    shutil.rmtree(stage)
            return {"project": project}
        if action == "run":
            if self.catalog["state"].get("trusted") is not True:
                raise ValueError("请先阅读并确认本地代码信任提示")
            if any(run.running for run in self.runs.values()):
                raise ValueError("已有程序运行中，请先停止")
            directory = self.directory(r["id"])
            entry = safe_path(directory, r.get("entry", "main.py"))
            if entry.suffix.lower() != ".py" or not entry.is_file():
                raise ValueError("请选择存在的 .py 文件运行")
            # Once launched, a run ID must reach the caller. An index failure
            # must not leave an unreported background process behind.
            self.touch(r["id"])
            run = Run(self.executable, Path(__file__).with_name("worker.py"), directory, entry)
            run.project_id = r["id"]
            self.runs = {run.id: run}  # Bound completed run retention to one run.
            return {"runId": run.id}
        if action in ("events", "input", "stop"):
            run = self.runs.get(r.get("runId"))
            if not run:
                raise ValueError("运行记录不存在")
            if action == "events":
                return run.poll(max(0, int(r.get("cursor", 0))))
            if action == "stop":
                run.stop()
                run.done.wait(3)
            else:
                if not run.running:
                    raise ValueError("程序已结束")
                if r.get("eof"):
                    return run.send_input(request_id=r.get("requestId"))
                else:
                    text = str(r.get("text", ""))
                    if len(text.encode()) > 64 * 1024:
                        raise ValueError("一次输入不能超过 64 KiB")
                    return run.send_input(text, request_id=r.get("requestId"))
            return {"ok": True}
        raise ValueError("不支持的操作: " + str(action))

    def active_for(self, project_id):
        return any(run.running and run.project_id == project_id for run in self.runs.values())

    def close(self):
        for run in self.runs.values():
            run.stop("应用关闭，程序已停止。")

class Handler(BaseHTTPRequestHandler):
    server_version = "PySlate/" + VERSION
    def log_message(self, *args):
        pass

    def secure(self):
        expected = "127.0.0.1:" + str(self.server.server_address[1])
        if self.headers.get("Host") != expected:
            raise ValueError("Host 不匹配")
        origin = self.headers.get("Origin")
        if origin and origin != "http://" + expected:
            raise ValueError("跨域请求已拒绝")
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            raise ValueError("跨站请求已拒绝")
        prefix = "/" + self.server.token + "/"
        path = unquote(urlsplit(self.path).path)
        if not path.startswith(prefix):
            raise ValueError("访问令牌无效")
        return path[len(prefix):]

    def respond(self, status, data, mime="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'self'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            relative = self.secure()
            if relative.startswith("course/"):
                path = safe_path(self.server.store.root, relative)
            else:
                path = safe_path(self.server.store.root / "web", relative or "index.html")
            if not path.is_file():
                raise FileNotFoundError("文件不存在")
            self.respond(200, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        except (ValueError, OSError) as error:
            self.respond(404, json.dumps({"error": str(error)}, ensure_ascii=False).encode())

    def do_POST(self):
        try:
            if self.secure() != "api":
                raise ValueError("接口不存在")
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("请求必须为 JSON")
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 29 * 1024 * 1024:
                raise ValueError("请求长度超限")
            self.connection.settimeout(15)
            request = json.loads(self.rfile.read(size))
            result = self.server.store.dispatch(request)
            self.respond(200, json.dumps(result, ensure_ascii=False).encode())
        except Exception as error:
            self.respond(400, json.dumps({"error": str(error)}, ensure_ascii=False).encode())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--data", type=Path, default=Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "PySlate" / "Data")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--token", default=None)
    parser.add_argument("--ready-file", type=Path)
    options = parser.parse_args()
    token = options.token or secrets.token_urlsafe(32)
    data_lock = DataLock(options.data)
    store = Store(options.root, options.data)
    server = ThreadingHTTPServer(("127.0.0.1", options.port), Handler)
    server.daemon_threads = True
    server.store, server.token = store, token
    ready = {"url": "http://127.0.0.1:%d/%s/index.html" % (server.server_address[1], token), "port": server.server_address[1], "pid": os.getpid()}
    if options.ready_file:
        atomic_write(options.ready_file, json.dumps(ready).encode())
    print(json.dumps(ready), flush=True)
    try:
        server.serve_forever()
    finally:
        store.close()
        server.server_close()
        data_lock.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("PySlate: " + str(error), file=sys.stderr, flush=True)
        raise SystemExit(1)
