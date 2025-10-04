import requests
from typing import Dict, Any, Optional
import os, json
from cerebras.cloud.sdk import Cerebras

GITHUB_API = "https://api.github.com"

def github_get(url: str, token: Optional[str] = None, params: dict = None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    r = requests.get(url, headers=headers, params=params or {}, timeout=30)
    r.raise_for_status()
    return r.json()

def call_gemini(prompt: str, gemini_token: str, model: str = "gemini-standard", max_tokens:int=512) -> Dict[str, Any]:
    """
    Placeholder Gemini API call. Replace endpoint and payload with the real Gemini HTTP API or official client.
    """
    if not gemini_token:
        raise ValueError("Gemini token required for LLM calls")
    # Example/placeholder:
    url = os.getenv("GEMINI_ENDPOINT", "https://api.gemini.example/v1/generate")
    headers = {"Authorization": f"Bearer {gemini_token}", "Content-Type": "application/json"}
    body = {"model": model, "prompt": prompt, "max_tokens": max_tokens}
    r = requests.post(url, json=body, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def call_cerebras(prompt: str, cerebras_token: str, model: str = "llama3.1-8b", max_tokens:int=512) -> Dict[str, Any]:
    client = Cerebras(api_key=cerebras_token)

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model=model,
        max_tokens=max_tokens,
    )

    return chat_completion.dict()

