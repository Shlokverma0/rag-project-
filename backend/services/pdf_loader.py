import pymupdf as fitz
from fastapi import HTTPException


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    PDF bytes leta hai, saara text ek string mein return karta hai.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid PDF file: {str(e)}")

    if doc.page_count == 0:
        raise HTTPException(status_code=400, detail="PDF has no pages.")

    full_text = ""
    for page in doc:
        full_text += page.get_text()

    doc.close()

    full_text = full_text.strip()

    if not full_text:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in PDF. It might be a scanned/image-only PDF."
        )

    return full_text