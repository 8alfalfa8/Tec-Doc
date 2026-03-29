# ◆ EKS基盤設計 & EKS環境構築手順

以下では、**エンタープライズ向け／実運用前提**で
**AWS/EKS基盤設計（設計観点・設計内容・判断理由）**と
**EKS環境構築手順（実作業レベル）**を体系的に詳説します。

※ Tomcat WAR 移行・ALB Ingress 前提で記載します。

---

## 1. AWS / EKS 基盤設計（設計編）

---

### 1.1 設計全体像（論理構成）

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

### 1.2 VPC設計

#### 設計方針

| 項目 | 方針            |
| -- | ------------- |
| 分離 | パブリック／プライベート  |
| 冗長 | 2AZ以上         |
| 通信 | PodはPrivateのみ |

#### サブネット設計例

| 種別      | AZ-a         | AZ-c         | 用途        |
| ------- | ------------ | ------------ | --------- |
| Public  | 10.0.1.0/24  | 10.0.2.0/24  | ALB / NAT |
| Private | 10.0.11.0/24 | 10.0.12.0/24 | EKS Node  |

#### 理由

* セキュリティ（Node非公開）
* EKSベストプラクティス準拠

---

### 1.3 EKSクラスター設計

#### クラスター

| 項目      | 設計                          |
| ------- | --------------------------- |
| バージョン   | 最新安定版                       |
| エンドポイント | Public + CIDR制限             |
| ログ      | audit / api / authenticator |

#### 理由

* kubectl操作性
* 監査対応

---

### 1.4 Node設計（Worker Node）

#### NodeGroup設計

| 項目      | 内容                 |
| ------- | ------------------ |
| 種別      | Managed Node Group |
| OS      | Amazon Linux 2     |
| インスタンス  | m6i.large          |
| AZ分散    | 2AZ                |
| Scaling | AutoScaling        |

#### Podリソース設計

| 項目     | 値          |
| ------ | ---------- |
| CPU    | 500m〜1core |
| Memory | 1Gi〜2Gi    |

---

### 1.5 IAM / セキュリティ設計

#### IAM設計

| 対象   | 内容       |
| ---- | -------- |
| Node | 最小権限     |
| Pod  | IRSA     |
| 管理者  | IAM Role |

#### IRSA（重要）

* PodごとにIAM Role割当
* S3/SecretsManagerアクセス分離

---

### 1.6 ネットワーク / 通信設計

| 通信      | 設計          |
| ------- | ----------- |
| Ingress | ALB         |
| 内部      | ClusterIP   |
| 外部API   | NAT Gateway |

---

### 1.7 ログ・監視設計

#### ログ

| 種別         | 保存先             |
| ---------- | --------------- |
| Pod stdout | CloudWatch Logs |
| ALB        | S3              |

#### 監視

| 項目   | ツール              |
| ---- | ---------------- |
| Node | CloudWatch       |
| Pod  | Metrics Server   |
| アラート | CloudWatch Alarm |

---

### 1.8 可用性・スケーリング設計

| 機能     | 内容                 |
| ------ | ------------------ |
| Pod冗長  | Replica            |
| 自動拡張   | HPA                |
| Node拡張 | Cluster Autoscaler |

---

### 1.9 セキュリティ設計（要点）

* Private Node
* SecurityGroup最小化
* NetworkPolicy（必要時）
* SecretsはK8s Secret or Secrets Manager

---

## 2. EKS環境構築手順（作業編）

---

### 2.1 事前準備

#### 必要情報

* AWSアカウント
* IAM権限（EKS / EC2 / VPC）
* ローカル端末

#### ツール

```bash
aws --version
kubectl version
eksctl version
```

---

### 2.2 VPC作成

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

* VPC
* Subnet
* NAT Gateway

---

### 2.3 EKSクラスター作成

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

```bash
kubectl get nodes
```

---

### 2.4 Managed Node Group作成

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

### 2.5 kubectl 接続設定

```bash
aws eks update-kubeconfig \
  --region ap-northeast-1 \
  --name prod-eks
```

---

### 2.6 IAM OIDC / IRSA設定

```bash
eksctl utils associate-iam-oidc-provider \
  --cluster prod-eks \
  --approve
```

#### Pod用IAM Role作成

* S3 / Secrets権限を付与

---

### 2.7 Add-on導入

#### Metrics Server

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

#### AWS Load Balancer Controller

```bash
helm install aws-load-balancer-controller eks/aws-load-balancer-controller
```

---

### 2.8 ログ設定

#### CloudWatch Agent

```bash
kubectl apply -f cwagent.yaml
```

---

### 2.9 Namespace作成

```bash
kubectl create namespace prod
kubectl create namespace ops
```

---

### 2.10 動作確認

```bash
kubectl get pods -A
kubectl top nodes
kubectl top pods
```

---

## 3. 成果物一覧（EKS基盤）

| 種別     | 成果物                  |
| ------ | -------------------- |
| 設計     | AWS/EKS設計書           |
| IaC    | Terraform / eksctl定義 |
| 環境     | EKSクラスター             |
| セキュリティ | IAM/IRSA             |
| 運用     | 監視設定                 |

---

## 4. よくある失敗と回避策

| 失敗      | 回避          |
| ------- | ----------- |
| Node不足  | AutoScaling |
| 権限過多    | IRSA        |
| Pod通信不可 | SG/Route    |
| ALB不通   | Subnetタグ    |

---
