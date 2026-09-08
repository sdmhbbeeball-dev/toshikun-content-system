from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

from .config import Settings


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    location: str
    message: str


NUMBER_RE = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)?(?:\s*(?:%|％|人|名|日|週|週間|か月|ヶ月|年|mg|g|ml|mL|µg|μg|ppm|倍))?")
RISKY_PATTERNS = {
    "medical_certainty": re.compile(r"(?:必ず|確実に|絶対に).{0,8}(?:治|効|改善|予防)|(?:治療|治癒)できる"),
    "causal_certainty": re.compile(r"(?:原因である|引き起こすことが証明|因果関係が証明)"),
}


def validate(content: dict[str, Any], manuscript: str, settings: Settings) -> list[Issue]:
    issues: list[Issue] = []
    for section, expected in settings.counts().items():
        items = content.get(section)
        if not isinstance(items, list):
            issues.append(Issue("error", "invalid_section", section, "配列がありません"))
            continue
        if len(items) != expected:
            issues.append(Issue("error", "wrong_count", section, f"{expected}件必要ですが{len(items)}件です"))
        for index, item in enumerate(items):
            location = f"{section}[{index}]"
            if not isinstance(item, dict):
                issues.append(Issue("error", "invalid_item", location, "オブジェクトではありません"))
                continue
            evidence = item.get("evidence")
            if not isinstance(evidence, str) or not evidence.strip():
                issues.append(Issue("error", "missing_evidence", location, "根拠抜粋がありません"))
            elif evidence.strip() not in manuscript:
                issues.append(Issue("warning", "evidence_not_verbatim", location, "根拠抜粋が原稿内に完全一致しません"))
            text = _item_text(item)
            for number in NUMBER_RE.findall(text):
                if number not in manuscript:
                    issues.append(Issue("warning", "new_number", location, f"原稿に同一表記がない数値: {number}"))
            for code, pattern in RISKY_PATTERNS.items():
                if pattern.search(text):
                    issues.append(Issue("warning", code, location, "科学的・医薬品的な断定表現を要確認"))
            if section == "x_posts" and len(item.get("text", "")) > settings.x_max_chars:
                issues.append(Issue("warning", "x_too_long", location, f"X本文が{settings.x_max_chars}文字を超えています"))
    issues.extend(_duplicate_angles(content))
    return issues


def report(issues: list[Issue]) -> dict[str, Any]:
    return {
        "status": "確認待ち",
        "summary": {
            "errors": sum(issue.severity == "error" for issue in issues),
            "warnings": sum(issue.severity == "warning" for issue in issues),
            "human_review_required": True,
        },
        "issues": [asdict(issue) for issue in issues],
        "notice": "自動検査は正確性を保証しません。原稿と照合して人間が最終確認してください。",
    }


def _item_text(item: dict[str, Any]) -> str:
    return "\n".join(_strings(value) for key, value in item.items() if key != "evidence")


def _strings(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(_strings(part) for part in value)
    return ""


def _duplicate_angles(content: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    for section, items in content.items():
        if not isinstance(items, list):
            continue
        seen: dict[str, int] = {}
        for index, item in enumerate(items):
            if not isinstance(item, dict) or not isinstance(item.get("angle"), str):
                continue
            normalized = re.sub(r"\W", "", item["angle"]).lower()
            if normalized and normalized in seen:
                issues.append(Issue("warning", "duplicate_angle", f"{section}[{index}]", f"{seen[normalized]}番目と同じ論点です"))
            else:
                seen[normalized] = index
    return issues

