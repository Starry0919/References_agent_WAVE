"""The Simulation/Demo Workspace sub-application (查缺补漏04): every content
router the real Workspace UI calls (projects, orchestrator, diagnosis,
designs, engineering_design, scientific_evaluation, virtual_cell,
experiments, learning) is reused UNMODIFIED here - zero duplicated business
logic, zero risk of the simulation surface drifting from the real,
already-tested one. The only difference is which database session each
endpoint gets: this sub-app overrides `get_db_session` (the exact
dependency every one of those routers already declares via
`Depends(get_db_session)`) to yield from the separate simulation engine
instead of `harness.db`'s.

Mounted at `/api/simulation` in `harness/server.py`, so effective paths are
e.g. `/api/simulation/api/projects`, `/api/simulation/api/orchestrator/runs`
- a real user's browser (or this repo's own frontend, once it switches its
API base path while inside `/simulation/*` routes - see
`frontend/src/api/client.ts`) can list/create/mutate objects here without
ever touching the real project ledger, because FastAPI resolves this
sub-app's dependency overrides independently of the parent app's.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException

from harness.api import deps as deps_module
from harness.api import designs as designs_api
from harness.api import diagnosis as diagnosis_api
from harness.api import engineering_design as engineering_design_api
from harness.api import experiments as experiments_api
from harness.api import learning as learning_api
from harness.api import orchestrator as orchestrator_api
from harness.api import projects as projects_api
from harness.api import scientific_evaluation as scientific_evaluation_api
from harness.api import virtual_cell as virtual_cell_api
from harness.simulation_demo.db import bootstrap_simulation_schema, get_simulation_db_session, simulation_session_scope
from harness.simulation_demo.seed import DEMO_PROJECT_NAME, find_existing_demo_project, run_synthetic_simulation_flow, seed_demo_if_needed

admin_router = APIRouter(prefix="/admin", tags=["simulation-admin"])


class _TestClientAdapter:
    """Wraps `fastapi.testclient.TestClient` bound to THIS sub-app - the
    exact same interface `run_synthetic_simulation_flow` drives in
    `tests/orchestrator/test_synthetic_simulation_full_dbtl_flow.py`."""

    def __init__(self) -> None:
        from fastapi.testclient import TestClient

        self._client = TestClient(simulation_app)

    def get(self, path: str) -> Any:
        return self._client.get(path)

    def post(self, path: str, json: dict[str, Any]) -> Any:
        return self._client.post(path, json=json)


@admin_router.get("/status")
def demo_status() -> dict:
    client = _TestClientAdapter()
    existing = find_existing_demo_project(client)
    return {"seeded": existing is not None, "project_id": existing["project_id"] if existing else None, "name": DEMO_PROJECT_NAME}


@admin_router.post("/seed")
def seed_demo() -> dict:
    client = _TestClientAdapter()
    try:
        return seed_demo_if_needed(client, simulation_session_scope)
    except RuntimeError as e:
        raise HTTPException(422, str(e))


@admin_router.post("/reset")
def reset_demo() -> dict:
    """Deletes the demo project (if any) and reseeds fresh - lets a
    teaching/demo session be replayed from scratch without restarting the
    server. Only ever touches the simulation engine's own projects table."""
    from harness.projects import service as proj_svc

    client = _TestClientAdapter()
    existing = find_existing_demo_project(client)
    if existing is not None:
        with simulation_session_scope() as s:
            proj_svc.delete_project(s, project_id=existing["project_id"])
    try:
        result = run_synthetic_simulation_flow(client, simulation_session_scope)
    except RuntimeError as e:
        raise HTTPException(422, str(e))
    return {"reset": True, **result}


def _build_simulation_app() -> FastAPI:
    sub_app = FastAPI(title="Agent Harness - Simulation/Demo Workspace")
    for router in (
        projects_api.router, designs_api.router, experiments_api.router, learning_api.router,
        diagnosis_api.router, engineering_design_api.router, scientific_evaluation_api.router,
        virtual_cell_api.router, orchestrator_api.router,
    ):
        sub_app.include_router(router)
    sub_app.include_router(admin_router)
    sub_app.dependency_overrides[deps_module.get_db_session] = get_simulation_db_session
    return sub_app


simulation_app = _build_simulation_app()
bootstrap_simulation_schema()
