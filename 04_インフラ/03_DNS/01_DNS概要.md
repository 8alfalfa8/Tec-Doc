# ◆ DNS概要

以下では **Linux環境におけるDNSサーバの実装・構築・運用・利用方法** を、
**実務**（**企業／金融・公共案件でも通用するレベル**） を前提に体系的に説明します。
※オンプレミス／クラウド（AWS・GCP等）いずれにも適用可能な一般原則です。

---

## 1. DNSの基礎整理（設計前提）

### 1.1 DNSの役割

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

### 1.2 DNSサーバ種別（重要）

| 種別       | 役割      | 主な用途     |
| -------- | ------- | -------- |
| 権威DNS    | 正解を持つ   | 自社ドメイン管理 |
| キャッシュDNS | 問合せ中継   | クライアント向け |
| フォワーダ    | 上位へ転送   | 社内DNS    |
| リカーシブ    | 再帰問い合わせ | 社内／ISP   |
| スタブ      | 軽量参照    | コンテナ     |

👉 **実務では「権威DNS」と「キャッシュDNS」を分離**するのが原則

---

## 2. Linux DNSサーバ主要実装方式

### 2.1 代表的DNSサーバソフト

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

## 3. DNSサーバ構成設計（重要）

### 3.1 標準構成（推奨）

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

* キャッシュDNSのみをクライアントに公開
* 権威DNSは直接参照させない
* NSは最低2台（異なるAZ/拠点）

---

### 3.2 Split DNS（内部/外部分離）

| 領域    | 内容                   |
| ----- | -------------------- |
| 内部DNS | intranet.example.com |
| 外部DNS | example.com          |

**金融・公共では必須**

---

## 4. DNSサーバ構築（BIND9）

### 4.1 インストール（RHEL / Ubuntu）

#### RHEL系

```bash
dnf install -y bind bind-utils

# RHEL/CentOS
#sudo yum install bind bind-utils

```

#### Ubuntu

```bash
sudo apt update
sudo apt install -y bind9 dnsutils

# Debian/Ubuntu
#sudo apt update
#sudo apt install bind9 bind9-utils bind9-doc
```

---

### 4.2 基本設定ファイル構成

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

### 4.3 基本的な設定例

#### named.conf（最小例）
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

#### named.conf.options (基本的なオプション設定)

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

#### named.conf (DNSキャッシュサーバーとしての設定)

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
};
```


---

### 4.4 ゾーンファイル例

#### 設定例１

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

#### 設定例２

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

---

### 4.5 逆引きゾーンファイル

```zone
; /etc/bind/zones/db.192.168.1
$TTL    86400
@       IN      SOA     ns1.example.com. admin.example.com. (
                        2024010101
                        3600
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

### 4.6 起動・確認

```bash
systemctl enable named
systemctl start named
```

```bash
named-checkconf
named-checkzone example.com /var/named/example.com.zone
```

---

## 5. キャッシュDNS（Unbound）構築

### 5.1 インストール

```bash
dnf install -y unbound
```

---

### 5.2 設定例

```conf
server:
  interface: 0.0.0.0
  access-control: 192.168.0.0/16 allow
  recursion: yes
  hide-identity: yes
  hide-version: yes
  prefetch: yes
```

---

## 6. DNSセキュリティ設計（必須）

### 6.1 必須対策

| 項目         | 内容              |
| ---------- | --------------- |
| 再帰制限       | 内部IPのみ          |
| Version隠蔽  | BIND version非公開 |
| ACL        | allow-query制御   |
| DNSSEC     | 改ざん防止           |
| TSIG       | ゾーン転送保護         |
| Rate Limit | DoS耐性           |

---

### 6.2 DNSSEC（概要）

| 項目    | 内容     |
| ----- | ------ |
| KSK   | 親ゾーン登録 |
| ZSK   | レコード署名 |
| RRSIG | 署名     |
| DS    | 親への登録  |

※金融系では「**DNSSEC対応有無**」が監査指摘になりやすい

### 6.3 基本的なセキュリティ対策設定例
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

## 7. 運用設計（非常に重要）

### 7.1 コマンドラインツール
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

### 7.2 ログ管理
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

### 7.3 ゾーン転送設定
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

### 7.4 運用タスク一覧

| タスク    | 内容           |
| ------ | ------------ |
| レコード管理 | 追加/変更/削除     |
| TTL管理  | 切替影響制御       |
| 障害対応   | NXDOMAIN/遅延  |
| ログ監視   | named.log    |
| パッチ適用  | CVE対応        |
| 定期検証   | dig/nslookup |

---

### 7.5 変更手順（例）

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

### 7.6 監視項目（Zabbix等）

| 項目        | 指標        |
| --------- | --------- |
| 応答時間      | ms        |
| NXDOMAIN率 | %         |
| QPS       | query/sec |
| プロセス      | named     |
| ポート       | 53        |

---

## 8. DNS利用（クライアント側）

### 8.1 /etc/resolv.conf

```conf
nameserver 192.168.1.20
nameserver 192.168.1.21
search example.com
```

---

### 8.2 動作確認

```bash
dig www.example.com
nslookup www.example.com
```

---

## 9. 高可用性設計

| 方式        | 内容         |
| --------- | ---------- |
| マルチNS     | 最低2台       |
| Anycast   | 大規模向け      |
| マスター/スレーブ | ゾーン転送      |
| 冗長FW      | UDP/TCP 53 |

---

## 10. 金融・公共向けDNSチェックリスト（抜粋）

* [ ] 権威/キャッシュ分離
* [ ] 再帰制御あり
* [ ] Split DNS採用
* [ ] DNSSEC方針定義
* [ ] ログ保管6か月以上
* [ ] 変更管理台帳あり
* [ ] 障害訓練実施

---

## 11. まとめ（実務視点）

* DNSは**インフラの中核**
* 「動く」より「**安全・運用できる**」が重要
* 金融・公共では
  **設計根拠・運用ルール・監査対応** が必須
* BIND + Unbound構成が最も無難

---
