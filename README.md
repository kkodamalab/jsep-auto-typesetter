# JSEP Auto Typesetter

日本語原稿をブラウザ上で縦書きに自動組版する、依存関係なしの静的 Web アプリです。

## Phase 1

- 原稿入力とリアルタイム文字数表示
- 文字数・行数を指定した自動改ページ
- A4比率の縦書きプレビュー
- ブラウザの印刷機能による PDF 出力
- 入力内容を外部送信しないクライアントサイド処理

## 開発

```bash
npm run dev
```

`http://localhost:4173` を開いてください。

```bash
npm test
npm run check
```

## デプロイ

`main` ブランチへの push で `.github/workflows/pages.yml` が静的ファイルを GitHub Pages にデプロイします。リポジトリの **Settings → Pages → Source** を **GitHub Actions** に設定してください。
