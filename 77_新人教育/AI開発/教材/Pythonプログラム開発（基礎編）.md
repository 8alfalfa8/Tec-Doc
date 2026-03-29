<!-- TOC_START -->
<a id="index"></a>📖 目次

- [📖 目次](#a-idindexa-目次)
- [1.はじめに](#1はじめに)
  - [1.1 目的](#11-目的)
  - [1.2 対象](#12-対象)
- [2.開発環境の準備](#2開発環境の準備)
  - [2.1 Pythonのインストール](#21-pythonのインストール)
  - [2.2 エディタ / IDE](#22-エディタ-ide)
  - [2.3 動作確認](#23-動作確認)
- [3.Pythonの基本文法](#3pythonの基本文法)
  - [3.1 コードの実行方法](#31-コードの実行方法)
  - [3.2 コメント](#32-コメント)
  - [3.3 変数とデータ型](#33-変数とデータ型)
  - [3.4 入力と出力](#34-入力と出力)
- [4.制御構文](#4制御構文)
  - [4.1 条件分岐（if文）](#41-条件分岐if文)
  - [4.2 繰り返し（for文、while文）](#42-繰り返しfor文while文)
- [5.データ構造](#5データ構造)
  - [5.1 リスト（配列）](#51-リスト配列)
  - [5.2 辞書（キーと値のペア）](#52-辞書キーと値のペア)
  - [5.3 その他](#53-その他)
- [6.関数](#6関数)
  - [6.1 定義と呼び出し](#61-定義と呼び出し)
  - [6.2 デフォルト引数](#62-デフォルト引数)
- [7.エラーハンドリング](#7エラーハンドリング)
- [8.ファイル操作](#8ファイル操作)
- [9.モジュールとライブラリ](#9モジュールとライブラリ)
  - [9.1 標準ライブラリの利用](#91-標準ライブラリの利用)
  - [9.2 外部ライブラリのインストール（pip）](#92-外部ライブラリのインストールpip)
- [10.実践演習問題](#10実践演習問題)
  - [問題1：FizzBuzz](#問題1fizzbuzz)
  - [問題2：簡易メモアプリ](#問題2簡易メモアプリ)
- [付録：よく使う便利機能](#付録よく使う便利機能)
- [本教材編集履歴](#本教材編集履歴)
<!-- TOC_END -->

# ◆ Pythonプログラム開発（基礎編）

Pythonは、シンプルで読みやすい文法を持つ汎用プログラミング言語であり、AI開発・データ分析・Web開発など幅広い分野で利用されています。コードの可読性が高く、初心者でも習得しやすい一方で、高度な処理にも対応できる柔軟性を備えている点が特徴です。

基本的な文法は直感的で、変数、条件分岐（if）、繰り返し（for / while）、関数定義（def）などをシンプルに記述できます。また、豊富な標準ライブラリに加え、外部ライブラリも非常に充実しており、数値計算（NumPy）、データ分析（Pandas）、可視化（Matplotlib）、Web開発（Flask、FastAPI）など、多様な用途に対応可能です。

特にAI開発の分野では、Pythonは事実上の標準言語となっています。機械学習や深層学習のフレームワーク（TensorFlow、PyTorch、scikit-learnなど）はPythonを中心に提供されており、モデル構築、学習、評価、デプロイまで一貫して対応できます。また、Jupyter Notebookを活用することで、コード・データ・ドキュメントを一体化した形で扱える点も大きな利点です。

さらに、PythonはLinux環境やクラウド基盤（AWS、GCP、Azure）との親和性も高く、データ処理基盤やAPIサーバーの構築、バッチ処理、自動化スクリプトなどにも広く利用されています。これにより、AI開発だけでなく、システム全体の構築・運用にも対応できる汎用性を持っています。

このようにPythonは、学習のしやすさと実用性を兼ね備えた言語として、AI時代の中核を担う存在です。[Markdown](Markdown基本記法.md)や、[Linux](Linux基本操作.md)、[Git](Git実務操作.md)と並び、AI開発を支える基盤技術の一つとして、今後もその重要性はさらに高まっていきます。

以下は、Pythonプログラム開発の基本を学ぶための新人教育用教材です。  
初心者がつまずきがちなポイントを押さえつつ、実践的な開発の流れを意識した構成にしています。

---

## <a id="index"></a>📖 目次
[🔙 目次に戻る](#index)


- [1.はじめに](#1はじめに)
- [2.開発環境の準備](#2開発環境の準備)
- [3.Pythonの基本文法](#3Pythonの基本文法)
- [4.制御構文](#4制御構文)
- [5.データ構造](#5データ構造)
- [6.関数](#6関数)
- [7.エラーハンドリング](#7エラーハンドリング)
- [8.ファイル操作](#8ファイル操作)
- [9.モジュールとライブラリ](#9モジュールとライブラリ)
- [10.実践演習問題](#10実践演習問題)
- [付録：よく使う便利機能](#付録よく使う便利機能)
- [本教材編集履歴](#本教材編集履歴)

---

[🔙 目次に戻る](#index)


## 1.はじめに

[🔙 目次に戻る](#index)

### 1.1 目的

[🔙 目次に戻る](#index)

- Pythonの基本文法を理解する
- 開発環境で自力でコードを書き、実行できる
- 簡単なプログラムを作成し、デバッグや改良ができる

[🔙 目次に戻る](#index)


### 1.2 対象

[🔙 目次に戻る](#index)

- プログラミング初心者（他言語経験があればなお可）
- Pythonを業務で使う前に基礎を固めたい方

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 2.開発環境の準備

[🔙 目次に戻る](#index)

### 2.1 Pythonのインストール

[🔙 目次に戻る](#index)

- Python公式サイト（[python.org](https://www.python.org/)）から最新の安定版をダウンロード
- インストール時に「Add Python to PATH」にチェック

[🔙 目次に戻る](#index)


### 2.2 エディタ / IDE

[🔙 目次に戻る](#index)

- **推奨：VS Code**（拡張機能「Python」を追加）
- その他：PyCharm Community Edition、Thonny（初学者向け）

[🔙 目次に戻る](#index)


### 2.3 動作確認

[🔙 目次に戻る](#index)

```bash
python --version
```
```bash
python -c "print('Hello, World!')"

[🔙 目次に戻る](#index)

```

[🔙 目次に戻る](#index)

---

[🔙 目次に戻る](#index)


## 3.Pythonの基本文法

[🔙 目次に戻る](#index)

### 3.1 コードの実行方法

[🔙 目次に戻る](#index)

- **インタラクティブモード**：`python` コマンドで対話的に実行
- **スクリプト実行**：`.py` ファイルを作成し `python ファイル名.py`

[🔙 目次に戻る](#index)


### 3.2 コメント

[🔙 目次に戻る](#index)

```python
# これはコメントです
print("Hello")  # 行末コメント
```

[🔙 目次に戻る](#index)


### 3.3 変数とデータ型

[🔙 目次に戻る](#index)

```python
# 数値
age = 25
price = 19.99

# 文字列
name = "Alice"

# 真偽値
is_active = True

# 型の確認
print(type(age))
```

[🔙 目次に戻る](#index)


### 3.4 入力と出力

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)


```python
name = input("名前を入力してください: ")
print(f"こんにちは、{name}さん！")
```

[🔙 目次に戻る](#index)

---

[🔙 目次に戻る](#index)


## 4.制御構文

[🔙 目次に戻る](#index)

### 4.1 条件分岐（if文）

[🔙 目次に戻る](#index)

```python
score = 85

if score >= 90:
    print("優秀")
elif score >= 70:
    print("合格")
else:
    print("要再試験")
```

[🔙 目次に戻る](#index)


### 4.2 繰り返し（for文、while文）

[🔙 目次に戻る](#index)

```python
# for文（リストで反復）
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# rangeを使ったループ
for i in range(5):
    print(i)

# while文
count = 0
while count < 3:
    print(count)
    count += 1
```

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 5.データ構造

[🔙 目次に戻る](#index)

### 5.1 リスト（配列）

[🔙 目次に戻る](#index)

```python
numbers = [1, 2, 3, 4, 5]
numbers.append(6)          # 要素追加
print(numbers[0])          # 1
print(numbers[-1])         # 6（末尾）
```

[🔙 目次に戻る](#index)


### 5.2 辞書（キーと値のペア）

[🔙 目次に戻る](#index)

```python
user = {"name": "Taro", "age": 30}
print(user["name"])
user["email"] = "taro@example.com"
```

[🔙 目次に戻る](#index)


### 5.3 その他

[🔙 目次に戻る](#index)

- タプル：変更不可のリスト `(1, 2, 3)`

[🔙 目次に戻る](#index)

- 集合：重複のないコレクション `{1, 2, 3}`

[🔙 目次に戻る](#index)

---

[🔙 目次に戻る](#index)


## 6.関数

[🔙 目次に戻る](#index)

### 6.1 定義と呼び出し

[🔙 目次に戻る](#index)

```python
def greet(name):
    """挨拶を行う関数（ドキュメント文字列）"""
    return f"Hello, {name}!"

message = greet("Bob")
print(message)
```

[🔙 目次に戻る](#index)


### 6.2 デフォルト引数

[🔙 目次に戻る](#index)

```python
def multiply(a, b=2):
    return a * b

print(multiply(3))   # 6
print(multiply(3, 4))  # 12
```

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 7.エラーハンドリング

[🔙 目次に戻る](#index)

```python
try:
    num = int(input("数字を入力: "))
    result = 10 / num
    print(f"結果: {result}")
except ValueError:
    print("数字ではありません")
except ZeroDivisionError:
    print("0で割ることはできません")
finally:
    print("処理終了")
```

[🔙 目次に戻る](#index)

---

[🔙 目次に戻る](#index)


## 8.ファイル操作

[🔙 目次に戻る](#index)

```python
# 書き込み
with open("sample.txt", "w", encoding="utf-8") as f:
    f.write("こんにちは\n")
    f.write("2行目です")

# 読み込み
with open("sample.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
```

[🔙 目次に戻る](#index)

---

[🔙 目次に戻る](#index)


## 9.モジュールとライブラリ

[🔙 目次に戻る](#index)

### 9.1 標準ライブラリの利用

[🔙 目次に戻る](#index)

```python
import math
import random

print(math.sqrt(16))          # 4.0
print(random.randint(1, 10))  # 1〜10の乱数
```

[🔙 目次に戻る](#index)


### 9.2 外部ライブラリのインストール（pip）

[🔙 目次に戻る](#index)

```bash
pip install requests
```
```python
import requests
response = requests.get("https://api.github.com")
print(response.status_code)
```

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 10.実践演習問題

[🔙 目次に戻る](#index)

### 問題1：FizzBuzz

[🔙 目次に戻る](#index)

1〜100までの数値について、3の倍数なら「Fizz」、5の倍数なら「Buzz」、15の倍数なら「FizzBuzz」、それ以外は数値を表示するプログラムを作成してください。

[🔙 目次に戻る](#index)


### 問題2：簡易メモアプリ

[🔙 目次に戻る](#index)

以下の機能を持つプログラムを作成してください。
- メモを新規追加（ファイルに追記）
- すべてのメモを表示
- メモを削除（全削除で可）

[🔙 目次に戻る](#index)

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 付録：よく使う便利機能

[🔙 目次に戻る](#index)

| 機能 | 例 |
|------|------|
| リスト内包表記 | `[x*2 for x in range(5)]` |
| 三項演算子 | `"ok" if score >= 70 else "ng"` |
| 便利な組み込み関数 | `len()`, `sum()`, `max()`, `sorted()` |

[🔙 目次に戻る](#index)

---

この教材は、1〜2日程度のハンズオン研修や、1週間の自己学習を想定しています。  
各セクションごとに実際にコードを書きながら進めることで、基礎をしっかりと身につけることができます。

---

[🔙 目次に戻る](#index)


## 本教材編集履歴
[🔙 目次に戻る](#index)


|作成者|バージョン|   日付   |　内容   |
|------|-------|----------|----------|
| Y.F  |1.0.0  |2026-03-28|新規作成|

repository: [https://github.com/8alfalfa8/Tec-Doc](https://github.com/8alfalfa8/Tec-Doc)

[🔙 目次に戻る](#index)

---

[🔙 目次に戻る](#index)

