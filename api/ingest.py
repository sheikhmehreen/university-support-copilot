"""Ingest the knowledge base into Supabase (pgvector).

Run from the api/ folder:  python ingest.py

Flow: read knowledge_base/**/*.md|.txt -> split into chunks -> embed with Jina
-> upsert into the kb_chunks table. Safe to re-run (upsert on source_file + chunk_index).
"""
import os
import re
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

JINA_KEY = os.getenv("EMBED_API_KEY")
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY")

KB_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"
MAX_CHARS = 1000  # target upper size of one chunk
ALLOWED = {"academic_affairs", "finance", "it_support", "student_services"}


def split_into_chunks(text: str) -> list[str]:
    """Split on markdown headings first, then on paragraphs if a section is too long."""
    sections = re.split(r"\n(?=#{1,3} )", text)
    chunks: list[str] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= MAX_CHARS:
            chunks.append(section)
            continue
        current = ""
        for para in section.split("\n\n"):
            if current and len(current) + len(para) > MAX_CHARS:
                chunks.append(current.strip())
                current = ""
            current += para + "\n\n"
        if current.strip():
            chunks.append(current.strip())
    return chunks


def embed(texts: list[str]) -> list[list[float]]:
    r = httpx.post(
        "https://api.jina.ai/v1/embeddings",
        headers={"Authorization": f"Bearer {JINA_KEY}"},
        json={
            "model": "jina-embeddings-v3",
            "task": "retrieval.passage",
            "input": texts,
        },
        timeout=60,
    )
    if r.status_code >= 300:
        print("Jina error:", r.status_code, r.text)
        raise SystemExit(1)
    data = sorted(r.json()["data"], key=lambda d: d["index"])
    return [d["embedding"] for d in data]


def save_rows(rows: list[dict]) -> None:
    r = httpx.post(
        f"{SUPABASE_URL}/rest/v1/kb_chunks?on_conflict=source_file,chunk_index",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
        json=rows,
        timeout=60,
    )
    if r.status_code >= 300:
        print("Supabase error:", r.status_code, r.text)
        raise SystemExit(1)


def main() -> None:
    if not (JINA_KEY and SUPABASE_URL and SUPABASE_KEY):
        print("Missing EMBED_API_KEY, SUPABASE_URL or SUPABASE_SECRET_KEY in api/.env")
        raise SystemExit(1)
    if not KB_DIR.exists():
        print(f"Knowledge base folder not found: {KB_DIR}")
        raise SystemExit(1)

    total = 0
    for path in sorted(KB_DIR.rglob("*")):
        if path.suffix not in {".md", ".txt"}:
            continue
        if path.parent.name not in ALLOWED:
            print(f"Skipped (not an allowed department): {path.name}")
            continue
        chunks = split_into_chunks(path.read_text(encoding="utf-8"))
        if not chunks:
            continue
        vectors = embed(chunks)
        source = path.relative_to(KB_DIR).as_posix()
        rows = [
            {
                "source_file": source,
                "department": path.parent.name,
                "chunk_index": i,
                "content": chunk,
                "embedding": "[" + ",".join(str(x) for x in vec) + "]",
            }
            for i, (chunk, vec) in enumerate(zip(chunks, vectors))
        ]
        save_rows(rows)
        print(f"{source}: {len(rows)} chunks")
        total += len(rows)
    print(f"Done. {total} chunks stored.")


if __name__ == "__main__":
    main()