def build(summary,cards,governance,labels):
    return {"level":1,"default_state":"collapsed","labels":{"summary":labels["summary"],"steps":labels["steps"],"governance":labels["governance"]},
            "summary":summary,"steps":cards,"governance_badge":{"qc_status":governance["qc_status"],"review_status":governance["review_status"]}}
