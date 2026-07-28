from harness.server import create_app


def test_only_idea_extraction_product_routers_are_registered():
    paths = set()
    for route in create_app().routes:
        if hasattr(route, "path"):
            paths.add(route.path)
        original = getattr(route, "original_router", None)
        if original is not None:
            paths.update(child.path for child in original.routes if hasattr(child, "path"))
    assert "/api/projects" in paths
    assert "/api/paper-extraction/tasks" in paths
    assert "/api/projects/{project_id}/ideas" in paths

    assert "/api/virtual-cell/cases" not in paths
    assert "/api/orchestrator/runs" not in paths
    assert not any(path.startswith("/api/simulation") for path in paths)
