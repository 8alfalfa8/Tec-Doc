# ◆ ECS・EKS 移行アーキテクチャ比較(Tomcat)

以下では、**オンプレミス Tomcat（WAR）を AWS へ移行**する前提で、
**ECS（Fargate）** と **EKS（Kubernetes）** の
**移行設計・作業タスク・差分・判断ポイント**を **比較形式**で詳しく整理します。

> 🎯 ゴール
>
> * 「**どこが同じで、どこが違うか**」
> * 「**どちらを選ぶと何が楽／大変か**」
>   を **設計レベルで判断可能**にすること

---

## 1. 全体移行アーキテクチャ比較

### 1.1 共通部分（ECS / EKS 共通）

```
[ Git / CI ]
     ↓
[ Docker Build ]
     ↓
[ ECR ]
     ↓
[ ALB + WAF ]
     ↓
[ ECS Service ] or [ EKS Ingress ]
     ↓
[ Tomcat Container ]
```

共通作業：

* WAR → Docker化
* 外部設定化（環境変数 / Secrets）
* ALB / WAF / TLS
* CloudWatch Logs

---

### 1.2 ECS（Fargate）版

```
Internet
  ↓
WAF
  ↓
ALB
  ↓
ECS Service
  ↓
Fargate Task (Tomcat)
```

---

### 1.3 EKS 版

```
Internet
  ↓
WAF
  ↓
ALB
  ↓
Ingress Controller
  ↓
Service
  ↓
Pod (Tomcat)
```

---

## 2. WAR → コンテナ化（共通）

### 2.1 Dockerfile 例（共通）

```dockerfile
FROM tomcat:9.0-jdk17
COPY app.war /usr/local/tomcat/webapps/app.war
```

#### 設計ポイント

| 項目  | 方針              |
| --- | --------------- |
| 設定  | 環境変数化           |
| ログ  | stdout / stderr |
| 永続化 | S3 / RDS        |

---

## 3. ECS（Fargate）移行設計

### 3.1 作業タスク一覧

| フェーズ | タスク              |
| ---- | ---------------- |
| 準備   | Docker化          |
| 構築   | ECS Cluster      |
| 構成   | Task Definition  |
| 接続   | ALB Target Group |
| 運用   | AutoScaling      |

---

### 3.2 Task Definition 設計

| 項目      | 設計              |
| ------- | --------------- |
| CPU     | 0.5 vCPU        |
| Memory  | 1GB             |
| Port    | 8080            |
| IAM     | Task Role       |
| Secrets | Secrets Manager |

---

### 3.3 メリット・デメリット（ECS）

#### 👍 メリット

* 移行が早い
* 運用が楽
* Kubernetes知識不要

#### 👎 デメリット

* NetworkPolicy不可
* 高度な制御不可

---

## 4. EKS 移行設計

### 4.1 作業タスク一覧

| フェーズ | タスク                  |
| ---- | -------------------- |
| 準備   | Docker化              |
| 構築   | EKS Cluster          |
| 構成   | Deployment / Service |
| 接続   | Ingress              |
| 運用   | HPA / GitOps         |

---

### 4.2 Deployment 設計

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: tomcat
        image: <ECR>
        ports:
        - containerPort: 8080
```

---

### 4.3 Ingress 設計（ALB）

```yaml
alb.ingress.kubernetes.io/scheme: internet-facing
alb.ingress.kubernetes.io/target-type: ip
```

---

### 4.4 メリット・デメリット（EKS）

#### 👍 メリット

* NetworkPolicy
* mTLS / Service Mesh
* マルチクラウド可

#### 👎 デメリット

* 構築・運用が重い
* 学習コスト高

---

## 5. 移行時の設計差分まとめ（重要）

| 観点     | ECS             | EKS               |
| ------ | --------------- | ----------------- |
| 定義     | Task Definition | YAML              |
| スケール   | Service AS      | HPA               |
| ネットワーク | SG              | **NetworkPolicy** |
| IAM    | Task Role       | IRSA              |
| 設定変更   | 再デプロイ           | 再Apply            |

---

## 6. 移行判断マトリクス（実務）

| 条件      | 推奨        |
| ------- | --------- |
| 短期移行    | ECS       |
| レガシーWAR | ECS       |
| API大量   | EKS       |
| 内部通信制御  | EKS       |
| 金融厳格    | **EKS推奨** |

---

## 7. 金融・公共向け結論

| フェーズ | 選択  |
| ---- | --- |
| 初期移行 | ECS |
| 安定後  | EKS |
| 高度化  | EKS |

👉 **段階移行（ECS → EKS）も現実解**

---
