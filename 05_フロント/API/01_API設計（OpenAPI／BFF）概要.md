
# ◆ API設計（OpenAPI / BFF）概要

以下では、**FastAPI（BFF）× OpenAPI** を前提に、
**実務（業務システム／金融・公共レベル）で通用する API設計**を
**設計思想 → OpenAPI設計 → BFF設計パターン → 実装・運用**の流れで体系的に解説します。

---

## 1. OpenAPI × BFF の位置づけ

### 1.1 なぜ OpenAPI を「設計の中心」に置くか

OpenAPI は単なる Swagger ではありません。

✔ **API契約（Contract）**<br>
✔ **フロント・バックの合意文書**<br>
✔ **テスト・型生成・監査の起点**

👉 BFF では 「**画面仕様＝API仕様**」 になるため、OpenAPIとの親和性が非常に高い。

---

## 2. BFF向け API設計原則

| 観点   | 原則          |
| ---- | ----------- |
| 粒度   | **画面単位API** |
| 利用者  | フロント限定      |
| 目的   | 画面表示最適化     |
| DB露出 | **禁止**      |
| 変更耐性 | フロント変更に追従   |
| 契約   | OpenAPIで固定  |

---

## 3. OpenAPI 設計方針（重要）

### 3.1 設計順序（推奨）

```
① 画面設計
② 画面単位API洗い出し
③ OpenAPI定義（YAML）
④ FastAPI実装
⑤ テスト & CI
```

👉 **コードファーストではなく「設計ファースト」**

---

### 3.2 APIパス設計（BFF特化）

```
/api/bff/v1/users
/api/bff/v1/users/{id}
/api/bff/v1/dashboard
```

* `/bff/` を必ず含める
* バージョン固定（v1）

---

## 4. OpenAPI 設計例（YAML）

### 4.1 ユーザー一覧画面 API

```yaml
openapi: 3.0.3
info:
  title: BFF API
  version: 1.0.0

paths:
  /api/bff/v1/users:
    get:
      summary: ユーザー一覧取得
      tags: [Users]
      parameters:
        - in: query
          name: page
          schema:
            type: integer
            minimum: 1
        - in: query
          name: size
          schema:
            type: integer
            maximum: 100
      responses:
        "200":
          description: 成功
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UserListResponse"
        "401":
          $ref: "#/components/responses/Unauthorized"
```

---

## 5. Components（API仕様を部品化・再利用するための定義集） 設計（再利用の要）

### 5.1 Schema

```yaml
components:
  schemas:
    User:
      type: object
      required: [id, name, email]
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string

    UserListResponse:
      type: object
      required: [items, total]
      properties:
        items:
          type: array
          items:
            $ref: "#/components/schemas/User"
        total:
          type: integer
```

---

### 5.2 共通レスポンス（重要）

```yaml
components:
  responses:
    Unauthorized:
      description: 認証エラー
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ErrorResponse"
```

---

### 5.3 共通エラー

```yaml
components:
  schemas:
    ErrorResponse:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
        message:
          type: string
```

---

## 6. 認証・認可定義（OpenAPI）

### 6.1 Security Scheme

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

```yaml
security:
  - bearerAuth: []
```

---

## 7. FastAPI への反映（実装）

FastAPIは OpenAPI-first が可能。

```python
@router.get(
    "/users",
    response_model=UserListResponse,
    summary="ユーザー一覧取得"
)
def get_users(...):
    ...
```

👉 **Pydantic = OpenAPI Schema**

---

## 8. OpenAPI 活用（実務で効く）

### 8.1 フロント向け型生成

```bash
openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-fetch \
  -o frontend/api
```

✔ API型安全
✔ 実装ミス防止

---

### 8.2 契約テスト

* OpenAPI変更 → CIで検知
* Breaking Change 防止

---

## 9. BFF特有の設計パターン

### 9.1 Aggregation API

```
GET /bff/dashboard
```

```json
{
  "summary": {...},
  "alerts": [...],
  "metrics": {...}
}
```

👉 **複数バックエンド集約**

---

### 9.2 View Model API

```
GET /bff/users/{id}/view
```

* 画面表示専用
* CRUDと分離

---

## 10. アンチパターン（要注意）

❌ CRUD API をそのまま公開<br>
❌ DBスキーマ露出<br>
❌ レスポンスの過剰汎用化<br>
❌ バージョンなしAPI

---

## 11. 運用・変更管理

| 項目   | 対応              |
| ---- | --------------- |
| 変更   | minor/major ルール |
| 廃止   | deprecated 記載   |
| レビュー | OpenAPI差分       |
| 監査   | API一覧提出         |

---

## 12. 金融・公共向け追加設計

* OpenAPIレビュー証跡
* API一覧管理台帳
* 認可スコープ明示
* エラーメッセージ統制

---

## 13. まとめ（設計の勘所）

✔ OpenAPI は **契約そのもの**<br>
✔ BFF は **画面専用API**<br>
✔ 設計 → OpenAPI → 実装の順<br>
✔ Components徹底再利用<br>
✔ CIで破壊的変更を防ぐ

---

