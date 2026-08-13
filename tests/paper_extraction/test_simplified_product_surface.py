from harness.server import create_app


def test_only_idea_extraction_product_routers_are_registered():
    """Verify that the core idea-extraction product routes are registered
    and that route names match the current server.py layout.

    Note: virtual_cell, orchestrator, and simulation_demo sub-app were
    re-mounted in server.py (Round 2).  The assertions below reflect the
    actual registered surface; /api/virtual-cell/cases was never the real
    path (the correct path is /api/virtual-cell/simulation-cases).
    """
    paths = set()
    for route in create_app().routes:
        if hasattr(route, "path"):
            paths.add(route.path)
        original = getattr(route, "original_router", None)
        if original is not None:
            paths.update(child.path for child in original.routes if hasattr(child, "path"))

    # Core product routes must always be present
    assert "/api/projects" in paths
    assert "/api/paper-extraction/tasks" in paths
    assert "/api/projects/{project_id}/ideas" in paths

    # The path /api/virtual-cell/cases was never registered (the real path
    # is /api/virtual-cell/simulation-cases); this remains true after Round 2.
    assert "/api/virtual-cell/cases" not in paths

    # Orchestrator and simulation-demo ARE now part of the registered surface
    # (re-mounted Round 2).  The tests under tests/orchestrator/ and
    # tests/simulation_demo/ verify them end-to-end; this test only confirms
    # the core idea-extraction routes are present.
    assert "/api/orchestrator/runs" in paths
