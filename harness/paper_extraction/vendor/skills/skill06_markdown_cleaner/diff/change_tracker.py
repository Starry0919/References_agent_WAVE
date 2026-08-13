class ChangeTracker:
    def __init__(self):
        self.changes = []

    def add(self, change_type, location, original, cleaned, reason):
        if original == cleaned:
            return
        self.changes.append({
            "change_id": f"change_{len(self.changes) + 1:04d}",
            "type": change_type, "location": location,
            "original": original, "cleaned": cleaned, "reason": reason
        })

