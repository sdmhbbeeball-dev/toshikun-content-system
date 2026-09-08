from __future__ import annotations

import argparse
import json
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


if __name__ == "__main__":
    raise SystemExit(main())

