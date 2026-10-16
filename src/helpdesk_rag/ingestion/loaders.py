import re
from pathlib import Path

import yaml
from langchain_core.documents import Document
from pypdf import PdfReader

SUPPORTED_SUFFIXES = {".md", ".txt", ".pdf"}

_FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Split optional YAML front matter (`---` fenced) from the document body."""
    match = _FRONT_MATTER.match(text)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    return (meta if isinstance(meta, dict) else {}), match.group(2)


def _base_metadata(path: Path, kb_dir: Path) -> dict:
    return {
        "source": path.relative_to(kb_dir).as_posix(),
        "title": path.stem.replace("-", " ").replace("_", " ").title(),
        "category": "general",
    }


def load_file(path: Path, kb_dir: Path) -> list[Document]:
    meta = _base_metadata(path, kb_dir)

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return [
            Document(page_content=text, metadata={**meta, "page": page_no})
            for page_no, page in enumerate(reader.pages, start=1)
            if (text := page.extract_text() or "").strip()
        ]

    front, body = parse_front_matter(path.read_text(encoding="utf-8"))
    # Pinecone metadata must be str/number/bool/list[str]; keep only simple scalar values.
    meta.update({k: str(v) for k, v in front.items() if isinstance(v, str | int | float)})
    return [Document(page_content=body, metadata=meta)] if body.strip() else []


def load_documents(kb_dir: Path) -> list[Document]:
    """Load every supported file under `kb_dir` (recursively)."""
    docs: list[Document] = []
    for path in sorted(kb_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            docs.extend(load_file(path, kb_dir))
    return docs
