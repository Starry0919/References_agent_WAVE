import unittest
from helpers import Store, request, content
from skill import execute
class AuditTest(unittest.TestCase):
    def test_human_modify_preserves_before_after(self):
        store=Store(); action={"action":"modify","actor_type":"human","actor_id":"reviewer-1","before":{"note":"old"},"after":{"note":"new"},"reason":"clarify note"}
        r=execute(request(content(evidence=False),action),logger=lambda _:None,event_store=store)
        event=r["output"]["audit_event"]
        self.assertEqual(event["before"],{"note":"old"}); self.assertEqual(event["after"],{"note":"new"})
        self.assertEqual(r["output"]["review_task"]["status"],"revision_required")
        self.assertEqual(len(store.events),1)
if __name__=="__main__": unittest.main()
