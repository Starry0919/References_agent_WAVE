"""FastAPI application: HTTP API plus the per-session WebSocket stream."""
from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from harness.agent import run_agent_turn
from harness.api import diagnosis as diagnosis_api
from harness.api import designs as designs_api
from harness.api import engineering_design as engineering_design_api
from harness.api import evaluation_metrics as evaluation_metrics_api
from harness.api import evidence_intelligence as evidence_intelligence_api
from harness.api import experiments as experiments_api
from harness.api import generation as generation_api
from harness.api import golden_set as golden_set_api
from harness.api import ideas as ideas_api
from harness.api import knowledge_distillation as knowledge_distillation_api
from harness.api import learning as learning_api
from harness.api import orchestrator as orchestrator_api
from harness.api import paper_extraction as paper_extraction_api
from harness.api import literature_search as literature_search_api
from harness.api import skill07_gold as skill07_gold_api
from harness.api import projects as projects_api
from harness.api import scientific_evaluation as scientific_evaluation_api
from harness.api import scientific_runtime as scientific_runtime_api
from harness.api import translation as translation_api
from harness.api import virtual_cell as virtual_cell_api
from harness.api import world_model as world_model_api
from harness.bootstrap import bootstrap_schema
from harness.config import PROJECT_ROOT
from harness.llm import aclose_cached_client
from harness.providers import describe
from harness.sessions import Session, SessionStore
from harness.simulation_demo.app import simulation_app
from harness.tools import all_tools
from harness.tools.base import shutdown_tool_pool
from harness.tools.loader import load_all_tools
from harness.workflow import checkpoint as workflow_checkpoint
from harness.workflow.controller import WorkflowController
from harness.workflow.synbio_stages import build_controller

logger = logging.getLogger(__name__)

WS_PING_INTERVAL_S = 20.0


def _shutdown_tool_executor(app: FastAPI) -> None:
    """Best-effort 关停工具执行器的线程池(executor.shutdown 此前没有调用方)。

    兼容两种形态:harness/tools/executor.py 若提供模块级 shutdown() 则直接
    调用;否则经由 lifespan 里构建的 WorkflowController 拿到 ToolExecutor
    实例来关。executor.py 正由另一处改动并行演进,这里对两种形态都容忍。
    """
    try:
        from harness.tools import executor as tools_executor

        module_shutdown = getattr(tools_executor, "shutdown", None)
        if callable(module_shutdown):
            module_shutdown()
            return
        controller = getattr(app.state, "workflow_controller", None)
        tool_executor = getattr(controller, "_tools", None)
        if tool_executor is not None and hasattr(tool_executor, "shutdown"):
            tool_executor.shutdown()
    except Exception:
        logger.exception("tool executor shutdown failed")


class MessageBody(BaseModel):
    """Request body for POST /api/sessions/{id}/messages."""

    content: str


class ApprovalBody(BaseModel):
    """Request body for POST /api/workflow-runs/{run_id}/approve - the
    "real" human-approval channel (doc 5.7): distinct from a chat-text
    answer, carries an explicit approver identity and decision."""

    decision_id: str
    approver: str
    decision: str  # "approved" | "rejected"
    risk_reason: str = ""


def _session_summary(session: Session) -> dict:
    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "status": session.status,
        "event_count": len(session.events),
    }


def _get_session_or_404(request: Request, session_id: str) -> Session:
    store: SessionStore = request.app.state.store
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return session


def create_app() -> FastAPI:
    """Build the FastAPI app with a lifespan that loads tools and sessions."""

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        errors = load_all_tools()
        for error in errors:
            logger.warning("tool load error: %s", error)
        app.state.store = SessionStore()
        app.state.workflow_controller = build_controller()
        applied_migrations = bootstrap_schema()
        if applied_migrations:
            logger.info("applied project-ledger migrations: %s", applied_migrations)
        (PROJECT_ROOT / "workspace").mkdir(parents=True, exist_ok=True)
        info = describe()
        logger.info(
            "agent harness ready: %d tool(s), provider=%s, model=%s",
            len(all_tools()),
            info["provider"],
            info["model"],
        )
        yield
        # 关停顺序:先 flush 并关闭全部会话文件句柄(保证 run_finished
        # 之后的日志完整落盘),再释放 LLM 连接池,最后停工具线程池。
        # 每步 best-effort:一步失败不阻断其余清理。
        try:
            app.state.store.close_all()
        except Exception:
            logger.exception("session store cleanup failed during shutdown")
        await aclose_cached_client()
        _shutdown_tool_executor(app)
        # 聊天循环的同步工具专用池(base.py 模块级)也一并关停;已被泄漏
        # 占用的线程不等待(wait=False),避免卡住退出。
        shutdown_tool_pool()

    app = FastAPI(title="Agent Harness", lifespan=lifespan)

    # Backend content localization (harness/i18n.py): the frontend sends its
    # active UI language on every request via X-Locale; this is the one
    # place that reads it, so every route/service/generator downstream can
    # call `harness.i18n.t(...)` without threading a locale parameter
    # through each intermediate call site.
    @app.middleware("http")
    async def _locale_middleware(request: Request, call_next):
        from harness.i18n import set_locale

        set_locale(request.headers.get("x-locale"))
        return await call_next(request)

    # Problem 02: the persistent DBTL project ledger's full API surface -
    # additive, independent of the chat-session routes below (doc 16).
    app.include_router(projects_api.router)
    app.include_router(learning_api.router)
    app.include_router(generation_api.router)
    app.include_router(ideas_api.router)
    app.include_router(paper_extraction_api.router)
    app.include_router(literature_search_api.router)
    app.include_router(skill07_gold_api.router)
    app.include_router(evidence_intelligence_api.router)
    app.include_router(world_model_api.router)
    app.include_router(scientific_runtime_api.router)
    # LLM-backed translation fallback for i18n.tsx keys with no curated
    # zh-CN entry yet (harness/translation/service.py) - see harness/i18n.py
    # for the (separate) generated-narrative locale mechanism.
    app.include_router(translation_api.router)
    # Sibling module to paper_extraction: textbook/monograph/guideline ->
    # evidence-gated Engineering Principle / Decision Rule / Design Pattern
    # knowledge objects, distinct from paper_extraction's ExperimentalCase
    # objects but sharing the KnowledgeObject common layer (see
    # harness/knowledge_distillation/SKILL.md 1.1) so Step11 can link them.
    app.include_router(knowledge_distillation_api.router)
    # Core idea workflow: diagnosis explains whether/why an extracted idea
    # is credible; engineering design turns an accepted idea into an
    # actionable intervention.
    app.include_router(diagnosis_api.router)
    app.include_router(engineering_design_api.router)
    app.include_router(designs_api.router)
    # Remounted (Round 2, per user instruction "API重新挂回来"): these five
    # were fully implemented and tested at the service layer but never
    # wired into the live app - `removed_api_module` below silently 404'd
    # every request to them. That mismatch was the root cause of ~22 of the
    # 26 failing tests found in the Round 2 test audit.
    app.include_router(virtual_cell_api.router)
    app.include_router(orchestrator_api.router)
    app.include_router(golden_set_api.router)
    app.include_router(evaluation_metrics_api.router)
    app.include_router(scientific_evaluation_api.router)
    app.include_router(experiments_api.router)
    # Simulation/Demo Workspace sub-app (harness/simulation_demo/app.py):
    # reuses the real content routers unmodified against a separate DB
    # session, so a teaching/demo run never touches the real project
    # ledger. The sub-app was fully built but never mounted here, which
    # silently 404'd every /api/simulation/* request via
    # `removed_api_module` below.
    app.mount("/api/simulation", simulation_app)

    # The prior single-file chat remains available for compatibility.
    @app.get("/legacy/chat")
    async def legacy_chat_page() -> FileResponse:
        return FileResponse(PROJECT_ROOT / "web" / "index.html")

    @app.get("/api/health")
    async def health() -> dict:
        info = describe()
        return {
            "ok": True,
            "provider": info["provider"],
            "model": info["model"],
            "tools": len(all_tools()),
        }

    @app.get("/api/tools")
    async def list_tools() -> dict:
        return {
            "tools": [
                {
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": spec.parameters,
                    "source": spec.source,
                }
                for spec in all_tools()
            ]
        }

    @app.get("/api/workflow-runs")
    async def list_workflow_runs() -> dict:
        """Additive endpoint (doc 5.10): structured Workflow Engine run
        state for a frontend to render stages/gates/decisions from, not
        prose. Does not touch or depend on the chat session API above."""
        summaries = []
        for run_id in workflow_checkpoint.list_run_ids():
            run = workflow_checkpoint.load(run_id)
            if run is None:
                continue
            summaries.append(
                {
                    "run_id": run.run_id,
                    "project_id": run.project_id,
                    "status": run.status.value,
                    "current_stage": run.current_stage,
                    "created_at": run.created_at,
                    "updated_at": run.updated_at,
                }
            )
        summaries.sort(key=lambda s: s["created_at"], reverse=True)
        return {"runs": summaries}

    @app.get("/api/workflow-runs/{run_id}")
    async def get_workflow_run(run_id: str) -> dict:
        run = workflow_checkpoint.load(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="workflow run not found")
        return run.model_dump(mode="json")

    @app.post("/api/workflow-runs/{run_id}/approve")
    async def approve_workflow_run(run_id: str, body: ApprovalBody, request: Request) -> dict:
        controller: WorkflowController = request.app.state.workflow_controller
        run = controller.resume(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="workflow run not found")
        if body.decision not in ("approved", "rejected"):
            raise HTTPException(status_code=422, detail="decision must be 'approved' or 'rejected'")
        run = controller.submit_approval(
            run,
            decision_id=body.decision_id,
            approver=body.approver,
            decision=body.decision,
            risk_reason=body.risk_reason,
        )
        run = controller.run_to_completion_or_pause(run, max_steps=30)
        return run.model_dump(mode="json")

    @app.get("/api/sessions")
    async def list_sessions(request: Request) -> dict:
        store: SessionStore = request.app.state.store
        return {"sessions": [_session_summary(s) for s in store.list()]}

    @app.post("/api/sessions")
    async def create_session(request: Request) -> dict:
        store: SessionStore = request.app.state.store
        return _session_summary(store.create())

    @app.get("/api/sessions/{session_id}")
    async def get_session(session_id: str, request: Request) -> dict:
        session = _get_session_or_404(request, session_id)
        return {
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at,
            "status": session.status,
            "events": [event.to_dict() for event in session.events],
        }

    @app.delete("/api/sessions/{session_id}")
    async def delete_session(session_id: str, request: Request) -> dict:
        session = _get_session_or_404(request, session_id)
        if session.status == "running":
            raise HTTPException(status_code=409, detail="session is running")
        store: SessionStore = request.app.state.store
        store.delete(session_id)
        return {"deleted": True}

    @app.post("/api/sessions/{session_id}/messages", status_code=202)
    async def post_message(session_id: str, body: MessageBody, request: Request) -> dict:
        session = _get_session_or_404(request, session_id)
        if not body.content or not body.content.strip():
            raise HTTPException(status_code=422, detail="content must not be empty")
        if session.status == "running":
            raise HTTPException(status_code=409, detail="session is busy")
        store: SessionStore = request.app.state.store
        session.status = "running"
        task = asyncio.create_task(run_agent_turn(store, session, body.content))
        session.current_task = task

        def _on_task_done(
            done_task: asyncio.Task, s: Session = session, content: str = body.content
        ) -> None:
            if done_task.cancelled():
                # Cancelled before run_agent_turn ever got an execution slice
                # (stop racing the 202): the coroutine never ran, so record
                # the accepted message and a terminal event here instead of
                # letting it vanish without a timeline trace.
                try:
                    s.emit("user_message", {"content": content})
                    store.append_message(s, {"role": "user", "content": content})
                    store.maybe_set_title(s, content)
                    s.emit("run_finished", {"status": "stopped"})
                except Exception:
                    logger.exception(
                        "could not record pre-start-cancelled message for session %s",
                        s.id,
                    )
            elif done_task.exception() is not None:
                # run_agent_turn is designed never to raise; retrieve anything
                # unexpected instead of leaving asyncio "never retrieved" noise.
                logger.error(
                    "agent task for session %s raised: %r", s.id, done_task.exception()
                )
            if s.current_task is done_task:
                s.current_task = None
                s.status = "idle"

        task.add_done_callback(_on_task_done)
        return {"accepted": True}

    @app.post("/api/sessions/{session_id}/stop")
    async def stop_session(session_id: str, request: Request) -> dict:
        session = _get_session_or_404(request, session_id)
        task = session.current_task
        if session.status == "running" and task is not None and not task.done():
            task.cancel()
            return {"stopped": True}
        return {"stopped": False}

    @app.websocket("/ws/{session_id}")
    async def ws_events(websocket: WebSocket, session_id: str) -> None:
        store: SessionStore = websocket.app.state.store
        session = store.get(session_id)
        if session is None:
            await websocket.close(code=1008)
            return
        await websocket.accept()
        try:
            assert session.bus is not None
            async with session.bus.subscribe() as queue:
                # Replay the backlog first (subscribed already, so nothing is
                # lost in between; clients dedup by seq).
                for event in list(session.events):
                    await websocket.send_json(event.to_dict())
                while True:
                    try:
                        event = await asyncio.wait_for(
                            queue.get(), timeout=WS_PING_INTERVAL_S
                        )
                    except asyncio.TimeoutError:
                        if store.get(session_id) is not session:
                            # Session deleted while we were watching: close so
                            # the client does not keep a ghost connection.
                            await websocket.close(code=1001)
                            return
                        await websocket.send_json({"type": "ping"})
                        continue
                    if event is None:
                        # The bus dropped this subscriber (queue overflow):
                        # close so the client reconnects and resyncs by seq.
                        await websocket.close(code=1013)
                        return
                    await websocket.send_json(event.to_dict())
        except WebSocketDisconnect:
            pass
        except Exception:
            logger.debug("websocket for session %s closed", session_id, exc_info=True)

    @app.api_route("/api/{removed_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def removed_api_module(removed_path: str) -> None:
        """Never let the SPA turn a removed API into a misleading HTTP 200."""
        raise HTTPException(status_code=404, detail=f"API module not available: {removed_path}")

    # Simplified idea-extraction frontend:
    # the real product surface is the built SPA in frontend/dist, served
    # same-origin (no CORS needed - Repository Truth Audit found no
    # CORSMiddleware anywhere in this backend). Registered LAST: the
    # catch-all path route must never shadow any /api, /ws or /legacy
    # route defined above.
    _frontend_dist = PROJECT_ROOT / "frontend" / "dist"
    if _frontend_dist.is_dir():
        app.mount("/assets", StaticFiles(directory=_frontend_dist / "assets"), name="frontend-assets")

        @app.get("/{full_path:path}")
        async def spa_fallback(full_path: str) -> FileResponse:
            """Client-side routes (prompt §6.3 deep links) all resolve to
            the same SPA shell; React Router takes it from there."""
            candidate = _frontend_dist / full_path
            if full_path and candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(_frontend_dist / "index.html")

    else:

        @app.get("/")
        async def frontend_not_built() -> dict:
            return {
                "ok": False,
                "detail": (
                    "frontend/dist not found - run `npm install && npm run build` in frontend/, "
                    "or use /legacy/chat for the original single-page UI."
                ),
            }

    return app


app = create_app()
