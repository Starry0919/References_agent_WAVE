import re


STAGES = [
    ("strain construction", re.compile(r"\b(?:construct|knockout|deletion|overexpress|CRISPR|transform)\w*\b|构建|敲除|转化", re.I)),
    ("culture", re.compile(r"\b(?:culture|cultivated|incubat|ferment|medium)\w*\b|培养|发酵", re.I)),
    ("treatment", re.compile(r"\b(?:induc|treated|added|exposed)\w*\b|诱导|处理|加入", re.I)),
    ("measurement", re.compile(r"\b(?:measured|assay|HPLC|LC-?MS|GC-?MS|RNA-?seq|qPCR)\b|测定|检测", re.I)),
    ("analysis", re.compile(r"\b(?:analy[sz]ed|ANOVA|t-?test|DESeq2|GraphPad)\b|分析", re.I))
]


def build_workflow(clean_json):
    workflow = []
    sections = {v["id"]: v["title"] for v in clean_json.get("sections", [])}
    for paragraph in clean_json.get("paragraphs", []):
        for stage, pattern in STAGES:
            if pattern.search(paragraph["text"]):
                workflow.append({
                    "stage": stage, "input": None,
                    "operation": paragraph["text"], "output": None,
                    "source_location": {
                        "section": sections.get(paragraph.get("section"), ""),
                        "paragraph": paragraph["paragraph_id"]
                    },
                    "status": "reported"
                })
                break
    return workflow

