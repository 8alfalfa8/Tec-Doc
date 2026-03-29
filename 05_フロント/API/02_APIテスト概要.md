<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. APIテストの全体像（まず俯瞰）](#1-apiテストの全体像まず俯瞰)
  - [1.1 APIテストの位置づけ](#11-apiテストの位置づけ)
    - [APIテストの目的](#apiテストの目的)
- [2. APIテスト設計（考え方）](#2-apiテスト設計考え方)
  - [2.1 設計方針（最重要）](#21-設計方針最重要)
  - [2.2 テスト観点一覧（チェックリスト）](#22-テスト観点一覧チェックリスト)
    - [共通観点（全API必須）](#共通観点全api必須)
    - [画面系API（BFF特有）](#画面系apibff特有)
- [3. APIテスト方法（何を使うか）](#3-apiテスト方法何を使うか)
  - [3.1 採用技術](#31-採用技術)
- [4. 構築手順（Step by Step）](#4-構築手順step-by-step)
  - [Step 1：テスト環境構築](#step-1テスト環境構築)
  - [Step 2：ディレクトリ構成作成](#step-2ディレクトリ構成作成)
  - [Step 3：TestClient 定義（conftest.py）](#step-3testclient-定義conftestpy)
  - [Step 4：認証モック設定](#step-4認証モック設定)
  - [Step 5：外部依存モック（重要）](#step-5外部依存モック重要)
    - [5.1 Dependency Override](#51-dependency-override)
  - [Step 6：APIテスト実装（例）](#step-6apiテスト実装例)
    - [6.1 正常系](#61-正常系)
    - [6.2 入力エラー（400）](#62-入力エラー400)
    - [6.3 認証エラー（401）](#63-認証エラー401)
    - [6.4 認可エラー（403）](#64-認可エラー403)
  - [Step 7：エラーレスポンス検証](#step-7エラーレスポンス検証)
  - [Step 8：OpenAPI 契約テスト](#step-8openapi-契約テスト)
- [5. テスト実行](#5-テスト実行)
- [6. CI/CD 組み込み（例）](#6-cicd-組み込み例)
- [7. 運用ルール（実務）](#7-運用ルール実務)
  - [7.1 テスト追加ルール](#71-テスト追加ルール)
  - [7.2 命名規約](#72-命名規約)
- [8. よくある失敗](#8-よくある失敗)
- [9. 金融・公共向け追加対応](#9-金融公共向け追加対応)
- [10. まとめ（重要ポイント）](#10-まとめ重要ポイント)
<!-- TOC_END -->

# ◆ APIテスト概要
以下では、**FastAPI（BFF）× OpenAPI × pytest** を前提に、
**実務（業務システム／金融・公共レベル）で通用する APIテスト**を
**設計 → 方法 → 構築手順 → 運用**まで、**作業手順書レベル**で詳しく説明します。

（これまでの流れ：API設計 → OpenAPI / Components → **APIテスト設計・構築**）

---

## 1. APIテストの全体像（まず俯瞰）
[🔙 目次に戻る](#index)


### 1.1 APIテストの位置づけ
[🔙 目次に戻る](#index)


```
単体テスト（Service）
   ↓
APIテスト（Router + Schema） ← 本テーマ
   ↓
E2E（画面＋API）
```

#### APIテストの目的
[🔙 目次に戻る](#index)


* API契約（OpenAPI）を守っているか
* 認証・認可・異常系が正しく動くか
* フロント実装を壊さないか

---

## 2. APIテスト設計（考え方）
[🔙 目次に戻る](#index)


### 2.1 設計方針（最重要）
[🔙 目次に戻る](#index)


| 項目    | 方針                   |
| ----- | -------------------- |
| 粒度    | **API単位（エンドポイント単位）** |
| 観点    | 正常系 + 異常系            |
| DB    | モック or テスト用          |
| 外部API | 必ずモック                |
| 認証    | 実装前提でテスト             |
| 契約    | OpenAPI準拠            |

---

### 2.2 テスト観点一覧（チェックリスト）
[🔙 目次に戻る](#index)


#### 共通観点（全API必須）
[🔙 目次に戻る](#index)


| 観点      | 内容              |
| ------- | --------------- |
| ステータス   | 200 / 4xx / 5xx |
| レスポンス形式 | JSON / Schema   |
| 必須項目    | 欠落していない         |
| 不要項目    | 出ていない           |
| 認証      | 401             |
| 認可      | 403             |
| 例外      | 想定外エラー          |

---

#### 画面系API（BFF特有）
[🔙 目次に戻る](#index)


* データ過不足がない
* 画面描画に必要な項目が揃っている
* Null許容の扱い

---

## 3. APIテスト方法（何を使うか）
[🔙 目次に戻る](#index)


### 3.1 採用技術
[🔙 目次に戻る](#index)


| 目的         | 技術                   |
| ---------- | -------------------- |
| テスト実行      | pytest               |
| HTTPクライアント | FastAPI TestClient   |
| 非同期        | pytest-asyncio       |
| モック        | dependency_overrides |
| 契約         | OpenAPI              |
| CI         | GitHub Actions       |

---

## 4. 構築手順（Step by Step）
[🔙 目次に戻る](#index)


### Step 1：テスト環境構築
[🔙 目次に戻る](#index)


```bash
pip install pytest pytest-asyncio httpx
```

FastAPI:

```bash
pip install fastapi[all]
```

---

### Step 2：ディレクトリ構成作成
[🔙 目次に戻る](#index)


```text
tests/
 ├ conftest.py        ← 共通設定
 ├ api/               ← APIテスト
 │   └ test_users.py
 ├ mocks/             ← 外部APIモック
 └ services/          ← 単体テスト
```

---

### Step 3：TestClient 定義（conftest.py）
[🔙 目次に戻る](#index)


```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)
```

---

### Step 4：認証モック設定
[🔙 目次に戻る](#index)


```python
@pytest.fixture
def auth_header():
    return {
        "Authorization": "Bearer dummy-token"
    }
```

---

### Step 5：外部依存モック（重要）
[🔙 目次に戻る](#index)


#### 5.1 Dependency Override
[🔙 目次に戻る](#index)


```python
from app.clients.core_api import get_core_client

class DummyClient:
    def get_users(self):
        return []

def override_core_client():
    return DummyClient()

app.dependency_overrides[get_core_client] = override_core_client
```

👉 **DB・外部APIを切り離す**

---

### Step 6：APIテスト実装（例）
[🔙 目次に戻る](#index)


#### 6.1 正常系
[🔙 目次に戻る](#index)


```python
def test_get_users_success(client, auth_header):
    res = client.get("/api/bff/v1/users", headers=auth_header)

    assert res.status_code == 200

    body = res.json()
    assert "items" in body
    assert "total" in body
```

---

#### 6.2 入力エラー（400）
[🔙 目次に戻る](#index)


```python
def test_get_users_invalid_param(client, auth_header):
    res = client.get(
        "/api/bff/v1/users?page=-1",
        headers=auth_header
    )

    assert res.status_code == 400
```

---

#### 6.3 認証エラー（401）
[🔙 目次に戻る](#index)


```python
def test_get_users_unauthorized(client):
    res = client.get("/api/bff/v1/users")
    assert res.status_code == 401
```

---

#### 6.4 認可エラー（403）
[🔙 目次に戻る](#index)


```python
def test_get_users_forbidden(client, auth_header):
    res = client.get(
        "/api/bff/v1/admin",
        headers=auth_header
    )
    assert res.status_code == 403
```

---

### Step 7：エラーレスポンス検証
[🔙 目次に戻る](#index)


```python
def test_user_not_found(client, auth_header):
    res = client.get(
        "/api/bff/v1/users/999",
        headers=auth_header
    )

    body = res.json()
    assert res.status_code == 404
    assert body["code"] == "USER_NOT_FOUND"
```

---

### Step 8：OpenAPI 契約テスト
[🔙 目次に戻る](#index)


```python
def test_openapi_schema(client):
    res = client.get("/openapi.json")
    assert res.status_code == 200
```

👉 CIで差分検知すると **破壊的変更防止**

---

## 5. テスト実行
[🔙 目次に戻る](#index)


```bash
pytest -v
```

---

## 6. CI/CD 組み込み（例）
[🔙 目次に戻る](#index)


```yaml
- name: Run API Tests
  run: |
    pytest --maxfail=1 --disable-warnings
```

品質ゲート：

* テスト失敗 → マージ不可
* Coverage 80%以上

---

## 7. 運用ルール（実務）
[🔙 目次に戻る](#index)


### 7.1 テスト追加ルール
[🔙 目次に戻る](#index)


* API追加 → テスト必須
* OpenAPI変更 → テスト修正
* バグ修正 → 再現テスト追加

---

### 7.2 命名規約
[🔙 目次に戻る](#index)


```text
test_[HTTPメソッド]_[条件]_[期待結果]
```

例：

```text
test_get_users_unauthorized_401
```

---

## 8. よくある失敗
[🔙 目次に戻る](#index)


❌ DB直結テスト<br>
❌ 正常系のみ<br>
❌ OpenAPI未検証<br>
❌ 認証スキップ

---

## 9. 金融・公共向け追加対応
[🔙 目次に戻る](#index)


* 監査ログ出力テスト
* エラー情報秘匿テスト
* レート制限テスト
* セキュリティヘッダ検証

---

## 10. まとめ（重要ポイント）
[🔙 目次に戻る](#index)


✔ APIテストは **契約テスト**<br>
✔ BFFでは **画面単位API** を検証<br>
✔ pytest + FastAPI が最適<br>
✔ 認証・異常系を必ず含める<br>
✔ CIで品質を自動担保

---

