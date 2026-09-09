import json
from pathlib import Path

from toshikun_sns.cli import main
from toshikun_sns.config import Settings
from toshikun_sns.output import render_review
from toshikun_sns.prompt import build_prompt
from toshikun_sns.quality import report


def test_prompt_contains_manuscript_and_counts() -> None:
    prompt = build_prompt("校正済み本文", Settings())
    assert "校正済み本文" in prompt
    assert '"x_posts": 10' in prompt
    assert "原稿抜粋" in prompt


def test_review_is_explicitly_pending_and_unpublished() -> None:
    review = render_review({}, report([]))
    assert "確認待ち（未投稿）" in review
    assert "人間の最終確認: 必須" in review
    json.dumps(report([]), ensure_ascii=False)


def test_init_creates_beginner_manuscript_without_overwriting(tmp_path: Path, capsys) -> None:
    manuscript = tmp_path / "manuscripts" / "first.md"
    assert main(["init", "--path", str(manuscript)]) == 0
    assert "## 本文" in manuscript.read_text(encoding="utf-8")
    assert "次に" in capsys.readouterr().out
    assert main(["init", "--path", str(manuscript)]) == 1


def test_doctor_explains_missing_api_key(monkeypatch, capsys) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert main(["doctor"]) == 1
    assert "APIキー: 未設定" in capsys.readouterr().err
