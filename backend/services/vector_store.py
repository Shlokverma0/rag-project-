import chromadb
from backend.services.embeddings import get_embeddings

# Local persistent ChromaDB - backend/data folder mein save hoga
client = chromadb.PersistentClient(path="backend/data/chroma_db")

collection = client.get_or_create_collection(name="pdf_documents")


def store_chunks(chunks: list[str], doc_id: str):
    """
    Chunks ko embeddings mein convert karke ChromaDB mein store karta hai.
    doc_id = kis document se ye chunks aaye hain (filename use karenge)
    """
    if not chunks:
        return

    embeddings = get_embeddings(chunks)

    # Har chunk ko unique ID chahiye
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

    # Metadata - kis document se ye chunk aaya, kya kaam aayega baad mein
    metadatas = [{"source": doc_id, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )


def get_collection_count():
    """Debug ke liye - kitne chunks store hain"""
    return collection.count()