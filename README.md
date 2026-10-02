# RAG PDF Q&A System

A small Retrieval-Augmented Generation (RAG) API that accepts text-based PDF files, stores document chunks in a persistent local ChromaDB collection, and answers questions using retrieved context and the Groq API.

> **Project status:** Learning prototype. It has not been load-tested or evaluated for answer accuracy. Do not use it for high-stakes decisions or confidential documents.

## How it works

```text
PDF upload
   -> validate file type and size (20 MB maximum)
   -> extract text with PyMuPDF
   -> split text into 500-character chunks with 50-character overlap
   -> create embeddings with all-MiniLM-L6-v2
   -> save chunks and embeddings in local ChromaDB

Question
   -> embed the question
   -> retrieve the top 3 matching chunks
   -> check context distance; refine and retry when context looks weak
   -> ask Groq to answer from the retrieved context only
   -> return the answer, chunks, distances, and retry details
```

## Features

- PDF text extraction with PyMuPDF (`pymupdf`)
- Character-based chunking with overlap
- Local sentence embeddings using `all-MiniLM-L6-v2`
- Persistent vector storage with ChromaDB
- Context-grounded responses through Groq (`openai/gpt-oss-20b`)
- Basic retrieval retry and context sufficiency checks
- Interactive API documentation through FastAPI / Swagger UI

## Technology

| Area | Technology |
| --- | --- |
| API | FastAPI |
| ASGI server | Uvicorn |
| PDF text extraction | PyMuPDF |
| Embeddings | Sentence Transformers, `all-MiniLM-L6-v2` |
| Vector store | ChromaDB, persisted under `backend/data/chroma_db` |
| Answer generation | Groq API, `openai/gpt-oss-20b` |
| Configuration | `python-dotenv` |

## Project structure

```text
rag-project/
├── backend/
│   ├── main.py                  # FastAPI endpoints
│   ├── config.py                # Environment configuration and upload limit
│   ├── data/
│   │   └── chroma_db/           # Local persistent vector database (generated)
│   └── services/
│       ├── pdf_loader.py        # Extract text from PDFs
│       ├── chunker.py           # Split extracted text into overlapping chunks
│       ├── embeddings.py        # Load the embedding model and encode text
│       ├── vector_store.py      # Persist and count ChromaDB chunks
│       ├── retriever.py         # Search for relevant chunks
│       ├── rag_pipeline.py     # Retrieval, retries, prompt, and answer generation
│       ├── planner.py           # Build a refined search query
│       └── evaluator.py         # Decide whether retrieved context is sufficient
├── requirements.txt
├── .env                         # Local secrets; do not commit
└── README.md
```

## Requirements

- Python 3.10 or newer
- A Groq API key
- Internet access the first time the embedding model is downloaded

## Setup

### Windows PowerShell

```powershell
cd C:\path\to\rag-project
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation in the current terminal, allow scripts for that process and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
cd /path/to/rag-project
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root (the same directory as `requirements.txt`) and add your Groq API key:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
```

Get a key from the [Groq Console](https://console.groq.com/). Keep `.env` private and never commit a real key. The embedding model is downloaded from Hugging Face on first use; a `HF_TOKEN` can optionally be configured in the environment for higher Hub rate limits.

## Run the API

From the project root, with the virtual environment active:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger UI. The server must remain running while you use the API.

## API

### `GET /health`

Returns a small status response when the API process is available.

### `POST /upload`

Upload a PDF as `multipart/form-data` with the field name `file`. The current endpoint checks the `.pdf` filename suffix, rejects empty files, and enforces a 20 MB maximum. It extracts text, chunks it, embeds the chunks, and stores them in ChromaDB.

Example response:

```json
{
  "filename": "rag-test-facts.pdf",
  "characters_extracted": 973,
  "total_chunks": 3,
  "total_chunks_in_db": 31,
  "message": "PDF processed and stored successfully!"
}
```

`total_chunks_in_db` is the count across the persistent collection, so it can include chunks from earlier uploads.

### `POST /ask`

Send a JSON question after uploading a document:

```json
{
  "question": "Which day is the library closed?"
}
```

Example response:

```json
{
  "question": "Which day is the library closed?",
  "answer": "The library is closed on Mondays.",
  "retrieved_chunks": ["Relevant document text..."],
  "distances": [1.28]
}
```

The endpoint returns the answer and the top 3 retrieved chunks with their ChromaDB distances. Lower distances indicate closer matches for the configured distance metric. The RAG pipeline tracks retry details internally, but the currently matched `/ask` route does not include those fields in its response.
## Quick test in Swagger

Use a text-based PDF. For a hands-on learning run, the synthetic `rag-test-facts.pdf` works well.

1. Start the server and open `/docs`.
2. Expand **GET `/health`**, click **Execute**, and inspect the status and JSON body.
3. Expand **POST `/upload`**, choose the PDF, and click **Execute**. Before looking at the response, predict what each field means. Then inspect `characters_extracted`, `total_chunks`, and `total_chunks_in_db`.
4. Read the PDF and write down what you think the answers are before asking the app.
5. Ask each question under **POST `/ask`**. For every result, compare `answer` with `retrieved_chunks`:

   - Which day is the library closed?
   - How many raised garden beds are there?
   - What does the community garden grow?
   - Who coordinates the garden volunteers?
   - How often does the ferry leave, and during what hours?
   - When is the Lantern Walk?
   - Where is the storm shelter?

6. Diagnose each result yourself:

   - Correct answer and a supporting chunk: upload, retrieval, and generation worked for that question.
   - Supporting fact is in `retrieved_chunks`, but the answer is wrong or says it is missing: retrieval found evidence; inspect answer generation and the context-sufficiency/retry logic.
   - Supporting fact is absent from retrieved chunks: inspect extraction, chunking, embeddings, and retrieval.
   - `total_chunks_in_db` is larger than `total_chunks`: ChromaDB contains chunks from earlier uploads too.

7. Try an unrelated question, such as “What is Pinebrook's population?” The expected behavior is to say the document does not provide that fact. If it invents an answer, record it as a hallucination case.
8. Try a `.txt` file with `/upload` and a blank question with `/ask`. Both should return a `400` validation error. A missing required field is normally reported as `422` by FastAPI.
9. Restart the server and ask another question. Existing ChromaDB data persists, so old chunks remain searchable.

### Answer key for the sample PDF

<details>
<summary>Open after you have tried answering from the PDF</summary>

- Library closure: Monday
- Garden beds: 24
- Garden crops: tomatoes, beans, and spinach
- Volunteer coordinator: Mira Patel
- Ferry: every 30 minutes, from 10:00 AM to 4:00 PM
- Lantern Walk: the second Friday of October
- Storm shelter: town hall

</details>

## Current limitations

- Scanned/image-only PDFs need OCR; this project currently extracts embedded text only.
- Chunks are stored persistently and retrieval searches the shared collection. There is no endpoint to delete a document or restrict a question to one uploaded filename.
- Chunk IDs are based on filename and chunk index. Uploading the same filename again may conflict with IDs already in ChromaDB.
- Retrieval and answer quality have not been formally evaluated. A relevant retrieved chunk does not guarantee that the LLM will always use it correctly.
- The API has no authentication, rate limiting, or user-level data isolation; it is intended for local learning and experimentation.
- Swagger reports a duplicate operation ID because `backend/main.py` registers `/ask` twice. The first matching route currently handles requests, so retry details computed by the pipeline are not included in the `/ask` response. Remove the duplicate registration and keep one handler.
- The model context retrieved from your documents is sent to Groq to generate answers. Avoid uploading confidential data unless you have reviewed the provider and data-handling requirements for your use case.

## Troubleshooting

- **`GROQ_API_KEY` error:** confirm `.env` is in the project root and contains a valid key; restart Uvicorn after changing it.
- **Hugging Face Hub unauthenticated warning:** the public embedding model can still download, but requests may have lower rate limits. Configure `HF_TOKEN` if needed.
- **Correct text appears in `retrieved_chunks`, but the answer says it cannot find it:** retrieval probably found context; inspect the RAG prompt, context sufficiency threshold, and generation response handling.
- **Old documents appear in results:** ChromaDB persists under `backend/data/chroma_db` and all stored chunks are currently searched together. Back up the folder before manually clearing local vector data.
- **`fitz` deprecation warning:** use the supported PyMuPDF import form in the PDF loader (`import pymupdf as fitz`) and ensure `pymupdf` is installed in the active virtual environment.

## Author and License

Created by **Shlok Verma**. Follow the project author on [GitHub](https://github.com/Shlokverma0).
