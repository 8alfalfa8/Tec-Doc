<!-- TOC_START -->
<a id="index"></a>📖 目次

- [Salesforce開発 基本用語集（実務向け）](#salesforce開発-基本用語集実務向け)
  - [1. 組織・環境に関する用語](#1-組織環境に関する用語)
    - [Org（組織）](#org組織)
    - [Sandbox](#sandbox)
    - [Instance](#instance)
  - [2. データモデル関連用語](#2-データモデル関連用語)
    - [オブジェクト（Object）](#オブジェクトobject)
    - [レコード（Record）](#レコードrecord)
    - [項目（Field）](#項目field)
    - [主従関係（Master-Detail）](#主従関係master-detail)
    - [参照関係（Lookup）](#参照関係lookup)
  - [3. 権限・セキュリティ用語（重要）](#3-権限セキュリティ用語重要)
    - [プロファイル](#プロファイル)
    - [権限セット](#権限セット)
    - [ロール](#ロール)
    - [共有設定（Sharing）](#共有設定sharing)
    - [OWD（組織の共有設定）](#owd組織の共有設定)
  - [4. 自動化・業務ロジック用語](#4-自動化業務ロジック用語)
    - [Flow（フロー）](#flowフロー)
    - [Process Builder](#process-builder)
    - [Apex](#apex)
    - [Trigger](#trigger)
    - [Batch Apex](#batch-apex)
  - [5. 画面・UI用語](#5-画面ui用語)
    - [Lightning Experience](#lightning-experience)
    - [Lightning App Builder](#lightning-app-builder)
    - [LWC（Lightning Web Components）](#lwclightning-web-components)
    - [Visualforce](#visualforce)
  - [6. 開発・構成管理用語](#6-開発構成管理用語)
    - [メタデータ](#メタデータ)
    - [Change Set](#change-set)
    - [Salesforce DX（SFDX）](#salesforce-dxsfdx)
    - [Package](#package)
  - [7. テスト・品質関連用語](#7-テスト品質関連用語)
    - [Apex Test](#apex-test)
    - [コードカバレッジ](#コードカバレッジ)
    - [Governor Limits](#governor-limits)
  - [8. 連携・API用語](#8-連携api用語)
    - [REST API / SOAP API](#rest-api-soap-api)
    - [Platform Event](#platform-event)
    - [Named Credential](#named-credential)
    - [MuleSoft](#mulesoft)
  - [9. 運用・監査用語](#9-運用監査用語)
    - [Setup Audit Trail](#setup-audit-trail)
    - [Debug Log](#debug-log)
    - [Release Update](#release-update)
  - [10. 実務で頻出する重要概念（用語ではないが必須）](#10-実務で頻出する重要概念用語ではないが必須)
  - [11. 混乱しやすい用語対比](#11-混乱しやすい用語対比)
<!-- TOC_END -->

# ◆ Salesforce開発おける基本用語
/
以下に、**Salesforce開発における基本用語**を、
**「業務・設計・開発・運用」まで実務で必ず出てくるもの**に絞って体系的に整理します。
（SI／PM／設計レビューで使える定義レベルです）

---

## Salesforce開発 基本用語集（実務向け）
[🔙 目次に戻る](#index)


---

### 1. 組織・環境に関する用語
[🔙 目次に戻る](#index)


#### Org（組織）
[🔙 目次に戻る](#index)


* Salesforceの**論理的なシステム単位**
* 本番Org／Sandboxは別Org

#### Sandbox
[🔙 目次に戻る](#index)


* 本番のコピー環境
* 種類：

  * Developer（設定＋メタデータ）
  * Developer Pro
  * Partial Copy（サンプルデータ）
  * Full（全データ）

#### Instance
[🔙 目次に戻る](#index)


* Salesforceの物理基盤（例：AP0, JP0）
* 通常は意識不要

---

### 2. データモデル関連用語
[🔙 目次に戻る](#index)


#### オブジェクト（Object）
[🔙 目次に戻る](#index)


* Salesforceの**テーブル**
* 種類：

  * 標準オブジェクト（Account等）
  * カスタムオブジェクト（__c）

#### レコード（Record）
[🔙 目次に戻る](#index)


* テーブルの1行

#### 項目（Field）
[🔙 目次に戻る](#index)


* カラム
* 種類：Text / Number / Picklist / Lookup 等

#### 主従関係（Master-Detail）
[🔙 目次に戻る](#index)


* 親子関係（親削除＝子削除）
* 子は親の権限を継承

#### 参照関係（Lookup）
[🔙 目次に戻る](#index)


* 緩い関連
* 権限・削除は独立

---

### 3. 権限・セキュリティ用語（重要）
[🔙 目次に戻る](#index)


#### プロファイル
[🔙 目次に戻る](#index)


* ユーザーの**基本権限**
* 1ユーザー1プロファイル

#### 権限セット
[🔙 目次に戻る](#index)


* プロファイルに**追加**する権限
* 推奨方式（柔軟）

#### ロール
[🔙 目次に戻る](#index)


* 組織階層
* レコード参照範囲に影響

#### 共有設定（Sharing）
[🔙 目次に戻る](#index)


* レコード単位の参照・編集制御

#### OWD（組織の共有設定）
[🔙 目次に戻る](#index)


* 権限設計の起点
* 原則「非公開」から設計

---

### 4. 自動化・業務ロジック用語
[🔙 目次に戻る](#index)


#### Flow（フロー）
[🔙 目次に戻る](#index)


* Salesforceの**標準自動化エンジン**
* 種類：

  * レコードトリガフロー
  * 画面フロー
  * 自動起動フロー

#### Process Builder
[🔙 目次に戻る](#index)


* 旧自動化ツール（非推奨）

#### Apex
[🔙 目次に戻る](#index)


* Salesforce独自のサーバサイド言語
* Javaライク

#### Trigger
[🔙 目次に戻る](#index)


* レコードイベント（Insert/Update等）で動作するApex

#### Batch Apex
[🔙 目次に戻る](#index)


* 大量データ向け非同期処理

---

### 5. 画面・UI用語
[🔙 目次に戻る](#index)


#### Lightning Experience
[🔙 目次に戻る](#index)


* 現行Web UI

#### Lightning App Builder
[🔙 目次に戻る](#index)


* 画面構築ツール（ノーコード）

#### LWC（Lightning Web Components）
[🔙 目次に戻る](#index)


* フロントエンド開発技術
* HTML + JavaScript

#### Visualforce
[🔙 目次に戻る](#index)


* 旧画面技術（レガシー）

---

### 6. 開発・構成管理用語
[🔙 目次に戻る](#index)


#### メタデータ
[🔙 目次に戻る](#index)


* Salesforceの設定情報全般
* オブジェクト定義、Flow、Apex等

#### Change Set
[🔙 目次に戻る](#index)


* メタデータの移送機能（GUI）

#### Salesforce DX（SFDX）
[🔙 目次に戻る](#index)


* CLIベース開発方式
* Git連携前提

#### Package
[🔙 目次に戻る](#index)


* 機能の再利用・配布単位

---

### 7. テスト・品質関連用語
[🔙 目次に戻る](#index)


#### Apex Test
[🔙 目次に戻る](#index)


* Apex用単体テスト
* 本番デプロイに必須

#### コードカバレッジ
[🔙 目次に戻る](#index)


* テスト実行率
* **75%以上必須**

#### Governor Limits
[🔙 目次に戻る](#index)


* 処理制限（CPU、SOQL等）

---

### 8. 連携・API用語
[🔙 目次に戻る](#index)


#### REST API / SOAP API
[🔙 目次に戻る](#index)


* 外部システム連携手段

#### Platform Event
[🔙 目次に戻る](#index)


* イベント駆動連携

#### Named Credential
[🔙 目次に戻る](#index)


* 認証情報管理

#### MuleSoft
[🔙 目次に戻る](#index)


* Salesforce公式iPaaS

---

### 9. 運用・監査用語
[🔙 目次に戻る](#index)


#### Setup Audit Trail
[🔙 目次に戻る](#index)


* 設定変更履歴

#### Debug Log
[🔙 目次に戻る](#index)


* 処理ログ

#### Release Update
[🔙 目次に戻る](#index)


* 年3回の自動機能更新

---

### 10. 実務で頻出する重要概念（用語ではないが必須）
[🔙 目次に戻る](#index)


| 概念        | 説明        |
| --------- | --------- |
| Fit & Gap | 標準機能適合度分析 |
| ノーコード優先   | Flow最優先   |
| バルク処理     | 大量データ前提設計 |
| 権限先行設計    | 後回し厳禁     |

---

### 11. 混乱しやすい用語対比
[🔙 目次に戻る](#index)


| 用語             | 誤解しやすい点  |
| -------------- | -------- |
| Org = 環境       | DBではない   |
| Object = Table | JOIN不可   |
| Flow = 簡易機能    | 実際は中核    |
| 権限セット          | プロファイル代替 |

---
