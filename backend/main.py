from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.config import MAX_FILE_SIZE_MB
from backend.services.chunker import chunk_text
from backend.services.pdf_loader import extract_text_from_pdf
from backend.services.rag_pipeline import NO_INFO_ANSWER, run_rag_pipeline
from backend.services.vector_store import (
    get_active_document,
    get_collection_count,
    store_chunks,
)

app = FastAPI(title="RAG PDF Q&A System", version="0.3.0")


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG backend is running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB allowed.",
        )

    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No readable text found in the PDF.")

    document_id = uuid4().hex
    store_chunks(chunks, doc_id=document_id, source=filename)

    return {
        "filename": filename,
        "characters_extracted": len(text),
        "total_chunks": len(chunks),
        "total_chunks_in_db": get_collection_count(),
        "message": "PDF processed and stored successfully! This is now the active document.",
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    active_document = get_active_document()
    if not active_document:
        raise HTTPException(
            status_code=409,
            detail="Upload a PDF before asking a question.",
        )
    document_id = active_document["document_id"]

    result = run_rag_pipeline(question, document_id=document_id, top_k=5)
    return {
        "question": question,
        "filename": active_document["filename"],
        "answer": result["answer"] or NO_INFO_ANSWER,
        "retrieved_chunks": result["retrieved_chunks"],
        "distances": result["distances"],
        "retries_used": result["retries_used"],
        "attempts": result["attempts"],
    }
