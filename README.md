# としくんSNS制作ライン

校正済みのYouTube長尺原稿1本から、媒体ごとに異なる論点を使ったSNSコンテンツ案を作り、**確認待ち**としてブラウザに表示するローカルアプリです。投稿は自動化しません。

## MVPで生成するもの

- Shorts 5本
- X 10投稿
- Instagram 3投稿（カルーセル可）
- 公式LINE 1本
- YouTubeタイトル候補 5本
- YouTubeサムネイル文言候補 5本
- 品質チェックレポート

生成物は公開可能な完成品ではなく、人間が科学的正確性・文体・媒体適合性を確認するためのドラフトです。

## 使う方へ

公開されたURLをChromeやSafariなどで開くだけです。Pythonのインストール、ファイルのダウンロード、コマンド操作は必要ありません。

1. 管理者から案内されたURLを開きます。
2. YouTube原稿を大きな入力欄へ貼り付けます。
3. 必要な場合だけ、管理者から案内されたアクセスパスワードを入力します。
4. 「SNSコンテンツを生成」を押します。
5. Shorts、X、Instagram、LINE、YouTubeタイトル、サムネ文言をタブで確認し、必要な案をコピーします。

すべてAIによる確認待ちのドラフトです。根拠抜粋、エラー、警告を元原稿と照合し、問題のない案だけを手作業で投稿してください。SNSへの自動投稿は行いません。

## 管理者向け：GitHubからWebへ公開する

このリポジトリは、RenderのBlueprintとしてそのまま公開できる構成です。APIキーをブラウザへ配布せず、Webサーバーの環境変数として安全に保持します。

### 最初の1回だけ行うこと

1. このコードを自分のGitHubリポジトリへ置きます。
2. Renderへログインし、**New → Blueprint** を選びます。
3. GitHubリポジトリを接続します。Renderがルートの `render.yaml` を読み取ります。
4. 設定画面で次のSecretを入力します。
   - `OPENAI_API_KEY`: OpenAI APIキー
   - `TOSHIKUN_ACCESS_PASSWORD`: 利用者へ案内する任意のパスワード
5. デプロイ完了後に表示される `https://...onrender.com` のURLを利用者へ案内します。

以後、利用者はURLを開くだけで使用できます。GitHubの既定ブランチへ変更を反映すると、Render側で再デプロイできます。

> **重要:** URLを完全公開すると第三者にAPIを利用される可能性があります。`TOSHIKUN_ACCESS_PASSWORD` は空にせず、推測されにくい値を設定してください。OpenAI側でも利用上限を設定してください。

## 開発者向けローカル実行（通常は使いません）

インストールして従来のコマンド操作を使う場合:

```bash
python -m pip install -e .
```

```bash
toshikun-sns generate manuscripts/first.md --output outputs
```

成功すると、保存先と品質チェック件数が表示されます。表示されたフォルダの `review.md` を最初に開いてください。

ブラウザ版をコマンドから起動する場合:

```bash
toshikun-sns-web
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
