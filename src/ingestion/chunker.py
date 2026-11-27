from src.core.models import Document, Chunk

def chunk_documents(docs: list[Document], chunk_size: int | None=None) -> list[Chunk]:
    chunks = []

    for doc in docs:
        pieces = [doc.text] if not chunk_size else _split_by_lines(chunk_size, doc.text)
        for idx, piece in enumerate(pieces):
            chunks.append(Chunk(
                chunk_id=f"{doc.source}-{doc.section}-{idx}",
                text=piece,
                source=doc.source,
                section=doc.section,
                doc_type=doc.doc_type,
                updated_at=doc.updated_at
            ))

    return chunks

def _split_by_lines(chunk_size: int, text: str) -> list[str]:
    pieces, curr = [], ""
    for line in text.split('\n'):
        candidate = line if not curr else curr + '\n' + line
        if curr and len(candidate) > chunk_size:
            pieces.append(curr)
            curr = line
        else:
            curr = candidate
    if curr:
        pieces.append(curr)

    return pieces