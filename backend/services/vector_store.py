import json
from pathlib import Path

import chromadb
from backend.services.embeddings import get_embeddings

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHROMA_DIR = DATA_DIR / "chroma_db"
ACTIVE_DOCUMENT_PATH = DATA_DIR / "active_document.json"

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(name="pdf_documents")


def store_chunks(chunks: list[str], doc_id: str, source: str) -> None:
    """Embed and persist one uploaded document under a unique ID."""
    if not chunks:
        raise ValueError("Cannot store a document with no text chunks")

    embeddings = get_embeddings(chunks)
    ids = [f"{doc_id}_chunk_{index}" for index in range(len(chunks))]
    metadatas = [
        {"document_id": doc_id, "source": source, "chunk_index": index}
        for index in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_DOCUMENT_PATH.write_text(
        json.dumps({"document_id": doc_id, "filename": source}, ensure_ascii=False),
        encoding="utf-8",
    )


def get_active_document() -> dict | None:
    """Return the most recently uploaded document, including after a restart."""
    try:
        active = json.loads(ACTIVE_DOCUMENT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(active, dict) or not active.get("document_id"):
        return None
    return active


def get_collection_count() -> int:
    return collection.count()
