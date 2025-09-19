import os, json, re
from typing import Optional, Dict, Any, List

def set_api_key_from_env() -> Optional[str]:
    key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY") or os.getenv("OPENAI_KEY")
    return key

def have_openai() -> bool:
    try:
        import openai  # noqa: F401
        return True
    except Exception:
        return False

def call_openai_json(prompt: str, model: str = "gpt-4.1-mini", temperature: float = 0.2) -> Optional[dict]:
    """Ask for JSON; be defensive about parsing across SDK versions."""
    if not set_api_key_from_env() or not have_openai():
        return None
    try:
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": "You are a precise JSON generator. Always return strict JSON."},
                {"role": "user", "content": prompt},
            ]
        )
        raw = resp.choices[0].message.content
        match = re.search(r"\{.*\}|\[.*\]", raw, re.S)
        text = match.group(0) if match else raw
        return json.loads(text)
    except Exception:
        return None

def llm_resume_analysis(resume_text: str, jd_text: str, model: str = "gpt-4.1-mini", temperature: float = 0.2) -> Optional[Dict[str, Any]]:
    # Build the prompt without nested triple quotes (fixes SyntaxError)
    prompt = (
        "Return JSON with keys skills, strengths, gaps, improvements, missing_keywords.\n\n"
        "JOB DESCRIPTION:\n"
        f"{jd_text}\n\n"
        "RESUME:\n"
        f"{resume_text}\n"
    )
    out = call_openai_json(prompt=prompt, model=model, temperature=temperature)
    return out
