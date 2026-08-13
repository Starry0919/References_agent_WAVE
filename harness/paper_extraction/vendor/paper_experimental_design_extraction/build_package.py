from __future__ import annotations
import hashlib,json,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
VERSION=(Path(__file__).parent/"VERSION").read_text(encoding="utf-8").strip()
OUTPUT=ROOT/"dist"/f"paper_experimental_design_extraction-{VERSION}.zip"
INCLUDE=("paper_experimental_design_extraction","skills","framework")
EXCLUDED={"__pycache__",".pytest_cache","runtime","logs","dist"}
def included(path):
    return not any(part in EXCLUDED for part in path.parts) and path.suffix not in {".pyc",".pyo"}
def build():
    files=[]
    for folder in INCLUDE:
        for path in (ROOT/folder).rglob("*"):
            if path.is_file() and included(path.relative_to(ROOT)):files.append(path)
    manifest={"module":"论文实验设计抽取","english_name":"Literature Experimental Design Extraction Module",
              "version":VERSION,"created_time":datetime.now(timezone.utc).isoformat(),"files":[]}
    for path in sorted(files):
        data=path.read_bytes();manifest["files"].append({"path":path.relative_to(ROOT).as_posix(),
            "size":len(data),"sha256":hashlib.sha256(data).hexdigest()})
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(OUTPUT,"w",zipfile.ZIP_DEFLATED) as archive:
        for path in files:archive.write(path,path.relative_to(ROOT).as_posix())
        archive.writestr("package_manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
    digest=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    (OUTPUT.with_suffix(".zip.sha256")).write_text(f"{digest}  {OUTPUT.name}\n",encoding="utf-8")
    return {"archive":str(OUTPUT),"sha256":digest,"files":len(files),"size":OUTPUT.stat().st_size}
if __name__=="__main__":print(json.dumps(build(),ensure_ascii=False,indent=2))
