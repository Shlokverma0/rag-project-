def refine_query(original_question: str) -> str:
    """
    Simple query refinement - question ko thoda broad/descriptive bana dete hain
    taaki retrieval better chunks dhoond sake.
    """
    refined = (
        f"Find information related to: {original_question}. "
        f"Include any relevant details, facts, or context about this topic "
        f"from the document."
    )
    return refined