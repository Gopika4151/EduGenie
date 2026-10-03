from gemini_client import generate_text


def get_learning_recommendations(
    topic: str, level: str = "beginner", model: str | None = None
) -> str:
    prompt = f"""You are EduGenie, a personalized learning-path designer.

Create a structured learning path for:
Topic: {topic}
Learner level: {level}

Include:
- A short goal statement
- Beginner -> intermediate -> advanced stages
- Suggested topics in each stage
- A practical project or exercise
- Approximate time for each stage
- Useful resource types such as official documentation, articles, books, or videos

Do not invent specific URLs. Keep the plan practical and adaptable."""
    return generate_text(prompt, model=model, max_output_tokens=1400)

