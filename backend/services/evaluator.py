def answer_indicates_no_info(answer: str) -> bool:
    """Recognize the pipeline's standard answer when context lacks the requested fact."""
    answer_lower = answer.lower()
    no_info_phrases = (
        "couldn't find enough information",
        "not present in the context",
        "cannot find",
        "no information",
        "not mentioned in the",
    )
    return any(phrase in answer_lower for phrase in no_info_phrases)
