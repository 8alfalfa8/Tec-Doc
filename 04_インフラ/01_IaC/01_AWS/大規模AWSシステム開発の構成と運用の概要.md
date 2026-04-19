## ◆ 大規模AWSシステム開発の構成と運用の概要

### 推奨アカウント構成

大規模案件であれば、**「ソースコード管理アカウント」「CIアカウント」「CD配布アカウント」も分離**した方が運用しやすいです。

| 区分     | AWSアカウント      | 主用途                                    |
| ------ | ------------- | -------------------------------------- |
| scm    | Source管理アカウント | CodeCommit、CodeArtifact                |
| cicd   | CI/CD実行アカウント  | CodePipeline、CodeBuild、Artifact S3、KMS |
| shared | 共通基盤アカウント     | ECR、監視、ログ、共通Secrets                    |
| dev    | 開発アカウント       | 開発検証                                   |
| stg    | ステージングアカウント   | 結合試験                                   |
| reh    | リハーサルアカウント    | 本番相当検証                                 |
| prod   | 本番アカウント       | 本番運用                                   |

この形にすると、たとえばCodeCommit障害や権限事故が起きても、本番アカウントには直接影響しません。

また、本番アカウントにはCodeBuildやCodePipelineを置かず、**本番は「デプロイ先」でしかない**状態にするのが重要です。

複数AWSアカウント構成では、CI/CDアカウントを中央集約し、各環境アカウントへクロスアカウントデプロイする構成が一般的です。 ([AWS 文档][1])

---

### 全体構成イメージ

```text
開発者PC
   ↓
scmアカウント
  └─ CodeCommit
   ↓
cicdアカウント
  ├─ CodePipeline
  ├─ CodeBuild
  ├─ Artifact S3
  ├─ KMS
  └─ CodeDeploy
   ↓ AssumeRole
dev / stg / reh / prod アカウント
  ├─ CloudFormation
  ├─ CDK Deploy Role
  ├─ CodeDeploy Role
  └─ 実環境リソース
```

---

### さらに分けるべきPipeline

大規模案件では、1本のPipelineに全部載せると重くなります。

そのため、Pipeline自体も役割ごとに分けます。

| Pipeline                | 対象                             |
| ----------------------- | ------------------------------ |
| infra-base-pipeline     | VPC、IAM、KMS、Route53、CloudTrail |
| shared-service-pipeline | ECR、監視、共通ログ、共通Secrets          |
| app-pipeline            | ECS、Lambda、API Gateway、Batch   |
| db-pipeline             | RDS、DynamoDB、Migration         |
| hotfix-pipeline         | 緊急修正専用                         |
| feature-pipeline        | ブランチごとの一時環境                    |

特に以下はアプリ配布と分離します。

* VPC
* Transit Gateway
* IAM
* KMS
* Route53
* Direct Connect
* CloudTrail
* GuardDuty
* Security Hub
* 共通ECR
* RDS

これらは変更頻度が低く、誤更新時の影響が大きいため、別Pipeline化が安全です。

AWS CDKでも、基盤・アプリ・監視などを別Stackや別Pipelineへ分離することが推奨されています。 ([AWS 文档][2])

---

### 実運用でのリポジトリ分離

大規模案件では、Gitリポジトリも分離することが多いです。

```text
infra-network-repo
infra-security-repo
infra-monitoring-repo
shared-service-repo
app-backend-repo
app-frontend-repo
db-migration-repo
pipeline-definition-repo
```

特に `pipeline-definition-repo` を独立させると、CI/CD構成変更をアプリ開発と切り離せます。

たとえば、CodePipelineの追加承認やBuildspec変更だけを、アプリ本体と別レビューで進められます。

---

### 推奨ブランチ戦略

```text
main
develop
release/*
feature/*
hotfix/*
```

配布先との対応は以下です。

| ブランチ      | 配布先             |
| --------- | --------------- |
| feature/* | feature環境       |
| develop   | dev             |
| release/* | stg / reh       |
| main      | prod            |
| hotfix/*  | hotfix環境 → prod |

featureブランチごとに一時環境を作る運用も、大規模案件ではかなり有効です。

たとえば `feature/add-payment-api` ブランチ作成時に、自動で `dev-payment-api-001` のような一時環境を作成します。

ブランチ単位の一時環境やbranch-based pipelineは、CDK Pipelinesでもよく使われる構成です。 ([Amazon Web Services, Inc.][3])

---

### CICDアカウント側のPipeline構成

```text
Source
↓
Validate
↓
Package
↓
Deploy-dev
↓
SDK-test-dev
↓
Approval-stg
↓
Deploy-stg
↓
SDK-test-stg
↓
Approval-reh
↓
Deploy-reh
↓
Performance-test-reh
↓
Approval-prod
↓
Deploy-prod
↓
Smoke-test-prod
↓
Post-monitoring
```

---

### Validateステージでやること

CIアカウントのCodeBuildで以下を実施します。

```bash
npm ci
npm run lint
npm run test
npm run build
npx cdk synth
npx cdk diff
npx cdk-nag
npx cfn-lint
npm audit --audit-level=high
checkov -d .
```

ここで落ちたものは、どの環境にも配布しません。

---

### CDK配布ロールの考え方

各環境アカウントには、CI/CDアカウントからAssumeRoleされるロールを用意します。

例:

```text
CdkDeployRole-Dev
CdkDeployRole-Stg
CdkDeployRole-Reh
CdkDeployRole-Prod
```

prodだけは別格です。

prod用ロールには以下を禁止します。

```text
iam:DeleteRole
kms:ScheduleKeyDeletion
organizations:*
cloudtrail:StopLogging
guardduty:Delete*
route53domains:*
```

さらにprodでは以下も推奨です。

* MFA必須
* 手動承認必須
* 承認者2名以上
* Change Request番号必須
* CloudTrail常時監査
* SCPで危険操作禁止

---

### DB変更は別Pipeline

DB系はアプリ配布と分離します。

```text
db-schema-pipeline
  ↓
DDLレビュー
  ↓
dev適用
  ↓
stg適用
  ↓
reh適用
  ↓
prod適用
```

特にRDSは、アプリ配布と同時にschema変更すると事故率が上がります。

実運用では以下を分離します。

* DDL
* DML
* Migration
* Seedデータ
* マスタデータ更新

---

### 現場でよくある「権限分離」

大規模案件では、以下のような分離が多いです。

| 役割       | できること           |
| -------- | --------------- |
| 開発者      | feature/dev配布まで |
| TL/PL    | stg配布承認         |
| 運用責任者    | reh承認           |
| CAB      | prod承認          |
| SRE      | rollback実施      |
| セキュリティ担当 | IAM/KMS変更承認     |

---

### 最後の推奨構成

大規模案件なら、最終的には以下くらいまで分離すると安定します。

```text
AWS Organizations
├─ scm account
├─ cicd account
├─ security account
├─ log archive account
├─ shared service account
├─ network account
├─ dev account
├─ stg account
├─ reh account
└─ prod account
```

特に、ログ保管とセキュリティは別アカウント化が強いです。

* CloudTrail
* Config
* Security Hub
* GuardDuty
* IAM Access Analyzer
* VPC Flow Logs

これらを専用アカウントへ集約すると、仮にprod侵害時でも監査証跡を守れます。

AWSでも、Landing Zone(AWS Control Tower) / AWS Organizations / CI専用アカウント / 環境別アカウント分離が推奨されています。 ([AWS 文档][2])

[1]: https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/set-up-a-ci-cd-pipeline-by-using-aws-codepipeline-and-aws-cdk.html?utm_source=chatgpt.com "Set up a CI/CD pipeline by using AWS CodePipeline and AWS CDK - AWS Prescriptive Guidance"
[2]: https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html?utm_source=chatgpt.com "Best practices for developing and deploying cloud infrastructure with the AWS CDK - AWS Cloud Development Kit (AWS CDK) v2"
[3]: https://aws.amazon.com/blogs/devops/multi-branch-pipeline-management-and-infrastructure-deployment-using-aws-cdk-pipelines/?utm_source=chatgpt.com "Multi-branch pipeline management and infrastructure deployment using AWS CDK Pipelines | AWS DevOps & Developer Productivity Blog"

---
