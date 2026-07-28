from pathlib import Path


class ManualUploadHandler:
    source_type = "manual_upload"

    def read(self, upload):
        path = Path(upload["path"]).expanduser().resolve()
        return {
            "data": path.read_bytes(), "content_type": "application/pdf",
            "source_url": str(path), "final_url": str(path),
            "source_type": self.source_type, "file_name": path.name
        }
