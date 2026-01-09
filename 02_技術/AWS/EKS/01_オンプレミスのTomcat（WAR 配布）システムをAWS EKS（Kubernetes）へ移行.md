# ◆ オンプレミスのTomcat（WAR 配布）システムをAWS EKS（Kubernetes）へ移行

以下は、**オンプレミスの Tomcat（WAR 配布）システムを AWS EKS（Kubernetes）へ移行**する際の
**実務レベルの作業タスク分解（WBS）＋各タスクの詳細**です。
実案件（エンタープライズ／SI）でそのまま使える粒度で整理しています。

---

## 1. 全体像（移行方式）

#### 移行アーキテクチャ概要

```
[Client]
   ↓
[ALB Ingress Controller]
   ↓
[Kubernetes Service]
   ↓
[Tomcat Pod (WAR)]
   ↓
[DB / 外部API]
```

#### 基本方針

| 項目    | 方針                             |
| ----- | ------------------------------ |
| アプリ   | WARをDocker化してTomcatコンテナとして稼働   |
| 実行基盤  | Amazon EKS（Managed Kubernetes） |
| 入口    | ALB Ingress Controller         |
| 設定    | ConfigMap / Secret             |
| ストレージ | EFS or S3（必要に応じて）              |
| CI/CD | GitHub Actions / CodePipeline  |
| 可用性   | Pod冗長＋AutoScaling              |

---

## 2. 作業タスク一覧（WBS）

| #  | タスク                   |
| -- | --------------------- |
| 1  | 現行（オンプレ）調査・棚卸         |
| 2  | 移行方式・非機能要件整理          |
| 3  | Docker化（Tomcat + WAR） |
| 4  | AWS/EKS基盤設計           |
| 5  | EKS環境構築               |
| 6  | アプリ設定の外部化             |
| 7  | Kubernetesリソース作成      |
| 8  | Ingress（ALB）構築        |
| 9  | CI/CD構築               |
| 10 | データ・外部連携確認            |
| 11 | テスト                   |
| 12 | 本番切替・移行               |
| 13 | 運用設計・引継ぎ              |

---

## 3. 各タスクの詳細

---

### ① 現行システム調査・棚卸

#### 入手情報

* WARファイル
* Tomcatバージョン
* Javaバージョン
* server.xml / context.xml / web.xml
* JVMオプション
* 外部依存（DB、外部API、ファイル）

#### 作業内容

* アプリ構成・起動方式の把握
* 環境依存箇所洗い出し

#### 確認ポイント

| 項目     | 内容        |
| ------ | --------- |
| ポート    | 8080固定か   |
| セッション  | メモリ or DB |
| ファイル出力 | ローカルか共有か  |
| バッチ    | 同居していないか  |

#### 成果物

* 現行構成図
* 環境依存一覧
* 移行影響調査書

---

### ② 移行方式・非機能要件整理

#### 入手情報

* SLA / SLO
* 性能要件（TPS、同時接続）
* 可用性要件
* セキュリティ要件

#### 作業内容

* ステートレス化可否
* セッション管理方針決定

#### 決定事項例

| 項目    | 方針                     |
| ----- | ---------------------- |
| セッション | Spring Session + Redis |
| ログ    | stdout → CloudWatch    |
| ファイル  | S3/EFS                 |

#### 成果物

* 移行方式設計書
* 非機能要件定義書

---

### ③ Docker化（Tomcat + WAR）

#### 入手情報

* WARファイル
* Tomcat公式イメージ
* JVM設定

#### Dockerfile例

```dockerfile
FROM tomcat:9.0-jdk17
COPY sample.war /usr/local/tomcat/webapps/
ENV JAVA_OPTS="-Xms512m -Xmx1024m"
```

#### 作業内容

* WAR組込み
* JVMチューニング
* ヘルスチェック設定

#### 成果物

* Dockerfile
* ローカル起動確認ログ

---

### ④ AWS / EKS 基盤設計

#### 入手情報

* AWSアカウント
* VPC設計方針
* セキュリティポリシー

#### 設計内容

| 項目   | 設計                 |
| ---- | ------------------ |
| VPC  | Private Subnet     |
| Node | Managed Node Group |
| IAM  | IRSA               |
| ログ   | CloudWatch         |

#### 成果物

* AWS構成図
* EKS設計書

---

### ⑤ EKS環境構築

#### 作業内容

* EKSクラスター作成
* ノードグループ作成
* kubectl 接続

#### コマンド例

```bash
eksctl create cluster --name app-cluster
```

#### 成果物

* EKSクラスター
* kubeconfig

---

### ⑥ アプリ設定の外部化

#### 設定対象

| 種別   | 管理方法         |
| ---- | ------------ |
| DB接続 | Secret       |
| 環境変数 | ConfigMap    |
| 証明書  | ACM + Secret |

#### 作業内容

* application.properties 分離
* 機密情報排除

#### 成果物

* ConfigMap定義
* Secret定義

---

### ⑦ Kubernetesリソース作成

#### 対象リソース

* Deployment
* Service
* HPA

#### Deployment例

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: tomcat
        image: xxxx.dkr.ecr.ap-northeast-1.amazonaws.com/app
```

#### 成果物

* YAMLマニフェスト一式

---

### ⑧ Ingress（ALB）構築

#### 作業内容

* ALB Ingress Controller導入
* HTTPS設定

#### 設定ポイント

| 項目      | 内容      |
| ------- | ------- |
| SSL     | ACM     |
| パス      | /app    |
| ヘルスチェック | /health |

#### 成果物

* Ingress定義
* ALB

---

### ⑨ CI/CD構築

#### 流れ

```
Git Push
 → Docker Build
 → ECR Push
 → kubectl apply
```

#### 使用例

* GitHub Actions
* CodePipeline

#### 成果物

* CI/CD定義
* 自動デプロイ確認

---

### ⑩ データ・外部連携確認

#### 作業内容

* DB接続確認
* 外部API疎通
* IAM権限確認

#### 成果物

* 接続確認結果

---

### ⑪ テスト

| 種別 | 内容       |
| -- | -------- |
| 単体 | 起動確認     |
| 結合 | API      |
| 性能 | 負荷       |
| 障害 | Pod Kill |

#### 成果物

* テスト結果報告書

---

### ⑫ 本番切替

#### 作業内容

* DNS切替
* Blue/Green or Canary

#### 成果物

* 切替手順書
* 切替完了報告

---

### ⑬ 運用設計・引継ぎ

#### 設計内容

| 項目  | 内容         |
| --- | ---------- |
| 監視  | CloudWatch |
| 障害  | Runbook    |
| ロール | 運用体制       |

#### 成果物

* 運用設計書
* 障害対応Runbook

---

## 4. よくある移行時の落とし穴

| 問題      | 対策             |
| ------- | -------------- |
| セッション消失 | 外部セッション        |
| ファイル消失  | S3/EFS         |
| JVM不足   | リソース設計         |
| 再起動     | readinessProbe |

---

