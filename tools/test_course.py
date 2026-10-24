"""Execute every course example and answer with the selected real CPython.

Each run receives a new temporary current directory. This prevents course fixture
files from replacing application or learner files; it is not an OS sandbox.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time


def normalize(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def write_fixtures(folder: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Fixture path must be project-relative: {name}")
        target = folder / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source_root = Path(__file__).resolve().parents[1]
    parser.add_argument("--course", type=Path, default=source_root / "course" / "course.json")
    parser.add_argument("--report", type=Path, default=source_root / "test-reports" / "course.json")
    parser.add_argument("--python", default=sys.executable, help="Real CPython executable")
    parser.add_argument("--worker", type=Path, help="Optional PySlate worker.py; reproduce its project search path and input protocol")
    parser.add_argument("--partial", action="store_true", help="Authoring only: permit a partial course; never use for release acceptance")
    parser.add_argument("--topic", action="append", help="Only execute selected topic IDs; schema still checks the full input document")
    parser.add_argument("--tier", choices=("beginner", "intermediate", "advanced"), help="Only execute this learning level")
    args = parser.parse_args()
    course_bytes = args.course.read_bytes()
    course = json.loads(course_bytes.decode("utf-8"))
    topics = [lesson for chapter in course["chapters"] for lesson in chapter["lessons"]]
    is_v2 = course["version"] >= 2
    lessons = [unit for topic in topics for unit in topic["tiers"]] if is_v2 else topics
    ids: set[str] = set()
    problems: list[str] = []
    required = ("id", "title", "minutes", "prerequisites", "objectives", "body", "code", "stdin", "expectedOutput", "exercise", "solution", "commonMistakes", "summary", "solutionExpectedOutput")
    for topic in topics:
        if topic["id"] in ids:
            problems.append(f"duplicate topic id {topic['id']}")
        for prerequisite in topic["prerequisites"]:
            if prerequisite not in ids:
                problems.append(f"{topic['id']}: prerequisite {prerequisite} is absent or comes later")
        ids.add(topic["id"])
        if is_v2 and [unit["id"] for unit in topic["tiers"]] != ["beginner", "intermediate", "advanced"]:
            problems.append(f"{topic['id']}: three ordered tiers are required")
    unit_ids = set()
    for lesson in lessons:
        identity = lesson.get("unitId", lesson["id"])
        for key in required:
            if key not in lesson:
                problems.append(f"{lesson.get('id')}: missing {key}")
        if identity in unit_ids:
            problems.append(f"duplicate unit id {identity}")
        unit_ids.add(identity)
        for prerequisite in lesson["prerequisites"]:
            if prerequisite not in ids:
                problems.append(f"{identity}: prerequisite {prerequisite} is absent")
        if is_v2:
            if lesson.get("unitId") != f"{lesson.get('topicId')}:{lesson['id']}":
                problems.append(f"{identity}: malformed unitId")
            visual = lesson.get("visual", {})
            if not all(visual.get(key) for key in ("kind", "caption", "alt", "stages")):
                problems.append(f"{identity}: missing semantic visual metadata")
            if lesson.get("diagram") != f"course-assets/tier-{lesson.get('topicId')}-{lesson['id']}.webp":
                problems.append(f"{identity}: unexpected tier image path")
            if len(lesson.get("testCases", [])) < (2 if lesson['id']=="beginner" else 4):
                problems.append(f"{identity}: insufficient canonical execution cases")
        if len(lesson["body"]) < 150:
            problems.append(f"{identity}: explanation is too short")
        if len(lesson["objectives"]) < 2 or len(lesson["commonMistakes"]) < 2:
            problems.append(f"{lesson['id']}: needs at least two objectives and common mistakes")
        for field in ("code", "solution"):
            try:
                ast.parse(lesson[field], filename=f"{lesson['id']}_{field}.py", feature_version=(3, 11))
            except SyntaxError as exc:
                problems.append(f"{lesson['id']} {field}: Python 3.11 grammar: {exc}")
        for field in ("files", "solutionFiles"):
            for name, content in lesson.get(field, {}).items():
                if name.endswith(".py"):
                    try:
                        ast.parse(content, filename=name, feature_version=(3, 11))
                    except SyntaxError as exc:
                        problems.append(f"{lesson['id']} {field}/{name}: Python 3.11 grammar: {exc}")
    if len(topics) < 48 and not args.partial:
        problems.append("fewer than 48 lessons")
    if is_v2 and not args.partial and (len(topics)!=58 or len(lessons)!=174):
        problems.append("v2 release requires exactly 58 topics and 174 units")
    if is_v2:
        for topic in topics:
            if len({unit['code'] for unit in topic['tiers']})!=3:
                problems.append(f"{topic['id']}: examples repeat between learning levels")
            for unit in topic['tiers']:
                if unit['code']==unit['solution']:
                    problems.append(f"{unit['unitId']}: answer repeats example unchanged")
    results = []
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    version = subprocess.run([args.python, "-VV"], capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    for lesson in lessons:
        identity = lesson.get("unitId", lesson["id"])
        if args.topic and lesson.get("topicId",lesson["id"]) not in args.topic:
            continue
        if args.tier and lesson["id"] != args.tier:
            continue
        cases = list(lesson.get("testCases", [])) if is_v2 else [
            {"name": "example", "field": "code", "stdin": lesson["stdin"], "expectedOutput": lesson["expectedOutput"]},
            {"name": "answer", "field": "solution", "stdin": lesson["stdin"], "expectedOutput": lesson["solutionExpectedOutput"]},
            *lesson.get("testCases", [])]
        for case in cases:
            started = time.perf_counter()
            with tempfile.TemporaryDirectory(prefix=f"pyslate_{lesson['id']}_") as temporary:
                temporary_path = Path(temporary)
                script = Path(temporary) / "lesson.py"
                source = lesson[case["field"]]
                for replacement in case.get("replacements", []):
                    if replacement["find"] not in source:
                        raise ValueError(f"{identity}/{case['name']}: replacement target absent: {replacement['find']!r}")
                    source = source.replace(replacement["find"], replacement["replace"])
                if case.get("assertions"):
                    source += "\n" + case["assertions"] + "\n"
                ast.parse(source, filename=identity, feature_version=(3,11))
                script.write_text(source, encoding="utf-8")
                write_fixtures(temporary_path, case.get("initialFiles", {}))
                command = [args.python, "-I", "-X", "utf8", str(script)]
                if "fileSet" in case:
                    write_fixtures(temporary_path, lesson[case["fileSet"]])
                    script = temporary_path / case.get("entrypoint", "main.py")
                    if case.get("replacements") or case.get("assertions"):
                        entry_source=script.read_text(encoding="utf-8")
                        for replacement in case.get("replacements",[]):
                            if replacement["find"] not in entry_source:
                                raise ValueError(f"{identity}: file entry replacement absent")
                            entry_source=entry_source.replace(replacement["find"],replacement["replace"])
                        entry_source+="\n"+case.get("assertions","")+"\n"
                        script.write_text(entry_source,encoding="utf-8")
                    # A normal project launch must include its own directory on
                    # sys.path, exactly as `python main.py` does.
                    command = [args.python, "-X", "utf8", str(script)]
                input_prefix = ""
                if args.worker:
                    handshake = "pyslate-course-test-handshake"
                    input_prefix = handshake + "\n"
                    command = [args.python, "-u", "-X", "utf8", str(args.worker.resolve()), str(script), "PYSLATE_COURSE_INPUT", handshake]
                try:
                    process = subprocess.run(command,
                                             input=input_prefix + case["stdin"], capture_output=True,
                                             text=True, encoding="utf-8", errors="replace",
                                             cwd=temporary, env=environment, timeout=8)
                    output = normalize(process.stdout)
                    errors = normalize(process.stderr)
                    passed = process.returncode == 0 and output == normalize(case["expectedOutput"])
                    # unittest writes its normal result to stderr. Reject tracebacks
                    # and compare exact stdout; a nonzero exit always fails.
                    passed = passed and "Traceback (most recent call last)" not in errors
                    checks = {}
                    for name, expected in case.get("expectedFiles", {}).items():
                        target = temporary_path / name
                        checks[name] = target.is_file() and normalize(target.read_text(encoding="utf-8")) == normalize(expected)
                    passed = passed and all(checks.values())
                    followup_result = None
                    if "followupStdin" in case:
                        followup = subprocess.run(command, input=input_prefix + case["followupStdin"], capture_output=True,
                                                  text=True, encoding="utf-8", errors="replace", cwd=temporary,
                                                  env=environment, timeout=8)
                        followup_passed = followup.returncode == 0 and normalize(followup.stdout) == normalize(case["followupExpectedOutput"])
                        passed = passed and followup_passed
                        followup_result = {"passed": followup_passed, "exitCode": followup.returncode,
                                           "stdout": normalize(followup.stdout), "stderr": normalize(followup.stderr),
                                           "expectedOutput": case["followupExpectedOutput"]}
                    result = {"lesson": lesson.get("topicId",lesson["id"]), "unitId":identity,"tier":lesson["id"] if is_v2 else None,"title": lesson["title"], "case": case["name"],
                              "field": case["field"], "passed": passed, "exitCode": process.returncode,
                              "stdout": output, "stderr": errors, "expectedOutput": case["expectedOutput"],
                              "filesCreated": sorted(str(path.relative_to(temporary)).replace("\\", "/") for path in Path(temporary).rglob("*") if path.is_file() and path != script)}
                    if checks:
                        result["fileChecks"] = checks
                    if followup_result is not None:
                        result["followup"] = followup_result
                except subprocess.TimeoutExpired:
                    result = {"lesson": lesson["id"], "case": case["name"], "field": case["field"], "passed": False, "error": "8-second timeout"}
            result["durationMs"] = round((time.perf_counter() - started) * 1000)
            results.append(result)
            print(f"{'PASS' if result['passed'] else 'FAIL'} {identity} {case['name']}")
    report = {"courseVersion": course["version"], "courseSha256": hashlib.sha256(course_bytes).hexdigest(),
              "python": version, "host": platform.platform(), "compatibilityTarget": "Python 3.11+; 3.11 grammar checked; execution version recorded above",
              "executionMode": "PySlate worker" if args.worker else "direct CPython",
              "worker": str(args.worker.resolve()) if args.worker else None,
              "isolation": "Fresh temporary working directory per run; not a security sandbox",
              "lessons":len(topics), "units":len(lessons), "projects":sum(topic["id"].startswith("p") for topic in topics),
              "selection":{"topics":args.topic,"tier":args.tier},
              "partialAuthoring":args.partial,
              "caseSemantics":"v2 testCases is canonical; replacements in order then append assertions; exact stdout, exit code and optional files/followup",
              "cases": len(results), "passed": sum(result["passed"] for result in results),
              "schemaProblems": problems, "results": results}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = ["# 课程执行测试", "", f"- 解释器：`{version}`", f"- 主机：`{platform.platform()}`", f"- 课程 SHA256：`{report['courseSha256']}`", f"- {len(topics)} 主题 / {len(lessons)} 学习单元 / {report['projects']} 个项目 / {report['passed']}/{len(results)} 个执行用例通过", f"- 结构及前置关系检查：{'通过' if not problems else '失败'}", "", "每个示例、参考答案及额外输入用例均在新的临时工作目录内由真实 CPython 子进程执行，比较退出码和完整标准输出。v2 testCases为完整用例集合；按顺序替换指定源文本后追加assertions。超时8秒。文件项目另有读回和不覆盖检查。临时目录只隔离测试文件，不构成操作系统安全沙箱。", "", "兼容目标是Python3.11+；语法解析不等于已在每个3.11+运行时逐一测试。Android、Windows嵌入环境另行验收。", "", "| 学习单元 | 用例 | 结果 |", "|---|---|---|"]
    markdown.extend(f"| {result.get('unitId',result['lesson'])} | {result['case']} | {'通过' if result['passed'] else '失败'} |" for result in results)
    markdown[2:2] = [f"- 执行模式：`{report['executionMode']}`", f"- Worker：`{report['worker'] or '未使用'}`"]
    if problems:
        markdown.extend(["", "## 结构问题", *[f"- {problem}" for problem in problems]])
    args.report.with_suffix(".md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    print(f"{report['passed']}/{len(results)} execution cases passed; {len(problems)} schema problems")
    return 0 if report["passed"] == len(results) and not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
