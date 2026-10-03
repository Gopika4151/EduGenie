from functools import lru_cache

from config import get_settings
from gemini_client import generate_text


@lru_cache
def _load_local_pipeline():
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise RuntimeError(
            "Local explanation requires the optional dependencies in "
            "requirements-local.txt. Install them or set USE_LOCAL_EXPLANATION=false."
        ) from exc

    settings = get_settings()
    return pipeline(
        "text2text-generation",
        model=settings.local_explanation_model,
        tokenizer=settings.local_explanation_model,
        device=-1,
    )


def _local_explanation(topic: str) -> str:
    pipe = _load_local_pipeline()
    prompt = (
        "Explain the following topic to a beginner in simple language. "
        "Use a short definition, 3-5 key points, and one simple example. "
        f"Topic: {topic}"
    )
    result = pipe(prompt, max_new_tokens=220, do_sample=False)
    return result[0]["generated_text"].strip()


def _gemini_explanation(topic: str, model: str | None = None) -> str:
    prompt = f"""You are EduGenie, an educational tutor.
Explain the topic below to a beginner.
Structure the answer as:
1. Simple definition
2. Key points
3. One easy example
Keep it clear and concise.

Topic:
{topic}"""
    return generate_text(prompt, model=model)


def explain_topic(topic: str, model: str | None = None) -> str:
    settings = get_settings()
    if settings.use_local_explanation:
        return _local_explanation(topic)
    return _gemini_explanation(topic, model=model)

