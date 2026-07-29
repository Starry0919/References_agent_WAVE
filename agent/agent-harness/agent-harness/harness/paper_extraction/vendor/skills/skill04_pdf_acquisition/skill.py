from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence

try:
    from .advisor import DoubaoPdfAdvisor
    from .artifact import ArtifactManager, verify_checksum
    from .artifact.metadata import enrich_identity_from_pdf, paper_identity
    from .downloader import (DoiDownloader, PublisherDownloader, RepositoryDownloader,
                             OpenAlexDownloader, EuropePmcDownloader, UnpaywallDownloader,
                             SemanticScholarDownloader)
    from .error_codes import error
    from .logger import JsonlSkillLogger
    from .schema import SKILL_ID, SKILL_VERSION, safe_paper_id, sha256_bytes, sha256_json
    from .uploader import ManualUploadHandler
    from .validator import PdfValidator
except ImportError:
    from advisor import DoubaoPdfAdvisor
    from artifact import ArtifactManager, verify_checksum
    from artifact.metadata import enrich_identity_from_pdf, paper_identity
    from downloader import (DoiDownloader, PublisherDownloader, RepositoryDownloader,
                            OpenAlexDownloader, EuropePmcDownloader, UnpaywallDownloader,
                            SemanticScholarDownloader)
    from error_codes import error
    from logger import JsonlSkillLogger
    from schema import SKILL_ID, SKILL_VERSION, safe_paper_id, sha256_bytes, sha256_json
    from uploader import ManualUploadHandler
    from validator import PdfValidator


class PdfAcquisitionSkill:
    def __init__(
        self,
        artifact_root: Optional[Path] = None,
        downloaders: Optional[Sequence[Any]] = None,
        upload_handler: Optional[Any] = None,
        logger: Optional[Callable[[Mapping[str, Any]], None]] = None,
        clock: Optional[Callable[[], datetime]] = None,
        pdf_advisor: Optional[Any] = None,
    ):
        module_root = Path(__file__).resolve().parents[2]
        self.manager = ArtifactManager(artifact_root or module_root / "paper_artifacts")
        self.downloaders = list(downloaders or [
            OpenAlexDownloader(), EuropePmcDownloader(), UnpaywallDownloader(),
            SemanticScholarDownloader(), PublisherDownloader(), RepositoryDownloader(), DoiDownloader()
        ])
        self.upload_handler = upload_handler or ManualUploadHandler()
        self.validator = PdfValidator()
        self.pdf_advisor = pdf_advisor if pdf_advisor is not None else DoubaoPdfAdvisor.from_environment()
        self.logger = logger if logger is not None else JsonlSkillLogger()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def execute(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        started = time.perf_counter()
        input_hash = sha256_json(request)
        if not isinstance(request, Mapping) or (
            not isinstance(request.get("accepted_candidates", []), list)
            or not isinstance(request.get("manual_uploads", []), list)
        ):
            return self._finish(self._failure(error("PDF001", {"field": "input"}), input_hash), started)
        if "accepted_candidates" not in request and "manual_uploads" not in request:
            return self._finish(self._failure(error("PDF001", {"field": "accepted_candidates/manual_uploads"}), input_hash), started)

        paper_artifacts, failed_items, deferred_items = [], [], []
        source_urls = request.get("source_urls") or {}
        policy = request.get("download_policy") or {}
        accepted = request.get("accepted_candidates", [])
        selected_ids = set(policy.get("paper_ids") or [])
        if selected_ids:
            accepted = [x for x in accepted if x.get("paper_id") in selected_ids]
        max_candidates = policy.get("max_candidates")
        if max_candidates is not None:
            max_candidates = max(1, int(max_candidates))
            deferred_items = [{"paper_id": x.get("paper_id"), "doi": x.get("identifiers", {}).get("doi"),
                               "reason": "deferred_by_small_batch_limit"} for x in accepted[max_candidates:]]
            accepted = accepted[:max_candidates]
        for candidate in accepted:
            if candidate.get("citation_validation", {}).get("status") != "valid":
                failed_items.append({
                    "paper_id": candidate.get("paper_id"), "error": error("PDF001"),
                    "attempts": [], "processing_status": "failed"
                })
                continue
            artifact, failure = self._download_candidate(candidate, source_urls.get(candidate.get("paper_id"), {}))
            if artifact:
                paper_artifacts.append(artifact)
            else:
                failed_items.append(failure)

        for upload in request.get("manual_uploads", []):
            artifact, failure = self._process_upload(upload)
            if artifact:
                paper_artifacts.append(artifact)
            else:
                failed_items.append(failure)

        artifact_refs = [item["artifact_ref"] for item in paper_artifacts]
        output = {
            "artifacts": artifact_refs,
            "paper_artifacts": paper_artifacts,
            "failed_items": failed_items,
            "deferred_items": deferred_items,
            "manual_download_items": [
                {"paper_id": x.get("paper_id"), "doi": next((c.get("identifiers", {}).get("doi") for c in accepted if c.get("paper_id") == x.get("paper_id")), None),
                 "doi_url": "https://doi.org/" + next((c.get("identifiers", {}).get("doi") for c in accepted if c.get("paper_id") == x.get("paper_id")), "")
                 if next((c.get("identifiers", {}).get("doi") for c in accepted if c.get("paper_id") == x.get("paper_id")), None) else None,
                 "reason": x["error"]["message"]} for x in failed_items
            ]
        }
        checks = self._self_check(output)
        if not all(check["passed"] for check in checks):
            return self._finish(self._failure(error("PDF005", {"failed_checks": [c["name"] for c in checks if not c["passed"]]}), input_hash), started)

        if failed_items and not paper_artifacts:
            status = "needs_review"
        elif failed_items:
            status = "succeeded_with_warnings"
        else:
            status = "succeeded"
        result = {
            "status": status, "output": output, "artifacts": artifact_refs,
            "self_check": {"passed": True, "checks": checks, "score": 1.0},
            "warnings": [{"code": item["error"]["local_code"], "paper_id": item.get("paper_id")} for item in failed_items],
            "errors": [],
            "metrics": {"verified_artifacts": len(paper_artifacts), "failed_items": len(failed_items),
                        "deferred_items": len(deferred_items), "sources_configured": len(self.downloaders)},
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": sha256_json(output)
            },
            "review_requests": [
                {"reason": "pdf_acquisition_failed", "paper_id": item.get("paper_id")}
                for item in failed_items
            ]
        }
        return self._finish(result, started)

    def _download_candidate(self, candidate, configured_urls):
        attempts = []
        downloaders = list(self.downloaders)
        advisor_used = False
        if self.pdf_advisor:
            try:
                ordered = self.pdf_advisor.prioritize(candidate, [v.source_type for v in downloaders])
                positions = {name: index for index, name in enumerate(ordered)}
                downloaders.sort(key=lambda value: positions.get(value.source_type, len(positions)))
                advisor_used = True
            except Exception:
                pass
        for attempt_number, downloader in enumerate(downloaders, 1):
            source_type = downloader.source_type
            url_key = {
                "publisher_download": "publisher_pdf",
                "repository_download": "repository_pdf",
                "doi_download": "doi_pdf"
            }.get(source_type)
            url = configured_urls.get(url_key) if isinstance(configured_urls, Mapping) else None
            try:
                response = downloader.fetch(candidate, url)
                validation = self.validator.validate_bytes(
                    response["data"], "original.pdf", response.get("content_type", "")
                )
                attempt = {
                    "attempt": attempt_number, "source_type": response["source_type"],
                    "source_url": response["source_url"], "status": "verified" if validation["valid"] else "invalid",
                    "validation_errors": validation["errors"]
                }
                attempt["advisor"] = "doubao" if advisor_used else "deterministic"
                if response.get("metadata_url"):
                    attempt["metadata_url"] = response["metadata_url"]
                if response.get("license"):
                    attempt["license"] = response["license"]
                attempts.append(attempt)
                if not validation["valid"]:
                    continue
                artifact = self._store(
                    candidate, response["data"], response["source_type"],
                    response["source_url"], attempts
                )
                return artifact, None
            except Exception as exc:
                attempts.append({
                    "attempt": attempt_number, "source_type": source_type,
                    "source_url": url, "status": "failed", "error_type": type(exc).__name__
                })
        return None, {
            "paper_id": candidate.get("paper_id"), "error": error("PDF002", retryable=False),
            "attempts": attempts, "processing_status": "failed"
        }

    def _process_upload(self, upload):
        try:
            response = self.upload_handler.read(upload)
            validation = self.validator.validate_bytes(
                response["data"], response["file_name"], response["content_type"]
            )
            if not validation["valid"]:
                return None, {
                    "paper_id": upload.get("paper_id"), "error": error("PDF006", {"validation_errors": validation["errors"]}),
                    "attempts": [{"attempt": 1, "source_type": "manual_upload", "status": "invalid"}],
                    "processing_status": "failed"
                }
            identity = dict(upload.get("paper_identity") or {})
            identity.setdefault("paper_id", upload.get("paper_id") or "manual_" + sha256_bytes(response["data"])[:16])
            candidate = {
                "paper_id": identity["paper_id"], "title": identity.get("title"),
                "authors": identity.get("authors", []), "journal": identity.get("journal"),
                "year": identity.get("year"), "identifiers": {"doi": identity.get("doi")} if identity.get("doi") else {}
            }
            return self._store(
                candidate, response["data"], "manual_upload", response["source_url"],
                [{"attempt": 1, "source_type": "manual_upload", "source_url": response["source_url"], "status": "verified"}]
            ), None
        except Exception as exc:
            return None, {
                "paper_id": upload.get("paper_id") if isinstance(upload, Mapping) else None,
                "error": error("PDF006", {"error_type": type(exc).__name__}),
                "attempts": [], "processing_status": "failed"
            }

    def _store(self, candidate, data, source_type, source_url, attempts):
        # Fills a missing title/DOI straight from the PDF itself (its own
        # document metadata + a page-1 DOI scan) - manual uploads never
        # supply these (uploader/manual_upload_handler.py only carries
        # `path`+`paper_id`), and citation metadata for a downloaded
        # candidate can also arrive with a gap. Never overwrites a value
        # already known from `candidate`.
        identity = paper_identity(candidate)
        identity = enrich_identity_from_pdf(identity, data)
        download_time = self.clock().isoformat()
        metadata = {
            "paper_identity": identity,
            "source_information": {
                "source_type": source_type, "source_url": source_url,
                "download_time": download_time
            },
            "download_attempts": attempts,
            "processing_status": "verified"
        }
        path, version, checksum, created = self.manager.store(identity["paper_id"], data, metadata)
        artifact_ref = {
            "artifact_id": "artifact:" + checksum[:24],
            "media_type": "application/pdf",
            "sha256": checksum,
            "version": str(version),
            "source": source_type,
            "uri": str(path)
        }
        return {
            "paper_identity": identity,
            "file_information": {
                "file_name": path.name, "path": str(path),
                "size_bytes": len(data), "mime_type": "application/pdf"
            },
            "source_information": {
                "source_type": source_type, "source_url": source_url,
                "download_time": download_time
            },
            "integrity": {
                "checksum_algorithm": "sha256", "checksum_value": checksum
            },
            "processing_status": "verified",
            "artifact_version": str(version),
            "immutable_reused": not created,
            "download_attempts": attempts,
            "artifact_ref": artifact_ref
        }

    @staticmethod
    def _self_check(output):
        identity = all(item["paper_identity"]["paper_id"] for item in output["paper_artifacts"])
        integrity = all(
            Path(item["file_information"]["path"]).is_file()
            and verify_checksum(Path(item["file_information"]["path"]), item["integrity"]["checksum_value"])
            for item in output["paper_artifacts"]
        )
        source = all(item["source_information"]["source_type"] for item in output["paper_artifacts"])
        checksum = all(len(item["integrity"]["checksum_value"]) == 64 for item in output["paper_artifacts"])
        skill05 = all(item["processing_status"] == "verified" and item["artifact_ref"]["uri"] for item in output["paper_artifacts"])
        return [
            {"name": "paper_identity_consistency", "passed": identity},
            {"name": "pdf_file_integrity", "passed": integrity},
            {"name": "source_completeness", "passed": source},
            {"name": "checksum_presence", "passed": checksum},
            {"name": "skill05_compatibility", "passed": skill05}
        ]

    def _finish(self, result, started):
        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        items = result.get("output", {}).get("paper_artifacts", []) if result.get("output") else []
        event = {
            "skill_name": SKILL_ID, "timestamp": self.clock().isoformat(),
            "paper_id": [v["paper_identity"]["paper_id"] for v in items],
            "doi": [v["paper_identity"]["doi"] for v in items],
            "source_type": [v["source_information"]["source_type"] for v in items],
            "download_attempts": [len(v["download_attempts"]) for v in items],
            "file_path": [v["file_information"]["path"] for v in items],
            "checksum": [v["integrity"]["checksum_value"] for v in items],
            "status": result["status"], "errors": result["errors"],
            "input_hash": result["provenance"]["input_hash"], "output_hash": result["provenance"]["output_hash"]
        }
        try:
            self.logger(event)
        except Exception:
            pass
        return result

    @staticmethod
    def _failure(err, input_hash):
        return {
            "status": "terminal_failure", "output": None, "artifacts": [],
            "self_check": {"passed": False, "checks": [], "score": 0.0},
            "warnings": [], "errors": [err], "metrics": {},
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": None
            },
            "review_requests": []
        }


def execute(request: Mapping[str, Any], **kwargs: Any) -> Dict[str, Any]:
    return PdfAcquisitionSkill(**kwargs).execute(request)
