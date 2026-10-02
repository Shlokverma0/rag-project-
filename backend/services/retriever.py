from backend.services.vector_store import collection
from backend.services.embeddings import get_embeddings


def retrieve_relevant_chunks(query: str, document_id: str, top_k: int = 5) -> dict:
    """Search only the selected uploaded document and return its best-matching chunks."""
    if not document_id:
        return {"chunks": [], "distances": [], "metadatas": []}

    matching = collection.get(
        where={"document_id": document_id},
        include=["metadatas"],
    )
    available = len(matching.get("ids", []))
    if available == 0:
        return {"chunks": [], "distances": [], "metadatas": []}

    query_embedding = get_embeddings([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(max(1, top_k), available),
        where={"document_id": document_id},
    )

    chunks = (results.get("documents") or [[]])[0] or []
    distances = (results.get("distances") or [[]])[0] or []
    metadatas = (results.get("metadatas") or [[]])[0] or []
    return {"chunks": chunks, "distances": distances, "metadatas": metadatas}
