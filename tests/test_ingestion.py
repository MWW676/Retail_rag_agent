import pytest
from pathlib import Path
from src.ingestion.loader import load_policy
from src.ingestion.chunker import chunk_documents

class TestIngestion:
    POLICY_PATH = Path("data/policy.md")

    def test_chunk_size(self):
        document = load_policy(path=self.POLICY_PATH)
        chunks = chunk_documents(document)
        for chunk in chunks:
            assert len(chunk.text) > 0, f"Chunk {chunk.chunk_id} is empty."

    def test_chunk_structure(self):
        document = load_policy(path=self.POLICY_PATH)
        chunks = chunk_documents(document)
        for chunk in chunks:
            assert chunk.section != "", f"Chunk {chunk.chunk_id} has no section."
            assert chunk.source == str(self.POLICY_PATH.name), f"Chunk {chunk.chunk_id} has incorrect source."

    def test_chunk_id_consistency(self):
        document = load_policy(path=self.POLICY_PATH)
        id_list = []

        for i in range(2):
            chunks = chunk_documents(document)
            ids = [chunk.chunk_id for chunk in chunks]
            id_list.append(ids)

        assert all(id_list[0] == ids for ids in id_list), "Chunk IDs are inconsistent across runs."
