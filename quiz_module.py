import json
import re

from gemini_client import generate_text


def clean_json_block(text: str) -> str:
    """Remove Markdown fences and isolate the first JSON array/object."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()

    array_start = cleaned.find("[")
    array_end = cleaned.rfind("]")
    if array_start >= 0 and array_end > array_start:
        return cleaned[array_start : array_end + 1]

    object_start = cleaned.find("{")
    object_end = cleaned.rfind("}")
    if object_start >= 0 and object_end > object_start:
        return cleaned[object_start : object_end + 1]

    return cleaned


def _validate_quiz(data):
    if not isinstance(data, list):
        raise ValueError("Quiz response must be a JSON array.")
    if len(data) != 3:
        raise ValueError("Quiz response must contain exactly 3 questions.")

    validated = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Question {index} is not an object.")

        question = str(item.get("question", "")).strip()
        options = item.get("options")
        answer = str(item.get("correct_answer", "")).strip()

        if not question or not isinstance(options, list) or len(options) != 4:
            raise ValueError(
                f"Question {index} must have a question and exactly 4 options."
            )
        options = [str(option).strip() for option in options]
        if any(not option for option in options):
            raise ValueError(f"Question {index} contains an empty option.")
        if answer not in options:
            raise ValueError(
                f"Question {index} correct_answer must match one of its options."
            )

        validated.append(
            {
                "question": question,
                "options": options,
                "correct_answer": answer,
            }
        )
    return validated


def generate_quiz(passage: str, model: str | None = None):
    prompt = f"""Create exactly 3 multiple-choice questions from the educational passage below.

Rules:
- Return ONLY valid JSON.
- Return a JSON array with exactly 3 objects.
- Each object must contain:
  "question": string,
  "options": [exactly 4 strings],
  "correct_answer": string
- correct_answer must exactly match one option.
- Questions must test understanding of the passage.
- Do not add explanations outside the JSON.

Passage:
{passage}"""

    raw = generate_text(
        prompt,
        model=model,
        temperature=0.2,
        max_output_tokens=1400,
        response_mime_type="application/json",
    )
    data = json.loads(clean_json_block(raw))
    return _validate_quiz(data)

