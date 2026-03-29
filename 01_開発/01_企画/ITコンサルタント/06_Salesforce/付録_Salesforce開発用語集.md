# ◆ Salesforce開発おける基本用語
/
以下に、**Salesforce開発における基本用語**を、
**「業務・設計・開発・運用」まで実務で必ず出てくるもの**に絞って体系的に整理します。
（SI／PM／設計レビューで使える定義レベルです）

---

## Salesforce開発 基本用語集（実務向け）

---

### 1. 組織・環境に関する用語

#### Org（組織）

* Salesforceの**論理的なシステム単位**
* 本番Org／Sandboxは別Org

#### Sandbox

* 本番のコピー環境
* 種類：

  * Developer（設定＋メタデータ）
  * Developer Pro
  * Partial Copy（サンプルデータ）
  * Full（全データ）

#### Instance

* Salesforceの物理基盤（例：AP0, JP0）
* 通常は意識不要

---

### 2. データモデル関連用語

#### オブジェクト（Object）

* Salesforceの**テーブル**
* 種類：

  * 標準オブジェクト（Account等）
  * カスタムオブジェクト（__c）

#### レコード（Record）

* テーブルの1行

#### 項目（Field）

* カラム
* 種類：Text / Number / Picklist / Lookup 等

#### 主従関係（Master-Detail）

* 親子関係（親削除＝子削除）
* 子は親の権限を継承

#### 参照関係（Lookup）

* 緩い関連
* 権限・削除は独立

---

### 3. 権限・セキュリティ用語（重要）

#### プロファイル

* ユーザーの**基本権限**
* 1ユーザー1プロファイル

#### 権限セット

* プロファイルに**追加**する権限
* 推奨方式（柔軟）

#### ロール

* 組織階層
* レコード参照範囲に影響

#### 共有設定（Sharing）

* レコード単位の参照・編集制御

#### OWD（組織の共有設定）

* 権限設計の起点
* 原則「非公開」から設計

---

### 4. 自動化・業務ロジック用語

#### Flow（フロー）

* Salesforceの**標準自動化エンジン**
* 種類：

  * レコードトリガフロー
  * 画面フロー
  * 自動起動フロー

#### Process Builder

* 旧自動化ツール（非推奨）

#### Apex

* Salesforce独自のサーバサイド言語
* Javaライク

#### Trigger

* レコードイベント（Insert/Update等）で動作するApex

#### Batch Apex

* 大量データ向け非同期処理

---

### 5. 画面・UI用語

#### Lightning Experience

* 現行Web UI

#### Lightning App Builder

* 画面構築ツール（ノーコード）

#### LWC（Lightning Web Components）

* フロントエンド開発技術
* HTML + JavaScript

#### Visualforce

* 旧画面技術（レガシー）

---

### 6. 開発・構成管理用語

#### メタデータ

* Salesforceの設定情報全般
* オブジェクト定義、Flow、Apex等

#### Change Set

* メタデータの移送機能（GUI）

#### Salesforce DX（SFDX）

* CLIベース開発方式
* Git連携前提

#### Package

* 機能の再利用・配布単位

---

### 7. テスト・品質関連用語

#### Apex Test

* Apex用単体テスト
* 本番デプロイに必須

#### コードカバレッジ

* テスト実行率
* **75%以上必須**

#### Governor Limits

* 処理制限（CPU、SOQL等）

---

### 8. 連携・API用語

#### REST API / SOAP API

* 外部システム連携手段

#### Platform Event

* イベント駆動連携

#### Named Credential

* 認証情報管理

#### MuleSoft

* Salesforce公式iPaaS

---

### 9. 運用・監査用語

#### Setup Audit Trail

* 設定変更履歴

#### Debug Log

* 処理ログ

#### Release Update

* 年3回の自動機能更新

---

### 10. 実務で頻出する重要概念（用語ではないが必須）

| 概念        | 説明        |
| --------- | --------- |
| Fit & Gap | 標準機能適合度分析 |
| ノーコード優先   | Flow最優先   |
| バルク処理     | 大量データ前提設計 |
| 権限先行設計    | 後回し厳禁     |

---

### 11. 混乱しやすい用語対比

| 用語             | 誤解しやすい点  |
| -------------- | -------- |
| Org = 環境       | DBではない   |
| Object = Table | JOIN不可   |
| Flow = 簡易機能    | 実際は中核    |
| 権限セット          | プロファイル代替 |

---
