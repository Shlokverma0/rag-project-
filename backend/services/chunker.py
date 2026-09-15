def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Text ko chunks mein todta hai, with overlap.
    chunk_size = har chunk mein kitne characters honge
    overlap = consecutive chunks ke beech kitna text common hoga
    """
    if not text or len(text) == 0:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())

        # Next chunk overlap ke saath shuru hoga
        start = start + chunk_size - overlap

    # Empty chunks hata do (agar koi bane ho)
    chunks = [c for c in chunks if len(c) > 0]

    return chunks