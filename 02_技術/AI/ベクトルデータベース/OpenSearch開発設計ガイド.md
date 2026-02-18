# ◆ OpenSearch開発設計ガイド

## 1. 設計フロー（開発プロセス）

### 1.1 全体設計フロー
```
要件定義 → データモデリング → インデックス設計 → マッピング定義 → 
シャード設計 → クラスタ設計 → 実装 → テスト → 本番導入
```

### 1.2 詳細ステップ

#### **ステップ1: 要件定義**
- 検索要件の明確化（全文検索、フィルタリング、集計など）
- パフォーマンス要件（レスポンスタイム、スループット）
- データ量の予測（日増分、総容量）
- 可用性・耐久性要件

#### **ステップ2: データモデリング**
```json
// 例: eコマース商品データ
{
  "product_id": "unique_identifier",
  "name": "商品名",
  "description": "詳細説明",
  "category": ["カテゴリ1", "カテゴリ2"],
  "price": 10000,
  "attributes": {
    "color": "red",
    "size": "L"
  },
  "created_at": "2024-01-01T00:00:00Z",
  "tags": ["人気", "新作"]
}
```

## 2. 設計思想（Design Philosophy）

### 2.1 OpenSearch特有の考え方

#### **セキュリティファースト**
```yaml
# デフォルトでセキュリティ有効化
plugins.security.ssl.transport.enabled: true
plugins.security.ssl.http.enabled: true
plugins.security.authcz.admin_dn:
  - CN=admin,OU=admin,O=Example Com
```

#### **スケーラビリティ重視**
- シャード単位での水平スケーリング
- ホット・ウォーム・コールドアーキテクチャ対応

#### **コスト最適化**
- データ階層化（Hot-Warm-Cold-Frozen）
- ライフサイクル管理の活用

## 3. データ設計方法

### 3.1 インデックス設計パターン

#### **タイムシリーズデータの場合**
```json
// インデックス命名: logs-YYYY.MM.DD
PUT logs-2024.01.01
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "index.lifecycle.name": "logs_policy"
  }
}
```

#### **マルチテナント設計**
```json
// テナントごとのインデックス分離
PUT tenant-{tenant_id}-products
{
  "settings": {
    "number_of_shards": 2,
    "routing.allocation.require.tenant": "{tenant_id}"
  }
}
```

### 3.2 マッピング設計

#### **動的マッピングの制御**
```json
PUT products
{
  "mappings": {
    "dynamic": "strict",  // 未定義フィールドを拒否
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "kuromoji",  // 日本語対応
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "price": {
        "type": "integer",
        "coerce": false  // 型変換を厳格に
      },
      "location": {
        "type": "geo_point"
      },
      "description": {
        "type": "text",
        "analyzer": "kuromoji_analyzer"
      }
    }
  }
}
```

### 3.3 テンプレート活用
```json
PUT _index_template/logs_template
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "refresh_interval": "30s"
    },
    "mappings": {
      "_source": {
        "enabled": true
      },
      "properties": {
        "@timestamp": {
          "type": "date",
          "format": "strict_date_optional_time||epoch_millis"
        }
      }
    },
    "aliases": {
      "all_logs": {}
    }
  },
  "priority": 200
}
```

## 4. シャード設計

### 4.1 シャード数決定方法
```python
# シャードサイズの最適化計算例
def calculate_shards(total_data_gb, daily_growth_gb, retention_days):
    """
    推奨: 1シャードあたり10-50GBを維持
    """
    max_shard_size_gb = 50
    total_shards = total_data_gb / max_shard_size_gb
    
    # 将来的なデータ増加を考慮
    future_data = total_data_gb + (daily_growth_gb * retention_days)
    return max(1, int(future_data / max_shard_size_gb))
```

### 4.2 シャード割り当て戦略
```json
PUT _cluster/settings
{
  "persistent": {
    "cluster.routing.allocation.awareness.attributes": "zone",
    "cluster.routing.allocation.awareness.force.zone.values": ["zone1", "zone2"]
  }
}
```

## 5. クラスタ設計

### 5.1 ノードタイプ別構成
```yaml
# docker-compose例（開発環境）
version: '3'
services:
  opensearch-node1:
    image: opensearchproject/opensearch:latest
    environment:
      - node.name=opensearch-node1
      - cluster.name=opensearch-cluster
      - discovery.seed_hosts=opensearch-node1,opensearch-node2
      - cluster.initial_master_nodes=opensearch-node1,opensearch-node2
      - bootstrap.memory_lock=true
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
      - plugins.security.disabled=false
  
  opensearch-dashboards:
    image: opensearchproject/opensearch-dashboards:latest
    ports:
      - "5601:5601"
```

### 5.2 プロダクション構成例
```
クラスタ構成例:
- マスターノード: 3台（専用、奇数台）
- データノード（ホット）: 3台以上
- データノード（ウォーム）: 2台以上
- コーディネーションノード: 2台以上（任意）
- インデックス専用ノード: 必要に応じて
```

## 6. 開発時の注意事項

### 6.1 パフォーマンス最適化

#### **インデックス設定**
```json
PUT products
{
  "settings": {
    "index": {
      "refresh_interval": "30s",  // バルクインデックス時のパフォーマンス向上
      "number_of_replicas": 1,
      "codec": "default",
      "mapping": {
        "total_fields": {
          "limit": 1000  // フィールド数の制限
        }
      }
    }
  }
}
```

#### **検索クエリの最適化**
```json
GET products/_search
{
  "query": {
    "bool": {
      "filter": [  // キャッシュ可能な条件はfilterで
        {
          "term": {
            "category": "electronics"
          }
        }
      ],
      "must": [
        {
          "match": {
            "description": "高性能"
          }
        }
      ]
    }
  },
  "aggs": {
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "to": 10000 },
          { "from": 10000, "to": 50000 },
          { "from": 50000 }
        ]
      }
    }
  },
  "size": 20,  // 必要最小限のサイズ指定
  "_source": ["name", "price"]  // 必要なフィールドのみ取得
}
```

### 6.2 セキュリティ設定
```yaml
# config/opensearch-security/config.yml
_meta:
  type: "config"
  config_version: 2

config:
  dynamic:
    http:
      anonymous_auth_enabled: false
    authc:
      basic_internal_auth_domain:
        http_enabled: true
        transport_enabled: true
        order: 0
        http_authenticator:
          type: basic
          challenge: false
        authentication_backend:
          type: intern
```

### 6.3 バックアップ・リカバリ設計
```json
PUT _snapshot/my_backup_repository
{
  "type": "s3",
  "settings": {
    "bucket": "my-opensearch-backups",
    "region": "ap-northeast-1"
  }
}

PUT _snapshot/my_backup_repository/snapshot_1
{
  "indices": "logs-*",
  "ignore_unavailable": true,
  "include_global_state": false
}
```

## 7. 監視と運用

### 7.1 必須監視項目
```json
GET _cluster/health
GET _nodes/stats
GET _cat/indices?v
GET _cat/shards?v
```

### 7.2 アラート設定例
```json
PUT _plugins/_alerting/monitors
{
  "name": "High CPU Usage Alert",
  "enabled": true,
  "schedule": {
    "period": {
      "interval": 5,
      "unit": "MINUTES"
    }
  },
  "inputs": [
    {
      "search": {
        "indices": [".opensearch-observability"],
        "query": {
          "size": 0,
          "aggregations": {
            "avg_cpu": {
              "avg": {
                "field": "system.cpu.total.pct"
              }
            }
          }
        }
      }
    }
  ],
  "triggers": [
    {
      "name": "High-CPU-Trigger",
      "severity": "1",
      "condition": {
        "script": {
          "source": "ctx.results[0].aggregations.avg_cpu.value > 0.8",
          "lang": "painless"
        }
      }
    }
  ]
}
```

## 8. ベストプラクティス

### 8.1 データモデリング
- ネストされたオブジェクトよりフラットな構造を優先
- 配列フィールドは最小限に
- マッピングテンプレートで一貫性を確保

### 8.2 パフォーマンス
- バルクAPIを活用（1リクエスト5-15MBが目安）
- インデックス作成時はレプリカ数を0に設定
- 適切なアナライザー選択（日本語ならKuromoji）

### 8.3 運用
- インデックスライフサイクル管理（ISLM）の活用
- 定期的なインデックス最適化（_forcemerge）
- 監査ログの有効化

## 9. トラブルシューティングチェックリスト

1. **検索が遅い場合**
   - シャード数が適切か確認
   - クエリキャッシュを活用しているか
   - フィールドデータサイズを監視

2. **インデックスが失敗する場合**
   - マッピング制限（field_limit）を確認
   - ディスク容量を確認
   - セキュリティ権限を確認

3. **クラスタ不安定の場合**
   - マスターノードの選定を確認
   - ネットワーク遅延を確認
   - JVMヒープサイズを最適化

この設計フローに従うことで、OpenSearchの特徴を活かした効率的でスケーラブルなシステムを構築できます。特にセキュリティ設定やライフサイクル管理は、初期設計段階から組み込むことが重要です。

---

## 🌱 AI開発構築参照例(ソースコードを含む)

[マルチLLM対応AIチャットアプリ](https://github.com/8alfalfa8/freeAiChat)

---
