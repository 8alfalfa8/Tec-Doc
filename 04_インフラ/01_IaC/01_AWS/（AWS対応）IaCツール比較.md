
---

<!-- TOC_START -->
<a id="index"></a>📖 目次

- [🧩 AWS対応IaCツール比較表](#aws対応iacツール比較表)
- [📝 各ツールの特徴・強み](#各ツールの特徴強み)
  - [✅ Terraform](#terraform)
  - [✅ AWS CloudFormation](#aws-cloudformation)
  - [✅ AWS CDK（Cloud Development Kit）](#aws-cdkcloud-development-kit)
- [🎯 選定の目安（どれを使うべきか）](#選定の目安どれを使うべきか)
- [🧪 補足：共存も可能](#補足共存も可能)
- [📝 推奨IaCツール(無料)](#推奨iacツール無料)
<!-- TOC_END -->

# 🚀 AWS対応IaCツール

---

## 🧩 AWS対応IaCツール比較表
[🔙 目次に戻る](#index)


| 項目           | Terraform                         | AWS CloudFormation    | AWS CDK                           |
| ------------ | --------------------------------- | --------------------- | --------------------------------- |
| 開発元          | HashiCorp                         | AWS                   | AWS                               |
| 対応クラウド       | ✅ マルチクラウド（AWS / Azure / GCP etc.） | ❌ AWSのみ               | ❌ AWSのみ                           |
| 記述言語         | 独自言語（HCL）                         | JSON / YAML           | TypeScript / Python / Java / C#など |
| 学習コスト        | 中程度（HCL習得が必要）                     | 低〜中（YAML/JSONに慣れていれば） | 高（言語とCDKライブラリ理解が必要）               |
| 再利用性（モジュール化） | 高（Moduleが豊富）                      | 中（Nested Stack）       | 非常に高（OOPで抽象化可能）                   |
| ドキュメント・事例    | 非常に豊富（Terraform Registryなど）       | 豊富（AWS公式）             | 増加中（AWS開発者向け）                     |
| 拡張性          | 高（Providerを追加可能）                  | 低（AWS内に限る）            | 高（プログラミング言語で制御可能）                 |
| CI/CDとの統合    | 容易（GitHub Actions, CodePipeline等） | 容易（CodePipelineと連携）   | 容易（ビルド後にCloudFormationでデプロイ）      |
| ステート管理       | 必要（S3+DynamoDBが一般的）               | 自動管理（AWSが管理）          | CloudFormationに依存                 |
| エラーメッセージ     | わかりやすい                            | わかりにくいことも多い           | 比較的わかりやすい（言語ベース）                  |
| テスト容易性       | △（サードパーティ要）                       | △                     | ◯（ユニットテスト可）                       |

---

## 📝 各ツールの特徴・強み
[🔙 目次に戻る](#index)


### ✅ Terraform
[🔙 目次に戻る](#index)


* **クラウド横断**対応（AWS/Azure/GCPなどを1つのコードで管理）
* 大規模環境やマルチクラウド戦略に最適
* コミュニティが非常に活発（moduleやproviderが豊富）
* **ステートファイル管理が重要**（S3+lockがベストプラクティス）

### ✅ AWS CloudFormation
[🔙 目次に戻る](#index)


* **AWS公式のツール**で、IAMやコンソール連携が抜群
* **変更セット（Change Set）** によるデプロイプレビュー機能が便利
* **YAML形式**が読みやすく、AWSサービス追加対応も早い
* スタックネストやテンプレート分割も可能だがやや複雑

### ✅ AWS CDK（Cloud Development Kit）
[🔙 目次に戻る](#index)


* **プログラミング言語でインフラを記述可能（OOP/抽象化）**
* 条件分岐・ループ・共通化などが柔軟に行える
* **開発者フレンドリー**：アプリとインフラを同一言語で管理可能
* デプロイには最終的にCloudFormationが生成される

---

## 🎯 選定の目安（どれを使うべきか）
[🔙 目次に戻る](#index)


| ユースケース                                | 推奨ツール                 |
| ------------------------------------- | --------------------- |
| AWS以外も扱う、クラウド横断・標準化                   | Terraform             |
| AWS環境のみ、AWSベストプラクティスに準拠               | CloudFormation        |
| AWSかつ開発者がコードで記述したい（TypeScript/Python） | AWS CDK               |
| 小規模プロジェクトで素早く構築                       | CloudFormation or CDK |
| チームで再利用性・テスト性を重視                      | Terraform or CDK      |

---

## 🧪 補足：共存も可能
[🔙 目次に戻る](#index)


* **Terraformでベースのインフラ（VPC, S3）を構築**
* **CloudFormationまたはCDKでアプリ系リソース（Lambda, API Gatewayなど）を管理**

など、使い分け・組み合わせもできます。

---
## 📝 推奨IaCツール(無料)
[🔙 目次に戻る](#index)


* Terraform Code Generator from Excel(for AWS)
  - Excelで定義されたAWSインフラ構成情報(パラメータシート)から、Terraformコードを自動生成するためのツールです。
  - https://github.com/8alfalfa8/aws-terraform-code-generator
---
