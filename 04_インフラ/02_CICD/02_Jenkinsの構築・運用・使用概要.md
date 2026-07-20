# ◆ Jenkinsの構築・運用・使用概要
<!-- PROFILE_BADGE_START -->

[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?logo=github)](https://github.com/8alfalfa8)
[![Qiita](https://img.shields.io/badge/Qiita-Profile-55C500?logo=qiita&logoColor=white)](https://qiita.com/8alfalfa8)
[![Zenn](https://img.shields.io/badge/Zenn-Profile-3EA8FF?logo=zenn&logoColor=white)](https://zenn.dev/8alfalfa8)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/8alfalfa8)

<!-- PROFILE_BADGE_END -->


以下では **Linux環境における Jenkins の**「**構築・運用・使用**」を、
**実務（特にAWS／金融・公共レベル）で通用する粒度**で体系的に整理します。

---

## 1. Jenkinsとは（前提整理）

### 1.1 Jenkinsの役割

Jenkinsは **CI/CD（継続的インテグレーション／デリバリー）** を担う自動化サーバです。

主な役割：

* ソースコードの変更検知
* ビルド・テスト・静的解析の自動実行
* 成果物（Jar / War / Docker Image等）の生成
* デプロイ（手動承認含む）

### 1.2 Jenkinsが向いている用途

* オンプレ／LinuxサーバでのCI/CD
* GitHub / GitLab / Bitbucket連携
* Maven / Gradle / npm / Docker / Terraform等の自動実行
* 厳格な権限制御・監査ログが必要な環境

---

## 2. Jenkins構築（Linux環境）

### 2.1 構成方式の選択

| 方式                 | 特徴          | 実務向き   |
| ------------------ | ----------- | ------ |
| 単体構成               | Masterのみ    | 検証用    |
| Master + Agent     | 負荷分散・セキュリティ | **推奨** |
| Docker Jenkins     | 再現性高        | ◎      |
| Kubernetes Jenkins | 大規模         | △（運用難） |

👉 **金融・公共：Master + Agent構成**

---

### 2.2 Jenkinsインストール（RHEL / Amazon Linux）

#### 2.2.1 前提

* OS：RHEL / Amazon Linux 2
* Java：OpenJDK 17（LTS）

```bash
sudo yum install -y java-17-openjdk
```

#### 2.2.2 Jenkinsインストール

```bash
sudo wget -O /etc/yum.repos.d/jenkins.repo \
 https://pkg.jenkins.io/redhat-stable/jenkins.repo

sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo yum install -y jenkins
```

#### 2.2.3 起動

```bash
sudo systemctl enable jenkins
sudo systemctl start jenkins
```

* 管理画面
  `http://<host>:8080`

---

### 2.3 初期セットアップ

#### 2.3.1 初期パスワード取得

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

#### 2.3.2 初期プラグイン

* Git
* Pipeline
* Credentials Binding
* Role-based Authorization Strategy
* Blue Ocean（任意）

---

### 2.4 セキュリティ設定（重要）

#### 2.4.1 認証・認可

* 認証：

  * Jenkins内部
  * LDAP / AD（推奨）
* 認可：

  * Role-Based Strategy

| ロール       | 権限       |
| --------- | -------- |
| admin     | 全権限      |
| developer | Job作成・実行 |
| viewer    | 閲覧のみ     |

---

#### 2.4.2 HTTPS化

* ALB / NginxでTLS終端
* JenkinsはHTTPのみ

---

## 3. Jenkins Agent設計（運用要）

### 3.1 Agentの役割

* ビルド処理を分離
* Master負荷軽減
* 権限分離（重要）

### 3.2 Agent構築方法

| 方法           | 特徴        |
| ------------ | --------- |
| SSH Agent    | シンプル      |
| JNLP Agent   | Jenkins主導 |
| Docker Agent | 再現性高      |

👉 **実務推奨：Docker Agent**

---

### 3.3 Agentセキュリティ

* sudo不可
* Workspace隔離
* 秘密情報は Credentials 管理

---

## 4. Jenkins運用設計（最重要）

### 4.1 運用管理項目一覧

| 項目       | 内容           |
| -------- | ------------ |
| ユーザー管理   | 権限付与・棚卸      |
| Job管理    | 命名規則・責任者     |
| Plugin管理 | 更新計画         |
| Backup   | Jenkins Home |
| 障害対応     | 再起動・復旧       |
| 監査       | 操作ログ         |

---

### 4.2 バックアップ設計

#### 対象

* `/var/lib/jenkins`

#### 方法

* 定期tar
* S3 / NFS保存
* 世代管理

```bash
tar czf jenkins_backup_$(date +%F).tar.gz /var/lib/jenkins
```

---

### 4.3 Plugin運用ルール

* 本番環境では **自動更新禁止**
* 検証環境で事前検証
* 更新履歴管理

---

### 4.4 監視項目

| 監視         | 内容          |
| ---------- | ----------- |
| プロセス       | jenkins     |
| ディスク       | workspace肥大 |
| CPU/Memory | Agent負荷     |
| Queue      | Job滞留       |

---

## 5. Jenkinsの使用方法（実務）

### 5.1 Job種別

| 種別          | 用途       |
| ----------- | -------- |
| Freestyle   | 単純処理     |
| Pipeline    | **標準**   |
| Multibranch | Git Flow |

---

### 5.2 Jenkins Pipeline（Declarative）

```groovy
pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps {
        git 'https://example.com/repo.git'
      }
    }
    stage('Build') {
      steps {
        sh 'mvn clean package'
      }
    }
    stage('Test') {
      steps {
        sh 'mvn test'
      }
    }
  }
}
```

---

### 5.3 Credentials管理

| 種別                | 用途      |
| ----------------- | ------- |
| Username/Password | Git     |
| SSH Key           | Git     |
| Secret Text       | API Key |

Pipeline内：

```groovy
withCredentials([string(credentialsId: 'API_KEY', variable: 'KEY')]) {
  sh 'echo $KEY'
}
```

---

## 6. Jenkins × 他ツール連携

### 6.1 代表連携

* GitLab / GitHub（Webhook）
* Nexus（成果物管理）
* SonarQube（品質）
* Docker / ECR
* Terraform / Ansible

---

## 7. 金融・公共向け厳格運用ポイント

| 項目        | 対応              |
| --------- | --------------- |
| 権限最小化     | Role設計          |
| 直接操作禁止    | Pipeline化       |
| 操作履歴      | Audit Log       |
| 本番承認      | Manual Approval |
| インターネット遮断 | Proxy経由         |

---

## 8. 成果物一覧（ドキュメント）

* Jenkins構築手順書
* 運用設計書
* 権限設計書
* Pipeline設計書
* 障害対応手順書
* 監査対応資料

---

