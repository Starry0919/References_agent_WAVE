from __future__ import annotations
import json,time
from pathlib import Path
from typing import Any,Mapping
try:
    from .schema import SKILL_ID,SKILL_VERSION,POLICY,sha256_json,unwrap
    from .error_codes import error
    from .logger import JsonlSkillLogger
    from .adapters import summary,cards,details,evidence as evidence_view,risk as risk_view,governance as governance_view,quality as quality_view,k12 as k12_view
    from .formatter import collapsed,expanded
    from .validator import validate
except ImportError:
    from schema import SKILL_ID,SKILL_VERSION,POLICY,sha256_json,unwrap
    from error_codes import error
    from logger import JsonlSkillLogger
    from adapters import summary,cards,details,evidence as evidence_view,risk as risk_view,governance as governance_view,quality as quality_view,k12 as k12_view
    from formatter import collapsed,expanded
    from validator import validate

class FrontendAdapter:
    def __init__(self,logger=None): self.logger=logger if logger is not None else JsonlSkillLogger()
    def execute(self,request:Mapping[str,Any]):
        started=time.perf_counter();input_hash=sha256_json(request)
        if not isinstance(request,Mapping) or not isinstance(request.get("engineering_plan"),Mapping):
            return self._finish(self._failure(error("UI001"),input_hash),started)
        engineering=unwrap(request["engineering_plan"])
        if not isinstance(engineering,dict) or not {"engineering_plans","ai_combination_proposals"}.issubset(engineering):
            return self._finish(self._failure(error("UI001"),input_hash),started)
        language=request.get("language","zh")
        try: labels=self._labels(language)
        except (OSError,json.JSONDecodeError,ValueError):
            return self._finish(self._failure(error("UI004",{"language":language}),input_hash),started)
        k12=unwrap(request.get("k12_analysis",{}));evidence=unwrap(request.get("evidence",{}))
        quality=unwrap(request.get("quality_report",{}));governance=unwrap(request.get("governance",{}))
        audit=request.get("audit_trail",{})
        card_items=cards(engineering);detail_items=details(engineering)
        if any(x["source_type"] is None for x in card_items+detail_items):
            return self._finish(self._failure(error("UI003"),input_hash),started)
        ev=evidence_view(evidence);qual=quality_view(quality);k12v=k12_view(k12)
        risk=risk_view(engineering,k12);gov=governance_view(governance,audit)
        summ=summary(engineering,k12,quality,governance,labels)
        source_payload={"engineering_plan":engineering,"k12_analysis":k12,"evidence":evidence,
                        "quality_report":quality,"governance":governance,"audit_trail":audit}
        collapsed_obj=collapsed(summ,card_items,gov,labels)
        expanded_obj=expanded(detail_items,ev,qual,k12v,risk,gov,source_payload,labels)
        output={"language":language,"summary_view":summ,"step_cards":card_items,"detail_panels":detail_items,
                "evidence_view":ev,"quality_view":qual,"k12_adaptation_view":k12v,"risk_view":risk,
                "governance_view":gov,"collapsed_view":collapsed_obj,"expanded_view":expanded_obj}
        checks=validate(output,engineering)
        if not all(x["passed"] for x in checks):
            return self._finish(self._failure(error("UI003",{"failed_checks":[x["name"] for x in checks if not x["passed"]]}),input_hash),started)
        warnings=[]
        if ev["status"]=="unknown":warnings.append(error("UI002"))
        result={"status":"succeeded_with_warnings" if warnings else "succeeded","output":output,"artifacts":[],
                "self_check":{"passed":True,"checks":checks,"score":1.0},"warnings":warnings,"errors":[],
                "metrics":{"steps":len(card_items),"evidence_items":len(ev["items"]),"governance_status":gov["review_status"],"language":language},
                "provenance":{"skill_id":SKILL_ID,"skill_version":SKILL_VERSION,"input_hash":input_hash,
                              "output_hash":sha256_json(output),"presentation_policy_version":POLICY},
                "review_requests":[]}
        return self._finish(result,started)
    @staticmethod
    def _labels(language):
        path=Path(__file__).parent/"i18n"/f"{language}.json"
        labels=json.loads(path.read_text(encoding="utf-8"))
        required={"decision_title","summary","steps","governance","what","why","how","evidence","risk"}
        if not required.issubset(labels):raise ValueError("missing labels")
        return labels
    def _finish(self,result,started):
        result["metrics"]["duration_ms"]=round((time.perf_counter()-started)*1000,3)
        event={"skill_name":SKILL_ID,"steps":result["metrics"].get("steps",0),"evidence_items":result["metrics"].get("evidence_items",0),
               "governance_status":result["metrics"].get("governance_status"),"language":result["metrics"].get("language"),
               "errors":result["errors"],"status":result["status"]}
        try:self.logger(event)
        except Exception:pass
        return result
    @staticmethod
    def _failure(err,input_hash):
        return {"status":"terminal_failure","output":None,"artifacts":[],"self_check":{"passed":False,"checks":[],"score":0.0},
                "warnings":[],"errors":[err],"metrics":{},"provenance":{"skill_id":SKILL_ID,"skill_version":SKILL_VERSION,
                "input_hash":input_hash,"output_hash":None},"review_requests":[]}
def execute(request:Mapping[str,Any],**kwargs):return FrontendAdapter(**kwargs).execute(request)
