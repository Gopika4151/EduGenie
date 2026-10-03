import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    @property
    def app_name(self) -> str:
        return os.getenv("APP_NAME", "EduGenie")

    @property
    def gemini_api_key(self) -> str:
        return os.getenv("GEMINI_API_KEY", "").strip()

    @property
    def gemini_model(self) -> str:
        return os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

    @property
    def use_local_explanation(self) -> bool:
        return os.getenv("USE_LOCAL_EXPLANATION", "false").lower() == "true"

    @property
    def local_explanation_model(self) -> str:
        return os.getenv("LOCAL_EXPLANATION_MODEL", "MBZUAI/LaMini-Flan-T5-783M").strip()

    @property
    def max_output_tokens(self) -> int:
        return int(os.getenv("MAX_OUTPUT_TOKENS", "1200"))

    @property
    def temperature(self) -> float:
        return float(os.getenv("TEMPERATURE", "0.3"))


def get_settings() -> Settings:
    # Reload dotenv so changes to .env take effect immediately
    load_dotenv(override=True)
    return Settings()

