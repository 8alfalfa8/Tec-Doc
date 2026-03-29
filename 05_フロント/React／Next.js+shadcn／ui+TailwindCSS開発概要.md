<!-- TOC_START -->
<a id="index"></a>📖 目次

- [0. 全体像（採用理由と役割分担）](#0-全体像採用理由と役割分担)
- [1. 開発前の設計（最重要）](#1-開発前の設計最重要)
  - [1.1 画面・機能設計](#11-画面機能設計)
  - [1.2 コンポーネント設計方針](#12-コンポーネント設計方針)
- [2. 環境構築（Next.js + Tailwind + shadcn/ui）](#2-環境構築nextjs-tailwind-shadcnui)
  - [2.1 Next.js プロジェクト作成](#21-nextjs-プロジェクト作成)
  - [2.2 Tailwind CSS 設定確認](#22-tailwind-css-設定確認)
  - [2.3 shadcn/ui 導入](#23-shadcnui-導入)
  - [2.4 UIコンポーネント追加](#24-uiコンポーネント追加)
- [3. 実装手順（基本フロー）](#3-実装手順基本フロー)
  - [3.1 ページ作成（Next.js App Router）](#31-ページ作成nextjs-app-router)
  - [3.2 shadcn/ui + Tailwind 使用例](#32-shadcnui-tailwind-使用例)
  - [3.3 レイアウト（Header / Sidebar）](#33-レイアウトheader-sidebar)
- [4. 状態管理・データ取得](#4-状態管理データ取得)
  - [4.1 Server Component / Client Component](#41-server-component-client-component)
  - [4.2 API連携（fetch）](#42-api連携fetch)
- [5. スタイリング指針（重要）](#5-スタイリング指針重要)
  - [5.1 Tailwind運用ルール](#51-tailwind運用ルール)
  - [5.2 テーマ・ダークモード](#52-テーマダークモード)
- [6. フォーム・バリデーション（実務必須）](#6-フォームバリデーション実務必須)
  - [6.1 React Hook Form + Zod](#61-react-hook-form-zod)
- [7. 品質担保（CI前提）](#7-品質担保ci前提)
  - [7.1 静的チェック](#71-静的チェック)
  - [7.2 コンポーネント単体テスト（任意）](#72-コンポーネント単体テスト任意)
- [8. ビルド・デプロイ](#8-ビルドデプロイ)
- [9. 実務でのベストプラクティスまとめ](#9-実務でのベストプラクティスまとめ)
<!-- TOC_END -->

# ◆ React / Next.js + shadcn/ui + Tailwind CSS開発概要

以下では、**React / Next.js + shadcn/ui + Tailwind CSS** を前提に、
**実務レベル**（**業務システム・BtoB・管理画面**）で通用するフロントエンド開発手順を
**設計 → 環境構築 → 実装 → 品質担保 → 運用**の流れで詳しく解説します。

---

## 0. 全体像（採用理由と役割分担）
[🔙 目次に戻る](#index)


| 技術                | 役割     | 採用理由                            |
| ----------------- | ------ | ------------------------------- |
| Next.js (React)   | フロント基盤 | SSR/SSG, App Router, SEO, 大規模向け |
| React             | UIロジック | コンポーネント分割・状態管理                  |
| shadcn/ui         | UI部品   | Headless + Radix 기반、高品質         |
| Tailwind CSS      | スタイル   | 設計不要・一貫性・保守性                    |
| TypeScript        | 型      | 大規模開発必須                         |
| ESLint / Prettier | 品質     | コード統一                           |

👉 **「UI設計 × 開発効率 × 品質」のバランスが非常に良い構成**

---

[🔙 目次に戻る](#index)


## 1. 開発前の設計（最重要）
[🔙 目次に戻る](#index)


### 1.1 画面・機能設計
[🔙 目次に戻る](#index)


**最低限やるべき成果物**

* 画面一覧（ページ構成）
* 画面遷移図
* コンポーネント分割方針
* API I/F 一覧（バックエンド連携）

例（管理画面想定）：

```
/login
/dashboard
/users
/users/[id]
/settings
```

---

[🔙 目次に戻る](#index)


### 1.2 コンポーネント設計方針
[🔙 目次に戻る](#index)


**Atomic Design を簡略化して使うのが実務向け**

```
components/
 ├─ ui/          ← shadcn/ui（Button, Dialog 等）
 ├─ common/      ← 共通部品（Header, Sidebar）
 ├─ features/    ← 業務機能単位（UserTable, UserForm）
 └─ layout/      ← レイアウト
```

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 2. 環境構築（Next.js + Tailwind + shadcn/ui）
[🔙 目次に戻る](#index)


### 2.1 Next.js プロジェクト作成
[🔙 目次に戻る](#index)


```bash
npx create-next-app@latest my-app \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"
```

構成例：

```
src/
 ├─ app/
 ├─ components/
 ├─ lib/
 └─ styles/
```

---

[🔙 目次に戻る](#index)


### 2.2 Tailwind CSS 設定確認
[🔙 目次に戻る](#index)


`tailwind.config.ts`

```ts
export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

👉 **shadcn/ui 前提の設定なので基本変更不要**

---

[🔙 目次に戻る](#index)


### 2.3 shadcn/ui 導入
[🔙 目次に戻る](#index)


```bash
npx shadcn-ui@latest init
```

選択項目：

* TypeScript: ✅
* Tailwind CSS: ✅
* App Router: ✅
* src/ 配下: ✅

---

[🔙 目次に戻る](#index)


### 2.4 UIコンポーネント追加
[🔙 目次に戻る](#index)


```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add table
```

[🔙 目次に戻る](#index)


生成先：

```
components/ui/button.tsx
components/ui/dialog.tsx
```

---

[🔙 目次に戻る](#index)


## 3. 実装手順（基本フロー）
[🔙 目次に戻る](#index)


### 3.1 ページ作成（Next.js App Router）
[🔙 目次に戻る](#index)


```tsx
// src/app/users/page.tsx
export default function UsersPage() {
  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">ユーザー一覧</h1>
    </div>
  )
}
```

---

[🔙 目次に戻る](#index)


### 3.2 shadcn/ui + Tailwind 使用例
[🔙 目次に戻る](#index)


```tsx
import { Button } from "@/components/ui/button"

<Button variant="default">登録</Button>
<Button variant="outline">キャンセル</Button>
```

Tailwindは**微調整専用**に使うのがコツ：

```tsx
<Button className="mt-4 w-full">
  保存
</Button>
```

---

[🔙 目次に戻る](#index)


### 3.3 レイアウト（Header / Sidebar）
[🔙 目次に戻る](#index)


```tsx
// src/app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html lang="ja">
      <body className="flex">
        <Sidebar />
        <main className="flex-1 p-6">{children}</main>
      </body>
    </html>

[🔙 目次に戻る](#index)

  )
}
```

---

[🔙 目次に戻る](#index)


## 4. 状態管理・データ取得
[🔙 目次に戻る](#index)


### 4.1 Server Component / Client Component
[🔙 目次に戻る](#index)


* **デフォルト：Server Component**
* フォーム・モーダル：Client Component

```tsx
"use client"
```

---

[🔙 目次に戻る](#index)


### 4.2 API連携（fetch）
[🔙 目次に戻る](#index)


```tsx
const res = await fetch(`${process.env.API_URL}/users`, {
  cache: "no-store",
})
const users = await res.json()
```

👉 実務では：

* React Query / TanStack Query
* SWR
  を併用するケースが多い

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 5. スタイリング指針（重要）
[🔙 目次に戻る](#index)


### 5.1 Tailwind運用ルール
[🔙 目次に戻る](#index)


❌ NG

```tsx
<div className="mt-1 mb-2 pl-3 pr-3 text-sm text-gray-600">
```

⭕ OK

```tsx
<div className="text-sm text-muted-foreground mt-2">
```

👉 **意味ベースのclassを優先**

---

[🔙 目次に戻る](#index)


### 5.2 テーマ・ダークモード
[🔙 目次に戻る](#index)


shadcn/ui は `CSS variables` 管理

```css
:root {
  --primary: 222.2 47.4% 11.2%;
}
```

```tsx
className="bg-primary text-primary-foreground"
```

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 6. フォーム・バリデーション（実務必須）
[🔙 目次に戻る](#index)


### 6.1 React Hook Form + Zod
[🔙 目次に戻る](#index)


```bash
npm install react-hook-form zod @hookform/resolvers
```

```ts
const schema = z.object({
  email: z.string().email(),
})
```

👉 **バックエンドとバリデーション定義共有が理想**

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 7. 品質担保（CI前提）
[🔙 目次に戻る](#index)


### 7.1 静的チェック
[🔙 目次に戻る](#index)


* TypeScript
* ESLint
* Prettier

```bash
npm run lint
npm run build
```

---

[🔙 目次に戻る](#index)


### 7.2 コンポーネント単体テスト（任意）
[🔙 目次に戻る](#index)


* Vitest
* Testing Library

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 8. ビルド・デプロイ
[🔙 目次に戻る](#index)


```bash
npm run build
npm run start
```

CI/CD では：

* GitHub Actions
* Vercel / AWS（CloudFront + S3）

---

[🔙 目次に戻る](#index)


## 9. 実務でのベストプラクティスまとめ
[🔙 目次に戻る](#index)


✔ shadcn/ui を**ベースUI**にする<br>
✔ Tailwind は「微調整のみ」<br>
✔ ページ肥大化 → Feature Component 分割<br>
✔ 型とLintを**妥協しない**<br>
✔ Server Component を基本に設計

---

[🔙 目次に戻る](#index)

