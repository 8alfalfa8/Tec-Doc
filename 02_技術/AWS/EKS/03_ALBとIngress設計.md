# ◆ ALB Ingress設計

以下では、**AWS EKS × ALB Ingress**（**AWS Load Balancer Controller**）について、
**設計思想 → 詳細設計項目 → 設定値 → 実装例 → 運用・注意点**まで、
**設計書レベルでそのまま使える粒度**で詳しく説明します。

---

## 1. ALB Ingress の位置づけ

### 1.1 役割

ALB Ingress は以下を担います。

| 項目       | 内容          |
| -------- | ----------- |
| L7ルーティング | HTTP/HTTPS  |
| SSL終端    | ACM         |
| パス分岐     | /app /api   |
| 可用性      | Multi-AZ    |
| スケーリング   | AWS Managed |

```
Internet
 ↓
ALB（AWS Managed）
 ↓
Ingress（K8s）
 ↓
Service（ClusterIP）
 ↓
Pod（Tomcat）
```

---

## 2. ALB Ingress 全体設計方針

| 項目      | 設計方針                         |
| ------- | ---------------------------- |
| ALB種別   | Internet-facing              |
| SSL     | ALB終端                        |
| Ingress | AWS Load Balancer Controller |
| Pod通信   | HTTP                         |
| 冗長      | ALB + Pod Replica            |
| 変更影響    | Ingress更新のみ                  |

---

## 3. ALB Ingress 詳細設計項目

---

### 3.1 ALB設計

#### ALB基本設計

| 項目     | 設定                        |
| ------ | ------------------------- |
| ALBタイプ | Application Load Balancer |
| スキーム   | internet-facing           |
| AZ     | 2AZ以上                     |
| Subnet | Public Subnet             |
| IP     | IPv4                      |

#### Subnetタグ（必須）

```text
kubernetes.io/role/elb=1
kubernetes.io/cluster/prod-eks=shared
```

❗ **タグ漏れはALB作成失敗の最大要因**

---

### 3.2 Listener設計

#### Listener構成

| ポート | プロトコル | 用途          |
| --- | ----- | ----------- |
| 80  | HTTP  | HTTPSリダイレクト |
| 443 | HTTPS | 本番通信        |

#### HTTP → HTTPSリダイレクト

* ALB Listener Ruleで実施
* Ingress Annotationで制御

---

### 3.3 SSL / 証明書設計

#### 証明書

| 項目   | 内容          |
| ---- | ----------- |
| 管理   | ACM         |
| ドメイン | example.com |
| 更新   | 自動          |

#### Annotation指定

```yaml
alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:...
```

---

### 3.4 セキュリティグループ設計

#### ALB用SG

| In/Out | 内容             |
| ------ | -------------- |
| In     | 443（0.0.0.0/0） |
| Out    | Node SG        |

#### Node用SG

| In | ALB SG |
| Out | 全許可 |

---

### 3.5 Ingress設計（Kubernetes）

#### 基本方針

* **1サービス = 1 Ingress（推奨）**
* Pathベース分岐可
* Hostベース分岐可

---

### 3.6 Ingress Annotation設計（重要）

#### 基本Annotation一覧

| Annotation                                 | 内容              |
| ------------------------------------------ | --------------- |
| kubernetes.io/ingress.class                | alb             |
| alb.ingress.kubernetes.io/scheme           | internet-facing |
| alb.ingress.kubernetes.io/target-type      | ip              |
| alb.ingress.kubernetes.io/backend-protocol | HTTP            |

#### target-type = ip の理由

* Pod直接ルーティング
* NodePort不要
* Fargate対応可

---

### 3.7 ヘルスチェック設計

#### ALBヘルスチェック

| 項目        | 値            |
| --------- | ------------ |
| Path      | /health      |
| Port      | traffic-port |
| Interval  | 30s          |
| Timeout   | 5s           |
| Healthy   | 2            |
| Unhealthy | 2            |

#### Tomcat側

* `/health` Servlet or Controller
* **200固定返却**

---

### 3.8 タイムアウト設計

#### ALB Idle Timeout

```yaml
alb.ingress.kubernetes.io/load-balancer-attributes: idle_timeout.timeout_seconds=60
```

| ケース   | 推奨      |
| ----- | ------- |
| 通常Web | 60      |
| 大容量DL | 120〜300 |

---

### 3.9 WAF設計（任意）

#### WAF連携

```yaml
alb.ingress.kubernetes.io/wafv2-acl-arn: arn:aws:wafv2:...
```

用途：

* SQLi / XSS
* Bot制御
* IP制限

---

### 3.10 アクセスログ設計

```yaml
alb.ingress.kubernetes.io/load-balancer-attributes: |
  access_logs.s3.enabled=true,
  access_logs.s3.bucket=alb-log-bucket
```

---

## 4. Ingress定義サンプル（実戦）

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tomcat-ingress
  namespace: prod
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:...
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP":80},{"HTTPS":443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/healthcheck-path: /health
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: tomcat-service
            port:
              number: 8080
```

---

## 5. ALB × Service設計

### Service種別

| 種別        | 理由         |
| --------- | ---------- |
| ClusterIP | ALBから直接Pod |

```yaml
kind: Service
spec:
  type: ClusterIP
```

---

## 6. 可用性・スケーリング設計

| レイヤ | 対応            |
| --- | ------------- |
| ALB | AWS Managed   |
| Pod | Replica + HPA |
| AZ  | Multi-AZ      |

---

## 7. 運用設計・監視

## 7.1 監視項目

| 対象     | メトリクス              |
| ------ | ------------------ |
| ALB    | 4xx/5xx            |
| Target | HealthyHost        |
| レイテンシ  | TargetResponseTime |

---

### 7.2 障害切り分けフロー

```
ALB 5xx？
 ├ Yes → Podログ
 └ No  → Ingress/Service
```

---

## 8. よくあるトラブルと対策

| 事象        | 原因       | 対策       |
| --------- | -------- | -------- |
| ALB作成されない | Subnetタグ | タグ確認     |
| 502       | Health失敗 | Path修正   |
| 404       | Path     | Prefix確認 |
| 接続不可      | SG       | In/Out確認 |

---

## 9. 設計成果物

* ALB Ingress設計書
* セキュリティ設計書
* Ingress定義YAML
* 運用Runbook（Ingress編）

---
