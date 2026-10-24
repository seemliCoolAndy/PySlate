"""Verify recorded source/package hashes, all174 images, and portable ZIP payload."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def digest(path):
    value=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1048576),b""): value.update(chunk)
    return value.hexdigest()


def main():
    root=Path(__file__).resolve().parents[2]
    output=root.parent/"windows"
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=root)
    parser.add_argument("--package",type=Path,default=output/"PySlate")
    parser.add_argument("--portable",type=Path,default=output/"PySlate-0.3.0-windows-x64-portable.zip")
    parser.add_argument("--report",type=Path,default=root/"test-reports/windows-v030-integrity.json")
    args=parser.parse_args()
    source,package=args.source.resolve(),args.package.resolve()
    manifest=json.loads((package/"BUILD-MANIFEST.json").read_text("utf-8-sig"))
    issues=[]
    def recorded(items,root):
        result={}
        for item in items:
            relative=PurePosixPath(item["path"])
            if relative.is_absolute() or ".." in relative.parts: raise ValueError("Invalid manifest path")
            path=root.joinpath(*relative.parts)
            result[relative.as_posix()]=item["sha256"]
            if not path.is_file() or digest(path)!=item["sha256"]: issues.append("Hash mismatch: "+str(path))
        return result
    source_hashes=recorded(manifest["sources"],source)
    package_hashes=recorded(manifest["files"],package)
    actual_sources={p.relative_to(source).as_posix() for name in ("windows","runtime","web","course","docs") for p in (source/name).rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    if actual_sources!=set(source_hashes): issues.append("Source snapshot file set changed")
    actual_package={p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    if actual_package!=set(package_hashes)|{"BUILD-MANIFEST.json"}: issues.append("Package file set changed")
    for relative,sha in source_hashes.items():
        if relative.startswith(("runtime/","web/","course/")):
            if package_hashes.get(relative)!=sha: issues.append("Source/package mismatch: "+relative)
        elif relative.startswith("docs/"):
            if Path(relative).name.startswith("RELEASE_REPORT"): continue
            dest="docs/developer/"+relative[5:]
            if package_hashes.get(dest)!=sha: issues.append("Developer doc mismatch: "+relative)
    user_docs=source/"docs"
    for name in ("USER_GUIDE.md","WINDOWS_GUIDE.md","ANDROID_GUIDE.md"):
        path=user_docs/name
        if path.exists() and package_hashes.get("docs/"+name)!=digest(path): issues.append("User guide mismatch: "+name)
    # These three texts come directly from the downloaded Windows SDK/runtime.
    replaced_licenses={"Python-LICENSE.txt","WebView2-LICENSE.txt","WebView2-NOTICE.txt"}
    license_count=0
    for path in sorted((source/"licenses").rglob("*")):
        if not path.is_file(): continue
        relative=path.relative_to(source/"licenses").as_posix()
        packaged=package/"licenses"/relative
        if not packaged.is_file(): issues.append("Missing third-party notice: "+relative)
        elif relative not in replaced_licenses and digest(path)!=digest(packaged): issues.append("Third-party notice mismatch: "+relative)
        license_count+=1
    for name in replaced_licenses|{"WebView2-Runtime-LICENSE.txt","PySlate-MIT.txt"}:
        if not (package/"licenses"/name).is_file(): issues.append("Missing required license: "+name)
    if any(p.name.startswith("RELEASE_REPORT") for p in (package/"docs").rglob("*")): issues.append("Release report must stay outside application package")
    course=json.loads((source/"course/course.json").read_text("utf-8"))
    lessons=[lesson for chapter in course["chapters"] for lesson in chapter["lessons"]]
    units=[unit for lesson in lessons for unit in lesson["tiers"]]
    if len(lessons)!=58 or len(units)!=174: issues.append("Expected58 topics and174 units")
    images=[]
    for lesson in lessons:
        if [unit["id"] for unit in lesson["tiers"]]!=["beginner","intermediate","advanced"]: issues.append("Tier order mismatch: "+lesson["id"])
        for unit in lesson["tiers"]:
            expected="course-assets/tier-"+lesson["id"]+"-"+unit["id"]+".webp"
            relative=unit["diagram"]
            a,b=source/"web"/relative,package/"web"/relative
            passed=relative==expected and a.is_file() and b.is_file()
            sha=digest(a) if a.is_file() else None
            if passed:
                with a.open("rb") as stream: header=stream.read(12)
                passed=header[:4]==b"RIFF" and header[8:12]==b"WEBP" and sha==digest(b)
            if not passed: issues.append("Image missing/invalid/different: "+relative)
            images.append({"unitId":lesson["id"]+":"+unit["id"],"file":relative,"sha256":sha,"passed":passed})
    if len({row["file"] for row in images})!=174: issues.append("Images are not174 unique paths")
    zip_hashes={**package_hashes,"BUILD-MANIFEST.json":digest(package/"BUILD-MANIFEST.json")}
    zip_count=0
    with zipfile.ZipFile(args.portable) as archive:
        names={item.filename for item in archive.infolist() if not item.is_dir()}
        if names!=set(zip_hashes): issues.append("Portable ZIP payload file set mismatch")
        for name in sorted(names):
            if name not in zip_hashes: continue
            value=hashlib.sha256()
            with archive.open(name) as stream:
                for chunk in iter(lambda:stream.read(1048576),b""): value.update(chunk)
            if value.hexdigest()!=zip_hashes[name]: issues.append("Portable ZIP hash mismatch: "+name)
            zip_count+=1
    report={"version":manifest["version"],"sourceCount":len(source_hashes),"packageCount":len(package_hashes),"portableFilesVerified":zip_count,"licenseFilesVerified":license_count,"topics":len(lessons),"units":len(units),"courseSHA256":digest(source/"course/course.json"),"images":images,"ignoredGeneratedCaches":[p.relative_to(package).as_posix() for p in package.rglob("*.pyc")],"issues":issues,"passed":not issues}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),"utf-8")
    print(json.dumps({key:value for key,value in report.items() if key!="images"},ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())

