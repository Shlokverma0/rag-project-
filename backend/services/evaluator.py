def is_context_sufficient(distances: list[float], threshold: float = 1.3) -> bool:
    """
    Distance check - agar sabse relevant chunk ka distance bhi threshold se zyada hai,
    matlab context weak hai (kuch bhi relevant nahi mila).
    Lower distance = zyada relevant (ChromaDB cosine distance use karta hai).
    """
    if not distances:
        return False

    best_distance = min(distances)
    return best_distance <= threshold


def answer_indicates_no_info(answer: str) -> bool:
    """
    Check karta hai ki LLM ka answer khud bol raha hai ki
    usko info nahi mili (hamare prompt ke rule ke hisaab se).
    """
    no_info_phrases = [
        "couldn't find enough information",
        "not present in the context",
        "cannot find",
        "no information",
        "not mentioned in the"
    ]
    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in no_info_phrases)