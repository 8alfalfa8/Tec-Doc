<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. 全体アーキテクチャ設計（ECS on EC2）](#1-全体アーキテクチャ設計ecs-on-ec2)
  - [1.1 論理構成図](#11-論理構成図)
  - [1.2 ECS on EC2 を選ぶ前提（整理）](#12-ecs-on-ec2-を選ぶ前提整理)
- [2. AWS インフラ設計（詳細）](#2-aws-インフラ設計詳細)
  - [2.1 VPC / ネットワーク設計](#21-vpc-ネットワーク設計)
    - [VPC](#vpc)
    - [Subnet設計](#subnet設計)
    - [ポイント](#ポイント)
  - [2.2 セキュリティ設計](#22-セキュリティ設計)
    - [Security Group](#security-group)
- [3. IAM 設計（ECS on EC2 の肝）](#3-iam-設計ecs-on-ec2-の肝)
  - [3.1 ECS 用 IAM ロール](#31-ecs-用-iam-ロール)
    - [① ECS Instance Role（EC2用）](#①-ecs-instance-roleec2用)
    - [② ECS Task Execution Role](#②-ecs-task-execution-role)
    - [③ ECS Task Role](#③-ecs-task-role)
- [4. ECR 設計](#4-ecr-設計)
  - [4.1 ECR リポジトリ](#41-ecr-リポジトリ)
    - [タグ戦略（推奨）](#タグ戦略推奨)
- [5. ECS（EC2）設計（超重要）](#5-ecsec2設計超重要)
  - [5.1 ECS Cluster](#51-ecs-cluster)
  - [5.2 EC2（Auto Scaling Group）設計](#52-ec2auto-scaling-group設計)
    - [インスタンス設計例](#インスタンス設計例)
    - [ASG 設定](#asg-設定)
  - [5.3 ECS Task Definition（EC2用）](#53-ecs-task-definitionec2用)
    - [リソース指定（Fargateとの違い）](#リソース指定fargateとの違い)
    - [コンテナ定義（例）](#コンテナ定義例)
  - [5.4 ECS Service](#54-ecs-service)
- [6. ALB 設計](#6-alb-設計)
  - [6.1 ALB 設定](#61-alb-設定)
    - [推奨](#推奨)
- [7. CI/CD 設計（ECS on EC2）](#7-cicd-設計ecs-on-ec2)
  - [7.1 CI/CD 全体像](#71-cicd-全体像)
  - [7.2 CIツール選定](#72-ciツール選定)
- [8. CI 構築手順（GitHub Actions 例）](#8-ci-構築手順github-actions-例)
  - [8.1 CI用 IAM](#81-ci用-iam)
    - [権限](#権限)
  - [8.2 GitHub Actions Workflow（概要）](#82-github-actions-workflow概要)
- [9. CD（Blue/Green）構成（推奨）](#9-cdbluegreen構成推奨)
    - [メリット](#メリット)
- [10. 監視・ログ設計](#10-監視ログ設計)
  - [10.1 ログ](#101-ログ)
  - [10.2 メトリクス](#102-メトリクス)
- [11. ECS on EC2 特有の設計ポイント（重要）](#11-ecs-on-ec2-特有の設計ポイント重要)
<!-- TOC_END -->

# ◆ ECR＋ECS（EC2 起動タイプ）を前提とした AWS インフラ設計例

以下では **ECR＋ECS（EC2 起動タイプ）を前提とした AWS インフラ設計例**と、
**実務でそのまま構築・レビューできるレベルの詳細手順（CI/CD 含む）**を、

* 全体アーキテクチャ設計
* インフラ詳細設計（NW / EC2 / ECS / IAM）
* ECS（EC2）特有の設計ポイント
* CI/CD 設計と構築手順
* 運用・拡張・失敗しやすい点

という流れで **体系的に解説**します。

---

## 1. 全体アーキテクチャ設計（ECS on EC2）
[🔙 目次に戻る](#index)


### 1.1 論理構成図
[🔙 目次に戻る](#index)


```
[ Developer ]
     |
     | Git Push
     v
[ GitHub / CodeCommit ]
     |
     v
[ CI (GitHub Actions / CodeBuild) ]
     |
     | docker build & push
     v
[ Amazon ECR ]
     |
     v
[ ECS Service ]
     |
     v
[ ECS Cluster (EC2) ]
     |
     v
[ EC2 Instances ]
     |
     v
[ ALB ]
     |
     v
[ Client ]
```

---

[🔙 目次に戻る](#index)


### 1.2 ECS on EC2 を選ぶ前提（整理）
[🔙 目次に戻る](#index)


| 観点     | 理由                   |
| ------ | -------------------- |
| 高負荷    | JVM Heap 大 / 高同時接続   |
| チューニング | ulimit / kernel / GC |
| コスト    | 常時稼働（RI / SP）        |
| 制限回避   | Fargate制約回避          |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 2. AWS インフラ設計（詳細）
[🔙 目次に戻る](#index)


---

### 2.1 VPC / ネットワーク設計
[🔙 目次に戻る](#index)


#### VPC
[🔙 目次に戻る](#index)


| 項目   | 値           |
| ---- | ----------- |
| CIDR | 10.0.0.0/16 |

[🔙 目次に戻る](#index)


#### Subnet設計
[🔙 目次に戻る](#index)


| 種別      | AZ              | CIDR         | 用途      |
| ------- | --------------- | ------------ | ------- |
| Public  | ap-northeast-1a | 10.0.1.0/24  | ALB     |
| Public  | ap-northeast-1c | 10.0.2.0/24  | ALB     |
| Private | 1a              | 10.0.11.0/24 | ECS EC2 |
| Private | 1c              | 10.0.12.0/24 | ECS EC2 |

[🔙 目次に戻る](#index)


#### ポイント
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* **EC2 は Private Subnet**
* NAT Gateway 経由で ECR / S3 / 外部通信
* AZ 分散必須

---

[🔙 目次に戻る](#index)


### 2.2 セキュリティ設計
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



#### Security Group
[🔙 目次に戻る](#index)


| 対象       | Inbound         | Outbound |
| -------- | --------------- | -------- |
| ALB      | 443 (0.0.0.0/0) | All      |
| ECS EC2  | ALB SG          | All      |
| ECS Task | EC2 SG          | All      |

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 3. IAM 設計（ECS on EC2 の肝）
[🔙 目次に戻る](#index)


---

### 3.1 ECS 用 IAM ロール
[🔙 目次に戻る](#index)


#### ① ECS Instance Role（EC2用）
[🔙 目次に戻る](#index)


* AmazonEC2ContainerServiceforEC2Role
* ECR Pull
* CloudWatch Logs

👉 **EC2起動時に必須**

---

[🔙 目次に戻る](#index)


#### ② ECS Task Execution Role
[🔙 目次に戻る](#index)


* ECR Pull
* CloudWatch Logs

---

[🔙 目次に戻る](#index)


#### ③ ECS Task Role
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)



* Secrets Manager
* S3 / DynamoDB / RDS などアプリ権限

---

[🔙 目次に戻る](#index)


## 4. ECR 設計
[🔙 目次に戻る](#index)


---

### 4.1 ECR リポジトリ
[🔙 目次に戻る](#index)


| 項目         | 設定           |
| ---------- | ------------ |
| Repository | myapp-tomcat |
| Image Scan | ON           |
| Lifecycle  | 30世代         |

#### タグ戦略（推奨）
[🔙 目次に戻る](#index)


* `git-sha`
* `release-yyyymmdd`

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 5. ECS（EC2）設計（超重要）
[🔙 目次に戻る](#index)


---

### 5.1 ECS Cluster
[🔙 目次に戻る](#index)


| 項目                | 内容                |
| ----------------- | ----------------- |
| Cluster Name      | myapp-ec2-cluster |
| Capacity Provider | ASG               |

---

[🔙 目次に戻る](#index)


### 5.2 EC2（Auto Scaling Group）設計
[🔙 目次に戻る](#index)


#### インスタンス設計例
[🔙 目次に戻る](#index)


| 項目            | 値                 |
| ------------- | ----------------- |
| Instance Type | m6i.large         |
| vCPU          | 2                 |
| Memory        | 8GB               |
| AMI           | ECS Optimized AMI |
| Root Volume   | 50GB              |

[🔙 目次に戻る](#index)


#### ASG 設定
[🔙 目次に戻る](#index)


| 項目      | 値 |
| ------- | - |
| Min     | 2 |
| Desired | 2 |
| Max     | 6 |

👉 **Capacity Provider と連携**

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 5.3 ECS Task Definition（EC2用）
[🔙 目次に戻る](#index)


#### リソース指定（Fargateとの違い）
[🔙 目次に戻る](#index)


| 項目     | 設定   |
| ------ | ---- |
| CPU    | 1024 |
| Memory | 4096 |

※ EC2全体のリソース内で**柔軟に割当**

---

[🔙 目次に戻る](#index)


#### コンテナ定義（例）
[🔙 目次に戻る](#index)


| 項目      | 値           |
| ------- | ----------- |
| Image   | ECR URI     |
| Port    | 8080        |
| Log     | awslogs     |
| Env     | APP_ENV     |
| Secrets | DB_PASSWORD |

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 5.4 ECS Service
[🔙 目次に戻る](#index)


| 項目            | 設定          |
| ------------- | ----------- |
| Desired       | 2           |
| Deployment    | Rolling     |
| Placement     | Spread (AZ) |
| Load Balancer | ALB         |

---

[🔙 目次に戻る](#index)


## 6. ALB 設計
[🔙 目次に戻る](#index)


---

### 6.1 ALB 設定
[🔙 目次に戻る](#index)


| 項目          | 値               |
| ----------- | --------------- |
| Scheme      | internet-facing |
| Listener    | 443             |
| Target Type | instance        |
| HealthCheck | /health         |

#### 推奨
[🔙 目次に戻る](#index)


* Idle Timeout：60s
* HTTP/2：ON

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 7. CI/CD 設計（ECS on EC2）
[🔙 目次に戻る](#index)


---

### 7.1 CI/CD 全体像
[🔙 目次に戻る](#index)


```
Git Push
 ↓
CI
  - mvn test
  - docker build
  - docker push (ECR)
 ↓
CD
  - Register Task Definition
  - Update ECS Service
```

---

[🔙 目次に戻る](#index)


### 7.2 CIツール選定
[🔙 目次に戻る](#index)


| ツール            | 理由           |
| -------------- | ------------ |
| GitHub Actions | シンプル         |
| CodePipeline   | Blue/Green対応 |
| Jenkins        | 高自由度         |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 8. CI 構築手順（GitHub Actions 例）
[🔙 目次に戻る](#index)


---

### 8.1 CI用 IAM
[🔙 目次に戻る](#index)


#### 権限
[🔙 目次に戻る](#index)


* ecr:PutImage
* ecs:RegisterTaskDefinition
* ecs:UpdateService

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 8.2 GitHub Actions Workflow（概要）
[🔙 目次に戻る](#index)


```yaml
name: ecs-ec2-deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::xxx:role/github-ci-role
          aws-region: ap-northeast-1

      - uses: aws-actions/amazon-ecr-login@v2

      - name: Build & Push
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker tag myapp:${{ github.sha }} $ECR_URI:${{ github.sha }}
          docker push $ECR_URI:${{ github.sha }}

      - name: Deploy
        run: |
          aws ecs update-service \
            --cluster myapp-ec2-cluster \

[🔙 目次に戻る](#index)

            --service myapp-service \
            --force-new-deployment
```

---

[🔙 目次に戻る](#index)


## 9. CD（Blue/Green）構成（推奨）
[🔙 目次に戻る](#index)


```
CodePipeline
 ├─ Source
 ├─ Build
 ├─ Deploy (ECS Blue/Green)
 └─ Approval
```

#### メリット
[🔙 目次に戻る](#index)


* 即ロールバック
* 無停止デプロイ
* 本番向け

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 10. 監視・ログ設計
[🔙 目次に戻る](#index)


---

### 10.1 ログ
[🔙 目次に戻る](#index)


| 種別        | 保存先             |
| --------- | --------------- |
| アプリ       | CloudWatch Logs |
| ECS Agent | CloudWatch      |
| ALB       | S3              |

---

[🔙 目次に戻る](#index)


### 10.2 メトリクス
[🔙 目次に戻る](#index)


* ECS CPU / Memory
* EC2 CPU / Disk
* ALB TargetResponseTime

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 11. ECS on EC2 特有の設計ポイント（重要）
[🔙 目次に戻る](#index)


✔ EC2 台数 × Task 配置計算<br>
✔ CPU / Memory オーバーコミット可<br>
✔ AMI 更新運用必須<br>
✔ EC2 障害時の Task 再配置

---

# 12. よくある失敗

❌ ECS Instance Role 未設定<br>
❌ ASG と Service スケール非連動<br>
❌ latest タグ運用<br>
❌ EC2 ディスク枯渇<br>
❌ ALB TargetType 間違い<br>

---

# 13. まとめ（設計判断）

| 観点      | ECS EC2 |
| ------- | ------- |
| 大規模Java | ◎       |
| 高同時接続   | ◎       |
| チューニング  | ◎       |
| 運用負荷    | △       |

---

[🔙 目次に戻る](#index)

