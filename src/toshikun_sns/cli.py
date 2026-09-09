from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .client import ApiError, generate_json
from .config import Settings
from .output import create_job_dir, write_job
from .prompt import SYSTEM_PROMPT, build_prompt
from .quality import report, validate


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="としくんSNS制作ライン（投稿は行いません）")
    commands = root.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="初回テスト用の原稿ファイルを作成")
    init.add_argument("--path", type=Path, default=Path("manuscripts/first.md"))
    commands.add_parser("doctor", help="実行前の設定を確認")
    generate = commands.add_parser("generate", help="原稿から確認待ちドラフトを生成")
    generate.add_argument("manuscript", type=Path)
    generate.add_argument("--output", type=Path, default=Path("outputs"))
    generate.add_argument("--dry-run", action="store_true", help="APIを呼ばずプロンプトを保存")
    check = commands.add_parser("validate", help="既存JSONを品質チェック")
    check.add_argument("content", type=Path)
    check.add_argument("--manuscript", type=Path, required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    settings = Settings.from_env()
    try:
        if args.command == "init":
            return _init_manuscript(args.path)
        if args.command == "doctor":
            return _doctor(settings)

        manuscript = args.manuscript.read_text(encoding="utf-8")
        if not manuscript.strip():
            raise ValueError("原稿が空です")
        if args.command == "validate":
            content = json.loads(args.content.read_text(encoding="utf-8"))
            print(json.dumps(report(validate(content, manuscript, settings)), ensure_ascii=False, indent=2))
            return 0

        job_dir = create_job_dir(args.output, manuscript)
        prompt = build_prompt(manuscript, settings)
        if args.dry_run:
            (job_dir / "manuscript.md").write_text(manuscript, encoding="utf-8")
            (job_dir / "prompt.txt").write_text(SYSTEM_PROMPT + "\n\n" + prompt, encoding="utf-8")
            print(f"dry-runを保存しました: {job_dir}")
            return 0
        content = generate_json(api_url=settings.api_url, model=settings.model, system=SYSTEM_PROMPT, prompt=prompt)
        quality = report(validate(content, manuscript, settings))
        write_job(job_dir, manuscript, content, quality, settings)
        print(f"確認待ち成果物を保存しました: {job_dir}")
        print(f"品質チェック: error={quality['summary']['errors']}, warning={quality['summary']['warnings']}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError, ApiError) as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1


MANUSCRIPT_TEMPLATE = """# YouTube動画タイトル

ここにタイトルを書いてください。

## 本文

ここに校正済みのYouTube原稿を、そのまま貼り付けてください。

## 研究情報（原稿で扱う場合）

- 研究の種類:
- 対象・人数:
- 期間・条件:
- 出典:
- 研究の限界:

## としくん本人の見解

研究結果と混ざらないよう、本人の見解はここに分けて書いてください。
"""


def _init_manuscript(path: Path) -> int:
    if path.exists():
        raise ValueError(f"{path} は既にあります。上書きしません")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(MANUSCRIPT_TEMPLATE, encoding="utf-8")
    print(f"原稿テンプレートを作成しました: {path}")
    print("次に、このファイルを開き、YouTube原稿を貼り付けて保存してください。")
    return 0


def _doctor(settings: Settings) -> int:
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"モデル: {settings.model}")
    print(f"API接続先: {settings.api_url}")
    if os.getenv("OPENAI_API_KEY"):
        print("APIキー: 設定済み（値は表示しません）")
        print("準備OKです。generate コマンドを実行できます。")
        return 0
    print("APIキー: 未設定", file=sys.stderr)
    print('次に、export OPENAI_API_KEY="あなたのAPIキー" を実行してください。', file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
