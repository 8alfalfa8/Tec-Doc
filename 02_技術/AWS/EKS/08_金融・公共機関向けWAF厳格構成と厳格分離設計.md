# ◆ 金融・公共機関向けWAF厳格構成と厳格分離設計

以下では、**金融機関・公共機関向け**を前提とした
**①WAF厳格構成** と **②金融／公共向けの厳格分離設計（ネットワーク・EKS・WAF）** を、
**実務・監査・規制（FISC／ISMAP／NISC／PCI DSS相当）に耐えるレベル**で体系的に整理します。

---

## ① 金融・公共向け WAF 厳格構成

### 1. 設計思想（前提）

金融・公共向けでは以下が**必須要件**になります。

| 観点     | 要求             |
| ------ | -------------- |
| ゼロトラスト | 外部からの通信はすべて疑う  |
| 多層防御   | WAF単体に依存しない    |
| 最小権限   | 通信・API・IAMすべて  |
| ルール可視性 | ブラックボックス禁止     |
| 監査証跡   | 7年以上ログ保管（要件次第） |
| 障害分離   | 攻撃＝全体停止を防ぐ     |

---

### 2. 金融・公共向け WAF 構成全体像

```
[ Internet ]
     |
[ AWS Shield Advanced ]
     |
[ AWS WAF (厳格ルール) ]
     |
[ ALB (Internal/External分離) ]
     |
[ ALB Ingress Controller ]
     |
[ Kubernetes Service ]
     |
[ Pod (mTLS / AuthN / AuthZ)]
```

---

### 3. WAF 厳格ルールセット構成

#### 3.1 ルール適用順序（重要）

| 優先度 | ルール群                 |
| --- | -------------------- |
| ①   | Geo/IP制御             |
| ②   | Rate Limit           |
| ③   | APIスキーマ検証            |
| ④   | Managed Rule（OWASP等） |
| ⑤   | カスタム業務ルール            |
| ⑥   | 例外ルール                |

---

#### 3.2 Geo・IP制御（必須）

```text
✔ 日本国内IPのみ許可
✔ 海外IPは原則ブロック
✔ VPN・踏み台国は個別拒否
```

```yaml
GeoMatch:
  Allow: JP
  Block: CN, RU, IR, KP, VN
```

※ **公共系は「海外＝即遮断」が標準**

---

#### 3.3 Rate Limit（金融向け厳格）

| 種別    | 制限               |
| ----- | ---------------- |
| API   | 50 req / 5分 / IP |
| 認証API | 5 req / 分 / IP   |
| 管理API | 1 req / 分        |

```yaml
RateBasedRule:
  Limit: 50
  AggregateKey: IP
```

---

#### 3.4 APIスキーマ厳格検証（最重要）

**API Gateway的思想をWAFに持ち込む**

| 項目          | 制御                |
| ----------- | ----------------- |
| HTTP Method | 明示許可（GET/POSTのみ等） |
| Path        | 完全一致 or 正規表現      |
| Header      | 許可リスト方式           |
| Query       | 定義外は拒否            |
| Body        | JSON Schema準拠     |

```yaml
Allow:
  Path: ^/api/v1/accounts$
  Method: POST
  Headers:
    - Content-Type: application/json
```

👉 **仕様外通信＝即Block**

---

#### 3.5 Managed Rule（カスタマイズ必須）

使用するが **デフォルト禁止**

| ルール     | 対応                   |
| ------- | -------------------- |
| OWASP   | Count → Blockへ昇格     |
| SQLi    | Body/Query/Header別制御 |
| XSS     | Cookie/Header強化      |
| LFI/RFI | 常時Block              |

---

#### 3.6 業務特化ルール（金融特有）

| 例      | 内容          |
| ------ | ----------- |
| 口座番号   | 桁数・形式不一致は拒否 |
| 金額     | 上限超過拒否      |
| 管理系API | 社内IP限定      |
| バッチAPI | 時間帯制御       |

---

### 4. WAF ログ・監査構成（金融必須）

| 項目    | 設計             |
| ----- | -------------- |
| ログ    | Full Request   |
| 保存    | S3 Object Lock |
| 保管期間  | 7〜10年          |
| 改ざん防止 | MFA Delete     |
| 分析    | Athena / SIEM  |

---

## ② 金融／公共向け 厳格分離設計

### 1. 分離設計の基本方針

| 分離対象   | 分離レベル    |
| ------ | -------- |
| 環境     | アカウント分離  |
| ネットワーク | VPC分離    |
| EKS    | クラスタ分離   |
| WAF    | WebACL分離 |
| ALB    | 完全分離     |
| IAM    | ロール完全独立  |

---

### 2. アカウント分離モデル（推奨）

```
AWS Organization
 ├─ security-account
 │    ├─ WAF
 │    ├─ GuardDuty
 │    ├─ SecurityHub
 │
 ├─ prod-account
 │    ├─ EKS (Prod)
 │    ├─ ALB (Prod)
 │
 ├─ staging-account
 │    ├─ EKS (Stg)
 │
 └─ dev-account
```

✔ **監査系は業務アカウントから完全分離**

---

### 3. ネットワーク厳格分離

| 領域       | 設計              |
| -------- | --------------- |
| Internet | Public Subnet   |
| ALB      | DMZ Subnet      |
| EKS Node | Private Subnet  |
| DB       | Isolated Subnet |

```
Internet
  ↓
[WAF]
  ↓
[ALB (DMZ)]
  ↓
[EKS Node (Private)]
  ↓
[DB (No Internet)]
```

---

### 4. EKS 厳格分離設計

#### 4.1 Namespace分離（最低限）

| Namespace | 用途    |
| --------- | ----- |
| system    | Core  |
| api       | 外部API |
| batch     | バッチ   |
| admin     | 管理    |

＋ NetworkPolicy 必須

---

#### 4.2 クラスタ分離（金融推奨）

| クラスタ      | 用途    |
| --------- | ----- |
| eks-api   | 対外API |
| eks-batch | 内部処理  |
| eks-admin | 管理    |

✔ 攻撃影響範囲を物理的に遮断

---

### 5. ALB × WAF 分離設計

| ALB  | WAF           |
| ---- | ------------- |
| API用 | API専用WebACL   |
| 管理用  | 管理専用WebACL    |
| バッチ  | WAFなし or 内部制限 |

---

### 6. IAM・運用分離（監査指摘最多）

| 項目  | 対応                  |
| --- | ------------------- |
| 管理者 | 人的IAM禁止             |
| 作業  | SSO＋Role            |
| IaC | Terraform Role      |
| 本番  | ReadOnly + Change申請 |

---

### 7. 金融・公共向け最終チェックリスト

#### セキュリティ

* [ ] Geo制御JP限定
* [ ] API仕様外通信遮断
* [ ] Rate Limit設定
* [ ] Shield Advanced有効

#### 分離

* [ ] アカウント分離
* [ ] VPC分離
* [ ] クラスタ分離

#### 監査

* [ ] WAFログ長期保管
* [ ] 変更履歴証跡
* [ ] SIEM連携

---
