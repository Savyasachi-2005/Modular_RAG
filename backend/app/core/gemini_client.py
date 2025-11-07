import json
import requests
from typing import Optional

from .config import settings


def generate_with_gemini(prompt: str) -> str:
    """
    Try to generate text using the Google Generative AI Python client if it is
    installed. If not available, fall back to the public REST endpoint using an
    API key from settings.gemini_api_key.
    """
    if not settings.gemini_api_key:
        return "[gemini_error] no api key configured"

    model = settings.gemini_model or "gemini-1"

    # Try the official Python client first (if installed)
    try:
        import google.generativeai as genai  # type: ignore

        try:
            genai.configure(api_key=settings.gemini_api_key)
        except Exception:
            # some client versions may not need configure or use different API
            pass

        # Try simple generate_text API
        try:
            resp = genai.generate_text(
                model=model,
                prompt=prompt,
                temperature=float(getattr(settings, "openai_temperature", 0.2)),
                max_output_tokens=int(getattr(settings, "openai_max_tokens", 1024)),
            )
            if isinstance(resp, dict):
                if "candidates" in resp and isinstance(resp["candidates"], list) and len(resp["candidates"]) > 0:
                    cand = resp["candidates"][0]
                    return cand.get("output") or cand.get("content") or cand.get("text") or json.dumps(cand)
                return resp.get("output") or resp.get("content") or json.dumps(resp)
            return str(resp)
        except Exception:
            # Try the responses-style API
            try:
                resp = genai.responses.generate(
                    model=model,
                    input=prompt,
                    temperature=float(getattr(settings, "openai_temperature", 0.2)),
                    max_output_tokens=int(getattr(settings, "openai_max_tokens", 1024)),
                )
                cands = getattr(resp, "candidates", None)
                if cands and len(cands) > 0:
                    c0 = cands[0]
                    content = getattr(c0, "content", None)
                    if content:
                        if isinstance(content, list):
                            parts = []
                            for p in content:
                                if isinstance(p, dict):
                                    parts.append(p.get("text") or p.get("content") or str(p))
                                else:
                                    parts.append(str(p))
                            return "".join(parts)
                        return str(content)
                return str(resp)
            except Exception as e_resp:
                return f"[gemini_genai_error] {str(e_resp)}"
    except ImportError:
        # Fallback to REST call using API key
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta2/models/{model}:generateText?key={settings.gemini_api_key}"
            payload = {
                "prompt": {"text": prompt},
                "temperature": float(getattr(settings, "openai_temperature", 0.2)),
                "maxOutputTokens": int(getattr(settings, "openai_max_tokens", 1024)),
            }
            resp = requests.post(url, json=payload, timeout=20)
            if resp.ok:
                data = resp.json()
                if isinstance(data, dict):
                    if "candidates" in data and isinstance(data["candidates"], list) and len(data["candidates"]) > 0:
                        cand = data["candidates"][0]
                        return cand.get("output") or cand.get("content") or cand.get("text") or json.dumps(cand)
                    return data.get("output") or data.get("content") or json.dumps(data)
                return str(data)
            else:
                return f"[gemini_error] {resp.status_code}: {resp.text}"
        except Exception as exc:
            return f"[gemini_exception] {str(exc)}"

