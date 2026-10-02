# JSEP Auto Typesetter

JSEP学術論文のWord原稿を、PandocとLuaLaTeX（luatexja）で横書きPDFへ変換する出版システムです。正式なJSEP書式が提供されるまで、変更可能な仮テンプレートを使用します。

## 実装済み（Phase 1）

- `.docx` をPandoc AST/Markdownへ変換し、タイトル、著者、抄録、本文、見出し、図表、参考文献、数式を読み取る基盤
- 抽出内容の確認・編集、文字サイズ・余白設定、変換警告表示
- Pandoc → LuaLaTeX → PDF の実変換
- GitHub Pages用の架空原稿限定デモ（変換APIは無効）
- FastAPIバックエンドと隔離設定付きDocker Compose

## Dockerで実行

```bash
docker compose up --build
```

`http://localhost:8000` を開きます。コンテナは非root、読み取り専用で動作し、書き込み可能領域は容量制限付き`/tmp`だけです。LaTeXは`--no-shell-escape`で実行され、編集欄のraw TeXもPandoc入力で無効化されます。アップロードは最大25MBで、要求ごとの一時ディレクトリから応答後に削除されます。原稿をAIや他の外部サービスへ送信する処理はありません。

## ローカルテスト

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

統合テストは実行時に完全な架空の`.docx`を生成し、Pandocで抽出後、LuaLaTeXで実PDFを作成してPDFヘッダーとサイズを検査します。Pandoc/LuaLaTeXがない環境ではこのテストだけがskipされます。

## GitHub Pages

`.github/workflows/pages.yml`は`frontend/`だけを公開します。Pagesでは架空原稿の編集UIだけを提供し、WordアップロードとPDF生成を無効化します。`main`へのpush後、Repository SettingsのPages Sourceを **GitHub Actions** に設定してください。

## 現在の制約・未実装

- 正式なJSEPテンプレート（提供後に`backend/template.tex`を差し替え予定）
- 編集後PDFへの抽出画像の引き継ぎと、参考文献スタイル/CSLによる厳密な整形
- 複雑なWord図表・OMML数式の完全な再現（Pandocの警告とPDFの目視確認が必要）
- 複数所属、脚注、査読用匿名化などの投稿規程固有機能
