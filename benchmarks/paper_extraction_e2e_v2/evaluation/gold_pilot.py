from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from harness.paper_extraction.gold_agreement import agreement_report
from harness.paper_extraction.gold_infrastructure import PACKAGES, RELEASES, load_draft

BASE=Path(__file__).resolve().parents[1]
PILOT=json.loads((BASE/'splits/gold_calibration_pilot.json').read_text(encoding='utf-8'))

def run():
    packages=[x for split in ('development','holdout') for x in PILOT[split]]
    per=[]; iaa=[]
    for item in packages:
        pid=item['package_id']; a=load_draft(pid,'ANNOTATOR_A'); b=load_draft(pid,'ANNOTATOR_B'); adj=load_draft(pid,'ADJUDICATOR')
        iaa.append({'package_id':pid,**agreement_report(a,b)})
        per.append({'package_id':pid,'split':'holdout' if item in PILOT['holdout'] else 'development',
          'reviewer_a_complete':a.get('review_state') in {'HUMAN_REVIEWED','READY_FOR_ADJUDICATION'},
          'reviewer_b_complete':b.get('review_state') in {'HUMAN_REVIEWED','READY_FOR_ADJUDICATION'},
          'ready_for_adjudication':a.get('review_state')=='HUMAN_REVIEWED' and b.get('review_state')=='HUMAN_REVIEWED',
          'adjudicated':adj.get('review_state') in {'ADJUDICATED_GOLD','FROZEN_GOLD'},'experiments':len(adj.get('experiments',[])),'claims':len(adj.get('claims',[])),'evidence_bundles':len(adj.get('evidence',[])),'ddr':len(adj.get('ddr',[])),'admissions':len(adj.get('admissions',[]))})
    progress={'pilot_version':PILOT['version'],'papers':len(per),'reviewer_a_complete':sum(x['reviewer_a_complete'] for x in per),'reviewer_b_complete':sum(x['reviewer_b_complete'] for x in per),'ready_for_adjudication':sum(x['ready_for_adjudication'] for x in per),'adjudicated':sum(x['adjudicated'] for x in per),'sealed_releases':len(list(RELEASES.glob('skill07-gold-v*'))),'experiments':sum(x['experiments'] for x in per),'claims':sum(x['claims'] for x in per),'evidence_bundles':sum(x['evidence_bundles'] for x in per),'ddr':sum(x['ddr'] for x in per),'admissions':sum(x['admissions'] for x in per),'records':per}
    (BASE/'reports/gold_pilot_progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
    iaa_result={'pilot_version':PILOT['version'],'status':'NOT_ESTIMABLE' if not any(x['status']=='MEASURED_HUMAN' for x in iaa) else 'PARTIALLY_MEASURED','papers':iaa}
    (BASE/'reports/gold_pilot_iaa.json').write_text(json.dumps(iaa_result,ensure_ascii=False,indent=2),encoding='utf-8')
    return progress,iaa_result
if __name__=='__main__': print(json.dumps(run(),ensure_ascii=False))
