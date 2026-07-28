from __future__ import annotations
import importlib,json,sys
from pathlib import Path
SKILLS=[
"skill01_requirement_parser","skill02_literature_retrieval","skill03_citation_validation","skill04_pdf_acquisition",
"skill05_pdf_parser","skill06_markdown_cleaner","skill07_experiment_extraction","skill08_evidence_binding",
"skill09_quality_evaluation","skill10_k12_transfer","skill11_engineering_proposal","skill12_qc_human_review","skill13_frontend_adapter"]
class SkillRegistry:
    def __init__(self,executors=None):
        self.root=Path(__file__).resolve().parents[2]
        self.executors=dict(executors or {})
    def execute(self,name,request,kwargs=None):
        if name in self.executors:return self.executors[name](request)
        skills_root=self.root/"skills"
        if str(skills_root) not in sys.path:sys.path.insert(0,str(skills_root))
        fn=importlib.import_module(f"{name}.skill").execute
        return fn(request,**(kwargs or {}))
    def metadata(self):
        result=[]
        for name in SKILLS:
            data=json.loads((self.root/"skills"/name/"interface.json").read_text(encoding="utf-8"))
            result.append({"skill_name":name,"version":data["version"],"input_schema":f"skills/{name}/interface.json#/input",
                           "output_schema":f"skills/{name}/interface.json#/output",
                           "status":"implemented" if (self.root/"skills"/name/"skill.py").is_file() else "unavailable",
                           "implementation":data["implementation"]})
        return result
