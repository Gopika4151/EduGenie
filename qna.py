from gemini_client import generate_text

SYSTEM_PROMPT = """You are EduGenie, a concise educational assistant.
Answer the learner's question accurately and clearly.
Use simple language suitable for a student.
When useful, use short bullet points or a small example.
Do not invent citations or claim certainty when the answer is uncertain.
"""


def answer_question(question: str, model: str | None = None) -> str:
    prompt = f"""{SYSTEM_PROMPT}

Student question:
{question}

Give a direct educational answer."""
    return generate_text(prompt, model=model)

