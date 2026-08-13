"""Design lineage traversal over `DesignVersion.parent_version_ids`. Since
`DesignVersion` rows are only ever inserted (never updated) via the
DESIGN_PROPOSED/DESIGN_APPROVED event path, this table alone is a valid,
directly queryable lineage graph - `build_lineage_graph` needs no event
replay to be correct.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.designs.models import DesignVersion


def get_ancestors(session: Session, design_version_id: str, *, max_depth: int = 20) -> list[DesignVersion]:
    """BFS upward through parent_version_ids, deduped and depth-bounded."""
    seen: set[str] = {design_version_id}
    frontier = [design_version_id]
    ancestors: list[DesignVersion] = []
    depth = 0
    while frontier and depth < max_depth:
        next_frontier: list[str] = []
        for vid in frontier:
            row = session.get(DesignVersion, vid)
            if row is None:
                continue
            for parent_id in row.parent_version_ids:
                if parent_id not in seen:
                    seen.add(parent_id)
                    next_frontier.append(parent_id)
                    parent_row = session.get(DesignVersion, parent_id)
                    if parent_row is not None:
                        ancestors.append(parent_row)
        frontier = next_frontier
        depth += 1
    return ancestors


def get_children(session: Session, design_version_id: str) -> list[DesignVersion]:
    row = session.get(DesignVersion, design_version_id)
    if row is None:
        return []
    all_versions = session.execute(select(DesignVersion).where(DesignVersion.project_id == row.project_id)).scalars().all()
    return [v for v in all_versions if design_version_id in v.parent_version_ids]


def build_lineage_graph(session: Session, project_id: str) -> dict:
    """Nodes + child->parent edges for the whole project - directly
    displayable as a Design Lineage Graph view."""
    versions = session.execute(select(DesignVersion).where(DesignVersion.project_id == project_id)).scalars().all()
    nodes = [
        {
            "design_version_id": v.design_version_id,
            "version_label": v.version_label,
            "status": v.status,
            "branch_name": v.branch_name,
        }
        for v in versions
    ]
    edges = [{"child": v.design_version_id, "parent": p} for v in versions for p in v.parent_version_ids]
    return {"project_id": project_id, "nodes": nodes, "edges": edges}
