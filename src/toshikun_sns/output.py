from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from .config import Settings


def create_job_dir(root: Path, manuscript: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(manuscript.encode()).hexdigest()[:8]
    path = root / f"{stamp}-{digest}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_job(path: Path, manuscript: str, content: dict[str, Any], quality: dict[str, Any], settings: Settings) -> None:
    (path / "manuscript.md").write_text(manuscript, encoding="utf-8")
    _json(path / "content.json", content)
    _json(path / "quality-report.json", quality)
    _json(path / "metadata.json", {
        "status": "確認待ち",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": settings.model,
        "counts": settings.counts(),
        "automatic_posting": False,
    })
    (path / "review.md").write_text(render_review(content, quality), encoding="utf-8")


def render_review(content: dict[str, Any], quality: dict[str, Any]) -> str:
    lines = ["# SNSコンテンツ確認票", "", "**状態: 確認待ち（未投稿）**", "",
             "> 自動生成案です。根拠を原稿と照合し、人間が修正・承認してください。", ""]
    labels = {
        "shorts": "Shorts", "x_posts": "X", "instagram": "Instagram", "line": "公式LINE",
        "youtube_titles": "YouTubeタイトル候補", "thumbnail_phrases": "サムネイル文言候補",
    }
    for section, label in labels.items():
        lines.extend([f"## {label}", ""])
        for index, item in enumerate(content.get(section, []), 1):
            lines.append(f"### {index}")
            if isinstance(item, dict):
                for key, value in item.items():
                    lines.extend([f"**{key}**", _markdown_value(value), ""])
            else:
                lines.extend([str(item), ""])
    summary = quality["summary"]
    lines.extend(["## 自動品質チェック", "", f"- エラー: {summary['errors']}", f"- 警告: {summary['warnings']}",
                  "- 人間の最終確認: 必須", ""])
    for issue in quality["issues"]:
        lines.append(f"- **{issue['severity']} / {issue['code']}** `{issue['location']}`: {issue['message']}")
    return "\n".join(lines) + "\n"


def _markdown_value(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(f"- {part}" for part in value)
    return str(value)


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

