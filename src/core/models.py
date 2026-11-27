from pydantic import BaseModel
from typing import Literal

class Document(BaseModel):
    text: str
    source: str
    section: str
    doc_type: Literal["policy", "help_article"]
    updated_at: str | None

class Chunk(BaseModel):
    chunk_id: str
    text: str
    source: str
    section: str
    doc_type: Literal["policy", "help_article"]
    updated_at: str | None

class Answer(BaseModel):
    answer: str
    cited_chunk_ids: list[str]
    refused: bool