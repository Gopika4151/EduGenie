import logging
import time
from typing import List, Optional

from google import genai
from google.genai import types

from config import get_settings

logger = logging.getLogger("edugenie.gemini_client")


class GeminiConfigurationError(RuntimeError):
    pass


# Supported models known to work with the Gemini API for automatic fallback
DEFAULT_FALLBACK_MODELS = [
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
]


def get_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is not configured. Please add your Google Gemini API key to .env."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def _normalize_model_name(name: str) -> str:
    name = name.strip()
    if name.startswith("models/"):
        name = name[len("models/"):]
    return name


def generate_text(
    prompt: str,
    *,
    model: Optional[str] = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
    response_mime_type: str | None = None,
) -> str:
    settings = get_settings()

    # 1. Determine requested/primary model
    requested_model = (
        model.strip() if (model and model.strip()) else settings.gemini_model
    )
    primary_model = _normalize_model_name(requested_model)

    # 2. Build candidate fallback chain starting with primary model
    models_to_try: List[str] = [primary_model]
    for fb in DEFAULT_FALLBACK_MODELS:
        if fb != primary_model and fb not in models_to_try:
            models_to_try.append(fb)

    config_kwargs = {
        "temperature": settings.temperature if temperature is None else temperature,
        "max_output_tokens": (
            settings.max_output_tokens
            if max_output_tokens is None
            else max_output_tokens
        ),
    }
    if response_mime_type:
        config_kwargs["response_mime_type"] = response_mime_type

    client = get_client()
    last_exception = None
    attempted_log = []

    for current_model in models_to_try:
        max_attempts = 2  # Retry once on transient issues (503 / 429) before fallback
        for attempt in range(1, max_attempts + 1):
            try:
                response = client.models.generate_content(
                    model=current_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs),
                )

                if hasattr(response, "text") and response.text:
                    if current_model != primary_model:
                        logger.warning(
                            "Primary model '%s' was unavailable; successfully used fallback model '%s'.",
                            primary_model,
                            current_model,
                        )
                    return response.text.strip()

                if hasattr(response, "candidates") and response.candidates:
                    finish_reason = getattr(
                        response.candidates[0], "finish_reason", "UNKNOWN"
                    )
                    raise RuntimeError(
                        f"Gemini returned an empty response (finish reason: {finish_reason})."
                    )

                raise RuntimeError("Gemini returned an empty response.")

            except Exception as e:
                last_exception = e
                err_msg = str(e)
                status_code = getattr(e, "code", None)

                # Transient errors: 503 (High demand/Unavailable), 429 (Rate limit/Resource exhausted), 500, 502, 504
                is_transient = (
                    status_code in (429, 500, 502, 503, 504)
                    or "503" in err_msg
                    or "429" in err_msg
                    or "500" in err_msg
                    or "UNAVAILABLE" in err_msg
                    or "high demand" in err_msg.lower()
                    or "RESOURCE_EXHAUSTED" in err_msg
                )

                # Model discontinued / not found / deprecated
                is_not_found = (
                    status_code == 404
                    or "404" in err_msg
                    or "NOT_FOUND" in err_msg
                    or "no longer available" in err_msg.lower()
                )

                attempted_log.append(f"{current_model} (attempt {attempt}: {err_msg[:90]})")

                if is_transient and attempt < max_attempts:
                    time.sleep(attempt * 1.5)
                    continue

                if is_transient or is_not_found:
                    # Proceed to next model in fallback list
                    logger.warning(
                        "Model '%s' failed (attempt %d/%d, error: %s). Falling back to next model.",
                        current_model,
                        attempt,
                        max_attempts,
                        err_msg[:120],
                    )
                    break
                else:
                    # Non-recoverable error (e.g. invalid API key or configuration error)
                    raise RuntimeError(f"AI Service Error: {err_msg}") from e

    # If all models in the fallback chain were exhausted
    raise RuntimeError(
        f"AI Service Error: All attempted models failed. "
        f"Selected model was '{primary_model}'. "
        f"Details: {str(last_exception)}"
    )