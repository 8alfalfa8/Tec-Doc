
---

<!-- TOC_START -->
<a id="index"></a>📖 目次

- [🎯 目的](#目的)
- [🏗️ 基本構成図](#基本構成図)
- [📁 リポジトリ構成（例）](#リポジトリ構成例)
- [🧪 GitHub Actions でのCI/CD構成例](#github-actions-でのcicd構成例)
- [🔐 セキュリティとガバナンスの考慮事項](#セキュリティとガバナンスの考慮事項)
- [✅ 本番運用でのベストプラクティス](#本番運用でのベストプラクティス)
- [📦 補足：CodePipeline/AWS環境で動かす場合](#補足codepipelineaws環境で動かす場合)
- [📝 推奨IaCツール(無料)](#推奨iacツール無料)
<!-- TOC_END -->

# 🚀 TerraformのCI/CD運用設計ガイド（AWS対応）

---

## 🎯 目的
[🔙 目次に戻る](#index)


TerraformをCI/CDパイプラインに組み込み、**インフラコードの品質・一貫性・自動反映**を実現すること。

---

[🔙 目次に戻る](#index)


## 🏗️ 基本構成図
[🔙 目次に戻る](#index)


```
GitHub（main/devブランチ）
   ↓ Pull Request
GitHub Actions / CIツール（CodePipeline等）
   ↓
Terraform Plan（dry-run）
   ↓（レビュー＆承認）
Terraform Apply（本番適用）
   ↓
AWS環境へ反映（S3, EC2, etc.）
```

---

[🔙 目次に戻る](#index)


## 📁 リポジトリ構成（例）
[🔙 目次に戻る](#index)


```
infra/
├── envs/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── backend.tf
│   │   └── variables.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── backend.tf
│   │   └── variables.tf
│   └── prod/
│       ├── main.tf
│       ├── backend.tf
│       └── variables.tf
├── modules/
│   ├── vpc/
│   ├── ec2/
│   └── rds/
├── .github/workflows/
│   └── terraform.yml
├── README.md
└── terraform.tfvars（環境別に管理）
```

---

[🔙 目次に戻る](#index)


## 🧪 GitHub Actions でのCI/CD構成例
[🔙 目次に戻る](#index)


```yaml
# .github/workflows/terraform.yml
name: Terraform CI/CD

on:
  pull_request:
    branches:
      - main
      - develop
  push:
    branches:
      - main
      - develop

env:
  AWS_REGION: ap-northeast-1

jobs:
  terraform:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v3
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.4

      - name: Terraform Init
        run: terraform -chdir=infra/envs/dev init

      - name: Terraform Validate
        run: terraform -chdir=infra/envs/dev validate

      - name: Terraform Plan
        run: terraform -chdir=infra/envs/dev plan -input=false

      - name: Terraform Apply (mainブランチ限定)
        if: github.ref == 'refs/heads/main'
        run: terraform -chdir=infra/envs/dev apply -auto-approve -input=false
```

---

[🔙 目次に戻る](#index)


## 🔐 セキュリティとガバナンスの考慮事項
[🔙 目次に戻る](#index)


| 項目      | 対策案                                    |
| ------- | -------------------------------------- |
| AWS認証情報 | GitHub Secretsなどで暗号化管理                 |
| ステート管理  | S3＋DynamoDB（リモートステート）でロック管理            |
| ブランチ保護  | `main` ブランチへの直接push禁止＋Pull Request承認必須 |
| 監査性     | `terraform plan` の出力をログ保存し、レビュー確認可能にする |

---

[🔙 目次に戻る](#index)


## ✅ 本番運用でのベストプラクティス
[🔙 目次に戻る](#index)


| 項目          | 内容                                         |
| ----------- | ------------------------------------------ |
| ステージング環境の分離 | `dev`, `staging`, `prod` フォルダを分離して環境ごとに明確化 |
| 自動テスト（Lint） | `tflint`, `tfsec` でセキュリティや構文チェック           |
| コードレビュー必須   | `Terraform Plan` の出力をレビュー後に `Apply`        |
| Applyの条件分岐  | ブランチによって `plan` のみ or `apply` を使い分ける       |

---

[🔙 目次に戻る](#index)


## 📦 補足：CodePipeline/AWS環境で動かす場合
[🔙 目次に戻る](#index)


GitHub Actions以外に、以下のような構成も可：

```
CodeCommit / GitHub
   ↓
AWS CodeBuild
   ↓
Terraform Plan / Apply
   ↓
S3（tfstate）＋DynamoDB（lock）
   ↓
本番AWSリソース
```

---

[🔙 目次に戻る](#index)

## 📝 推奨IaCツール(無料)
[🔙 目次に戻る](#index)


* Terraform Code Generator from Excel(for AWS)
  - Excelで定義されたAWSインフラ構成情報(パラメータシート)から、Terraformコードを自動生成するためのツールです。
  - https://github.com/8alfalfa8/aws-terraform-code-generator
---

[🔙 目次に戻る](#index)


