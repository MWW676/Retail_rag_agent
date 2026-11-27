import re
from pathlib import Path
from src.core.models import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

def _load_markdown(path: Path, doc_type: str) -> list[Document]:
    with open(path, 'r', encoding='utf-8') as f:
        policy = f.read()

    headers = [("#", "header1"), ("##", "header2"), ("###", "header3")]
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers)
    chunks = splitter.split_text(policy)

    res, updated_at = [], None
    for chunk in chunks:
        header_list = [chunk.metadata.get(header, "") for _, header in headers]
        section_header = ">".join(filter(None, header_list))
        if "Last updated:" in chunk.page_content:
            substr = re.search(r'\d{4}[-]\d{2}[-]\d{2}', chunk.page_content)
            updated_at = substr.group(0)
            chunk.page_content = "".join(chunk.page_content.split("\n", 1)[1:])
        res.append(Document(
            text=chunk.page_content,
            source=str(path.name),
            section=section_header,
            doc_type=doc_type,
            updated_at=updated_at
        ))

    return res

def load_policy(path: Path) -> list[Document]:
    """
    Load a policy document from a file and return it as a list of Document object.
    """
    return _load_markdown(path, doc_type="policy")

def load_articles(dir: Path) -> list[Document]:
    res = []
    for path in sorted(dir.glob("*.md")):
        res.extend(_load_markdown(path, doc_type="help_article"))

    return res
