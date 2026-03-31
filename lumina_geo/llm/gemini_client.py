import random
import time

import google.generativeai as genai

from lumina_geo.config import settings

genai.configure(api_key=settings.gemini_api_key)


_GENERATION_CONFIG = genai.GenerationConfig(temperature=0)


def call_gemini(prompt: str, max_retries: int = 5) -> str:
    model = genai.GenerativeModel(settings.gemini_model)
    last_exc: Exception | None = None

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt, generation_config=_GENERATION_CONFIG)
            return response.text
        except Exception as exc:
            last_exc = exc
            if attempt == max_retries - 1:
                break
            wait = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait)

    raise RuntimeError(
        f"Gemini API call failed after {max_retries} attempts: {last_exc}"
    ) from last_exc
