# ◆ オンプレミスからAWSのECSへ移行時のECS Task / Service 設計

以下では、**オンプレミスのTomcat（WAR）を前提にしたECS Task / Service 設計**について、
**①既存オンプレ値からの設定値算出方法（実務的な計算式・考え方）**と
**②その設定に関係するAWS（ECS / Fargate / ALB）の制限**を、**項目別に体系的**に説明します。

> ※「どう決めるか」「なぜその値か」「AWS制限にどう引っかかるか」を重視しています。

---

## 1. ECS Task / Service 設計の全体観

#### ECS Task / Service で設計対象となる主な項目

| 分類     | 項目                  |
| ------ | ------------------- |
| リソース   | CPU / Memory        |
| Java   | JVM Heap / GC       |
| ネットワーク | Port / 同時接続         |
| 可用性    | Desired / Min / Max |
| スケーリング | Auto Scaling        |
| ヘルス    | Health Check        |
| 起動     | 起動時間 / Grace Period |
| 制限     | AWS上限制約             |

---

## 2. CPU 設計（オンプレ → ECS）

---

### 2.1 オンプレCPU情報の取得

#### 入手情報（必須）

| 情報          | 例            |
| ----------- | ------------ |
| CPUコア数      | 4 Core       |
| 利用率         | 平常30%、ピーク70% |
| JVM Thread数 | 200          |
| 同時ユーザ数      | 300          |

---

### 2.2 ECS CPU値の考え方

#### ECS CPU単位

* **1 vCPU = 1024 CPU units**

| ECS指定値 | vCPU |
| ------ | ---- |
| 256    | 0.25 |
| 512    | 0.5  |
| 1024   | 1    |
| 2048   | 2    |
| 4096   | 4    |

---

### 2.3 CPU値算出ロジック

#### ① オンプレの実効CPU使用量

```
4 core × 70%（ピーク）＝ 2.8 core
```

#### ② コンテナオーバーヘッド考慮

```
2.8 × 1.2（余裕） ≒ 3.4 core
```

#### ③ ECS設定値

➡ **4096 CPU（4 vCPU）**

---

### 2.4 AWS制限（CPU）

### Fargate制限（重要）

* CPUとMemoryは**組み合わせ固定**
* CPU最大：**16 vCPU（16384）**

---

## 3. Memory（メモリ）設計

---

### 3.1 オンプレのメモリ情報

#### 入手情報

| 項目        | 例      |
| --------- | ------ |
| 物理メモリ     | 16GB   |
| JVM Heap  | -Xmx8G |
| 非Heap     | 約2GB   |
| OS/Tomcat | 約2GB   |

---

### 3.2 メモリ算出方法

#### ① 実使用量

```
8G（Heap）+ 2G（NonHeap）+ 2G（OS） = 12G
```

#### ② バースト余裕

```
12G × 1.3 = 15.6G
```

#### ③ ECS設定値

➡ **Memory = 16GB（16384）**

---

### 3.3 AWS制限（Memory）

#### Fargate制限

| CPU  | Memory選択肢 |
| ---- | --------- |
| 1024 | 2–8 GB    |
| 2048 | 4–16 GB   |
| 4096 | 8–30 GB   |

❗ **自由指定不可**

---

## 4. JVM Heap設計（超重要）

---

### 4.1 原則

> **JVM HeapはECS Memoryの50〜70%**

#### 計算例

```
ECS Memory = 16GB
Heap = 10GB（約62%）
```

#### JVMオプション例

```bash
-Xms10G
-Xmx10G
-XX:MaxMetaspaceSize=512M
```

---

### 4.2 注意点

* Container OOM Kill防止
* 非Heap領域（Metaspace, Thread, DirectBuffer）確保

---

## 5. ポート / ネットワーク設計

---

## 5.1 ポート

#### オンプレ

* Tomcat：8080固定

#### ECS

* コンテナPort：8080
* ALB TargetPort：8080

---

### 5.2 AWS制限

| 項目             | 制限          |
| -------------- | ----------- |
| ALB Target     | 最大1,000     |
| 同時接続           | ソフトリミット     |
| Ephemeral Port | 32768–61000 |

---

## 6. 同時接続・スレッド設計

---

## 6.1 Tomcat Thread算出

#### オンプレ設定確認

```xml
maxThreads="200"
```

#### ECS換算

* 1 vCPUあたり **約50〜100 threads**
* 4 vCPU → 200〜400 threads

---

### 6.2 AWS制限

* コンテナ自体の制限なし
* **ALB idle timeout（デフォルト60秒）**

---

## 7. Desired / Min / Max Task数

---

### 7.1 計算ロジック

#### ① オンプレ

* 物理サーバ1台
* ピーク時70%

#### ② ECS

* 1Task = ピークの50〜60%

➡ **Min=2 / Desired=2 / Max=6**

---

### 7.2 AWS制限

| 項目            | 制限     |
| ------------- | ------ |
| Service Task数 | 10,000 |
| ALB Target    | 1,000  |

---

## 8. Auto Scaling 設計

---

## 8.1 スケール指標

| 指標          | 目安             |
| ----------- | -------------- |
| CPU         | 60–70%         |
| Memory      | 70%            |
| ALB Request | 1,000 req/Task |

---

### 8.2 AWS制限

* スケールクールダウン最小：**1分**
* スケール単位：**1 Task**

---

## 9. Health Check / 起動時間

---

## 9.1 起動時間計算

| 内容         | 秒  |
| ---------- | -- |
| JVM起動      | 30 |
| WAR展開      | 40 |
| DB接続       | 20 |
| ➡ **約90秒** |    |

---

## 9.2 設定

| 項目                  | 値   |
| ------------------- | --- |
| Health Interval     | 30  |
| Unhealthy Threshold | 5   |
| Grace Period        | 180 |

---

### 9.3 AWS制限

* ALB Health Check Timeout：2–120秒
* Interval：5–300秒

---

## 10. ECS Task / Service 制限まとめ（重要）

| 項目          | 制限        |
| ----------- | --------- |
| Task CPU    | 最大16 vCPU |
| Task Memory | 最大120GB   |
| Container数  | 10        |
| Env変数       | 8KB       |
| Secrets     | 100個      |
| ENI         | Taskごと1   |

---

---

# 11. 実務での設計まとめ（判断軸）

✔ オンプレの**ピーク時実測値**<br>
✔ JVMの**Heap以外の消費**<br>
✔ Fargateの**CPU×Memory制約表**<br>
✔ スケール前提（単体最適NG）

---
