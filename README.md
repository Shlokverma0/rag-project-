markdown
# 📄 PDF RAG Q&A System

A Retrieval-Augmented Generation (RAG) based question-answering system that lets you upload a PDF and ask questions about its content. The system retrieves relevant sections from the document and uses an LLM (via Groq) to generate accurate, context-grounded answers — with basic agentic retry logic when the first retrieval attempt doesn't find enough relevant information.

---

## 🚀 Features

- Upload any text-based PDF document
- Automatic text extraction, cleaning, and chunking
- Semantic search using vector embeddings (ChromaDB)
- Context-grounded answer generation using Groq LLM
- Basic agentic retry logic: if initial retrieval is weak, the system refines the query and retries (max 2 attempts) before returning an honest "not found" response
- Prevents hallucination — answers are generated only from retrieved document context
- Interactive API testing via Swagger UI

> ⚠️ This is a basic/academic implementation built for learning purposes. No accuracy or performance metrics have been formally measured.

---

## 🏗️ Architecture

User uploads PDF
↓
FastAPI receives PDF
↓
Text extraction (PyMuPDF)
↓
Text chunking (with overlap)
↓
Generate embeddings (Sentence Transformers)
↓
Store embeddings in ChromaDB
↓
User asks a question
↓
Question converted into embedding
↓
Relevant chunks retrieved (top-k similarity search)
↓
Check if retrieved context is sufficient
↓
Not sufficient → refine query → retry (max 2 attempts)
↓
Context sent to Groq LLM along with question
↓
LLM generates final answer
↓
Answer returned to user


---

## 🛠️ Tech Stack

| Component        | Technology                         |
|-------------------|-------------------------------------|
| Backend Framework | FastAPI                            |
| Server            | Uvicorn                            |
| PDF Processing    | PyMuPDF                            |
| Embeddings        | Sentence-Transformers (all-MiniLM-L6-v2) |
| Vector Database   | ChromaDB                           |
| LLM               | Groq API (openai/gpt-oss-20b)      |
| Config Management | python-dotenv                      |

---

## 📁 Folder Structure

rag-project/
│
├── backend/
│ ├── main.py
│ ├── config.py
│ │
│ ├── services/
│ │ ├── pdf_loader.py
│ │ ├── chunker.py
│ │ ├── embeddings.py
│ │ ├── vector_store.py
│ │ ├── retriever.py
│ │ ├── rag_pipeline.py
│ │ ├── planner.py
│ │ └── evaluator.py
│ │
│ └── data/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md


---

## ⚙️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/rag-project.git
cd rag-project
```

2. **Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables** (see below)

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

GROQ_API_KEY=your_groq_api_key_here


Get a free API key from [Groq Console](https://console.groq.com).

---

## ▶️ How to Run

```bash
uvicorn backend.main:app --reload --port 8000
```

Then open:

http://127.0.0.1:8000/docs


This opens the Swagger UI, where you can interact with all API endpoints directly.

---

## 📡 API Endpoints

### `GET /health`
Simple health check to confirm the backend is running.

### `POST /upload`
Upload a PDF file. Extracts text, chunks it, generates embeddings, and stores them in ChromaDB.

**Response:**
```json
{
  "filename": "example.pdf",
  "characters_extracted": 5645,
  "total_chunks": 13,
  "total_chunks_in_db": 13,
  "message": "PDF processed and stored successfully!"
}
```

### `POST /ask`
Ask a question about the uploaded document.

**Request:**
```json
{ "question": "What is the candidate's machine learning experience?" }
```

**Response:**
```json
{
  "question": "...",
  "answer": "...",
  "retrieved_chunks": ["...", "...", "..."],
  "distances": [0.45, 0.62, 0.71],
  "retries_used": 1,
  "attempts": [{"attempt": 1, "query_used": "...", "context_sufficient": true}]
}
```

If the document doesn't contain relevant information even after retry, the system responds honestly instead of guessing.

---

## 🔮 Future Improvements

- React frontend
- Multi-document support
- Authentication
- Streaming LLM responses
- Formal evaluation metrics
- Cloud deployment
- OCR support for scanned PDFs

---

## ⚠️ Notes

- Basic academic implementation built under time constraints — not production-optimized.
- No formal accuracy/performance benchmarks have been measured.
- Retry logic uses a simple distance-threshold + keyword check.