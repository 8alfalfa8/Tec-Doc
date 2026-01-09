# ◆ API専用WAF設計

以下は、**API専用（REST/JSON）向けの AWS WAF 設計**を、
**EKS × ALB Ingress × Tomcat**（**またはAPIサーバ**）前提でまとめた
**実運用・監査・セキュリティレビュー対応レベルの設計書**です。

Web画面向けWAFとは思想・ルールが大きく異なるため、
「**API特有の脅威に特化した設計**」として整理します。

---

## 1. API専用WAFの設計思想（Webとの違い）

### 1.1 Web向けWAFとの決定的な違い

| 観点   | Web画面     | API       |
| ---- | --------- | --------- |
| 通信形式 | HTML/FORM | JSON      |
| 利用者  | 人         | システム      |
| 攻撃   | XSS中心     | 不正API呼出   |
| 誤検知  | 多い        | 少ない（設計次第） |

👉 **APIは「仕様通りかどうか」を厳格に見る**

---

### 1.2 API WAFの基本原則

| 原則     | 内容           |
| ------ | ------------ |
| 明示的許可  | Allow List前提 |
| レート制御  | 必須           |
| メソッド制限 | GET/POST限定   |
| JSON前提 | Body検査最適化    |
| 自動化耐性  | Bot/スクリプト対策  |

---

## 2. 全体アーキテクチャ（API専用）

```
Client / System
   ↓
AWS WAF（API ACL）
   ↓
ALB（/api/* 専用）
   ↓
Ingress（api.example.com）
   ↓
Service / Pod（API）
```

#### ポイント

* **Web用ALB/WAFと分離（推奨）**
* 最低でも **Web ACLは分離**

---

## 3. Web ACL 基本設計（API用）

| 項目      | 設計        |
| ------- | --------- |
| Scope   | Regional  |
| 対象      | ALB       |
| Default | Block（推奨） |
| Logging | 必須        |
| 可視化     | Athena    |

👉 APIは **Default Block + Allow設計** が理想

---

## 4. ルール優先度設計（API向け）

| Priority | 種別           |
| -------- | ------------ |
| 0–9      | Allow（正規API） |
| 10–49    | Rate Limit   |
| 50–99    | Method制御     |
| 100–199  | AWS Managed  |
| 200–299  | Custom Block |
| 300–399  | Geo制御        |

---

## 5. Allow（正規API）ルール設計（最重要）

### 5.1 パスAllow（API仕様ベース）

例：`/api/v1/*`

```text
Condition:
  URI startsWith /api/v1/
Action:
  Allow
Priority:
  0
```

#### 監査説明

> API仕様書に記載されたエンドポイントのみを許可しています。

---

### 5.2 Header Allow（API Key / JWT）

#### 必須Header例

* `Authorization`
* `X-API-KEY`

```text
Condition:
  Header exists Authorization
Action:
  Allow
```

👉 Headerが無い通信は **Default Block**

---

## 6. Rate Limit 設計（API最重要）

### 6.1 IPベース制限

| 項目     | 値              |
| ------ | -------------- |
| 制限     | 300 req / 5min |
| Action | Block          |

```text
Priority: 10
```

---

### 6.2 API単位制限（推奨）

| API         | 制限         |
| ----------- | ---------- |
| /api/login  | 50 / 5min  |
| /api/search | 200 / 5min |

👉 **ログイン系は特に厳格**

---

## 7. HTTPメソッド制御（API特有）

### 7.1 許可メソッド

| 許可      | 拒否     |
| ------- | ------ |
| GET     | PUT    |
| POST    | DELETE |
| OPTIONS | PATCH  |

```text
Condition:
  Method NOT IN [GET, POST, OPTIONS]
Action:
  Block
Priority:
  50
```

---

## 8. JSON Body検査設計（誤検知防止）

### 8.1 Managed Rule調整（重要）

#### AWSManagedRulesCommonRuleSet

| 対象   | 設定     |
| ---- | ------ |
| Body | Size制限 |
| JSON | 正規化    |

👉 Web向けXSS誤検知を抑制

---

### 8.2 サイズ制限

| 項目        | 値        |
| --------- | -------- |
| JSON Body | 8KB〜16KB |
| 超過        | Block    |

---

## 9. AWS Managed Rule（API向け）

| ルール            | 方針            |
| -------------- | ------------- |
| CommonRuleSet  | Count → Block |
| SQLiRuleSet    | Block         |
| KnownBadInputs | Block         |
| LinuxRule      | 必要時           |

---

## 10. Bot / 自動化対策（API）

### 10.1 User-Agent制御

Block対象例：

* curl
* python-requests
* postman-runtime（本番）

```text
Priority: 200
```

---

### 10.2 Bot Control（高要件）

* Credential stuffing
* Scraping

👉 **課金注意／本番のみ**

---

## 11. Geo制御（APIでは有効）

| 国      | Action |
| ------ | ------ |
| JP     | Allow  |
| Others | Block  |

👉 APIは業務範囲が明確なため適用しやすい

---

## 12. ログ・監査設計（APIは厳格）

### 12.1 ログ要件

| 項目 | 内容               |
| -- | ---------------- |
| 保存 | S3               |
| 期間 | 1年以上             |
| 内容 | IP / Path / Rule |

---

### 12.2 監査での説明例

> API通信はWAFで仕様外アクセスを遮断し、
> 正規エンドポイント・認証ヘッダを満たす通信のみ許可しています。

---

## 13. API専用WAFのアンチパターン

| NG            | 理由       |
| ------------- | -------- |
| Web用WAF流用     | 誤検知多発    |
| Default Allow | 不正API露出  |
| Rate制御なし      | ブルートフォース |
| Header未検査     | 認証回避     |

---

## 14. 成果物一覧（設計・監査提出）

* API WAF設計書
* Web ACLルール一覧
* API仕様 × WAF対応表
* Rate Limit設計書
* 誤検知対応記録
* ログ保存ポリシー

---

## 15. Web用WAFとの比較（まとめ）

| 観点      | Web   | API   |
| ------- | ----- | ----- |
| Default | Allow | Block |
| 主制御     | 攻撃検知  | 仕様遵守  |
| Rate    | 緩     | 厳     |
| Header  | 任意    | 必須    |

---

