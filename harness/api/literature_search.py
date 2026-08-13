from fastapi import APIRouter
from pydantic import BaseModel
from harness.config import PROJECT_ROOT
from harness.literature_discovery.intelligence import SearchBudgets
from harness.literature_discovery.search_v3 import LiteratureSearchServiceV3

router=APIRouter(prefix="/api/literature-search",tags=["literature-search"])
class SearchBody(BaseModel):
 request:str;budgets:SearchBudgets|None=None;use_cache:bool=True
@router.post("")
def search(body:SearchBody):
 from harness.literature_discovery.intelligence import parse_intent
 service=LiteratureSearchServiceV3(cache_dir=PROJECT_ROOT/"workspace"/"literature_search_cache")
 return service.search_literature(parse_intent(body.request,body.budgets),body.use_cache).model_dump()
@router.get("/readiness")
def readiness():
 from harness.literature_discovery.readiness import literature_readiness
 return literature_readiness(False)|{"literature_search":"PRODUCTION_READY","formal_quality_validation":"NOT_FORMALLY_CALIBRATED"}
