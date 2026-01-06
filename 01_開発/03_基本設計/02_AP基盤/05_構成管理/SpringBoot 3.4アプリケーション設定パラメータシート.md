# Spring Boot 3.4 アプリケーション設定パラメータシート

以下は **Spring Boot 3.4** 向けの **設定パラメータシート（設計用テンプレート）** です。
そのままExcelに貼り付けて利用できるよう、表形式で整理しています。
環境変数・プロファイル別・外部サービス設定まで網羅しています。

---

## Spring Boot 3.4 アプリケーション設定パラメータシート（設計テンプレート）

| No     | カテゴリ              | 設定項目         | 設定キー                                                    | 値（例）                                                                                             | 環境（local/stg/prod） | 備考           |
| ------ | ----------------- | ------------------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------ | ------------ |
| **1**  | **アプリケーション**      | アプリ名         | `spring.application.name`                               | myapp-web                                                                                        | 全環境                | サービス識別名      |
| **2**  |                   | ポート番号        | `server.port`                                           | 8080                                                                                             | 全環境                | 起動ポート        |
| **3**  |                   | コンテキストパス     | `server.servlet.context-path`                           | /api                                                                                             | 全環境                | APIルート指定     |
| **4**  |                   | エンコーディング     | `server.servlet.encoding.charset`                       | UTF-8                                                                                            | 全環境                | 文字コード設定      |
| **5**  | **データソース**        | JDBC URL     | `spring.datasource.url`                                 | jdbc:postgresql://db:5432/appdb                                                                  | 環境別                | DB接続情報       |
| **6**  |                   | DBユーザ        | `spring.datasource.username`                            | appuser                                                                                          | 全環境                | -            |
| **7**  |                   | DBパスワード      | `spring.datasource.password`                            | `${DB_PASSWORD}`                                                                                 | 全環境                | 環境変数管理       |
| **8**  |                   | ドライバクラス      | `spring.datasource.driver-class-name`                   | org.postgresql.Driver                                                                            | 全環境                | -            |
| **9**  |                   | コネクションプールサイズ | `spring.datasource.hikari.maximum-pool-size`            | 10                                                                                               | 環境別                | HikariCP設定   |
| **10** | **JPA/Hibernate** | DDL自動生成      | `spring.jpa.hibernate.ddl-auto`                         | none / update                                                                                    | localのみupdate      | スキーマ生成制御     |
| **11** |                   | SQLログ出力      | `spring.jpa.show-sql`                                   | true                                                                                             | localのみ            | 開発デバッグ用      |
| **12** |                   | フォーマット出力     | `spring.jpa.properties.hibernate.format_sql`            | true                                                                                             | local              | -            |
| **13** |                   | 名前戦略         | `spring.jpa.hibernate.naming.physical-strategy`         | org.hibernate.boot.model.naming.PhysicalNamingStrategyStandardImpl                               | 全環境                | -            |
| **14** | **ログ**            | ルートログレベル     | `logging.level.root`                                    | INFO                                                                                             | 全環境                | -            |
| **15** |                   | パッケージ別レベル    | `logging.level.com.example`                             | DEBUG                                                                                            | local              | 自作コード用       |
| **16** |                   | ログファイル出力     | `logging.file.name`                                     | /var/log/app/app.log                                                                             | stg/prod           | -            |
| **17** |                   | ログローテート      | `logging.logback.rollingpolicy.max-history`             | 30                                                                                               | prod               | 保存日数         |
| **18** | **セキュリティ**        | 認証方式         | `spring.security.oauth2.resourceserver.jwt.jwk-set-uri` | [https://auth.example.com/.well-known/jwks.json](https://auth.example.com/.well-known/jwks.json) | 全環境                | Keycloakなど   |
| **19** |                   | CORS許可       | `app.cors.allowed-origins`                              | [https://frontend.example.com](https://frontend.example.com)                                     | 全環境                | -            |
| **20** |                   | JWT有効期限      | `app.jwt.expiration`                                    | 3600                                                                                             | 全環境                | 秒単位          |
| **21** | **メール**           | SMTPサーバ      | `spring.mail.host`                                      | smtp.gmail.com                                                                                   | 全環境                | -            |
| **22** |                   | ポート          | `spring.mail.port`                                      | 587                                                                                              | 全環境                | TLS用         |
| **23** |                   | ユーザ          | `spring.mail.username`                                  | [noreply@example.com](mailto:noreply@example.com)                                                | 全環境                | -            |
| **24** |                   | パスワード        | `spring.mail.password`                                  | `${MAIL_PASSWORD}`                                                                               | 全環境                | Secrets管理    |
| **25** |                   | TLS有効        | `spring.mail.properties.mail.smtp.starttls.enable`      | true                                                                                             | 全環境                | -            |
| **26** | **外部API連携**       | APIベースURL    | `api.partner.url`                                       | [https://api.partner.com](https://api.partner.com)                                               | stg/prod           | 外部連携先        |
| **27** |                   | タイムアウト       | `api.partner.timeout`                                   | 5000                                                                                             | 全環境                | ミリ秒          |
| **28** |                   | リトライ回数       | `api.partner.retry`                                     | 3                                                                                                | 全環境                | -            |
| **29** | **キャッシュ**         | キャッシュタイプ     | `spring.cache.type`                                     | redis                                                                                            | prod               | localはsimple |
| **30** |                   | Redisホスト     | `spring.data.redis.host`                                | redis                                                                                            | stg/prod           | -            |
| **31** |                   | Redisポート     | `spring.data.redis.port`                                | 6379                                                                                             | 全環境                | -            |
| **32** | **メッセージキュー**      | Kafkaサーバ     | `spring.kafka.bootstrap-servers`                        | kafka:9092                                                                                       | prod               | -            |
| **33** |                   | グループID       | `spring.kafka.consumer.group-id`                        | app-group                                                                                        | 全環境                | -            |
| **34** | **Actuator**      | ヘルスチェック      | `management.endpoints.web.exposure.include`             | health,info,metrics                                                                              | 全環境                | -            |
| **35** |                   | ポート          | `management.server.port`                                | 8081                                                                                             | stg/prod           | 別ポートで公開      |
| **36** | **ファイルアップロード**    | 最大サイズ        | `spring.servlet.multipart.max-file-size`                | 10MB                                                                                             | 全環境                | -            |
| **37** |                   | 最大リクエストサイズ   | `spring.servlet.multipart.max-request-size`             | 15MB                                                                                             | 全環境                | -            |
| **38** | **プロファイル管理**      | アクティブプロファイル  | `spring.profiles.active`                                | local / stg / prod                                                                               | 環境変数指定             | -            |
| **39** | **時刻設定**          | タイムゾーン       | `spring.jackson.time-zone`                              | Asia/Tokyo                                                                                       | 全環境                | -            |
| **40** | **その他**           | APIバージョン     | `app.api.version`                                       | v1                                                                                               | 全環境                | API識別用       |

---

### 🔧 運用補足

* **機密情報（DB_PASSWORD, MAIL_PASSWORD, JWT_SECRET）** は `.env` または Secrets Manager に格納。
* **application.yml** → 共通設定、環境別 `application-{profile}.yml` で上書き。
* **プロファイル切替**：

  ```bash
  java -jar app.jar --spring.profiles.active=stg
  ```
* **構成例ディレクトリ**

  ```
  src/main/resources/
  ├── application.yml
  ├── application-local.yml
  ├── application-stg.yml
  └── application-prod.yml
  ```

---

