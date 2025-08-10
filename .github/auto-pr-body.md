feat(api): add /items endpoint (BASE proxy) + tests and docs

## 概要
- 新規: GET /items を追加（BASE API /1/items のプロキシ）
- ルーター: app/routers/items.py 追加、app/main.py に include_router
- クエリ転送: visible, order, sort, limit, offset, category_id
- 認可: 環境変数 BASE_ACCESS_TOKEN を Bearer で付与（BASE_API_URL 既定 https://api.base.ec）
- エラー処理: requests 例外を 502 に変換、BASE 側エラーはステータス/本文を伝播
- テスト: /items 正常系・未設定エラーをモックで検証、BaseAPIClient のテストもモック化
- ドキュメント: README に /items と環境変数を追記、docs/ai-context.md に「第8章: 自動読込規約」追記

## 動作確認
- ローカルテスト結果: 9 passed, 1 warning（urllib3/LibreSSLの注意）
- OpenAPI: /docs に /items が出現
- Render 反映後の確認想定: /items?limit=3, /docs

## 必要な環境変数（Render）
- BASE_ACCESS_TOKEN: 必須
- BASE_API_URL: 任意（デフォルト https://api.base.ec）

## 影響範囲
- 公開API: /items 追加
- ドキュメント: README, ai-context
- テスト/依存: pytest 追加、HTTP外部呼び出しをモック

## リスクとフォロー
- BASE応答仕様に依存 → 必要ならスキーマ定義追加
- タイムアウト 15s（将来設定化）
