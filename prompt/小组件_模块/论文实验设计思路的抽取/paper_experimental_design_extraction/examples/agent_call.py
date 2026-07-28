import json
from pathlib import Path
from paper_experimental_design_extraction import execute
request=json.loads((Path(__file__).parent/"upload_request.json").read_text(encoding="utf-8"))
result=execute(request)
print(json.dumps({"task_id":result["task_id"],"status":result["status"]},ensure_ascii=False,indent=2))
