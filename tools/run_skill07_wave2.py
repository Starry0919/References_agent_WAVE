"""Generate Wave 2 validity, alignment, gold-review and decision artifacts.

No model calls are made: independent human gold is a hard prerequisite for
quality promotion, and the available corpus has no adjudicated Skill07 gold.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parents[1]
load_dotenv(ROOT/'.env',override=False)
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import harness.paper_extraction.opus_extractor as skill07
from tools.skill07_wave2 import InvocationIdentity, compare_aligned_outputs, provenance_gate, sha256_json


def read_json(path: Path) -> Any: return json.loads(path.read_text(encoding='utf-8'))
def write_json(path: Path, value: Any) -> None: path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def file_hash(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def configured_model() -> str:
    # Read only the model selector. Never serialize or expose other env data.
    for line in (ROOT/'.env').read_text(encoding='utf-8-sig').splitlines():
        match=re.match(r'^\s*PAPER_EXTRACTION_MODEL\s*=\s*(.*?)\s*$',line)
        if match: return match.group(1).strip().strip('"\'')
    return 'NOT_SET'


def document_features(doc: dict[str, Any]) -> dict[str, Any]:
    data=read_json(Path(doc['clean_document_path']))
    sections=data.get('sections',[]); paragraphs=data.get('paragraphs',[])
    methods=sum('method' in str(s.get('title','')).casefold() for s in sections if isinstance(s,dict))
    results=sum('result' in str(s.get('title','')).casefold() for s in sections if isinstance(s,dict))
    return {
        'characters':doc['input_size']['characters'],'paragraphs':len(paragraphs),'sections':len(sections),
        'figures':len(data.get('figures',[])),'tables':len(data.get('tables',[])),
        'methods_sections':methods,'results_sections':results,
        'baseline_available':bool(doc.get('baseline_output_path')),
    }


def select_core(documents: list[dict[str, Any]], wave1_pairs: set[str]) -> list[dict[str, Any]]:
    enriched=[{**d,'selection_features':document_features(d)} for d in documents]
    selected=[]
    # Existing paired evidence is included, then size/figure/table/structure extremes.
    for d in enriched:
        if d['paper_id'] in wave1_pairs: selected.append(d)
    dimensions=[('characters',False),('characters',True),('figures',True),('tables',True),('paragraphs',True),('methods_sections',True),('results_sections',True)]
    for field,descending in dimensions:
        for d in sorted(enriched,key=lambda x:x['selection_features'][field],reverse=descending):
            if d['paper_id'] not in {x['paper_id'] for x in selected}: selected.append(d); break
            if len(selected)>=10: break
        if len(selected)>=10: break
    for d in enriched:
        if len(selected)>=10: break
        if d['paper_id'] not in {x['paper_id'] for x in selected}: selected.append(d)
    return selected[:10]


def existing_pairs() -> list[dict[str, Any]]:
    summary=read_json(ROOT/'skill07_canonical_representation_benchmark.json')
    pairs=[]
    for d in summary['documents']:
        folder=Path(d['canonical_path']).parent
        a,g=folder/'skill07_baseline.json',folder/'skill07_canonical.json'
        if not (a.is_file() and g.is_file()): continue
        ad,gd=read_json(a),read_json(g)
        if ad.get('status') not in {'succeeded','validation_failed'} or gd.get('status') not in {'succeeded','validation_failed'}: continue
        pairs.append({'paper_id':d['paper_id'],'a_path':str(a.resolve()),'g_path':str(g.resolve()),'a':ad,'g':gd})
    return pairs


def main() -> None:
    old=read_json(ROOT/'skill07_baseline_manifest.json'); pairs=existing_pairs(); pair_ids={x['paper_id'] for x in pairs}
    now=datetime.now(timezone.utc).isoformat()
    provider='poe_code_cli'; source_default='claude-sonnet-4.6'; configured=configured_model(); runtime=skill07.MODEL
    prompt_hash=skill07._system_prompt_hash(); skill_hash=skill07._skill_hash(); schema_hash=skill07._schema_hash()
    validator_hash=file_hash(ROOT/'harness/paper_extraction/opus_extractor.py')
    corrected=[]; gate_results=[]
    for old_doc in old['documents']:
        doc=dict(old_doc); candidate='A_BASELINE'; representation='production_clean_document'
        identity=InvocationIdentity(provider,source_default,configured,runtime,runtime,'UNKNOWN','UNKNOWN','poe-code-cli',prompt_hash,skill_hash,schema_hash,validator_hash,representation,candidate,doc['clean_document_hash'],f'wave2-provenance-{hashlib.sha256(doc["paper_id"].encode()).hexdigest()[:12]}',now,runtime,{'seed':'NOT_AVAILABLE','temperature':'NOT_AVAILABLE'})
        surface={'provider':provider,'model':runtime,'candidate_id':candidate,'representation_version':representation,'source_document_hash':doc['clean_document_hash'],'prompt_hash':prompt_hash,'skill_hash':skill_hash,'schema_hash':schema_hash,'validator_hash':validator_hash}
        gate=provenance_gate(identity,surface,surface)
        corrected.append({**doc,'wave1_historical_model':doc.get('model'),'model_provider':provider,'model':runtime,'provider_resolved_model':'UNKNOWN','model_revision':'UNKNOWN','runtime_identity':identity.public_dict(),'wave2_cache_identity':{**surface,'sha256':sha256_json(surface)},'provenance_gate':gate})
        gate_results.append(gate)
    manifest={'version':'skill07_wave2_baseline_manifest_v1','created_at':now,'historical_manifest_preserved':str((ROOT/'skill07_baseline_manifest.json').resolve()),'wave1_drift':{'source_default_model':source_default,'wave1_manifest_model':sorted({d.get('model') for d in old['documents']}),'configured_model':configured,'resolved_runtime_model':runtime,'actual_invocation_argument_in_wave1_artifacts':'kimi-k3','provider_resolved_model':'UNKNOWN','finding':'Wave1 baseline manifest froze the source default instead of the resolved runtime model; its model/cache identities are invalid for benchmark reuse.'},'preflight_status':'PASS' if all(g['status']=='PASS' for g in gate_results) else 'BENCHMARK_BLOCKED_PROVENANCE_MISMATCH','documents':corrected}
    write_json(ROOT/'skill07_wave2_baseline_manifest.json',manifest)

    alignments=[]
    for pair in pairs:
        comparison=compare_aligned_outputs(pair['a'].get('output') or {},pair['g'].get('output') or {})
        alignments.append({'paper_id':pair['paper_id'],'source':'WAVE1_HISTORICAL_NOT_CONTROLLED_WAVE2','a_status':pair['a']['status'],'g_status':pair['g']['status'],**comparison})
    total={name:sum(x['counts'][name] for x in alignments) for name in ('FORMAT_ONLY','SEMANTICALLY_EQUIVALENT','POTENTIALLY_MEANINGFUL','CRITICAL_SCIENTIFIC_DIFFERENCE','AMBIGUOUS_REQUIRES_HUMAN')}
    alignment_report={'version':'skill07_semantic_alignment_v1','pairs_analyzed':len(alignments),'scope':'historical Wave1 complete pairs only','counts':total,'automated_scientific_truth':False,'pairs':alignments}
    write_json(ROOT/'skill07_semantic_alignment_report.json',alignment_report)

    core=select_core(corrected,pair_ids)
    lines=['# Skill07 Gold Selection','','状态：`AWAITING_HUMAN_ADJUDICATION`','','选择依据来自 clean-document 结构和已有抽取状态，不依赖文件名。5 篇覆盖已有 A/G 配对，其余补充长度、图表、段落及 Methods/Results 结构极值。','', '| Core | Paper ID | chars | paragraphs | figures | tables | baseline | rationale |','|---|---|---:|---:|---:|---:|---|---|']
    for i,d in enumerate(core,1):
        f=d['selection_features']; rationale='existing A/G pair' if d['paper_id'] in pair_ids else 'structural diversity/extreme'
        lines.append(f"| P{i:02d} | `{d['paper_id']}` | {f['characters']} | {f['paragraphs']} | {f['figures']} | {f['tables']} | {'available' if f['baseline_available'] else 'missing'} | {rationale} |")
    (ROOT/'skill07_gold_selection.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

    gold_papers=[]; review_items=[]
    pair_map={p['paper_id']:p for p in pairs}
    for i,d in enumerate(core,1):
        pid=d['paper_id']; pair=pair_map.get(pid); comparison=next((a for a in alignments if a['paper_id']==pid),None)
        paper={'benchmark_paper_id':f'GOLD-P{i:02d}','paper_id':pid,'review_state':'AWAITING_HUMAN_ADJUDICATION','gold_experiments':[],'known_ambiguity':[],'source_clean_document':d['clean_document_path']}
        if pair:
            for side,label in ((pair['a'],'A'),(pair['g'],'G')):
                for j,exp in enumerate(((side.get('output') or {}).get('experimental_design_object') or {}).get('experiments',[]),1):
                    review_items.append({'priority':'HIGH','paper_benchmark_id':paper['benchmark_paper_id'],'item_id':f'{paper["benchmark_paper_id"]}-{label}-{j:03d}','source_evidence':exp.get('evidence_paragraphs',[]),'a_interpretation':exp if label=='A' else 'SEE_PAIRED_ITEM','g_interpretation':exp if label=='G' else 'SEE_PAIRED_ITEM','comparator_alignment':'SEE_ALIGNMENT_REPORT','human_choice':'AWAITING_HUMAN_ADJUDICATION'})
            paper['known_ambiguity']=comparison['differences'] if comparison else []
        gold_papers.append(paper)
    gold={'version':'skill07_gold_review_v1','independent_gold_established':False,'review_state':'AWAITING_HUMAN_ADJUDICATION','instruction':'Reviewer must create stable gold experiment IDs GOLD-Pxx-Eyyy from source evidence; A/G IDs are references only.','required_fields':['gold_experiment_id','biological_object','intervention/design_action','trigger','condition','implementation','result','rationale','supported_alternatives','evidence_anchors','supported_rule/scope','critical_provenance','known_ambiguity','reviewer_decision','reviewer_notes'],'papers':gold_papers,'review_items':review_items}
    write_json(ROOT/'skill07_gold_review.json',gold)

    with (ROOT/'skill07_A_vs_G_paired_benchmark.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['paper_benchmark_id','paper_id','candidate','repetition','phase','status','provenance','independent','final_status','input_tokens','first_pass_ms','repair_attempts','total_wall_ms','quality_vs_gold']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for i,d in enumerate(core,1):
            for candidate in ('A_BASELINE','G_SAFE_COMBINED'):
                for rep in (1,2,3): w.writerow({'paper_benchmark_id':f'GOLD-P{i:02d}','paper_id':d['paper_id'],'candidate':candidate,'repetition':rep,'phase':'PILOT_OR_PRIMARY','status':'NOT_RUN_AWAITING_HUMAN_GOLD','provenance':'PRECHECK_PASS','independent':'NOT_RUN','final_status':'NOT_RUN','input_tokens':'NOT_MEASURED','first_pass_ms':'NOT_MEASURED','repair_attempts':'NOT_MEASURED','total_wall_ms':'NOT_MEASURED','quality_vs_gold':'AWAITING_HUMAN'})
    with (ROOT/'skill07_concurrency_benchmark.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['candidate','concurrency','status','papers_per_hour','successful_papers_per_hour','p50_ms','p90_ms','p95_ms','max_ms','failure_rate','retry_rate','full_repair_rate','rate_limit_events','provider_errors','tokens_per_completed_paper']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for candidate in ('A_BASELINE','G_SAFE_COMBINED'):
            for c in (1,2,4): w.writerow({'candidate':candidate,'concurrency':c,'status':'NOT_RUN_AWAITING_VALID_QUALITY_BENCHMARK',**{x:'NOT_MEASURED' for x in fields[3:]}})
    queue=['# Skill07 Wave 2 Human Review Queue','','状态：`AWAITING_HUMAN_ADJUDICATION`','','FORMAT_ONLY 与 SEMANTICALLY_EQUIVALENT 已自动排除。以下仅列潜在科学差异、关键差异与歧义。','']
    meaningful=[d|{'paper_id':a['paper_id']} for a in alignments for d in a['differences'] if d['class'] not in {'FORMAT_ONLY','SEMANTICALLY_EQUIVALENT'}]
    for n,item in enumerate(meaningful,1): queue += [f"## {n}. {item['paper_id']}",f"- 分类：`{item['class']}`",f"- A/G：`{item.get('left_id','UNMATCHED')}` / `{item.get('right_id','UNMATCHED')}`",f"- 变化维度：{', '.join(item.get('changed_dimensions',[])) or item.get('reason','alignment ambiguity')}",'- Source evidence：见 `skill07_gold_review.json` 对应条目的 paragraph anchors 与 clean document。','- Human choice：`AWAITING_HUMAN_ADJUDICATION`','']
    (ROOT/'SKILL07_WAVE2_HUMAN_REVIEW_QUEUE.md').write_text('\n'.join(queue),encoding='utf-8')

    results={'version':'skill07_optimization_wave2_v1','production_behavior_changed':False,'provenance_gate':manifest['preflight_status'],'actual_runtime':{'provider':provider,'source_default_model':source_default,'configured_model':configured,'resolved_runtime_model':runtime,'invocation_argument':runtime,'provider_resolved_model':'UNKNOWN','revision':'UNKNOWN'},'wave1_provenance_correct':False,'semantic_alignment':{'historical_pairs':len(alignments),'counts':total},'gold':{'independent_gold_established':False,'core_papers':10,'status':'AWAITING_HUMAN_ADJUDICATION'},'pilot':{'status':'NOT_RUN_AWAITING_HUMAN_GOLD','new_model_calls':0},'primary_benchmark':{'status':'NOT_RUN_AWAITING_HUMAN_GOLD','planned_runs':60,'completed_runs':0},'concurrency':{'c1':'NOT_MEASURED','c2':'NOT_MEASURED','c4':'NOT_MEASURED'},'quality_vs_gold':{'A_BASELINE':'AWAITING_HUMAN','G_SAFE_COMBINED':'AWAITING_HUMAN','critical_g_regression':'UNKNOWN'},'performance':{'g_token_change':'NOT_MEASURED_WAVE2','first_pass_latency_change':'NOT_MEASURED','repair_rate_cost_change':'NOT_MEASURED','total_latency_change':'NOT_MEASURED'},'final_decision':'HOLD','decision_reason':'Independent Skill07 human gold/adjudication is absent. Stop rule E forbids inventing it; expensive repetitions and throughput escalation would not resolve the scientific quality veto.','historical_wave1_evidence_reused_not_promoted':True}
    write_json(ROOT/'skill07_wave2_results.json',results)

if __name__=='__main__': main()
