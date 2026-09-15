from backend.services.vector_store import collection
from backend.services.embeddings import get_embeddings


def retrieve_relevant_chunks(query: str, top_k: int = 3) -> dict:
    """
    Query leta hai, uska embedding banata hai, ChromaDB mein similarity search karta hai.
    Top-k sabse relevant chunks return karta hai.
    """
    query_embedding = get_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # results ek dict hai jisme lists of lists hoti hain (batch support ke liye)
    # Humne sirf 1 query bheji, isliye index [0] use karenge
    chunks = results["documents"][0] if results["documents"] else []
    distances = results["distances"][0] if results["distances"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []

    return {
        "chunks": chunks,
        "distances": distances,
        "metadatas": metadatas
    }