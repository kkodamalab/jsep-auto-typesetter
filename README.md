# JSEP Auto Typesetter

JSEP学術論文のWord原稿を、PandocとLuaLaTeX（luatexja）で横書きPDFへ変換する出版システムです。正式なJSEP書式が提供されるまで、変更可能な仮テンプレートを使用します。

## 実装済み（Phase 1）

- `.docx` をPandoc AST/Markdownへ変換し、Word文書プロパティを含むタイトル、著者、抄録、本文、見出し、図表、参考文献、数式を読み取る基盤
- 抽出内容の確認・編集、文字サイズ・余白設定、変換警告表示
- Pandoc → LuaLaTeX → PDF の実変換
- GitHub Pages用の架空原稿限定デモ（変換APIは無効）
- FastAPIバックエンドと隔離設定付きDocker Compose

## Dockerで実行

```bash
docker compose up --build
```

`http://localhost:8000` を開きます。コンテナは非root、読み取り専用で動作し、書き込み可能領域は容量制限付き`/tmp`だけです。LaTeXは`--no-shell-escape`で実行され、編集欄のraw TeXもPandoc入力で無効化されます。PandocのSmart Typographyは無効化し、タイトル・著者名の引用符を原稿どおり保持します。アップロードは最大25MBで、要求ごとの一時ディレクトリから応答後に削除されます。原稿をAIや他の外部サービスへ送信する処理はありません。

> [!WARNING]
> 認証・認可、利用者ごとのクォータ、ネットワーク隔離は未実装です。現状のバックエンドをインターネットへ公開したり、本番運用したりしないでください。信頼できるローカル環境または隔離された検証環境だけで使用してください。

## ローカルテスト

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

統合テストは画像、キャプション、表、数式、日本語、特殊文字を含む完全な架空の`.docx`を生成します。Pandocで抽出後、LuaLaTeXで実PDFを作成し、Popplerでページ数、抽出文字、埋め込み画像を検査します。MarkdownとTeXでは原稿のASCII文字が保持されることを直接検査します。PDF抽出テキストは、luatexjaのToUnicode表現で生じる全角数字をNFKCで比較用に正規化し、pdftotextが組版位置から再構築する空白を比較時だけ除外します。直線/曲線アポストロフィなど意味のある句読点差は同一視しません。各段階と全コンテンツの検査を最後まで行い、失敗項目を一括報告します。成功時は全ページをPNGへ変換し、`test-artifacts/`へDOCX・PDF、架空原稿のMarkdown/TeX、通常/raw両方の抽出テキストとともに出力します。LuaLaTeX失敗時はTeXとログを診断用に出力します。この診断出力は統合テスト専用であり、実際の投稿原稿を扱うAPIには存在しません。CIの統合テストはツール不足や成果物不足を成功扱いにしません。

アップロードごとに推測困難なIDと専用一時ディレクトリを割り当てます。Pandocが抽出した`media/`とMarkdown内の画像・キャプション参照は編集確認中も同じ領域に保持され、PDF応答完了時、変換エラー時、または1時間の期限切れ時に原稿と一緒に削除されます。

## GitHub Pages

`.github/workflows/pages.yml`は`frontend/`だけを公開します。Pagesでは架空原稿の編集UIだけを提供し、WordアップロードとPDF生成を無効化します。`main`へのpush後、Repository SettingsのPages Sourceを **GitHub Actions** に設定してください。

## 現在の制約・未実装

- 正式なJSEPテンプレート（提供後に`backend/template.tex`を差し替え予定）
- 参考文献スタイル/CSLによる厳密な整形
- 複雑なWord図表・OMML数式の完全な再現（Pandocの警告とPDFの目視確認が必要）
- 複数所属、脚注、査読用匿名化などの投稿規程固有機能
