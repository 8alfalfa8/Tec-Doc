# ◆ Playwrightの構築・運用・使用概要

以下は **Linux環境を前提**にした
**Playwright の構築・運用・使用方法の完全ガイド**です。
（※ これまでのご相談内容から、**CI/CD（GitLab / Jenkins）・品質管理・金融/公共向け厳格運用**を意識した構成で整理しています）

---

## 1. Playwrightとは（位置づけ）

### 1.1 概要

Playwright は Microsoft が提供する **E2E（End-to-End）テスト自動化ツール**です。

| 項目     | 内容                                             |
| ------ | ---------------------------------------------- |
| 対応ブラウザ | Chromium / Firefox / WebKit                    |
| 実行方式   | Headless / Headed                              |
| 言語     | TypeScript / JavaScript / Python / Java / .NET |
| 主用途    | Web UIのE2Eテスト、自動回帰テスト                          |
| 特徴     | 高速・安定、Auto-wait、並列実行、Trace取得                   |

---

### 1.2 他ツールとの比較（簡易）

| ツール            | 特徴             | 向き           |
| -------------- | -------------- | ------------ |
| Selenium       | 実績豊富だが不安定になりがち | 既存資産         |
| Cypress        | 開発者向け、Chrome中心 | SPA中心        |
| **Playwright** | **安定・高速・CI向き** | **大規模/厳格運用** |

---

## 2. 標準アーキテクチャ（推奨）

```
[ GitLab / GitHub ]
        |
        v
[ CI (Jenkins / GitLab CI) ]
        |
        v
[ Playwright Test ]
   ├─ Chromium
   ├─ Firefox
   └─ WebKit
        |
        v
[ Test Report / Trace / Artifact ]
```

---

## 3. Playwright 構築手順（Linux）

### 3.1 前提条件

| 項目      | 推奨                    |
| ------- | --------------------- |
| OS      | RHEL / Rocky / Ubuntu |
| Node.js | 18 LTS以上              |
| npm     | Node同梱                |
| CPU     | 2core以上               |
| メモリ     | 4GB以上（CI並列時は8GB）      |

---

### 3.2 Node.js インストール（例）

```bash
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
node -v
npm -v
```

---

### 3.3 Playwright 初期化

```bash
mkdir playwright-test
cd playwright-test
npm init playwright@latest
```

#### 初期化時の選択（推奨）

```
✔ TypeScript
✔ tests フォルダ
✔ GitHub Actions → No（CIは後で定義）
✔ Install Playwright browsers
```

---

### 3.4 ディレクトリ構成（標準）

```
playwright-test/
├─ playwright.config.ts
├─ package.json
├─ tests/
│   ├─ login.spec.ts
│   ├─ order.spec.ts
│   └─ admin/
├─ test-results/
├─ playwright-report/
└─ .gitignore
```

---

## 4. Playwright 設定（重要）

### 4.1 playwright.config.ts（標準例）

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30 * 1000,
  retries: 1,
  workers: 4,

  reporter: [
    ['html', { open: 'never' }],
    ['list']
  ],

  use: {
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',
  },

  projects: [
    { name: 'Chromium', use: { browserName: 'chromium' }},
    { name: 'Firefox',  use: { browserName: 'firefox' }},
    { name: 'WebKit',   use: { browserName: 'webkit' }},
  ],
});
```

---

## 5. テスト実装方法

### 5.1 基本テスト例

```ts
import { test, expect } from '@playwright/test';

test('ログイン成功', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.fill('#user', 'test');
  await page.fill('#password', 'password');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL(/dashboard/);
});
```

---

### 5.2 金融・公共向けで重要な観点

| 観点       | 実装例                    |
| -------- | ---------------------- |
| タイムアウト管理 | 明示的wait禁止（auto-wait活用） |
| データ分離    | テスト専用ID                |
| 冪等性      | 毎回初期状態から開始             |
| 証跡       | Trace / Screenshot保存   |

---

## 6. 運用設計（非常に重要）

### 6.1 運用ポリシー

| 項目      | 方針        |
| ------- | --------- |
| 実行タイミング | PR / 夜間回帰 |
| ブラウザ    | 本番同等      |
| 失敗時     | Trace確認必須 |
| 成功基準    | Flaky 0   |

---

### 6.2 テスト分類

| 種別         | 実行頻度  |
| ---------- | ----- |
| Smoke      | 毎PR   |
| Regression | 夜間    |
| Full E2E   | リリース前 |

---

## 7. CI/CD 連携

### 7.1 GitLab CI 例

```yaml
playwright_test:
  image: mcr.microsoft.com/playwright:v1.41.0-jammy
  script:
    - npm ci
    - npx playwright test
  artifacts:
    when: always
    paths:
      - playwright-report
      - test-results
```

---

### 7.2 Jenkins 例（Declarative）

```groovy
stage('Playwright Test') {
  steps {
    sh 'npm ci'
    sh 'npx playwright test'
  }
  post {
    always {
      archiveArtifacts artifacts: 'playwright-report/**'
    }
  }
}
```

---

## 8. 障害対応・トラブルシュート

| 問題         | 対処              |
| ---------- | --------------- |
| Flakyテスト   | retries + Trace |
| Headless差異 | headed実行        |
| CIで失敗      | docker image固定  |
| タイムアウト     | UI変更確認          |

---

## 9. セキュリティ・監査対応

| 項目   | 対策       |
| ---- | -------- |
| 認証情報 | Secret管理 |
| ログ   | マスキング    |
| 実行証跡 | レポート保管   |
| 権限   | CI実行限定   |

---

## 10. 成果物一覧（プロジェクト納品レベル）

* Playwright構築手順書
* playwright.config.ts
* テスト設計書（観点表）
* テストケース一覧
* CI連携定義
* 運用Runbook
* 障害対応手順書

---
