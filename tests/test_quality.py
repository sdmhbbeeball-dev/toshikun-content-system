from toshikun_sns.config import Settings
from toshikun_sns.quality import validate


def valid_content(evidence: str) -> dict:
    def items(count: int, section: str) -> list[dict]:
        rows = []
        for index in range(count):
            row = {"angle": f"{section}の論点{index}", "text": "肌を観察します", "evidence": evidence}
            if section == "shorts":
                row.update(hook="注目点です", script="肌を観察します")
            if section == "instagram":
                row.update(format="single", caption="確認しましょう", slides=[])
            rows.append(row)
        return rows
    return {
        "shorts": items(5, "shorts"), "x_posts": items(10, "x"),
        "instagram": items(3, "instagram"), "line": items(1, "line"),
        "youtube_titles": [{"text": f"肌の話{i}", "evidence": evidence} for i in range(5)],
        "thumbnail_phrases": [{"text": f"肌を知る{i}", "evidence": evidence} for i in range(5)],
    }


def test_valid_shape_has_no_errors() -> None:
    issues = validate(valid_content("肌を観察します"), "肌を観察します", Settings())
    assert not [issue for issue in issues if issue.severity == "error"]


def test_flags_wrong_count_missing_evidence_and_new_number() -> None:
    content = valid_content("肌を観察します")
    content["shorts"] = [{"angle": "別", "script": "30日で必ず治療できる", "evidence": ""}]
    issues = validate(content, "肌を観察します", Settings())
    codes = {issue.code for issue in issues}
    assert {"wrong_count", "missing_evidence", "new_number", "medical_certainty"} <= codes


def test_flags_non_verbatim_evidence_and_duplicate_angle() -> None:
    content = valid_content("肌を観察します")
    content["x_posts"][1]["angle"] = content["x_posts"][0]["angle"]
    content["line"][0]["evidence"] = "存在しない抜粋"
    codes = {issue.code for issue in validate(content, "肌を観察します", Settings())}
    assert "evidence_not_verbatim" in codes
    assert "duplicate_angle" in codes

