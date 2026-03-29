<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. 全体像（GitLab × Nexus の役割分担）](#1-全体像gitlab-nexus-の役割分担)
  - [1.1 役割整理](#11-役割整理)
    - [なぜNexusが必要か？](#なぜnexusが必要か)
  - [1.2 GitLab × Nexus役割分担（重要）](#12-gitlab-nexus役割分担重要)
- [2. Linux環境での構築設計（共通前提）](#2-linux環境での構築設計共通前提)
  - [2.1 推奨構成例](#21-推奨構成例)
    - [サーバ分離（推奨）](#サーバ分離推奨)
    - [GitLab推奨スペック（目安）](#gitlab推奨スペック目安)
    - [Nexus推奨スペック（目安）](#nexus推奨スペック目安)
  - [2.2 Linux共通前提](#22-linux共通前提)
- [3. GitLab 構築（Linux）](#3-gitlab-構築linux)
  - [3.1 GitLabインストール（Omnibus）](#31-gitlabインストールomnibus)
    - [設定ファイル](#設定ファイル)
      - [重要設定例](#重要設定例)
    - [反映](#反映)
  - [3.2 GitLab Runner 構築](#32-gitlab-runner-構築)
    - [Runner登録](#runner登録)
- [4. Nexus Repository 構築（Linux）](#4-nexus-repository-構築linux)
  - [4.1 インストール](#41-インストール)
    - [① ユーザ作成](#①-ユーザ作成)
    - [② ダウンロード](#②-ダウンロード)
    - [③ 実行ユーザ設定](#③-実行ユーザ設定)
    - [④ 起動](#④-起動)
  - [4.2 リポジトリ設計（重要）](#42-リポジトリ設計重要)
    - [代表的なリポジトリ](#代表的なリポジトリ)
      - [Maven例](#maven例)
  - [4.3 Docker Registry](#43-docker-registry)
- [5. GitLab × Nexus 連携（CI/CD）](#5-gitlab-nexus-連携cicd)
  - [5.1 認証方式](#51-認証方式)
  - [5.2 認証情報管理(「ユーザ/パスワード」方式例)](#52-認証情報管理ユーザパスワード方式例)
  - [5.3 GitLab CIからNexusへ成果物登録](#53-gitlab-ciからnexusへ成果物登録)
    - [Maven設定（settings.xml）](#maven設定settingsxml)
  - [5.4 .gitlab-ci.yml 例（Maven）](#54-gitlab-ciyml-例maven)
  - [5.5 Docker Image Push](#55-docker-image-push)
- [6. 運用設計（非常に重要）](#6-運用設計非常に重要)
  - [6.1 GitLab運用](#61-gitlab運用)
    - [日次](#日次)
    - [定期](#定期)
  - [6.2 Nexus運用](#62-nexus運用)
    - [容量管理](#容量管理)
    - [バックアップ](#バックアップ)
  - [6.3 アカウント・権限](#63-アカウント権限)
  - [6.4 セキュリティ運用](#64-セキュリティ運用)
  - [6.5 監視項目](#65-監視項目)
  - [6.6 障害対応](#66-障害対応)
  - [6.7 バージョンアップ](#67-バージョンアップ)
- [7. 利用方法（利用者視点）](#7-利用方法利用者視点)
  - [7.1 開発者](#71-開発者)
  - [7.2 開発者の流れ](#72-開発者の流れ)
  - [7.3 成果物管理ルール](#73-成果物管理ルール)
  - [7.4 運用者](#74-運用者)
- [8. セキュリティ・監査](#8-セキュリティ監査)
- [9. 金融・公共向けの追加設計（実務）](#9-金融公共向けの追加設計実務)
- [10. よくあるトラブル](#10-よくあるトラブル)
- [11. 成果物一覧（実務）](#11-成果物一覧実務)
- [12. まとめ](#12-まとめ)
<!-- TOC_END -->

# ◆ GitLab × Nexusの構築概要

以下では、**Linux環境における GitLab + Nexus（Sonatype Nexus Repository）** を
**「構築 → 運用 → 利用（開発者視点／CI/CD視点）」** の流れで、**実務・運用設計レベル**まで踏み込んで整理します。  
（金融・公共系や中〜大規模SIで一般的な構成を前提にしています）

---

## 1. 全体像（GitLab × Nexus の役割分担）
[🔙 目次に戻る](#index)


### 1.1 役割整理
[🔙 目次に戻る](#index)


| コンポーネント          | 主な役割                               |
| ---------------- | ---------------------------------- |
| GitLab           | ソースコード管理、Issue、Merge Request、CI/CD |
| GitLab Runner    | CI/CDジョブ実行                         |
| Nexus Repository | 成果物（Artifact）の集中管理                 |
| Linux OS         | セキュアで安定した実行基盤                      |

#### なぜNexusが必要か？
[🔙 目次に戻る](#index)


* GitLabだけでもCI/CDは可能
* **「成果物の長期保管・再利用・バージョン管理」** を厳密に行うにはNexusが必須
* 金融・公共系では **再現性・証跡** が重視される

---

### 1.2 GitLab × Nexus役割分担（重要）
[🔙 目次に戻る](#index)


| 領域       | GitLab                | Nexus     |
| -------- | --------------------- | --------- |
| ソースコード   | ◎                     | ×         |
| CI/CD    | ◎                     | ×         |
| バイナリ管理   | △（Container Registry） | ◎         |
| 依存ライブラリ  | ×                     | ◎         |
| リリース成果物  | △                     | ◎         |
| セキュリティ制御 | ○                     | ◎（Repo単位） |

📌 **GitLab = ソースとパイプライン**  
📌 **Nexus = 成果物・依存物の金庫**

---

## 2. Linux環境での構築設計（共通前提）
[🔙 目次に戻る](#index)


### 2.1 推奨構成例
[🔙 目次に戻る](#index)


```
[User]
   |
   v
[HTTPS]
   |
   v
[GitLab Server] ---- [GitLab Runner]
  - Source
  - CI/CD
       |
       | (Artifact Upload)
       v
[Nexus Repository Manager]
  - Proxy Repo
  - Hosted Repo
       |
       v
[Deploy Server / K8s / ECS]
```

#### サーバ分離（推奨）
[🔙 目次に戻る](#index)


| サーバ    | 理由              |
| ------ | --------------- |
| GitLab | I/O負荷が高い(CPU/メモリ消費大)|
| Runner | ジョブ増加時にスケール     |
| Nexus  | ディスク容量・バックアップ重視(ディスクI/O集中) |

---
#### GitLab推奨スペック（目安）
[🔙 目次に戻る](#index)


| 規模 | CPU    | MEM  | Disk  |
| -- | ------ | ---- | ----- |
| 小  | > 4core  | > 8GB  | SSD推奨、容量はリポジトリサイズに応じて |
| 中〜大  | > 8core  | > 16GB | RAID構成、高速SSD推奨 |

---

#### Nexus推奨スペック（目安）
[🔙 目次に戻る](#index)


| 規模 | CPU    | MEM  | Disk  |
| -- | ------ | ---- | ----- |
| 小  | > 4core  | > 8GB  | > 200GB |
| 中  | > 8core  | > 16GB | > 500GB |
| 大  | > 16core | > 32GB | > 1TB+  |

📌 **SSD必須**

---

### 2.2 Linux共通前提
[🔙 目次に戻る](#index)


* OS：RHEL / Rocky Linux / AlmaLinux / Ubuntu LTS
* 時刻同期：chrony / ntpd
* セキュリティ：

  * firewalld / iptables
  * SELinux（Permissive or Enforcing＋例外）
* ディスク：

  * GitLab：/var/opt/gitlab
  * Nexus：/nexus-data（**大容量必須**）

---

## 3. GitLab 構築（Linux）
[🔙 目次に戻る](#index)


### 3.1 GitLabインストール（Omnibus）
[🔙 目次に戻る](#index)


```bash
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.rpm.sh | sudo bash
sudo EXTERNAL_URL="https://gitlab.example.com" yum install -y gitlab-ee
```

#### 設定ファイル
[🔙 目次に戻る](#index)


```bash
/etc/gitlab/gitlab.rb
```

##### 重要設定例
[🔙 目次に戻る](#index)


```ruby
external_url 'https://gitlab.example.com'
gitlab_rails['gitlab_shell_ssh_port'] = 2222
nginx['redirect_http_to_https'] = true
```

#### 反映
[🔙 目次に戻る](#index)


```bash
gitlab-ctl reconfigure
```

---

### 3.2 GitLab Runner 構築
[🔙 目次に戻る](#index)


```bash
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh | sudo bash
yum install -y gitlab-runner
```

#### Runner登録
[🔙 目次に戻る](#index)


```bash
gitlab-runner register
```

* Executor：shell / docker（推奨）
* タグ：`build`, `deploy` 等

---

## 4. Nexus Repository 構築（Linux）
[🔙 目次に戻る](#index)


### 4.1 インストール
[🔙 目次に戻る](#index)


#### ① ユーザ作成
[🔙 目次に戻る](#index)


```bash
useradd nexus
```

#### ② ダウンロード
[🔙 目次に戻る](#index)


```bash
cd /opt
wget https://download.sonatype.com/nexus/3/latest-unix.tar.gz
tar zxvf latest-unix.tar.gz
ln -s nexus-3* nexus
chown -R nexus:nexus nexus /opt/sonatype-work
```

#### ③ 実行ユーザ設定
[🔙 目次に戻る](#index)


```bash
vi /opt/nexus/bin/nexus.rc
run_as_user="nexus"
```

#### ④ 起動
[🔙 目次に戻る](#index)


```bash
sudo -u nexus /opt/nexus/bin/nexus start
```

---

### 4.2 リポジトリ設計（重要）
[🔙 目次に戻る](#index)


#### 代表的なリポジトリ
[🔙 目次に戻る](#index)


| 種別     | 例               |
| ------ | --------------- |
| hosted | 社内(自社)成果物           |
| proxy  | 外部OSS取得(Maven Central 等) |
| group  | 論理統合(hosted＋proxy)   |

##### Maven例
[🔙 目次に戻る](#index)


* maven-releases（hosted）
* maven-snapshots（hosted）
* maven-central（proxy）
* maven-public（group）

---

### 4.3 Docker Registry
[🔙 目次に戻る](#index)


```
docker-proxy
docker-hosted
docker-group
```

---

## 5. GitLab × Nexus 連携（CI/CD）
[🔙 目次に戻る](#index)


### 5.1 認証方式
[🔙 目次に戻る](#index)


| 方法           | 備考   |
| ------------ | ---- |
| ユーザ/パスワード    | 小規模  |
| Deploy Token | 推奨   |
| LDAP連携       | 企業向け |

---

### 5.2 認証情報管理(「ユーザ/パスワード」方式例)
[🔙 目次に戻る](#index)


* Nexusユーザを作成（deploy専用）
* GitLab CI Variablesに登録

```text
NEXUS_USER
NEXUS_PASS
NEXUS_URL
```

---

### 5.3 GitLab CIからNexusへ成果物登録
[🔙 目次に戻る](#index)


#### Maven設定（settings.xml）
[🔙 目次に戻る](#index)


```xml
<servers>
  <server>
    <id>nexus</id>
    <username>${NEXUS_USER}</username>
    <password>${NEXUS_PASS}</password>
  </server>
</servers>
```

---

### 5.4 .gitlab-ci.yml 例（Maven）
[🔙 目次に戻る](#index)


```yaml
stages:
  - build
  - deploy

build:
  stage: build
  script:
    - mvn clean package

deploy:
  stage: deploy
  script:
    - mvn deploy \
      -Dnexus.url=$NEXUS_URL \
      -Dnexus.user=$NEXUS_USER \
      -Dnexus.pass=$NEXUS_PASS
```

👉 **成果物はGitLabではなくNexusへ保管**

---

### 5.5 Docker Image Push
[🔙 目次に戻る](#index)


```bash
docker login nexus.example.com:5000
docker push nexus.example.com:5000/app:1.0.0
```

---
## 6. 運用設計（非常に重要）
[🔙 目次に戻る](#index)


### 6.1 GitLab運用
[🔙 目次に戻る](#index)


#### 日次
[🔙 目次に戻る](#index)


* CI失敗確認
* ディスク使用率監視

#### 定期
[🔙 目次に戻る](#index)


* バックアップ

```bash
gitlab-backup create
```

* ログ確認

```bash
gitlab-ctl tail
```

---

### 6.2 Nexus運用
[🔙 目次に戻る](#index)


#### 容量管理
[🔙 目次に戻る](#index)


* 古いSnapshot自動削除
* Blob Store監視

#### バックアップ
[🔙 目次に戻る](#index)


* `/nexus-data` 定期バックアップ
* DB（OrientDB / H2）の整合性確認

---
### 6.3 アカウント・権限
[🔙 目次に戻る](#index)


* [GitLab×Nexusのアカウント・権限管理](GitLab×Nexusのアカウント・権限管理.md)

---

### 6.4 セキュリティ運用
[🔙 目次に戻る](#index)


| 項目     | 対応                         |
| ------ | -------------------------- |
| アクセス制御 | ロールベース                     |
| 通信     | HTTPS必須                    |
| 監査     | GitLab Audit Log           |
| 脆弱性    | GitLab Dependency Scanning |

---
### 6.5 監視項目
[🔙 目次に戻る](#index)


| 項目       | 内容   |
| -------- | ---- |
| Disk     | 容量枯渇 |
| Heap     | OOM  |
| Response | 8081 |
| Job失敗    | CI   |

---

### 6.6 障害対応
[🔙 目次に戻る](#index)


| 事象      | 対応         |
| ------- | ---------- |
| Nexus停止 | JVM Heap調整 |
| Push失敗  | Repo権限     |
| CI失敗    | Token期限    |

---

### 6.7 バージョンアップ
[🔙 目次に戻る](#index)


* Nexus → マイナーアップデート定期
* GitLab → 月次
* **同時アップデート禁止**

---

## 7. 利用方法（利用者視点）
[🔙 目次に戻る](#index)


### 7.1 開発者
[🔙 目次に戻る](#index)


* GitLabでコード管理
* MRレビュー
* CI結果確認
* 成果物は直接Nexus参照

### 7.2 開発者の流れ
[🔙 目次に戻る](#index)


```
Git Push
 → GitLab CI起動
 → ビルド
 → Nexusへ登録
 → デプロイ
```

---

### 7.3 成果物管理ルール
[🔙 目次に戻る](#index)


| 種別       | ルール           |
| -------- | ------------- |
| SNAPSHOT | 自動            |
| RELEASE  | 手動承認          |
| Docker   | immutable tag |

---

### 7.4 運用者
[🔙 目次に戻る](#index)


* Runner稼働監視
* Nexus容量・性能管理
* 障害対応（I/O・DB）

---

## 8. セキュリティ・監査
[🔙 目次に戻る](#index)


| 項目     | 対応       |
| ------ | -------- |
| OSS改ざん | Proxy固定  |
| 成果物改ざん | Hostedのみ |
| 証跡     | CIログ     |
| 操作履歴   | Audit    |

---

## 9. 金融・公共向けの追加設計（実務）
[🔙 目次に戻る](#index)


| 項目    | 対応                   |
| ----- | -------------------- |
| 環境分離  | Dev / Stg / Prod     |
| 操作証跡  | GitLab Audit         |
| 成果物固定 | Releaseはimmutability |
| 手順書   | 運用Runbook必須          |

---

## 10. よくあるトラブル
[🔙 目次に戻る](#index)


| 事象        | 原因          |
| --------- | ----------- |
| CI遅延      | Runner不足    |
| Nexus容量枯渇 | Snapshot無制御 |
| デプロイ失敗    | 認証情報ミス      |
| GitLab高負荷 | ディスクI/O     |

---

## 11. 成果物一覧（実務）
[🔙 目次に戻る](#index)


* GitLab構築手順書
* Nexus構築手順書
* リポジトリ設計書
* CI/CD設計書
* バックアップ/復旧手順
* 障害対応Runbook
* 監査説明資料

---

## 12. まとめ
[🔙 目次に戻る](#index)


**GitLab＋Nexus構成の本質的価値**

* ソースと成果物の責務分離
* CI/CDの再現性・統制
* 監査・証跡対応
* 中長期運用の安定性

---
