DEFAULT_PROMPT = (
    "Answer the user's question based on the information provided in the document context below.\n"
    "Your response should reference the context clearly, but you may paraphrase or summarize appropriately.\n"
    "When asked in Korean, respond in Korean; when asked in English, respond in English."
)


def build_prompt(context_pages: list, user_query: str) -> str:
    context = "\n\n".join(context_pages)
    prompt = (
        f"{DEFAULT_PROMPT}\n\n"
        "=== Document Context ===\n"
        f"{context}\n\n"
        "=== User Question ===\n"
        f"{user_query}\n\n"
        "=== Answer ==="
    )
    return prompt