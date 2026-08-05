class PromptBuilder:
    """
    Builds prompts for ScholarMind AI.

    The prompt contains:
    - system instruction
    - retrieved context
    - user question
    """

    SYSTEM_PROMPT = """
You are ScholarMind AI.

You answer questions ONLY from the supplied research paper.

Rules:

1. Use ONLY the supplied context.

2. Never invent facts.

3. If the answer is unavailable, say:

"I couldn't find this information in the paper."

4. Cite sources by their source number when possible.

5. Be concise but informative.
"""

    @staticmethod
    def build(question: str, context: str):

        return f"""
{PromptBuilder.SYSTEM_PROMPT}

==============================
Context
==============================

{context}

==============================
Question
==============================

{question}

==============================
Answer
==============================
Return a direct answer first, then a short source list.
"""