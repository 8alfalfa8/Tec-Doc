# ◆ Playwrightの構築・運用・使用概要

以下は **Linux環境を前提**にした
**Playwright の構築・運用・使用方法の完全ガイド**です。<br>
（※ **CI/CD（GitLab / Jenkins）・品質管理・金融/公共向け厳格運用**を意識した構成で整理しています）

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



# ◆ 金融・公共向け E2E試験計画書（Playwright）

## 1. 目的

本計画書は、金融機関・公共機関向け業務システムにおいて、Playwright を用いた E2E（End-to-End）試験を実施するための計画・方針・体制・手順を定義することを目的とする。

特に以下を重視する。

* 業務シナリオの完全性担保
* 本番同等性（環境・設定・データ）
* 監査対応可能な証跡取得
* Flakyテスト排除による再現性確保

---

## 2. 適用範囲

| 項目     | 内容                          |
| ------ | --------------------------- |
| 対象システム | Web業務システム（内部職員向け／外部利用者向け）   |
| 対象環境   | 検証環境 / 総合試験環境 / ステージング      |
| 対象ブラウザ | Chromium / Firefox / WebKit |
| 対象外    | 単体試験・API単体試験（別計画書で定義）       |

---

## 3. 試験方針（金融・公共向け）

### 3.1 基本方針

* 手動試験で実施していた **業務シナリオをE2Eで完全再現**する
* UI操作結果だけでなく **業務データの整合性**を確認する
* CI/CD上で **常時再実行可能**であること

### 3.2 禁止事項

* sleep / 固定待機時間の使用
* 本番データの流用
* 1テスト内で複数業務シナリオを混在させる実装

---

## 4. 試験レベルと位置づけ

| 試験レベル          | 目的       | 実施主体  |
| -------------- | -------- | ----- |
| Smoke E2E      | サービス稼働確認 | CI自動  |
| Regression E2E | 機能退行防止   | 夜間自動  |
| Full E2E       | 業務担保     | リリース前 |

---

## 5. 試験対象業務シナリオ

### 5.1 代表的業務シナリオ例

| No | 業務 | シナリオ概要      |
| -- | -- | ----------- |
| 1  | 認証 | ログイン → 権限判定 |
| 2  | 登録 | 新規登録 → 承認   |
| 3  | 更新 | 情報更新 → 反映確認 |
| 4  | 照会 | 条件検索 → 一覧表示 |
| 5  | 取消 | 業務取消 → 状態確認 |

---

## 6. 試験観点（重要）

### 6.1 業務観点

* 正常系業務フロー
* 業務エラー時の復旧可否
* 冪等性（再実行時の結果一致）

### 6.2 非機能観点

| 観点     | 内容         |
| ------ | ---------- |
| 可用性    | 再実行成功率100% |
| 操作性    | 画面遷移・入力制御  |
| セキュリティ | 認可・セッション   |
| 監査     | 操作証跡・ログ    |

---

## 7. テストデータ設計

### 7.1 テストデータ方針

* E2E専用テストユーザーを使用
* テストごとにデータ初期化
* 本番同等データ構造（匿名化）

### 7.2 データ管理

| 項目  | 方法           |
| --- | ------------ |
| 初期化 | API / DBリセット |
| 分離  | テストIDプレフィックス |
| 保全  | CI完了時自動削除    |

---

## 8. 実行環境

| 項目   | 内容                  |
| ---- | ------------------- |
| OS   | Linux               |
| 実行基盤 | GitLab CI / Jenkins |
| コンテナ | Playwright公式Image   |
| 並列実行 | ブラウザ単位              |

---

## 9. 証跡・成果物管理（監査対応）

### 9.1 取得対象

* HTML Test Report
* Screenshot（失敗時）
* Trace（初回失敗）
* 実行ログ

### 9.2 保管方針

| 成果物   | 保存期間 |
| ----- | ---- |
| 試験結果  | 1年   |
| Trace | 3ヶ月  |
| ログ    | 1年   |

---

## 10. 合否判定基準

| 項目    | 基準   |
| ----- | ---- |
| 試験成功率 | 100% |
| Flaky | 0件   |
| 重大障害  | 0件   |
| 業務影響  | なし   |

---

## 11. 障害対応・是正プロセス

1. 試験失敗検知
2. Trace / Screenshot確認
3. 原因分類（環境／実装／仕様）
4. 是正対応
5. 再試験・証跡更新

---

## 12. 体制・役割

| 役割    | 責務      |
| ----- | ------- |
| QA責任者 | 承認・合否判定 |
| 自動化担当 | 実装・保守   |
| 業務担当  | シナリオ確認  |

---

## 13. リスクと対策

| リスク     | 対策           |
| ------- | ------------ |
| UI変更頻発  | PageObject導入 |
| Flaky増加 | Trace分析ルール   |
| 実行時間増大  | 並列制御         |

---

## 14. 付録

* Playwright設定ファイル
* E2Eテストケース一覧
* CI定義ファイル
* 運用Runbook

---

# ◆ Flaky撲滅運用ルール（金融・公共向け / Playwright）

## 1. 目的

本ルールは、金融機関・公共機関向けシステムにおける E2E 自動試験（Playwright）で発生する Flaky（不安定テスト）を根絶し、
**再現性100%・監査耐性・自動判定可能な試験運用**を実現することを目的とする。

---

## 2. Flakyの定義（公式定義）

以下のいずれかに該当するテストを Flaky と定義する。

| No | 判定条件                  |
| -- | --------------------- |
| 1  | 同一コード・同一環境で成功/失敗が変動する |
| 2  | 再実行により成功するが原因不明       |
| 3  | タイミング依存（sleep 等）を含む   |
| 4  | UI描画・非同期処理に依存する       |

※ 金融・公共案件では **Flaky = 不合格** とする

---

## 3. 基本原則（金融・公共向け三原則）

1. **再実行で直る試験は不良品**
2. **原因不明の成功は認めない**
3. **sleep は原則禁止**

---

## 4. 設計段階ルール（最重要）

### 4.1 テスト設計ルール

| 項目    | ルール               |
| ----- | ----------------- |
| テスト粒度 | 1業務シナリオ = 1テスト    |
| 独立性   | テスト間で状態共有禁止       |
| 冪等性   | 何度実行しても同一結果       |
| 前提条件  | setup/teardownで明示 |

---

### 4.2 Locator設計ルール

| NG        | OK           |
| --------- | ------------ |
| CSS階層     | data-testid  |
| nth-child | role / label |
| text完全一致  | 正規表現         |

```ts
page.getByTestId('login-button')
page.getByRole('button', { name: /ログイン/ })
```

---

## 5. 実装ルール（厳格）

### 5.1 禁止事項

* `page.waitForTimeout()`
* 固定秒数待機
* try-catchでの握りつぶし
* if文での結果分岐合格

---

### 5.2 必須実装

| 項目        | 内容             |
| --------- | -------------- |
| Auto-wait | Playwright標準利用 |
| Expect    | 必ず検証を記述        |
| Timeout   | configで一元管理    |
| Trace     | on-first-retry |

---

## 6. 環境・データ起因Flaky対策

### 6.1 テストデータルール

| 項目   | ルール       |
| ---- | --------- |
| ユーザー | E2E専用     |
| 同時実行 | データ分離     |
| 初期化  | API/DBで強制 |

---

### 6.2 環境差異対策

| 観点     | 対策             |
| ------ | -------------- |
| ブラウザ   | バージョン固定        |
| CI     | Docker Image固定 |
| ネットワーク | リトライ禁止         |

---

## 7. retries運用ルール（重要）

| 項目      | 方針           |
| ------- | ------------ |
| retries | 最大1回         |
| 目的      | Trace取得のみ    |
| 判定      | retry成功でも不合格 |

※ retriesは **救済ではなく分析手段**

---

## 8. Flaky発生時の是正プロセス（必須）

1. 試験失敗検知
2. retries実行（Trace取得）
3. 原因分類

   * テスト実装
   * 業務仕様
   * 環境
4. 恒久対策実施
5. 再実行（単発禁止）

---

## 9. 原因分類テンプレート

| 分類 | 例          |
| -- | ---------- |
| 実装 | Locator不安定 |
| 業務 | 状態遷移漏れ     |
| 環境 | リソース不足     |
| 外部 | API不安定     |

---

## 10. 合否判定ルール（監査対応）

| 状態      | 判定  |
| ------- | --- |
| 初回成功    | 合格  |
| retry成功 | 不合格 |
| 原因不明    | 不合格 |
| 手動確認    | 不合格 |

---

## 11. KPI・可視化

| 指標     | 目標 |
| ------ | -- |
| Flaky率 | 0% |
| 再試験率   | 0% |
| 平均実行時間 | 安定 |

---

## 12. レビュー・監査対応

* Flaky是正履歴を保存
* Traceを証跡として提出
* ルール違反テストはマージ禁止

---

## 13. 付録

* Playwright config例
* Flaky分析チェックリスト
* CIゲート条件定義

---


