import hashlib,json
from pathlib import Path
import pdfplumber
import pytest
from fastapi.testclient import TestClient
from harness.server import create_app
from harness.paper_extraction.gold_exports import original_pdf,paper_metadata,review_pdf
from harness.paper_extraction.gold_infrastructure import PACKAGES

def test_all_ten_pdf_mappings_are_exact_and_fingerprinted():
 seen=set()
 for i in range(1,11):
  bid=f'GOLD-P{i:02d}';m=paper_metadata(bid);p,name=original_pdf(bid)
  assert m['paper_id']==json.loads((PACKAGES/bid/'source_index.json').read_text(encoding='utf-8'))['paper_id']
  assert hashlib.sha256(p.read_bytes()).hexdigest()==m['source_pdf_hash'] and p not in seen and name.startswith(bid)
  seen.add(p)
def test_wrong_mapping_and_missing_pdf_fail_clearly(tmp_path,monkeypatch):
 import harness.paper_extraction.gold_exports as x
 original=x.read
 def bad(path):
  d=original(path)
  if str(path).endswith('skill07_wave2_baseline_manifest.json'):d['documents']=[z for z in d['documents'] if z['paper_id']!='6d69baa813434a95b3a7e47b1532d728_1-s2.0-S1096717621001750-main']
  return d
 monkeypatch.setattr(x,'read',bad)
 with pytest.raises(ValueError):x.original_pdf('GOLD-P01')
def test_review_pdf_is_formatted_current_role_zero_gold_and_no_other_draft():
 before=(PACKAGES/'GOLD-P01'/'annotations'/'ANNOTATOR_A.json').read_bytes();data,name=review_pdf('GOLD-P01','ANNOTATOR_A','zh-CN')
 assert data.startswith(b'%PDF') and 'ANNOTATOR-A' in name.upper()
 with pdfplumber.open(__import__('io').BytesIO(data)) as pdf:
  text='\n'.join(p.extract_text() or '' for p in pdf.pages)
 assert 'GOLD-P01' in text and ('Working annotation document' in text or '工作标注文档' in text) and 'ANNOTATOR B' not in text
 assert (PACKAGES/'GOLD-P01'/'annotations'/'ANNOTATOR_A.json').read_bytes()==before
def test_download_endpoints_and_role_isolation():
 c=TestClient(create_app());r=c.get('/api/skill07-gold/papers/GOLD-P01/review-package.pdf?role=ANNOTATOR_B&locale=en-US')
 assert r.status_code==200 and r.headers['x-gold-tier']=='WORKING_ANNOTATION_NOT_GOLD' and r.content.startswith(b'%PDF')
 assert c.get('/api/skill07-gold/papers/GOLD-P01/original.pdf').status_code==200
