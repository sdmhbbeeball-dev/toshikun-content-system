# としくんSNS制作ライン

校正済みのYouTube長尺原稿1本から、媒体ごとに異なる論点を使ったSNSコンテンツ案を作り、**確認待ち**として整理するローカルCLIです。投稿は自動化しません。

## MVPで生成するもの

- Shorts 5本
- X 10投稿
- Instagram 3投稿（カルーセル可）
- 公式LINE 1本
- YouTubeタイトル候補 5本
- YouTubeサムネイル文言候補 5本
- 品質チェックレポート

生成物は公開可能な完成品ではなく、人間が科学的正確性・文体・媒体適合性を確認するためのドラフトです。

## セットアップ

Python 3.11以上を使います。外部ライブラリは不要です。

```bash
python -m pip install -e .
export OPENAI_API_KEY="..."   # .envやGitには保存しない
```

## 実行

```bash
toshikun-sns generate manuscripts/example.md --output outputs
```

APIを呼ばず、入力・設定とプロンプトだけを確認できます。

```bash
toshikun-sns generate manuscripts/example.md --output outputs --dry-run
```

既存の生成JSONを再検査するには:

```bash
toshikun-sns validate outputs/<job-id>/content.json \
  --manuscript manuscript.md
```

成功時も `quality-report.json` の警告を確認してください。成果物は `outputs/<job-id>/` に保存され、状態は常に `確認待ち` です。詳細は [プロジェクト方針](docs/PROJECT.md) と [運用手順](docs/OPERATIONS.md) を参照してください。

## 設定

環境変数で接続先を変更できます。

| 変数 | 既定値 | 用途 |
|---|---|---|
| `OPENAI_API_KEY` | なし | API認証（必須） |
| `TOSHIKUN_MODEL` | `gpt-5.2` | 使用モデル |
| `TOSHIKUN_API_URL` | `https://api.openai.com/v1/responses` | Responses互換エンドポイント |

APIレスポンスは `output_text`、または Responses API形式の `output[].content[].text` にJSON文字列が返ることを想定しています。
