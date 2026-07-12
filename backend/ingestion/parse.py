# backend/ingestion/parse.py
"""
Parses knowledge base source files into plain text.

Supports:
- PDF  → extracted via pypdf (lightweight, pure-Python)
- DOCX → extracted via python-docx (reads paragraph text)
- MD   → read as-is (already plain text)

Returns a list of {source, text} dicts so downstream code knows
which file each chunk came from (used for the `sources` field in API responses).
"""

import os
from pathlib import Path
from typing import List, Dict

from pypdf import PdfReader
from docx import Document


def parse_pdf(filepath: str) -> str:
    """Extract all text from a PDF, page by page."""
    reader = PdfReader(filepath)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())
    return "\n\n".join(pages)


def parse_docx(filepath: str) -> str:
    """Extract all paragraph text from a DOCX file."""
    doc = Document(filepath)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def parse_markdown(filepath: str) -> str:
    """Read a markdown file as plain text — no conversion needed."""
    return Path(filepath).read_text(encoding="utf-8")


# Map file extensions to their parser functions
PARSERS = {
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".md": parse_markdown,
}


def parse_all(kb_dir: str) -> List[Dict[str, str]]:
    """
    Walk the knowledge_base directory, parse every supported file,
    and return a list of {source: filename, text: extracted_text} dicts.

    Unsupported file types are skipped with a warning — not a crash.
    """
    documents = []
    kb_path = Path(kb_dir)

    if not kb_path.exists():
        raise FileNotFoundError(f"Knowledge base directory not found: {kb_dir}")

    # Walk all files recursively
    for filepath in sorted(kb_path.rglob("*")):
        if filepath.is_dir():
            continue

        ext = filepath.suffix.lower()
        parser = PARSERS.get(ext)

        if parser is None:
            print(f"[SKIP] Unsupported file type: {filepath.name}")
            continue

        try:
            text = parser(str(filepath))
            if text.strip():
                documents.append({
                    "source": filepath.name,  # just the filename, not full path
                    "text": text.strip(),
                })
                print(f"[OK]   Parsed {filepath.name} ({len(text)} chars)")
            else:
                print(f"[WARN] Empty content from: {filepath.name}")
        except Exception as e:
            # Don't crash the whole pipeline if one file fails
            print(f"[ERR]  Failed to parse {filepath.name}: {e}")

    return documents


# ── Quick test: run this file directly to verify parsing works ──
if __name__ == "__main__":
    # Resolve knowledge_base path relative to the project root
    project_root = Path(__file__).resolve().parent.parent.parent
    kb_dir = project_root / "knowledge_base"

    print(f"Parsing knowledge base at: {kb_dir}\n")
    docs = parse_all(str(kb_dir))

    print(f"\n{'='*60}")
    print(f"Parsed {len(docs)} document(s):\n")
    for doc in docs:
        preview = doc["text"][:200].replace("\n", " ")
        print(f"  [{doc['source']}] {preview}...")
    print()
