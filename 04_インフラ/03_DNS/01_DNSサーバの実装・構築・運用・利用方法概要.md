<!-- TOC_START -->
<a id="index"></a>📖 目次

- [1. DNSの基礎整理（設計前提）](#1-dnsの基礎整理設計前提)
  - [1.1 DNSの役割](#11-dnsの役割)
  - [1.2 DNSサーバ種別（重要）](#12-dnsサーバ種別重要)
- [2. Linux DNSサーバ主要実装方式](#2-linux-dnsサーバ主要実装方式)
  - [2.1 代表的DNSサーバソフト](#21-代表的dnsサーバソフト)
- [3. DNSサーバ構成設計（重要）](#3-dnsサーバ構成設計重要)
  - [3.1 標準構成（推奨）](#31-標準構成推奨)
    - [ポイント](#ポイント)
  - [3.2 Split DNS（内部/外部分離）](#32-split-dns内部外部分離)
- [4. DNSサーバ構築（BIND9）](#4-dnsサーバ構築bind9)
  - [4.1 インストール（RHEL / Ubuntu）](#41-インストールrhel-ubuntu)
    - [RHEL系](#rhel系)
    - [Ubuntu](#ubuntu)
  - [4.2 基本設定ファイル構成](#42-基本設定ファイル構成)
  - [4.3 基本的な設定例](#43-基本的な設定例)
    - [named.conf（最小例）](#namedconf最小例)
    - [named.conf.options (基本的なオプション設定)](#namedconfoptions-基本的なオプション設定)
    - [named.conf (DNSキャッシュサーバーとしての設定)](#namedconf-dnsキャッシュサーバーとしての設定)
  - [4.4 ゾーンファイル例](#44-ゾーンファイル例)
    - [設定例１](#設定例１)
    - [設定例２](#設定例２)
  - [4.5 逆引きゾーンファイル](#45-逆引きゾーンファイル)
  - [4.6 起動・確認](#46-起動確認)
- [5. キャッシュDNS（Unbound）構築](#5-キャッシュdnsunbound構築)
  - [5.1 インストール](#51-インストール)
  - [5.2 設定例](#52-設定例)
- [6. DNSセキュリティ設計（必須）](#6-dnsセキュリティ設計必須)
  - [6.1 必須対策](#61-必須対策)
  - [6.2 DNSSEC（概要）](#62-dnssec概要)
  - [6.3 基本的なセキュリティ対策設定例](#63-基本的なセキュリティ対策設定例)
  - [6.4 ACL設定](#64-acl設定)
- [7. 運用設計（非常に重要）](#7-運用設計非常に重要)
  - [7.1 コマンドラインツール](#71-コマンドラインツール)
  - [7.2 ログ管理](#72-ログ管理)
  - [7.3 ゾーン転送設定](#73-ゾーン転送設定)
  - [7.4 運用タスク一覧](#74-運用タスク一覧)
  - [7.5 変更手順（例）](#75-変更手順例)
  - [7.6 監視とメンテナンス](#76-監視とメンテナンス)
    - [監視項目（Zabbix等）](#監視項目zabbix等)
    - [バックアップとリストア](#バックアップとリストア)
- [8. DNS利用（クライアント側）](#8-dns利用クライアント側)
  - [8.1 /etc/resolv.conf](#81-etcresolvconf)
  - [8.2 動作確認](#82-動作確認)
- [9. 高可用性設計](#9-高可用性設計)
- [10. 金融・公共向けDNSチェックリスト（抜粋）](#10-金融公共向けdnsチェックリスト抜粋)
- [11. まとめ（実務視点）](#11-まとめ実務視点)
<!-- TOC_END -->

# ◆ DNS概要

以下では **Linux環境におけるDNSサーバの実装・構築・運用・利用方法** を、
**実務**（**企業／金融・公共案件でも通用するレベル**） を前提に体系的に整理します。<br>
※オンプレミス／クラウド（AWS・GCP等）いずれにも適用可能な一般原則です。

---

## 1. DNSの基礎整理（設計前提）
[🔙 目次に戻る](#index)


### 1.1 DNSの役割
[🔙 目次に戻る](#index)


- ドメイン名とIPアドレスの相互変換
- 階層的な分散データベースシステム
- 主要レコードタイプ: A, AAAA, CNAME, MX, NS, TXT, PTR

DNS（Domain Name System）は以下を担います。

| 機能         | 内容               |
| ---------- | ---------------- |
| 名前解決       | FQDN → IPアドレス    |
| サービスディスカバリ | SRV / TXT レコード   |
| 冗長制御       | 複数NS、複数A         |
| セキュリティ基盤   | DNSSEC、Split DNS |
| 運用制御       | TTLによる変更影響制御     |

---

[🔙 目次に戻る](#index)


### 1.2 DNSサーバ種別（重要）
[🔙 目次に戻る](#index)


| 種別       | 役割      | 主な用途     |
| -------- | ------- | -------- |
| 権威DNS    | 正解を持つ   | 自社ドメイン管理 |
| キャッシュDNS | 問合せ中継   | クライアント向け |
| フォワーダ    | 上位へ転送   | 社内DNS    |
| リカーシブ    | 再帰問い合わせ | 社内／ISP   |
| スタブ      | 軽量参照    | コンテナ     |

👉 **実務では「権威DNS」と「キャッシュDNS」を分離**するのが原則

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 2. Linux DNSサーバ主要実装方式
[🔙 目次に戻る](#index)


### 2.1 代表的DNSサーバソフト
[🔙 目次に戻る](#index)


| ソフト          | 特徴           | 推奨用途       |
| ------------ | ------------ | ---------- |
| **BIND9(Berkeley Internet Name Domain)**    | デファクト、機能豊富、安定性が高い   | 権威／キャッシュ両用 |
| **Unbound**  | 高速・安全        | キャッシュDNS   |
| **PowerDNS** | 各種データベース連携可能     | 大規模権威DNS   |
| **dnsmasq**  | 軽量（DNSフォワーダーとDHCPサーバー）   | 小規模／開発     |
| **CoreDNS**  | Cloud Native | Kubernetes |

👉 **金融・公共案件**

* 権威DNS：**BIND / PowerDNS**
* キャッシュDNS：**Unbound**

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


## 3. DNSサーバ構成設計（重要）
[🔙 目次に戻る](#index)


### 3.1 標準構成（推奨）
[🔙 目次に戻る](#index)


```
[Client]
   |
[Cache DNS (Unbound)]
   |
[Authoritative DNS (BIND)]
   |
[Internet Root]
```

#### ポイント
[🔙 目次に戻る](#index)


* キャッシュDNSのみをクライアントに公開
* 権威DNSは直接参照させない
* NSは最低2台（異なるAZ/拠点）

---

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)


### 3.2 Split DNS（内部/外部分離）
[🔙 目次に戻る](#index)


| 領域    | 内容                   |
| ----- | -------------------- |
| 内部DNS | intranet.example.com |

[🔙 目次に戻る](#index)

| 外部DNS | example.com          |

**金融・公共では必須**

---

[🔙 目次に戻る](#index)


## 4. DNSサーバ構築（BIND9）
[🔙 目次に戻る](#index)


### 4.1 インストール（RHEL / Ubuntu）
[🔙 目次に戻る](#index)


#### RHEL系
[🔙 目次に戻る](#index)


```bash
dnf install -y bind bind-utils

# RHEL/CentOS
#sudo yum install bind bind-utils

```

[🔙 目次に戻る](#index)


#### Ubuntu
[🔙 目次に戻る](#index)


```bash
sudo apt update
sudo apt install -y bind9 dnsutils

# Debian/Ubuntu
#sudo apt update
#sudo apt install bind9 bind9-utils bind9-doc
```

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 4.2 基本設定ファイル構成
[🔙 目次に戻る](#index)


```
/etc/bind/
├── named.conf           # メイン設定ファイル
├── named.conf.local     # ローカルゾーン設定
├── named.conf.options   # オプション設定
├── named.conf.default-zones # デフォルトゾーン
└── zones/               # ゾーンファイルディレクトリ
```


| ファイル                     | 内容      |
| ------------------------ | ------- |
| /etc/named.conf          | メイン設定ファイル   |
| /var/named/              | ゾーンファイル |
| /etc/named.rfc1912.zones | ゾーン定義   |
| /var/log/named/          | ログ      |

---

[🔙 目次に戻る](#index)


### 4.3 基本的な設定例
[🔙 目次に戻る](#index)


#### named.conf（最小例）

[🔙 目次に戻る](#index)

```conf
options {
    directory "/var/named";
    recursion no;
    allow-query { any; };
    listen-on port 53 { any; };
};

zone "example.com" IN {
    type master;
    file "example.com.zone";
};
```

[🔙 目次に戻る](#index)


#### named.conf.options (基本的なオプション設定)
[🔙 目次に戻る](#index)


```bind
options {
    directory "/var/cache/bind";
    
    // リスニング設定
    listen-on port 53 { any; };
    listen-on-v6 port 53 { any; };
    
    // クエリ許可設定
    allow-query { any; };
    allow-recursion { localhost; localnets; };
    
    // フォワーダー設定（オプション）
    forwarders {
        8.8.8.8;
        8.8.4.4;
    };
    
    // DNSSEC設定
    dnssec-validation auto;
    
    // キャッシュ設定
    max-cache-size 256M;
    max-cache-ttl 3600;
};
```

[🔙 目次に戻る](#index)


#### named.conf (DNSキャッシュサーバーとしての設定)
[🔙 目次に戻る](#index)


```bind
options {
    directory "/var/cache/bind";
    recursion yes;
    allow-recursion { localhost; localnets; };
    forward only;
    forwarders {
        8.8.8.8;
        8.8.4.4;
    };
    dnssec-enable yes;
    dnssec-validation yes;
    auth-nxdomain no;

[🔙 目次に戻る](#index)

};
```


---

[🔙 目次に戻る](#index)


### 4.4 ゾーンファイル例
[🔙 目次に戻る](#index)


#### 設定例１
[🔙 目次に戻る](#index)


```zone
$TTL 3600
@   IN SOA ns1.example.com. admin.example.com. (
        2026010101 ; Serial
        3600       ; Refresh
        900        ; Retry
        604800     ; Expire
        300 )      ; Minimum

    IN NS ns1.example.com.
    IN NS ns2.example.com.

ns1 IN A 192.168.1.10
ns2 IN A 192.168.1.11
www IN A 192.168.1.100
```

[🔙 目次に戻る](#index)


#### 設定例２
[🔙 目次に戻る](#index)


```zone
; /etc/bind/zones/db.example.com
$TTL    86400
@       IN      SOA     ns1.example.com. admin.example.com. (
                        2024010101      ; Serial
                        3600            ; Refresh
                        1800            ; Retry
                        604800          ; Expire
                        86400 )         ; Minimum TTL

; NSレコード
        IN      NS      ns1.example.com.
        IN      NS      ns2.example.com.

; Aレコード
ns1     IN      A       192.168.1.10
ns2     IN      A       192.168.1.11
www     IN      A       192.168.1.100
mail    IN      A       192.168.1.101
@       IN      A       192.168.1.1

; MXレコード
        IN      MX      10 mail.example.com.

; CNAMEレコード
ftp     IN      CNAME   www.example.com.
```

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


### 4.5 逆引きゾーンファイル
[🔙 目次に戻る](#index)


```zone
; /etc/bind/zones/db.192.168.1
$TTL    86400
@       IN      SOA     ns1.example.com. admin.example.com. (
                        2024010101
                        3600

[🔙 目次に戻る](#index)

                        1800
                        604800
                        86400 )

        IN      NS      ns1.example.com.
        IN      NS      ns2.example.com.

10      IN      PTR     ns1.example.com.
11      IN      PTR     ns2.example.com.
100     IN      PTR     www.example.com.
101     IN      PTR     mail.example.com.
1       IN      PTR     example.com.
```


---

[🔙 目次に戻る](#index)


### 4.6 起動・確認
[🔙 目次に戻る](#index)


```bash
systemctl enable named
systemctl start named
```

```bash
named-checkconf
named-checkzone example.com /var/named/example.com.zone
```

---

[🔙 目次に戻る](#index)


## 5. キャッシュDNS（Unbound）構築
[🔙 目次に戻る](#index)


### 5.1 インストール
[🔙 目次に戻る](#index)


```bash
dnf install -y unbound
```

---

[🔙 目次に戻る](#index)


### 5.2 設定例
[🔙 目次に戻る](#index)


```conf
server:
  interface: 0.0.0.0
  access-control: 192.168.0.0/16 allow
  recursion: yes
  hide-identity: yes
  hide-version: yes
  prefetch: yes
```

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 6. DNSセキュリティ設計（必須）
[🔙 目次に戻る](#index)


### 6.1 必須対策
[🔙 目次に戻る](#index)


| 項目         | 内容              |
| ---------- | --------------- |
| 再帰制限       | 内部IPのみ          |
| Version隠蔽  | BIND version非公開 |
| ACL        | allow-query制御   |
| DNSSEC     | 改ざん防止           |
| TSIG       | ゾーン転送保護         |
| Rate Limit | DoS耐性           |

---

[🔙 目次に戻る](#index)


### 6.2 DNSSEC（概要）
[🔙 目次に戻る](#index)


| 項目    | 内容     |
| ----- | ------ |
| KSK   | 親ゾーン登録 |
| ZSK   | レコード署名 |
| RRSIG | 署名     |
| DS    | 親への登録  |

※金融系では「**DNSSEC対応有無**」が監査指摘になりやすい

---

[🔙 目次に戻る](#index)


### 6.3 基本的なセキュリティ対策設定例

[🔙 目次に戻る](#index)

```bind
options {
    // 再帰問い合わせの制限
    allow-recursion { localnets; trusted-nets; };
    
    // ゾーン転送の制限
    allow-transfer { none; };
    
    // クエリ制限
    rate-limit {
        responses-per-second 10;
        window 5;
    };
    
    // キャッシュポイズニング対策
    use-queryport-pool yes;
    queryport-pool-ports 5000-65000;
    
    // DNSSEC対応
    dnssec-enable yes;
    dnssec-validation yes;
};
```
---

[🔙 目次に戻る](#index)


### 6.4 ACL設定

[🔙 目次に戻る](#index)

```bind
// ACL定義
acl trusted-nets {
    192.168.1.0/24;
    10.0.0.0/8;
};

[🔙 目次に戻る](#index)


acl dns-servers {
    192.168.1.10;
    192.168.1.11;
};
```

---

[🔙 目次に戻る](#index)


## 7. 運用設計（非常に重要）
[🔙 目次に戻る](#index)


### 7.1 コマンドラインツール

[🔙 目次に戻る](#index)

```bash
# DNS設定のテスト
nslookup example.com
dig example.com
dig example.com MX
dig -x 192.168.1.1  # 逆引き

# BINDツール
named-checkconf      # 設定ファイルチェック
named-checkzone example.com /etc/bind/zones/db.example.com

# 統計情報の確認
rndc status
rndc stats
```

---

[🔙 目次に戻る](#index)


### 7.2 ログ管理

[🔙 目次に戻る](#index)

```bash
# BINDのログ設定 (named.conf)
logging {
    channel default_log {
        file "/var/log/named/named.log" versions 5 size 10m;
        severity info;
        print-time yes;
        print-severity yes;
        print-category yes;
    };
    category default { default_log; };
    category queries { default_log; };
};

# ログの確認
sudo tail -f /var/log/named/named.log
journalctl -u named -f
```

---

[🔙 目次に戻る](#index)


### 7.3 ゾーン転送設定

[🔙 目次に戻る](#index)

```bind
// マスターサーバー設定
zone "example.com" {
    type master;
    file "/etc/bind/zones/db.example.com";
    allow-transfer { 192.168.1.11; };  // スレーブサーバー
    also-notify { 192.168.1.11; };
};

// スレーブサーバー設定
zone "example.com" {
    type slave;
    file "/var/cache/bind/db.example.com";
    masters { 192.168.1.10; };
};
```

---

[🔙 目次に戻る](#index)


### 7.4 運用タスク一覧
[🔙 目次に戻る](#index)


| タスク    | 内容           |
| ------ | ------------ |
| レコード管理 | 追加/変更/削除     |
| TTL管理  | 切替影響制御       |
| 障害対応   | NXDOMAIN/遅延  |
| ログ監視   | named.log    |
| パッチ適用  | CVE対応        |
| 定期検証   | dig/nslookup |

---

[🔙 目次に戻る](#index)


### 7.5 変更手順（例）
[🔙 目次に戻る](#index)


1. TTLを事前に短縮
2. レコード追加
3. named-checkzone
4. reload
5. dig確認
6. TTL復旧

```bash
rndc reload example.com
```

---

[🔙 目次に戻る](#index)


### 7.6 監視とメンテナンス
[🔙 目次に戻る](#index)


#### 監視項目（Zabbix等）
[🔙 目次に戻る](#index)


| 項目        | 指標        |
| --------- | --------- |
| 応答時間      | ms        |
| NXDOMAIN率 | %         |
| QPS       | query/sec |
| プロセス      | named     |
| ポート       | 53        |


```bash
# サービス状態確認
systemctl status named

# DNS応答確認
dig @localhost example.com +short
dig @localhost google.com +stats

# キャッシュ状態確認
rndc dumpdb -cache
cat /var/cache/bind/named_dump.db | head -50

# リソース使用状況
ps aux | grep named
```

[🔙 目次に戻る](#index)


#### バックアップとリストア

[🔙 目次に戻る](#index)


[🔙 目次に戻る](#index)

```bash
# 設定ファイルのバックアップ
sudo tar czf /backup/bind-config-$(date +%Y%m%d).tar.gz /etc/bind/

# ゾーンファイルのバックアップ
sudo rsync -av /etc/bind/zones/ /backup/bind-zones/

# 自動バックアップスクリプト例
#!/bin/bash
BACKUP_DIR="/backup/bind"
DATE=$(date +%Y%m%d)
tar czf "$BACKUP_DIR/bind-full-$DATE.tar.gz" /etc/bind /var/cache/bind
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

[🔙 目次に戻る](#index)

```
---

[🔙 目次に戻る](#index)


## 8. DNS利用（クライアント側）
[🔙 目次に戻る](#index)


### 8.1 /etc/resolv.conf
[🔙 目次に戻る](#index)


```conf
nameserver 192.168.1.20
nameserver 192.168.1.21
search example.com
```

---

[🔙 目次に戻る](#index)


### 8.2 動作確認
[🔙 目次に戻る](#index)


```bash
dig www.example.com
nslookup www.example.com
```

[🔙 目次に戻る](#index)


---

[🔙 目次に戻る](#index)


## 9. 高可用性設計
[🔙 目次に戻る](#index)


| 方式        | 内容         |
| --------- | ---------- |
| マルチNS     | 最低2台       |
| Anycast   | 大規模向け      |
| マスター/スレーブ | ゾーン転送      |
| 冗長FW      | UDP/TCP 53 |

---

[🔙 目次に戻る](#index)


## 10. 金融・公共向けDNSチェックリスト（抜粋）
[🔙 目次に戻る](#index)


* [ ] 権威/キャッシュ分離
* [ ] 再帰制御あり
* [ ] Split DNS採用
* [ ] DNSSEC方針定義
* [ ] ログ保管6か月以上
* [ ] 変更管理台帳あり
* [ ] 障害訓練実施

---

[🔙 目次に戻る](#index)


## 11. まとめ（実務視点）
[🔙 目次に戻る](#index)


* DNSは**インフラの中核**
* 「動く」より「**安全・運用できる**」が重要
* 金融・公共では
  **設計根拠・運用ルール・監査対応** が必須
* BIND + Unbound構成が最も無難

---

[🔙 目次に戻る](#index)

