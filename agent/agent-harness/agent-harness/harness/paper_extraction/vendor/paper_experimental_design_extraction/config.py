from dataclasses import dataclass,field
from pathlib import Path
@dataclass
class ModuleConfig:
    llm_provider:str="none"
    retry:int=3
    review_enabled:bool=True
    logging_level:str="INFO"
    state_dir:Path=field(default_factory=lambda:Path(__file__).parent/"storage"/"runtime")
    language:str="zh"
DEFAULT_CONFIG=ModuleConfig()
