# ◆ Pythonプログラム開発（実践編）

以下、「次のステップ」で挙げた各項目（オブジェクト指向、仮想環境、テスト、Git、Webフレームワーク）について、実践的な教材を整理しました。
基礎編と同様に、コード例を交えながら段階的に学べる構成にしています。

---

## 目次
1. [オブジェクト指向プログラミング](#1-オブジェクト指向プログラミング)
2. [仮想環境（venv）](#2-仮想環境venv)
3. [テスト（unittest / pytest）](#3-テストunittest--pytest)
4. [Gitによるバージョン管理](#4-gitによるバージョン管理)
5. [Webフレームワーク（Flask入門）](#5-webフレームワークflask入門)

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

### 1.4 演習：簡易ショッピングカート
以下の要件を満たすクラスを作成してください。
- `Product`クラス（名前、価格、在庫数）
- `Cart`クラス（商品と数量を管理、合計金額計算、在庫確認）
- `Order`クラス（カートから注文を作成、注文番号発行）

---

## 2. 仮想環境（venv）

### 2.1 なぜ仮想環境が必要か
- プロジェクトごとに異なるバージョンのライブラリを使用できる
- システム全体のPython環境を汚染しない
- 依存関係の競合を防止する

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

### 2.4 仮想環境の無効化と削除
```bash
# 仮想環境を終了
deactivate

# 仮想環境の削除（ディレクトリごと削除）
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
```

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

---

## 3. テスト（unittest / pytest）

作成中

## 4. Gitによるバージョン管理

作成中

## 5. Webフレームワーク（Flask入門）

作成中
