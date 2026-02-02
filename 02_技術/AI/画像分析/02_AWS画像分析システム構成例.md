# ◆ AWS画像分析システム構成例

以下では、**AWSにおける画像分析システムの代表的な構築例**を、
**①全体アーキテクチャ → ②処理フロー → ③ユースケース別構成 → ④設計・運用の勘所（金融・公共向け）**
の順で、**実務設計レベル**まで落として詳しくご説明します。

---

## 1. AWS画像分析システム 全体アーキテクチャ（標準例）

### ① サーバレス／マネージド中心構成（推奨）

```
[利用者 / カメラ / 外部システム]
          │
          ▼
     Amazon API Gateway
          │
          ▼
       AWS Lambda
          │
 ┌────────┼────────┐
 ▼        ▼        ▼
Rekognition Textract Comprehend
 ▼        ▼
S3       DynamoDB / Aurora
 ▼
Athena / QuickSight
```

**特徴**

* 短期PoC〜中規模本番まで対応
* インフラ運用コスト最小
* 監査・セキュリティ対応しやすい

---

### ② カスタムAI（深層学習）構成（高精度・特殊用途）

```
[画像入力]
   ▼
S3（Raw）
   ▼
SageMaker Endpoint（推論）
   ▼
Lambda（後処理）
   ▼
RDS / DynamoDB
```

**特徴**

* 製造業・医療・独自帳票向け
* 精度最優先
* MLOps設計が重要

---

## 2. 処理フロー（AWS具体サービス対応）

### Step 1：画像取得・アップロード

**方法**

* Web/モバイル → API Gateway
* IoTカメラ → S3 Direct Upload
* バッチ → SFTP → S3

**設計ポイント**

* S3は **Raw / Processed / Result** バケット分離
* SSE-KMS による暗号化必須（公共・金融）

---

### Step 2：トリガー起動

| トリガー           | 用途        |
| -------------- | --------- |
| S3 Event       | ファイル到着即処理 |
| API            | 同期処理      |
| Step Functions | 複雑フロー     |

---

### Step 3：前処理（Lambda / ECS）

**内容**

* リサイズ
* 傾き補正
* マスキング（顔・個人情報）
* フォーマット変換

※ 画像サイズが大きい場合は **ECS/Fargate** 推奨

---

### Step 4：画像分析（AI推論）

#### AWSマネージドAI例

| サービス        | 用途         |
| ----------- | ---------- |
| Rekognition | 物体検出、顔、ラベル |
| Textract    | OCR（帳票）    |
| Comprehend  | OCR後テキスト分析 |

```text
画像 → Rekognition.detect_labels
     → confidence付き結果
```

---

#### SageMaker（独自モデル）

```
Lambda
 → SageMaker Endpoint
   → 推論
 → 結果返却
```

**用途**

* 外観検査
* 異常検知
* 独自帳票

---

### Step 5：後処理・業務ルール判定

**例**

```text
IF (検出結果 = 危険物 AND 信頼度 > 0.9)
THEN アラート
```

* Lambdaで実装
* ルールはDynamoDBで管理（非エンジニア変更可）

---

### Step 6：結果保存・可視化

| 保存先        | 内容         |
| ---------- | ---------- |
| DynamoDB   | 即時参照       |
| Aurora     | 業務DB       |
| S3         | 原画像＋結果JSON |
| Athena     | 分析         |
| QuickSight | ダッシュボード    |

---

## 3. ユースケース別 AWS構成例

---

### ① OCR（請求書・帳票）

```
S3（PDF）
 → Textract（AnalyzeDocument）
 → Lambda（項目マッピング）
 → RDS（会計連携）
```

**ポイント**

* テンプレート不要
* 金融では人手確認フロー必須

---

### ② 監視・安全管理

```
Kinesis Video Streams
 → Rekognition Video
 → Lambda
 → SNS / EventBridge
```

**用途**

* 侵入検知
* 転倒検知
* 不審行動

---

### ③ 製造業 外観検査

```
カメラ
 → S3
 → SageMaker（異常検知）
 → Step Functions
 → MES連携
```

---

## 4. セキュリティ・監査設計（金融・公共）

### 必須対策

| 項目   | 対応              |
| ---- | --------------- |
| IAM  | 最小権限            |
| 暗号化  | S3 / DB / 通信    |
| 監査   | CloudTrail      |
| ログ   | CloudWatch Logs |
| 個人情報 | マスキング           |

---

## 5. 非機能設計の勘所

### 性能

* 同期API：Lambda 1〜3秒以内
* 非同期：SQS + Step Functions

### コスト

* Rekognition：画像サイズ最適化
* SageMaker：Endpoint Auto Scaling

### 可用性

* マルチAZ
* DLQ設計必須

---

## 6. PoC → 本番 移行チェックポイント

| 観点   | 内容     |
| ---- | ------ |
| 精度   | 実データ評価 |
| 運用   | 再学習計画  |
| 責任分界 | AI判断＋人 |
| SLA  | 応答時間   |

---

## 7. まとめ（AWS構築の王道）

* **小さく始める：Rekognition / Textract**
* **高度化：SageMaker**
* **制御：Step Functions**
* **運用：MLOps設計が成否を分ける**

---

