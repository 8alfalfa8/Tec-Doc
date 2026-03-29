<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. 全体像（移行方式）](#1-全体像移行方式)
    - [移行アーキテクチャ概要](#移行アーキテクチャ概要)
    - [基本方針](#基本方針)
- [2. 作業タスク一覧（WBS）](#2-作業タスク一覧wbs)
- [3. 各タスクの詳細](#3-各タスクの詳細)
  - [① 現行システム調査・棚卸](#①-現行システム調査棚卸)
    - [入手情報](#入手情報)
    - [作業内容](#作業内容)
    - [確認ポイント](#確認ポイント)
    - [成果物](#成果物)
  - [② 移行方式・非機能要件整理](#②-移行方式非機能要件整理)
    - [入手情報](#入手情報)
    - [作業内容](#作業内容)
    - [決定事項例](#決定事項例)
    - [成果物](#成果物)
  - [③ Docker化（Tomcat + WAR）](#③-docker化tomcat-war)
    - [入手情報](#入手情報)
    - [Dockerfile例](#dockerfile例)
    - [作業内容](#作業内容)
    - [成果物](#成果物)
  - [④ AWS / EKS 基盤設計](#④-aws-eks-基盤設計)
    - [入手情報](#入手情報)
    - [設計内容](#設計内容)
    - [成果物](#成果物)
  - [⑤ EKS環境構築](#⑤-eks環境構築)
    - [作業内容](#作業内容)
    - [コマンド例](#コマンド例)
    - [成果物](#成果物)
  - [⑥ アプリ設定の外部化](#⑥-アプリ設定の外部化)
    - [設定対象](#設定対象)
    - [作業内容](#作業内容)
    - [成果物](#成果物)
  - [⑦ Kubernetesリソース作成](#⑦-kubernetesリソース作成)
    - [対象リソース](#対象リソース)
    - [Deployment例](#deployment例)
    - [成果物](#成果物)
  - [⑧ Ingress（ALB）構築](#⑧-ingressalb構築)
    - [作業内容](#作業内容)
    - [設定ポイント](#設定ポイント)
    - [成果物](#成果物)
  - [⑨ CI/CD構築](#⑨-cicd構築)
    - [流れ](#流れ)
    - [使用例](#使用例)
    - [成果物](#成果物)
  - [⑩ データ・外部連携確認](#⑩-データ外部連携確認)
    - [作業内容](#作業内容)
    - [成果物](#成果物)
  - [⑪ テスト](#⑪-テスト)
    - [成果物](#成果物)
  - [⑫ 本番切替](#⑫-本番切替)
    - [作業内容](#作業内容)
    - [成果物](#成果物)
  - [⑬ 運用設計・引継ぎ](#⑬-運用設計引継ぎ)
    - [設計内容](#設計内容)
    - [成果物](#成果物)
- [4. よくある移行時の落とし穴](#4-よくある移行時の落とし穴)
<!-- TOC_END -->

# ◆ オンプレミスのTomcat（WAR 配布）システムをAWS EKS（Kubernetes）へ移行

以下は、**オンプレミスの Tomcat（WAR 配布）システムを AWS EKS（Kubernetes）へ移行**する際の
**実務レベルの作業タスク分解（WBS）＋各タスクの詳細**です。
実案件（エンタープライズ／SI）でそのまま使える粒度で整理しています。

---

## 1. 全体像（移行方式）
[🔙 目次に戻る](#index)


#### 移行アーキテクチャ概要
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


#### 基本方針
[🔙 目次に戻る](#index)


| 項目    | 方針                             |
| ----- | ------------------------------ |
| アプリ   | WARをDocker化してTomcatコンテナとして稼働   |
| 実行基盤  | Amazon EKS（Managed Kubernetes） |
| 入口    | ALB Ingress Controller         |
| 設定    | ConfigMap / Secret             |
| ストレージ | EFS or S3（必要に応じて）              |
| CI/CD | GitHub Actions / CodePipeline  |
| 可用性   | Pod冗長＋AutoScaling              |

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 2. 作業タスク一覧（WBS）
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


## 3. 各タスクの詳細
[🔙 目次に戻る](#index)


---

### ① 現行システム調査・棚卸
[🔙 目次に戻る](#index)


#### 入手情報
[🔙 目次に戻る](#index)


* WARファイル
* Tomcatバージョン
* Javaバージョン
* server.xml / context.xml / web.xml
* JVMオプション
* 外部依存（DB、外部API、ファイル）

[🔙 目次に戻る](#index)


#### 作業内容
[🔙 目次に戻る](#index)


* アプリ構成・起動方式の把握
* 環境依存箇所洗い出し

[🔙 目次に戻る](#index)


#### 確認ポイント
[🔙 目次に戻る](#index)


| 項目     | 内容        |
| ------ | --------- |
| ポート    | 8080固定か   |
| セッション  | メモリ or DB |
| ファイル出力 | ローカルか共有か  |
| バッチ    | 同居していないか  |

[🔙 目次に戻る](#index)


#### 成果物

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)


* 現行構成図
* 環境依存一覧
* 移行影響調査書

---

[🔙 目次に戻る](#index)


### ② 移行方式・非機能要件整理
[🔙 目次に戻る](#index)


#### 入手情報
[🔙 目次に戻る](#index)


* SLA / SLO
* 性能要件（TPS、同時接続）
* 可用性要件
* セキュリティ要件

[🔙 目次に戻る](#index)


#### 作業内容
[🔙 目次に戻る](#index)


* ステートレス化可否
* セッション管理方針決定

[🔙 目次に戻る](#index)


#### 決定事項例
[🔙 目次に戻る](#index)


| 項目    | 方針                     |
| ----- | ---------------------- |
| セッション | Spring Session + Redis |
| ログ    | stdout → CloudWatch    |
| ファイル  | S3/EFS                 |

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



#### 成果物
[🔙 目次に戻る](#index)


* 移行方式設計書
* 非機能要件定義書

---

[🔙 目次に戻る](#index)


### ③ Docker化（Tomcat + WAR）
[🔙 目次に戻る](#index)


#### 入手情報
[🔙 目次に戻る](#index)


* WARファイル
* Tomcat公式イメージ
* JVM設定

[🔙 目次に戻る](#index)


#### Dockerfile例
[🔙 目次に戻る](#index)


```dockerfile
FROM tomcat:9.0-jdk17
COPY sample.war /usr/local/tomcat/webapps/
ENV JAVA_OPTS="-Xms512m -Xmx1024m"
```

[🔙 目次に戻る](#index)


#### 作業内容
[🔙 目次に戻る](#index)


* WAR組込み
* JVMチューニング
* ヘルスチェック設定

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



#### 成果物
[🔙 目次に戻る](#index)


* Dockerfile
* ローカル起動確認ログ

---

[🔙 目次に戻る](#index)


### ④ AWS / EKS 基盤設計
[🔙 目次に戻る](#index)


#### 入手情報
[🔙 目次に戻る](#index)


* AWSアカウント
* VPC設計方針
* セキュリティポリシー

[🔙 目次に戻る](#index)


#### 設計内容
[🔙 目次に戻る](#index)


| 項目   | 設計                 |
| ---- | ------------------ |
| VPC  | Private Subnet     |
| Node | Managed Node Group |
| IAM  | IRSA               |
| ログ   | CloudWatch         |

[🔙 目次に戻る](#index)


#### 成果物
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* AWS構成図
* EKS設計書

---

[🔙 目次に戻る](#index)


### ⑤ EKS環境構築
[🔙 目次に戻る](#index)


#### 作業内容
[🔙 目次に戻る](#index)


* EKSクラスター作成
* ノードグループ作成
* kubectl 接続

[🔙 目次に戻る](#index)


#### コマンド例
[🔙 目次に戻る](#index)


```bash
eksctl create cluster --name app-cluster
```

[🔙 目次に戻る](#index)


#### 成果物
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* EKSクラスター
* kubeconfig

---

[🔙 目次に戻る](#index)


### ⑥ アプリ設定の外部化
[🔙 目次に戻る](#index)


#### 設定対象
[🔙 目次に戻る](#index)


| 種別   | 管理方法         |
| ---- | ------------ |
| DB接続 | Secret       |
| 環境変数 | ConfigMap    |
| 証明書  | ACM + Secret |

[🔙 目次に戻る](#index)


#### 作業内容
[🔙 目次に戻る](#index)


* application.properties 分離
* 機密情報排除

[🔙 目次に戻る](#index)


#### 成果物
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* ConfigMap定義
* Secret定義

---

[🔙 目次に戻る](#index)


### ⑦ Kubernetesリソース作成
[🔙 目次に戻る](#index)


#### 対象リソース
[🔙 目次に戻る](#index)


* Deployment
* Service
* HPA

[🔙 目次に戻る](#index)


#### Deployment例
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


#### 成果物
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* YAMLマニフェスト一式

---

[🔙 目次に戻る](#index)


### ⑧ Ingress（ALB）構築
[🔙 目次に戻る](#index)


#### 作業内容
[🔙 目次に戻る](#index)


* ALB Ingress Controller導入
* HTTPS設定

[🔙 目次に戻る](#index)


#### 設定ポイント
[🔙 目次に戻る](#index)


| 項目      | 内容      |
| ------- | ------- |
| SSL     | ACM     |
| パス      | /app    |
| ヘルスチェック | /health |

[🔙 目次に戻る](#index)


#### 成果物
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* Ingress定義
* ALB

---

[🔙 目次に戻る](#index)


### ⑨ CI/CD構築
[🔙 目次に戻る](#index)


#### 流れ
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



```
Git Push
 → Docker Build
 → ECR Push
 → kubectl apply
```

[🔙 目次に戻る](#index)


#### 使用例
[🔙 目次に戻る](#index)


* GitHub Actions
* CodePipeline

[🔙 目次に戻る](#index)


#### 成果物
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* CI/CD定義
* 自動デプロイ確認

---

[🔙 目次に戻る](#index)


### ⑩ データ・外部連携確認
[🔙 目次に戻る](#index)


#### 作業内容
[🔙 目次に戻る](#index)


* DB接続確認
* 外部API疎通
* IAM権限確認

[🔙 目次に戻る](#index)


#### 成果物
[🔙 目次に戻る](#index)


* 接続確認結果

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### ⑪ テスト
[🔙 目次に戻る](#index)


| 種別 | 内容       |
| -- | -------- |
| 単体 | 起動確認     |
| 結合 | API      |
| 性能 | 負荷       |
| 障害 | Pod Kill |

#### 成果物
[🔙 目次に戻る](#index)


* テスト結果報告書

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### ⑫ 本番切替
[🔙 目次に戻る](#index)


#### 作業内容
[🔙 目次に戻る](#index)


* DNS切替
* Blue/Green or Canary

[🔙 目次に戻る](#index)


#### 成果物
[🔙 目次に戻る](#index)


* 切替手順書
* 切替完了報告

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### ⑬ 運用設計・引継ぎ
[🔙 目次に戻る](#index)


#### 設計内容
[🔙 目次に戻る](#index)


| 項目  | 内容         |
| --- | ---------- |
| 監視  | CloudWatch |
| 障害  | Runbook    |
| ロール | 運用体制       |

[🔙 目次に戻る](#index)


#### 成果物
[🔙 目次に戻る](#index)


* 運用設計書
* 障害対応Runbook

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 4. よくある移行時の落とし穴
[🔙 目次に戻る](#index)


| 問題      | 対策             |
| ------- | -------------- |
| セッション消失 | 外部セッション        |
| ファイル消失  | S3/EFS         |
| JVM不足   | リソース設計         |
| 再起動     | readinessProbe |

---

[🔙 目次に戻る](#index)


