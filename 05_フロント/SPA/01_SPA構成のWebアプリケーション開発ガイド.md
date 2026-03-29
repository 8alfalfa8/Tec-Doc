# ◆ SPA構成のWebアプリケーション開発ガイド

以下では、**SPA（Single Page Application）構成のWebアプリケーション開発**について、
**要件定義 → アーキテクチャ設計 → フロントエンド設計 → バックエンド設計 → 認証認可 → 通信設計 → 非機能設計 → 構築・CI/CD → 運用**
という実案件（特に**金融・公共・業務系**を想定）で通用するレベルの粒度で、体系的に詳しくご説明します。

---

## 1. SPAとは何か（前提整理）

### 1.1 SPAの特徴

* 初回ロード時にHTML/CSS/JSを取得
* 以降は **画面遷移＝JSによるDOM更新**
* サーバとは **API通信（JSON）** のみ

### 1.2 SPAのメリット / デメリット

| 観点  | 内容                    |
| --- | --------------------- |
| UX  | 画面遷移が高速・リッチ           |
| 開発  | フロントとバックを分離可能         |
| 再利用 | APIを他システムでも利用可        |
| 課題  | 初期表示、SEO、セキュリティ、JS肥大化 |

---

## 2. 全体アーキテクチャ設計（基本）

### 2.1 標準的SPA構成（業務系）

```
[ Browser ]
   |
   | HTTPS
   v
[ CDN / WAF ]
   |
   | 静的配信
   v
[ SPA (React / Vue) ]
   |
   | HTTPS (JSON)
   v
[ BFF / API Gateway ]
   |
   v
[ Backend API (FastAPI / Spring) ]
   |
   v
[ DB / 外部サービス ]
```

### 2.2 なぜBFFを置くのか（重要）

* フロント都合のAPI設計が可能
* 認証情報の集約
* 外部API・マイクロサービスの隠蔽
* セキュリティ境界の明確化

👉 **業務SPAではBFFほぼ必須**

---

## 3. 要件定義フェーズ（SPA特有の観点）

### 3.1 機能要件

* 画面一覧（SPAでも画面概念は残す）
* CRUD / ワークフロー
* 非同期処理（進捗表示）

### 3.2 非機能要件（SPAで特に重要）

| 項目     | 内容                   |
| ------ | -------------------- |
| 初期表示時間 | LCP / TTI            |
| セキュリティ | XSS / CSRF / Token管理 |
| 可用性    | API障害時の挙動            |
| 操作性    | ローディング・エラー表示         |
| ブラウザ   | 対応範囲（IE除外等）          |

---

## 4. フロントエンド設計（SPAの中核）

### 4.1 技術選定

* React / Vue / Angular
* TypeScript（**必須**）
* 状態管理：Redux / Zustand / Pinia
* ルーティング：React Router / Vue Router

---

### 4.2 画面設計（SPA流）

#### ① 画面遷移設計

* URL設計は**業務画面単位**
* 例：

```
/login
/dashboard
/users
/users/:id
```

#### ② コンポーネント設計（重要）

```
Page
 ├─ Layout
 │   ├─ Header
 │   ├─ Sidebar
 │   └─ Footer
 └─ Feature
     ├─ List
     ├─ Detail
     └─ Form
```

**設計ポイント**

* Page：ルーティング単位
* Feature：業務単位
* Component：再利用部品

---

### 4.3 状態管理設計

| 種類    | 例           |
| ----- | ----------- |
| グローバル | ログインユーザー、権限 |
| 画面単位  | 検索条件、ページング  |
| 一時    | フォーム入力値     |

👉 **「何をどこで持つか」設計しないと破綻**

---

## 5. バックエンド / API設計

### 5.1 API設計原則

* REST / JSON
* URIはリソース指向
* HTTPステータス厳密

例：

```
GET    /api/users
GET    /api/users/{id}
POST   /api/users
PUT    /api/users/{id}
DELETE /api/users/{id}
```

---

### 5.2 BFF設計の実例

```
GET /bff/dashboard
  ↓
- ユーザー情報
- 権限情報
- お知らせ
```

👉 フロントは **1回のAPI呼び出しで済む**

---

## 6. 認証・認可設計（SPAで最重要）

### 6.1 認証方式

| 方式                        | 実務評価   |
| ------------------------- | ------ |
| Cookie + Session          | △      |
| JWT (LocalStorage)        | ❌（XSS） |
| **JWT (HttpOnly Cookie)** | ◎      |
| OIDC (Keycloak / Cognito) | ◎      |

---

### 6.2 SPA認証フロー（推奨）

```
① ログイン
② HttpOnly Cookie に Token
③ SPAは Tokenを触らない
④ APIは Cookieで認証
```

👉 **金融・公共案件ではほぼこの方式**

---

## 7. 通信・エラーハンドリング設計

### 7.1 API通信共通処理

* 認証エラー → ログアウト
* 5xx → 共通エラー画面
* タイムアウト → 再試行

### 7.2 ローディング設計

* 画面全体
* ボタン単位
* 非同期処理単位

---

## 8. セキュリティ設計（SPA特有）

| 脅威      | 対策                    |
| ------- | --------------------- |
| XSS     | CSP / エスケープ           |
| CSRF    | SameSite Cookie       |
| Token漏洩 | HttpOnly              |
| API乱用   | Rate Limit            |
| 改ざん     | Subresource Integrity |

---

## 9. ビルド・構築・CI/CD

### 9.1 ビルド

* npm / pnpm
* Vite / Webpack
* 環境変数（.env）

### 9.2 配置構成

* 静的ファイル → CDN / S3
* API → ECS / Kubernetes
* WAF → 前段配置

---

### 9.3 CI/CDパイプライン

```
Git Push
 ↓
Lint / Test
 ↓
Build SPA
 ↓
Deploy to CDN
 ↓
API Deploy
```

---

## 10. テスト設計（SPA）

| 種別      | ツール                  |
| ------- | -------------------- |
| 単体      | Jest / Vitest        |
| コンポーネント | Testing Library      |
| E2E     | Playwright / Cypress |
| API     | pytest / Postman     |

---

## 11. 運用設計

### 11.1 監視

* フロント：JS Error / LCP
* API：レスポンス / エラー率

### 11.2 ログ

* フロント：操作ログ
* バック：監査ログ

---

## 12. よくある失敗と対策

| 失敗       | 対策             |
| -------- | -------------- |
| 状態がカオス   | 状態管理設計を先に      |
| APIが細かすぎ | BFF導入          |
| 認証事故     | TokenをJSで扱わない  |
| 初期表示遅い   | Code Splitting |

---

## 13. 成果物一覧（実案件想定）

* SPAアーキテクチャ図
* 画面遷移図
* コンポーネント設計書
* API設計書（OpenAPI）
* 認証認可設計書
* 非機能要件定義書
* テスト計画書

---


