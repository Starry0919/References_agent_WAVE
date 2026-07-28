def build(details,evidence,quality,k12,risk,governance,source_payload,labels):
    return {"level":3,"default_state":"expanded","labels":{"what":labels["what"],"why":labels["why"],"how":labels["how"],
            "evidence":labels["evidence"],"risk":labels["risk"]},"detail_panels":details,"evidence":evidence,
            "quality":quality,"k12_adaptation":k12,"risk":risk,"governance":governance,"source_payload":source_payload}
