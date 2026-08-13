"""Temporary analysis script."""
import sys
sys.path.insert(0, '.')

from harness.workflow.synbio_stages import build_controller
from harness.workflow.contracts import (
    EngineeringDecision, TargetEntity, TargetEntityType, OperationType, EvidenceRecord
)

ctrl = build_controller()

# --- Case 1: normal tryptophan run ---
run = ctrl.create_run('Improve E. coli K-12 L-tryptophan production from glucose')
run = ctrl.run_to_completion_or_pause(run, max_steps=30)
print("=== Case 1: normal tryptophan ===")
print(f"  status={run.status.value}  stage={run.current_stage}")
print(f"  stage_records={len(run.stage_records)}")
print(f"  decisions total={len(run.engineering_decisions)}")
for d in run.engineering_decisions:
    print(f"    {d.target_entity.canonical_id} / {d.operation.value} / {d.status.value} / conf={d.confidence}")
print()

# --- Case 2: missing product -> waiting_user ---
run2 = ctrl.create_run('Improve biosensor circuit in E. coli')
run2 = ctrl.run_to_completion_or_pause(run2, max_steps=30)
print("=== Case 2: missing product ===")
print(f"  status={run2.status.value}  stage={run2.current_stage}")
if run2.pending_request:
    print(f"  pending_kind={run2.pending_request.kind.value}")
    print(f"  question={run2.pending_request.question}")
print()

# --- Case 3: essential gene forced essential-gate path ---
ctrl3 = build_controller()
run3 = ctrl3.create_run('Improve E. coli tryptophan')
# advance through INTAKE -> BOTTLENECK_PRIORITIZATION (6 stages)
for _ in range(6):
    run3 = ctrl3.advance(run3)
print(f"after 6 advances: stage={run3.current_stage}")

# inject murA knockout to force essential-gene gate
evid = EvidenceRecord(action_source='unknown', evidence_status='reference_available', confidence='high')
cand = EngineeringDecision(
    target_entity=TargetEntity(type=TargetEntityType.gene, canonical_id='murA', display_name='murA'),
    operation=OperationType.knockout,
    mechanism='testing essential gene gate',
    expected_effect='test',
    evidence_record_ids=[evid.evidence_record_id],
)
run3.evidence_records.append(evid)
run3.candidate_designs.append(cand)

run3 = ctrl3.advance(run3)  # ENGINEERING_STRATEGY_GENERATION
print(f"after ESG: stage={run3.current_stage}  status={run3.status.value}  candidates={len(run3.candidate_designs)}")

run3 = ctrl3.advance(run3)  # MODEL_AND_RULE_VALIDATION
print(f"after MRV: stage={run3.current_stage}  status={run3.status.value}")
if run3.pending_request:
    print(f"  pending_kind={run3.pending_request.kind.value}  decision_id={run3.pending_request.decision_id}")
for d in run3.engineering_decisions:
    print(f"  decision: {d.target_entity.canonical_id} / {d.operation.value} / {d.status.value}")
print()

# --- Case 4: DDR corpus coverage check ---
from workflows.synbio_v1.modules import retriever
ddrs = retriever.load_ddrs()
print(f"=== Case 4: DDR corpus ===")
print(f"  Total DDRs loaded: {len(ddrs)}")
ids = sorted(d['ddr_id'] for d in ddrs)
print(f"  IDs: {ids}")
print()

# --- Case 5: isoprene (DDR-003) ---
run5 = ctrl.create_run('Design E. coli for isoprene production from glucose')
run5 = ctrl.run_to_completion_or_pause(run5, max_steps=30)
print("=== Case 5: isoprene ===")
print(f"  status={run5.status.value}  decisions={len(run5.engineering_decisions)}")
matched = None
for r in run5.stage_records:
    if r.stage_id == 'CONTEXT_AND_EVIDENCE_ACQUISITION':
        matched = r.output.get('matched_ddr')
print(f"  matched_ddr={matched}")
print()

print("=== Analysis complete ===")

# --- Case 8: checkpoint round-trip ---
print("=== Case 8: checkpoint round-trip ===")
from harness.workflow import checkpoint
ctrl8 = build_controller()
run8 = ctrl8.create_run('E. coli L-tryptophan checkpoint test')
run8 = ctrl8.run_to_completion_or_pause(run8, max_steps=30)
loaded8 = checkpoint.load(run8.run_id)
print(f"  run_id matches: {loaded8.run_id == run8.run_id}")
print(f"  status matches: {loaded8.status.value == run8.status.value}")
print(f"  decisions: {len(loaded8.engineering_decisions)} == {len(run8.engineering_decisions)}")
print(f"  report len: {len(loaded8.final_report or '')} == {len(run8.final_report or '')}")


# --- Case 6: essential-gene approval path ---
print("=== Case 9: FastAPI route inventory ===")
from harness.server import create_app
app = create_app()
api_paths = sorted(set(
    r.path for r in app.routes
    if hasattr(r, 'path') and ('/api' in r.path or '/ws' in r.path)
))
print(f"  API/WS routes: {len(api_paths)}")
for p in api_paths:
    print(f"  {p}")

print()
print("=== Case 6: murA approval path ===")
ctrl6 = build_controller()
run6 = ctrl6.create_run('Improve E. coli tryptophan')
for _ in range(6):
    run6 = ctrl6.advance(run6)
evid6 = EvidenceRecord(action_source='unknown', evidence_status='reference_available', confidence='high')
cand6 = EngineeringDecision(
    target_entity=TargetEntity(type=TargetEntityType.gene, canonical_id='murA', display_name='murA'),
    operation=OperationType.knockout,
    mechanism='testing approval path',
    expected_effect='test',
    evidence_record_ids=[evid6.evidence_record_id],
)
run6.evidence_records.append(evid6)
run6.candidate_designs.append(cand6)
run6 = ctrl6.advance(run6)  # ESG
run6 = ctrl6.advance(run6)  # MRV -> waiting_user
print(f"  after MRV: status={run6.status.value}  pending={run6.pending_request.kind.value if run6.pending_request else None}  decision_id={run6.pending_request.decision_id if run6.pending_request else None}")
pending_id = run6.pending_request.decision_id
run6 = ctrl6.submit_approval(run6, decision_id=pending_id, approver='analyst', decision='approved', risk_reason='risk accepted')
run6 = ctrl6.run_to_completion_or_pause(run6, max_steps=30)
print(f"  after approval: status={run6.status.value}  stage={run6.current_stage}")
for d in run6.engineering_decisions:
    if d.target_entity.canonical_id == 'murA':
        print(f"  murA final status: {d.status.value}")

# --- Case 7: FBA tool domain check ---
print("=== Case 7: FBA tool ===")
from harness.workflow.synbio_stages import _fba_flux_analysis, WORKFLOW_TOOLS
from harness.tools.executor import ToolOutOfDomainError, ToolUnavailableError
print(f"  workflow tools: {list(WORKFLOW_TOOLS.keys())}")
try:
    r = _fba_flux_analysis('E. coli K-12', 'L-tryptophan', [('pykF', 'knockout')])
    print(f"  FBA runtime_status: {r.get('runtime_status')}")
    print(f"  FBA model: {r.get('model_name')} v{r.get('model_version')}")
    print(f"  FBA outputs keys: {list(r.get('outputs',{}).keys())}")
    print(f"  FBA domain_flags: {r.get('domain_flags')}")
except ToolUnavailableError as e:
    print(f"  FBA unavailable: {e}")
except ToolOutOfDomainError as e:
    print(f"  FBA out_of_domain: {e}")
    print(f"  FBA outputs keys: {list(r.get('outputs',{}).keys())}")
    print(f"  FBA domain_flags: {r.get('domain_flags')}")
    # test out-of-domain gene
    r2 = None
    ood_msg = None
    try:
        r2 = _fba_flux_analysis('E. coli K-12', 'L-tryptophan', [('trpE', 'overexpression')])
    except ToolOutOfDomainError as ood:
        ood_msg = str(ood)[:120]
    if ood_msg:
        print(f"  trpE correctly raises ToolOutOfDomainError: {ood_msg}")
    else:
        print(f"  trpE OOD result (should not happen): {r2}")
except ToolUnavailableError as e:
    print(f"  FBA unavailable: {e}")
except ToolOutOfDomainError as e:
    print(f"  FBA out_of_domain (pykF unexpectedly): {e}")
except Exception as e:
    import traceback; traceback.print_exc()

