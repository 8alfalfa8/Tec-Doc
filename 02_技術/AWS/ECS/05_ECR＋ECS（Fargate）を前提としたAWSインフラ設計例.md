<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. 全体アーキテクチャ設計例（標準・王道）](#1-全体アーキテクチャ設計例標準王道)
  - [1.1 システム全体構成図（論理）](#11-システム全体構成図論理)
  - [1.2 前提条件（想定）](#12-前提条件想定)
- [2. AWSインフラ設計（詳細）](#2-awsインフラ設計詳細)
  - [2.1 VPC / ネットワーク設計](#21-vpc-ネットワーク設計)
    - [VPC](#vpc)
    - [Subnet](#subnet)
    - [ポイント](#ポイント)
  - [2.2 セキュリティ設計](#22-セキュリティ設計)
    - [Security Group](#security-group)
    - [IAMロール（必須）](#iamロール必須)
      - [ECS Task Execution Role](#ecs-task-execution-role)
      - [ECS Task Role](#ecs-task-role)
- [3. ECR設計](#3-ecr設計)
  - [3.1 ECRリポジトリ設計](#31-ecrリポジトリ設計)
  - [3.2 ECRポリシー](#32-ecrポリシー)
- [4. ECS（Fargate）設計](#4-ecsfargate設計)
  - [4.1 ECS Cluster](#41-ecs-cluster)
  - [4.2 Task Definition（重要）](#42-task-definition重要)
    - [リソース](#リソース)
    - [Container定義](#container定義)
  - [4.3 ECS Service](#43-ecs-service)
- [5. ALB設計](#5-alb設計)
  - [5.1 ALB](#51-alb)
    - [推奨設定](#推奨設定)
- [6. CI/CD設計（超重要）](#6-cicd設計超重要)
  - [6.1 CI/CD全体フロー](#61-cicd全体フロー)
  - [6.2 CIツール選択](#62-ciツール選択)
- [7. CI構築手順（GitHub Actions例）](#7-ci構築手順github-actions例)
  - [7.1 IAM（CI用）](#71-iamci用)
    - [ポリシー](#ポリシー)
  - [7.2 GitHub Actions Workflow例（概要）](#72-github-actions-workflow例概要)
  - [7.3 ポイント](#73-ポイント)
- [8. CD（Blue/Green）設計（発展）](#8-cdbluegreen設計発展)
  - [8.1 構成](#81-構成)
    - [メリット](#メリット)
- [9. 監視・ログ設計](#9-監視ログ設計)
  - [9.1 ログ](#91-ログ)
  - [9.2 メトリクス](#92-メトリクス)
- [10. 構築手順まとめ（順序）](#10-構築手順まとめ順序)
    - [Step-by-Step](#step-by-step)
- [11. よくある失敗ポイント](#11-よくある失敗ポイント)
<!-- TOC_END -->

# ◆ ECR＋ECS（Fargate）を前提としたAWSインフラ設計例

以下では、**ECR＋ECS（Fargate）を前提としたAWSインフラ設計例**と、
**実務でそのまま構築できるレベルの詳細手順（CI/CD含む）**を、

* 設計全体像
* インフラ設計（NW / セキュリティ / ECS）
* CI/CD設計（Git → Build → ECR → ECS）
* 構築手順（順番・設定値・注意点）

という流れで **体系的かつ深掘り**して説明します。

---

## 1. 全体アーキテクチャ設計例（標準・王道）
[🔙 目次に戻る](#index)


### 1.1 システム全体構成図（論理）
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

[🔙 目次に戻る](#index)


### 1.2 前提条件（想定）
[🔙 目次に戻る](#index)


| 項目   | 内容                    |
| ---- | --------------------- |
| アプリ  | Java / Tomcat / WAR   |
| 実行基盤 | ECS on Fargate        |
| デプロイ | Rolling or Blue/Green |
| 環境   | dev / stg / prod      |
| IaC  | Terraform（推奨）         |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 2. AWSインフラ設計（詳細）
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


#### Subnet
[🔙 目次に戻る](#index)


| 種別      | CIDR         | 用途           |
| ------- | ------------ | ------------ |
| Public  | 10.0.1.0/24  | ALB          |
| Private | 10.0.11.0/24 | ECS(Fargate) |
| Private | 10.0.12.0/24 | ECS(Fargate) |

[🔙 目次に戻る](#index)


#### ポイント
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* **FargateはPrivate Subnet**
* NAT Gateway 経由で外部通信
* AZ分散必須

---

[🔙 目次に戻る](#index)


### 2.2 セキュリティ設計
[🔙 目次に戻る](#index)


#### Security Group
[🔙 目次に戻る](#index)


| 対象  | In     | Out |
| --- | ------ | --- |
| ALB | 443    | All |
| ECS | ALB SG | All |

[🔙 目次に戻る](#index)


#### IAMロール（必須）
[🔙 目次に戻る](#index)


##### ECS Task Execution Role

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)


* ECR pull
* CloudWatch Logs

[🔙 目次に戻る](#index)


##### ECS Task Role
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* Secrets Manager
* S3 / RDS 接続

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 3. ECR設計
[🔙 目次に戻る](#index)


---

### 3.1 ECRリポジトリ設計
[🔙 目次に戻る](#index)


| 項目        | 設定               |
| --------- | ---------------- |
| Repo名     | myapp-tomcat     |
| Tag       | git-sha / latest |
| Scan      | ON               |
| Lifecycle | 30世代保持           |

---

[🔙 目次に戻る](#index)


### 3.2 ECRポリシー
[🔙 目次に戻る](#index)


* 不要イメージ自動削除
* 脆弱性スキャン有効化

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 4. ECS（Fargate）設計
[🔙 目次に戻る](#index)


---

### 4.1 ECS Cluster
[🔙 目次に戻る](#index)


| 項目       | 設定            |
| -------- | ------------- |
| Cluster  | myapp-cluster |
| Capacity | Fargate       |

---

[🔙 目次に戻る](#index)


### 4.2 Task Definition（重要）
[🔙 目次に戻る](#index)


#### リソース
[🔙 目次に戻る](#index)


| 項目     | 値            |
| ------ | ------------ |
| CPU    | 2048（2 vCPU） |
| Memory | 4096（4GB）    |

[🔙 目次に戻る](#index)


#### Container定義
[🔙 目次に戻る](#index)


| 項目      | 値           |
| ------- | ----------- |
| Image   | ECR URI     |
| Port    | 8080        |
| Log     | awslogs     |
| Env     | DB_URL等     |
| Secrets | DB_PASSWORD |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 4.3 ECS Service
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



| 項目         | 設定      |
| ---------- | ------- |
| Desired    | 2       |
| Min        | 2       |
| Max        | 6       |
| Deployment | Rolling |
| Health     | ALB     |

---

[🔙 目次に戻る](#index)


## 5. ALB設計
[🔙 目次に戻る](#index)


---

### 5.1 ALB
[🔙 目次に戻る](#index)


| 項目       | 値               |
| -------- | --------------- |
| Scheme   | internet-facing |
| Listener | 443             |
| Target   | ECS             |
| Health   | /health         |

#### 推奨設定
[🔙 目次に戻る](#index)


* HTTP/2：ON
* Idle Timeout：60秒

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 6. CI/CD設計（超重要）
[🔙 目次に戻る](#index)


---

### 6.1 CI/CD全体フロー
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


### 6.2 CIツール選択
[🔙 目次に戻る](#index)


| ツール            | 特徴    |
| -------------- | ----- |
| GitHub Actions | シンプル  |
| CodePipeline   | AWS完結 |
| GitLab CI      | 柔軟    |

👉 **GitHub Actionsが実務で最も多い**

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 7. CI構築手順（GitHub Actions例）
[🔙 目次に戻る](#index)


---

### 7.1 IAM（CI用）
[🔙 目次に戻る](#index)


#### ポリシー
[🔙 目次に戻る](#index)


* ECR push
* ECS UpdateService
* RegisterTaskDefinition

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 7.2 GitHub Actions Workflow例（概要）
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


### 7.3 ポイント

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)


* イメージタグは **git-sha**
* force-new-deployment で再起動
* 本番は Blue/Green 推奨

---

[🔙 目次に戻る](#index)


## 8. CD（Blue/Green）設計（発展）
[🔙 目次に戻る](#index)


---

### 8.1 構成
[🔙 目次に戻る](#index)


```
CodePipeline
 ├─ Build
 ├─ Deploy (ECS)
 └─ Approval
```

#### メリット
[🔙 目次に戻る](#index)


* 即ロールバック
* 無停止デプロイ

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 9. 監視・ログ設計
[🔙 目次に戻る](#index)


---

### 9.1 ログ
[🔙 目次に戻る](#index)


| 種別  | 保存先             |
| --- | --------------- |
| アプリ | CloudWatch Logs |
| ALB | S3              |
| ECS | CloudWatch      |

---

[🔙 目次に戻る](#index)


### 9.2 メトリクス
[🔙 目次に戻る](#index)


* CPU / Memory
* ALB RequestCountPerTarget
* TargetResponseTime

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 10. 構築手順まとめ（順序）
[🔙 目次に戻る](#index)


#### Step-by-Step
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 11. よくある失敗ポイント
[🔙 目次に戻る](#index)


❌ Task Role未設定<br>
❌ NATなしでECR Pull失敗<br>
❌ Heap > Fargate Memory<br>
❌ ALB Health Checkミス<br>
❌ latestタグ運用

---

[🔙 目次に戻る](#index)

