# BASE API 統合マニュアル

本ドキュメントは、BASE API公式ドキュメント（2025年8月時点）をもとに、全APIエンドポイント・パラメータ・レスポンス例・エラー例・解説を体系的にまとめたものです。

---

## 目次

1. [はじめに・共通事項](#はじめに・共通事項)
2. [OAuth 認証](#oauth-認証)
3. [ユーザー情報](#ユーザー情報)
4. [商品(Item)関連](#商品item関連)
5. [商品カテゴリ(Item Category)](#商品カテゴリitem-category)
6. [カテゴリ(Category)](#カテゴリcategory)
7. [注文(Orders)](#注文orders)
8. [エラーコード一覧](#エラーコード一覧)

---

## はじめに・共通事項

- BASE APIは、BASEショップのデータを外部システムから操作・取得するためのRESTful APIです。
- 全てのリクエスト・レスポンスはJSON形式です。
- 認証にはOAuth2.0を利用します。
- `https` 通信が必須です。

---

## OAuth 認証

### 概要

BASE APIの利用には、必ずOAuth2による認可が必要です。  
認証フローは下記の3つのエンドポイントで構成されます。

#### 1. 認可コード取得
`GET /1/oauth/authorize`

#### 2. アクセストークン発行
`POST /1/oauth/access_token`

#### 3. リフレッシュトークンによるアクセストークン更新
`POST /1/oauth/refresh_token`

---

### 1. /1/oauth/authorize

- メソッド: GET
- 説明: ユーザーの認証・許可を経て、認可コードを取得します。

#### リクエストパラメータ

| Name         | Description                    | 必須 |
|--------------|-------------------------------|------|
| client_id    | アプリケーションID             | ○    |
| redirect_uri | リダイレクトURI                | ○    |
| response_type| 固定値: code                   | ○    |
| scope        | 要求する権限（例: read_items）  | ○    |
| state        | 任意のパラメータ（CSRF対策等） | 任意 |

#### 説明

- 認可が成功すると、指定した`redirect_uri`に`code`および`state`（指定した場合）が付与されてリダイレクトされます。

---

### 2. /1/oauth/access_token

- メソッド: POST
- 説明: 認可コードを使用してアクセストークン・リフレッシュトークンを取得します。

#### リクエストパラメータ

| Name         | Description                         | 必須 |
|--------------|------------------------------------|------|
| client_id    | アプリケーションID                  | ○    |
| client_secret| アプリケーションシークレット         | ○    |
| code         | /1/oauth/authorizeで取得したコード   | ○    |
| grant_type   | 固定値: authorization_code          | ○    |
| redirect_uri | リダイレクトURI                     | ○    |

#### レスポンス例

```json
{
  "access_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "token_type": "Bearer",
  "expires_in": 86400,
  "refresh_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "scope": "read_items"
}
```

---

### 3. /1/oauth/refresh_token

- メソッド: POST
- 説明: 有効なリフレッシュトークンから新しいアクセストークンを発行します。

#### リクエストパラメータ

| Name           | Description                 | 必須 |
|----------------|----------------------------|------|
| client_id      | アプリケーションID          | ○    |
| client_secret  | アプリケーションシークレット | ○    |
| refresh_token  | リフレッシュトークン         | ○    |
| grant_type     | 固定値: refresh_token       | ○    |

#### レスポンス例

```json
{
  "access_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "token_type": "Bearer",
  "expires_in": 86400,
  "refresh_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "scope": "read_items"
}
```

#### エラー例

```json
{
  "error": "invalid_grant",
  "error_description": "リフレッシュトークンが不正です。"
}
```

---

## ユーザー情報

### /1/users/me

- メソッド: GET
- スコープ: `read_users`
- 概要: 認証済みのユーザー情報（ショップ情報）を取得します。

#### リクエストパラメータ

なし

#### レスポンス例

```json
{
  "user_id": 1000,
  "shop_id": 1000,
  "login_id": "sample@example.com",
  "shop_name": "サンプルショップ",
  "shop_url": "https://sample.thebase.in",
  "shop_domain": "sample",
  "shop_email": "sample@example.com",
  "shop_tel": "000-0000-0000",
  "shop_zip": "000-0000",
  "shop_addr": "東京都○○区○○1-1-1"
}
```

---

## 商品(Item)関連

### /1/items

- メソッド: GET
- スコープ: `read_items`
- 概要: 商品情報の一覧を取得

#### リクエストパラメータ

| Name         | Description                                                  | 必須/任意 | 備考                       |
|--------------|-------------------------------------------------------------|-----------|----------------------------|
| visible      | 公開ステータス 1:表示、0:非表示                             | 任意      |                            |
| order        | 並び替え項目。list_order、created、modified のいずれか       | 任意      | デフォルト: list_order     |
| sort         | 並び順。asc か desc                                         | 任意      | デフォルト: asc            |
| limit        | 取得件数リミット（MAX:100）                                 | 任意      | デフォルト: 20             |
| offset       | オフセット                                                  | 任意      | デフォルト: 0              |
| max_image_no | 画像番号 1~20                                               | 任意      | デフォルト: 5              |
| image_size   | 画像サイズ origin,76,146,300,500,640,sp_480,sp_640          | 任意      | カンマ区切りで複数指定可   |
| category_id  | カテゴリID                                                  | 任意      |                            |

#### レスポンス例

```json
{
  "items": [
    {
      "item_id": 1234,
      "title": "Tシャツ",
      "detail": "とってもオシャレなTシャツです。",
      "price": 3900,
      "proper_price": null,
      "item_tax_type": 1,
      "stock": 10,
      "visible": 1,
      "list_order": 1,
      "identifier": "abcd-1234",
      "img1_origin": "https://...jpg",
      "img2_origin": "https://...jpg",
      "img3_origin": null,
      "img4_origin": null,
      "img5_origin": null,
      "modified": 1414731171,
      "variations": [
        {
          "variation_id": 11,
          "variation": "黒色",
          "variation_stock": 6,
          "variation_identifier": "abcd-1234-b",
          "barcode": "abcd-1234-b"
        },
        {
          "variation_id": 12,
          "variation": "白色",
          "variation_stock": 4,
          "variation_identifier": "abcd-1234-w",
          "barcode": "abcd-1234-w"
        }
      ]
    }
  ]
}
```

#### 解説

- `item_id`: 商品ID
- `title`: 商品名
- `detail`: 商品説明
- `price`: 価格（税込）
- `proper_price`: 通常価格（税込）
- `item_tax_type`: 税率設定。1:標準税率、2:軽減税率
- `stock`: 在庫数
- `visible`: 表示フラグ。1:表示、0:非表示
- `list_order`: 表示順
- `identifier`: 商品コード
- `img1_origin`～`img5_origin`: 商品画像URL
- `variations`: バリエーション情報

#### エラー例

```json
{
  "error": "access_denied",
  "error_description": "httpsでアクセスしてください。"
}
```
```json
{
  "error": "invalid_request",
  "error_description": "アクセストークンが無効です。"
}
```
```json
{
  "error": "invalid_scope",
  "error_description": "スコープが無効です。"
}
```

---

### /1/items/search

- メソッド: GET
- スコープ: `read_items`
- 概要: 商品を検索

#### リクエストパラメータ

| Name           | Description            | 必須/任意 |
|----------------|-----------------------|-----------|
| title          | 商品名                 | 任意      |
| detail         | 商品説明               | 任意      |
| price_from     | 価格下限               | 任意      |
| price_to       | 価格上限               | 任意      |
| stock_from     | 在庫下限               | 任意      |
| stock_to       | 在庫上限               | 任意      |
| visible        | 公開ステータス         | 任意      |
| limit          | 取得件数リミット       | 任意      |
| offset         | オフセット             | 任意      |

#### レスポンス例

（/1/itemsと同様）

---

### /1/items/detail

- メソッド: GET
- スコープ: `read_items`
- 概要: 商品詳細情報取得

#### リクエストパラメータ

| Name   | Description  | 必須/任意 |
|--------|--------------|-----------|
| item_id| 商品ID       | 必須      |

#### レスポンス例

（/1/itemsと同様、1件のみ返却）

---

### /1/items/add

- メソッド: POST
- スコープ: `write_items`
- 概要: 商品登録

#### リクエストパラメータ

| Name         | Description      | 必須/任意 |
|--------------|-----------------|-----------|
| title        | 商品名           | 必須      |
| detail       | 商品説明         | 任意      |
| price        | 価格（税込）     | 必須      |
| stock        | 在庫数           | 必須      |
| visible      | 公開ステータス   | 任意      |
| identifier   | 商品コード       | 任意      |
| img1, img2...| 商品画像(base64) | 任意      |

#### レスポンス例

（登録後の商品情報）

---

### /1/items/edit

- メソッド: POST
- スコープ: `write_items`
- 概要: 商品情報の編集

#### リクエストパラメータ

| Name      | Description      | 必須/任意 |
|-----------|-----------------|-----------|
| item_id   | 商品ID           | 必須      |
| title等   | 編集項目         | 任意      |

---

### /1/items/delete

- メソッド: POST
- スコープ: `write_items`
- 概要: 商品削除

#### リクエストパラメータ

| Name    | Description | 必須/任意 |
|---------|-------------|-----------|
| item_id | 商品ID      | 必須      |

---

### /1/items/add_image

- メソッド: POST
- スコープ: `write_items`
- 概要: 商品画像追加

#### リクエストパラメータ

| Name    | Description   | 必須/任意 |
|---------|--------------|-----------|
| item_id | 商品ID        | 必須      |
| img     | 画像(base64)  | 必須      |

---

### /1/items/delete_image

- メソッド: POST
- スコープ: `write_items`
- 概要: 商品画像削除

#### リクエストパラメータ

| Name      | Description   | 必須/任意 |
|-----------|--------------|-----------|
| item_id   | 商品ID        | 必須      |
| image_no  | 画像番号      | 必須      |

---

### /1/items/edit_stock

- メソッド: POST
- スコープ: `write_items`
- 概要: 商品在庫数の変更

#### リクエストパラメータ

| Name      | Description | 必須/任意 |
|-----------|------------|-----------|
| item_id   | 商品ID      | 必須      |
| stock     | 在庫数      | 必須      |

---

### /1/items/delete_variation

- メソッド: POST
- スコープ: `write_items`
- 概要: バリエーション削除

#### リクエストパラメータ

| Name          | Description          | 必須/任意 |
|---------------|---------------------|-----------|
| item_id       | 商品ID              | 必須      |
| variation_id  | バリエーションID     | 必須      |

---

## 商品カテゴリ(Item Category)

### /1/item_categories/detail/:item_id

- メソッド: GET
- スコープ: `read_items`
- 概要: 商品に紐付くカテゴリ情報の取得

#### リクエストパラメータ

なし（パスパラメータ：item_id）

#### レスポンス例

```json
{
  "item_categories": [
    {
      "item_category_id": 123,
      "item_id": 1000,
      "category_id": 11
    },
    {
      "item_category_id": 124,
      "item_id": 1000,
      "category_id": 12
    }
  ]
}
```

---

### /1/item_categories/add

- メソッド: POST
- スコープ: `write_items`
- 概要: 商品とカテゴリの紐付け追加

#### リクエストパラメータ

| Name       | Description  | 必須/任意 |
|------------|--------------|-----------|
| item_id    | 商品ID       | 必須      |
| category_id| カテゴリID   | 必須      |

---

### /1/item_categories/delete

- メソッド: POST
- スコープ: `write_items`
- 概要: 商品とカテゴリの紐付け削除

#### リクエストパラメータ

| Name           | Description         | 必須/任意 |
|----------------|--------------------|-----------|
| item_category_id| 商品カテゴリID     | 必須      |

---

## カテゴリ(Category)

### /1/categories

- メソッド: GET
- スコープ: `read_items`
- 概要: カテゴリ情報の一覧を取得

#### リクエストパラメータ

なし

#### レスポンス例

```json
{
  "categories": [
    {
      "category_id": 1234,
      "name": "メンズ",
      "list_order": 1,
      "number": 1,
      "parent_number": 0,
      "code": "0001"
    },
    {
      "category_id": 1235,
      "name": "トップス",
      "list_order": 1,
      "number": 2,
      "parent_number": 1,
      "code": "0001-0002"
    }
  ]
}
```

---

### /1/categories/add

- メソッド: POST
- スコープ: `write_items`
- 概要: カテゴリ情報登録

#### リクエストパラメータ

| Name         | Description      | 必須/任意 |
|--------------|-----------------|-----------|
| name         | カテゴリ名        | 必須      |
| list_order   | 並び順           | 任意      |
| parent_number| 親カテゴリ番号    | 任意      |

---

### /1/categories/edit

- メソッド: POST
- スコープ: `write_items`
- 概要: カテゴリ情報編集

#### リクエストパラメータ

| Name         | Description      | 必須/任意 |
|--------------|-----------------|-----------|
| category_id  | カテゴリID        | 必須      |
| name         | カテゴリ名        | 任意      |
| list_order   | 並び順           | 任意      |

---

### /1/categories/delete

- メソッド: POST
- スコープ: `write_items`
- 概要: カテゴリ情報削除

#### リクエストパラメータ

| Name         | Description      | 必須/任意 |
|--------------|-----------------|-----------|
| category_id  | カテゴリID        | 必須      |

---

## 注文(Orders)

### /1/orders

- メソッド: GET
- スコープ: `read_orders`
- 概要: 受注データの一覧取得

#### リクエストパラメータ例

| Name         | Description      | 必須/任意 |
|--------------|-----------------|-----------|
| status       | 受注ステータス    | 任意      |
| limit        | 取得件数         | 任意      |
| offset       | オフセット       | 任意      |

---

### /1/orders/detail

- メソッド: GET
- スコープ: `read_orders`
- 概要: 受注詳細情報取得

#### リクエストパラメータ

| Name    | Description | 必須/任意 |
|---------|-------------|-----------|
| order_id| 注文ID      | 必須      |

---

### /1/orders/edit_status

- メソッド: POST
- スコープ: `write_orders`
- 概要: 受注ステータス変更

#### リクエストパラメータ

| Name    | Description      | 必須/任意 |
|---------|-----------------|-----------|
| order_id| 注文ID           | 必須      |
| status  | ステータス値     | 必須      |

---

## エラーコード一覧

| error                | error_description                   |
|----------------------|-------------------------------------|
| access_denied        | httpsでアクセスしてください。       |
| invalid_request      | アクセストークンが無効です。         |
| invalid_scope        | スコープが無効です。                 |
| not_post_method      | POSTで送信してください。             |
| bad_category_id      | 不正なcategory_idです。              |
| bad_item_id          | 不正なitem_idです。                  |
| bad_parent_number    | 不正なparent_numberです。             |
| validation_error     | バリデーションエラーです。            |
| db_error             | DBエラーです。                       |
| invalid_grant        | 認可コードが不正です。                |

---

# 付録

- 各エンドポイントのレスポンスやエラーは、必要に応じて公式ドキュメントで最新情報を確認してください。
- 本マニュアルは2025年8月時点のBASE API仕様に準拠しています。