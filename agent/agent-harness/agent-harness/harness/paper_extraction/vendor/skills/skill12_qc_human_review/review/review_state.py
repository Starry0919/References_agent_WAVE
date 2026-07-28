ALLOWED = {
    "pending": {"in_review", "approved", "rejected", "revision_required"},
    "in_review": {"approved", "rejected", "revision_required"},
    "approved": {"closed"}, "rejected": {"closed"}, "revision_required": {"in_review", "closed"}, "closed": set(),
}
def valid_transition(current, target):
    return target in ALLOWED.get(current, set())
