# EC-LIVE FastAPI Renderデプロイ手順（推奨構成）

本番運用URL（Render）: https://ec-live.onrender.com/

本ガイドは、**Render（https://render.com）でFastAPI（本プロジェクト）を安定・安全に公開運用するための推奨手順**です。

---

## 1. Renderアカウント作成・ログイン

1. [Render](https://render.com/) で無料アカウント作成（GitHub連携を推奨）
2. ログイン状態にする

---

## 2. GitHubリポジトリの準備

- このプロジェクト（mikky0415/EC-LIVE）がGitHubへpush済みであることを確認
- プライベートリポジトリの場合、RenderのGitHub権限設定で必ず該当リポジトリにアクセス許可を与える

---

## 3. Renderで新規Web Service作成

1. Renderダッシュボードで「New +」→「Web Service」
2. 「Connect account」でGitHub連携（未連携なら）
3. リポジトリ一覧から `mikky0415/EC-LIVE` を選択

---

## 4. サービス詳細設定（推奨値）

### 4-1. 基本情報
- **Name**: ec-live-api など分かりやすい名前
- **Region**: Tokyo（日本で運用する場合推奨）

### 4-2. Branch
- `main` を選択

### 4-3. Build & Start Command（重要: gunicornは不要）
- **Build Command**  
  ```
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- **Start Command（推奨）**  
  ```
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
  - gunicorn は本プロジェクトでは使用しません（requirementsにも含めません）。
  - `$PORT` はRenderの自動割当て環境変数なので必ずこの指定にすること。

---

## 5. 環境変数（.envの内容）をRenderの「Environment」へ登録

- サービス作成画面の「Environment」セクションで「Add Environment Variable」
    - `BASE_API_URL` → `https://api.base.ec`
    - `BASE_ACCESS_TOKEN` → BASE管理画面で発行したトークン

※`.env`ファイル自体はアップロード不要・不可。「Environment Variables」からWebで必ず追加！

---

## 6. デプロイ・初回ビルド

- 「Create Web Service」でサービス作成
- ビルド・デプロイが自動で進行
- 数分後「Live」状態になればデプロイ成功

---

## 7. 動作確認

- Renderが発行したURL（例: https://ec-live-api.onrender.com）にアクセス
- `/items` でBASE API商品一覧が返るか確認
- `/docs` でSwagger UIが開くことを確認

---

## 8. 運用・更新のポイント

- コードをGitHubのmainブランチにpushすると、Renderが**自動で再デプロイ**（手作業不要）
- 環境変数を変更したら「Manual Deploy」や「Restart」で再起動
- 依存パッケージ追加時は`requirements.txt`修正後にpushでOK
- 無料枠は一定時間アクセスがないとスリープ（有料化で常時稼働可）

---

## 9. トラブル対応例

- **No module named 'app'**
    - ディレクトリ構成が正しいか確認（`app/`ディレクトリごとpush必須）
- **Internal Server Error/Timeout**
    - BASE_APIトークンやURLが正しいか、「Environment Variables」を再確認
- **/docsや/itemsにアクセス不可**
    - サービスURL・エンドポイントのスペルミスに注意
    
- **bash: gunicorn: command not found**
    - Start Command が `gunicorn ...` になっていると発生します。Renderのサービス設定で次のように修正してください。
      ```
      uvicorn app.main:app --host 0.0.0.0 --port $PORT
      ```
    - もしくはこのリポジトリの `render.yaml` を使ったBlueprintデプロイで設定を固定化してください。

---

## 10. まとめ

RenderはFastAPI（Python）アプリの本番運用も簡単です。  
困ったら「Deploy logs」を確認し、エラー全文を添えて質問してください。

---

### READMEへの案内例

README.mdに以下を追記しておくと親切です：

```markdown
## Renderでのデプロイ手順

詳しくは[docs/RENDER_DEPLOY_GUIDE.md](./docs/RENDER_DEPLOY_GUIDE.md)を参照してください。
```