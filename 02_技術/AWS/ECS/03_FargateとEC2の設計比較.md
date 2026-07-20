# ◆ Fargate vs EC2の設計比較
<!-- PROFILE_BADGE_START -->

[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?logo=github)](https://github.com/8alfalfa8)
[![Qiita](https://img.shields.io/badge/Qiita-Profile-55C500?logo=qiita&logoColor=white)](https://qiita.com/8alfalfa8)
[![Zenn](https://img.shields.io/badge/Zenn-Profile-3EA8FF?logo=zenn&logoColor=white)](https://zenn.dev/8alfalfa8)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/8alfalfa8)

<!-- PROFILE_BADGE_END -->


以下では **ECS on Fargate と ECS on EC2 の設計比較**を、
**オンプレ Tomcat（WAR）→ AWS ECS 移行**という文脈で、

* 設計観点別の違い
* リソース設計・性能・制限
* コスト・運用・スケーリング
* Tomcat / Java ワークロードでの実務判断基準
* 典型的な選定パターン

まで **設計レビューにそのまま使えるレベル**で整理します。

---

## 1. 結論サマリー（まずこれ）

| 観点          | Fargate   | EC2         |
| ----------- | --------- | ----------- |
| 初期導入        | ◎（即利用）    | △（設計多）      |
| 運用負荷        | ◎（OS管理不要） | △（OS/AMI管理） |
| 性能チューニング    | △         | ◎           |
| 高負荷/低レイテンシ  | △         | ◎           |
| コスト最適化      | △         | ◎           |
| 制限回避        | △         | ◎           |
| Java/Tomcat | ○         | ◎           |
| 長期大規模       | △         | ◎           |

👉 **「まずFargate、詰まったらEC2」が王道**

---

## 2. アーキテクチャの違い

### 2.1 Fargate

```
ALB
 └─ ECS Service
     └─ Task（Fargate）
         └─ Container
```

* OS / EC2 不可視
* Task単位で課金
* CPU / Memory 組み合わせ固定

---

### 2.2 EC2

```
ALB
 └─ ECS Service
     └─ EC2 Instance
         └─ Docker
             └─ Task × 複数
```

* インスタンス管理あり
* リソース共有
* 細かいチューニング可能

---

## 3. リソース設計比較（超重要）

### 3.1 CPU / Memory

#### Fargate

| 特性     | 内容        |
| ------ | --------- |
| 指定方法   | Task単位    |
| CPU    | 最大16 vCPU |
| Memory | 最大120GB   |
| 組み合わせ  | 固定        |

❌ JVM Heap 微調整が難しい

---

#### EC2

| 特性     | 内容         |
| ------ | ---------- |
| 指定方法   | Instance単位 |
| CPU    | 制限なし       |
| Memory | Instance依存 |
| 組み合わせ  | 自由         |

⭕ 大規模Heap / DirectBuffer向き

---

## 4. Java / Tomcat 観点の違い

| 観点              | Fargate | EC2  |
| --------------- | ------- | ---- |
| JVM GC          | 制限あり    | 最適化可 |
| HugePage        | ❌       | ⭕    |
| swap            | ❌       | ⭕    |
| File descriptor | 固定      | 調整可  |
| Kernel param    | 不可      | 可能   |

👉 **低レイテンシ or 高スループットはEC2有利**

---

## 5. スケーリング設計

### 5.1 Fargate

| 特性      | 内容     |
| ------- | ------ |
| スケール    | Task単位 |
| 起動時間    | 30〜90秒 |
| 最小単位    | 1 Task |
| Burst耐性 | △      |

---

### 5.2 EC2

| 特性   | 内容              |
| ---- | --------------- |
| スケール | Instance + Task |
| 起動時間 | 数分              |
| 最小単位 | Instance        |
| 定常負荷 | ◎               |

---

## 6. ネットワーク・同時接続

| 観点             | Fargate | EC2        |
| -------------- | ------- | ---------- |
| ENI            | Taskごと  | Instanceごと |
| Ephemeral Port | 少なめ     | 多い         |
| 同時接続           | △       | ◎          |

👉 **API大量接続はEC2有利**

---

## 7. ストレージ・ファイル

| 項目     | Fargate | EC2     |
| ------ | ------- | ------- |
| 永続化    | EFSのみ   | EBS/EFS |
| I/O性能  | △       | ◎       |
| ローカルFS | 揮発      | 管理可     |

---

## 8. コスト比較（目安）

### 8.1 同等構成例

* 4 vCPU / 16GB
* 常時稼働

| 種別          | 月額      |
| ----------- | ------- |
| Fargate     | 高       |
| EC2 (RI/SP) | 30〜50%安 |

👉 **24/365はEC2圧勝**

---

## 9. 可用性・障害対応

| 観点   | Fargate | EC2  |
| ---- | ------- | ---- |
| AZ分散 | 自動      | 設計必要 |
| 障害復旧 | 早い      | 運用次第 |
| OS障害 | AWS対応   | 自己対応 |

---

## 10. 制限一覧（重要）

### Fargate制限（抜粋）

* CPU×Memory固定
* HugePage不可
* Host access不可
* ulimit変更不可

### EC2制限

* EC2制限のみ（実質無制限）

---

## 11. 典型的な選定パターン

#### Fargate向き

* Web/API（中規模）
* 負荷変動大
* 運用人員少
* PoC / 短期

#### EC2向き

* 大規模Java
* 高同時接続
* 低レイテンシ
* 常時高負荷

---

## 12. 実務向け判断フローチャート

```
24/365 稼働？
 ├─ Yes → EC2
 └─ No
     ↓
Heap > 16GB？
 ├─ Yes → EC2
 └─ No
     ↓
Kernel tuning 必要？
 ├─ Yes → EC2
 └─ No → Fargate
```

---
