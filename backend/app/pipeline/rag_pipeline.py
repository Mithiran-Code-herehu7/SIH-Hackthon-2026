from app.llm.provider import get_llm_provider
from app.rag.service import search_documents


def answer_with_rag(
    query: str,
    top_k: int = 5,
) -> tuple[str, list[dict]]:
    results = search_documents(
        query,
        top_k,
    )

    if not results:
        return (
            "No relevant information was found in the indexed documents.",
            [],
        )

    context = "\n\n".join(
        result["text"]
        for result in results
    )

    prompt = f"""Answer the user's question using only the provided context.

Context:
{context}

User question:
{query}

Answer:"""

    llm = get_llm_provider()

    response = llm.generate(prompt)

    sources = [
        {
            "file_id": result["file_id"],
            "filename": result["filename"],
            "chunk_index": result["chunk_index"],
            "score": result["score"],
        }
        for result in results
    ]

    return response, sources