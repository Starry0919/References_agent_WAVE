class ReviewService:
    def collect(self, artifacts):
        return [r for a in artifacts for r in (a.get("content") or {}).get("review_items", [])] if artifacts else []

    def nonblocking_state(self, has_review, failed):
        return "FAILED" if failed else "WAITING_REVIEW" if has_review else "COMPLETED"
