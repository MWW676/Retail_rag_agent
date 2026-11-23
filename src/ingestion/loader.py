from pathlib import Path
from src.core.models import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

def load_policy(path: Path) -> list[Document]:
    """
    Load a policy document from a file and return it as a list of Document object.
    """
    with open(path, 'r', encoding='utf-8') as f:
        policy = f.read()

    headers = [("#", "header1"), ("##", "header2"), ("###", "header3")]

    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers)
    chunks = splitter.split_text(policy)

    res = []
    for chunk in chunks:
        header_list = [chunk.metadata.get(header, "") for _, header in headers]
        section_header = ">".join(filter(None, header_list))
        res.append(Document(
            text=chunk.page_content,
            source=str(path.name),
            section=section_header
        ))

    return res
