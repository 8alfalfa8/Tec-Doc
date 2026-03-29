<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. Jenkinsとは（前提整理）](#1-jenkinsとは前提整理)
  - [1.1 Jenkinsの役割](#11-jenkinsの役割)
  - [1.2 Jenkinsが向いている用途](#12-jenkinsが向いている用途)
- [2. Jenkins構築（Linux環境）](#2-jenkins構築linux環境)
  - [2.1 構成方式の選択](#21-構成方式の選択)
  - [2.2 Jenkinsインストール（RHEL / Amazon Linux）](#22-jenkinsインストールrhel-amazon-linux)
    - [2.2.1 前提](#221-前提)
    - [2.2.2 Jenkinsインストール](#222-jenkinsインストール)
    - [2.2.3 起動](#223-起動)
  - [2.3 初期セットアップ](#23-初期セットアップ)
    - [2.3.1 初期パスワード取得](#231-初期パスワード取得)
    - [2.3.2 初期プラグイン](#232-初期プラグイン)
  - [2.4 セキュリティ設定（重要）](#24-セキュリティ設定重要)
    - [2.4.1 認証・認可](#241-認証認可)
    - [2.4.2 HTTPS化](#242-https化)
- [3. Jenkins Agent設計（運用要）](#3-jenkins-agent設計運用要)
  - [3.1 Agentの役割](#31-agentの役割)
  - [3.2 Agent構築方法](#32-agent構築方法)
  - [3.3 Agentセキュリティ](#33-agentセキュリティ)
- [4. Jenkins運用設計（最重要）](#4-jenkins運用設計最重要)
  - [4.1 運用管理項目一覧](#41-運用管理項目一覧)
  - [4.2 バックアップ設計](#42-バックアップ設計)
    - [対象](#対象)
    - [方法](#方法)
  - [4.3 Plugin運用ルール](#43-plugin運用ルール)
  - [4.4 監視項目](#44-監視項目)
- [5. Jenkinsの使用方法（実務）](#5-jenkinsの使用方法実務)
  - [5.1 Job種別](#51-job種別)
  - [5.2 Jenkins Pipeline（Declarative）](#52-jenkins-pipelinedeclarative)
  - [5.3 Credentials管理](#53-credentials管理)
- [6. Jenkins × 他ツール連携](#6-jenkins-他ツール連携)
  - [6.1 代表連携](#61-代表連携)
- [7. 金融・公共向け厳格運用ポイント](#7-金融公共向け厳格運用ポイント)
- [8. 成果物一覧（ドキュメント）](#8-成果物一覧ドキュメント)
<!-- TOC_END -->

# ◆ Jenkinsの構築・運用・使用概要

以下では **Linux環境における Jenkins の**「**構築・運用・使用**」を、
**実務（特にAWS／金融・公共レベル）で通用する粒度**で体系的に整理します。

---

## 1. Jenkinsとは（前提整理）
[🔙 目次に戻る](#index)


### 1.1 Jenkinsの役割
[🔙 目次に戻る](#index)


Jenkinsは **CI/CD（継続的インテグレーション／デリバリー）** を担う自動化サーバです。

主な役割：

* ソースコードの変更検知
* ビルド・テスト・静的解析の自動実行
* 成果物（Jar / War / Docker Image等）の生成
* デプロイ（手動承認含む）

[🔙 目次に戻る](#index)


### 1.2 Jenkinsが向いている用途
[🔙 目次に戻る](#index)


* オンプレ／LinuxサーバでのCI/CD
* GitHub / GitLab / Bitbucket連携
* Maven / Gradle / npm / Docker / Terraform等の自動実行
* 厳格な権限制御・監査ログが必要な環境

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 2. Jenkins構築（Linux環境）
[🔙 目次に戻る](#index)


### 2.1 構成方式の選択
[🔙 目次に戻る](#index)


| 方式                 | 特徴          | 実務向き   |
| ------------------ | ----------- | ------ |
| 単体構成               | Masterのみ    | 検証用    |
| Master + Agent     | 負荷分散・セキュリティ | **推奨** |
| Docker Jenkins     | 再現性高        | ◎      |
| Kubernetes Jenkins | 大規模         | △（運用難） |

👉 **金融・公共：Master + Agent構成**

---

[🔙 目次に戻る](#index)


### 2.2 Jenkinsインストール（RHEL / Amazon Linux）
[🔙 目次に戻る](#index)


#### 2.2.1 前提
[🔙 目次に戻る](#index)


* OS：RHEL / Amazon Linux 2
* Java：OpenJDK 17（LTS）

```bash
sudo yum install -y java-17-openjdk
```

[🔙 目次に戻る](#index)


#### 2.2.2 Jenkinsインストール
[🔙 目次に戻る](#index)


```bash
sudo wget -O /etc/yum.repos.d/jenkins.repo \
 https://pkg.jenkins.io/redhat-stable/jenkins.repo

sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo yum install -y jenkins
```

[🔙 目次に戻る](#index)


#### 2.2.3 起動
[🔙 目次に戻る](#index)


```bash
sudo systemctl enable jenkins
sudo systemctl start jenkins
```

[🔙 目次に戻る](#index)


* 管理画面
  `http://<host>:8080`

---

[🔙 目次に戻る](#index)


### 2.3 初期セットアップ
[🔙 目次に戻る](#index)


#### 2.3.1 初期パスワード取得
[🔙 目次に戻る](#index)


```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

[🔙 目次に戻る](#index)


#### 2.3.2 初期プラグイン
[🔙 目次に戻る](#index)


* Git
* Pipeline
* Credentials Binding
* Role-based Authorization Strategy
* Blue Ocean（任意）

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 2.4 セキュリティ設定（重要）
[🔙 目次に戻る](#index)


#### 2.4.1 認証・認可
[🔙 目次に戻る](#index)


* 認証：

[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


#### 2.4.2 HTTPS化
[🔙 目次に戻る](#index)


* ALB / NginxでTLS終端
* JenkinsはHTTPのみ

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 3. Jenkins Agent設計（運用要）
[🔙 目次に戻る](#index)


### 3.1 Agentの役割
[🔙 目次に戻る](#index)


* ビルド処理を分離
* Master負荷軽減
* 権限分離（重要）

[🔙 目次に戻る](#index)


### 3.2 Agent構築方法
[🔙 目次に戻る](#index)


| 方法           | 特徴        |
| ------------ | --------- |
| SSH Agent    | シンプル      |
| JNLP Agent   | Jenkins主導 |
| Docker Agent | 再現性高      |

👉 **実務推奨：Docker Agent**

---

[🔙 目次に戻る](#index)


### 3.3 Agentセキュリティ
[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



* sudo不可
* Workspace隔離
* 秘密情報は Credentials 管理

---

[🔙 目次に戻る](#index)


## 4. Jenkins運用設計（最重要）
[🔙 目次に戻る](#index)


### 4.1 運用管理項目一覧
[🔙 目次に戻る](#index)


| 項目       | 内容           |
| -------- | ------------ |
| ユーザー管理   | 権限付与・棚卸      |
| Job管理    | 命名規則・責任者     |
| Plugin管理 | 更新計画         |
| Backup   | Jenkins Home |
| 障害対応     | 再起動・復旧       |
| 監査       | 操作ログ         |

---

[🔙 目次に戻る](#index)


### 4.2 バックアップ設計
[🔙 目次に戻る](#index)


#### 対象
[🔙 目次に戻る](#index)


* `/var/lib/jenkins`

[🔙 目次に戻る](#index)


#### 方法
[🔙 目次に戻る](#index)


* 定期tar
* S3 / NFS保存
* 世代管理

```bash
tar czf jenkins_backup_$(date +%F).tar.gz /var/lib/jenkins
```

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 4.3 Plugin運用ルール
[🔙 目次に戻る](#index)


* 本番環境では **自動更新禁止**
* 検証環境で事前検証
* 更新履歴管理

---

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)



### 4.4 監視項目
[🔙 目次に戻る](#index)


| 監視         | 内容          |
| ---------- | ----------- |
| プロセス       | jenkins     |
| ディスク       | workspace肥大 |
| CPU/Memory | Agent負荷     |
| Queue      | Job滞留       |

---

[🔙 目次に戻る](#index)


## 5. Jenkinsの使用方法（実務）
[🔙 目次に戻る](#index)


### 5.1 Job種別
[🔙 目次に戻る](#index)


| 種別          | 用途       |
| ----------- | -------- |
| Freestyle   | 単純処理     |
| Pipeline    | **標準**   |
| Multibranch | Git Flow |

---

[🔙 目次に戻る](#index)


### 5.2 Jenkins Pipeline（Declarative）
[🔙 目次に戻る](#index)


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

[🔙 目次に戻る](#index)


### 5.3 Credentials管理
[🔙 目次に戻る](#index)


| 種別                | 用途      |
| ----------------- | ------- |
| Username/Password | Git     |
| SSH Key           | Git     |
| Secret Text       | API Key |

Pipeline内：

```groovy
withCredentials([string(credentialsId: 'API_KEY', variable: 'KEY')]) {

[🔙 目次に戻る](#index)

  sh 'echo $KEY'
}
```

---

[🔙 目次に戻る](#index)


## 6. Jenkins × 他ツール連携
[🔙 目次に戻る](#index)


### 6.1 代表連携
[🔙 目次に戻る](#index)


* GitLab / GitHub（Webhook）
* Nexus（成果物管理）
* SonarQube（品質）
* Docker / ECR
* Terraform / Ansible

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 7. 金融・公共向け厳格運用ポイント
[🔙 目次に戻る](#index)


| 項目        | 対応              |
| --------- | --------------- |
| 権限最小化     | Role設計          |
| 直接操作禁止    | Pipeline化       |
| 操作履歴      | Audit Log       |
| 本番承認      | Manual Approval |
| インターネット遮断 | Proxy経由         |

---

[🔙 目次に戻る](#index)


## 8. 成果物一覧（ドキュメント）
[🔙 目次に戻る](#index)


* Jenkins構築手順書
* 運用設計書
* 権限設計書
* Pipeline設計書
* 障害対応手順書
* 監査対応資料

---

[🔙 目次に戻る](#index)


