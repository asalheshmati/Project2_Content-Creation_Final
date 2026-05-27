# llm_integration.py
"""OpenAI API integration for content generation."""

import os
from pathlib import Path

from openai import OpenAI

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(dotenv_path=None):
        """Minimal .env loader used when python-dotenv is unavailable."""
        if dotenv_path is None:
            return False

        env_file = Path(dotenv_path)
        if not env_file.exists():
            return False

        for line in env_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue

            key, value = stripped.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")

        return True


PROJECT_ROOT = Path(__file__).resolve().parents[1]
try:
    load_dotenv(PROJECT_ROOT / ".env", override=True)
except TypeError:
    load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()
DEFAULT_MODEL_CANDIDATES = (
    "gpt-4o-mini",
    "gpt-4.1-nano",
)


def validate_openai_configuration():
    """
    Check that the OpenAI API key is present before we start the app flow.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    placeholder_markers = (
        "your_api_key_here",
        "your-real-api-key",
        "your-re",
        "replace_me",
        "replace-me",
        "changeme",
        "change-me",
    )

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing from ai-content-creator/.env."
        )

    lowered_key = api_key.lower()
    if any(marker in lowered_key for marker in placeholder_markers):
        raise RuntimeError(
            "OPENAI_API_KEY still looks like a placeholder value in "
            "ai-content-creator/.env. Replace it with a real OpenAI API key."
        )


def generate_ai_response(prompt):
    """
    This function sends a prompt to the AI model and returns the response text.
    """
    configured_model = os.getenv("OPENAI_MODEL", "").strip()
    candidate_models = []

    if configured_model:
        candidate_models.append(configured_model)

    for model_name in DEFAULT_MODEL_CANDIDATES:
        if model_name not in candidate_models:
            candidate_models.append(model_name)

    last_error = None

    for model_name in candidate_models:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as exc:
            message = str(exc).lower()
            last_error = exc

            if "incorrect api key" in message or "invalid_api_key" in message:
                raise RuntimeError(
                    "OpenAI rejected the API key from ai-content-creator/.env. "
                    "Replace OPENAI_API_KEY with a valid key from the OpenAI dashboard."
                ) from exc

            model_access_errors = (
                "does not have access to model",
                "model_not_found",
            )
            if any(error_text in message for error_text in model_access_errors):
                continue

            raise

    raise RuntimeError(
        "None of the configured models are available for this project. "
        "Set OPENAI_MODEL in ai-content-creator/.env to a model your project "
        "can access, such as gpt-4o-mini or gpt-4.1-nano."
    ) from last_error
