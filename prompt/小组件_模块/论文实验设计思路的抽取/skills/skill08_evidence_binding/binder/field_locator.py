class DocumentEvidenceIndex:
    def __init__(self, clean_json):
        self.sections = {v["id"]: v for v in clean_json.get("sections", [])}
        self.units = {}
        for paragraph in clean_json.get("paragraphs", []):
            section = self.sections.get(paragraph.get("section"), {})
            self.units[paragraph["paragraph_id"]] = {
                "unit_id": paragraph["paragraph_id"], "text": paragraph["text"],
                "section": section.get("title", ""), "subsection": None,
                "paragraph": paragraph["paragraph_id"], "page": paragraph.get("page"),
                "figure": None, "table": None, "evidence_type": "supplement"
                if "supplement" in section.get("title", "").casefold() else "text"
            }
        for figure in clean_json.get("figures", []):
            unit_id = "figure:" + figure["figure_id"]
            self.units[unit_id] = {
                "unit_id": unit_id, "text": figure.get("caption") or "",
                "section": None, "subsection": None, "paragraph": None,
                "page": figure.get("page"), "figure": figure["figure_id"],
                "table": None, "evidence_type": "figure"
            }
        for table in clean_json.get("tables", []):
            unit_id = "table:" + table["table_id"]
            text = table.get("title") or ""
            if table.get("content"):
                text += "\n" + "\n".join(" | ".join(map(str, row)) for row in table["content"])
            self.units[unit_id] = {
                "unit_id": unit_id, "text": text.strip(),
                "section": None, "subsection": None, "paragraph": None,
                "page": table.get("page"), "figure": None,
                "table": table["table_id"], "evidence_type": "table"
            }

    def get(self, unit_id):
        return self.units.get(unit_id)

    def text_units(self):
        return [v for v in self.units.values() if v["evidence_type"] in {"text", "supplement"}]

    def visual_units(self):
        return [v for v in self.units.values() if v["evidence_type"] in {"figure", "table"}]

