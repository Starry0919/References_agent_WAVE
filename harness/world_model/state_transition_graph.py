"""Component: State Transition Graph (dynamic engineering relationships,
Module 4 prompt §12). Nodes are states, edges are `StateTransitionRecord`s.
A state node is identified by its real `snapshot_id` when the transition
references one (so multiple transitions sharing the same measured state
correctly collapse into one node); a transition with no snapshot gets its
own isolated initial/final node pair rather than being guessed into merging
with an unrelated transition's state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from harness.world_model.models import StateTransitionRecord
from harness.world_model.transitions import list_transitions


@dataclass
class StateNode:
    id: str
    label: str
    snapshot_id: str | None
    entities_involved: list[str] = field(default_factory=list)


@dataclass
class TransitionEdge:
    source: str
    target: str
    transition_id: str
    perturbation_type: str
    origin: str
    status: str
    outcome: str


@dataclass
class StateTransitionGraph:
    nodes: list[StateNode] = field(default_factory=list)
    edges: list[TransitionEdge] = field(default_factory=list)


def _state_node(state: dict[str, Any], transition_id: str, which: str) -> StateNode:
    snapshot_id = state.get("snapshot_id")
    node_id = f"state:{snapshot_id}" if snapshot_id else f"state:{transition_id}:{which}"
    return StateNode(id=node_id, label=state.get("summary") or "(no summary recorded)", snapshot_id=snapshot_id, entities_involved=list(state.get("entities_involved") or []))


def build_state_transition_graph(
    session: Session, *, project_id: str | None = None, entity_id: str | None = None, origin: str | None = None, limit: int = 50,
) -> StateTransitionGraph:
    transitions: list[StateTransitionRecord] = list_transitions(session, project_id=project_id, entity_id=entity_id, origin=origin, limit=limit)

    nodes_by_id: dict[str, StateNode] = {}
    edges: list[TransitionEdge] = []
    for t in transitions:
        initial = _state_node(t.initial_state, t.transition_id, "initial")
        final = _state_node(t.final_state, t.transition_id, "final")
        nodes_by_id.setdefault(initial.id, initial)
        nodes_by_id.setdefault(final.id, final)
        edges.append(TransitionEdge(
            source=initial.id, target=final.id, transition_id=t.transition_id,
            perturbation_type=t.perturbation.get("type", "unknown"), origin=t.origin, status=t.status, outcome=t.outcome,
        ))

    return StateTransitionGraph(nodes=list(nodes_by_id.values()), edges=edges)
