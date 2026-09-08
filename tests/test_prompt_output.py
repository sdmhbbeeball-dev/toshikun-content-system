import json

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
