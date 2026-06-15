from __future__ import annotations
import re
import os
from typing import Protocol, runtime_checkable


def extract_score(text: str) -> float:
    """Parse a 0-100 score from an LLM audit reply.

    Prefers the mandated 'SCORE: <n>' suffix; falls back to the last number in
    the text, and finally to a neutral 50.0. Shared by every Auditor backend.
    """
    match = re.search(r"SCORE:\s*([0-9.]+)", text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    nums = re.findall(r"\b\d{1,3}(?:\.\d+)?\b", text)
    return float(nums[-1]) if nums else 50.0


@runtime_checkable
class Auditor(Protocol):
    """Layer 3 Auditor."""
    def audit(self, prompt: str) -> float: ...

class LLMAuditor:
    def __init__(self, backend="local", model_name="qwen2.5:7b-instruct", base_url="http://localhost:11434/v1"):
        self.backend = backend.lower()
        self.model_name = model_name
        self.base_url = base_url
        self.system_prompt = (
            "You are a strict, quantitative financial auditor (Layer 3 of Nova Engine). "
            "Your job is to read the provided macro context and 4-quarter fundamental data for a company, "
            "and output a fundamental risk score from 0 to 100. "
            "100 = flawless balance sheet and strong tailwinds. 0 = bankrupt or extremely toxic. "
            "You must include a brief rationale, and you MUST end your response exactly with 'SCORE: <number>'."
        )

    def audit(self, prompt: str) -> float:
        try:
            if self.backend == "local":
                return self._call_local(prompt)
            elif self.backend == "anthropic":
                return self._call_anthropic(prompt)
            elif self.backend == "gemini":
                return self._call_gemini(prompt)
            else:
                print(f"[Auditor] Unknown backend: {self.backend}, using stub logic.")
                return 35.0 if "FORD" in prompt else 80.0
        except Exception as e:
            print(f"[Auditor] Error calling {self.backend}: {e}")
            return 50.0  # Safe default on error

    def _extract_score(self, text: str) -> float:
        return extract_score(text)

    def _call_local(self, prompt: str) -> float:
        from openai import OpenAI
        client = OpenAI(base_url=self.base_url, api_key="ollama")
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=300
        )
        return self._extract_score(response.choices[0].message.content)

    def _call_anthropic(self, prompt: str) -> float:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1
        )
        return self._extract_score(response.content[0].text)

    def _call_gemini(self, prompt: str) -> float:
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=self.system_prompt)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.1, max_output_tokens=300)
        )
        return self._extract_score(response.text)

class StubAuditor:
    """Fallback stub for testing without API keys."""
    def audit(self, prompt: str) -> float:
        return 35.0 if "FORD" in prompt else 80.0


class NeutralAuditor:
    """Layer 3 that abstains (constant 50.0).

    Used for HISTORICAL REPLAY: the live LLM is far too slow for thousands of
    cycles, and point-in-time news/fundamentals aren't available — so Layer 3
    stays neutral and the scanner's point-in-time 32-marker signal drives the
    decision, keeping the generated dataset lookahead-free.
    """
    def audit(self, prompt: str) -> float:
        return 50.0
