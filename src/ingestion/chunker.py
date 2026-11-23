from src.core.models import Document, Chunk

def chunk_documents(docs: list[Document]) -> list[Chunk]:
    chunks, idx = [], 0
    section = docs[0].section if docs else ""

    for doc in docs:
        if doc.section != section:
            idx = 0
            section = doc.section
        chunk_id = f"{doc.source}-{section}-{idx}"
        chunks.append(Chunk(
            chunk_id=chunk_id,
            text=doc.text,
            source=doc.source,
            section=doc.section
        ))
        idx += 1
        print(f"Chunk created: {chunk_id} under section {section}")

    print(f"Total chunks created: {len(chunks)}")
    return chunks