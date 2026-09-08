from __future__ import annotations

import json

from .config import Settings


SYSTEM_PROMPT = """あなたは現役の化粧品研究員『としくん』のSNS編集者です。
入力された校正済み原稿だけを情報源として、日本語のドラフトを作成してください。

絶対条件:
- 原稿にない事実や数値を追加・推測しない。不明なら使わない。
- 研究結果、第三者の主張、本人の見解を区別する。
- ヒト研究、動物研究、in vitroを混同しない。
- 相関を因果に、統計的有意差を臨床的意義に読み替えない。
- 医薬品的な治療・予防・治癒・効果保証を断定しない。
- 結論に必要な対象、条件、限界を落とさない。
- 数値、単位、濃度、人数、期間は原文どおりにする。
- 煽りやクリック率のために正確性を犠牲にしない。
- 各項目の evidence は、根拠となる原稿中の連続した短い原文抜粋にする。
- 同じ主張の言い換えを量産せず、異なる論点・フックを選ぶ。

JSON以外は出力しないでください。"""


def build_prompt(manuscript: str, settings: Settings) -> str:
    schema = {
        "shorts": [{"angle": "論点", "hook": "冒頭", "script": "台本", "evidence": "原稿抜粋"}],
        "x_posts": [{"angle": "論点", "text": "投稿本文", "evidence": "原稿抜粋"}],
        "instagram": [{
            "angle": "論点", "format": "carousel または single",
            "caption": "キャプション", "slides": ["スライド文言"], "evidence": "原稿抜粋"
        }],
        "line": [{"angle": "論点", "text": "本文", "evidence": "原稿抜粋"}],
        "youtube_titles": [{"text": "候補", "evidence": "原稿抜粋"}],
        "thumbnail_phrases": [{"text": "候補", "evidence": "原稿抜粋"}],
    }
    return f"""次の件数を厳守してください: {json.dumps(settings.counts(), ensure_ascii=False)}

媒体要件:
- Shorts: 強く正確なフック、1本1知識の短い台本。
- X: {settings.x_max_chars}文字以内、専門性と発見があり単独で理解可能。
- Instagram: 保存しやすい設計。必要ならcarouselで複数スライド。
- LINE: 既存視聴者に自然に語りかけ、過剰な広告にしない。
- YouTubeタイトル・サムネ: 内容と整合し、重要条件を落とさない。

出力JSONの形（各配列は指定件数）:
{json.dumps(schema, ensure_ascii=False, indent=2)}

<manuscript>
{manuscript}
</manuscript>"""

