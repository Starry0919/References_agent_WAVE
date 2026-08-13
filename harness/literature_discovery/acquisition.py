from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

import httpx

from .models import AcquisitionRecord, AcquisitionState, PaperCandidate, utc_now
from .resolvers import ResolverRouter
from .pdf_identity import verify_pdf_identity


class AcquisitionManager:
    def __init__(self, storage_dir: Path, timeout: float = 30, max_bytes: int = 50 * 1024 * 1024, min_bytes: int = 1024, client: httpx.Client | None = None):
        self.storage_dir = storage_dir
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.min_bytes = min_bytes
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=True, headers={"User-Agent": "WAVE-Literature/0.1"})

    def acquire(self, candidate: PaperCandidate) -> AcquisitionRecord:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        key = candidate.doi or candidate.candidate_id
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in key)[:120]
        target = self.storage_dir / f"{safe}.pdf"
        if target.is_file() and validate_pdf(target.read_bytes(), self.min_bytes):
            data = target.read_bytes()
            identity=verify_pdf_identity(candidate,target)
            if identity["status"]=="MISMATCH":
                target.unlink(missing_ok=True)
            else:
                return AcquisitionRecord(state=AcquisitionState.ALREADY_PRESENT, local_path=str(target.resolve()), sha256=hashlib.sha256(data).hexdigest(), byte_size=len(data), attempted_at=utc_now(),identity_verification=identity,attempts=[{"source":"local_cache","status":"valid_pdf_reused"}])
        resolver_events = []
        if candidate.doi:
            locations, resolver_events = ResolverRouter(client=self.client).resolve(candidate.doi)
            candidate.oa_urls = list(dict.fromkeys([*candidate.oa_urls, *(x.url for x in locations)]))
        else:
            candidate.oa_urls = self._resolve_urls(candidate)
        if not candidate.oa_urls:
            return AcquisitionRecord(state=AcquisitionState.NO_OA_SOURCE, failure_reason="PAYWALL_OR_NO_LEGAL_FULLTEXT", attempted_at=utc_now(), attempts=resolver_events)
        failures: list[str] = []
        for url in candidate.oa_urls:
            try:
                with self.client.stream("GET", url, headers={"Accept": "application/pdf"}) as response:
                    response.raise_for_status()
                    content_type = response.headers.get("content-type", "").casefold()
                    fd, tmp_name = tempfile.mkstemp(prefix="wave_pdf_", suffix=".tmp", dir=self.storage_dir)
                    size = 0
                    try:
                        with os.fdopen(fd, "wb") as fh:
                            for chunk in response.iter_bytes():
                                size += len(chunk)
                                if size > self.max_bytes:
                                    raise ValueError("PDF exceeds configured maximum")
                                fh.write(chunk)
                        tmp = Path(tmp_name)
                        data = tmp.read_bytes()
                        if "html" in content_type or not validate_pdf(data, self.min_bytes):
                            failures.append("NOT_PDF")
                            tmp.unlink(missing_ok=True)
                            continue
                        tmp.replace(target)
                        identity=verify_pdf_identity(candidate,target)
                        resolver_events.append({"source":"download","url":url,"status":"downloaded","bytes":len(data)})
                        if identity["status"]=="MISMATCH":
                            target.unlink(missing_ok=True)
                            resolver_events[-1]["status"]="identity_mismatch";failures.append("PDF_IDENTITY_MISMATCH");continue
                        return AcquisitionRecord(state=AcquisitionState.ACQUIRED, source_url=url, local_path=str(target.resolve()), sha256=hashlib.sha256(data).hexdigest(), byte_size=len(data), attempted_at=utc_now(),attempts=resolver_events,identity_verification=identity)
                    except Exception:
                        Path(tmp_name).unlink(missing_ok=True)
                        raise
            except httpx.TimeoutException:
                failures.append("TIMEOUT")
            except (httpx.HTTPError, ValueError):
                failures.append("HTTP_ERROR")
        reason = failures[-1] if failures else "RESOLUTION_FAILED"
        state = {"TIMEOUT": AcquisitionState.TIMEOUT, "NOT_PDF": AcquisitionState.NOT_PDF, "HTTP_ERROR": AcquisitionState.HTTP_ERROR}.get(reason, AcquisitionState.RESOLUTION_FAILED)
        return AcquisitionRecord(state=state, failure_reason=reason, attempted_at=utc_now(),attempts=resolver_events)

    def _resolve_urls(self, candidate: PaperCandidate) -> list[str]:
        urls = list(dict.fromkeys(candidate.oa_urls))
        if urls or not candidate.doi:
            return urls
        try:
            response = self.client.get(f"https://api.openalex.org/works/https://doi.org/{candidate.doi}")
            response.raise_for_status()
            data = response.json()
            for location in [data.get("best_oa_location") or {}, *(data.get("locations") or [])]:
                url = location.get("pdf_url")
                if url and url not in urls:
                    urls.append(url)
        except (httpx.HTTPError, ValueError):
            return urls
        return urls


def validate_pdf(data: bytes, min_bytes: int = 1024) -> bool:
    if len(data) < min_bytes or not data.startswith(b"%PDF-"):
        return False
    prefix = data[:1024].lstrip().lower()
    if prefix.startswith(b"<!doctype html") or b"<html" in prefix:
        return False
    return b"%%EOF" in data[-4096:]


def handoff_manifest(candidates: list[PaperCandidate], project_id: str | None = None) -> dict:
    acquired = [c for c in candidates if c.acquisition.state in {AcquisitionState.ACQUIRED, AcquisitionState.ALREADY_PRESENT} and c.acquisition.local_path]
    return {
        "contract_version": "wave-literature-handoff/1.0",
        "project_id": project_id,
        "papers": [
            {
                "candidate_id": c.candidate_id, "title": c.canonical_title, "doi": c.doi,
                "local_pdf": c.acquisition.local_path, "sha256": c.acquisition.sha256,
                "source_url": c.acquisition.source_url,
                "relevance": c.relevance.model_dump(mode="json") if c.relevance else None,
                "provenance": [r.model_dump(mode="json") for r in c.source_records],
                "processing_state": "ready_for_existing_ingest",
            } for c in acquired
        ],
        "existing_pipeline_payloads": [
            {
                "source_type": "upload", "project_id": project_id,
                "user_request": f"Extract experimental design from discovered paper: {c.canonical_title}",
                "organism": "Escherichia coli", "strain": "K-12",
                # Existing build_request/workflow expects literature_source.files
                # to be a list of path strings, not metadata objects.
                "files": [c.acquisition.local_path],
                "max_papers": 1,
            } for c in acquired
        ],
    }
