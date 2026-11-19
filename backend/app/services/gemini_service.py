import time
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types
from google.genai.errors import APIError

from backend.app.core.config import settings
from backend.app.core.logging import logger

class GeminiServiceError(Exception):
    """Custom exception for Gemini LLM errors."""
    pass

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not configured in settings or environment.")

        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.primary_model = settings.GEMINI_MODEL
        self.candidate_models = [self.primary_model] + [
            m for m in settings.FALLBACK_MODELS if m != self.primary_model
        ]

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 2048,
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates content from Gemini with automatic fallback on transient 503 / rate limit errors.
        Returns:
            {"text": str, "model_used": str}
        """
        if not self.client:
            raise GeminiServiceError(
                "GEMINI_API_KEY is missing. Please set your GEMINI_API_KEY in the .env file."
            )

        models_to_try = [model_override] if model_override else self.candidate_models
        last_error = None

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            system_instruction=system_instruction
        )

        for model_name in models_to_try:
            try:
                logger.info(f"Invoking Gemini model: {model_name}...")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return {
                        "text": response.text.strip(),
                        "model_used": model_name
                    }
                else:
                    logger.warning(f"Empty response from model {model_name}")

            except APIError as e:
                last_error = e
                err_code = getattr(e, 'code', None)
                logger.warning(f"Model {model_name} returned API error ({err_code}): {e}")
                # If model is unavailable (503) or 404, fall back to next model
                if err_code in (503, 404, 429):
                    time.sleep(0.5)
                    continue
                else:
                    raise GeminiServiceError(f"Gemini API Error: {str(e)}") from e
            except Exception as e:
                last_error = e
                logger.warning(f"Error calling {model_name}: {e}")
                continue

        raise GeminiServiceError(
            f"All candidate Gemini models failed. Last error: {str(last_error)}"
        )
