<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. 目的・背景](#1-目的背景)
- [2. 全体アーキテクチャ概要（論理図）](#2-全体アーキテクチャ概要論理図)
- [3. 採用方針と責務分離](#3-採用方針と責務分離)
  - [3.1 基本方針](#31-基本方針)
  - [3.2 責務分離表](#32-責務分離表)
- [4. ネットワーク詳細設計](#4-ネットワーク詳細設計)
  - [4.1 VPC / Subnet 構成](#41-vpc-subnet-構成)
  - [4.2 通信制御方針](#42-通信制御方針)
- [5. ALB / WAF / ルーティング設計](#5-alb-waf-ルーティング設計)
  - [5.1 パスルーティング](#51-パスルーティング)
  - [5.2 WAF WebACL 分離](#52-waf-webacl-分離)
- [6. ECS 詳細設計](#6-ecs-詳細設計)
  - [6.1 ECS クラスタ](#61-ecs-クラスタ)
  - [6.2 Task Definition](#62-task-definition)
- [7. EKS 詳細設計](#7-eks-詳細設計)
  - [7.1 クラスタ構成](#71-クラスタ構成)
  - [7.2 Namespace 設計](#72-namespace-設計)
  - [7.3 Ingress](#73-ingress)
- [8. CI/CD 設計](#8-cicd-設計)
- [9. セキュリティ・監査設計](#9-セキュリティ監査設計)
  - [9.1 IAM](#91-iam)
  - [9.2 ログ](#92-ログ)
- [10. 運用・段階移行ロードマップ](#10-運用段階移行ロードマップ)
- [11. まとめ（設計結論）](#11-まとめ設計結論)
  - [この設計書でカバーしている範囲](#この設計書でカバーしている範囲)
<!-- TOC_END -->

# ECS + EKS ハイブリッド詳細設計書（金融・公共向け）

## 1. 目的・背景
[🔙 目次に戻る](#index)


本設計書は、オンプレミスの Tomcat（WAR）資産を AWS へ移行するにあたり、**ECS（Fargate）と EKS（Kubernetes）を併用するハイブリッド構成**を採用し、

* 既存資産の安定移行
* 新規機能・API の拡張性確保
* 金融・公共向けの厳格なセキュリティ／監査要件
  を同時に満たすことを目的とする。

---

[🔙 目次に戻る](#index)


## 2. 全体アーキテクチャ概要（論理図）
[🔙 目次に戻る](#index)


```
[ Internet ]
     |
 [ AWS Shield ]
     |
 [ AWS WAF ]
     |
 [ ALB (Public) ]
     |
     +----------------------+----------------------+
     |                                             |
[ ECS Service ]                               [ EKS Ingress ]
[ Fargate ]                                  [ ALB Controller ]
[ Tomcat WAR ]                               [ Service / Pod ]
     |                                             |
     +----------------------+----------------------+
                            |
                      [ RDS / S3 ]
```

---

[🔙 目次に戻る](#index)


## 3. 採用方針と責務分離
[🔙 目次に戻る](#index)


### 3.1 基本方針
[🔙 目次に戻る](#index)


* **ECS**：既存 Tomcat（WAR）アプリの安定稼働基盤
* **EKS**：新規 API／将来拡張／高度な通信制御が必要な領域

[🔙 目次に戻る](#index)


### 3.2 責務分離表
[🔙 目次に戻る](#index)


| 領域            | ECS（Fargate） | EKS |
| ------------- | ------------ | --- |
| 既存WAR         | ◎            | △   |
| 新規API         | ×            | ◎   |
| NetworkPolicy | ×            | ◎   |
| 運用負荷          | 低            | 高   |
| 拡張性           | 中            | 高   |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 4. ネットワーク詳細設計
[🔙 目次に戻る](#index)


### 4.1 VPC / Subnet 構成
[🔙 目次に戻る](#index)


```
VPC (10.0.0.0/16)
 ├─ Public Subnet
 │    └─ ALB
 ├─ Private Subnet A
 │    ├─ ECS Fargate
 │    └─ EKS Node
 └─ Isolated Subnet
      └─ RDS
```

[🔙 目次に戻る](#index)


### 4.2 通信制御方針
[🔙 目次に戻る](#index)


| 通信経路           | 制御方式            |
| -------------- | --------------- |
| Internet → ALB | WAF + SG        |
| ALB → ECS      | SG              |
| ALB → EKS      | SG              |
| ECS → EKS      | Private IP + SG |
| EKS 内部         | NetworkPolicy   |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 5. ALB / WAF / ルーティング設計
[🔙 目次に戻る](#index)


### 5.1 パスルーティング
[🔙 目次に戻る](#index)


| パス       | 転送先         |
| -------- | ----------- |
| /app/*   | ECS（Tomcat） |
| /api/*   | EKS（API）    |
| /admin/* | ECS（社内IP制限） |

[🔙 目次に戻る](#index)


### 5.2 WAF WebACL 分離
[🔙 目次に戻る](#index)


| 対象       | WebACL               |
| -------- | -------------------- |
| Web（ECS） | 標準 + XSS/SQLi        |
| API（EKS） | API厳格（Method/Schema） |
| 管理       | Geo/IP/Rate超厳格       |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 6. ECS 詳細設計
[🔙 目次に戻る](#index)


### 6.1 ECS クラスタ
[🔙 目次に戻る](#index)


* 起動タイプ：Fargate
* 配置：Private Subnet

[🔙 目次に戻る](#index)


### 6.2 Task Definition
[🔙 目次に戻る](#index)


| 項目      | 設定例             |
| ------- | --------------- |
| CPU     | 0.5 vCPU        |
| Memory  | 1GB             |
| Port    | 8080            |
| IAM     | Task Role       |
| Secrets | Secrets Manager |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 7. EKS 詳細設計
[🔙 目次に戻る](#index)


### 7.1 クラスタ構成
[🔙 目次に戻る](#index)


* マネージドノード
* Private Endpoint

[🔙 目次に戻る](#index)


### 7.2 Namespace 設計
[🔙 目次に戻る](#index)


| Namespace | 用途    |
| --------- | ----- |
| system    | Core  |
| api       | 外部API |
| internal  | 内部API |

[🔙 目次に戻る](#index)


### 7.3 Ingress
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* AWS Load Balancer Controller
* ALB target-type: ip

---

[🔙 目次に戻る](#index)


## 8. CI/CD 設計
[🔙 目次に戻る](#index)


| 項目       | ECS        | EKS        |
| -------- | ---------- | ---------- |
| Build    | CodeBuild  | CodeBuild  |
| Deploy   | CodeDeploy | ArgoCD     |
| Rollback | Service更新  | Git Revert |

---

[🔙 目次に戻る](#index)


## 9. セキュリティ・監査設計
[🔙 目次に戻る](#index)


### 9.1 IAM
[🔙 目次に戻る](#index)


* ECS Task Role / EKS IRSA 分離
* 人的IAM禁止（SSO）

[🔙 目次に戻る](#index)


### 9.2 ログ
[🔙 目次に戻る](#index)


| 種別      | 出力先                    |
| ------- | ---------------------- |
| ALB/WAF | S3（ObjectLock）         |
| ECS     | CloudWatch Logs        |
| EKS     | CloudWatch + Audit Log |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 10. 運用・段階移行ロードマップ
[🔙 目次に戻る](#index)


```
Phase1: ECSのみ
Phase2: EKS併設（API）
Phase3: ECS縮退 or 維持
```

---

[🔙 目次に戻る](#index)


## 11. まとめ（設計結論）
[🔙 目次に戻る](#index)


* **短期安定：ECS**
* **中長期拡張：EKS**
* **両立解：ハイブリッド**

本構成は、金融・公共監査においても「合理的な技術選択」として説明可能である。

---

### この設計書でカバーしている範囲
[🔙 目次に戻る](#index)


* 全体アーキテクチャ（論理図）
* ECS と EKS の**責務分離の明確化**
* VPC／Subnet／通信経路の詳細設計
* ALB・WAF・パスルーティング設計
* ECS / EKS それぞれの詳細設計
* CI/CD 分離設計
* 金融・公共向けセキュリティ／監査観点
* 段階移行ロードマップ

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)

