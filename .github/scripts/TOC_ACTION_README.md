# 📖 Markdown 目次自動更新 GitHub Action

`.md` ファイルが作成・更新されると、目次（TOC）と「目次に戻る」リンクを自動で生成・更新します。

---

## 動作概要

| タイミング | 処理内容 |
|---|---|
| `.md` ファイルの push / PR | 変更されたファイルを検出 |
| スクリプト実行 | 目次を再生成・既存目次を上書き更新 |
| 変更があった場合 | `[skip ci]` タグ付きで自動コミット |

---

## ファイル構成

```
.github/
├── workflows/
│   └── update-toc.yml       # GitHub Actions ワークフロー
└── scripts/
    └── update_toc.py        # 目次生成・更新スクリプト
```

---

## カスタマイズ方法

### GitHub Variables で設定（推奨）

リポジトリの **Settings → Variables → Actions** で以下の変数を設定できます。

| 変数名 | デフォルト値 | 説明 |
|---|---|---|
| `TOC_LEVEL` | `2` | 目次の基準見出しレベル（1=`#`, 2=`##`, 3=`###`） |
| `BACK_LABEL` | `🔙 目次に戻る` | 「目次に戻る」リンクのラベルテキスト |
| `EXCLUDE_FILES` | （空） | 除外するファイル（カンマ区切り、例: `CHANGELOG.md,docs/api.md`） |

### ワークフロー直接編集

`update-toc.yml` の `env` セクションをデフォルト値ごと変更することもできます。

```yaml
env:
  TOC_LEVEL: "3"            # ### レベルを基準に
  BACK_LABEL: "⬆ トップへ"  # ラベルを変更
  EXCLUDE_FILES: "README.md" # README は除外
```

---

## 目次の仕様

### 生成される目次

```markdown
## <a id="index"></a>📖 目次

- [セクション1](#セクション1)
  - [サブセクション1-1](#サブセクション1-1)
- [セクション2](#セクション2)
```

### 「目次に戻る」リンク

各 `TOC_LEVEL` 見出しのセクション末尾（次の見出しの直前）に自動挿入されます。

```markdown
[🔙 目次に戻る](#index)
```

### 既存の目次・リンクの扱い

- 既存の `<a id="index">` を含む目次セクションを検出して **上書き更新**
- 既存の「目次に戻る」リンクを除去してから **再挿入**（重複しない）

---

## ローカルで手動実行

```bash
# 単一ファイル
python .github/scripts/update_toc.py --files "docs/guide.md" --level 2

# 複数ファイル
python .github/scripts/update_toc.py \
  --files "README.md docs/guide.md" \
  --level 2 \
  --back-label "🔙 目次に戻る" \
  --exclude "CHANGELOG.md"
```

---

## 必要な権限

ワークフローが自動コミットするため、以下の設定が必要です。

**Settings → Actions → General → Workflow permissions**  
→ **Read and write permissions** を選択

---

## 使用している Action

| Action | 用途 |
|---|---|
| `actions/checkout@v4` | リポジトリのチェックアウト |
| `actions/setup-python@v5` | Python 環境のセットアップ |
| `tj-actions/changed-files@v44` | 変更された `.md` ファイルの検出 |
| `stefanzweifel/git-auto-commit-action@v5` | 更新内容の自動コミット |
