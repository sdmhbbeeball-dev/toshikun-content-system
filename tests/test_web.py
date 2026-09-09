import pytest

from toshikun_sns import web


def test_generate_content_builds_quality_report(monkeypatch) -> None:
    evidence = "校正済み原稿"

    def fake_generate_json(**kwargs):
        assert evidence in kwargs["prompt"]
        return {key: [] for key in web.Settings().counts()}

    monkeypatch.setattr(web, "generate_json", fake_generate_json)
    result = web.generate_content(evidence)
    assert result["quality"]["status"] == "確認待ち"
    assert result["quality"]["summary"]["errors"] == 6


def test_generate_content_rejects_empty_manuscript() -> None:
    with pytest.raises(ValueError, match="原稿を貼り付け"):
        web.generate_content("   ")


def test_generate_content_checks_optional_access_password(monkeypatch) -> None:
    monkeypatch.setenv("TOSHIKUN_ACCESS_PASSWORD", "correct")
    with pytest.raises(ValueError, match="パスワード"):
        web.generate_content("原稿", "wrong")


def test_browser_page_has_all_channels_and_generate_button() -> None:
    html = web.STATIC_DIR.joinpath("index.html").read_text(encoding="utf-8")
    javascript = web.STATIC_DIR.joinpath("app.js").read_text(encoding="utf-8")
    assert "SNSコンテンツを生成" in html
    for channel in ("Shorts", "X", "Instagram", "LINE", "YouTubeタイトル", "サムネ文言"):
        assert channel in javascript
