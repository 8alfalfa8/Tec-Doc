# ◆ Pythonプログラム開発（実践編）

以下、「次のステップ」で挙げた各項目（オブジェクト指向、仮想環境、テスト、Git、Webフレームワーク）について、実践的な教材を整理しました。
基礎編と同様に、コード例を交えながら段階的に学べる構成にしています。

---

## <a id="index"></a>📖 目次

- [1. オブジェクト指向プログラミング](#1-オブジェクト指向プログラミング)
  - [1.1 クラスとインスタンス](#11-クラスとインスタンス)
  - [1.2 継承](#12-継承)
  - [1.3 カプセル化](#13-カプセル化)
  - [1.4 演習：簡易ショッピングカート](#14-演習簡易ショッピングカート)
- [2. 仮想環境venv](#2-仮想環境venv)
  - [2.1 なぜ仮想環境が必要か](#21-なぜ仮想環境が必要か)
  - [2.2 仮想環境の作成と有効化](#22-仮想環境の作成と有効化)
  - [2.3 パッケージの管理](#23-パッケージの管理)
  - [2.5 実践的な運用](#25-実践的な運用)
- [3. テスト（unittest / pytest）](#3-テストunittest--pytest)
  - [3.1 unittest（標準ライブラリ）](#31-unittest標準ライブラリ)
  - [3.2 pytest（よりシンプルなテスト）](#32-pytestよりシンプルなテスト)
  - [3.3 テスト駆動開発（TDD）の流れ](#33-テスト駆動開発TDDの流れ)
- [4. gitによるバージョン管理](#4-gitによるバージョン管理)
  - [4.1 基本設定](#41-基本設定)
  - [4.2 ローカルリポジトリの基本操作](#42-ローカルリポジトリの基本操作)
  - [4.3 ブランチ操作](#43-ブランチ操作)
  - [4.4 リモートリポジトリ（GitHub/GitLab）](#44-リモートリポジトリGitHubGitLab)
  - [4.6 .gitignoreの例](#46-gitignoreの例)
- [5. webフレームワークflask入門](#5-webフレームワークflask入門)
  - [5.1 環境準備](#51-環境準備)
  - [5.2 最小限のWebアプリケーション](#52-最小限のWebアプリケーション)
  - [5.3 テンプレート（Jinja2）](#53-テンプレートJinja2)
  - [5.4 フォーム処理とリダイレクト](#54-フォーム処理とリダイレクト)
  - [5.5 データベース連携（SQLite + SQLAlchemy）](#55-データベース連携SQLite--SQLAlchemy)
  - [5.6 演習：簡易ブログアプリ](#56-演習簡易ブログアプリ)
- [本教材編集履歴](#本教材編集履歴)

---

## 1. オブジェクト指向プログラミング

### 1.1 クラスとインスタンス
オブジェクト指向は、データ（属性）と処理（メソッド）をひとまとめにした「クラス」を設計し、それを元に「インスタンス」を作成してプログラムを組み立てる手法です。

```python
class User:
    """ユーザーを表すクラス"""
    
    # クラス変数（すべてのインスタンスで共有）
    user_count = 0
    
    def __init__(self, name, age):
        """コンストラクタ：インスタンス初期化"""
        # インスタンス変数
        self.name = name
        self.age = age
        User.user_count += 1
    
    def greet(self):
        """挨拶メソッド"""
        return f"こんにちは、{self.name}です。{self.age}歳です。"
    
    def have_birthday(self):
        """年齢を1つ増やす"""
        self.age += 1
        print(f"{self.name}が{self.age}歳になりました！")

# インスタンスの作成
user1 = User("Alice", 25)
user2 = User("Bob", 30)

# メソッドの呼び出し
print(user1.greet())  # こんにちは、Aliceです。25歳です。
user2.have_birthday()  # Bobが31歳になりました！

# クラス変数の参照
print(f"総ユーザー数: {User.user_count}")  # 総ユーザー数: 2
```

[🔝 目次に戻る](#index)

---

### 1.2 継承
既存のクラスを基に、機能を拡張した新しいクラスを作成します。

```python
class AdminUser(User):
    """管理者ユーザークラス（Userを継承）"""
    
    def __init__(self, name, age, role="admin"):
        # 親クラスのコンストラクタを呼び出し
        super().__init__(name, age)
        self.role = role
        self.permissions = ["read", "write", "delete"]
    
    # メソッドのオーバーライド
    def greet(self):
        return f"管理者: {self.name}です。権限: {self.permissions}"
    
    def delete_user(self, target_user):
        """ユーザー削除（管理者専用機能）"""
        print(f"{self.name}が{target_user.name}を削除しました")

# 使用例
admin = AdminUser("Charlie", 35)
print(admin.greet())  # 管理者: Charlieです。権限: ['read', 'write', 'delete']
admin.delete_user(user1)  # CharlieがAliceを削除しました
```

[🔝 目次に戻る](#index)

---

### 1.3 カプセル化
属性を外部から直接アクセスできないように保護します。Pythonでは命名規則で表現します。

```python
class BankAccount:
    """銀行口座クラス（カプセル化の例）"""
    
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance  # 先頭に__でプライベート変数（名前修飾）
    
    def deposit(self, amount):
        """入金"""
        if amount > 0:
            self.__balance += amount
            return True
        return False
    
    def withdraw(self, amount):
        """出金"""
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            return True
        return False
    
    def get_balance(self):
        """残高確認（getter）"""
        return self.__balance
    
    @property
    def balance_info(self):
        """プロパティを使用した読み取り専用アクセス"""
        return f"{self.owner}の残高: {self.__balance}円"

account = BankAccount("Taro", 100000)
account.deposit(50000)
print(account.balance_info)  # Taroの残高: 150000円
# print(account.__balance)  # AttributeError（直接アクセス不可）
```

[🔝 目次に戻る](#index)

---

### 1.4 演習：簡易ショッピングカート
以下の要件を満たすクラスを作成してください。
- `Product`クラス（名前、価格、在庫数）
- `Cart`クラス（商品と数量を管理、合計金額計算、在庫確認）
- `Order`クラス（カートから注文を作成、注文番号発行）

[🔝 目次に戻る](#index)

---

## 2. 仮想環境（venv）

### 2.1 なぜ仮想環境が必要か
- プロジェクトごとに異なるバージョンのライブラリを使用できる
- システム全体のPython環境を汚染しない
- 依存関係の競合を防止する

[🔝 目次に戻る](#index)

---

### 2.2 仮想環境の作成と有効化
```bash
# プロジェクトディレクトリに移動
cd my_project

# 仮想環境の作成（python3 -m venv 環境名）
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 有効化が成功すると、プロンプトに (venv) が表示される
(venv) $ 
```

[🔝 目次に戻る](#index)

---

### 2.3 パッケージの管理
```bash
# 必要なパッケージのインストール
pip install requests pandas numpy

# インストール済みパッケージの一覧表示
pip list

# 依存関係をファイルに出力（再現性の確保）
pip freeze > requirements.txt

# 別の環境で同じ依存関係を再現
pip install -r requirements.txt
```

[🔝 目次に戻る](#index)

---

### 2.4 仮想環境の無効化と削除
```bash
# 仮想環境を終了
deactivate

# 仮想環境の削除（ディレクトリごと削除）
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
```

[🔝 目次に戻る](#index)

---

### 2.5 実践的な運用
```bash
# プロジェクト構成例
my_project/
├── venv/                 # 仮想環境（.gitignoreに追加）
├── requirements.txt      # 依存関係リスト
├── src/                  # ソースコード
│   └── main.py
└── tests/                # テストコード
```

[🔝 目次に戻る](#index)

---

## 3. テスト（unittest / pytest）

### 3.1 unittest（標準ライブラリ）
Python標準のテストフレームワークです。

```python
# calculator.py
class Calculator:
    @staticmethod
    def add(a, b):
        return a + b
    
    @staticmethod
    def subtract(a, b):
        return a - b
    
    @staticmethod
    def multiply(a, b):
        return a * b
    
    @staticmethod
    def divide(a, b):
        if b == 0:
            raise ValueError("0での除算はできません")
        return a / b
```

```python
# test_calculator.py
import unittest
from calculator import Calculator

class TestCalculator(unittest.TestCase):
    """Calculatorクラスのテスト"""
    
    def setUp(self):
        """各テストメソッド実行前に呼び出される"""
        self.calc = Calculator()
        print("テスト準備完了")
    
    def tearDown(self):
        """各テストメソッド実行後に呼び出される"""
        print("テスト終了")
    
    def test_add(self):
        """加算のテスト"""
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)
        self.assertEqual(self.calc.add(0, 0), 0)
    
    def test_subtract(self):
        """減算のテスト"""
        self.assertEqual(self.calc.subtract(5, 3), 2)
        self.assertEqual(self.calc.subtract(0, 5), -5)
    
    def test_multiply(self):
        """乗算のテスト"""
        self.assertEqual(self.calc.multiply(4, 3), 12)
        self.assertEqual(self.calc.multiply(0, 10), 0)
    
    def test_divide(self):
        """除算のテスト"""
        self.assertEqual(self.calc.divide(10, 2), 5)
        self.assertAlmostEqual(self.calc.divide(7, 3), 2.33333333, places=6)
    
    def test_divide_by_zero(self):
        """0除算のテスト"""
        with self.assertRaises(ValueError):
            self.calc.divide(10, 0)

if __name__ == "__main__":
    unittest.main()
```

実行方法：
```bash
python -m unittest test_calculator.py
python -m unittest discover  # すべてのテストを自動発見
```

[🔝 目次に戻る](#index)

---

### 3.2 pytest（よりシンプルなテスト）
pytestはより簡潔にテストを記述できる人気のフレームワークです。

```bash
pip install pytest
```

```python
# test_calculator_pytest.py
import pytest
from calculator import Calculator

calc = Calculator()

def test_add():
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0

def test_divide():
    assert calc.divide(10, 2) == 5
    assert calc.divide(7, 3) == pytest.approx(2.333333, 0.0001)

def test_divide_by_zero():
    with pytest.raises(ValueError, match="0での除算はできません"):
        calc.divide(10, 0)

# パラメータ化テスト（複数の入力値を一度にテスト）
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 6),
    (0, 5, 0),
    (-3, 4, -12),
])
def test_multiply_parametrized(a, b, expected):
    assert calc.multiply(a, b) == expected
```

実行：
```bash
pytest
pytest -v  # 詳細表示
pytest -k "add"  # 特定のテストのみ実行
```

[🔝 目次に戻る](#index)

---

### 3.3 テスト駆動開発（TDD）の流れ
1. **Red**：失敗するテストを先に書く
2. **Green**：テストが通る最低限のコードを書く
3. **Refactor**：コードを改善する（テストが通ることを確認）

[🔝 目次に戻る](#index)

---

## 4. Gitによるバージョン管理

### 4.1 基本設定
```bash
# ユーザー情報の設定（初回のみ）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 設定確認
git config --list
```

[🔝 目次に戻る](#index)

---

### 4.2 ローカルリポジトリの基本操作
```bash
# プロジェクトをGit管理下に置く
cd my_project
git init

# ステータス確認
git status

# ファイルをステージングに追加
git add file.py
git add .  # すべての変更を追加

# コミット（スナップショットを作成）
git commit -m "Initial commit: add basic calculator"

# 変更履歴の確認
git log --oneline  # 簡潔に表示
git log --graph --pretty=oneline  # グラフ表示
```

[🔝 目次に戻る](#index)

---

### 4.3 ブランチ操作
```bash
# ブランチの作成
git branch feature/add-divide

# ブランチの切り替え
git checkout feature/add-divide
# または（Git 2.23以降）
git switch feature/add-divide

# ブランチの作成と切り替えを同時に
git checkout -b feature/add-divide

# ブランチ一覧
git branch -a

# マージ（ブランチの統合）
git checkout main
git merge feature/add-divide

# ブランチの削除
git branch -d feature/add-divide
```

[🔝 目次に戻る](#index)

---

### 4.4 リモートリポジトリ（GitHub/GitLab）
```bash
# リモートリポジトリの追加
git remote add origin https://github.com/username/my_project.git

# プッシュ（ローカルの変更をリモートに反映）
git push -u origin main

# プル（リモートの変更をローカルに取得）
git pull origin main

# クローン（リモートから新規取得）
git clone https://github.com/username/my_project.git
```

[🔝 目次に戻る](#index)

---

### 4.5 実践的なワークフロー
```bash
# 1. 最新の状態を取得
git checkout main
git pull origin main

# 2. 作業用ブランチを作成
git checkout -b feature/add-login

# 3. コーディング（変更をコミット）
git add .
git commit -m "Add login functionality"

# 4. さらに修正
git add .
git commit -m "Add password validation"

# 5. リモートにプッシュ
git push origin feature/add-login

# 6. プルリクエストを作成（Web上で）
# 7. レビュー後、mainにマージ
```

[🔝 目次に戻る](#index)

---

### 4.6 .gitignoreの例
```
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
env/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# 環境変数
.env
```

[🔝 目次に戻る](#index)

---

## 5. Webフレームワーク（Flask入門）

### 5.1 環境準備
```bash
mkdir flask_app
cd flask_app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install flask
```

[🔝 目次に戻る](#index)

---

### 5.2 最小限のWebアプリケーション
```python
# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Flaskアプリケーションの作成
app = Flask(__name__)

# ルーティングとビュー関数
@app.route('/')
def home():
    return '<h1>Hello, Flask!</h1><p>ようこそ</p>'

@app.route('/user/<name>')
def user_profile(name):
    return f'<h2>{name}さんのページ</h2>'

# クエリパラメータの取得
@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    return f'検索キーワード: {keyword}'

# 起動
if __name__ == '__main__':
    app.run(debug=True)
```

実行：
```bash
python app.py
# http://127.0.0.1:5000 にアクセス
```

[🔝 目次に戻る](#index)

---

### 5.3 テンプレート（Jinja2）
ディレクトリ構成：
```
flask_app/
├── app.py
├── templates/
│   ├── base.html
│   └── index.html
└── static/
    └── style.css
```

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Flask App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <nav>
        <a href="{{ url_for('home') }}">ホーム</a>
        <a href="{{ url_for('task_list') }}">タスク一覧</a>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

```html
<!-- templates/index.html -->
{% extends "base.html" %}

{% block title %}タスク管理アプリ{% endblock %}

{% block content %}
<h1>タスク一覧</h1>
<form method="POST" action="{{ url_for('add_task') }}">
    <input type="text" name="task" required>
    <button type="submit">追加</button>
</form>

<ul>
    {% for task in tasks %}
    <li>
        {{ task }}
        <a href="{{ url_for('delete_task', task_id=loop.index0) }}">削除</a>
    </li>
    {% endfor %}
</ul>
{% endblock %}
```

[🔝 目次に戻る](#index)

---

### 5.4 フォーム処理とリダイレクト
```python
# app.py（拡張版）
from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # セッション用の秘密鍵

# メモリ上にデータを保存（簡易的なデータベース代わり）
tasks = []

@app.route('/tasks')
def task_list():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task = request.form.get('task')
    if task:
        tasks.append(task)
    return redirect(url_for('task_list'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
    return redirect(url_for('task_list'))

# JSON API（REST APIの例）
@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json()
    task = data.get('task')
    if task:
        tasks.append(task)
        return jsonify({'status': 'success', 'task': task}), 201
    return jsonify({'status': 'error'}), 400
```

[🔝 目次に戻る](#index)

---

### 5.5 データベース連携（SQLite + SQLAlchemy）
```bash
pip install flask-sqlalchemy
```

```python
# app_with_db.py
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# モデル定義
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.title}>'

# データベース作成（初回のみ）
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('tasks.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    if title:
        task = Task(title=title)
        db.session.add(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('index'))
```

[🔝 目次に戻る](#index)

---

### 5.6 演習：簡易ブログアプリ
以下の機能を持つブログアプリを作成してください。
- 記事一覧画面（タイトル、作成日時）
- 記事詳細画面（本文も表示）
- 新規記事投稿画面（タイトル、本文）
- 記事編集・削除機能
- （発展）ユーザー認証機能

[🔝 目次に戻る](#index)

---

## おわりに

この教材を通じて、Pythonの基礎から実践的な開発手法までを学びました。各セクションは独立しているので、必要に応じて参照しながら学習を進めてください。

---

## 本教材編集履歴

|作成者|バージョン| 日付 | 内容 |
|------|-------|----------|----------|
| Y.F  |1.0.0  |2026-03-31|新規作成|

repository: [https://github.com/8alfalfa8/Tec-Doc](https://github.com/8alfalfa8/Tec-Doc)

[🔝 目次に戻る](#index)

---
