try:
    from ..schema import stable_id, now_iso
except ImportError:
    from schema import stable_id, now_iso
def build(artifact_id, event_type, actor, action, before, after, reason, evidence=None):
    timestamp = now_iso()
    return {"event_id": stable_id("audit", artifact_id, event_type, timestamp), "event_type": event_type,
            "artifact_id": artifact_id, "actor": actor, "timestamp": timestamp, "action": action,
            "before": before, "after": after, "reason": reason, "evidence": evidence or []}
