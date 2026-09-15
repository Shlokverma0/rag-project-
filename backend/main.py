from fastapi import FastAPI, UploadFile, File, HTTPException

from backend.services.pdf_loader import extract_text_from_pdf
from backend.config import MAX_FILE_SIZE_MB

app = FastAPI(title="RAG PDF Q&A System")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG backend is running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # File type check
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await file.read()

    # Size check
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB allowed.")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Extract text
    text = extract_text_from_pdf(file_bytes)

    return {
        "filename": file.filename,
        "characters_extracted": len(text),
        "preview": text[:300]  # sirf pehle 300 characters dikhayenge, poora nahi
    }

from fastapi import FastAPI, UploadFile, File, HTTPException

from backend.services.pdf_loader import extract_text_from_pdf
from backend.services.chunker import chunk_text
from backend.config import MAX_FILE_SIZE_MB

app = FastAPI(title="RAG PDF Q&A System")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG backend is running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await file.read()

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB allowed.")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Extract text
    text = extract_text_from_pdf(file_bytes)

    # Chunk text
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    return {
        "filename": file.filename,
        "characters_extracted": len(text),
        "total_chunks": len(chunks),
        "first_chunk_preview": chunks[0] if chunks else "",
        "second_chunk_preview": chunks[1] if len(chunks) > 1 else ""
    }

from fastapi import FastAPI, UploadFile, File, HTTPException

from backend.services.pdf_loader import extract_text_from_pdf
from backend.services.chunker import chunk_text
from backend.services.vector_store import store_chunks, get_collection_count
from backend.config import MAX_FILE_SIZE_MB

app = FastAPI(title="RAG PDF Q&A System")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG backend is running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await file.read()

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB allowed.")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Extract text
    text = extract_text_from_pdf(file_bytes)

    # Chunk text
    chunks = chunk_text(text, chunk_size=500, overlap=50)

    # Store in ChromaDB (embeddings automatically banenge is step mein)
    store_chunks(chunks, doc_id=file.filename)

    return {
        "filename": file.filename,
        "characters_extracted": len(text),
        "total_chunks": len(chunks),
        "total_chunks_in_db": get_collection_count(),
        "message": "PDF processed and stored successfully!"
    }

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend.services.pdf_loader import extract_text_from_pdf
from backend.services.chunker import chunk_text
from backend.services.vector_store import store_chunks, get_collection_count
from backend.services.retriever import retrieve_relevant_chunks
from backend.config import MAX_FILE_SIZE_MB

app = FastAPI(title="RAG PDF Q&A System")


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG backend is running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await file.read()

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB allowed.")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    store_chunks(chunks, doc_id=file.filename)

    return {
        "filename": file.filename,
        "characters_extracted": len(text),
        "total_chunks": len(chunks),
        "total_chunks_in_db": get_collection_count(),
        "message": "PDF processed and stored successfully!"
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    if not request.question or request.question.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = retrieve_relevant_chunks(request.question, top_k=3)

    return {
        "question": request.question,
        "retrieved_chunks": result["chunks"],
        "distances": result["distances"]
    }

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend.services.pdf_loader import extract_text_from_pdf
from backend.services.chunker import chunk_text
from backend.services.vector_store import store_chunks, get_collection_count
from backend.services.rag_pipeline import run_rag_pipeline
from backend.config import MAX_FILE_SIZE_MB

app = FastAPI(title="RAG PDF Q&A System")


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RAG backend is running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = await file.read()

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB allowed.")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    store_chunks(chunks, doc_id=file.filename)

    return {
        "filename": file.filename,
        "characters_extracted": len(text),
        "total_chunks": len(chunks),
        "total_chunks_in_db": get_collection_count(),
        "message": "PDF processed and stored successfully!"
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    if not request.question or request.question.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = run_rag_pipeline(request.question, top_k=3)

    return {
        "question": request.question,
        "answer": result["answer"],
        "retrieved_chunks": result["retrieved_chunks"],
        "distances": result["distances"]
    }

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    if not request.question or request.question.strip() == "":
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = run_rag_pipeline(request.question, top_k=3)

    return {
        "question": request.question,
        "answer": result["answer"],
        "retrieved_chunks": result["retrieved_chunks"],
        "distances": result["distances"],
        "retries_used": result["retries_used"],
        "attempts": result["attempts"]
    }