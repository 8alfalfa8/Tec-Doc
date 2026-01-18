
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

# ◆ BFF API バージョン戦略

以下では、**FastAPI（BFF）× OpenAPI** を前提に、
**業務システム／金融・公共レベルでも破綻しない BFF API バージョン戦略**を
**設計思想 → 方式選定 → 実装 → 運用 → 移行**まで体系的に説明します。

---

## 1. なぜ BFF に「明確なバージョン戦略」が必要か

BFF は **フロント専用API** であり、次の特性を持ちます。

* UI変更に最も影響を受ける
* 変更頻度が高い
* フロントと密結合

👉 **無秩序に変更すると、即座にフロント破壊**

---

## 2. BFF におけるバージョン戦略の結論

### 2.1 推奨結論（実務ベスト）

> **URL パスバージョン方式 + 明確な破壊的変更ルール**

```
/api/bff/v1/...
/api/bff/v2/...
```

理由：

* 明示的で分かりやすい
* フロント・監査・運用に強い
* OpenAPI と相性抜群

---

## 3. バージョニング方式の比較

| 方式     | 採用 | 理由       |
| ------ | -- | -------- |
| URLパス  | ◎  | 明確・運用容易  |
| Header | △  | 可視性が低い   |
| Query  | ×  | 誤用されやすい  |
| Accept | △  | 複雑・教育コスト |

👉 **金融・公共では URL方式が事実上の標準**

---

## 4. バージョン定義ルール（重要）

### 4.1 何が「バージョンアップ」か

#### ❌ バージョンを上げない変更

* 項目追加（optional）
* パフォーマンス改善
* 内部実装変更

#### ⭕ バージョンを上げる変更

* 項目削除
* 型変更
* 意味変更
* API統合・分割

👉 **フロントが修正必要ならバージョンアップ**

---

## 5. ディレクトリ構成（FastAPI）

```text
app/
 ├ api/
 │   ├ v1/
 │   │   └ users.py
 │   └ v2/
 │       └ users.py
 └ main.py
```

```python
app.include_router(v1_router, prefix="/api/bff/v1")
app.include_router(v2_router, prefix="/api/bff/v2")
```

---

## 6. OpenAPI におけるバージョン管理

### 6.1 OpenAPI ファイル分割

```text
openapi/
 ├ v1.yaml
 └ v2.yaml
```

```yaml
info:
  version: "1.0.0"
```

---

### 6.2 deprecated の使い方

```yaml
/api/bff/v1/users:
  get:
    deprecated: true
```

👉 **即削除しない**

---

## 7. フロント（Next.js）側の対応

```ts
const API_BASE = "/api/bff/v1"
```

v2移行時：

```ts
const API_BASE = "/api/bff/v2"
```

👉 **切替は最小差分**

---

## 8. 移行戦略（実務で最重要）

### 8.1 並行稼働（Blue-Green）

```
v1 (既存)
v2 (新)
```

* v1 を deprecated
* v2 を追加
* 段階的移行

---

### 8.2 移行フロー（例）

1. v2 API 実装
2. OpenAPI v2 公開
3. フロント一部画面を v2 対応
4. 全移行完了
5. v1 廃止

---

## 9. テスト・CI とバージョン

* **バージョンごとにテスト**
* v1/v2 両方を CI で検証
* OpenAPI差分チェック

---

## 10. 監査・金融向け追加ルール

| 観点 | 内容          |
| -- | ----------- |
| 台帳 | APIバージョン管理表 |
| 期限 | 廃止予定日明記     |
| 通知 | 利用者影響通知     |
| 証跡 | レビュー履歴      |

---

## 11. よくある失敗

❌ v1 を上書き修正<br>
❌ deprecated 無視<br>
❌ フロント同時修正強制<br>
❌ OpenAPI未更新

---

## 12. ベストプラクティスまとめ

✔ BFFは **URLバージョン必須**<br>
✔ 破壊的変更のみバージョンUP<br>
✔ 並行稼働を前提<br>
✔ OpenAPIを単一真実源に<br>
✔ 廃止は計画的に

---

