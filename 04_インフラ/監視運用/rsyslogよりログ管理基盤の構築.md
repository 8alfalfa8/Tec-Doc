# ◆ rsyslogよりログ管理基盤の構築

rsyslog（**R**ocket-fast **SY**Stem for **LOG** processing）は、Linux/Unix系で広く利用される**高性能なSyslogデーモン兼ログ処理基盤**です。  
従来の syslogd を拡張したもので、**システムログの収集・保存・転送・加工・ルーティング**を高い柔軟性で実現できます。  
多くのLinuxディストリビューションで標準採用されています。 ([rsyslog][1])

---

## 1. rsyslogとは何か

一言でいうと：

> **「Linux/Unixのログを集約・加工・転送するための高性能ログパイプラインエンジン」**

です。

単なる `/var/log/messages` 出力ツールではなく、現在では：

* ローカルログ保存
* リモートSyslogサーバ転送
* JSON変換
* DB/Elasticsearch/Kafka連携
* SIEM/SOC連携
* ログフィルタリング / ルーティング

まで担える**本格的なログ基盤コンポーネント**です。 ([rsyslog][2])

---

## 2. 主な用途

---

## ① OS/ミドルウェアログの収集

例：

* kernel log
* auth.log
* messages
* secure
* cron
* mail

---

### ② リモートログ集約

各サーバ/NW機器/Firewallから：

```text
Syslog over UDP/TCP/TLS
```

で中央ログサーバへ集約

---

### ③ SIEM/監査基盤への転送

* Splunk
* Elastic Stack
* Graylog
* Loki
* QRadar
* Sentinel

---

### ④ ログ加工/正規化

* JSON変換
* 不要項目除去
* タグ付与
* CEF変換
* RFC3164 → RFC5424変換

---

## 3. rsyslogのアーキテクチャ

rsyslogは**プラグイン型マイクロカーネル構造**です。
機能をモジュールで追加できます。 ([docs.rsyslog.com][3])

---

### 全体処理フロー

```text
[Log Source]
   ↓
[Input Module]
   ↓
[Queue]
   ↓
[Parser]
   ↓
[Ruleset / Filter]
   ↓
[Action / Output]
   ↓
[Destination]
```

---

## 4. 主要コンポーネント詳細

---

### 4-1. Input Module（入力）

ログ受信元

| Module    | 用途                |
| --------- | ----------------- |
| imuxsock  | ローカルsyslog socket |
| imjournal | systemd journal読取 |
| imfile    | 任意ファイル監視          |
| imtcp     | TCP syslog受信      |
| imudp     | UDP syslog受信      |
| imrelp    | RELP信頼転送          |

---

### 4-2. Parser（解析）

ログフォーマット解析

対応例：

* RFC3164
* RFC5424
* JSON
* CEF
* LEEF

---

### 4-3. Ruleset / Filter（振分）

条件分岐

例：

```text
if facility == authpriv then /var/log/secure
if hostname == fw01 then remote-fw.log
```

---

### 4-4. Output Module（出力）

| Module          | 出力先           |
| --------------- | ------------- |
| omfile          | ファイル          |
| omfwd           | リモートSyslog    |
| omhttp          | HTTP API      |
| omkafka         | Kafka         |
| omelasticsearch | Elasticsearch |
| ommysql         | MySQL         |
| ompgsql         | PostgreSQL    |

---

## 5. rsyslogの強み

---

### 5-1. 高性能

非常に高速です。

* 数十万～100万 msg/sec級実績あり（条件依存）
* マルチスレッド処理対応
* バッチ/非同期キュー処理可能 ([GitHub][4])

---

### 5-2. Queueベースで信頼性が高い

転送先障害時：

```text
送信失敗 → Queue保持 → 復旧後再送
```

可能

---

### 5-3. 柔軟なフィルタリング

* facility
* severity
* hostname
* programname
* regex
* contains
* startswith

等で制御可能

---

### 5-4. TLS暗号化対応

Syslog over TLS：

```text
TCP 6514
```

で暗号化転送可能

---

## 6. 設定例

---

### 6-1. 特定ログをファイル保存

```conf
authpriv.*    /var/log/secure
```

---

### 6-2. 全ログをリモート転送

```conf
*.* @@logserver.example.com:514
```

意味：

| 記号 | 意味  |
| -- | --- |
| @  | UDP |
| @@ | TCP |

---

### 6-3. TLS転送例

```conf
action(
  type="omfwd"
  target="log.example.com"
  port="6514"
  protocol="tcp"
  StreamDriver="gtls"
)
```

---

## 7. Queue（超重要）

rsyslogの信頼性を支える核心機能です。  
Queueにより：

---

### In-Memory Queue

高速だが再起動で消失

---

### Disk-Assisted Queue

メモリ超過/障害時にディスク退避

---

### Persistent Queue

完全永続化

---

### 用途

```text
転送先ダウン
ネットワーク断
SIEM遅延
大量バーストログ
```

吸収可能。 ([rsyslog][5])

---

## 8. 実務での典型構成

---

### 小規模

```text
App/OS
 ↓
rsyslog
 ↓
/var/log/*
```

---

### 中規模

```text
各サーバ
 ↓
rsyslog Forwarder
 ↓
Central rsyslog Collector
 ↓
Elastic / Splunk / Loki
```

---

### 大規模/SIEM構成

```text
Network Device / FW / Server / App
        ↓
   Edge rsyslog Relay
        ↓
   Central Collector Cluster
        ↓
 Kafka / SIEM / DataLake
```

---

## 9. 他ログ基盤との比較

| 製品         | 特徴             | 用途            |
| ---------- | -------------- | ------------- |
| rsyslog    | 軽量・高速・標準的      | OS/NWログ基盤     |
| syslog-ng  | 柔軟性高           | 複雑ルーティング      |
| Fluent Bit | Cloud Native向け | Kubernetes    |
| Logstash   | 重いが高機能         | ETL/加工中心      |
| Vector     | 次世代高速          | Observability |

---

## 10. 注意点 / 設計ポイント

---

### 10-1. journaldとの関係

最近のLinuxでは：

```text
Application
 ↓
systemd-journald
 ↓
rsyslog
 ↓
/var/log/*
```

構成が一般的です。

そのため：

* journald rate limit
* rsyslog rate limit

双方考慮必要
（実運用でもハマりやすいポイント）

---

### 10-2. ログローテーションは別管理

rsyslog自身ではなく通常：

```text
logrotate
```

で管理します。  
（保持期間/世代管理） ([Reddit][6])

---

## 11. インフラ設計観点での評価

rsyslogは特に以下で有効です。

---

### 監査ログ集約

* Linux監査
* sudo履歴
* 認証ログ
* セキュリティイベント

---

### ミッションクリティカル運用

* Queueによる耐障害性
* TLS暗号化
* 中継サーバ構成
* Store&Forward

---

### SIEM前段ログハブ

```text
各種ログソース
↓
rsyslogで正規化/集約
↓
SIEM投入
```

---

## 12. まとめ

---

### rsyslogとは

> **高性能・高信頼・高拡張性を持つエンタープライズ向けログ収集/転送基盤**

---

## 特徴まとめ

| 項目 | 内容                        |
| -- | ------------------------- |
| 役割 | ログ収集/保存/転送/加工             |
| 強み | 高速・軽量・Queue信頼性            |
| 対応 | Syslog/TLS/JSON/DB/Kafka等 |
| 用途 | Central Logging / SIEM連携  |
| 採用 | Linux標準級                  |

[1]: https://www.rsyslog.com/doc/rsyslog-book.html?utm_source=chatgpt.com "rsyslog documentation"
[2]: https://www.rsyslog.com/doc/index.html?utm_source=chatgpt.com "rsyslog 8.2510.0 documentation"
[3]: https://docs.rsyslog.com/doc/development/architecture.html?utm_source=chatgpt.com "System Architecture - rsyslog 8 daily stable documentation"
[4]: https://github.com/rsyslog/rsyslog?utm_source=chatgpt.com "GitHub - rsyslog/rsyslog: a Rocket-fast SYStem for LOG processing pipelines"
[5]: https://www.rsyslog.com/doc/development/engine_overview.html?utm_source=chatgpt.com "Developer Overview: rsyslog Engine - rsyslog documentation"
[6]: https://www.reddit.com/r/linuxadmin/comments/mgjsxp?utm_source=chatgpt.com "How rsyslog knows what to forward"

---
---
# ◆ AWS/オンプレ大規模システムにおけるrsyslogを用いた中央ログ集約アーキテクチャ設計

以下では、**AWS / オンプレ大規模システムにおける rsyslog を用いた中央ログ集約アーキテクチャ設計**を、実運用レベルを意識して整理します。  
単なる「ログを送る」構成ではなく、**高可用性・耐障害性・監査要件・SIEM連携・運用性**まで含めた設計観点です。

---

## 1. なぜ rsyslog を中央ログ集約に使うのか

大規模環境では、各サーバが個別にログを保持するだけでは以下の問題があります。

* 障害調査時にログが分散する
* 改ざん検知/監査要件を満たしにくい
* サーバ廃棄時にログ消失
* SIEM/分析基盤への投入が非効率
* 大量ログ時に転送先が詰まりやすい

rsyslog は以下を満たせるため、**「ログハブ」** として適しています。

* 高速転送
* Queue/再送制御
* TLS暗号化
* 中継/多段構成
* 柔軟なルーティング
* 多様な出力先（SIEM / Kafka / Elasticsearch 等）

---

## 2. 全体アーキテクチャ（推奨構成）

### ハイブリッド大規模環境例

```text
[App/OS/NW Device]
      │
      ▼
+------------------+
| Local rsyslog    |
| Forwarder Agent  |
+------------------+
      │ TLS/RELP
      ▼
+------------------+      +------------------+
| Relay/Edge #1    | HA   | Relay/Edge #2    |
+------------------+      +------------------+
      │
      ▼
+------------------------------+
| Central Collector Cluster    |
| (rsyslog Aggregator)         |
+------------------------------+
      │
      ├─→ SIEM (Splunk/QRadar)
      ├─→ Elasticsearch/OpenSearch
      ├─→ S3/DataLake
      └─→ Long-term Archive
```

---

## 3. レイヤ別役割設計

---

### 3-1. Local Forwarder（各サーバ）

#### 役割

* ローカルログ収集
* 一次フィルタ
* タグ付与
* Queue保持
* Relayへ転送

#### 設計ポイント

| 項目    | 推奨                  |
| ----- | ------------------- |
| Queue | Disk Assisted Queue |
| 転送    | TCP/TLS or RELP     |
| 保持    | 数GB～数十GB            |
| 再送    | 無制限 or 長時間          |

---

### 3-2. Relay/Edge層

#### 役割

* バースト吸収
* ネットワーク境界中継
* 一次正規化
* ルーティング

#### 必要理由

大規模環境では：

```text
1000台 → Collector直送
```

は危険です。

理由：

* Collector負荷集中
* 接続数過多
* 障害時影響大

そのため：

```text
1000台 → 10 Relay → Collector
```

が一般的です。

---

### 3-3. Central Collector

#### 役割

* 全ログ集約
* 永続保存
* SIEM連携
* 監査保管

---

## 4. 冗長化設計（超重要）

---

### 4-1. Relay冗長化

```text
Forwarder
 ├─ Primary Relay
 └─ Secondary Relay
```

#### rsyslog設定例

```conf
action(
 type="omfwd"
 target="relay1"
 action.resumeRetryCount="-1"
)

action(
 type="omfwd"
 target="relay2"
 action.execOnlyWhenPreviousIsSuspended="on"
)
```

---

### 4-2. Collector冗長化

#### 方法A：LB配下

```text
Relay
 ↓
NLB/HAProxy
 ↓
Collector Cluster
```

---

#### 方法B：Anycast / DNS RR

高性能環境向け

---

### 4-3. Queueによる障害吸収

Collector全断時：

```text
Forwarder Queue
 ↓
Relay Queue
 ↓
Disk Spill
```

で耐える設計

---

## 5. Queue設計（最重要）

---

### Queue階層

```text
Host Queue
Relay Queue
Collector Queue
```

---

### 設計例

#### 想定条件

* 1台平均：500 msg/sec
* 1000台
* 総量：500,000 msg/sec
* 障害耐性：30分

---

#### 必要容量概算

```text
500,000 × 1800 = 900,000,000 messages
```

1 msg = 500B とすると：

```text
約450GB
```

→ Queue/Storage設計必須

---

### 推奨Queue設定

```conf
queue.type="LinkedList"
queue.filename="fwdqueue"
queue.maxdiskspace="50g"
queue.saveonshutdown="on"
queue.highwatermark="400000"
queue.lowwatermark="200000"
```

---

## 6. セキュリティ/TLS設計

---

### 推奨プロトコル

| Protocol   | 推奨度 | 理由        |
| ---------- | --- | --------- |
| UDP Syslog | 非推奨 | 欠損/順序保証なし |
| TCP Syslog | 可   | 基本        |
| TCP/TLS    | 推奨  | 暗号化       |
| RELP/TLS   | 最推奨 | 配送保証      |

---

### TLS設計例

```text
Forwarder
  ↓ mTLS
Relay
  ↓ mTLS
Collector
```

---

### 証明書管理

* Private CA運用推奨
* Host証明書自動配布
* 期限監視必須

---

## 7. AWS環境での設計ポイント

---

### 配置例

```text
EC2/EKS/ECS
 ↓
Local rsyslog
 ↓
Private Subnet Relay
 ↓
Collector ASG
```

---

### AWS連携先

#### S3保管

* 長期監査保存

#### OpenSearch

* 検索分析

#### Security Lake / SIEM

* セキュリティ監視

---

### 注意点

#### CloudWatch Logsとの棲み分け

| 用途           | 推奨         |
| ------------ | ---------- |
| AWS Nativeログ | CloudWatch |
| OS/syslog    | rsyslog    |
| SIEM前段統合     | rsyslog    |

---

## 8. SIEM連携設計

---

### 典型パターン

```text
Collector
 ├─ omfwd → Splunk HEC
 ├─ omkafka → Kafka
 ├─ omelasticsearch
 └─ omfile → Archive
```

---

### 正規化例

Collectorで：

```text
RFC3164 → JSON
Host情報付加
Environment Tag付加
Region/AZ付加
```

---

## 9. 運用設計（重要）

---

### 監視項目

| 監視対象              | 内容       |
| ----------------- | -------- |
| Queue深さ           | 輻輳検知     |
| Disk使用率           | Queue枯渇  |
| Input/Output Rate | 性能監視     |
| TLS期限             | 証明書期限    |
| Process死活         | daemon監視 |

---

### 障害時Runbook

#### Queue増加

原因：

* SIEM遅延
* Network断
* Collector障害

対処：

1. Queue深さ確認
2. 転送先確認
3. Disk残量確認
4. 必要に応じ迂回ルート切替

---

## 10. 実務ベストプラクティス

---

### Do

* Relay層を置く
* TLS必須
* Disk Queue有効化
* Queue容量を障害時間ベース算出
* JSON正規化して下流連携
* 監視/可視化を行う

---

### Don't

* UDP運用
* Collector単一構成
* Queueなし
* Disk容量無設計
* SIEM直送のみ

---

## 11. 推奨構成まとめ

```text
[Server/NW]
   ↓
[Local rsyslog Forwarder]
   ↓ TLS/RELP
[Relay HA Cluster]
   ↓
[Collector Cluster]
   ↓
[SIEM / OpenSearch / S3]
```

---

## 12. インフラアーキテクト視点の評価ポイント

面接/レビューで評価される観点：

---

### 可用性

* Queue/再送設計
* Relay/Collector冗長化

---

### 性能

* msg/sec見積
* Queue sizing

---

### セキュリティ

* TLS/mTLS
* 証明書運用

---

### 運用

* Queue監視
* 証明書期限監視
* 障害Runbook

---
---

# ◆ AWSのCloudWatchに統合して一元管理する設計

以下では、**rsyslog を前段に置きつつ、最終的に AWS の CloudWatch に統合して一元管理する場合の設計**を、
**大規模・実運用・監査対応を前提**に整理します。

---

## 1. 前提：なぜ「直接 CloudWatch 送信」ではなく rsyslog を挟むのか

CloudWatch Logs Agent / Unified Agent を各サーバに直接入れる構成も可能ですが、大規模環境では課題があります。

| 課題                | 内容                        |
| ----------------- | ------------------------- |
| 送信先制御が弱い          | 複雑なルーティング/加工が苦手           |
| バッファ制御限定          | 長時間障害吸収に弱い                |
| マルチ送信が苦手          | SIEM/監査保管との並列送信が面倒        |
| Syslog/NW機器統合しにくい | NW機器はCloudWatch Agent送信不可 |
| 標準化困難             | Linux/Windows/NW混在で統一困難   |

そのため実務では：

> **rsyslog を「ログ集約・正規化ハブ」**
> **CloudWatch を「最終統合監視/検索基盤」**

として役割分離する設計がよく採られます。

---

## 2. 推奨全体アーキテクチャ

```text
[EC2 / On-Prem / NW Device / App]
          │
          ▼
   Local rsyslog Forwarder
          │
      TLS / RELP
          ▼
   Relay / Aggregator Layer
          │
          ▼
 CloudWatch Forwarder Node
 (rsyslog → CW Agent / Fluent Bit)
          │
          ▼
   Amazon CloudWatch Logs
          │
 ├─ Metric Filter
 ├─ Logs Insights
 ├─ Alarm
 ├─ Subscription Filter
 └─ S3 Archive / SIEM連携
```

---

## 3. 設計思想（重要）

CloudWatch を「保存先」ではなく：

> **Observability / Monitoring / Alerting Platform**

として扱います。

rsyslog 側は：

> **Reliable Log Transport Layer**

です。

---

## 4. CloudWatch 連携方式比較

---

### 方式A：Collectorサーバから CloudWatch Agent 転送（推奨）

```text
rsyslog Collector
   ↓ /var/log/aggregated/*.log
CloudWatch Agent
   ↓
CloudWatch Logs
```

#### メリット

* AWS標準サポート
* 安定運用しやすい
* 障害切り分け容易
* CloudWatch Agent管理容易

#### デメリット

* 一度ファイル経由

---

### 方式B：Fluent Bit連携

```text
rsyslog → Fluent Bit → CloudWatch
```

#### メリット

* 高性能
* 柔軟変換可能

#### デメリット

* 運用複雑化

---

### 方式C：Lambda/Kinesis経由

大規模分析向け
（通常不要）

---

## 5. 推奨ロググループ設計

CloudWatch設計で非常に重要です。

---

### 推奨命名例

```text
/company/prod/os/auth
/company/prod/os/messages
/company/prod/app/api
/company/prod/network/firewall
/company/stg/os/auth
```

---

### 分割粒度設計

#### 粗すぎる例（NG）

```text
/all-logs
```

理由：

* 検索しにくい
* IAM制御困難
* 保持期間分離不可

---

### 細かすぎる例（NG）

```text
/host001/auth
/host002/auth
```

理由：

* 管理爆発

---

## 6. CloudWatch Stream設計

---

### 推奨

```text
{hostname}/{instance-id}
```

例：

```text
web01/i-0123456789
```

---

## 7. 保持期間設計

ログ種別ごとに分離推奨

| ログ種別     | 保持      |
| -------- | ------- |
| OS一般ログ   | 30～90日  |
| アプリログ    | 30～180日 |
| セキュリティ監査 | 1～7年    |
| 操作監査     | 1～7年    |

---

## 8. 監査要件対応

CloudWatch単体では長期保管コスト高のため：

---

### 推奨

```text
CloudWatch Logs
   ↓ Subscription
Kinesis Firehose
   ↓
S3 Archive
```

---

### 効果

* CloudWatch：短中期検索
* S3：長期監査保管

---

## 9. 監視/アラート設計

---

### Queue監視

rsyslog：

* Queue Depth
* Queue Disk Usage
* Retry Count

---

### CloudWatch側

* IncomingBytes
* IncomingLogEvents
* DeliveryErrors

---

### メトリクス化

#### 例

```text
ERROR
FATAL
Unauthorized
sudo:
```

を Metric Filter 化

---

## 10. 障害時設計

---

### CloudWatch障害時

```text
CloudWatch Agent停止
or API障害
```

↓

```text
Collector File保持
```

↓

```text
再送
```

---

### Collector障害時

```text
Forwarder Queue保持
```

---

## 11. AWS ネットワーク設計

---

### Private環境推奨

```text
Collector
 ↓
VPC Endpoint (Logs)
 ↓
CloudWatch Logs
```

---

### 理由

* Internet不要
* セキュア
* NAT費削減

---

## 12. IAM設計

CloudWatch Forwarder Node に最小権限付与

例：

```json
logs:CreateLogGroup
logs:CreateLogStream
logs:PutLogEvents
logs:DescribeLogStreams
```

---

## 13. コスト設計（重要）

CloudWatch Logs は高額化しやすいです。

---

### 注意点

大量ログ環境では：

```text
500GB/day
```

規模でかなり高額になります。

---

### 対策

#### rsyslogで事前フィルタ

除外例：

* debug
* healthcheck
* 不要アクセスログ

---

#### サンプリング

大量アクセスログ

---

#### 圧縮/アーカイブ

S3移送

---

## 14. 実運用ベストプラクティス

---

### 推奨構成

```text
Source Hosts
   ↓
Local rsyslog
   ↓
Relay Cluster
   ↓
Collector Cluster
   ↓
CloudWatch Forwarder
   ↓
CloudWatch Logs
   ↓
S3 Archive
```

---

## 15. 設計レビュー観点

---

### 可用性

* Queue多段化
* Collector冗長化
* CW障害吸収

---

### 運用性

* ロググループ命名統一
* 保持期間設計
* Runbook整備

---

### コスト

* Filter設計
* Archive分離

---

## 16. 結論（推奨アーキテクチャ）

---

### エンタープライズ推奨

> **rsyslog = Reliable Transport / Normalize Layer**  
> **CloudWatch = Monitoring / Search / Alert Layer**  
> **S3 = Archive / Audit Layer**

---

### 最終構成図

```text
[All Systems]
   ↓
rsyslog Forwarder
   ↓
Relay HA
   ↓
Collector HA
   ↓
CloudWatch Logs
   ↓
S3 Archive / SIEM
```

---
---

# ◆ rsyslog と CloudWatch における分類体系

以下では、**rsyslog と CloudWatch における「種類」「レベル」「分類体系」** を、
実務設計で混同しやすいポイントを整理しながら体系的に説明します。

---

## 1. まず整理：rsyslog と CloudWatch で“レベル”の意味が異なる

| 観点     | rsyslog                    | CloudWatch           |
| ------ | -------------------------- | -------------------- |
| 基本概念   | Syslog標準に基づくログ分類           | AWSログ保存/監視サービス       |
| レベルの意味 | Syslog Severity / Facility | ログの階層構造・メトリクス/アラーム設定 |
| 標準化    | RFC3164 / RFC5424          | AWS独自概念              |
| 主用途    | ログ生成/転送時の分類                | 保存・分析・監視             |

---

## 2. rsyslog の分類体系（超重要）

Syslog は主に以下でログを分類します。

```text
Facility（種別）
Severity（重要度）
```

---

## 3. Severity（重要度レベル）

Syslog の重大度です。
**0 が最重要、7 が最軽微**です。

| 数値 | 名称             | 意味       | 実務用途      |
| -- | -------------- | -------- | --------- |
| 0  | emerg          | システム使用不能 | カーネルパニック等 |
| 1  | alert          | 即時対応必要   | DB停止等     |
| 2  | crit           | 重大障害     | 主要機能停止    |
| 3  | err / error    | エラー      | 処理失敗      |
| 4  | warning / warn | 警告       | リソース逼迫    |
| 5  | notice         | 通知       | 重要イベント    |
| 6  | info           | 情報       | 通常ログ      |
| 7  | debug          | デバッグ     | 開発/調査     |

---

### 実務での扱い例

#### CloudWatch 監視対象

```text
severity <= 3
```

→ 即アラート

---

#### 保存のみ

```text
severity 4-6
```

---

#### 通常除外

```text
severity=7
```

（コスト削減）

---

## 4. Facility（ログ種別）

ログの発生元カテゴリです。

---

### 標準Facility一覧

| Facility      | 用途             |
| ------------- | -------------- |
| kern          | Kernel         |
| user          | User Process   |
| mail          | Mail System    |
| daemon        | System Daemon  |
| auth          | Authentication |
| authpriv      | Security/Auth  |
| cron          | Cron           |
| local0～local7 | カスタム用途         |

---

### 実務でよく使う local0-local7

アプリ独自ログ分類用

例：

| Facility | 用途           |
| -------- | ------------ |
| local0   | Web App      |
| local1   | Batch        |
| local2   | API          |
| local3   | Security App |

---

## 5. rsyslog フィルタ例

---

### Severityで振り分け

```conf
*.err    /var/log/error.log
```

---

### Facilityで振り分け

```conf
authpriv.*    /var/log/secure
```

---

### 組み合わせ

```conf
local0.warning    /var/log/app_warn.log
```

---

## 6. CloudWatch Logs の階層構造

CloudWatch Logs には Syslog のような標準 Severity はありません。
CloudWatch は**保存構造**を持ちます。

---

### 階層

```text
Log Group
 └ Log Stream
    └ Log Event
```

---

## 7. Log Group（論理分類）

最上位コンテナ

---

### 例

```text
/company/prod/os/auth
/company/prod/app/api
/company/prod/network/fw
```

---

### 用途

* 保持期間設定
* IAM制御
* Subscription設定
* Metric Filter設定

---

## 8. Log Stream（送信元単位）

通常：

```text
hostname / instance-id
```

---

### 例

```text
web01/i-123456
```

---

## 9. Log Event

1件1件のログレコード

---

## 10. CloudWatch での“レベル管理”方法

CloudWatch 自体は Severity を理解しないため：

---

### 方法1：文字列ベース

```text
ERROR
WARN
INFO
DEBUG
```

---

### 方法2：JSON構造化

推奨

```json
{
  "severity": "ERROR",
  "facility": "auth",
  "host": "web01",
  "message": "login failed"
}
```

---

## 11. CloudWatch Metric Filter

ログから疑似的にレベル抽出

---

### 例

```text
ERROR
FATAL
CRITICAL
```

検知 → Metric化

---

## 12. 実務推奨：rsyslog→CloudWatch マッピング

---

### 推奨マッピング

| Syslog Severity | CloudWatch運用      |
| --------------- | ----------------- |
| 0-2             | Critical Alarm    |
| 3               | Error Alarm       |
| 4               | Warning Dashboard |
| 5-6             | Search Only       |
| 7               | 原則除外              |

---

## 13. 代表的ログ分類設計例

---

### OSログ

```text
/company/prod/os/messages
/company/prod/os/secure
/company/prod/os/audit
```

---

### Middleware

```text
/company/prod/mw/nginx
/company/prod/mw/apache
/company/prod/mw/postgres
```

---

### App

```text
/company/prod/app/backend
/company/prod/app/frontend
```

---

## 14. 推奨JSON正規化例

CloudWatchで扱いやすくするため：

```json
{
  "timestamp": "2026-04-30T12:00:00Z",
  "hostname": "web01",
  "env": "prod",
  "facility": "authpriv",
  "severity": "err",
  "program": "sshd",
  "message": "Failed password"
}
```

---

## 15. 監視設計例

---

### Critical

```text
severity in (emerg,alert,crit)
```

即PagerDuty/SNS

---

### Warning

```text
severity=warning
```

Dashboardのみ

---

### Debug

保存しない

---

## 16. 設計時の注意点

---

### rsyslog Severity と App Log Level の違い

混同注意

---

#### App Log

```text
TRACE
DEBUG
INFO
WARN
ERROR
FATAL
```

---

#### Syslog Severity

```text
debug
info
notice
warning
err
crit
alert
emerg
```

---

### マッピングルールを決める必要あり

---

## 17. 実務ベストプラクティス

---

### rsyslog 側

* Facilityでソース分類
* Severityで重要度分類
* JSON化して転送

---

### CloudWatch 側

* Log Groupでドメイン分割
* Metric Filterで監視
* Retention分離
* SubscriptionでS3/SIEM転送

---

## 18. まとめ

---

### rsyslog

> **「ログの意味付け・分類」担当**

---

### CloudWatch

> **「保存・検索・監視」担当**

---

### 設計原則

```text
Source Log
 ↓
rsyslogでFacility/Severity付与
 ↓
JSON正規化
 ↓
CloudWatch保存
 ↓
Metric Filter / Alarm
```

---

