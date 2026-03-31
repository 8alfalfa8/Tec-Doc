# ◆ データ基礎（JSON／DB）

データ基礎（JSON／DB）は、システム開発やAI開発に不可欠な情報管理の基盤です。JSONは軽量で可読性の高いデータ形式で、API連携や設定、AIとのデータ交換に広く利用されます。一方、DBはデータの保存・検索・更新を担い、RDB（MySQL等）とNoSQL（MongoDB等）を用途に応じて使い分けます。これにより、APIで取得したJSONデータの蓄積・加工・分析が可能になります。AI分野では、学習データ管理や推論結果の保存、RAGにおけるデータ統合など、あらゆる工程で重要な役割を果たします。データを正しく扱う力はAI時代の必須スキルです。

本教材ではデータベースの基礎知識を体系的に習得します。

---

## <a id="index"></a>📖 目次
### (基礎編)
- [1. なぜデータ基礎が重要か](#1-なぜデータ基礎が重要か)
- [2. JSONとは（最重要）](#2-JSONとは最重要)
- [3. JSON操作（Python）](#3-JSON操作Python)
- [4. データベースとは](#4-データベースとは)
- [5. DBの種類](#5-DBの種類)
- [6. RDB基礎（重要）](#6-RDB基礎重要)
- [7. 正規化（設計の基礎）](#7-正規化設計の基礎)
- [8. NoSQLとの違い](#8-NoSQLとの違い)
- [9. API × JSON × DBの関係](#9-API--JSON--DBの関係)
- [10. 実装例（Python + DB）](#10-実装例Python--DB)
- [11. ORM（重要概念）](#11-ORM重要概念)
- [12. AI開発とデータ](#12-AI開発とデータ)
- [13. 実務での使い方](#13-実務での使い方)
- [14. よくあるミス](#14-よくあるミス)
- [15. 初心者向け演習](#15-初心者向け演習)
- [16. 重要まとめ](#16-重要まとめ)
- [17. 最重要メッセージ](#17-最重要メッセージ)
- [18. 最終理解](#18-最終理解)

### (上級編)
- [19. SQLiteで学ぶSQL基礎](#19-SQLiteで学ぶSQL基礎)
- [20. RAGのためのベクトルデータベース入門](#20-RAGのためのベクトルデータベース入門)
- [21. 実践：AIアプリケーションでのデータ管理](#21-実践AIアプリケーションでのデータ管理)
- [22. まとめ：データベース選定ガイド](#22-まとめデータベース選定ガイド)
- [23. 次の挑戦：ハンズオン課題](#23-次の挑戦ハンズオン課題)
- [本教材編集履歴](#本教材編集履歴)

---

## 1. なぜデータ基礎が重要か

AI・アプリ・システムはすべて

👉 **データの入出力で成り立つ**

### ■ 例

```text
入力 → 処理 → 出力
```

* 入力：JSON
* 処理：Python / AI
* 出力：JSON / DB保存

### ■ 重要な理解

👉 **「API × DB」＝ システムの本体**

[🔝 目次に戻る](#index)

---

## 2. JSONとは（最重要）

### ■ JSONとは

👉 **データ交換フォーマット（API標準）**

### ■ 基本構造

```json
{
  "name": "Taro",
  "age": 20,
  "isActive": true
}
```

### ■ データ型

| 型      | 例              |
| ------ | -------------- |
| 文字列    | `"text"`       |
| 数値     | `123`          |
| 真偽値    | `true / false` |
| 配列     | `[1,2,3]`      |
| オブジェクト | `{}`           |

### ■ ネスト構造

```json
{
  "user": {
    "name": "Taro",
    "skills": ["Python", "AWS"]
  }
}
```

### ■ ポイント

👉 **JSON = 木構造（ツリー構造）**

[🔝 目次に戻る](#index)

---

## 3. JSON操作（Python）

### ■ 読み取り

```python
import json

data = '{"name":"Taro"}'
obj = json.loads(data)

print(obj["name"])
```

### ■ 書き込み

```python
import json

data = {"name": "Taro"}

json_str = json.dumps(data)
print(json_str)
```

### ■ 実務ポイント

* APIレスポンス処理
* ログ解析
* AI入出力

[🔝 目次に戻る](#index)

---

## 4. データベースとは

### ■ DBとは

👉 **データを保存・管理する仕組み**


### ■ なぜ必要か

* データの永続化
* 検索・更新
* 同時アクセス制御

| 方法 | メリット | デメリット | AI開発での使用場面 |
|:---|:---|:---|:---|
| JSONファイル | 簡単、可読性が高い | 大規模データに非効率、同時アクセス不可 | 設定ファイル、小規模データ |
| **データベース** | 高速検索、同時アクセス、整合性維持 | 学習コスト、セットアップ必要 | **ユーザーデータ、会話履歴、RAG用ナレッジベース** |

[🔝 目次に戻る](#index)

---

## 5. DBの種類

### 5.1 ■ RDB（リレーショナルDB）

- **特徴**: 表形式でデータを管理。厳格なスキーマ（構造）を持つ
- **代表例**: **SQLite**（学習用）、**PostgreSQL**（本番用）、MySQL
- **AI開発での用途**: ユーザー管理、設定情報、ログ保存

👉 表（テーブル）形式
| id | name |
| -- | ---- |
| 1  | Taro |

#### 主なDB

* MySQL
* PostgreSQL

### 5.2 ■ NoSQL

- **特徴**: 柔軟なスキーマ、JSONライクなデータ構造
- **代表例**: **MongoDB**、Firebase
- **AI開発での用途**: 多様な形式のデータ、プロトタイピング

👉 柔軟な構造

```json
{
  "name": "Taro",
  "skills": ["AI", "Cloud"]
}
```

#### 主なDB

* MongoDB

---

### 5.3 ■ ベクトルDB（AI特化）

- **特徴**: データを「ベクトル（数値の配列）」として保存し、意味的な類似性で検索
- **代表例**: **Chroma**（学習用）、Pinecone、Weaviate、Milvus
- **AI開発での用途**: **RAG**、類似文書検索、レコメンデーション

👉 意味検索用

#### 主なDB

* Weaviate
* Pinecone

[🔝 目次に戻る](#index)

---

## 6. RDB基礎（重要）

### ■ テーブル構造

```text
users テーブル
-----------------
id | name | age
```

### ■ SQL（基本操作）

SQL（Structured Query Language）は、RDBを操作するための言語です。  
AI開発では、データの準備や分析のために必須のスキルです。

#### SELECT

```sql
SELECT * FROM users;
```

#### INSERT

```sql
INSERT INTO users (name, age)
VALUES ('Taro', 20);
```

#### UPDATE

```sql
UPDATE users
SET age = 21
WHERE name = 'Taro';
```

#### DELETE

```sql
DELETE FROM users
WHERE name = 'Taro';
```

#### SQLの主要コマンドまとめ

| コマンド | 用途 | 例 |
|:---|:---|:---|
| `CREATE TABLE` | テーブル作成 | `CREATE TABLE users (id INT, name TEXT)` |
| `INSERT INTO` | データ挿入 | `INSERT INTO users VALUES (1, 'Alice')` |
| `SELECT` | データ取得 | `SELECT * FROM users WHERE id = 1` |
| `UPDATE` | データ更新 | `UPDATE users SET name = 'Bob' WHERE id = 1` |
| `DELETE` | データ削除 | `DELETE FROM users WHERE id = 1` |

### ■ ポイント

👉 **SQL = データ操作言語**

[🔝 目次に戻る](#index)

---

## 7. 正規化（設計の基礎）

### ■ 例（NG）

```text
user:
name | skills
Taro | Python, AWS
```

### ■ 正規化後（OK）

```text
users
id | name

skills
user_id | skill
```

### ■ 理由

👉 データの重複防止・整合性確保

[🔝 目次に戻る](#index)

---

## 8. NoSQLとの違い

| 項目   | RDB    | NoSQL    |
| ---- | ------ | -------- |
| 構造   | 固定     | 柔軟       |
| スキーマ | 必須     | 任意       |
| JOIN | あり     | なし       |
| 用途   | 業務システム | Web / AI |

[🔝 目次に戻る](#index)

---

## 9. API × JSON × DBの関係

### ■ 全体像

```text
[フロント]
   ↓ JSON
[API]
   ↓
[DB]
```

### ■ 流れ

1. APIがJSON受け取る
2. DBに保存
3. JSONで返す

[🔝 目次に戻る](#index)

---

## 10. 実装例（Python + DB）

### ■ SQLite例

```python
import sqlite3

conn = sqlite3.connect("sample.db")
cur = conn.cursor()

cur.execute("CREATE TABLE users (id INTEGER, name TEXT)")
cur.execute("INSERT INTO users VALUES (1, 'Taro')")

conn.commit()
conn.close()
```

[🔝 目次に戻る](#index)

---

## 11. ORM（重要概念）

### ■ ORMとは

👉 **SQLを書かずにDB操作**

### ■ 例（イメージ）

```python
user = User(name="Taro")
session.add(user)
```

### ■ 主なORM

* SQLAlchemy
* Django ORM

[🔝 目次に戻る](#index)

---

## 12. AI開発とデータ

### ■ AIで扱うデータ

* JSON（API）
* テキスト
* ベクトル（埋め込み）

### ■ RAG構成

```text
ユーザー質問
   ↓
ベクトル検索
   ↓
DB（知識）
   ↓
AI回答
```

[🔝 目次に戻る](#index)

---

## 13. 実務での使い方

### ■ よくある構成

* API（FastAPI）
* DB（PostgreSQL）
* キャッシュ（Redis）

## ■ 用途

* ユーザー管理
* ログ管理
* AI知識ベース

[🔝 目次に戻る](#index)

---

## 14. よくあるミス

❌ JSON構造理解不足

❌ DB設計が雑

❌ SQL書けない

❌ 正規化していない

[🔝 目次に戻る](#index)

---

## 15. 初心者向け演習

### ■ 演習①

👉 JSONを読む・書く

### ■ 演習②

👉 SQLiteでCRUD

### ■ 演習③

👉 APIとDB連携

[🔝 目次に戻る](#index)

---

## 16. 重要まとめ

👉 データ基礎の本質

* JSON = データ形式
* DB = データ保存
* SQL = 操作

[🔝 目次に戻る](#index)

---

## 17. 最重要メッセージ

👉 **「すべてのAIはデータで動く」**

[🔝 目次に戻る](#index)

---

## 18. 最終理解

👉 初心者 → 実務レベルの到達点

* API理解できる
* JSON読める
* SQL書ける
* DB設計できる

[🔝 目次に戻る](#index)

---
---
# ◆ 上級編（IT開発経験者対象）

以下は、IT開発経験者向けの難易度の高い内容となります。

---
### 19. SQLiteで学ぶSQL基礎

SQLiteはファイル1つで動作する軽量データベースで、学習に最適です。

```python
import sqlite3

# データベース接続（ファイルがなければ作成）
conn = sqlite3.connect('ai_learning.db')
cursor = conn.cursor()

# テーブルの作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_message TEXT NOT NULL,
    ai_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER
)
''')

# データの挿入（INSERT）
cursor.execute('''
INSERT INTO conversations (user_message, ai_response, tokens_used)
VALUES (?, ?, ?)
''', ("PythonでDBを学びたい", "SQLiteを使うと簡単ですよ", 45))

# 複数データの一括挿入
conversations_data = [
    ("JSONとDBの違いは？", "構造化の厳密さが異なります", 32),
    ("RAGって何？", "検索と生成を組み合わせた技術です", 56),
    ("ベクトルDBを教えて", "データを数値化して類似検索します", 78)
]
cursor.executemany('''
INSERT INTO conversations (user_message, ai_response, tokens_used)
VALUES (?, ?, ?)
''', conversations_data)

conn.commit()  # 変更を確定
```

### 19.2 データの検索（SELECT）の極意

```python
# 全てのデータを取得
cursor.execute("SELECT * FROM conversations")
all_data = cursor.fetchall()
print("=== 全データ ===")
for row in all_data:
    print(f"ID:{row[0]}, ユーザー:{row[1]}, トークン:{row[4]}")

# 条件を指定して検索（WHERE）
cursor.execute("SELECT * FROM conversations WHERE tokens_used > 50")
high_token_data = cursor.fetchall()
print(f"\n=== 50トークン以上の会話: {len(high_token_data)}件 ===")

# 特定のカラムのみ取得、並び替え（ORDER BY）
cursor.execute('''
SELECT user_message, tokens_used 
FROM conversations 
ORDER BY tokens_used DESC 
LIMIT 3
''')
print("\n=== トークン使用量トップ3 ===")
for msg, tokens in cursor.fetchall():
    print(f"- {msg} ({tokens} tokens)")

# LIKEを使った部分一致検索
cursor.execute("SELECT * FROM conversations WHERE user_message LIKE '%DB%'")
db_related = cursor.fetchall()
print(f"\n=== DB関連の会話: {len(db_related)}件 ===")

# データの更新（UPDATE）
cursor.execute('''
UPDATE conversations 
SET tokens_used = tokens_used + 10 
WHERE user_message LIKE '%Python%'
''')
print(f"更新された行数: {cursor.rowcount}")

# データの削除（DELETE）
cursor.execute("DELETE FROM conversations WHERE tokens_used < 30")
print(f"削除された行数: {cursor.rowcount}")

conn.commit()
conn.close()
```

[🔝 目次に戻る](#index)

---

## 20. RAGのためのベクトルデータベース入門

RAG（Retrieval-Augmented Generation）は、AI開発において最も重要な技術の1つです。  
外部知識をAIに与えて、より正確な回答を生成します。

### 20.1 ベクトルDBの基本概念

1. **埋め込み（Embedding）**: テキストや画像を数値の配列（ベクトル）に変換
2. **類似度検索**: ベクトル空間上で近いものを「意味的に類似」と判断
3. **RAGの流れ**:
   - ユーザー質問 → ベクトル化
   - 関連ドキュメントをベクトルDBから検索
   - 質問＋検索結果をAIに渡して回答生成

### 20.2 ChromaDBで学ぶベクトルDB（学習用）

```python
# インストール: pip install chromadb sentence-transformers

import chromadb
from sentence_transformers import SentenceTransformer

# 埋め込みモデルの準備（日本語対応）
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# ChromaDBクライアントの起動
client = chromadb.Client()

# コレクション（テーブル）の作成
collection = client.create_collection(
    name="ai_knowledge",
    embedding_function=lambda texts: model.encode(texts).tolist()
)

# 知識データの追加
documents = [
    "Pythonはプログラミング言語で、AI開発に広く使われています",
    "RAGは検索拡張生成の略で、外部知識を活用する技術です",
    "ベクトルDBはデータを数値化して類似検索を行うデータベースです",
    "OpenAIはGPTシリーズのAIモデルを提供している企業です",
    "SQLはリレーショナルデータベースを操作するための言語です"
]

ids = [f"doc_{i}" for i in range(len(documents))]

collection.add(
    documents=documents,
    ids=ids
)

# 類似検索の実行
query = "AIで外部知識を使う方法を教えて"
results = collection.query(
    query_texts=[query],
    n_results=2  # 上位2件を取得
)

print("=== 検索結果 ===")
for i, doc in enumerate(results['documents'][0]):
    print(f"{i+1}. {doc}")
    print(f"   距離: {results['distances'][0][i]}\n")

# コレクションの削除
client.delete_collection("ai_knowledge")
```

### 20.3 簡単なRAGシステムの実装

```python
import chromadb
from sentence_transformers import SentenceTransformer
import requests

class SimpleRAG:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name="knowledge_base",
            embedding_function=lambda texts: self.model.encode(texts).tolist()
        )
    
    def add_knowledge(self, texts, ids):
        """知識ベースに情報を追加"""
        self.collection.add(
            documents=texts,
            ids=ids
        )
    
    def search(self, query, n_results=3):
        """関連情報を検索"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0]
    
    def generate_response(self, query):
        """検索結果を使って応答を生成（実際はOpenAI APIなどと連携）"""
        # 関連情報を検索
        context = self.search(query)
        
        # 簡易的な応答生成（実際はLLMに渡す）
        if context:
            response = f"【参考情報】\n"
            for i, info in enumerate(context, 1):
                response += f"{i}. {info}\n"
            response += f"\n【回答】\n質問「{query}」に対する関連情報を提供しました。"
        else:
            response = "関連情報が見つかりませんでした。"
        
        return response

# 使用例
rag = SimpleRAG()

# 知識を追加
knowledge = [
    "RAGは検索拡張生成の略で、外部知識ベースから関連情報を検索してLLMの回答精度を向上させる技術です",
    "ベクトルデータベースは、データを高次元ベクトルとして保存し、類似度検索を高速に行うためのデータベースです",
    "埋め込みモデルは、テキストの意味を数値ベクトルに変換するニューラルネットワークモデルです"
]

rag.add_knowledge(knowledge, [f"doc_{i}" for i in range(len(knowledge))])

# 質問に対する応答
queries = [
    "RAGって何？",
    "ベクトルDBの特徴は？",
    "埋め込みモデルの役割は？"
]

for q in queries:
    print(f"\n質問: {q}")
    print(rag.generate_response(q))
```

[🔝 目次に戻る](#index)

---

## 21. 実践：AIアプリケーションでのデータ管理

### 21.1 SQLite + JSON の組み合わせ

実際のAIアプリケーションでは、構造化データ（ユーザー情報）はSQL、非構造化データ（会話履歴）はJSONとして保存することが多いです。

```python
import sqlite3
import json
from datetime import datetime

class AIDataManager:
    def __init__(self, db_path="ai_app.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_tables()
    
    def _init_tables(self):
        # ユーザーテーブル
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 会話セッションテーブル（JSONで履歴を保存）
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT NOT NULL,
            messages JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        self.conn.commit()
    
    def add_user(self, name, email):
        self.cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def save_conversation(self, user_id, session_id, messages):
        # messagesは辞書のリスト [{role, content}, ...]
        messages_json = json.dumps(messages, ensure_ascii=False)
        self.cursor.execute('''
        INSERT INTO conversations (user_id, session_id, messages)
        VALUES (?, ?, ?)
        ''', (user_id, session_id, messages_json))
        self.conn.commit()
    
    def get_user_conversations(self, user_id):
        self.cursor.execute('''
        SELECT session_id, messages, created_at 
        FROM conversations 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        ''', (user_id,))
        
        results = []
        for session_id, messages_json, created_at in self.cursor.fetchall():
            results.append({
                "session_id": session_id,
                "messages": json.loads(messages_json),
                "created_at": created_at
            })
        return results
    
    def close(self):
        self.conn.close()

# 使用例
db = AIDataManager()

# ユーザー追加
user_id = db.add_user("田中太郎", "tanaka@example.com")
print(f"ユーザーID: {user_id}")

# 会話保存
conversation = [
    {"role": "user", "content": "RAGについて教えて"},
    {"role": "assistant", "content": "RAGは検索拡張生成の略です..."}
]
db.save_conversation(user_id, "session_001", conversation)

# 会話履歴の取得
history = db.get_user_conversations(user_id)
print(f"会話履歴: {len(history)}件")
print(json.dumps(history, ensure_ascii=False, indent=2))

db.close()
```

### 21.2 パフォーマンスとインデックス

大量データを扱う場合の最適化テクニックです。

```python
# インデックスの作成（検索を高速化）
cursor.execute("CREATE INDEX idx_user_id ON conversations(user_id)")
cursor.execute("CREATE INDEX idx_created_at ON conversations(created_at)")

# トランザクション（一連の操作をまとめて実行）
try:
    cursor.execute("BEGIN TRANSACTION")
    # 複数のSQL操作
    cursor.execute("INSERT INTO users ...")
    cursor.execute("INSERT INTO conversations ...")
    cursor.execute("UPDATE users ...")
    conn.commit()  # 全て成功したら確定
except Exception as e:
    conn.rollback()  # エラー時は全てキャンセル
    print(f"エラー: {e}")
```

[🔝 目次に戻る](#index)

---

## 22. まとめ：データベース選定ガイド

| ユースケース | 推奨DB | 理由 |
|:---|:---|:---|
| 学習・プロトタイピング | SQLite, ChromaDB | セットアップが簡単、ファイルベース |
| Webアプリ（本番） | PostgreSQL, MongoDB | スケーラビリティ、信頼性 |
| RAGシステム | ChromaDB, Pinecone, Weaviate | ベクトル検索に最適化 |
| 分析・レポーティング | PostgreSQL, DuckDB | 複雑な集計クエリに対応 |
| キャッシュ | Redis | 高速なキーバリューストア |

[🔝 目次に戻る](#index)

---
## 23. 次の挑戦：ハンズオン課題

1. **課題1（JSON操作）**: 
   - 架空のECサイトの商品データ（JSON形式）を作成してください（10商品以上）
   - 価格が1000円以上の商品だけを抽出する関数を作成してください
   - カテゴリ別に商品数を集計してください

2. **課題2（SQL基礎）**:
   - SQLiteに「books」テーブル（id, title, author, price, published_year）を作成してください
   - 5冊以上のデータを挿入してください
   - 出版年が2020年以降の本を価格の高い順に取得してください
   - 著者別の平均価格を計算してください

3. **課題3（RAG入門）**:
   - ChromaDBを使って、自分の好きなトピック（例：料理、旅行、スポーツ）に関する知識ベースを作成してください
   - 少なくとも5つの知識ドキュメントを追加してください
   - 異なる3つの質問に対して、関連情報を検索するプログラムを作成してください

4. **課題4（応用）**:
   - SQLiteとJSONを組み合わせて、ブログ投稿システムを作成してください
   - ユーザーテーブルと投稿テーブル（本文はJSON形式でタグ情報も保存）を設計してください
   - 特定のタグが含まれる投稿を検索する機能を実装してください

[🔝 目次に戻る](#index)

---

## 本教材編集履歴

|作成者|バージョン| 日付 | 内容 |
|------|-------|----------|----------|
| Y.F  |1.0.0  |2026-03-31|新規作成|

repository: [https://github.com/8alfalfa8/Tec-Doc](https://github.com/8alfalfa8/Tec-Doc)

[🔝 目次に戻る](#index)

---
