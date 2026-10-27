"""Step 5a: LLM wrapper - Gemini or OpenAI, chosen by LLM_PROVIDER."""
from . import config


class LLMNotConfigured(RuntimeError):
    pass


def generate(system: str, prompt: str) -> str:
    if config.LLM_PROVIDER == "openai":
        if not config.OPENAI_API_KEY:
            raise LLMNotConfigured("OPENAI_API_KEY is not set in .env")
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            temperature=0.1,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""

    if not config.GEMINI_API_KEY:
        raise LLMNotConfigured("GEMINI_API_KEY is not set in .env")
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    resp = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system, temperature=0.1),
    )
    return resp.text or ""
