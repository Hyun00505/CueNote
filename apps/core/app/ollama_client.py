import json
import logging
from typing import Any
from urllib import request

try:
    from .json_extract import extract_first_json
except ImportError:
    from json_extract import extract_first_json

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "smollm2:1.7b"

logger = logging.getLogger("cuenote.core")


def generate(prompt: str, temperature: float = 0.0, num_ctx: int = 4096) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": num_ctx},
    }
    req = request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=60) as response:
        body = response.read().decode("utf-8")
    data = json.loads(body)
    return data.get("response", "")


def call_json(prompt: str, schema_hint: str) -> Any:
    text = generate(prompt)
    try:
        json_text = extract_first_json(text)
        return json.loads(json_text)
    except Exception as exc:
        logger.warning("JSON parse failed, retrying once: %s", exc)
        repair_prompt = (
            "Return ONLY valid JSON that matches this schema hint.\n"
            f"Schema hint: {schema_hint}\n"
            "If you need to correct formatting, do so silently.\n\n"
            f"Original prompt:\n{prompt}"
        )
        text = generate(repair_prompt)
        json_text = extract_first_json(text)
        return json.loads(json_text)
