<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. 全体移行アーキテクチャ比較](#1-全体移行アーキテクチャ比較)
  - [1.1 共通部分（ECS / EKS 共通）](#11-共通部分ecs-eks-共通)
  - [1.2 ECS（Fargate）版](#12-ecsfargate版)
  - [1.3 EKS 版](#13-eks-版)
- [2. WAR → コンテナ化（共通）](#2-war-コンテナ化共通)
  - [2.1 Dockerfile 例（共通）](#21-dockerfile-例共通)
    - [設計ポイント](#設計ポイント)
- [3. ECS（Fargate）移行設計](#3-ecsfargate移行設計)
  - [3.1 作業タスク一覧](#31-作業タスク一覧)
  - [3.2 Task Definition 設計](#32-task-definition-設計)
  - [3.3 メリット・デメリット（ECS）](#33-メリットデメリットecs)
    - [👍 メリット](#メリット)
    - [👎 デメリット](#デメリット)
- [4. EKS 移行設計](#4-eks-移行設計)
  - [4.1 作業タスク一覧](#41-作業タスク一覧)
  - [4.2 Deployment 設計](#42-deployment-設計)
  - [4.3 Ingress 設計（ALB）](#43-ingress-設計alb)
  - [4.4 メリット・デメリット（EKS）](#44-メリットデメリットeks)
    - [👍 メリット](#メリット)
    - [👎 デメリット](#デメリット)
- [5. 移行時の設計差分まとめ（重要）](#5-移行時の設計差分まとめ重要)
- [6. 移行判断マトリクス（実務）](#6-移行判断マトリクス実務)
- [7. 金融・公共向け結論](#7-金融公共向け結論)
<!-- TOC_END -->

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
[🔙 目次に戻る](#index)


### 1.1 共通部分（ECS / EKS 共通）
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


### 1.2 ECS（Fargate）版
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


### 1.3 EKS 版
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)

  ↓
Pod (Tomcat)
```

---

[🔙 目次に戻る](#index)


## 2. WAR → コンテナ化（共通）
[🔙 目次に戻る](#index)


### 2.1 Dockerfile 例（共通）
[🔙 目次に戻る](#index)


```dockerfile
FROM tomcat:9.0-jdk17
COPY app.war /usr/local/tomcat/webapps/app.war
```

#### 設計ポイント
[🔙 目次に戻る](#index)


| 項目  | 方針              |
| --- | --------------- |
| 設定  | 環境変数化           |
| ログ  | stdout / stderr |
| 永続化 | S3 / RDS        |

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 3. ECS（Fargate）移行設計
[🔙 目次に戻る](#index)


### 3.1 作業タスク一覧
[🔙 目次に戻る](#index)


| フェーズ | タスク              |
| ---- | ---------------- |
| 準備   | Docker化          |
| 構築   | ECS Cluster      |
| 構成   | Task Definition  |
| 接続   | ALB Target Group |
| 運用   | AutoScaling      |

---

[🔙 目次に戻る](#index)


### 3.2 Task Definition 設計
[🔙 目次に戻る](#index)


| 項目      | 設計              |
| ------- | --------------- |
| CPU     | 0.5 vCPU        |
| Memory  | 1GB             |
| Port    | 8080            |
| IAM     | Task Role       |
| Secrets | Secrets Manager |

---

[🔙 目次に戻る](#index)


### 3.3 メリット・デメリット（ECS）
[🔙 目次に戻る](#index)


#### 👍 メリット
[🔙 目次に戻る](#index)


* 移行が早い
* 運用が楽
* Kubernetes知識不要

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



#### 👎 デメリット
[🔙 目次に戻る](#index)


* NetworkPolicy不可
* 高度な制御不可

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 4. EKS 移行設計
[🔙 目次に戻る](#index)


### 4.1 作業タスク一覧
[🔙 目次に戻る](#index)


| フェーズ | タスク                  |
| ---- | -------------------- |
| 準備   | Docker化              |
| 構築   | EKS Cluster          |
| 構成   | Deployment / Service |
| 接続   | Ingress              |
| 運用   | HPA / GitOps         |

---

[🔙 目次に戻る](#index)


### 4.2 Deployment 設計
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


### 4.3 Ingress 設計（ALB）
[🔙 目次に戻る](#index)


```yaml
alb.ingress.kubernetes.io/scheme: internet-facing
alb.ingress.kubernetes.io/target-type: ip
```

---

[🔙 目次に戻る](#index)


### 4.4 メリット・デメリット（EKS）
[🔙 目次に戻る](#index)


#### 👍 メリット
[🔙 目次に戻る](#index)


* NetworkPolicy
* mTLS / Service Mesh
* マルチクラウド可

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


#### 👎 デメリット
[🔙 目次に戻る](#index)


* 構築・運用が重い
* 学習コスト高

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 5. 移行時の設計差分まとめ（重要）
[🔙 目次に戻る](#index)


| 観点     | ECS             | EKS               |
| ------ | --------------- | ----------------- |
| 定義     | Task Definition | YAML              |
| スケール   | Service AS      | HPA               |
| ネットワーク | SG              | **NetworkPolicy** |
| IAM    | Task Role       | IRSA              |
| 設定変更   | 再デプロイ           | 再Apply            |

---

[🔙 目次に戻る](#index)


## 6. 移行判断マトリクス（実務）
[🔙 目次に戻る](#index)


| 条件      | 推奨        |
| ------- | --------- |
| 短期移行    | ECS       |
| レガシーWAR | ECS       |
| API大量   | EKS       |
| 内部通信制御  | EKS       |
| 金融厳格    | **EKS推奨** |

---

[🔙 目次に戻る](#index)


## 7. 金融・公共向け結論
[🔙 目次に戻る](#index)


| フェーズ | 選択  |
| ---- | --- |
| 初期移行 | ECS |
| 安定後  | EKS |
| 高度化  | EKS |

👉 **段階移行（ECS → EKS）も現実解**

---

[🔙 目次に戻る](#index)

