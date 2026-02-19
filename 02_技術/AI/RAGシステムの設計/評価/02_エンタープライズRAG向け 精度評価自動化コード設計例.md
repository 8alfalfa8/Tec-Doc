# ◆ エンタープライズRAG向け 精度評価自動化コード設計例

以下に、**エンタープライズRAG向け 精度評価自動化コード設計例（実装アーキテクチャ＋Python疑似コード）**を提示します。
監査対応を前提に **再現性・ログ保存・CI統合** を組み込みます。

---

## 1. 全体アーキテクチャ

```
/evaluation
 ├── dataset/
 │     └── gold.json
 ├── retrieval_eval.py
 ├── generation_eval.py
 ├── safety_eval.py
 ├── scorer.py
 ├── pipeline.py
 └── report.py
```

使用想定：

* LLM API：OpenAI
* RAG基盤：LangChain
* ログ管理：Weights & Biases

---

## 2. ゴールドデータ設計（gold.json）

```json
[
  {
    "question": "有給休暇の付与条件は？",
    "gold_doc_ids": ["doc_123"],
    "gold_answer": "入社6か月後に10日付与される。",
    "security_level": "public"
  }
]
```

---

## 3. Retrieval評価コード

### retrieval_eval.py

```python
def recall_at_k(results, gold_doc_ids, k):
    top_k = results[:k]
    retrieved_ids = [r["doc_id"] for r in top_k]
    return int(any(doc_id in retrieved_ids for doc_id in gold_doc_ids))


def mean_reciprocal_rank(results, gold_doc_ids):
    for idx, r in enumerate(results):
        if r["doc_id"] in gold_doc_ids:
            return 1.0 / (idx + 1)
    return 0.0
```

---

## 4. 生成品質評価

### 4.1 Faithfulness（LLM自己評価）

#### generation_eval.py

```python
from openai import OpenAI

client = OpenAI()

def evaluate_faithfulness(answer, context):
    prompt = f"""
    以下の回答がコンテキストに忠実か0〜1で評価せよ。
    回答: {answer}
    コンテキスト: {context}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    score = float(response.choices[0].message.content.strip())
    return score
```

---

### 4.2 回答類似度（Embeddingベース）

```python
from sklearn.metrics.pairwise import cosine_similarity

def embedding_similarity(vec1, vec2):
    return cosine_similarity([vec1], [vec2])[0][0]
```

---

## 5. ハルシネーション検出

```python
def hallucination_check(answer, context):
    return 0 if answer in context else 1
```

（実務では部分一致＋意味類似度で判定）

---

## 6. セキュリティ評価

### safety_eval.py

```python
def leakage_test(answer, security_level):
    if security_level == "confidential":
        return 1  # 漏洩
    return 0
```

実際は：

* 権限外アクセス試験
* プロンプトインジェクションテスト

---

## 7. 統合スコアリング

### scorer.py

```python
def total_score(recall, faithfulness, relevance, safety):
    return (
        0.3 * recall +
        0.3 * faithfulness +
        0.2 * relevance +
        0.2 * (1 - safety)
    )
```

---

## 8. 全体パイプライン

### pipeline.py

```python
def run_evaluation(dataset, rag_system):
    results = []

    for sample in dataset:
        question = sample["question"]
        gold_ids = sample["gold_doc_ids"]

        retrieved = rag_system.retrieve(question)
        answer, context = rag_system.generate(question)

        recall = recall_at_k(retrieved, gold_ids, k=5)
        mrr = mean_reciprocal_rank(retrieved, gold_ids)
        faith = evaluate_faithfulness(answer, context)

        score = total_score(recall, faith, relevance=faith, safety=0)

        results.append({
            "question": question,
            "recall": recall,
            "mrr": mrr,
            "faithfulness": faith,
            "total_score": score
        })

    return results
```

---

## 9. レポート出力

### report.py

```python
import pandas as pd

def generate_report(results):
    df = pd.DataFrame(results)
    print("平均Recall:", df["recall"].mean())
    print("平均MRR:", df["mrr"].mean())
    print("平均Faithfulness:", df["faithfulness"].mean())
    print("総合スコア:", df["total_score"].mean())
    df.to_csv("evaluation_report.csv", index=False)
```

---

## 10. CI/CD統合例

#### GitHub Actions

```
- RAG変更PR作成
- 自動評価実行
- 総合スコア0.85未満なら失敗
```

---

## 11. ダッシュボード統合

* 実験比較
* モデル別スコア
* チャンクサイズ比較
* 月次推移

MLOps連携：

* Weights & Biases
* Datadog

---

## 12. エンタープライズ拡張設計

#### 追加すべき高度評価

* nDCG
* Context Precision
* 反事実テスト
* 攻撃耐性自動生成
* 多言語評価

---

## 13. 成熟度モデル

| レベル | 状態           |
| --- | ------------ |
| Lv1 | 手動評価         |
| Lv2 | Retrieval自動化 |
| Lv3 | 生成評価自動化      |
| Lv4 | セキュリティ自動化    |
| Lv5 | CI強制ゲート      |

---

## ■ 実務で最重要

1. データセット品質が全て
2. Recallが悪いと何も改善しない
3. Faithfulnessは必須
4. CI組込まないと形骸化

---

