import yaml
from pydantic import BaseModel, ConfigDict
from typing import Literal
from pathlib import Path

class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    llm_model: str
    embedding_model: str
    temperature: float
    chunk_size: int | None
    top_k: int
    prompt_version: str
    policy_mode: Literal["retrieved", "full"]

def load_config(path: Path) -> AppConfig:
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return AppConfig(**data)
