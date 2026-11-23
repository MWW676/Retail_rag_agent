from pydantic import BaseModel

class Document(BaseModel):
    text: str
    source: str
    section: str

class Chunk(BaseModel):
    chunk_id: str
    text: str
    source: str
    section: str
