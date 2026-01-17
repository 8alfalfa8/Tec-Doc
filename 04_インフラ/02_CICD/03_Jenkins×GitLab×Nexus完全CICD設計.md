# ◆ Jenkins × GitLab × Nexus 完全CI/CD設計

以下は **Jenkins × GitLab × Nexus による**「**完全CI/CD設計**」です。
**金融・公共レベル**（**監査・権限制御・分離設計**）を前提に、
**構成／処理フロー／権限設計／Pipeline例／運用ルール**まで落とします。

---

## 1. 全体像（目的と思想）

### 1.1 目的

* **ソース～成果物までの完全自動化**
* 人手作業を排除し **再現性・証跡・統制** を確保
* Jenkinsを **制御点（Control Plane）** とする

### 1.2 基本思想（重要）

| 項目   | 方針                          |
| ---- | --------------------------- |
| 人手操作 | 本番は原則禁止                     |
| 認証情報 | Jenkins Credentials 一元管理    |
| 成果物  | **Nexusのみが正**               |
| デプロイ | Pipeline経由のみ                |
| 監査   | Git / Jenkins / Nexus で三点証跡 |

---

## 2. 全体アーキテクチャ

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

### 3.1 GitLab 設計

#### 3.1.1 リポジトリ構成（例）

```
repo/
 ├ src/
 ├ pom.xml
 ├ Jenkinsfile
 └ docs/
```

#### 3.1.2 ブランチ戦略（厳格）

| ブランチ      | 用途   |
| --------- | ---- |
| main      | 本番   |
| release/* | リリース |
| develop   | 統合   |
| feature/* | 開発   |

#### 3.1.3 権限

| ロール        | 権限     |
| ---------- | ------ |
| Maintainer | Merge可 |
| Developer  | Push可  |
| Reporter   | Read   |

* **main直push禁止**
* MR必須＋レビュー必須

---

### 3.2 Jenkins 設計

#### 3.2.1 Job構成

| Job種別                | 内容    |
| -------------------- | ----- |
| Multibranch Pipeline | Git連動 |
| Deploy Pipeline      | 環境別   |

#### 3.2.2 Credentials設計

| 種別          | 用途              |
| ----------- | --------------- |
| Git SSH Key | GitLab          |
| Nexus User  | Artifact Upload |
| Deploy Key  | 本番              |

**Pipeline内ハードコード禁止**

---

### 3.3 Nexus 設計

#### 3.3.1 リポジトリ種別

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

| ロール       | 権限    |
| --------- | ----- |
| ci-upload | write |
| developer | read  |
| admin     | all   |

**削除権限は管理者のみ**

---

## 4. CI/CD処理フロー（詳細）

### 4.1 CI（ビルド・テスト）

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

9. Jenkins → NexusへUpload
10. バージョン固定
11. チェックサム生成
12. 監査ログ保存

---

### 4.3 CD（デプロイ）

13. リリース承認（Manual）
14. 承認後デプロイ実行
15. 対象環境へ展開
16. デプロイ結果記録

---

## 5. Jenkinsfile（実務用サンプル）

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

### 6.1 運用ルール

| 項目        | ルール       |
| --------- | --------- |
| Jenkins操作 | 管理者のみ     |
| 本番実行      | 承認必須      |
| 成果物       | Nexus以外禁止 |
| ロール       | 定期棚卸      |

---

### 6.2 障害対応

* Jenkins停止 → Agent切替
* Nexus障害 → Artifact復旧
* GitLab障害 → CI停止許容

---

## 7. 監査・証跡設計

| 証跡    | 保存先           |
| ----- | ------------- |
| ソース変更 | GitLab        |
| 実行履歴  | Jenkins       |
| 成果物   | Nexus         |
| 承認    | Jenkins Input |

---

## 8. 成果物一覧（設計ドキュメント）

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

### チェックリスト構築手順書（Linux）

---

## 0. 事前準備（共通）

#### 0.1 環境情報整理

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

### 1.1 GitLabインストール

* [ ] GitLabサーバ構築
* [ ] HTTPS有効化
* [ ] 管理者初期設定

### 1.2 ユーザー・権限

* [ ] 管理者アカウント作成
* [ ] Developer / Maintainer 作成
* [ ] 外部認証（LDAP/AD）設定（任意）

### 1.3 リポジトリ設計

* [ ] プロジェクト作成
* [ ] ブランチ戦略設定
* [ ] main直Push禁止
* [ ] MR必須設定
* [ ] Review必須設定

### 1.4 Webhook設定

* [ ] Jenkins向けWebhook登録
* [ ] イベント（Push / Merge）有効化
* [ ] 接続テスト実施

**成果物**

* GitLab設定シート
* 権限設計書

---

## 2. Nexus 構築チェックリスト

### 2.1 Nexusインストール

* [ ] Nexusインストール（OSS / Pro）
* [ ] HTTPS設定
* [ ] 管理者初期設定

## 2.2 リポジトリ作成

* [ ] hosted（releases）
* [ ] hosted（snapshots）
* [ ] proxy（maven central）
* [ ] group（maven-public）

### 2.3 権限設計

* [ ] ci-upload ロール作成
* [ ] read-only ロール作成
* [ ] adminロール確認
* [ ] 削除権限制限

### 2.4 保管ポリシー

* [ ] バージョニングルール
* [ ] スナップショット世代管理
* [ ] クリーンアップポリシー

**成果物**

* Nexusリポジトリ定義書
* 権限一覧表

---

## 3. Jenkins 構築チェックリスト

### 3.1 Jenkinsインストール

* [ ] Java（LTS）インストール
* [ ] Jenkinsインストール
* [ ] サービス起動確認
* [ ] 管理画面接続確認

### 3.2 初期設定

* [ ] 初期Admin設定
* [ ] 不要プラグイン無効化
* [ ] 必須プラグイン導入

  * [ ] Git
  * [ ] Pipeline
  * [ ] Credentials
  * [ ] Role Strategy

### 3.3 認証・認可

* [ ] 認証方式設定（内部 / LDAP）
* [ ] ロール作成（admin/dev/view）
* [ ] 権限割当

### 3.4 セキュリティ

* [ ] HTTPS（ALB/Nginx）
* [ ] CLI無効化
* [ ] Script Console制限

**成果物**

* Jenkins設定仕様書
* 権限設計書

---

## 4. Jenkins Agent 構築チェックリスト

### 4.1 Agent設計

* [ ] Master/Agent分離
* [ ] Agent実行ユーザー作成
* [ ] sudo権限なし確認

### 4.2 Agent接続

* [ ] SSH/JNLP/Docker Agent選定
* [ ] 接続テスト
* [ ] ラベル設定

### 4.3 Agent環境

* [ ] Maven/Gradle導入
* [ ] Docker導入（必要時）
* [ ] 作業ディレクトリ制限

**成果物**

* Agent構成図
* Agent設定表

---

## 5. Jenkins × GitLab 連携チェック

* [ ] GitLab Plugin設定
* [ ] SSHキー登録
* [ ] Webhook受信確認
* [ ] Push → Job起動確認

**成果物**

* 連携確認結果

---

## 6. Jenkins × Nexus 連携チェック

* [ ] Nexus Credentials登録
* [ ] Maven settings.xml設定
* [ ] 成果物アップロード確認
* [ ] バージョン整合性確認

**成果物**

* Artifactアップロード結果

---

## 7. Pipeline構築チェック

### 7.1 Jenkinsfile配置

* [ ] リポジトリに配置
* [ ] コードレビュー実施

### 7.2 CI Pipeline

* [ ] Checkout
* [ ] Build
* [ ] Test
* [ ] 静的解析（任意）

### 7.3 CD Pipeline

* [ ] 成果物取得（Nexus）
* [ ] 承認ステージ
* [ ] デプロイ

### 7.4 異常系確認

* [ ] ビルド失敗時停止
* [ ] テスト失敗時停止
* [ ] 承認拒否時停止

**成果物**

* Jenkinsfile
* Pipeline設計書

---

## 8. 運用・監査チェック

### 8.1 運用設計

* [ ] バックアップ設計
* [ ] Plugin更新ルール
* [ ] 障害対応手順
* [ ] 監視設計

### 8.2 監査対応

* [ ] 実行ログ保存
* [ ] 操作履歴取得
* [ ] 成果物証跡確認
* [ ] 承認記録保存

**成果物**

* 運用設計書
* 監査証跡一覧

---

## 9. 総合テスト

* [ ] Git Push → CI動作
* [ ] Artifact Nexus登録
* [ ] 承認 → デプロイ
* [ ] ロール別操作制限確認
* [ ] 障害時復旧テスト

**成果物**

* CI/CD総合試験報告書

---

### 付録：レビュー観点（監査用）

* 人手作業が残っていないか
* 本番直操作が可能になっていないか
* 認証情報の平文管理がないか
* 成果物の正本がNexusか

---

