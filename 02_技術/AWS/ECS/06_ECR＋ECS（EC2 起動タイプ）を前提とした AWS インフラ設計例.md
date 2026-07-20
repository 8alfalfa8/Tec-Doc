# ◆ ECR＋ECS（EC2 起動タイプ）を前提とした AWS インフラ設計例
<!-- PROFILE_BADGE_START -->

[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?logo=github)](https://github.com/8alfalfa8)
[![Qiita](https://img.shields.io/badge/Qiita-Profile-55C500?logo=qiita&logoColor=white)](https://qiita.com/8alfalfa8)
[![Zenn](https://img.shields.io/badge/Zenn-Profile-3EA8FF?logo=zenn&logoColor=white)](https://zenn.dev/8alfalfa8)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/8alfalfa8)

<!-- PROFILE_BADGE_END -->


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

### 1.1 論理構成図

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

### 1.2 ECS on EC2 を選ぶ前提（整理）

| 観点     | 理由                   |
| ------ | -------------------- |
| 高負荷    | JVM Heap 大 / 高同時接続   |
| チューニング | ulimit / kernel / GC |
| コスト    | 常時稼働（RI / SP）        |
| 制限回避   | Fargate制約回避          |

---

## 2. AWS インフラ設計（詳細）

---

### 2.1 VPC / ネットワーク設計

#### VPC

| 項目   | 値           |
| ---- | ----------- |
| CIDR | 10.0.0.0/16 |

#### Subnet設計

| 種別      | AZ              | CIDR         | 用途      |
| ------- | --------------- | ------------ | ------- |
| Public  | ap-northeast-1a | 10.0.1.0/24  | ALB     |
| Public  | ap-northeast-1c | 10.0.2.0/24  | ALB     |
| Private | 1a              | 10.0.11.0/24 | ECS EC2 |
| Private | 1c              | 10.0.12.0/24 | ECS EC2 |

#### ポイント

* **EC2 は Private Subnet**
* NAT Gateway 経由で ECR / S3 / 外部通信
* AZ 分散必須

---

### 2.2 セキュリティ設計

#### Security Group

| 対象       | Inbound         | Outbound |
| -------- | --------------- | -------- |
| ALB      | 443 (0.0.0.0/0) | All      |
| ECS EC2  | ALB SG          | All      |
| ECS Task | EC2 SG          | All      |

---

## 3. IAM 設計（ECS on EC2 の肝）

---

### 3.1 ECS 用 IAM ロール

#### ① ECS Instance Role（EC2用）

* AmazonEC2ContainerServiceforEC2Role
* ECR Pull
* CloudWatch Logs

👉 **EC2起動時に必須**

---

#### ② ECS Task Execution Role

* ECR Pull
* CloudWatch Logs

---

#### ③ ECS Task Role

* Secrets Manager
* S3 / DynamoDB / RDS などアプリ権限

---

## 4. ECR 設計

---

### 4.1 ECR リポジトリ

| 項目         | 設定           |
| ---------- | ------------ |
| Repository | myapp-tomcat |
| Image Scan | ON           |
| Lifecycle  | 30世代         |

#### タグ戦略（推奨）

* `git-sha`
* `release-yyyymmdd`

---

## 5. ECS（EC2）設計（超重要）

---

### 5.1 ECS Cluster

| 項目                | 内容                |
| ----------------- | ----------------- |
| Cluster Name      | myapp-ec2-cluster |
| Capacity Provider | ASG               |

---

### 5.2 EC2（Auto Scaling Group）設計

#### インスタンス設計例

| 項目            | 値                 |
| ------------- | ----------------- |
| Instance Type | m6i.large         |
| vCPU          | 2                 |
| Memory        | 8GB               |
| AMI           | ECS Optimized AMI |
| Root Volume   | 50GB              |

#### ASG 設定

| 項目      | 値 |
| ------- | - |
| Min     | 2 |
| Desired | 2 |
| Max     | 6 |

👉 **Capacity Provider と連携**

---

### 5.3 ECS Task Definition（EC2用）

#### リソース指定（Fargateとの違い）

| 項目     | 設定   |
| ------ | ---- |
| CPU    | 1024 |
| Memory | 4096 |

※ EC2全体のリソース内で**柔軟に割当**

---

#### コンテナ定義（例）

| 項目      | 値           |
| ------- | ----------- |
| Image   | ECR URI     |
| Port    | 8080        |
| Log     | awslogs     |
| Env     | APP_ENV     |
| Secrets | DB_PASSWORD |

---

### 5.4 ECS Service

| 項目            | 設定          |
| ------------- | ----------- |
| Desired       | 2           |
| Deployment    | Rolling     |
| Placement     | Spread (AZ) |
| Load Balancer | ALB         |

---

## 6. ALB 設計

---

### 6.1 ALB 設定

| 項目          | 値               |
| ----------- | --------------- |
| Scheme      | internet-facing |
| Listener    | 443             |
| Target Type | instance        |
| HealthCheck | /health         |

#### 推奨

* Idle Timeout：60s
* HTTP/2：ON

---

## 7. CI/CD 設計（ECS on EC2）

---

### 7.1 CI/CD 全体像

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

### 7.2 CIツール選定

| ツール            | 理由           |
| -------------- | ------------ |
| GitHub Actions | シンプル         |
| CodePipeline   | Blue/Green対応 |
| Jenkins        | 高自由度         |

---

## 8. CI 構築手順（GitHub Actions 例）

---

### 8.1 CI用 IAM

#### 権限

* ecr:PutImage
* ecs:RegisterTaskDefinition
* ecs:UpdateService

---

### 8.2 GitHub Actions Workflow（概要）

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
            --service myapp-service \
            --force-new-deployment
```

---

## 9. CD（Blue/Green）構成（推奨）

```
CodePipeline
 ├─ Source
 ├─ Build
 ├─ Deploy (ECS Blue/Green)
 └─ Approval
```

#### メリット

* 即ロールバック
* 無停止デプロイ
* 本番向け

---

## 10. 監視・ログ設計

---

### 10.1 ログ

| 種別        | 保存先             |
| --------- | --------------- |
| アプリ       | CloudWatch Logs |
| ECS Agent | CloudWatch      |
| ALB       | S3              |

---

### 10.2 メトリクス

* ECS CPU / Memory
* EC2 CPU / Disk
* ALB TargetResponseTime

---

## 11. ECS on EC2 特有の設計ポイント（重要）

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
