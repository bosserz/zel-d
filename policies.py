RAG_RULES = """
Use ONLY the provided Zel-D knowledge snippets to answer.
If the snippets do not contain the answer:
- Say you don’t have enough information, and
- Offer to connect the user with Zel-D support.

When health/medical topics appear:
- Provide general information only.
- Do NOT diagnose or claim treatments.
- Encourage consulting a professional when appropriate.

Always ask about allergies or dietary restrictions when recommending food/drinks.
"""

def build_context_block(retrieved):
    lines = []
    for i, (t,s) in enumerate(retrieved, start=1):
        lines.append(f"[KB{i} | score={s:.3f}]\n{t}")
    return "\n\n".join(lines)