from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ApiError(RuntimeError):
    pass


def generate_json(
    *, api_url: str, model: str, system: str, prompt: str, api_key: str | None = None
) -> dict[str, Any]:
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ApiError("OPENAI_API_KEY が設定されていません")

    body = json.dumps({
        "model": model,
        "instructions": system,
        "input": prompt,
        "text": {"format": {"type": "json_object"}},
    }).encode("utf-8")
    request = Request(
        api_url,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=180) as response:
            payload = json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:1000]
        raise ApiError(f"APIエラー ({error.code}): {detail}") from error
    except (URLError, TimeoutError) as error:
        raise ApiError(f"APIへ接続できません: {error}") from error

    text = payload.get("output_text") or _extract_output_text(payload)
    if not text:
        raise ApiError("APIレスポンスにテキスト出力がありません")
    try:
        result = json.loads(text)
    except json.JSONDecodeError as error:
        raise ApiError("API出力が有効なJSONではありません") from error
    if not isinstance(result, dict):
        raise ApiError("API出力の最上位はJSONオブジェクトである必要があります")
    return result


def _extract_output_text(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                parts.append(content["text"])
    return "".join(parts)
