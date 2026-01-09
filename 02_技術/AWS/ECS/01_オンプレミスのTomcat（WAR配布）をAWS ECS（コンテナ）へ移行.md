# ◆ オンプレミスのTomcat（WAR配布）をAWS ECS（コンテナ）へ移行

以下は、**オンプレミスのTomcat（WAR配布）をAWS ECS（コンテナ）へ移行**する際の、**実務レベルでの作業タスク分解**と**各タスクの詳細**です。
単なる手順ではなく、**設計・構築・移行・運用を見据えた実践的な内容**で整理しています。

---

## 1. 全体作業フェーズと構成イメージ

### 移行後の基本アーキテクチャ（例）

```
ALB
 └─ ECS Service
     └─ ECS Task
         └─ Tomcat Container
              └─ WARアプリ
```

* コンテナ基盤：ECS（Fargate or EC2）
* コンテナイメージ：Tomcat + WAR
* 外部連携：RDS / S3 / ElastiCache / Secrets Manager
* CI/CD：CodePipeline / GitHub Actions 等

---

## 2. フェーズ別作業タスク一覧

| フェーズ  | タスク                    |
| ----- | ---------------------- |
| 現状調査  | 現行Tomcat/アプリ調査         |
| 移行設計  | コンテナ設計・ECS設計           |
| コンテナ化 | Dockerfile作成           |
| AWS設計 | ECS / ALB / IAM / NW設計 |
| 構築    | ECS環境構築                |
| 移行    | WAR・設定移行               |
| テスト   | 機能・性能・障害テスト            |
| 切替    | 本番切替                   |
| 運用    | 監視・ログ・運用設計             |

---

## 3. 各作業タスクの詳細

---

### ① 現行オンプレミス環境調査（最重要）

#### 目的

* **WARをそのまま動かせるか**
* **コンテナ化時の制約洗い出し**

#### 必要な入手情報

| 分類     | 内容                                 |
| ------ | ---------------------------------- |
| Tomcat | バージョン、起動オプション                      |
| Java   | JDK/JREバージョン                       |
| WAR    | サイズ、依存ライブラリ                        |
| 設定     | server.xml / context.xml / web.xml |
| 外部     | DB接続、外部API                         |
| ファイル   | ローカルファイル依存有無                       |
| バッチ    | cron / シェル有無                       |

#### 作業内容

* Tomcat起動コマンド確認
* JVMオプション確認（Heap, GC）
* 環境依存パス洗い出し
* ファイル永続化要否確認

#### 成果物

* 現行環境調査シート
* コンテナ化可否リスト
* 移行リスク一覧

---

### ② コンテナ化方針設計

#### 主な設計判断

| 項目      | 判断例              |
| ------- | ---------------- |
| ベースイメージ | tomcat:9-jdk17   |
| WAR配置   | webapps/ROOT.war |
| 設定方法    | 環境変数             |
| ログ      | stdout/stderr    |
| ファイル    | S3 or EFS        |

#### 重要ポイント

* **コンテナ内に状態を持たせない**
* **WARはイメージに含める or 起動時DL**

#### 成果物

* コンテナ設計書
* 環境変数定義一覧

---

### ③ Dockerfile作成（Tomcat + WAR）

#### 作業内容

* Tomcat公式イメージ利用
* WAR配置
* 不要app削除
* タイムゾーン設定

#### 設定例

```dockerfile
FROM tomcat:9.0-jdk17

ENV TZ=Asia/Tokyo

RUN rm -rf /usr/local/tomcat/webapps/*

COPY app.war /usr/local/tomcat/webapps/ROOT.war

EXPOSE 8080
```

#### 成果物

* Dockerfile
* ビルド済みDocker Image

---

### ④ AWSインフラ設計

#### 必要設計要素

| 項目      | 内容                       |
| ------- | ------------------------ |
| VPC     | 既存 or 新規                 |
| Subnet  | Public / Private         |
| ALB     | HTTPS終端                  |
| ECS     | Fargate推奨                |
| IAM     | TaskRole / ExecutionRole |
| Secrets | DBパスワード                  |

#### ポイント

* **ALB + ECS Service**
* **Task RoleでSecrets取得**
* **セキュリティグループ最小化**

#### 成果物

* AWS構成図
* IAM設計書
* NW設計書

---

### ⑤ ECS Task / Service 設計

#### Task定義設定例

| 項目     | 内容       |
| ------ | -------- |
| CPU    | 512      |
| Memory | 1024     |
| Port   | 8080     |
| Env    | DB_URL 等 |
| Logs   | awslogs  |

#### 設定内容

* コンテナ定義
* 環境変数
* シークレット参照

#### 成果物

* ECS Task Definition
* ECS Service設定

---

### ⑥ 外部設定・Secrets移行

#### 作業内容

* DB接続情報をSecrets Managerへ登録
* ECS Task Roleに権限付与
* 環境変数 or ファイル注入

#### 設定例

```json
"secrets": [
  {
    "name": "DB_PASSWORD",
    "valueFrom": "arn:aws:secretsmanager:..."
  }
]
```

#### 成果物

* Secrets定義一覧
* IAMポリシー

---

### ⑦ ログ・監視設計

#### ログ

| 種類     | 方法             |
| ------ | -------------- |
| アプリ    | stdout         |
| Tomcat | catalina.out   |
| ALB    | ALB Access Log |

#### 監視

* CloudWatch Metrics
* ALB HealthCheck
* ECS Service Auto Healing

#### 成果物

* 監視設計書
* アラート定義

---

### ⑧ テスト

### 実施テスト

| 種類 | 内容       |
| -- | -------- |
| 単体 | WAR起動    |
| 結合 | DB/API接続 |
| 性能 | 負荷試験     |
| 障害 | コンテナ停止   |

#### 成果物

* テスト結果報告書
* 性能比較資料

---

### ⑨ 本番切替

#### 作業内容

* DNS切替（Route53）
* ALB Target切替
* ロールバック手順確認

#### 成果物

* 切替手順書
* ロールバック手順書

---

### ⑩ 運用・改善

#### 運用項目

* スケールアウト設定
* JVMチューニング
* イメージ更新手順

#### 成果物

* 運用設計書
* 障害対応Runbook

---

## 4. 移行時の典型的な注意点

| 問題      | 対策            |
| ------- | ------------- |
| ファイル消失  | S3/EFS        |
| セッション消失 | ElastiCache   |
| 起動遅延    | HealthCheck調整 |
| Heap不足  | Fargateメモリ増加  |

---
