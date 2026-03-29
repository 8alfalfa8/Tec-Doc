<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. WAF設計の基本思想（最重要）](#1-waf設計の基本思想最重要)
  - [1.1 設計原則](#11-設計原則)
- [2. WAF全体構成](#2-waf全体構成)
    - [Web ACL構成](#web-acl構成)
- [3. ルール構成（推奨順序）](#3-ルール構成推奨順序)
- [4. AWS Managed Rule 詳細設計](#4-aws-managed-rule-詳細設計)
  - [4.1 Core Rule Set（必須）](#41-core-rule-set必須)
    - [AWSManagedRulesCommonRuleSet](#awsmanagedrulescommonruleset)
  - [4.2 Known Bad Inputs（必須）](#42-known-bad-inputs必須)
    - [AWSManagedRulesKnownBadInputsRuleSet](#awsmanagedrulesknownbadinputsruleset)
  - [4.3 SQLi Rule Set（必須）](#43-sqli-rule-set必須)
    - [AWSManagedRulesSQLiRuleSet](#awsmanagedrulessqliruleset)
  - [4.4 Linux / Unix Rule（任意）](#44-linux-unix-rule任意)
- [5. Rate Based Rule（DDoS・ブルートフォース対策）](#5-rate-based-ruleddosブルートフォース対策)
  - [5.1 基本設計](#51-基本設計)
    - [効果](#効果)
  - [5.2 パス限定レート制限（推奨）](#52-パス限定レート制限推奨)
- [6. カスタムBlockルール設計](#6-カスタムblockルール設計)
  - [6.1 管理画面保護（重要）](#61-管理画面保護重要)
    - [条件](#条件)
  - [6.2 User-Agent制御](#62-user-agent制御)
    - [Block対象例](#block対象例)
  - [6.3 HTTPメソッド制御](#63-httpメソッド制御)
- [7. Bot Control（任意・高機能）](#7-bot-control任意高機能)
  - [7.1 AWS Bot Control](#71-aws-bot-control)
    - [料金注意](#料金注意)
- [8. Geo制御（リージョン制限）](#8-geo制御リージョン制限)
  - [8.1 設計例](#81-設計例)
    - [注意](#注意)
- [9. 例外（Allow）ルール設計（重要）](#9-例外allowルール設計重要)
  - [9.1 誤検知対策の王道](#91-誤検知対策の王道)
    - [例](#例)
- [10. ログ・監査設計](#10-ログ監査設計)
  - [10.1 ログ出力](#101-ログ出力)
    - [監査対応](#監査対応)
  - [10.2 可視化](#102-可視化)
- [11. チューニング手順（実務）](#11-チューニング手順実務)
    - [Step 1](#step-1)
    - [Step 2](#step-2)
    - [Step 3](#step-3)
    - [Step 4](#step-4)
- [12. よくある誤検知と対策](#12-よくある誤検知と対策)
- [13. 成果物一覧](#13-成果物一覧)
- [14. 監査でよくある質問](#14-監査でよくある質問)
<!-- TOC_END -->

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
[🔙 目次に戻る](#index)


### 1.1 設計原則
[🔙 目次に戻る](#index)


| 原則   | 内容               |
| ---- | ---------------- |
| 多層防御 | WAF + ALB + App  |
| 段階適用 | Count → Block    |
| 標準優先 | AWS Managed Rule |
| 例外明示 | Allowは最小限        |
| 証跡重視 | 全ルールログ化          |

👉 **「いきなりBlockしない」**のが監査・運用両面で重要

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 2. WAF全体構成
[🔙 目次に戻る](#index)


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
[🔙 目次に戻る](#index)


| 項目             | 設定                   |
| -------------- | -------------------- |
| Scope          | Regional             |
| 対象             | ALB                  |
| Default Action | Allow                |
| Logging        | 有効（Kinesis Firehose） |

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 3. ルール構成（推奨順序）
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


## 4. AWS Managed Rule 詳細設計
[🔙 目次に戻る](#index)


### 4.1 Core Rule Set（必須）
[🔙 目次に戻る](#index)


#### AWSManagedRulesCommonRuleSet
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 4.2 Known Bad Inputs（必須）
[🔙 目次に戻る](#index)


#### AWSManagedRulesKnownBadInputsRuleSet
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 4.3 SQLi Rule Set（必須）
[🔙 目次に戻る](#index)


#### AWSManagedRulesSQLiRuleSet
[🔙 目次に戻る](#index)


| 対象            | 内容  |
| ------------- | --- |
| SQL Injection | 高精度 |

```text
Priority: 70
Action: Block
```

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 4.4 Linux / Unix Rule（任意）
[🔙 目次に戻る](#index)


| 用途     | 管理画面等 |
| ------ | ----- |
| コマンド注入 | 管理API |

---

[🔙 目次に戻る](#index)


## 5. Rate Based Rule（DDoS・ブルートフォース対策）
[🔙 目次に戻る](#index)


### 5.1 基本設計
[🔙 目次に戻る](#index)


| 項目     | 値               |
| ------ | --------------- |
| 制限     | 2000 req / 5min |
| 単位     | IP              |
| Action | Block           |

```text
Priority: 10
```

#### 効果
[🔙 目次に戻る](#index)


* DDoS軽減
* パスワード総当たり防止

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 5.2 パス限定レート制限（推奨）
[🔙 目次に戻る](#index)


例：ログインAPI

| Path   | 制限             |
| ------ | -------------- |

[🔙 目次に戻る](#index)

| /login | 100 req / 5min |

👉 通常画面と分離するのがベスト

---

[🔙 目次に戻る](#index)


## 6. カスタムBlockルール設計
[🔙 目次に戻る](#index)


### 6.1 管理画面保護（重要）
[🔙 目次に戻る](#index)


#### 条件
[🔙 目次に戻る](#index)


* URI `/admin`
* IPホワイトリスト以外

```text
Action: Block
Priority: 200
```

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 6.2 User-Agent制御
[🔙 目次に戻る](#index)


#### Block対象例
[🔙 目次に戻る](#index)


* curl
* python-requests
* nikto

```text
Action: Block
Priority: 210
```

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



### 6.3 HTTPメソッド制御
[🔙 目次に戻る](#index)


| 許可 | GET / POST   |
| -- | ------------ |
| 拒否 | PUT / DELETE |

👉 API設計に応じて調整

---

[🔙 目次に戻る](#index)


## 7. Bot Control（任意・高機能）
[🔙 目次に戻る](#index)


### 7.1 AWS Bot Control
[🔙 目次に戻る](#index)


| 機能    | 内容    |
| ----- | ----- |
| 悪性Bot | 自動検知  |
| 正常Bot | Allow |

```text
Priority: 300
```

#### 料金注意
[🔙 目次に戻る](#index)


* リクエスト課金あり
* 本番のみ推奨

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 8. Geo制御（リージョン制限）
[🔙 目次に戻る](#index)


### 8.1 設計例
[🔙 目次に戻る](#index)


| 国      | Action |
| ------ | ------ |
| JP     | Allow  |
| Others | Block  |

```text
Priority: 400
```

#### 注意
[🔙 目次に戻る](#index)


* VPN回避あり
* 監査で理由説明必須

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 9. 例外（Allow）ルール設計（重要）
[🔙 目次に戻る](#index)


### 9.1 誤検知対策の王道
[🔙 目次に戻る](#index)


#### 例
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 10. ログ・監査設計
[🔙 目次に戻る](#index)


### 10.1 ログ出力
[🔙 目次に戻る](#index)


| 項目  | 設定   |
| --- | ---- |
| 保存先 | S3   |
| 形式  | JSON |
| 保持  | 1年   |

#### 監査対応
[🔙 目次に戻る](#index)


* いつ・どのIPが・どのルールに引っかかったか

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 10.2 可視化
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* Athena + S3
* CloudWatch Dashboard

---

[🔙 目次に戻る](#index)


## 11. チューニング手順（実務）
[🔙 目次に戻る](#index)


#### Step 1
[🔙 目次に戻る](#index)


* 全Managed Rule → Count

[🔙 目次に戻る](#index)


#### Step 2
[🔙 目次に戻る](#index)


* 1〜2週間ログ分析

[🔙 目次に戻る](#index)


#### Step 3
[🔙 目次に戻る](#index)


* 誤検知例外追加

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



#### Step 4
[🔙 目次に戻る](#index)


* Block切替

---

[🔙 目次に戻る](#index)


## 12. よくある誤検知と対策
[🔙 目次に戻る](#index)


| 誤検知    | 対策       |
| ------ | -------- |
| 日本語検索  | Query除外  |
| JSON   | Body検査調整 |
| Base64 | サイズ制限    |

---

[🔙 目次に戻る](#index)


## 13. 成果物一覧
[🔙 目次に戻る](#index)


* WAF設計書（本資料）
* Web ACL構成図
* ルール一覧表（Priority/Action）
* 誤検知対応記録
* ログ保存ポリシー

---

[🔙 目次に戻る](#index)


## 14. 監査でよくある質問
[🔙 目次に戻る](#index)


**Q. なぜこのルール順？**
→ Allow例外 → Rate制限 → 一般攻撃 → 特殊攻撃 の順で影響最小化。

**Q. 誤検知は？**
→ Count運用 → ログ分析 → 例外化。

---

[🔙 目次に戻る](#index)

