from __future__ import annotations
import copy,json
from pathlib import Path
import jsonschema
from .config import DEFAULT_CONFIG
from .workflow import WorkflowEngine
def execute(request,options=None):
    options=dict(options or {})
    schema=json.loads((Path(__file__).parent/"schema"/"input.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(request)
    config=copy.copy(DEFAULT_CONFIG)
    if options.get("state_dir"):config.state_dir=Path(options["state_dir"])
    if options.get("language"):config.language=options["language"]
    result=WorkflowEngine(config,options.get("executors")).run(request,options)
    out_schema=json.loads((Path(__file__).parent/"schema"/"output.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(out_schema).validate(result)
    return result
