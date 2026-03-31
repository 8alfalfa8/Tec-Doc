# ◆ Web基礎（HTTP／API）

**Web基礎（HTTP／API）** は、システム開発やAI連携に不可欠な基盤知識です。HTTPはクライアントとサーバー間の通信プロトコルで、GET・POST・PUT・DELETEなどのメソッドやステータスコードによりデータのやり取りを制御します。APIはシステム間連携の仕組みで、HTTPとJSONを用いたWeb APIが一般的です。これにより、フロントエンドとバックエンドの連携やクラウド・マイクロサービス構成が実現されます。AI分野では、モデルがAPIとして提供されるため、その理解は不可欠であり、RAGなどの高度な構成でも重要な役割を担います。

本教材では実務にWeb基礎を体系的に習得します。

---

## <a id="index"></a>📖 目次

- [1. Webとは何か（超基本）](#1-Webとは何か超基本)
- [2. HTTPとは（最重要）](#2-HTTPとは最重要)
- [3. HTTPメソッド（超頻出）](#3-HTTPメソッド超頻出)
- [4. ステータスコード](#4-ステータスコード)
- [5. APIとは何か](#5-APIとは何か)
- [6. REST API](#6-REST-API)
- [7. JSON（データ形式）](#7-JSONデータ形式)
- [8. 実装（Python）](#8-実装Python)
- [9. curl（LinuxでのAPI実行）](#9-curlLinuxでのAPI実行)
- [10. 認証（重要）](#10-認証重要)
- [11. エラー対応（実務力）](#11-エラー対応実務力)
- [12. Webアーキテクチャ（重要理解）](#12-Webアーキテクチャ重要理解)
- [13. AI開発との接続](#13-AI開発との接続)
- [14. 実務での使われ方](#14-実務での使われ方)
- [15. 初心者がやるべき演習](#15-初心者がやるべき演習)
- [16. よくある落とし穴](#16-よくある落とし穴)
- [17. 重要まとめ](#17-重要まとめ)
- [18. 最重要メッセージ](#18-最重要メッセージ)
- [19. 次の挑戦：ハンズオン課題](#19-次の挑戦ハンズオン課題)
- [本教材編集履歴](#本教材編集履歴)

---

## 1. Webとは何か（超基本）

### ■ Webの正体

👉 **クライアントとサーバーの通信**

```
[ブラウザ] → リクエスト → [サーバー]
[ブラウザ] ← レスポンス ← [サーバー]
```

### ■ 例

ブラウザでGoogleを開くと：

1. リクエスト送信
2. サーバーがHTML返す
3. 画面が表示される

### ■ 用語

| 用語     | 意味       |
| ------ | -------- |
| クライアント | ブラウザやアプリ |
| サーバー   | データを返す側  |
| リクエスト  | 要求       |
| レスポンス  | 応答       |

[🔝 目次に戻る](#index)

---

## 2. HTTPとは（最重要）

### ■ HTTPとは

👉 **Web通信のルール（プロトコル）**

正式名称：HyperText Transfer Protocol

### ■ 通信の中身（実際）

#### リクエスト例

```
GET /index.html HTTP/1.1
Host: example.com
```

#### レスポンス例

```
HTTP/1.1 200 OK
Content-Type: text/html

<html>...</html>
```

### ■ 超重要ポイント

👉 **HTTP = 「お願い」と「返答」の仕組み**

[🔝 目次に戻る](#index)

---

## 3. HTTPメソッド（超頻出）

### ■ 基本4つ（絶対覚える）

| メソッド   | 意味 | 用途    |
| ------ | -- | ----- |
| GET    | 取得 | データ取得 |
| POST   | 作成 | データ登録 |
| PUT    | 更新 | データ更新 |
| DELETE | 削除 | データ削除 |

### ■ イメージ

```
GET    → 見る
POST   → 作る
PUT    → 直す
DELETE → 消す
```

[🔝 目次に戻る](#index)

---

## 4. ステータスコード

サーバーからの応答には、結果を示す3桁のコードが付随します。特に重要なものを覚えましょう。
*   **2xx (成功)**:
    *   `200 OK`: 成功。最も一般的。
*   **4xx (クライアントエラー)**: あなた（コード）に問題がある。
    *   `401 Unauthorized`: APIキーが間違っている、または認証が必要。
    *   `404 Not Found`: エンドポイント（URL）が間違っている。
*   **5xx (サーバーエラー)**: 相手側（AIサーバー）に問題がある。
    *   `500 Internal Server Error`: AIサーバー内部でエラーが発生した。

### ■ 代表例

| コード | 意味      |
| --- | ------- |
| 200 | 成功      |
| 201 | 作成成功    |
| 400 | リクエスト不正 |
| 401 | 認証エラー   |
| 403 | 権限なし    |
| 404 | 見つからない  |
| 500 | サーバーエラー |

### ■ 実務ポイント

👉 **ログ解析・障害対応で必須**

[🔝 目次に戻る](#index)

---

## 5. APIとは何か

**API (Application Programming Interface)** は、アプリケーションが他のアプリケーションの機能を「借用」するための窓口です。  
**APIの本質**👉 $\color{red}{\text{「機能の窓口」}}$

### ■ イメージ

```
[あなたのアプリ] → API → [外部サービス]
```

**レストランに例えると:**
*   **あなた**: クライアント（Pythonスクリプト）
*   **メニュー**: API仕様書
*   **注文**: リクエスト（`POST /chat/completions`）
*   **料理**: レスポンス（AIの回答）
*   **店員**: APIエンドポイント

AI開発では、**「AIに仕事をさせるために、APIという形で指示を出し、結果を受け取る」** という流れが基本となります。

### ■ 例

* 天気API
* 決済API
* AI API


### ■ AIとの関係

👉 **AIはほぼAPIとして使う**

例：

* OpenAI API
* 外部データ連携

[🔝 目次に戻る](#index)

---

## 6. REST API

### ■ RESTとは

現代のWeb APIの主流である設計様式です。  
👉 **HTTPを使った設計ルール**

### ■ URL設計例

```
GET    /users        → 一覧取得
GET    /users/1      → 1件取得
POST   /users        → 新規作成
PUT    /users/1      → 更新
DELETE /users/1      → 削除
```

### ■ ポイント

👉 **URL = リソース（データ）を表す**

[🔝 目次に戻る](#index)

---

## 7. JSON（データ形式）

### ■ JSONとは

APIのリクエスト（送信データ）とレスポンス（受信データ）は、ほぼ **JSON (JavaScript Object Notation)** という形式でやり取りされます。 
👉 **APIで使われる標準データ形式**

### JSONの基本構造
JSONは「キー」と「値」のペアの集合です。Pythonの辞書（`dict`）とほぼ同じ構造なので非常に親しみやすいです。

### ■ 例

```json
{
  "id": 1,
  "name": "Taro",
  "active": true
}
```

**OpenAI APIのリクエスト例:**
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "user",
      "content": "こんにちは！"
    }
  ],
  "temperature": 0.7
}
```

### ■ 特徴

* 軽い
* 人間が読める
* プログラムで扱いやすい

[🔝 目次に戻る](#index)

---

## 8. 実装（Python）

### ■ GETリクエスト

```python
import requests

res = requests.get("https://jsonplaceholder.typicode.com/users")

print(res.status_code)
print(res.json())
```

### ■ POSTリクエスト

```python
import requests

data = {
    "name": "Taro"
}

res = requests.post(
    "https://jsonplaceholder.typicode.com/users",
    json=data
)

print(res.json())
```

### ■ ポイント

* `status_code`確認
* `json()`でデータ取得

### PythonでのJSON操作
Pythonには標準で `json` モジュールが用意されています。

```python
import json

# Pythonの辞書 -> JSON文字列 (シリアライズ)
data_dict = {"name": "AI", "version": 1}
json_str = json.dumps(data_dict, indent=2, ensure_ascii=False)
print(json_str)
# 出力:
# {
#   "name": "AI",
#   "version": 1
# }

# JSON文字列 -> Pythonの辞書 (デシリアライズ)
received_json = '{"status": "success", "data": "Hello"}'
parsed_dict = json.loads(received_json)
print(parsed_dict["data"])  # 出力: Hello
```

[🔝 目次に戻る](#index)

---

## 9. curl（LinuxでのAPI実行）

### ■ GET

```bash
curl https://jsonplaceholder.typicode.com/users
```

### ■ POST

```bash
curl -X POST https://example.com \
     -H "Content-Type: application/json" \
     -d '{"name":"Taro"}'
```

### ■ 実務での用途

* APIテスト
* 障害調査
* 自動化スクリプト

[🔝 目次に戻る](#index)

---

## 10. 認証（重要）

### ■ APIキー

```bash
Authorization: Bearer xxxxx
```

### ■ なぜ必要か

👉 **不正アクセス防止**

### ■ 実務例

* クラウドAPI
* AI API
* 決済API

[🔝 目次に戻る](#index)

---

## 11. エラー対応（実務力）

### ■ よくある問題

| 問題  | 原因       |
| --- | -------- |
| 400 | パラメータ不正  |
| 401 | APIキー間違い |
| 404 | URLミス    |
| 500 | サーバー障害   |

### ■ 対応方法

👉 必ず確認：

* URL
* メソッド
* ヘッダー
* JSON形式

[🔝 目次に戻る](#index)

---

## 12. Webアーキテクチャ（重要理解）

### ■ 全体像

```
[フロント] → [API] → [バックエンド] → [DB]
```

### ■ 技術例

| 層    | 技術         |
| ---- | ---------- |
| フロント | React      |
| API  | FastAPI    |
| DB   | PostgreSQL |

[🔝 目次に戻る](#index)

---

## 13. AI開発との接続

### ■ AIはAPIで使う

```python
# イメージ
response = client.chat.completions.create(...)
```

### ■ できること

* AIチャット
* 自動分析
* エージェント構築

[🔝 目次に戻る](#index)

---

## 14. 実務での使われ方

### ■ 代表ユースケース

* フロント ↔ バックエンド通信
* マイクロサービス連携
* 外部サービス連携
* AI統合

[🔝 目次に戻る](#index)

---

## 15. 初心者がやるべき演習

### ■ 演習①

👉 APIを叩く

```bash
curl https://jsonplaceholder.typicode.com/posts
```

### ■ 演習②

👉 Pythonで取得

### ■ 演習③

👉 自作API（FastAPI）

[🔝 目次に戻る](#index)

---

## 16. よくある落とし穴

❌ HTTP理解せずにAI開発

❌ JSON構造が読めない

❌ エラー原因が分からない

[🔝 目次に戻る](#index)

---

## 17. 重要まとめ

👉 Web基礎の本質

* HTTP = 通信ルール
* API = 機能の入口
* JSON = データ形式

[🔝 目次に戻る](#index)

---

## 18. 最重要メッセージ

👉 AI時代の核心

**「すべてはAPIで繋がる」**

[🔝 目次に戻る](#index)

---

## 19. 次の挑戦：ハンズオン課題

1.  **課題1**: 無料の天気API（例: `https://open-meteo.com/`）を使って、現在地の気温を取得するPythonスクリプトを作成してください。
2.  **課題2**: 架空のAPIではなく、実際に `requests` ライブラリを使って、GitHubのAPI（認証不要）から自分のユーザー情報を取得してみましょう。エンドポイント: `https://api.github.com/users/{あなたのGitHubユーザー名}`

[🔝 目次に戻る](#index)

---

## 本教材編集履歴

|作成者|バージョン| 日付 | 内容 |
|------|-------|----------|----------|
| Y.F  |1.0.0  |2026-03-31|新規作成|

repository: [https://github.com/8alfalfa8/Tec-Doc](https://github.com/8alfalfa8/Tec-Doc)

[🔝 目次に戻る](#index)

---
