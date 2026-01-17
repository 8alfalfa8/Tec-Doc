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

