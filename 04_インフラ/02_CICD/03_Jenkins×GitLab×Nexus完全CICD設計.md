<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. 全体像（目的と思想）](#1-全体像目的と思想)
  - [1.1 目的](#11-目的)
  - [1.2 基本思想（重要）](#12-基本思想重要)
- [2. 全体アーキテクチャ](#2-全体アーキテクチャ)
- [3. コンポーネント別設計](#3-コンポーネント別設計)
  - [3.1 GitLab 設計](#31-gitlab-設計)
    - [3.1.1 リポジトリ構成（例）](#311-リポジトリ構成例)
    - [3.1.2 ブランチ戦略（厳格）](#312-ブランチ戦略厳格)
    - [3.1.3 権限](#313-権限)
  - [3.2 Jenkins 設計](#32-jenkins-設計)
    - [3.2.1 Job構成](#321-job構成)
    - [3.2.2 Credentials設計](#322-credentials設計)
  - [3.3 Nexus 設計](#33-nexus-設計)
    - [3.3.1 リポジトリ種別](#331-リポジトリ種別)
    - [3.3.2 権限設計](#332-権限設計)
- [4. CI/CD処理フロー（詳細）](#4-cicd処理フロー詳細)
  - [4.1 CI（ビルド・テスト）](#41-ciビルドテスト)
  - [4.2 Artifact管理](#42-artifact管理)
  - [4.3 CD（デプロイ）](#43-cdデプロイ)
- [5. Jenkinsfile（実務用サンプル）](#5-jenkinsfile実務用サンプル)
- [6. 運用設計（超重要）](#6-運用設計超重要)
  - [6.1 運用ルール](#61-運用ルール)
  - [6.2 障害対応](#62-障害対応)
- [7. 監査・証跡設計](#7-監査証跡設計)
- [8. 成果物一覧（設計ドキュメント）](#8-成果物一覧設計ドキュメント)
- [Jenkins × GitLab × Nexus](#jenkins-gitlab-nexus)
  - [チェックリスト構築手順書（Linux）](#チェックリスト構築手順書linux)
- [0. 事前準備（共通）](#0-事前準備共通)
    - [0.1 環境情報整理](#01-環境情報整理)
- [1. GitLab 構築チェックリスト](#1-gitlab-構築チェックリスト)
  - [1.1 GitLabインストール](#11-gitlabインストール)
  - [1.2 ユーザー・権限](#12-ユーザー権限)
  - [1.3 リポジトリ設計](#13-リポジトリ設計)
  - [1.4 Webhook設定](#14-webhook設定)
- [2. Nexus 構築チェックリスト](#2-nexus-構築チェックリスト)
  - [2.1 Nexusインストール](#21-nexusインストール)
- [2.2 リポジトリ作成](#22-リポジトリ作成)
  - [2.3 権限設計](#23-権限設計)
  - [2.4 保管ポリシー](#24-保管ポリシー)
- [3. Jenkins 構築チェックリスト](#3-jenkins-構築チェックリスト)
  - [3.1 Jenkinsインストール](#31-jenkinsインストール)
  - [3.2 初期設定](#32-初期設定)
  - [3.3 認証・認可](#33-認証認可)
  - [3.4 セキュリティ](#34-セキュリティ)
- [4. Jenkins Agent 構築チェックリスト](#4-jenkins-agent-構築チェックリスト)
  - [4.1 Agent設計](#41-agent設計)
  - [4.2 Agent接続](#42-agent接続)
  - [4.3 Agent環境](#43-agent環境)
- [5. Jenkins × GitLab 連携チェック](#5-jenkins-gitlab-連携チェック)
- [6. Jenkins × Nexus 連携チェック](#6-jenkins-nexus-連携チェック)
- [7. Pipeline構築チェック](#7-pipeline構築チェック)
  - [7.1 Jenkinsfile配置](#71-jenkinsfile配置)
  - [7.2 CI Pipeline](#72-ci-pipeline)
  - [7.3 CD Pipeline](#73-cd-pipeline)
  - [7.4 異常系確認](#74-異常系確認)
- [8. 運用・監査チェック](#8-運用監査チェック)
  - [8.1 運用設計](#81-運用設計)
  - [8.2 監査対応](#82-監査対応)
- [9. 総合テスト](#9-総合テスト)
  - [付録：レビュー観点（監査用）](#付録レビュー観点監査用)
<!-- TOC_END -->

# ◆ Jenkins × GitLab × Nexus 完全CI/CD設計

以下は **Jenkins × GitLab × Nexus による**「**完全CI/CD設計**」です。
**金融・公共レベル**（**監査・権限制御・分離設計**）を前提に、
**構成／処理フロー／権限設計／Pipeline例／運用ルール**まで落とします。

---

## 1. 全体像（目的と思想）
[🔙 目次に戻る](#index)


### 1.1 目的
[🔙 目次に戻る](#index)


* **ソース～成果物までの完全自動化**
* 人手作業を排除し **再現性・証跡・統制** を確保
* Jenkinsを **制御点（Control Plane）** とする

### 1.2 基本思想（重要）
[🔙 目次に戻る](#index)


| 項目   | 方針                          |
| ---- | --------------------------- |
| 人手操作 | 本番は原則禁止                     |
| 認証情報 | Jenkins Credentials 一元管理    |
| 成果物  | **Nexusのみが正**               |
| デプロイ | Pipeline経由のみ                |
| 監査   | Git / Jenkins / Nexus で三点証跡 |

---

## 2. 全体アーキテクチャ
[🔙 目次に戻る](#index)


```
[Developer]
    |
    | Git Push / Merge
    v
[GitLab]
  - Source Repo
  - Merge Request
    |
    | Webhook
    v
[Jenkins Master]  ← 認証・承認・制御
    |
    | Build/Test
    v
[Jenkins Agent]
    |
    | Artifact Upload
    v
[Nexus Repository]
    |
    | Approved Artifact
    v
[Deploy Target]
 (ECS / EC2 / On-Prem)
```

---

## 3. コンポーネント別設計
[🔙 目次に戻る](#index)


### 3.1 GitLab 設計
[🔙 目次に戻る](#index)


#### 3.1.1 リポジトリ構成（例）
[🔙 目次に戻る](#index)


```
repo/
 ├ src/
 ├ pom.xml
 ├ Jenkinsfile
 └ docs/
```

#### 3.1.2 ブランチ戦略（厳格）
[🔙 目次に戻る](#index)


| ブランチ      | 用途   |
| --------- | ---- |
| main      | 本番   |
| release/* | リリース |
| develop   | 統合   |
| feature/* | 開発   |

#### 3.1.3 権限
[🔙 目次に戻る](#index)


| ロール        | 権限     |
| ---------- | ------ |
| Maintainer | Merge可 |
| Developer  | Push可  |
| Reporter   | Read   |

* **main直push禁止**
* MR必須＋レビュー必須

---

### 3.2 Jenkins 設計
[🔙 目次に戻る](#index)


#### 3.2.1 Job構成
[🔙 目次に戻る](#index)


| Job種別                | 内容    |
| -------------------- | ----- |
| Multibranch Pipeline | Git連動 |
| Deploy Pipeline      | 環境別   |

#### 3.2.2 Credentials設計
[🔙 目次に戻る](#index)


| 種別          | 用途              |
| ----------- | --------------- |
| Git SSH Key | GitLab          |
| Nexus User  | Artifact Upload |
| Deploy Key  | 本番              |

**Pipeline内ハードコード禁止**

---

### 3.3 Nexus 設計
[🔙 目次に戻る](#index)


#### 3.3.1 リポジトリ種別
[🔙 目次に戻る](#index)


| 種別     | 用途            |
| ------ | ------------- |
| hosted | 成果物保管         |
| proxy  | Maven Central |
| group  | 開発用           |

例：

* `maven-releases`
* `maven-snapshots`
* `maven-public`

---

#### 3.3.2 権限設計
[🔙 目次に戻る](#index)


| ロール       | 権限    |
| --------- | ----- |
| ci-upload | write |
| developer | read  |
| admin     | all   |

**削除権限は管理者のみ**

---

## 4. CI/CD処理フロー（詳細）
[🔙 目次に戻る](#index)


### 4.1 CI（ビルド・テスト）
[🔙 目次に戻る](#index)


1. DeveloperがGitLabにPush
2. GitLab Webhook → Jenkins
3. Jenkins Pipeline起動
4. Checkout
5. Build（Maven）
6. Unit Test
7. 静的解析（Sonar等）
8. 成果物生成

---

### 4.2 Artifact管理
[🔙 目次に戻る](#index)


9. Jenkins → NexusへUpload
10. バージョン固定
11. チェックサム生成
12. 監査ログ保存

---

### 4.3 CD（デプロイ）
[🔙 目次に戻る](#index)


13. リリース承認（Manual）
14. 承認後デプロイ実行
15. 対象環境へ展開
16. デプロイ結果記録

---

## 5. Jenkinsfile（実務用サンプル）
[🔙 目次に戻る](#index)


```groovy
pipeline {
  agent { label 'docker-agent' }

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  stages {
    stage('Checkout') {
      steps {
        git credentialsId: 'gitlab-key',
            url: 'git@gitlab.example.com:app/repo.git'
      }
    }

    stage('Build') {
      steps {
        sh 'mvn clean package -DskipTests=false'
      }
    }

    stage('Test') {
      steps {
        sh 'mvn test'
      }
    }

    stage('Upload to Nexus') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'nexus-creds',
          usernameVariable: 'NEXUS_USER',
          passwordVariable: 'NEXUS_PASS'
        )]) {
          sh '''
          mvn deploy \
            -Dnexus.username=$NEXUS_USER \
            -Dnexus.password=$NEXUS_PASS
          '''
        }
      }
    }

    stage('Approval') {
      when {
        branch 'main'
      }
      steps {
        input message: '本番リリース承認'
      }
    }

    stage('Deploy') {
      when {
        branch 'main'
      }
      steps {
        sh './deploy.sh'
      }
    }
  }
}
```

---

## 6. 運用設計（超重要）
[🔙 目次に戻る](#index)


### 6.1 運用ルール
[🔙 目次に戻る](#index)


| 項目        | ルール       |
| --------- | --------- |
| Jenkins操作 | 管理者のみ     |
| 本番実行      | 承認必須      |
| 成果物       | Nexus以外禁止 |
| ロール       | 定期棚卸      |

---

### 6.2 障害対応
[🔙 目次に戻る](#index)


* Jenkins停止 → Agent切替
* Nexus障害 → Artifact復旧
* GitLab障害 → CI停止許容

---

## 7. 監査・証跡設計
[🔙 目次に戻る](#index)


| 証跡    | 保存先           |
| ----- | ------------- |
| ソース変更 | GitLab        |
| 実行履歴  | Jenkins       |
| 成果物   | Nexus         |
| 承認    | Jenkins Input |

---

## 8. 成果物一覧（設計ドキュメント）
[🔙 目次に戻る](#index)


* CI/CD全体設計書
* Jenkins運用設計書
* GitLab権限設計書
* Nexusリポジトリ設計書
* Pipeline設計書
* 監査対応資料

---



# ◆ Jenkins × GitLab × Nexus チェックリスト構築手順

以下は **Jenkins × GitLab × Nexus のチェックリスト形式**「**構築手順書**」です。
**金融・公共案件でそのままレビュー・監査に出せる粒度**で、
**作業／確認／成果物**を明確にしています。

---

## Jenkins × GitLab × Nexus
[🔙 目次に戻る](#index)


### チェックリスト構築手順書（Linux）
[🔙 目次に戻る](#index)


---

## 0. 事前準備（共通）
[🔙 目次に戻る](#index)


#### 0.1 環境情報整理
[🔙 目次に戻る](#index)


* [ ] OS / Version 確定（例：Amazon Linux 2）
* [ ] ネットワーク構成確定（FW / Proxy）
* [ ] DNS / FQDN 決定
* [ ] 時刻同期（NTP）
* [ ] 管理者アカウント準備

**成果物**

* 環境構成図
* サーバ一覧表

---

## 1. GitLab 構築チェックリスト
[🔙 目次に戻る](#index)


### 1.1 GitLabインストール
[🔙 目次に戻る](#index)


* [ ] GitLabサーバ構築
* [ ] HTTPS有効化
* [ ] 管理者初期設定

### 1.2 ユーザー・権限
[🔙 目次に戻る](#index)


* [ ] 管理者アカウント作成
* [ ] Developer / Maintainer 作成
* [ ] 外部認証（LDAP/AD）設定（任意）

### 1.3 リポジトリ設計
[🔙 目次に戻る](#index)


* [ ] プロジェクト作成
* [ ] ブランチ戦略設定
* [ ] main直Push禁止
* [ ] MR必須設定
* [ ] Review必須設定

### 1.4 Webhook設定
[🔙 目次に戻る](#index)


* [ ] Jenkins向けWebhook登録
* [ ] イベント（Push / Merge）有効化
* [ ] 接続テスト実施

**成果物**

* GitLab設定シート
* 権限設計書

---

## 2. Nexus 構築チェックリスト
[🔙 目次に戻る](#index)


### 2.1 Nexusインストール
[🔙 目次に戻る](#index)


* [ ] Nexusインストール（OSS / Pro）
* [ ] HTTPS設定
* [ ] 管理者初期設定

## 2.2 リポジトリ作成
[🔙 目次に戻る](#index)


* [ ] hosted（releases）
* [ ] hosted（snapshots）
* [ ] proxy（maven central）
* [ ] group（maven-public）

### 2.3 権限設計
[🔙 目次に戻る](#index)


* [ ] ci-upload ロール作成
* [ ] read-only ロール作成
* [ ] adminロール確認
* [ ] 削除権限制限

### 2.4 保管ポリシー
[🔙 目次に戻る](#index)


* [ ] バージョニングルール
* [ ] スナップショット世代管理
* [ ] クリーンアップポリシー

**成果物**

* Nexusリポジトリ定義書
* 権限一覧表

---

## 3. Jenkins 構築チェックリスト
[🔙 目次に戻る](#index)


### 3.1 Jenkinsインストール
[🔙 目次に戻る](#index)


* [ ] Java（LTS）インストール
* [ ] Jenkinsインストール
* [ ] サービス起動確認
* [ ] 管理画面接続確認

### 3.2 初期設定
[🔙 目次に戻る](#index)


* [ ] 初期Admin設定
* [ ] 不要プラグイン無効化
* [ ] 必須プラグイン導入

  * [ ] Git
  * [ ] Pipeline
  * [ ] Credentials
  * [ ] Role Strategy

### 3.3 認証・認可
[🔙 目次に戻る](#index)


* [ ] 認証方式設定（内部 / LDAP）
* [ ] ロール作成（admin/dev/view）
* [ ] 権限割当

### 3.4 セキュリティ
[🔙 目次に戻る](#index)


* [ ] HTTPS（ALB/Nginx）
* [ ] CLI無効化
* [ ] Script Console制限

**成果物**

* Jenkins設定仕様書
* 権限設計書

---

## 4. Jenkins Agent 構築チェックリスト
[🔙 目次に戻る](#index)


### 4.1 Agent設計
[🔙 目次に戻る](#index)


* [ ] Master/Agent分離
* [ ] Agent実行ユーザー作成
* [ ] sudo権限なし確認

### 4.2 Agent接続
[🔙 目次に戻る](#index)


* [ ] SSH/JNLP/Docker Agent選定
* [ ] 接続テスト
* [ ] ラベル設定

### 4.3 Agent環境
[🔙 目次に戻る](#index)


* [ ] Maven/Gradle導入
* [ ] Docker導入（必要時）
* [ ] 作業ディレクトリ制限

**成果物**

* Agent構成図
* Agent設定表

---

## 5. Jenkins × GitLab 連携チェック
[🔙 目次に戻る](#index)


* [ ] GitLab Plugin設定
* [ ] SSHキー登録
* [ ] Webhook受信確認
* [ ] Push → Job起動確認

**成果物**

* 連携確認結果

---

## 6. Jenkins × Nexus 連携チェック
[🔙 目次に戻る](#index)


* [ ] Nexus Credentials登録
* [ ] Maven settings.xml設定
* [ ] 成果物アップロード確認
* [ ] バージョン整合性確認

**成果物**

* Artifactアップロード結果

---

## 7. Pipeline構築チェック
[🔙 目次に戻る](#index)


### 7.1 Jenkinsfile配置
[🔙 目次に戻る](#index)


* [ ] リポジトリに配置
* [ ] コードレビュー実施

### 7.2 CI Pipeline
[🔙 目次に戻る](#index)


* [ ] Checkout
* [ ] Build
* [ ] Test
* [ ] 静的解析（任意）

### 7.3 CD Pipeline
[🔙 目次に戻る](#index)


* [ ] 成果物取得（Nexus）
* [ ] 承認ステージ
* [ ] デプロイ

### 7.4 異常系確認
[🔙 目次に戻る](#index)


* [ ] ビルド失敗時停止
* [ ] テスト失敗時停止
* [ ] 承認拒否時停止

**成果物**

* Jenkinsfile
* Pipeline設計書

---

## 8. 運用・監査チェック
[🔙 目次に戻る](#index)


### 8.1 運用設計
[🔙 目次に戻る](#index)


* [ ] バックアップ設計
* [ ] Plugin更新ルール
* [ ] 障害対応手順
* [ ] 監視設計

### 8.2 監査対応
[🔙 目次に戻る](#index)


* [ ] 実行ログ保存
* [ ] 操作履歴取得
* [ ] 成果物証跡確認
* [ ] 承認記録保存

**成果物**

* 運用設計書
* 監査証跡一覧

---

## 9. 総合テスト
[🔙 目次に戻る](#index)


* [ ] Git Push → CI動作
* [ ] Artifact Nexus登録
* [ ] 承認 → デプロイ
* [ ] ロール別操作制限確認
* [ ] 障害時復旧テスト

**成果物**

* CI/CD総合試験報告書

---

### 付録：レビュー観点（監査用）
[🔙 目次に戻る](#index)


* 人手作業が残っていないか
* 本番直操作が可能になっていないか
* 認証情報の平文管理がないか
* 成果物の正本がNexusか

---

