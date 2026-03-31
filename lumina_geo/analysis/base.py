from abc import ABC, abstractmethod

from lumina_geo.llm.gemini_client import call_gemini
from lumina_geo.reporting.models import LensResult

SYSTEM_PROMPT = (
    "Act as a Search Engine LLM Crawler analyzing content for GEO "
    "(Generative Engine Optimization) readiness. "
    "You MUST respond with valid JSON only — no markdown fences, no commentary."
)


class BaseLens(ABC):
    @abstractmethod
    def analyze(self, content: str) -> LensResult:
        ...

    def _call(self, content: str, lens_instructions: str) -> str:
        prompt = f"{SYSTEM_PROMPT}\n\n{lens_instructions}\n\nCONTENT:\n{content}"
        return call_gemini(prompt)
