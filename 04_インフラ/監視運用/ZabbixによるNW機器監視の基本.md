# ◆ ZabbixによるNW機器監視の基本

Zabbix では、ルータ、L2/L3スイッチ、FW、LB、UPS、無線APなどのNW機器を主に **SNMP** で監視します。

SNMP監視では、NW機器にエージェントを入れる必要はなく、Zabbix Server / Proxy から機器に対してSNMPで情報取得します。
特にNW機器では、CPU、メモリ、IF帯域、エラーカウンタ、温度、FAN、電源状態などの監視が一般的です。 ([Zabbix][1])

---

## SNMPとは

Simple Network Management Protocol は、NW機器やサーバの状態を取得するための標準プロトコルです。

主に以下3種類があります。

* SNMPv1
* SNMPv2c
* SNMPv3

SNMPv1/v2c は community string（例: public/private）ベースで簡単ですが、暗号化がありません。

一方、SNMPv3 は認証・暗号化に対応しており、実運用では v3 を推奨します。特にインターネット越しや拠点間監視では、v2cを避けるべきです。 ([Zabbix Blog][2])

---

## ZabbixにおけるSNMP監視方式

ZabbixでのSNMP監視は大きく2種類あります。

### 1. Polling監視

Zabbix Serverが定期的にNW機器へ問い合わせを行います。

```text
Zabbix → SNMP GET → Router / Switch / FW
```

例えば5分ごとにCPU使用率、IF通信量、温度などを取得します。

Pollingは以下のような継続的な数値監視に向いています。

* CPU使用率
* メモリ使用率
* IF帯域
* エラーパケット数
* 温度
* ファン回転数
* 稼働時間
* Ping応答
* セッション数

Pollingは履歴・トレンド分析に強く、グラフ化しやすいのが特徴です。 ([thezabbixbook.com][3])

---

### 2. Trap監視

SNMP Trapは、機器側からイベント発生時に即時通知する方式です。

```text
Router / Switch → SNMP Trap → Zabbix
```

例えば以下のようなイベントをリアルタイム通知できます。

* IF Down / Up
* 電源断
* FAN故障
* 温度異常
* 不正ログイン
* MACアドレス変化
* 冗長回線切替
* 電源ユニット故障

Pollingでは5分ごとの監視だと障害検知が遅れる可能性がありますが、Trapならイベント発生直後に通知できます。 ([Zabbix Blog][2])

---

## PollingとTrapの使い分け

実務では、**PollingとTrapを併用**するのが基本です。

| 項目      | Polling        | Trap               |
| ------- | -------------- | ------------------ |
| 取得方式    | Zabbixが取得      | 機器が送信              |
| タイミング   | 定期             | 即時                 |
| 向いているもの | CPU、帯域、温度など継続値 | LinkDown、電源断などイベント |
| メリット    | 履歴・分析に強い       | 障害検知が速い            |
| デメリット   | 障害検知に遅延        | UDPなので取りこぼしあり      |

Trapだけに依存するのは危険です。機器が完全停止するとTrap自体を送れないためです。

そのため、以下のような設計が一般的です。

* ICMP Ping監視
* SNMP Polling監視
* SNMP Trap監視

この3つを組み合わせることで、「機器が死んだ」「SNMPだけ死んだ」「IFだけ落ちた」を切り分けしやすくなります。 
Redditでも「Trapは通知、Pollingはメトリクス取得」として併用が推奨されています。 ([Reddit][4])

---

## よく監視するSNMP OID

代表的な監視項目です。

| 監視項目       | 主なOID/MIB                        |
| ---------- | -------------------------------- |
| CPU使用率     | HOST-RESOURCES-MIB, vendor MIB   |
| メモリ使用率     | HOST-RESOURCES-MIB               |
| インタフェース状態  | IF-MIB::ifOperStatus             |
| インタフェース通信量 | IF-MIB::ifInOctets / ifOutOctets |
| IFエラー数     | IF-MIB::ifInErrors / ifOutErrors |
| 稼働時間       | SNMPv2-MIB::sysUpTime            |
| 温度         | ENTITY-SENSOR-MIB                |
| 電源/FAN状態   | ENTITY-MIB, vendor MIB           |
| シリアル番号     | ENTITY-MIB                       |
| VLAN情報     | Q-BRIDGE-MIB                     |
| BGP状態      | BGP4-MIB                         |
| OSPF状態     | OSPF-MIB                         |

標準MIBだけで取得できる項目もありますが、詳細監視にはベンダ独自MIBが必要です。

例えば以下のようなベンダMIBがあります。

* Cisco: CISCO-CPU-MIB, CISCO-MEMORY-MIB
* Juniper Networks: JUNIPER-MIB
* Fortinet: FORTINET-FORTIGATE-MIB
* MikroTik: MIKROTIK-MIB

テンプレートが対応していない場合、OIDを直接指定して独自Itemを作ることもあります。 ([Zabbix][1])

---

## Zabbixの実装構成

一般的な構成は以下です。

```text
[Zabbix Server / Proxy]
   ├─ UDP/161 → SNMP Polling
   ├─ UDP/162 ← SNMP Trap受信
   └─ ICMP Ping
        ↓
[Router / Switch / FW / UPS]
```

* UDP/161: SNMP Polling
* UDP/162: SNMP Trap受信
* ICMP: Ping監視

SNMP Trapを利用する場合は、Zabbix Server側で `snmptrapd` を動かし、Trap受信用スクリプトと連携します。
UDP/162をFWで開放する必要があります。 ([Zabbix Blog][2])

---

## ZabbixでのSNMP Trap設定の流れ

大まかな流れは以下です。

1. NW機器側でTrap送信先をZabbix Serverへ設定
2. Zabbix Server側で `snmptrapd` を導入
3. Trap受信スクリプトを設定
4. HostにSNMP Interfaceを追加
5. Item Type = SNMP trap を作成
6. Triggerを設定
7. Actionでメールやチャット通知

例えば、Link Down Trapだけを拾う場合は以下のようなItem Keyを使います。

```text
snmptrap[linkDown]
```

全Trapを拾う場合は以下です。

```text
snmptrap.fallback
```

Trapは正規表現でフィルタリングできるため、「電源断だけ」「温度異常だけ」といった制御も可能です。 ([Zabbix][5])

---

## 実務で重要なポイント

**1. SNMPv3を優先する**

特に社外回線や複数拠点監視では、SNMPv2cは平文のため避けるべきです。

**2. Trapだけに依存しない**

TrapはUDPなのでロストする可能性があります。PollingとICMPを併用します。 ([thezabbixbook.com][3])

**3. Proxyを活用する**

拠点数が多い場合は、各拠点にZabbix Proxyを置くとWAN越し通信量を削減できます。

**4. Low Level Discoveryを使う**

IF、FAN、電源、VLANなどを自動検出できます。ポート増減にも追従しやすくなります。 ([Zabbix][1])

**5. テンプレートを活用する**

Zabbixには300以上の監視テンプレートがあり、主要ベンダのNW機器はかなり自動化できます。 ([Zabbix][1])

**6. Trapログのローテーション設計を行う**

Trapログは肥大化しやすいため、logrotate設計が必要です。Zabbix側はローテーションを自動では行いません。 ([Zabbix][5])

[1]: https://www.zabbix.com/jp/network_monitoring?utm_source=chatgpt.com "Network Monitoring - Zabbix"
[2]: https://blog.zabbix.com/snmp-traps-in-zabbix/8210/?utm_source=chatgpt.com "SNMP Traps in Zabbix - Zabbix Blog"
[3]: https://www.thezabbixbook.com/nl/ch04-zabbix-collecting-data/snmp-trapping/?utm_source=chatgpt.com "SNMP Trapping - Zabbix Book"
[4]: https://www.reddit.com/r/sysadmin/comments/1qlx9mo/snmp_trap_handler_suggestions/?utm_source=chatgpt.com "SNMP trap handler suggestions"
[5]: https://www.zabbix.com/documentation/7.4/en/manual/config/items/itemtypes/snmptrap?utm_source=chatgpt.com "3 SNMP traps"

---
