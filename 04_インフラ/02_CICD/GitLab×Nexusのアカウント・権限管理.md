# GitLab × Nexusアカウント・権限管理

以下は **「運用設計（非常に重要）」観点での GitLab × Nexus のアカウント・権限設計**です。
**金融・公共系／監査対応案件でレビューに耐えるレベル**まで落としています。

---

## アカウント・権限 運用設計

---

## 1. 基本原則（最重要）

### 1.1 設計原則

| 原則   | 内容           |
| ---- | ------------ |
| 最小権限 | 必要最低限の操作のみ許可 |
| 職務分離 | 開発・運用・管理の分離  |
| 個人特定 | 共有アカウント禁止    |
| 証跡確保 | 誰が・いつ・何をしたか  |

👉 **「CI用アカウント」と「人の操作」は完全分離**

---

## 2. ロール体系（全体）

### 2.1 ロール対応表

| ロール       | GitLab     | Nexus     |
| --------- | ---------- | --------- |
| GitLab管理者 | Admin      | －         |
| Nexus管理者  | －          | Admin     |
| プロジェクト管理者 | Maintainer | －         |
| 開発者       | Developer  | Read      |
| CI/CD実行   | Bot User   | Deploy    |
| 監査・閲覧     | Reporter   | Read Only |

---

## 3. GitLab 側 アカウント・権限設計

---

### 3.1 GitLab 標準ロール（重要）

| ロール        | 権限概要      | 利用者            |
| ---------- | --------- | -------------- |
| Owner      | 全権限       | システム管理者（限定）    |
| Maintainer | 設定変更・MR承認 | PL / Tech Lead |
| Developer  | Push・CI実行 | 開発者            |
| Reporter   | 参照のみ      | 監査             |
| Guest      | Issue参照   | 原則使用しない        |

---

### 3.2 推奨割当ルール

#### 管理者

* GitLab Admin は **2名以内**
* 日常作業では Admin 権限を使わない

#### プロジェクト

* Owner：設定しない or 最小
* Maintainer：PL／TLのみ
* Developer：一般開発者

---

### 3.3 CI/CD 用アカウント（重要）

#### 種別

* **Project Access Token**
* **Group Access Token**
* 専用 Bot User（人と分離）

#### 権限

* `read_repository`
* `read_registry`
* `write_registry`（必要時のみ）

❌ `api` 権限は原則禁止

---

### 3.4 SSH / 認証設計

* 個人 SSH Key 必須
* 共用鍵禁止
* 失効管理（退職時）

---

## 4. Nexus 側 アカウント・権限設計

---

### 4.1 ロール分離（必須）

| ロール         | 内容      |
| ----------- | ------- |
| nx-admin    | Nexus管理 |
| nx-deployer | 成果物登録   |
| nx-reader   | 参照のみ    |

---

### 4.2 推奨ロール定義

#### nx-admin

* リポジトリ作成
* Blob管理
* ユーザ管理

👉 **CIや開発者に付与禁止**

---

#### nx-deployer（CI用）

* 対象 hosted リポジトリへの upload
* delete 不可（immutable）

---

#### nx-reader

* proxy / group 参照のみ
* ローカル成果物の削除不可

---

### 4.3 CI/CD 専用ユーザ（必須）

| 項目   | 内容             |
| ---- | -------------- |
| ユーザ名 | nexus-ci       |
| 認証   | パスワード or Token |
| 権限   | nx-deployer    |
| 利用範囲 | CIのみ           |

---

## 5. GitLab × Nexus 連携時の権限制御

---

### 5.1 CI → Nexus フロー

```
[GitLab CI]
   ↓ (Token)
[nexus-ci]
   ↓ (Deploy)
[maven-releases]
```

✔ CIは **アップロードのみ可能**
❌ 削除・上書き不可

---

### 5.2 GitLab CI 変数管理

| 設定        | 理由                  |
| --------- | ------------------- |
| Protected | main / releaseのみ    |
| Masked    | ログ秘匿                |
| 環境別       | Dev / Stg / Prod 分離 |

---

## 6. 環境別アカウント設計（超重要）

| 環境   | GitLab | Nexus     |
| ---- | ------ | --------- |
| Dev  | 緩め     | Snapshot可 |
| Stg  | 制限     | Release禁止 |
| Prod | 厳格     | Immutable |

---

### 6.1 本番（Prod）追加制御

* 手動承認（Manual Job）
* Maintainer 以上のみ
* Nexus Delete 禁止

---

## 7. 監査・証跡設計

---

### 7.1 GitLab

* Audit Events 有効化
* MR承認履歴
* CI実行履歴

---

### 7.2 Nexus

* アクセスログ保存
* 成果物変更履歴
* Blob操作ログ

---

## 8. ライフサイクル管理（運用）

---

### 8.1 入社・異動

* 役割に応じたロール付与
* Admin権限は申請制

---

### 8.2 退職・契約終了

* 即日アカウント無効化
* Token失効
* SSH Key削除

---

## 9. よくある事故と防止策

| 事故      | 防止         |
| ------- | ---------- |
| CIで全削除  | delete権限剥奪 |
| Token漏洩 | Masked変数   |
| 誤Deploy | 手動承認       |
| 管理者乱用   | 権限レビュー     |

---

## 10. 運用設計チェックリスト（抜粋）

* [ ] Admin権限最小化
* [ ] CI専用アカウント分離
* [ ] Delete不可設計
* [ ] 環境別権限分離
* [ ] 監査ログ保存

---

## まとめ（運用の要点）

> **GitLab＝「誰がコードを変えたか」**
> **Nexus＝「何が本番に出たか」**

この2点を
**アカウントと権限で“技術的に強制”すること**が
運用設計の最重要ポイントです。

---

