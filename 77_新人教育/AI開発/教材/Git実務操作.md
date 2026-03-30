# ◆ Git実務操作

**Git実務操作**は、AI開発を含むソフトウェア開発に不可欠なバージョン管理スキルです。Gitによりコードやドキュメントの履歴を安全に管理し、作業の可視化と品質向上を実現します。基本操作（add／commit／log／diff）や、リモート連携（clone／pull／push）、ブランチ運用によりチーム開発を効率化します。さらにGitHub等と連携したPR・コードレビュー、CI/CDによる自動化も重要です。AI開発では、プロンプトやデータ、モデル設定も含めて管理することで再現性を確保でき、AIDDにおいても中核的役割を担います。

本教材では、実務で必要なコマンドに絞り習得します。

---

## <a id="index"></a>📖 目次

- [前提](#前提)
- [1. 基本の流れ（毎日やること）](#1-基本の流れ毎日やること)
- [2. 実務で絶対に使う緊急時コマンド](#2-実務で絶対に使う緊急時コマンド)
- [3. ブランチ操作（レビュー対応など）](#3-ブランチ操作レビュー対応など)
- [4. 履歴確認](#4-履歴確認)
- [5. よく使うオプション・テクニック集](#5-よく使うオプションテクニック集)
- [本教材編集履歴](#本教材編集履歴)

---

## 前提
- [Github]はユーザ登録済みとします。
- [Git]はインストール済みとします。
- ターミナル（コマンドプロンプト）で操作します。

[Github]:https://github.com/
[Git]:https://git-scm.com/

[🔝 目次に戻る](#index)

---

## 1. 基本の流れ（毎日やること）

### リポジトリを持ってくる（初回のみ）
```bash
# クローン
git clone https://github.com/ユーザー名/リポジトリ名.git

# クローンしたディレクトリに移動
cd リポジトリ名
```

### 作業を始める前（毎朝やること）
```bash
# 最新の状態に更新
git pull origin main
# main の部分は master や develop の場合もある
```

### 作業ブランチを作成して移動
```bash
# ブランチを作成して同時に移動
git checkout -b feature/作業内容

# 例: git checkout -b feature/add-login-function
```

### ファイルを変更したら（1日の終わり or 区切りで）
```bash
# 変更状態を確認
git status

# 変更したファイルをステージに追加
git add ファイル名
# 全部追加する場合
git add .

# コミット
git commit -m "〇〇を追加した"
```

### リモートにプッシュ
```bash
# 初めてプッシュする場合
git push origin HEAD

# 2回目以降（同じブランチで作業中）
git push
```

[🔝 目次に戻る](#index)

---

## 2. 実務で絶対に使う緊急時コマンド

### 直前のコミットを取り消したい（まだプッシュしてない場合）
```bash
# コミットだけ取り消して変更は残す
git reset --soft HEAD^

# コミットも変更も全部消す（要注意！）
git reset --hard HEAD^
```

### 間違えて add してしまった
```bash
# ステージから下ろす（ファイルの変更は残る）
git reset HEAD ファイル名
```

### 今の変更を一時的に隠したい（別のブランチで緊急対応）
```bash
# 一時退避
git stash

# 戻す
git stash pop
```

### コンフリクト（競合）が起きた
1. エディタで `<<<<<<<` と `=======` と `>>>>>>>` が入ったファイルを開く
2. 残したい方のコードに修正して保存
3. 以下を実行
```bash
git add 修正したファイル
git commit -m "コンフリクト解消"
```

[🔝 目次に戻る](#index)

---

## 3. ブランチ操作（レビュー対応など）

### 他の人のブランチをローカルに持ってくる
```bash
git fetch origin
git checkout -b ブランチ名 origin/ブランチ名
```

### ブランチを切り替える
```bash
git checkout ブランチ名
```

### ブランチ一覧を見る
```bash
# ローカルのブランチ一覧
git branch

# リモートも含めた一覧
git branch -a
```

[🔝 目次に戻る](#index)

---

## 4. 履歴確認

### コミットログを見る
```bash
# シンプルに見る（実務はこれで十分）
git log --oneline

# グラフ付きで見たい場合
git log --oneline --graph
```

### 誰がいつ何を変えたか見る
```bash
git blame ファイル名
```

[🔝 目次に戻る](#index)

---

## 5. よく使うオプション・テクニック集

### プルするとき、自分のコミットが消えそうで怖い場合
```bash
# 取り込む前にどう変わるか確認
git fetch origin
git log HEAD..origin/main --oneline
```

### リモートのブランチが消えたのでローカルも消したい
```bash
# リモートの追跡が消えたブランチを一括削除
git remote prune origin
```

### 直前のコミットメッセージを間違えた
```bash
git commit --amend -m "正しいメッセージ"
```

## 今日から使えるフロー（1日の流れ）

**朝:**
```bash
git checkout main
git pull origin main
git checkout -b feature/自分の作業
```

**日中:**
```bash
git add .
git commit -m "進捗"
git push origin HEAD  # バックアップ兼共有
```

**夕方（PR出す前）:**
```bash
git checkout main
git pull origin main
git checkout feature/自分の作業
git merge main  # mainの最新を自分のブランチに取り込む
# コンフリクトがあれば解消
git push
```

## $\color{red}{\text{注意：絶対にやってはいけないこと}}$
- `git push -f`（強制プッシュ）を共用ブランチ（main, develop）で実行しない
- コンフリクトを怖がらない（誰でも起きます）

これだけ覚えておけば、ほとんどの現場で通用します。あとは必要に応じて調べながらで大丈夫です。

[🔝 目次に戻る](#index)

---

## 本教材編集履歴

|作成者|バージョン|   日付   |　内容   |
|------|-------|----------|----------|
| Y.F  |1.0.0  |2026-03-31|新規作成|

repository: [https://github.com/8alfalfa8/Tec-Doc](https://github.com/8alfalfa8/Tec-Doc)

[🔝 目次に戻る](#index)

---

