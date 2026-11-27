import re
from pathlib import Path
from src.ingestion.loader import load_policy, load_articles
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

    def test_chunk_size_500(self):
        document = load_policy(self.POLICY_PATH)
        chunks = chunk_documents(document, 500)
        assert len(chunks) > 12, "Chunks count is not greater than 12 at chunk size 500."

        ids = [chunk.chunk_id for chunk in chunks]
        assert len(ids) == len(set(ids)), "Non unique id in chunks."

        for chunk in chunks:
            assert len(chunk.text) <= 500, "Chunk size is over 500 limit."

    def test_chunk_id_consistency_with_chunk_size_500(self):
        document = load_policy(path=self.POLICY_PATH)
        id_list = []

        for i in range(2):
            chunks = chunk_documents(document, 500)
            ids = [chunk.chunk_id for chunk in chunks]
            id_list.append(ids)

        assert all(id_list[0] == ids for ids in id_list), "Chunk IDs are inconsistent across runs."

    def test_load_help_articles(self):
        ariticle_path = Path("data/help_articles")
        articles = load_articles(ariticle_path)

        assert len({d.source for d in articles}) == 15, "Failed to read all 15 articles."
        assert len(articles) == 29, "Failed to load articles into 29 chunks."

        for doc in articles:
            assert doc.doc_type == "help_article"
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", doc.updated_at)
            assert "Last updated" not in doc.text

    def test_load_policy(self):
        document = load_policy(path=self.POLICY_PATH)

        for policy in document:
            assert policy.doc_type == "policy", "Wrong doc_type for policy documents."
            assert  policy.updated_at is None

    def test_unique_chunk_id_on_combined_docs(self):
        article_path = Path("data/help_articles")
        doc_path = [(self.POLICY_PATH, "policy"), (article_path, "help_articles")]

        chunks = []
        for path, doc_type in doc_path:
            doc = load_policy(path) if doc_type == "policy" else load_articles(path)
            results = chunk_documents(doc, chunk_size=500)
            chunks.extend(results)

        chunk_ids = [chunk.chunk_id for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids)), "Non unique chunk ids detected in combined doc's chunks."
