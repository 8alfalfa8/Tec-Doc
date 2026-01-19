# AWS Route53 × BIND ハイブリッドDNS詳細設計書

## 1. 文書概要

### 1.1 目的

本書は、AWS Route53 と オンプレミス／IaaS上の BIND を組み合わせたハイブリッドDNS構成について、金融・公共系システムに適用可能な詳細設計を定義する。

### 1.2 適用範囲

* AWS Route53（Public / Private Hosted Zone）
* オンプレミス／クラウド上のBIND9
* 内部DNS／外部DNS

### 1.3 前提基準

* FISC安全対策基準
* ISMAP
* AWS Well-Architected（Security / Reliability）

---

## 2. 全体アーキテクチャ設計

### 2.1 論理構成

```
[Client]
   |
[Cache DNS(Unbound)]
   |
+---------------------+
|  BIND(Authoritative)|  <---->  Route53
+---------------------+
   |
[Internet Root]
```

### 2.2 役割分担

| コンポーネント         | 役割               |
| --------------- | ---------------- |
| Route53 Public  | 外部公開DNS、DNSSEC対応 |
| Route53 Private | AWS内部名前解決        |
| BIND（権威）        | 内部ゾーン管理          |
| Unbound         | 再帰DNS            |

---

## 3. ゾーン分割設計（Split DNS）

### 3.1 ゾーン管理方針

| ゾーン                  | 管理先             | 公開範囲    |
| -------------------- | --------------- | ------- |
| example.com          | Route53 Public  | インターネット |
| aws.example.com      | Route53 Private | AWS内部   |
| internal.example.com | BIND            | 社内NW    |

### 3.2 委任設計

* Route53 → BIND へのNS委任（内部専用）
* 条件付きフォワード利用

---

## 4. Route53設計

### 4.1 Public Hosted Zone

* DNSSEC：有効
* レコード管理：ALB / CloudFront
* TTL：60〜300秒

### 4.2 Private Hosted Zone

* VPC関連付け
* オンプレDNSから条件付きフォワード

---

## 5. BIND設計（オンプレ／IaaS）

### 5.1 権威DNS設定

* recursion：no
* allow-query：内部NW限定
* ゾーン：internal.example.com

### 5.2 Route53連携

* フォワーダ：VPC Resolver
* TSIG利用（内部転送）

---

## 6. 名前解決フロー

### 6.1 外部公開系

1. Client → Public DNS
2. Route53 Public → 応答

### 6.2 AWS内部系

1. EC2 → Route53 Resolver
2. Private Hosted Zone

### 6.3 社内内部系

1. Client → Unbound
2. BIND（internal zone）

---

## 7. セキュリティ設計

### 7.1 DNSSEC適用範囲

| 対象              | DNSSEC |
| --------------- | ------ |
| Route53 Public  | 有効     |
| Route53 Private | 非対応    |
| BIND Internal   | 方針次第   |

### 7.2 通信制御

* UDP/TCP 53 のみ
* セキュリティグループ／FW制御

---

## 8. 可用性・冗長設計

### 8.1 Route53

* マルチAZ（AWS管理）

### 8.2 BIND

* マスター／スレーブ
* 異拠点配置

---

## 9. 運用設計

### 9.1 レコード管理分担

| 種別   | 管理者    |
| ---- | ------ |
| 外部公開 | AWS管理者 |
| 内部   | 基盤運用者  |

### 9.2 変更手順

* TTL短縮
* 並行稼働
* 切戻し設計

---

## 10. 障害対応設計

### 10.1 Route53障害時

* 他AZ影響なし
* 内部DNSには影響なし

### 10.2 BIND障害時

* スレーブ切替
* キャッシュ活用

---

## 11. 監視設計

### 11.1 Route53

* Route53 Health Check
* CloudWatch

### 11.2 BIND

* プロセス監視
* 応答監視（dig）

---

## 12. 監査対応ポイント（金融・公共）

| 観点   | 説明         |
| ---- | ---------- |
| 境界分離 | 外部／内部ゾーン分離 |
| 責任分界 | AWS責任共有モデル |
| 証跡   | 変更履歴・ログ    |

---

## 13. 付録

### 13.1 比較（Route53 vs BIND）

| 項目   | Route53 | BIND |
| ---- | ------- | ---- |
| 可用性  | ◎       | △    |
| 柔軟性  | △       | ◎    |
| 運用負荷 | 低       | 高    |

### 13.2 用語集

* Hosted Zone
* Resolver
* Conditional Forward

---


# ◆ 本設計書についての説明

本設計書は **監査・設計レビューでそのまま提出可能な粒度** で、
Route53とBINDの **責任分界・ゾーン分割・セキュリティ境界** を明確にしています。

---

## 本設計書の強み（実務視点）

### ✅ 金融・公共で突っ込まれやすい論点を網羅

* **Split DNS（外部／AWS内部／社内）** の明確な分離
* Route53（マネージド）とBIND（自己管理）の**責任境界**
* DNSSECの **適用可否と理由**（Publicのみ）
* 「なぜBINDを残すのか？」への説明材料

### ✅ AWS監査・FISC対応しやすい構成

* Route53：可用性・DNSSECをAWS責任範囲で担保
* BIND：内部統制・詳細制御・ログ完全取得
* ハイブリッドでも **再帰・権威・管理責任が混ざらない**

---

## 典型ユースケース

* 金融機関の **インターネット公開系はRoute53**
* 基幹系・閉域系・オンプレ連携は **BIND**
* AWS移行途中でも **DNS設計を変えずに段階移行**

---

