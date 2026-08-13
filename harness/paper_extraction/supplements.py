"""Additive supplement artifact intake; never injects Skill07 by default."""
from __future__ import annotations
import csv,hashlib,io,json,mimetypes,zipfile
from pathlib import Path,PurePosixPath
from typing import Any

INJECTION_DEFAULT=False
ALLOWED={'.pdf','.docx','.xlsx','.xls','.csv','.tsv','.txt','.zip'}

def classify(name:str)->str:
    ext=Path(name).suffix.lower()
    return {'.pdf':'PDF','.docx':'DOCX','.xlsx':'SPREADSHEET','.xls':'SPREADSHEET','.csv':'TABLE','.tsv':'TABLE','.txt':'TEXT','.zip':'ARCHIVE'}.get(ext,'UNSUPPORTED')

def inspect_zip(data:bytes,max_files=200,max_uncompressed=256*1024*1024,max_ratio=100)->list[dict[str,Any]]:
    entries=[];total=0
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if len(z.infolist())>max_files:raise ValueError('archive file-count limit exceeded')
        for i in z.infolist():
            p=PurePosixPath(i.filename)
            if p.is_absolute() or '..' in p.parts:raise ValueError('unsafe zip path')
            if Path(i.filename).suffix.lower() in {'.exe','.dll','.bat','.cmd','.ps1','.sh','.js','.msi'}:raise ValueError('executable archive member rejected')
            total+=i.file_size
            if total>max_uncompressed:raise ValueError('archive uncompressed-size limit exceeded')
            if i.compress_size and i.file_size/i.compress_size>max_ratio:raise ValueError('archive compression-ratio limit exceeded')
            entries.append({'name':i.filename,'size':i.file_size,'type':classify(i.filename)})
    return entries

def ingest(paper_id:str,source_reference:str,filename:str,data:bytes,store:Path,parser_version='supplement-v1')->dict[str,Any]:
    kind=classify(filename);sha=hashlib.sha256(data).hexdigest();store=Path(store);store.mkdir(parents=True,exist_ok=True);path=store/sha
    status='PARSED_METADATA_ONLY';structure=None
    if kind=='UNSUPPORTED':status='UNSUPPORTED_TYPE'
    elif kind=='ARCHIVE':structure={'entries':inspect_zip(data)}
    elif kind in {'TABLE'}:
        delimiter='\t' if filename.lower().endswith('.tsv') else ','
        rows=list(csv.reader(io.StringIO(data.decode('utf-8-sig')),delimiter=delimiter));structure={'rows':len(rows),'columns':max(map(len,rows),default=0),'header':rows[0] if rows else []}
    elif kind=='SPREADSHEET':structure={'preservation':'ORIGINAL_WORKBOOK_RETAINED_WITH_SHEET_STRUCTURE'}
    path.write_bytes(data)
    return {'paper_id':paper_id,'source_reference':source_reference,'original_filename':filename,'sha256':sha,'file_type':kind,'parse_status':status,'parser_version':parser_version,'storage_ref':str(path),'skill07_supplement_injection':'DISABLED_BY_DEFAULT','structure':structure}

def unavailable(paper_id:str,state='SUPPLEMENT_NOT_FOUND',reference:str|None=None):
    if state not in {'SUPPLEMENT_NOT_FOUND','SUPPLEMENT_LINK_UNAVAILABLE','SUPPLEMENT_ACCESS_FAILED'}:raise ValueError('invalid supplement state')
    return {'paper_id':paper_id,'availability':state,'source_reference':reference,'skill07_supplement_injection':'DISABLED_BY_DEFAULT'}
