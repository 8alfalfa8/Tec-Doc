Spring Bootアプリを直接起動する場合の外部プロファイル参照方法について説明します。

1. コマンドライン引数での指定

基本的な起動方法

```bash
# プロファイルと外部設定を指定
java -jar myapp.jar \
  --spring.profiles.active=prod \
  --spring.config.location=file:/etc/myapp/
```

複数の設定場所を指定

```bash
java -jar myapp.jar \
  --spring.profiles.active=prod \
  --spring.config.location=file:/etc/myapp/,file:./config/,classpath:/
```

2. 環境変数での指定

環境変数を使用

```bash
export SPRING_PROFILES_ACTIVE=prod
export SPRING_CONFIG_LOCATION=file:/etc/myapp/
java -jar myapp.jar
```

環境別の起動スクリプト

start-d1.sh

```bash
#!/bin/bash
export SPRING_PROFILES_ACTIVE=d1
export SPRING_CONFIG_LOCATION=file:/opt/myapp/conf/
export APP_ENVIRONMENT=d1
java -jar myapp.jar
```

start-d2.sh

```bash
#!/bin/bash
export SPRING_PROFILES_ACTIVE=d2
export SPRING_CONFIG_LOCATION=file:/opt/myapp/conf/
export APP_ENVIRONMENT=d2
java -jar myapp.jar
```

start-prod.sh

```bash
#!/bin/bash
export SPRING_PROFILES_ACTIVE=prod
export SPRING_CONFIG_LOCATION=file:/opt/myapp/conf/
export APP_ENVIRONMENT=prod
java -jar myapp.jar
```

3. ディレクトリ構造

```
/opt/myapp/
├── myapp.jar
├── start-d1.sh
├── start-d2.sh
├── start-prod.sh
└── conf/
    ├── application-d1.yaml
    ├── application-d2.yaml
    ├── application-prod.yaml
    └── application-common.yaml

/etc/myapp/
├── application-d1.yaml
├── application-d2.yaml
├── application-prod.yaml
└── application-common.yaml
```

4. 外部設定ファイルの例

共通外部設定 (/opt/myapp/conf/application-common.yaml)

```yaml
spring:
  jpa:
    open-in-view: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        jdbc:
          lob:
            non_contextual_creation: true

app:
  company:
    name: "My Company"
    version: "1.0.0"
  
logging:
  level:
    root: INFO
    com.example: DEBUG
```

d1環境設定 (/opt/myapp/conf/application-d1.yaml)

```yaml
spring:
  profiles: d1
  datasource:
    url: jdbc:postgresql://d1-db:5432/d1db
    username: ${DB_D1_USERNAME:d1_user}
    password: ${DB_D1_PASSWORD:d1_pass}
    hikari:
      maximum-pool-size: 5

app:
  environment: "開発環境1"
  api:
    base-url: "https://api-d1.example.com"
    timeout: 5000
  feature:
    debug-mode: true
    experimental-features: true
```

d2環境設定 (/opt/myapp/conf/application-d2.yaml)

```yaml
spring:
  profiles: d2
  datasource:
    url: jdbc:postgresql://d2-db:5432/d2db
    username: ${DB_D2_USERNAME:d2_user}
    password: ${DB_D2_PASSWORD:d2_pass}
    hikari:
      maximum-pool-size: 10

app:
  environment: "開発環境2"
  api:
    base-url: "https://api-d2.example.com"
    timeout: 3000
  feature:
    debug-mode: true
    experimental-features: false
```

prod環境設定 (/opt/myapp/conf/application-prod.yaml)

```yaml
spring:
  profiles: prod
  datasource:
    url: jdbc:postgresql://prod-db:5432/proddb
    username: ${DB_PROD_USERNAME}
    password: ${DB_PROD_PASSWORD}
    hikari:
      maximum-pool-size: 20
      connection-timeout: 30000

app:
  environment: "本番環境"
  api:
    base-url: "https://api.example.com"
    timeout: 10000
  feature:
    debug-mode: false
    experimental-features: false
  security:
    cors:
      allowed-origins: "https://example.com"
      
management:
  endpoints:
    web:
      exposure:
        include: "health,info,metrics"
  endpoint:
    health:
      show-details: when_authorized
```

5. JVMシステムプロパティでの指定

システムプロパティを使用

```bash
java -Dspring.profiles.active=prod \
     -Dspring.config.location=file:/opt/myapp/conf/ \
     -Dapp.environment=prod \
     -jar myapp.jar
```

複数プロファイルの指定

```bash
java -Dspring.profiles.active=prod,monitoring,audit \
     -Dspring.config.location=file:/opt/myapp/conf/ \
     -jar myapp.jar
```

6. Spring Bootアプリケーション側の設定

メインアプリケーションクラス

```java
@SpringBootApplication
public class Application {
    
    private static final Logger logger = LoggerFactory.getLogger(Application.class);
    
    public static void main(String[] args) {
        SpringApplication application = new SpringApplication(Application.class);
        
        // カスタムプロパティソースを追加
        application.addListeners(new ApplicationStartupListener());
        
        // デフォルトプロパティを設定
        application.setDefaultProperties(getDefaultProperties());
        
        application.run(args);
    }
    
    private static Properties getDefaultProperties() {
        Properties props = new Properties();
        
        // 外部設定ファイルのインポート
        props.put("spring.config.import", 
            "optional:file:/opt/myapp/conf/application-common.yaml," +
            "optional:file:/opt/myapp/conf/application-{spring.profiles.active}.yaml," +
            "optional:file:./config/application-{spring.profiles.active}.yaml");
        
        // デフォルトプロファイル
        props.put("spring.profiles.default", "d1");
        
        return props;
    }
    
    static class ApplicationStartupListener implements ApplicationListener<ApplicationEnvironmentPreparedEvent> {
        @Override
        public void onApplicationEvent(ApplicationEnvironmentPreparedEvent event) {
            ConfigurableEnvironment env = event.getEnvironment();
            String[] activeProfiles = env.getActiveProfiles();
            logger.info("アクティブなプロファイル: {}", Arrays.toString(activeProfiles));
            logger.info("設定ファイルの場所: {}", env.getProperty("spring.config.location"));
        }
    }
}
```

設定検証クラス

```java
@Component
public class ConfigValidator implements ApplicationRunner {
    
    private static final Logger logger = LoggerFactory.getLogger(ConfigValidator.class);
    
    @Autowired
    private Environment environment;
    
    @Value("${app.environment:不明}")
    private String appEnvironment;
    
    @Override
    public void run(ApplicationArguments args) throws Exception {
        logger.info("=== 設定検証開始 ===");
        logger.info("環境: {}", appEnvironment);
        logger.info("アクティブプロファイル: {}", Arrays.toString(environment.getActiveProfiles()));
        
        // 外部設定の確認
        checkExternalConfigs();
        
        logger.info("=== 設定検証完了 ===");
    }
    
    private void checkExternalConfigs() {
        String[] configs = {
            "app.company.name",
            "spring.datasource.url",
            "app.api.base-url"
        };
        
        for (String config : configs) {
            String value = environment.getProperty(config);
            if (value != null) {
                logger.info("設定 {}: {}", config, value);
            } else {
                logger.warn("設定 {} が見つかりません", config);
            }
        }
    }
}
```

7. 設定の優先順位を確認するコントローラー

```java
@RestController
@RequestMapping("/api/admin")
public class ConfigController {
    
    @Autowired
    private Environment environment;
    
    @GetMapping("/config")
    public Map<String, Object> getConfigInfo() {
        Map<String, Object> config = new HashMap<>();
        
        // プロファイル情報
        config.put("activeProfiles", environment.getActiveProfiles());
        config.put("defaultProfiles", environment.getDefaultProfiles());
        
        // 設定ソース情報
        config.put("configLocation", environment.getProperty("spring.config.location"));
        config.put("configImport", environment.getProperty("spring.config.import"));
        
        // 重要な設定値
        Map<String, String> settings = new HashMap<>();
        settings.put("app.environment", environment.getProperty("app.environment"));
        settings.put("spring.datasource.url", environment.getProperty("spring.datasource.url"));
        settings.put("app.api.base-url", environment.getProperty("app.api.base-url"));
        config.put("settings", settings);
        
        // プロパティソースの一覧
        List<String> propertySources = new ArrayList<>();
        for (PropertySource<?> source : ((AbstractEnvironment) environment).getPropertySources()) {
            propertySources.add(source.getName());
        }
        config.put("propertySources", propertySources);
        
        return config;
    }
}
```

8. 詳細な起動オプション

クラスパスと外部設定の組み合わせ

```bash
java -cp "myapp.jar:./config/" \
  -Dspring.profiles.active=prod \
  -Dspring.config.location=optional:classpath:/,optional:file:./config/,optional:file:/etc/myapp/ \
  com.example.Application
```

プロファイルグループの使用

```bash
java -jar myapp.jar \
  --spring.profiles.active=production \
  --spring.profiles.group.production=prod,monitoring,security \
  --spring.profiles.group.development=d1,debug \
  --spring.config.location=file:/opt/myapp/conf/
```

9. Dockerを使用する場合

Dockerfile

```dockerfile
FROM openjdk:17-jre-slim

WORKDIR /app
COPY target/myapp.jar .
COPY conf/ /app/conf/

ENV SPRING_PROFILES_ACTIVE=d1
ENV SPRING_CONFIG_LOCATION=file:/app/conf/

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "myapp.jar"]
```

docker-compose.yml

```yaml
version: '3.8'

services:
  app-d1:
    build: .
    environment:
      - SPRING_PROFILES_ACTIVE=d1
      - DB_D1_USERNAME=d1_user
      - DB_D1_PASSWORD=d1_password
    volumes:
      - ./conf/d1/:/app/conf/
    ports:
      - "8080:8080"

  app-d2:
    build: .
    environment:
      - SPRING_PROFILES_ACTIVE=d2
      - DB_D2_USERNAME=d2_user
      - DB_D2_PASSWORD=d2_password
    volumes:
      - ./conf/d2/:/app/conf/
    ports:
      - "8081:8080"

  app-prod:
    build: .
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DB_PROD_USERNAME=prod_user
      - DB_PROD_PASSWORD=prod_password
    volumes:
      - ./conf/prod/:/app/conf/
    ports:
      - "8082:8080"
```

10. 設定の優先順位まとめ

Spring Bootの設定優先順位（高い順）:

1. デプロイ時引数 (--key=value)
2. JVMシステムプロパティ (-Dkey=value)
3. 環境変数
4. テスト用の@TestPropertySource
5. jar外部のapplication-{profile}.yaml
6. jar内部のapplication-{profile}.yaml
7. jar外部のapplication.yaml
8. jar内部のapplication.yaml
9. @PropertySourceアノテーション
10. デフォルトプロパティ

この方法により、JBossを使用せずに直接Spring Bootアプリを起動する場合でも、外部設定ファイルを柔軟に参照できます。環境変数や起動パラメータで簡単に環境を切り替えられるため、CI/CDパイプラインとの連携も容易です。