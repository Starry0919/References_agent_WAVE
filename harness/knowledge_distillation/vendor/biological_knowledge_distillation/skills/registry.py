"""Loads the 13 internal steps from the sibling top-level ``skills/`` folder
(``.../教材生物学知识蒸馏/skills/stepNN_*``), the same layout used by the
论文实验设计抽取 module. Step numbering is an internal execution-tracking
device only - the orchestrator (module.execute / 生物学知识蒸馏) is the only
capability exposed to the outer agent; see SKILL.md.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

STEPS = [
    "step01_task_contract",
    "step02_source_validation",
    "step03_document_parsing",
    "step04_scope_selection",
    "step05_basic_knowledge_extraction",
    "step06_principle_distillation",
    "step07_decision_rule_generation",
    "step08_pattern_validation_failure",
    "step09_evidence_binding",
    "step10_knowledge_fusion",
    "step11_paper_case_linking",
    "step12_quality_governance",
    "step13_frontend_adapter",
]


class SkillRegistry:
    def __init__(self, executors=None):
        self.root = Path(__file__).resolve().parents[2]
        self.executors = dict(executors or {})

    def execute(self, name, request, kwargs=None):
        if name in self.executors:
            return self.executors[name](request)
        skills_root = self.root / "skills"
        if str(skills_root) not in sys.path:
            sys.path.insert(0, str(skills_root))
        fn = importlib.import_module(f"{name}.skill").execute
        return fn(request, **(kwargs or {}))

    def metadata(self):
        result = []
        for name in STEPS:
            interface_path = self.root / "skills" / name / "interface.json"
            data = json.loads(interface_path.read_text(encoding="utf-8"))
            result.append({
                "step_name": name,
                "version": data["version"],
                "input_schema": f"skills/{name}/interface.json#/input",
                "output_schema": f"skills/{name}/interface.json#/output",
                "status": "implemented" if (self.root / "skills" / name / "skill.py").is_file() else "unavailable",
                "implementation": data["implementation"],
            })
        return result
