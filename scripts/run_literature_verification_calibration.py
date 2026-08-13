import argparse, json
from pathlib import Path
from harness.literature_verification.gold import evaluate

ROOT = Path(__file__).resolve().parents[1]; DATA = ROOT / "artifacts/data/literature"
parser = argparse.ArgumentParser(); parser.add_argument("--gold", default=str(DATA / "literature_verification_gold_batch_v1.json")); args = parser.parse_args()
data = json.loads(Path(args.gold).read_text(encoding="utf-8")); rows = []
for item in data["papers"]:
    rows.append({"paper_id": item["paper_id"], "gold": item.get("adjudicated") or {}, "prediction": item.get("machine_prediction")})
out = evaluate(rows, {x["paper_id"]: x.get("machine_score", 0) for x in data["papers"]})
out["annotation_disagreements"] = sum(bool(x.get("annotator_A") and x.get("annotator_B") and x["annotator_A"] != x["annotator_B"]) for x in data["papers"])
(DATA / "literature_verification_calibration_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
