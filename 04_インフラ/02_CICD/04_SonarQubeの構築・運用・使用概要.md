# ◆ SonarQubeの構築・運用・使用概要

以下では **Linux環境における SonarQube の**「**構築・運用・使用**」を、
**金融・公共系／CI/CD前提／実務レベル**で体系的にご説明します。
（※ Jenkins / GitLab 連携を想定した標準構成）

---

## 1. SonarQubeとは（実務視点）

### 1.1 目的

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

### 3.1 前提条件

#### OS・リソース

| 項目     | 推奨                           |
| ------ | ---------------------------- |
| OS     | RHEL / Rocky / Alma / Ubuntu |
| CPU    | 4 core 以上                    |
| Memory | 8GB（本番 16GB 推奨）              |
| Disk   | 50GB〜                        |

#### 必須ソフト

* Java 17（LTS）
* PostgreSQL 13+
* systemd
* unzip, curl

---

### 3.2 OS設定（重要）

#### カーネルパラメータ（必須）

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

```bash
vi /etc/security/limits.conf

sonar   -   nofile   65536
sonar   -   nproc    4096
```

---

### 3.3 PostgreSQL構築

```bash
dnf install -y postgresql-server
postgresql-setup --initdb
systemctl enable --now postgresql
```

#### DB作成

```sql
CREATE DATABASE sonarqube;
CREATE USER sonar WITH PASSWORD 'StrongPassword';
GRANT ALL PRIVILEGES ON DATABASE sonarqube TO sonar;
```

---

### 3.4 SonarQubeインストール

```bash
useradd sonar
cd /opt
wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-10.x.zip
unzip sonarqube-10.x.zip
chown -R sonar:sonar sonarqube
```

#### 設定（sonar.properties）

```properties
sonar.jdbc.url=jdbc:postgresql://localhost/sonarqube
sonar.jdbc.username=sonar
sonar.jdbc.password=StrongPassword

sonar.web.host=0.0.0.0
sonar.web.port=9000
```

---

### 3.5 systemd登録

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

### 4.1 初期ログイン

* URL: `http://<host>:9000`
* 初期ID/PW: `admin / admin`
* **即変更必須**

---

### 4.2 認証連携（推奨）

| 方法           | 用途      |
| ------------ | ------- |
| GitLab OAuth | CI/CD連携 |
| LDAP / AD    | 企業利用    |
| SAML         | 大規模統合   |

---

### 4.3 権限モデル

| ロール           | 権限             |
| ------------- | -------------- |
| Admin         | サーバ設定          |
| Project Admin | Quality Gate管理 |
| Developer     | 結果閲覧           |
| CI User       | 解析実行専用         |

👉 **CI用トークンは個人利用禁止**

---

## 5. SonarQubeの使い方（開発・CI）

### 5.1 プロジェクト作成

* 手動作成
* GitLab連携自動作成（推奨）

---

### 5.2 sonar-scanner（基本）

```bash
sonar-scanner \
  -Dsonar.projectKey=my-app \
  -Dsonar.sources=src \
  -Dsonar.host.url=http://sonar:9000 \
  -Dsonar.login=TOKEN
```

---

### 5.3 Jenkins連携（例）

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

### 6.1 標準指標

| 指標         | 例     |
| ---------- | ----- |
| 新規バグ       | 0     |
| 新規脆弱性      | 0     |
| 新規コードカバレッジ | ≥ 80% |
| 新規重複率      | ≤ 3%  |

👉 **「既存資産は問わない」「新規のみ厳格」が鉄則**

---

## 7. 運用設計（非常に重要）

### 7.1 日次運用

| 項目    | 内容            |
| ----- | ------------- |
| 死活監視  | systemd / ポート |
| ディスク  | /opt / data   |
| ジョブ失敗 | CIログ確認        |

---

### 7.2 バックアップ

#### 対象

* PostgreSQL DB
* `$SONARQUBE_HOME/data`
* `$SONARQUBE_HOME/extensions`

```bash
pg_dump sonarqube > sonarqube.sql
tar czf sonar_data.tar.gz data extensions
```

---

### 7.3 アップグレード

| 手順       | 注意   |
| -------- | ---- |
| DBバックアップ | 必須   |
| LTS利用    | 推奨   |
| プラグイン互換  | 事前確認 |
| ダウンタイム   | あり   |

---

## 8. よくある障害・対策

| 事象      | 原因                 | 対策         |
| ------- | ------------------ | ---------- |
| 起動しない   | vm.max_map_count不足 | sysctl修正   |
| 解析失敗    | メモリ不足              | -Xmx増加     |
| CI遅延    | 同時解析多              | Executor制御 |
| Gate未通過 | ルール過剰              | Gate調整     |

---

## 9. 金融・公共向けベストプラクティス

* LTS版のみ使用
* Quality Gate 変更は申請制
* 管理者操作は証跡必須
* CIトークンの定期ローテーション
* OSSライセンス管理（併用推奨）

---

## 10. まとめ

SonarQubeは
**「ツール」ではなく「品質統制基盤」**です。

* 構築：OS・DB・Javaチューニングが肝
* 使用：CI/CDとQuality Gateが本体
* 運用：ルール・権限・証跡管理が最重要

---

