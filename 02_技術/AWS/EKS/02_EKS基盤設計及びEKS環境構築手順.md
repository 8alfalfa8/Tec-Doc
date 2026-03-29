<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. AWS / EKS 基盤設計（設計編）](#1-aws-eks-基盤設計設計編)
  - [1.1 設計全体像（論理構成）](#11-設計全体像論理構成)
  - [1.2 VPC設計](#12-vpc設計)
    - [設計方針](#設計方針)
    - [サブネット設計例](#サブネット設計例)
    - [理由](#理由)
  - [1.3 EKSクラスター設計](#13-eksクラスター設計)
    - [クラスター](#クラスター)
    - [理由](#理由)
  - [1.4 Node設計（Worker Node）](#14-node設計worker-node)
    - [NodeGroup設計](#nodegroup設計)
    - [Podリソース設計](#podリソース設計)
  - [1.5 IAM / セキュリティ設計](#15-iam-セキュリティ設計)
    - [IAM設計](#iam設計)
    - [IRSA（重要）](#irsa重要)
  - [1.6 ネットワーク / 通信設計](#16-ネットワーク-通信設計)
  - [1.7 ログ・監視設計](#17-ログ監視設計)
    - [ログ](#ログ)
    - [監視](#監視)
  - [1.8 可用性・スケーリング設計](#18-可用性スケーリング設計)
  - [1.9 セキュリティ設計（要点）](#19-セキュリティ設計要点)
- [2. EKS環境構築手順（作業編）](#2-eks環境構築手順作業編)
  - [2.1 事前準備](#21-事前準備)
    - [必要情報](#必要情報)
    - [ツール](#ツール)
  - [2.2 VPC作成](#22-vpc作成)
    - [成果物](#成果物)
  - [2.3 EKSクラスター作成](#23-eksクラスター作成)
    - [確認](#確認)
  - [2.4 Managed Node Group作成](#24-managed-node-group作成)
  - [2.5 kubectl 接続設定](#25-kubectl-接続設定)
  - [2.6 IAM OIDC / IRSA設定](#26-iam-oidc-irsa設定)
    - [Pod用IAM Role作成](#pod用iam-role作成)
  - [2.7 Add-on導入](#27-add-on導入)
    - [Metrics Server](#metrics-server)
    - [AWS Load Balancer Controller](#aws-load-balancer-controller)
  - [2.8 ログ設定](#28-ログ設定)
    - [CloudWatch Agent](#cloudwatch-agent)
  - [2.9 Namespace作成](#29-namespace作成)
  - [2.10 動作確認](#210-動作確認)
- [3. 成果物一覧（EKS基盤）](#3-成果物一覧eks基盤)
- [4. よくある失敗と回避策](#4-よくある失敗と回避策)
<!-- TOC_END -->

# ◆ EKS基盤設計 & EKS環境構築手順

以下では、**エンタープライズ向け／実運用前提**で
**AWS/EKS基盤設計（設計観点・設計内容・判断理由）**と
**EKS環境構築手順（実作業レベル）**を体系的に詳説します。

※ Tomcat WAR 移行・ALB Ingress 前提で記載します。

---

## 1. AWS / EKS 基盤設計（設計編）
[🔙 目次に戻る](#index)


---

### 1.1 設計全体像（論理構成）
[🔙 目次に戻る](#index)


```
Internet
  ↓
ALB（Ingress）
  ↓
EKS Cluster
  ├─ NodeGroup-A（AZ-a）
  ├─ NodeGroup-B（AZ-c）
  │
  ├─ Namespace: prod
  │   └─ Tomcat Pod
  └─ Namespace: ops
      └─ Monitoring / Logging
```

---

[🔙 目次に戻る](#index)


### 1.2 VPC設計
[🔙 目次に戻る](#index)


#### 設計方針
[🔙 目次に戻る](#index)


| 項目 | 方針            |
| -- | ------------- |
| 分離 | パブリック／プライベート  |
| 冗長 | 2AZ以上         |
| 通信 | PodはPrivateのみ |

[🔙 目次に戻る](#index)


#### サブネット設計例
[🔙 目次に戻る](#index)


| 種別      | AZ-a         | AZ-c         | 用途        |
| ------- | ------------ | ------------ | --------- |
| Public  | 10.0.1.0/24  | 10.0.2.0/24  | ALB / NAT |
| Private | 10.0.11.0/24 | 10.0.12.0/24 | EKS Node  |

[🔙 目次に戻る](#index)


#### 理由
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* セキュリティ（Node非公開）
* EKSベストプラクティス準拠

---

[🔙 目次に戻る](#index)


### 1.3 EKSクラスター設計
[🔙 目次に戻る](#index)


#### クラスター
[🔙 目次に戻る](#index)


| 項目      | 設計                          |
| ------- | --------------------------- |
| バージョン   | 最新安定版                       |
| エンドポイント | Public + CIDR制限             |
| ログ      | audit / api / authenticator |

[🔙 目次に戻る](#index)


#### 理由
[🔙 目次に戻る](#index)


* kubectl操作性
* 監査対応

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 1.4 Node設計（Worker Node）
[🔙 目次に戻る](#index)


#### NodeGroup設計
[🔙 目次に戻る](#index)


| 項目      | 内容                 |
| ------- | ------------------ |
| 種別      | Managed Node Group |
| OS      | Amazon Linux 2     |
| インスタンス  | m6i.large          |
| AZ分散    | 2AZ                |
| Scaling | AutoScaling        |

[🔙 目次に戻る](#index)


#### Podリソース設計
[🔙 目次に戻る](#index)


| 項目     | 値          |
| ------ | ---------- |
| CPU    | 500m〜1core |
| Memory | 1Gi〜2Gi    |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 1.5 IAM / セキュリティ設計
[🔙 目次に戻る](#index)


#### IAM設計
[🔙 目次に戻る](#index)


| 対象   | 内容       |
| ---- | -------- |
| Node | 最小権限     |
| Pod  | IRSA     |
| 管理者  | IAM Role |

[🔙 目次に戻る](#index)


#### IRSA（重要）
[🔙 目次に戻る](#index)


* PodごとにIAM Role割当
* S3/SecretsManagerアクセス分離

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 1.6 ネットワーク / 通信設計
[🔙 目次に戻る](#index)


| 通信      | 設計          |
| ------- | ----------- |
| Ingress | ALB         |
| 内部      | ClusterIP   |
| 外部API   | NAT Gateway |

---

[🔙 目次に戻る](#index)


### 1.7 ログ・監視設計
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



#### ログ
[🔙 目次に戻る](#index)


| 種別         | 保存先             |
| ---------- | --------------- |
| Pod stdout | CloudWatch Logs |
| ALB        | S3              |

[🔙 目次に戻る](#index)


#### 監視
[🔙 目次に戻る](#index)


| 項目   | ツール              |
| ---- | ---------------- |
| Node | CloudWatch       |
| Pod  | Metrics Server   |
| アラート | CloudWatch Alarm |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 1.8 可用性・スケーリング設計
[🔙 目次に戻る](#index)


| 機能     | 内容                 |
| ------ | ------------------ |
| Pod冗長  | Replica            |
| 自動拡張   | HPA                |
| Node拡張 | Cluster Autoscaler |

---

[🔙 目次に戻る](#index)


### 1.9 セキュリティ設計（要点）
[🔙 目次に戻る](#index)


* Private Node
* SecurityGroup最小化
* NetworkPolicy（必要時）
* SecretsはK8s Secret or Secrets Manager

---

[🔙 目次に戻る](#index)


## 2. EKS環境構築手順（作業編）
[🔙 目次に戻る](#index)


---

### 2.1 事前準備
[🔙 目次に戻る](#index)


#### 必要情報
[🔙 目次に戻る](#index)


* AWSアカウント
* IAM権限（EKS / EC2 / VPC）
* ローカル端末

[🔙 目次に戻る](#index)


#### ツール
[🔙 目次に戻る](#index)


```bash
aws --version
kubectl version
eksctl version
```

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 2.2 VPC作成
[🔙 目次に戻る](#index)


（既存VPCがない場合）

```bash
eksctl create cluster \
  --name dummy \
  --region ap-northeast-1 \
  --vpc-private-subnets=xxx \
  --dry-run
```

※ 実務では **Terraform推奨**

#### 成果物
[🔙 目次に戻る](#index)


* VPC
* Subnet
* NAT Gateway

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 2.3 EKSクラスター作成
[🔙 目次に戻る](#index)


```bash
eksctl create cluster \
  --name prod-eks \
  --region ap-northeast-1 \
  --version 1.29 \
  --vpc-private-subnets subnet-a,subnet-c \
  --with-oidc \
  --managed
```

#### 確認
[🔙 目次に戻る](#index)


```bash
kubectl get nodes
```

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 2.4 Managed Node Group作成
[🔙 目次に戻る](#index)


```bash
eksctl create nodegroup \
  --cluster prod-eks \
  --name app-ng \
  --node-type m6i.large \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 6 \
  --node-private-networking
```

---

[🔙 目次に戻る](#index)


### 2.5 kubectl 接続設定
[🔙 目次に戻る](#index)


```bash
aws eks update-kubeconfig \
  --region ap-northeast-1 \
  --name prod-eks
```

---

[🔙 目次に戻る](#index)


### 2.6 IAM OIDC / IRSA設定
[🔙 目次に戻る](#index)


```bash
eksctl utils associate-iam-oidc-provider \
  --cluster prod-eks \
  --approve
```

#### Pod用IAM Role作成
[🔙 目次に戻る](#index)


* S3 / Secrets権限を付与

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 2.7 Add-on導入
[🔙 目次に戻る](#index)


#### Metrics Server
[🔙 目次に戻る](#index)


```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

[🔙 目次に戻る](#index)


#### AWS Load Balancer Controller
[🔙 目次に戻る](#index)


```bash
helm install aws-load-balancer-controller eks/aws-load-balancer-controller
```

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



---

[🔙 目次に戻る](#index)


### 2.8 ログ設定
[🔙 目次に戻る](#index)


#### CloudWatch Agent
[🔙 目次に戻る](#index)


```bash
kubectl apply -f cwagent.yaml
```

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 2.9 Namespace作成
[🔙 目次に戻る](#index)


```bash
kubectl create namespace prod
kubectl create namespace ops
```

---

[🔙 目次に戻る](#index)


### 2.10 動作確認
[🔙 目次に戻る](#index)


```bash
kubectl get pods -A
kubectl top nodes
kubectl top pods
```

---

[🔙 目次に戻る](#index)


## 3. 成果物一覧（EKS基盤）
[🔙 目次に戻る](#index)


| 種別     | 成果物                  |
| ------ | -------------------- |
| 設計     | AWS/EKS設計書           |
| IaC    | Terraform / eksctl定義 |
| 環境     | EKSクラスター             |
| セキュリティ | IAM/IRSA             |
| 運用     | 監視設定                 |

---

[🔙 目次に戻る](#index)


## 4. よくある失敗と回避策
[🔙 目次に戻る](#index)


| 失敗      | 回避          |
| ------- | ----------- |
| Node不足  | AutoScaling |
| 権限過多    | IRSA        |
| Pod通信不可 | SG/Route    |
| ALB不通   | Subnetタグ    |

---

[🔙 目次に戻る](#index)

