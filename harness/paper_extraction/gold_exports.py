"""Deterministic, role-isolated Human Gold review exports."""
from __future__ import annotations
import hashlib,io,json,re
from pathlib import Path
from typing import Any
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether,PageBreak,Paragraph,SimpleDocTemplate,Spacer,Table,TableStyle
from .gold_infrastructure import PACKAGES,ROOT,load_draft,read,validate_draft
from .human_review_view import build_understanding

SKILL07_DATA=ROOT/'artifacts'/'data'/'skill07'

def _font()->str:
    candidates=[Path('C:/Windows/Fonts/msyh.ttc'),Path('C:/Windows/Fonts/simhei.ttf'),Path('C:/Windows/Fonts/arial.ttf')]
    for p in candidates:
        if p.is_file():
            try:pdfmetrics.registerFont(TTFont('WaveCJK',str(p),subfontIndex=0));return 'WaveCJK'
            except Exception:continue
    return 'Helvetica'

def paper_metadata(benchmark_id:str)->dict[str,Any]:
    package=PACKAGES/benchmark_id; source=read(package/'source_index.json'); clean=read(Path(source['source_document_path'])); meta=clean.get('document_metadata',{})
    manifest=read(SKILL07_DATA/'skill07_wave2_baseline_manifest.json'); matches=[d for d in manifest['documents'] if d['paper_id']==source['paper_id']]
    if len(matches)!=1:raise ValueError('paper ID does not map to exactly one source manifest record')
    item=matches[0]; pdf=Path(item['source_pdf'])
    available=pdf.is_file() and hashlib.sha256(pdf.read_bytes()).hexdigest()==item['pdf_hash']
    return {'benchmark_paper_id':benchmark_id,'paper_id':source['paper_id'],'title':meta.get('title') or meta.get('paper_title') or build_understanding(benchmark_id)['title'],'doi':meta.get('doi') or 'NOT_REPORTED','journal':meta.get('journal') or 'NOT_REPORTED','year':meta.get('year') or meta.get('publication_year') or 'NOT_REPORTED','source_pdf_available':available,'source_pdf_path':str(pdf) if available else None,'source_pdf_hash':item['pdf_hash'],'paper_position':int(benchmark_id[-2:]),'paper_total':10}

def original_pdf(benchmark_id:str)->tuple[Path,str]:
    meta=paper_metadata(benchmark_id)
    if not meta['source_pdf_available']:raise FileNotFoundError('Original PDF is missing or its fingerprint does not match the manifest.')
    safe=re.sub(r'[^A-Za-z0-9._-]+','-',str(meta['title']))[:60].strip('-') or 'paper'
    return Path(meta['source_pdf_path']),f'{benchmark_id}_{safe}.pdf'

def review_pdf(benchmark_id:str,role:str,locale:str='zh-CN')->tuple[bytes,str]:
    if role not in {'ANNOTATOR_A','ANNOTATOR_B','ADJUDICATOR'}:raise ValueError('invalid role')
    # Deliberately read only the requested role. Adjudication comparisons are
    # exported only after a real reconciliation state exists (not yet).
    draft=load_draft(benchmark_id,role); package=PACKAGES/benchmark_id; source=read(package/'source_index.json'); meta=paper_metadata(benchmark_id); validation=validate_draft(draft,source)
    zh=locale=='zh-CN'; font=_font();styles=getSampleStyleSheet()
    title=ParagraphStyle('title',parent=styles['Title'],fontName=font,fontSize=22,leading=29,textColor=colors.HexColor('#17324d'),alignment=TA_CENTER,spaceAfter=10)
    h1=ParagraphStyle('h1',parent=styles['Heading1'],fontName=font,fontSize=15,leading=20,textColor=colors.HexColor('#17324d'),spaceBefore=10,spaceAfter=6)
    h2=ParagraphStyle('h2',parent=styles['Heading2'],fontName=font,fontSize=12,leading=16,textColor=colors.HexColor('#245b78'),spaceBefore=7,spaceAfter=4)
    body=ParagraphStyle('body',parent=styles['BodyText'],fontName=font,fontSize=9.5,leading=15,textColor=colors.HexColor('#263746'),spaceAfter=5)
    small=ParagraphStyle('small',parent=body,fontSize=8,leading=12,textColor=colors.HexColor('#586b7a'))
    buff=io.BytesIO()
    def pages(canvas,doc):
        canvas.saveState();canvas.setFont(font,8);canvas.setFillColor(colors.HexColor('#657786'));canvas.drawString(18*mm,12*mm,'WAVE · Skill07 Human Gold Review');canvas.drawRightString(192*mm,12*mm,f'{doc.page}');canvas.restoreState()
    doc=SimpleDocTemplate(buff,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=17*mm,bottomMargin=19*mm,title=f'{benchmark_id} Human Gold Review')
    story=[Spacer(1,16*mm),Paragraph('WAVE',title),Paragraph('Skill07 Human Gold Review' if not zh else 'Skill07 Human Gold 人工科学审核',title),Spacer(1,4*mm),Paragraph(benchmark_id,h1),Paragraph(str(meta['title']),h2),Spacer(1,8*mm)]
    warning='Working annotation document - not frozen Gold' if not zh else '工作标注文档 - 非冻结 Gold'
    story += [Table([[warning]],colWidths=[165*mm],style=TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fff4d6')),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#d6a62b')),('FONTNAME',(0,0),(-1,-1),font),('ALIGN',(0,0),(-1,-1),'CENTER'),('PADDING',(0,0),(-1,-1),8)])),Spacer(1,8*mm),Paragraph(('角色：' if zh else 'Role: ')+role.replace('_',' ').title(),body),Paragraph(('生成状态：' if zh else 'Current status: ')+draft['review_state'],body),Paragraph(('本材料遵循 source-first；机器候选不是答案，可保留不确定。' if zh else 'Review source first. Machine candidates are not answers; uncertainty may remain.'),body),PageBreak()]
    story += [Paragraph('Paper Metadata' if not zh else '论文信息',h1),Table([[('Title' if not zh else '标题'),meta['title']],[('DOI'),meta['doi']],[('Journal / Year' if not zh else '期刊 / 年份'),f"{meta['journal']} / {meta['year']}"],[('Source ID' if not zh else '来源 ID'),meta['paper_id']]],colWidths=[35*mm,130*mm],style=TableStyle([('FONTNAME',(0,0),(-1,-1),font),('FONTSIZE',(0,0),(-1,-1),8.5),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.25,colors.HexColor('#cbd5df')),('BACKGROUND',(0,0),(0,-1),colors.HexColor('#eef4f7')),('PADDING',(0,0),(-1,-1),5)])),Spacer(1,4*mm)]
    story += [Paragraph('Progress & Validation' if not zh else '进度与校验',h1),Paragraph(f"Source coverage: {draft['source_coverage_review_complete']} · Experiments: {len(draft['experiments'])} · Claims: {len(draft['claims'])} · Evidence: {len(draft['evidence'])} · Critical blockers: {len(validation['blockers'])}",body)]
    story += [Paragraph('Experiments' if not zh else '实验 Gold 草稿',h1)]
    if not draft['experiments']:story.append(Paragraph('No human experiments recorded yet.' if not zh else '尚未记录人工实验；这不表示论文没有实验。',body))
    for exp in draft['experiments']:
        rows=[]
        for key,label in [('experiment_role','Role / 角色'),('experiment_granularity','Granularity / 粒度'),('intervention_or_design_action','Intervention / 干预'),('trigger','Trigger / 触发'),('conditions','Conditions / 条件'),('implementation','Implementation / 实施'),('readouts','Readouts / 检测指标'),('results','Results / 结果'),('rationale','Rationale / 理由'),('known_ambiguities','Uncertainty / 不确定性')]:rows.append([label,Paragraph(str(exp.get(key,'UNKNOWN')),small)])
        story += [KeepTogether([Paragraph(f"{exp['gold_experiment_id']} · {exp.get('experiment_title') or 'Untitled'}",h2),Table(rows,colWidths=[38*mm,127*mm],style=TableStyle([('FONTNAME',(0,0),(-1,-1),font),('FONTSIZE',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.2,colors.HexColor('#dbe3e8')),('PADDING',(0,0),(-1,-1),4)]))])]
    story += [Paragraph('Atomic Claims' if not zh else '原子科学主张',h1)]
    for c in draft['claims']:story += [Paragraph(f"{c['claim_id']} · {c['claim_type']} · {c['criticality']}",h2),Paragraph(c.get('claim_text_normalized') or 'UNKNOWN',body)]
    if not draft['claims']:story.append(Paragraph('No human claims recorded yet.' if not zh else '尚未记录人工主张。',body))
    story += [Paragraph('Evidence Anchors' if not zh else '证据锚点',h1)]
    for e in draft['evidence']:story += [Paragraph(f"{e['evidence_id']} · {e.get('section')} · {e.get('paragraph_id')}",h2),Paragraph(e.get('quote_or_excerpt') or e.get('anchor_text_or_fingerprint') or 'UNKNOWN',body)]
    if not draft['evidence']:story.append(Paragraph('No human evidence anchors recorded yet.' if not zh else '尚未记录人工证据锚点。',body))
    story += [Paragraph('Validation & Unresolved' if not zh else '校验与未解决项',h1)]
    for b in validation['blockers']:story.append(Paragraph(f"• {b['code']}: {b.get('id','')}",body))
    aids=read(package/'coverage_aids.json') if (package/'coverage_aids.json').is_file() else {}
    story.append(Paragraph(f"Unlinked source regions: {len(aids.get('unlinked_source_regions',[]))}; unlinked figures: {len(aids.get('unlinked_figures',[]))}; unlinked tables: {len(aids.get('unlinked_tables',[]))}.",body))
    story += [PageBreak(),Paragraph('Candidate Comparison - Reference only, machine-generated, NOT GOLD' if not zh else '机器候选对照 - 仅供参考，非 Gold',h1),Paragraph('Candidates remain hidden in this role-safe export until the reviewer chooses to consult them in the workbench. Another annotator draft is never included.',body),Paragraph('Provenance Appendix' if not zh else '审核相关溯源附录',h1),Paragraph(f"Benchmark: {benchmark_id} · Paper ID: {meta['paper_id']} · Role: {role} · Draft revision: {draft['revision']} · Schema tier: {draft['annotation_tier']}",small)]
    doc.build(story,onFirstPage=pages,onLaterPages=pages)
    filename=f"{benchmark_id}_{role.title().replace('_','-')}_Human-Gold-Review.pdf"
    return buff.getvalue(),filename
