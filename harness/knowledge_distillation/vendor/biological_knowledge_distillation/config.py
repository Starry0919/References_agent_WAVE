from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ModuleConfig:
    llm_provider: str = "none"
    retry: int = 3
    review_enabled: bool = True
    logging_level: str = "INFO"
    state_dir: Path = field(default_factory=lambda: Path(__file__).parent / "storage" / "runtime")
    default_output_languages: tuple = ("zh", "en")
    default_organism_scope_when_unstated: str = "unknown"  # never silently default to E. coli K-12


DEFAULT_CONFIG = ModuleConfig()
