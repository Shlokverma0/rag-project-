from sentence_transformers import SentenceTransformer

# Ye model chhota, fast, aur free hai - pehli baar chalane pe download hoga (~80MB)
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Text list leta hai, har text ke liye ek embedding vector return karta hai.
    """
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()