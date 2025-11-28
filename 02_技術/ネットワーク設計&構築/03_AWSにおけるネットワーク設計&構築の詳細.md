# AWS におけるネットワーク設計と構築 — タスク／成果物／構築手順（詳解）

以下は、企業規模のクラウド移行／新規構築プロジェクトでの**ネットワーク（VPC〜オンプレ接続〜セキュリティ）を設計・実装する際の実務フロー**です。要件定義から運用移行までの典型的なタスク、作成すべき成果物（納品物）、そして構築手順（手順書に落とすべき具体手順）を段階的にまとめます。最重要ポイントには公式ドキュメントへの参照を付けています。

---

# 1) 全体フェーズと主要タスク（上流→下流）

1. **準備／ガバナンス設計**

   * アカウント戦略（AWS Organizations を使うか、アカウント分離方針）
   * ガードレール（Service Control Policies）、IAM 基本方針
   * IP（CIDR）設計方針（将来の分割・ピアリング／Direct Connect対応を考慮）
   * Deliverable：アカウント・ガバナンス設計書、CIDRポリシー表

2. **要件定義（機能／非機能）**

   * 可用性（AZ数）、レイテンシ、帯域、接続数、セキュリティ（分離レベル）
   * オンプレ連携（Direct Connect / Site-to-Site VPN / Private IP VPN 等）
   * SaaS接続やパートナー接続（PrivateLink 必要性）
   * Deliverable：ネットワーク要件定義書、接続要件一覧

3. **論理設計（アーキテクチャ設計）**

   * VPC 数・役割（管理系／業務系／ログ系 等）、サブネット（Public/Private/Isolated）
   * ルーティング設計（ルートテーブル、Transit Gateway / VPC Peering の選定）
   * セキュリティ領域（Security Group, NACL, Network Firewall, WAF）
   * Deliverable：論理アーキテクチャ図、CIDR割当表、セキュリティポリシーマトリクス

4. **詳細設計**

   * サブネットごとのルートテーブル、NAT/Gateway、エンドポイント（VPC Endpoint / PrivateLink）一覧
   * BGP/ASN、VPN/IKEバージョン、Direct Connect VIF 要件
   * モニタリング（VPC Flow Logs, CloudWatch, Network Access Analyzer, GuardDuty）
   * Deliverable：詳細設計書（テーブル化）、構築スクリプト（Terraform/CloudFormation）仕様

5. **実装（構築）**

   * IaC による VPC / サブネット / IGW / NAT / Route Table / SG / NACL / Endpoints のデプロイ
   * Transit Gateway や Direct Connect、VPN の設定・接続
   * セキュリティ機能（Network Firewall、WAF）や監査（Flow Logs）の有効化
   * Deliverable：Terraform コード、CloudFormation テンプレート、実行ログ、変更管理チケット

6. **テスト／検証**

   * 接続テスト（ping/traceroute、BGP session、帯域検証）
   * フェイルオーバー試験（AZ障害、VPN切断時の冗長性）
   * セキュリティテスト（ポートスキャン、Network Access Analyzer）
   * Deliverable：テスト計画・結果報告書、課題一覧

7. **リリース／切替（カットオーバー）**

   * DNS 切替（Route53 設計）、ルーティング切替手順、巻き戻し手順
   * Deliverable：カットオーバー手順書、ロール/連絡先一覧、ロールバック手順

8. **運用移行／ナレッジ移譲**

   * 運用 runbook（障害対応手順、監視アラート定義）
   * コスト管理（VPC 関連コストの見積りと最適化）
   * Deliverable：運用手順書、SOP（標準作業手順）、DR（復旧）計画

---

# 2) 主要成果物（納品物）一覧（テンプレート化しておくべきもの）

* **ネットワーク要件定義書**：SLA、帯域、暗号化要件、コンプライアンス要件
* **CIDR割当表 / IPプラン**：アカウント/リージョン/環境ごとのCIDR
* **論理アーキテクチャ図**（Visio / draw.io / Lucid 等）
* **物理／接続アーキテクチャ図**（Direct Connect 場所、回線、ピアリング）
* **セキュリティルールマトリクス**：SG / NACL / Firewall ルールの一覧と責任者
* **ルーティング設計書**：各サブネットのルートテーブル、Transit Gateway テーブル設計
* **IaC リポジトリ（Terraform / CloudFormation）**：モジュール、README、変数定義
* **構築手順書（Runbook）**：手順コマンド、パラメータ、事後確認リスト
* **テスト計画・試験結果レポート**
* **運用手順書（アラート、ログ確認、障害対応）**
* **セキュリティ監査レポート（VPC Flow Logs, Network Access Analyzer の結果）**

---

# 3) 具体的な「構築手順書」サンプル（実務で使える段階的手順）

> 以下は IaC（Terraform） を使う前提での順序。手順書は「目的→前提条件→コマンド／パラメータ→検証方法」を明確に。

## A. 事前準備

1. AWS アカウント／リージョンの確認、必要な IAM ロール作成（CloudFormation / Terraform 実行用）
2. 変数定義（CIDR、AZ、タグ、環境名、運用担当）を YAML/TFVars に記載
3. 構築メンバーとロール（実行者、レビューア、承認者）を決定

## B. VPC とサブネット作成（例）

1. Terraform: `vpc` モジュールを適用 — VPC 作成（例: 10.0.0.0/16）
2. Public subnet（各 AZ に 1 個以上）を作成（例: 10.0.0.0/24, 10.0.1.0/24）
3. Private subnet（アプリケーション）を作成（例: 10.0.10.0/24）
4. Isolated subnet（データベース）を作成（例: 10.0.20.0/24）
5. IGW（Internet Gateway）を作成して Public subnet にアタッチ
6. NAT Gateway は冗長性を考え AZ 毎に作る（コスト考慮）
7. Route Tables: Public -> IGW、Private -> NAT / TransitGateway へルート設定

**検証**：各サブネット内の EC2 から外部への疎通確認（curl、dig）、パブリックIP取得の確認

## C. セキュリティ設定

1. Security Groups のテンプレート化（Web, App, DB）— 最小権限で作成

   * Security Group はステートフルである点に注意（戻りトラフィックは自動許可）。公式参照。([AWS文档][1])
2. NACL の設定（サブネット境界でのデナイ/アロールール）— 管理用、外部向けでデフォルト拒否を検討
3. Network Firewall / WAF の配置（必要に応じて）
4. VPC Flow Logs を有効化して CloudWatch or S3 に保存（監査用）。([AWS文档][2])

**検証**：ポートスキャン（内部から）、許可/拒否のログ確認（Flow Logs）

## D. プライベート接続（オンプレ→AWS）

1. 要件に応じて選定：**Direct Connect（専用線）** or **Site-to-Site VPN（IPsec）**

   * VPN は IKEv2 推奨（公式のベストプラクティス）。([AWS文档][3])
2. Transit Gateway を使うか、Virtual Private Gateway + VPC Peering を使うか決定。大規模環境は Transit Gateway 推奨。([AWS文档][4])
3. BGP 設計（ASN、プレフィックス）、冗長構成（Customer Gateway の二重化）
4. Direct Connect の場合は virtual interface 設定と VLAN/帯域の確保

**検証**：BGP セッション確立、経路伝播確認、帯域測定

## E. サービス接続・最適化

1. VPC Endpoint（Interface / Gateway）を用いて S3、DynamoDB、ECR などへのプライベートアクセスを作成（インターネット経由を避ける）
2. PrivateLink を使って SaaS / パートナー接続を設計（必要に応じて）。Transit Gateway と PrivateLink の使い分けを明確に。([Amazon Web Services, Inc.][5])
3. Route53（プライベートホストゾーン）で内部 DNS 設計

**検証**：エンドポイント経由でのアクセス確認、DNS 解決の検証

## F. 監視・ログ・運用設定

1. VPC Flow Logs、CloudWatch アラーム、GuardDuty、Network Access Analyzer を有効にする（不正アクセス検知・調査用）。([AWS文档][2])
2. 定期的なネットワーク構成の自動評価（AWS Config ルール等）
3. コスト・タグ付けポリシーを実施（NAT、Transit Gateway、Data Transfer のコストに注意）

**検証**：アラート発生試験、ログの保持確認

---

# 4) 運用・テスト項目（チェックリスト例）

* [ ] CIDR がオーバーラップしていないか
* [ ] SG が最小ルールであるか（ここは重要）
* [ ] NAT Gateway の冗長性（AZ 毎に配置）とコスト検討
* [ ] Transit Gateway ルートテーブル整合性
* [ ] VPC Endpoints が不要なパブリック経路を開かないか
* [ ] Flow Logs の保存先と保持期間
* [ ] Direct Connect / VPN の BGP 冗長（2 セッション）実施
* [ ] IKE バージョンは IKEv2 推奨で設定（VPN）。([AWS文档][3])

---

# 5) 設計上の重要な考慮点（ベストプラクティス要約）

* **スケールを見越した CIDR 設計**：後での分割やピアリングを考慮する（/16, /20 等を用途に応じて）。（Well-Architected のネットワーキング指針参照）。([AWS文档][6])
* **Transit Gateway の活用**：多数の VPC／オンプレ接続がある場合、管理性・スケール面で有利。([AWS文档][4])
* **セキュリティの多層化**：Security Group（ステートフル）＋ NACL（サブネット境界）＋ Network Firewall（インスペクション）を組合せる。([AWS文档][1])
* **専用線と VPN の使い分け**：帯域・レイテンシ重視なら Direct Connect、柔軟性重視なら Site-to-Site VPN。Direct Connect と VPN の併用で冗長化も可能。([AWS文档][7])

---

# 6) 実践で使えるテンプレ（短い Terraform スニペット例）

（ここは手順書に貼れるテンプレの一例。実運用では変数化・モジュール化を推奨）

```hcl
# example: VPC + public subnet + IGW (抜粋)
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags = { Name = "${var.env}-vpc" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = { Name = "${var.env}-igw" }
}

resource "aws_subnet" "public_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_a
  availability_zone = var.az_a
  map_public_ip_on_launch = true
  tags = { Name = "${var.env}-public-a" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}
resource "aws_route_table_association" "rta_public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}
```

---

# 7) よくある失敗パターン（実務ノウハウ）

* CIDR 設計不足 → 後に VPC ピアリングや Direct Connect で衝突する。
* NAT Gateway を AZ 1 だけに置き、AZ 間データ転送でコスト増。
* Security Group を雑に開けてしまう（プリンシプルは “deny by default” を維持）([AWS文档][8])
* 監査ログ（VPC Flow Logs）を保管しておらず、障害解析に手間がかかる。([AWS文档][2])

---

# 8) 参考（公式ドキュメント・ホワイトペーパー）

主要なベストプラクティス・機能説明（参照）：

* Transit Gateway の説明・設計ベストプラクティス。([AWS文档][4])
* AWS Well-Architected — Networking のガイドライン。([AWS文档][6])
* Security Groups / NACL の仕様と設計注意点。([AWS文档][1])
* VPC セキュリティベストプラクティス（Flow Logs, Network Firewall 等）。([AWS文档][2])
* Site-to-Site VPN のベストプラクティス（IKEv2 推奨）。([AWS文档][3])

---
