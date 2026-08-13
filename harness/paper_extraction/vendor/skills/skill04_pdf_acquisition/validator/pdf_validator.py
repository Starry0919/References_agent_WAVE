from pathlib import Path


class PdfValidator:
    def validate_bytes(self, data: bytes, file_name: str, content_type: str = "application/pdf"):
        errors = []
        if not str(file_name).casefold().endswith(".pdf"):
            errors.append("invalid_extension")
        if not data:
            errors.append("empty_file")
        if data and not data.startswith(b"%PDF-"):
            errors.append("invalid_magic_header")
        if data and b"%%EOF" not in data[-2048:]:
            errors.append("missing_eof_marker")
        normalized_type = str(content_type or "").split(";", 1)[0].strip().casefold()
        if normalized_type not in {"application/pdf", "application/octet-stream"}:
            errors.append("invalid_mime_type")
        return {"valid": not errors, "errors": errors, "size_bytes": len(data), "mime_type": "application/pdf"}

    def validate_file(self, path: Path):
        if not path.exists() or not path.is_file():
            return {"valid": False, "errors": ["file_not_found"], "size_bytes": 0, "mime_type": "application/pdf"}
        return self.validate_bytes(path.read_bytes(), path.name)

