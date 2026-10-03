from gemini_client import generate_text


def summarize_text(text: str, model: str | None = None) -> str:
    prompt = f"""You are EduGenie, a study assistant.
Summarize the following educational passage for quick revision.
Preserve the important facts and relationships.
Remove repetition and unnecessary wording.
Use a short paragraph followed by bullet points when appropriate.

Passage:
{text}"""
    return generate_text(prompt, model=model, max_output_tokens=900)

