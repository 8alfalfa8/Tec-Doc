<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. SonarQubeとは（実務視点）](#1-sonarqubeとは実務視点)
  - [1.1 目的](#11-目的)
- [2. 全体アーキテクチャ（Linux）](#2-全体アーキテクチャlinux)
- [3. SonarQube構築（Linux）](#3-sonarqube構築linux)
  - [3.1 前提条件](#31-前提条件)
    - [OS・リソース](#osリソース)
    - [必須ソフト](#必須ソフト)
  - [3.2 OS設定（重要）](#32-os設定重要)
    - [カーネルパラメータ（必須）](#カーネルパラメータ必須)
    - [ulimit設定](#ulimit設定)
  - [3.3 PostgreSQL構築](#33-postgresql構築)
    - [DB作成](#db作成)
  - [3.4 SonarQubeインストール](#34-sonarqubeインストール)
    - [設定（sonar.properties）](#設定sonarproperties)
  - [3.5 systemd登録](#35-systemd登録)
- [4. 初期設定・セキュリティ](#4-初期設定セキュリティ)
  - [4.1 初期ログイン](#41-初期ログイン)
  - [4.2 認証連携（推奨）](#42-認証連携推奨)
  - [4.3 権限モデル](#43-権限モデル)
- [5. SonarQubeの使い方（開発・CI）](#5-sonarqubeの使い方開発ci)
  - [5.1 プロジェクト作成](#51-プロジェクト作成)
  - [5.2 sonar-scanner（基本）](#52-sonar-scanner基本)
  - [5.3 Jenkins連携（例）](#53-jenkins連携例)
    - [Quality Gate 強制](#quality-gate-強制)
- [6. Quality Gate（最重要）](#6-quality-gate最重要)
  - [6.1 標準指標](#61-標準指標)
- [7. 運用設計（非常に重要）](#7-運用設計非常に重要)
  - [7.1 日次運用](#71-日次運用)
  - [7.2 バックアップ](#72-バックアップ)
    - [対象](#対象)
  - [7.3 アップグレード](#73-アップグレード)
- [8. よくある障害・対策](#8-よくある障害対策)
- [9. 金融・公共向けベストプラクティス](#9-金融公共向けベストプラクティス)
- [10. まとめ](#10-まとめ)
- [0. 基本情報（冒頭記載）](#0-基本情報冒頭記載)
- [1. 事前準備チェック](#1-事前準備チェック)
  - [1.1 インフラ・NW](#11-インフラnw)
  - [1.2 OS初期設定](#12-os初期設定)
- [2. OSチューニング（必須）](#2-osチューニング必須)
  - [2.1 kernelパラメータ](#21-kernelパラメータ)
  - [2.2 ulimit設定](#22-ulimit設定)
- [3. PostgreSQL構築](#3-postgresql構築)
  - [3.1 DBインストール](#31-dbインストール)
  - [3.2 DB・ユーザー作成](#32-dbユーザー作成)
- [4. Java環境構築](#4-java環境構築)
- [5. SonarQubeインストール](#5-sonarqubeインストール)
  - [5.1 ユーザー作成](#51-ユーザー作成)
  - [5.2 本体配置](#52-本体配置)
  - [5.3 設定ファイル編集](#53-設定ファイル編集)
- [6. systemd登録](#6-systemd登録)
- [7. 初期セットアップ](#7-初期セットアップ)
  - [7.1 初期ログイン](#71-初期ログイン)
  - [7.2 認証連携](#72-認証連携)
- [8. Jenkins / GitLab 連携設定](#8-jenkins-gitlab-連携設定)
  - [8.1 SonarQubeトークン](#81-sonarqubeトークン)
  - [8.2 Jenkins設定](#82-jenkins設定)
  - [8.3 Quality Gate連携](#83-quality-gate連携)
- [9. Quality Gate設計（重要）](#9-quality-gate設計重要)
- [10. 動作確認・試験](#10-動作確認試験)
- [11. 運用設計](#11-運用設計)
  - [11.1 バックアップ](#111-バックアップ)
  - [11.2 監視](#112-監視)
  - [11.3 権限管理](#113-権限管理)
- [12. 監査・セキュリティ対応](#12-監査セキュリティ対応)
- [補足（実務ノウハウ）](#補足実務ノウハウ)
<!-- TOC_END -->

# ◆ SonarQubeの構築・運用・使用概要

以下では **Linux環境における SonarQube の**「**構築・運用・使用**」を、
**金融・公共系／CI/CD前提／実務レベル**で体系的にご整理します。
（※ Jenkins / GitLab 連携を想定した標準構成）

---

## 1. SonarQubeとは（実務視点）
[🔙 目次に戻る](#index)


### 1.1 目的
[🔙 目次に戻る](#index)


SonarQubeは **静的コード解析（SAST）による品質・セキュリティの自動評価基盤** です。

| 観点     | 内容                   |
| ------ | -------------------- |
| 品質     | バグ、コードスメル、重複コード      |
| セキュリティ | 脆弱性、セキュリティホットスポット    |
| 保守性    | 技術的負債、可読性            |
| 統制     | Quality Gate による自動判定 |

👉 **「レビューの属人化排除」「品質基準の自動化」** が最大の価値です。

---

## 2. 全体アーキテクチャ（Linux）
[🔙 目次に戻る](#index)


```
[Developer]
   |
   | git push
   v
[GitLab]
   |
   | CI Job
   v
[Jenkins / GitLab Runner]
   |
   | sonar-scanner
   v
[SonarQube Server]
   |
   | JDBC
   v
[PostgreSQL]
```

---

## 3. SonarQube構築（Linux）
[🔙 目次に戻る](#index)


### 3.1 前提条件
[🔙 目次に戻る](#index)


#### OS・リソース
[🔙 目次に戻る](#index)


| 項目     | 推奨                           |
| ------ | ---------------------------- |
| OS     | RHEL / Rocky / Alma / Ubuntu |
| CPU    | 4 core 以上                    |
| Memory | 8GB（本番 16GB 推奨）              |
| Disk   | 50GB〜                        |

#### 必須ソフト
[🔙 目次に戻る](#index)


* Java 17（LTS）
* PostgreSQL 13+
* systemd
* unzip, curl

---

### 3.2 OS設定（重要）
[🔙 目次に戻る](#index)


#### カーネルパラメータ（必須）
[🔙 目次に戻る](#index)


```bash
sysctl -w vm.max_map_count=262144
sysctl -w fs.file-max=65536
```

永続化：

```bash
vi /etc/sysctl.conf
vm.max_map_count=262144
fs.file-max=65536
```

#### ulimit設定
[🔙 目次に戻る](#index)


```bash
vi /etc/security/limits.conf

sonar   -   nofile   65536
sonar   -   nproc    4096
```

---

### 3.3 PostgreSQL構築
[🔙 目次に戻る](#index)


```bash
dnf install -y postgresql-server
postgresql-setup --initdb
systemctl enable --now postgresql
```

#### DB作成
[🔙 目次に戻る](#index)


```sql
CREATE DATABASE sonarqube;
CREATE USER sonar WITH PASSWORD 'StrongPassword';
GRANT ALL PRIVILEGES ON DATABASE sonarqube TO sonar;
```

---

### 3.4 SonarQubeインストール
[🔙 目次に戻る](#index)


```bash
useradd sonar
cd /opt
wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-10.x.zip
unzip sonarqube-10.x.zip
chown -R sonar:sonar sonarqube
```

#### 設定（sonar.properties）
[🔙 目次に戻る](#index)


```properties
sonar.jdbc.url=jdbc:postgresql://localhost/sonarqube
sonar.jdbc.username=sonar
sonar.jdbc.password=StrongPassword

sonar.web.host=0.0.0.0
sonar.web.port=9000
```

---

### 3.5 systemd登録
[🔙 目次に戻る](#index)


```bash
vi /etc/systemd/system/sonarqube.service
```

```ini
[Unit]
Description=SonarQube service
After=network.target

[Service]
Type=forking
User=sonar
Group=sonar
ExecStart=/opt/sonarqube/bin/linux-x86-64/sonar.sh start
ExecStop=/opt/sonarqube/bin/linux-x86-64/sonar.sh stop
LimitNOFILE=65536
LimitNPROC=4096
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now sonarqube
```

---

## 4. 初期設定・セキュリティ
[🔙 目次に戻る](#index)


### 4.1 初期ログイン
[🔙 目次に戻る](#index)


* URL: `http://<host>:9000`
* 初期ID/PW: `admin / admin`
* **即変更必須**

---

### 4.2 認証連携（推奨）
[🔙 目次に戻る](#index)


| 方法           | 用途      |
| ------------ | ------- |
| GitLab OAuth | CI/CD連携 |
| LDAP / AD    | 企業利用    |
| SAML         | 大規模統合   |

---

### 4.3 権限モデル
[🔙 目次に戻る](#index)


| ロール           | 権限             |
| ------------- | -------------- |
| Admin         | サーバ設定          |
| Project Admin | Quality Gate管理 |
| Developer     | 結果閲覧           |
| CI User       | 解析実行専用         |

👉 **CI用トークンは個人利用禁止**

---

## 5. SonarQubeの使い方（開発・CI）
[🔙 目次に戻る](#index)


### 5.1 プロジェクト作成
[🔙 目次に戻る](#index)


* 手動作成
* GitLab連携自動作成（推奨）

---

### 5.2 sonar-scanner（基本）
[🔙 目次に戻る](#index)


```bash
sonar-scanner \
  -Dsonar.projectKey=my-app \
  -Dsonar.sources=src \
  -Dsonar.host.url=http://sonar:9000 \
  -Dsonar.login=TOKEN
```

---

### 5.3 Jenkins連携（例）
[🔙 目次に戻る](#index)


```groovy
stage('SonarQube Analysis') {
  steps {
    withSonarQubeEnv('sonarqube') {
      sh 'mvn sonar:sonar'
    }
  }
}
```

#### Quality Gate 強制
[🔙 目次に戻る](#index)


```groovy
stage('Quality Gate') {
  steps {
    timeout(time: 5, unit: 'MINUTES') {
      waitForQualityGate abortPipeline: true
    }
  }
}
```

---

## 6. Quality Gate（最重要）
[🔙 目次に戻る](#index)


### 6.1 標準指標
[🔙 目次に戻る](#index)


| 指標         | 例     |
| ---------- | ----- |
| 新規バグ       | 0     |
| 新規脆弱性      | 0     |
| 新規コードカバレッジ | ≥ 80% |
| 新規重複率      | ≤ 3%  |

👉 **「既存資産は問わない」「新規のみ厳格」が鉄則**

---

## 7. 運用設計（非常に重要）
[🔙 目次に戻る](#index)


### 7.1 日次運用
[🔙 目次に戻る](#index)


| 項目    | 内容            |
| ----- | ------------- |
| 死活監視  | systemd / ポート |
| ディスク  | /opt / data   |
| ジョブ失敗 | CIログ確認        |

---

### 7.2 バックアップ
[🔙 目次に戻る](#index)


#### 対象
[🔙 目次に戻る](#index)


* PostgreSQL DB
* `$SONARQUBE_HOME/data`
* `$SONARQUBE_HOME/extensions`

```bash
pg_dump sonarqube > sonarqube.sql
tar czf sonar_data.tar.gz data extensions
```

---

### 7.3 アップグレード
[🔙 目次に戻る](#index)


| 手順       | 注意   |
| -------- | ---- |
| DBバックアップ | 必須   |
| LTS利用    | 推奨   |
| プラグイン互換  | 事前確認 |
| ダウンタイム   | あり   |

---

## 8. よくある障害・対策
[🔙 目次に戻る](#index)


| 事象      | 原因                 | 対策         |
| ------- | ------------------ | ---------- |
| 起動しない   | vm.max_map_count不足 | sysctl修正   |
| 解析失敗    | メモリ不足              | -Xmx増加     |
| CI遅延    | 同時解析多              | Executor制御 |
| Gate未通過 | ルール過剰              | Gate調整     |

---

## 9. 金融・公共向けベストプラクティス
[🔙 目次に戻る](#index)


* LTS版のみ使用
* Quality Gate 変更は申請制
* 管理者操作は証跡必須
* CIトークンの定期ローテーション
* OSSライセンス管理（併用推奨）

---

## 10. まとめ
[🔙 目次に戻る](#index)


SonarQubeは
**「ツール」ではなく「品質統制基盤」**です。

* 構築：OS・DB・Javaチューニングが肝
* 使用：CI/CDとQuality Gateが本体
* 運用：ルール・権限・証跡管理が最重要

---


# ◆ SonarQube 構築チェックリスト（作業手順書）

**（Jenkins × GitLab 連携・Linux環境）**

以下は
**Jenkins / GitLab 連携を前提とした SonarQube 構築チェックリスト**（**作業手順書**）です。
**金融・公共案件／監査対応／CI/CD標準**を想定し、「**作業 → 確認 → 成果物**」が明確になる構成にしています。

---

## 0. 基本情報（冒頭記載）
[🔙 目次に戻る](#index)


| 項目                | 内容                    |
| ----------------- | --------------------- |
| 対象システム            | SonarQube             |
| OS                | RHEL / Rocky / Ubuntu |
| SonarQube Version | LTS（例：10.x LTS）       |
| Java              | OpenJDK 17            |
| DB                | PostgreSQL 13+        |
| CI                | Jenkins / GitLab CI   |
| 認証                | GitLab OAuth / LDAP   |

---

## 1. 事前準備チェック
[🔙 目次に戻る](#index)


### 1.1 インフラ・NW
[🔙 目次に戻る](#index)


☐ サーバ確保（CPU 4core / Memory 8GB以上）
☐ 固定IP / DNS 登録
☐ Jenkins / GitLab Runner から疎通可能
☐ FW / SG：TCP 9000 許可
☐ NTP 同期設定

**成果物**

* サーバ構成表
* ネットワーク構成図

---

### 1.2 OS初期設定
[🔙 目次に戻る](#index)


☐ OS最新化
☐ 必須パッケージ導入（unzip, curl, wget）
☐ swap 設定確認（推奨 ON）

```bash
dnf update -y
dnf install -y unzip wget curl
```

**成果物**

* OS設定チェックシート

---

## 2. OSチューニング（必須）
[🔙 目次に戻る](#index)


### 2.1 kernelパラメータ
[🔙 目次に戻る](#index)


☐ vm.max_map_count 設定
☐ fs.file-max 設定

```bash
sysctl -w vm.max_map_count=262144
sysctl -w fs.file-max=65536
```

永続化確認

```bash
sysctl -a | grep vm.max_map_count
```

---

### 2.2 ulimit設定
[🔙 目次に戻る](#index)


☐ sonarユーザー用制限設定

```bash
vi /etc/security/limits.conf

sonar  -  nofile  65536
sonar  -  nproc   4096
```

**成果物**

* OSチューニング設定一覧

---

## 3. PostgreSQL構築
[🔙 目次に戻る](#index)


### 3.1 DBインストール
[🔙 目次に戻る](#index)


☐ PostgreSQL インストール
☐ 自動起動設定

```bash
dnf install -y postgresql-server
postgresql-setup --initdb
systemctl enable --now postgresql
```

---

### 3.2 DB・ユーザー作成
[🔙 目次に戻る](#index)


☐ DB作成
☐ 専用ユーザー作成
☐ パスワード管理ルール遵守

```sql
CREATE DATABASE sonarqube;
CREATE USER sonar WITH PASSWORD '********';
GRANT ALL PRIVILEGES ON DATABASE sonarqube TO sonar;
```

**成果物**

* DB接続情報管理表（秘匿）

---

## 4. Java環境構築
[🔙 目次に戻る](#index)


☐ OpenJDK 17 インストール
☐ JAVA_HOME 設定確認

```bash
dnf install -y java-17-openjdk
java -version
```

**成果物**

* ミドルウェア構成表

---

## 5. SonarQubeインストール
[🔙 目次に戻る](#index)


### 5.1 ユーザー作成
[🔙 目次に戻る](#index)


☐ sonar 専用ユーザー作成

```bash
useradd sonar
```

---

### 5.2 本体配置
[🔙 目次に戻る](#index)


☐ SonarQube ダウンロード
☐ /opt 配置
☐ 権限設定

```bash
cd /opt
wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-10.x.zip
unzip sonarqube-10.x.zip
chown -R sonar:sonar sonarqube
```

---

### 5.3 設定ファイル編集
[🔙 目次に戻る](#index)


☐ DB接続設定
☐ Listenアドレス確認

```properties
sonar.jdbc.url=jdbc:postgresql://localhost/sonarqube
sonar.jdbc.username=sonar
sonar.jdbc.password=********

sonar.web.host=0.0.0.0
sonar.web.port=9000
```

**成果物**

* SonarQube設定ファイル控え

---

## 6. systemd登録
[🔙 目次に戻る](#index)


☐ サービス定義作成
☐ 自動起動設定

```ini
[Service]
User=sonar
ExecStart=/opt/sonarqube/bin/linux-x86-64/sonar.sh start
ExecStop=/opt/sonarqube/bin/linux-x86-64/sonar.sh stop
```

```bash
systemctl daemon-reload
systemctl enable --now sonarqube
```

☐ 起動確認（port 9000）

**成果物**

* サービス定義ファイル

---

## 7. 初期セットアップ
[🔙 目次に戻る](#index)


### 7.1 初期ログイン
[🔙 目次に戻る](#index)


☐ 管理者PW変更
☐ 言語・時刻設定確認

---

### 7.2 認証連携
[🔙 目次に戻る](#index)


☐ GitLab OAuth設定
☐ LDAP連携（任意）

**成果物**

* 認証連携設定仕様書

---

## 8. Jenkins / GitLab 連携設定
[🔙 目次に戻る](#index)


### 8.1 SonarQubeトークン
[🔙 目次に戻る](#index)


☐ CI専用トークン作成
☐ 個人トークン禁止

---

### 8.2 Jenkins設定
[🔙 目次に戻る](#index)


☐ SonarQube Server登録
☐ SonarScanner設定

```groovy
withSonarQubeEnv('sonarqube') {
  sh 'mvn sonar:sonar'
}
```

---

### 8.3 Quality Gate連携
[🔙 目次に戻る](#index)


☐ Gate判定をPipelineで強制

```groovy
waitForQualityGate abortPipeline: true
```

**成果物**

* Jenkinsfileテンプレート
* CI連携設計書

---

## 9. Quality Gate設計（重要）
[🔙 目次に戻る](#index)


☐ 新規コードのみ判定
☐ バグ・脆弱性 0
☐ カバレッジ基準定義

| 指標      | 基準    |
| ------- | ----- |
| 新規バグ    | 0     |
| 新規脆弱性   | 0     |
| 新規カバレッジ | ≥ 80% |

**成果物**

* Quality Gate定義書

---

## 10. 動作確認・試験
[🔙 目次に戻る](#index)


☐ 解析成功確認
☐ Gate通過/失敗確認
☐ Jenkinsビルド連動確認

**成果物**

* 試験結果報告書

---

## 11. 運用設計
[🔙 目次に戻る](#index)


### 11.1 バックアップ
[🔙 目次に戻る](#index)


☐ DBバックアップ設計
☐ data/extensions 退避

---

### 11.2 監視
[🔙 目次に戻る](#index)


☐ プロセス監視
☐ ディスク監視
☐ ジョブ失敗検知

---

### 11.3 権限管理
[🔙 目次に戻る](#index)


☐ Admin最小化
☐ Gate変更は申請制

**成果物**

* 運用設計書
* 障害対応Runbook

---

## 12. 監査・セキュリティ対応
[🔙 目次に戻る](#index)


☐ 管理操作ログ確認
☐ トークン棚卸
☐ ルール変更履歴管理

**成果物**

* 監査対応資料

---

## 補足（実務ノウハウ）
[🔙 目次に戻る](#index)


* **最初から厳しすぎるGateはNG**
* 既存資産は評価対象外
* CIトークンは半年ローテーション
* LTS以外は使わない

---
