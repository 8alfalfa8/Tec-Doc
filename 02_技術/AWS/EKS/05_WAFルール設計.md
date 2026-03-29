# ◆ WAFルール設計

以下は、**AWS WAF v2 × ALB Ingress × EKS**（**Tomcat**）を前提にした
**WAFルール設計（設計書レベル）**です。

**監査・顧客説明・実装にそのまま使える**ように、

* 設計思想
* ルール構成
* 個別ルール定義
* 優先度設計
* チューニング・誤検知対策
* 成果物
  までを体系的に整理します。

---

## 1. WAF設計の基本思想（最重要）

### 1.1 設計原則

| 原則   | 内容               |
| ---- | ---------------- |
| 多層防御 | WAF + ALB + App  |
| 段階適用 | Count → Block    |
| 標準優先 | AWS Managed Rule |
| 例外明示 | Allowは最小限        |
| 証跡重視 | 全ルールログ化          |

👉 **「いきなりBlockしない」**のが監査・運用両面で重要

---

## 2. WAF全体構成

```
Client
 ↓
AWS WAF
 ↓
ALB
 ↓
Ingress
 ↓
Service / Pod
```

#### Web ACL構成

| 項目             | 設定                   |
| -------------- | -------------------- |
| Scope          | Regional             |
| 対象             | ALB                  |
| Default Action | Allow                |
| Logging        | 有効（Kinesis Firehose） |

---

## 3. ルール構成（推奨順序）

**優先度（小さい数字ほど先に評価）**

| Priority | ルール種別             |
| -------- | ----------------- |
| 0–9      | Allow（例外）         |
| 10–49    | Rate Limit        |
| 50–199   | AWS Managed Rules |
| 200–299  | Custom Block      |
| 300–399  | Bot Control       |
| 400–499  | Geo制御             |

---

## 4. AWS Managed Rule 詳細設計

### 4.1 Core Rule Set（必須）

#### AWSManagedRulesCommonRuleSet

| 攻撃   | 内容            |
| ---- | ------------- |
| SQLi | SQL Injection |
| XSS  | クロスサイト        |
| LFI  | ローカルファイル      |
| RFI  | リモートファイル      |

```text
Priority: 50
Action: Count → Block
```

👉 **まずCountでログ確認 → 本番Block**

---

### 4.2 Known Bad Inputs（必須）

#### AWSManagedRulesKnownBadInputsRuleSet

| 対象    | 内容        |
| ----- | --------- |
| 悪性文字列 | 明確な攻撃パターン |
| 不正UA  | 既知ツール     |

```text
Priority: 60
Action: Block
```

誤検知が少ないため **即Block可**

---

### 4.3 SQLi Rule Set（必須）

#### AWSManagedRulesSQLiRuleSet

| 対象            | 内容  |
| ------------- | --- |
| SQL Injection | 高精度 |

```text
Priority: 70
Action: Block
```

---

### 4.4 Linux / Unix Rule（任意）

| 用途     | 管理画面等 |
| ------ | ----- |
| コマンド注入 | 管理API |

---

## 5. Rate Based Rule（DDoS・ブルートフォース対策）

### 5.1 基本設計

| 項目     | 値               |
| ------ | --------------- |
| 制限     | 2000 req / 5min |
| 単位     | IP              |
| Action | Block           |

```text
Priority: 10
```

#### 効果

* DDoS軽減
* パスワード総当たり防止

---

### 5.2 パス限定レート制限（推奨）

例：ログインAPI

| Path   | 制限             |
| ------ | -------------- |
| /login | 100 req / 5min |

👉 通常画面と分離するのがベスト

---

## 6. カスタムBlockルール設計

### 6.1 管理画面保護（重要）

#### 条件

* URI `/admin`
* IPホワイトリスト以外

```text
Action: Block
Priority: 200
```

---

### 6.2 User-Agent制御

#### Block対象例

* curl
* python-requests
* nikto

```text
Action: Block
Priority: 210
```

---

### 6.3 HTTPメソッド制御

| 許可 | GET / POST   |
| -- | ------------ |
| 拒否 | PUT / DELETE |

👉 API設計に応じて調整

---

## 7. Bot Control（任意・高機能）

### 7.1 AWS Bot Control

| 機能    | 内容    |
| ----- | ----- |
| 悪性Bot | 自動検知  |
| 正常Bot | Allow |

```text
Priority: 300
```

#### 料金注意

* リクエスト課金あり
* 本番のみ推奨

---

## 8. Geo制御（リージョン制限）

### 8.1 設計例

| 国      | Action |
| ------ | ------ |
| JP     | Allow  |
| Others | Block  |

```text
Priority: 400
```

#### 注意

* VPN回避あり
* 監査で理由説明必須

---

## 9. 例外（Allow）ルール設計（重要）

### 9.1 誤検知対策の王道

#### 例

* 正常なパラメータでSQLi誤検知

```text
Condition:
  Path = /search
  QueryString = q
Action: Allow
Priority: 0
```

👉 **Blockルールより先に評価**

---

## 10. ログ・監査設計

### 10.1 ログ出力

| 項目  | 設定   |
| --- | ---- |
| 保存先 | S3   |
| 形式  | JSON |
| 保持  | 1年   |

#### 監査対応

* いつ・どのIPが・どのルールに引っかかったか

---

### 10.2 可視化

* Athena + S3
* CloudWatch Dashboard

---

## 11. チューニング手順（実務）

#### Step 1

* 全Managed Rule → Count

#### Step 2

* 1〜2週間ログ分析

#### Step 3

* 誤検知例外追加

#### Step 4

* Block切替

---

## 12. よくある誤検知と対策

| 誤検知    | 対策       |
| ------ | -------- |
| 日本語検索  | Query除外  |
| JSON   | Body検査調整 |
| Base64 | サイズ制限    |

---

## 13. 成果物一覧

* WAF設計書（本資料）
* Web ACL構成図
* ルール一覧表（Priority/Action）
* 誤検知対応記録
* ログ保存ポリシー

---

## 14. 監査でよくある質問

**Q. なぜこのルール順？**
→ Allow例外 → Rate制限 → 一般攻撃 → 特殊攻撃 の順で影響最小化。

**Q. 誤検知は？**
→ Count運用 → ログ分析 → 例外化。

---
