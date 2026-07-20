# ◆ ECR＋ECS（Fargate）を前提としたAWSインフラ設計例
<!-- PROFILE_BADGE_START -->

[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?logo=github)](https://github.com/8alfalfa8)
[![Qiita](https://img.shields.io/badge/Qiita-Profile-55C500?logo=qiita&logoColor=white)](https://qiita.com/8alfalfa8)
[![Zenn](https://img.shields.io/badge/Zenn-Profile-3EA8FF?logo=zenn&logoColor=white)](https://zenn.dev/8alfalfa8)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/8alfalfa8)

<!-- PROFILE_BADGE_END -->


以下では、**ECR＋ECS（Fargate）を前提としたAWSインフラ設計例**と、
**実務でそのまま構築できるレベルの詳細手順（CI/CD含む）**を、

* 設計全体像
* インフラ設計（NW / セキュリティ / ECS）
* CI/CD設計（Git → Build → ECR → ECS）
* 構築手順（順番・設定値・注意点）

という流れで **体系的かつ深掘り**して説明します。

---

## 1. 全体アーキテクチャ設計例（標準・王道）

### 1.1 システム全体構成図（論理）

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
[ ECR ]
     |
     v
[ ECS Service (Fargate) ]
     |
     v
[ ALB ]
     |
     v
[ Client ]
```

---

### 1.2 前提条件（想定）

| 項目   | 内容                    |
| ---- | --------------------- |
| アプリ  | Java / Tomcat / WAR   |
| 実行基盤 | ECS on Fargate        |
| デプロイ | Rolling or Blue/Green |
| 環境   | dev / stg / prod      |
| IaC  | Terraform（推奨）         |

---

## 2. AWSインフラ設計（詳細）

---

### 2.1 VPC / ネットワーク設計

#### VPC

| 項目   | 値           |
| ---- | ----------- |
| CIDR | 10.0.0.0/16 |

#### Subnet

| 種別      | CIDR         | 用途           |
| ------- | ------------ | ------------ |
| Public  | 10.0.1.0/24  | ALB          |
| Private | 10.0.11.0/24 | ECS(Fargate) |
| Private | 10.0.12.0/24 | ECS(Fargate) |

#### ポイント

* **FargateはPrivate Subnet**
* NAT Gateway 経由で外部通信
* AZ分散必須

---

### 2.2 セキュリティ設計

#### Security Group

| 対象  | In     | Out |
| --- | ------ | --- |
| ALB | 443    | All |
| ECS | ALB SG | All |

#### IAMロール（必須）

##### ECS Task Execution Role

* ECR pull
* CloudWatch Logs

##### ECS Task Role

* Secrets Manager
* S3 / RDS 接続

---

## 3. ECR設計

---

### 3.1 ECRリポジトリ設計

| 項目        | 設定               |
| --------- | ---------------- |
| Repo名     | myapp-tomcat     |
| Tag       | git-sha / latest |
| Scan      | ON               |
| Lifecycle | 30世代保持           |

---

### 3.2 ECRポリシー

* 不要イメージ自動削除
* 脆弱性スキャン有効化

---

## 4. ECS（Fargate）設計

---

### 4.1 ECS Cluster

| 項目       | 設定            |
| -------- | ------------- |
| Cluster  | myapp-cluster |
| Capacity | Fargate       |

---

### 4.2 Task Definition（重要）

#### リソース

| 項目     | 値            |
| ------ | ------------ |
| CPU    | 2048（2 vCPU） |
| Memory | 4096（4GB）    |

#### Container定義

| 項目      | 値           |
| ------- | ----------- |
| Image   | ECR URI     |
| Port    | 8080        |
| Log     | awslogs     |
| Env     | DB_URL等     |
| Secrets | DB_PASSWORD |

---

### 4.3 ECS Service

| 項目         | 設定      |
| ---------- | ------- |
| Desired    | 2       |
| Min        | 2       |
| Max        | 6       |
| Deployment | Rolling |
| Health     | ALB     |

---

## 5. ALB設計

---

### 5.1 ALB

| 項目       | 値               |
| -------- | --------------- |
| Scheme   | internet-facing |
| Listener | 443             |
| Target   | ECS             |
| Health   | /health         |

#### 推奨設定

* HTTP/2：ON
* Idle Timeout：60秒

---

## 6. CI/CD設計（超重要）

---

### 6.1 CI/CD全体フロー

```
Git Push
 ↓
CI
  - mvn test
  - docker build
  - docker push(ECR)
 ↓
CD
  - ECS Task Definition更新
  - ECS Service更新
```

---

### 6.2 CIツール選択

| ツール            | 特徴    |
| -------------- | ----- |
| GitHub Actions | シンプル  |
| CodePipeline   | AWS完結 |
| GitLab CI      | 柔軟    |

👉 **GitHub Actionsが実務で最も多い**

---

## 7. CI構築手順（GitHub Actions例）

---

### 7.1 IAM（CI用）

#### ポリシー

* ECR push
* ECS UpdateService
* RegisterTaskDefinition

---

### 7.2 GitHub Actions Workflow例（概要）

```yaml
name: build-and-deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build & Push
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker tag myapp:${{ github.sha }} $ECR_URI:${{ github.sha }}
          docker push $ECR_URI:${{ github.sha }}

      - name: Deploy ECS
        run: |
          aws ecs update-service \
            --cluster myapp \
            --service myapp-svc \
            --force-new-deployment
```

---

### 7.3 ポイント

* イメージタグは **git-sha**
* force-new-deployment で再起動
* 本番は Blue/Green 推奨

---

## 8. CD（Blue/Green）設計（発展）

---

### 8.1 構成

```
CodePipeline
 ├─ Build
 ├─ Deploy (ECS)
 └─ Approval
```

#### メリット

* 即ロールバック
* 無停止デプロイ

---

## 9. 監視・ログ設計

---

### 9.1 ログ

| 種別  | 保存先             |
| --- | --------------- |
| アプリ | CloudWatch Logs |
| ALB | S3              |
| ECS | CloudWatch      |

---

### 9.2 メトリクス

* CPU / Memory
* ALB RequestCountPerTarget
* TargetResponseTime

---

## 10. 構築手順まとめ（順序）

#### Step-by-Step

1. VPC / Subnet / NAT
2. ALB 作成
3. ECR 作成
4. IAM Role 作成
5. ECS Cluster
6. Task Definition
7. ECS Service
8. CI/CD構築
9. 監視設定
10. 負荷テスト

---

## 11. よくある失敗ポイント

❌ Task Role未設定<br>
❌ NATなしでECR Pull失敗<br>
❌ Heap > Fargate Memory<br>
❌ ALB Health Checkミス<br>
❌ latestタグ運用

---
