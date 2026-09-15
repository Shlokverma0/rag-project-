from groq import Groq
from backend.config import GROQ_API_KEY
from backend.services.retriever import retrieve_relevant_chunks
from backend.services.evaluator import is_context_sufficient, answer_indicates_no_info
from backend.services.planner import refine_query

client = Groq(api_key=GROQ_API_KEY)

LLM_MODEL = "openai/gpt-oss-20b"
MAX_RETRIES = 2


def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are a helpful assistant answering questions based ONLY on the provided document context.

RULES:
- Answer only using the information in the context below.
- If the answer is not present in the context, say: "I couldn't find enough information in the uploaded document to answer this question."
- Do not invent or assume information that is not in the context.
- Keep the answer clear and concise.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

    return prompt


def generate_answer(question: str, context_chunks: list[str]) -> str:
    prompt = build_prompt(question, context_chunks)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500
    )

    return response.choices[0].message.content


def run_rag_pipeline(question: str, top_k: int = 3) -> dict:
    """
    Agentic RAG pipeline:
    Attempt 1: normal retrieval
    Agar weak context -> query refine karke Attempt 2
    Max 2 attempts, phir honest "not found" message
    """
    current_query = question
    attempts_log = []  # debug/transparency ke liye - kya hua har attempt mein

    for attempt in range(1, MAX_RETRIES + 1):
        retrieval_result = retrieve_relevant_chunks(current_query, top_k=top_k)
        chunks = retrieval_result["chunks"]
        distances = retrieval_result["distances"]

        context_ok = is_context_sufficient(distances)

        attempts_log.append({
            "attempt": attempt,
            "query_used": current_query,
            "context_sufficient": context_ok
        })

        if not chunks or not context_ok:
            # Context weak hai - agar aur retry bacha hai, query refine karo
            if attempt < MAX_RETRIES:
                current_query = refine_query(question)
                continue
            else:
                return {
                    "answer": "I couldn't find enough information in the uploaded document to answer this question.",
                    "retrieved_chunks": chunks,
                    "distances": distances,
                    "attempts": attempts_log,
                    "retries_used": attempt
                }

        # Context sufficient hai - answer generate karo
        answer = generate_answer(question, chunks)

        # Check karo LLM ne khud "nahi mila" bola kya
        if answer_indicates_no_info(answer) and attempt < MAX_RETRIES:
            current_query = refine_query(question)
            continue

        return {
            "answer": answer,
            "retrieved_chunks": chunks,
            "distances": distances,
            "attempts": attempts_log,
            "retries_used": attempt
        }

    # Fallback (yaha normally nahi pahunchega, but safety ke liye)
    return {
        "answer": "I couldn't find enough information in the uploaded document to answer this question.",
        "retrieved_chunks": [],
        "distances": [],
        "attempts": attempts_log,
        "retries_used": MAX_RETRIES
    }