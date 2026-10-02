import re


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    """Split text into overlapping chunks, preferring line and sentence boundaries."""
    if not text or not text.strip():
        return []
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap must be smaller than chunk_size")

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    chunks: list[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        hard_end = min(start + chunk_size, text_length)
        end = hard_end

        if hard_end < text_length:
            search_from = start + int(chunk_size * 0.60)
            boundaries = [
                text.rfind("\n\n", search_from, hard_end),
                text.rfind("\n", search_from, hard_end),
                text.rfind(". ", search_from, hard_end),
                text.rfind("? ", search_from, hard_end),
                text.rfind("! ", search_from, hard_end),
                text.rfind("; ", search_from, hard_end),
                text.rfind(" ", search_from, hard_end),
            ]
            boundary = max(boundaries)
            if boundary >= search_from:
                end = boundary + (2 if text.startswith("\n\n", boundary) else 1)

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_length:
            break

        next_start = max(start + 1, end - overlap)
        while next_start < end and not text[next_start].isspace():
            next_start += 1
        while next_start < text_length and text[next_start].isspace():
            next_start += 1
        start = next_start

    return chunks
