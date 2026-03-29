<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. ECS Task / Service 設計の全体観](#1-ecs-task-service-設計の全体観)
    - [ECS Task / Service で設計対象となる主な項目](#ecs-task-service-で設計対象となる主な項目)
- [2. CPU 設計（オンプレ → ECS）](#2-cpu-設計オンプレ-ecs)
  - [2.1 オンプレCPU情報の取得](#21-オンプレcpu情報の取得)
    - [入手情報（必須）](#入手情報必須)
  - [2.2 ECS CPU値の考え方](#22-ecs-cpu値の考え方)
    - [ECS CPU単位](#ecs-cpu単位)
  - [2.3 CPU値算出ロジック](#23-cpu値算出ロジック)
    - [① オンプレの実効CPU使用量](#①-オンプレの実効cpu使用量)
    - [② コンテナオーバーヘッド考慮](#②-コンテナオーバーヘッド考慮)
    - [③ ECS設定値](#③-ecs設定値)
  - [2.4 AWS制限（CPU）](#24-aws制限cpu)
  - [Fargate制限（重要）](#fargate制限重要)
- [3. Memory（メモリ）設計](#3-memoryメモリ設計)
  - [3.1 オンプレのメモリ情報](#31-オンプレのメモリ情報)
    - [入手情報](#入手情報)
  - [3.2 メモリ算出方法](#32-メモリ算出方法)
    - [① 実使用量](#①-実使用量)
    - [② バースト余裕](#②-バースト余裕)
    - [③ ECS設定値](#③-ecs設定値)
  - [3.3 AWS制限（Memory）](#33-aws制限memory)
    - [Fargate制限](#fargate制限)
- [4. JVM Heap設計（超重要）](#4-jvm-heap設計超重要)
  - [4.1 原則](#41-原則)
    - [計算例](#計算例)
    - [JVMオプション例](#jvmオプション例)
  - [4.2 注意点](#42-注意点)
- [5. ポート / ネットワーク設計](#5-ポート-ネットワーク設計)
- [5.1 ポート](#51-ポート)
    - [オンプレ](#オンプレ)
    - [ECS](#ecs)
  - [5.2 AWS制限](#52-aws制限)
- [6. 同時接続・スレッド設計](#6-同時接続スレッド設計)
- [6.1 Tomcat Thread算出](#61-tomcat-thread算出)
    - [オンプレ設定確認](#オンプレ設定確認)
    - [ECS換算](#ecs換算)
  - [6.2 AWS制限](#62-aws制限)
- [7. Desired / Min / Max Task数](#7-desired-min-max-task数)
  - [7.1 計算ロジック](#71-計算ロジック)
    - [① オンプレ](#①-オンプレ)
    - [② ECS](#②-ecs)
  - [7.2 AWS制限](#72-aws制限)
- [8. Auto Scaling 設計](#8-auto-scaling-設計)
- [8.1 スケール指標](#81-スケール指標)
  - [8.2 AWS制限](#82-aws制限)
- [9. Health Check / 起動時間](#9-health-check-起動時間)
- [9.1 起動時間計算](#91-起動時間計算)
- [9.2 設定](#92-設定)
  - [9.3 AWS制限](#93-aws制限)
- [10. ECS Task / Service 制限まとめ（重要）](#10-ecs-task-service-制限まとめ重要)
<!-- TOC_END -->

# ◆ オンプレミスからAWSのECSへ移行時のECS Task / Service 設計

以下では、**オンプレミスのTomcat（WAR）を前提にしたECS Task / Service 設計**について、
**①既存オンプレ値からの設定値算出方法（実務的な計算式・考え方）**と
**②その設定に関係するAWS（ECS / Fargate / ALB）の制限**を、**項目別に体系的**に説明します。

> ※「どう決めるか」「なぜその値か」「AWS制限にどう引っかかるか」を重視しています。

---

## 1. ECS Task / Service 設計の全体観
[🔙 目次に戻る](#index)


#### ECS Task / Service で設計対象となる主な項目
[🔙 目次に戻る](#index)


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
[🔙 目次に戻る](#index)


---

### 2.1 オンプレCPU情報の取得
[🔙 目次に戻る](#index)


#### 入手情報（必須）
[🔙 目次に戻る](#index)


| 情報          | 例            |
| ----------- | ------------ |
| CPUコア数      | 4 Core       |
| 利用率         | 平常30%、ピーク70% |
| JVM Thread数 | 200          |
| 同時ユーザ数      | 300          |

---

### 2.2 ECS CPU値の考え方
[🔙 目次に戻る](#index)


#### ECS CPU単位
[🔙 目次に戻る](#index)


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
[🔙 目次に戻る](#index)


#### ① オンプレの実効CPU使用量
[🔙 目次に戻る](#index)


```
4 core × 70%（ピーク）＝ 2.8 core
```

#### ② コンテナオーバーヘッド考慮
[🔙 目次に戻る](#index)


```
2.8 × 1.2（余裕） ≒ 3.4 core
```

#### ③ ECS設定値
[🔙 目次に戻る](#index)


➡ **4096 CPU（4 vCPU）**

---

### 2.4 AWS制限（CPU）
[🔙 目次に戻る](#index)


### Fargate制限（重要）
[🔙 目次に戻る](#index)


* CPUとMemoryは**組み合わせ固定**
* CPU最大：**16 vCPU（16384）**

---

## 3. Memory（メモリ）設計
[🔙 目次に戻る](#index)


---

### 3.1 オンプレのメモリ情報
[🔙 目次に戻る](#index)


#### 入手情報
[🔙 目次に戻る](#index)


| 項目        | 例      |
| --------- | ------ |
| 物理メモリ     | 16GB   |
| JVM Heap  | -Xmx8G |
| 非Heap     | 約2GB   |
| OS/Tomcat | 約2GB   |

---

### 3.2 メモリ算出方法
[🔙 目次に戻る](#index)


#### ① 実使用量
[🔙 目次に戻る](#index)


```
8G（Heap）+ 2G（NonHeap）+ 2G（OS） = 12G
```

#### ② バースト余裕
[🔙 目次に戻る](#index)


```
12G × 1.3 = 15.6G
```

#### ③ ECS設定値
[🔙 目次に戻る](#index)


➡ **Memory = 16GB（16384）**

---

### 3.3 AWS制限（Memory）
[🔙 目次に戻る](#index)


#### Fargate制限
[🔙 目次に戻る](#index)


| CPU  | Memory選択肢 |
| ---- | --------- |
| 1024 | 2–8 GB    |
| 2048 | 4–16 GB   |
| 4096 | 8–30 GB   |

❗ **自由指定不可**

---

## 4. JVM Heap設計（超重要）
[🔙 目次に戻る](#index)


---

### 4.1 原則
[🔙 目次に戻る](#index)


> **JVM HeapはECS Memoryの50〜70%**

#### 計算例
[🔙 目次に戻る](#index)


```
ECS Memory = 16GB
Heap = 10GB（約62%）
```

#### JVMオプション例
[🔙 目次に戻る](#index)


```bash
-Xms10G
-Xmx10G
-XX:MaxMetaspaceSize=512M
```

---

### 4.2 注意点
[🔙 目次に戻る](#index)


* Container OOM Kill防止
* 非Heap領域（Metaspace, Thread, DirectBuffer）確保

---

## 5. ポート / ネットワーク設計
[🔙 目次に戻る](#index)


---

## 5.1 ポート
[🔙 目次に戻る](#index)


#### オンプレ
[🔙 目次に戻る](#index)


* Tomcat：8080固定

#### ECS
[🔙 目次に戻る](#index)


* コンテナPort：8080
* ALB TargetPort：8080

---

### 5.2 AWS制限
[🔙 目次に戻る](#index)


| 項目             | 制限          |
| -------------- | ----------- |
| ALB Target     | 最大1,000     |
| 同時接続           | ソフトリミット     |
| Ephemeral Port | 32768–61000 |

---

## 6. 同時接続・スレッド設計
[🔙 目次に戻る](#index)


---

## 6.1 Tomcat Thread算出
[🔙 目次に戻る](#index)


#### オンプレ設定確認
[🔙 目次に戻る](#index)


```xml
maxThreads="200"
```

#### ECS換算
[🔙 目次に戻る](#index)


* 1 vCPUあたり **約50〜100 threads**
* 4 vCPU → 200〜400 threads

---

### 6.2 AWS制限
[🔙 目次に戻る](#index)


* コンテナ自体の制限なし
* **ALB idle timeout（デフォルト60秒）**

---

## 7. Desired / Min / Max Task数
[🔙 目次に戻る](#index)


---

### 7.1 計算ロジック
[🔙 目次に戻る](#index)


#### ① オンプレ
[🔙 目次に戻る](#index)


* 物理サーバ1台
* ピーク時70%

#### ② ECS
[🔙 目次に戻る](#index)


* 1Task = ピークの50〜60%

➡ **Min=2 / Desired=2 / Max=6**

---

### 7.2 AWS制限
[🔙 目次に戻る](#index)


| 項目            | 制限     |
| ------------- | ------ |
| Service Task数 | 10,000 |
| ALB Target    | 1,000  |

---

## 8. Auto Scaling 設計
[🔙 目次に戻る](#index)


---

## 8.1 スケール指標
[🔙 目次に戻る](#index)


| 指標          | 目安             |
| ----------- | -------------- |
| CPU         | 60–70%         |
| Memory      | 70%            |
| ALB Request | 1,000 req/Task |

---

### 8.2 AWS制限
[🔙 目次に戻る](#index)


* スケールクールダウン最小：**1分**
* スケール単位：**1 Task**

---

## 9. Health Check / 起動時間
[🔙 目次に戻る](#index)


---

## 9.1 起動時間計算
[🔙 目次に戻る](#index)


| 内容         | 秒  |
| ---------- | -- |
| JVM起動      | 30 |
| WAR展開      | 40 |
| DB接続       | 20 |
| ➡ **約90秒** |    |

---

## 9.2 設定
[🔙 目次に戻る](#index)


| 項目                  | 値   |
| ------------------- | --- |
| Health Interval     | 30  |
| Unhealthy Threshold | 5   |
| Grace Period        | 180 |

---

### 9.3 AWS制限
[🔙 目次に戻る](#index)


* ALB Health Check Timeout：2–120秒
* Interval：5–300秒

---

## 10. ECS Task / Service 制限まとめ（重要）
[🔙 目次に戻る](#index)


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
