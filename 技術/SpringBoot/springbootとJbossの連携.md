d1、d2、prod環境でWAR内部と外部の両方のYAML設定を利用するJBossとSpring Bootの設定一式を作成します。

ディレクトリ構造

```
/opt/wildfly/
├── bin/
│   └── standalone.conf
├── standalone/
│   ├── configuration/
│   │   └── standalone.xml
│   └── conf/
│       ├── application-d1.yaml
│       ├── application-d2.yaml
│       ├── application-prod.yaml
│       └── application-common.yaml
└── deployments/
    └── myapp.war

myapp-project/
├── src/
│   └── main/
│       ├── resources/
│       │   ├── application.yaml
│       │   ├── application-d1.yaml
│       │   ├── application-d2.yaml
│       │   └── application-prod.yaml
│       └── webapp/
└── pom.xml
```

1. WAR内部の設定ファイル

基本設定 (src/main/resources/application.yaml)

```yaml
spring:
  application:
    name: my-application
  config:
    import:
      - "optional:file:/opt/wildfly/standalone/conf/application-common.yaml"
      - "optional:file:/opt/wildfly/standalone/conf/application-{profile}.yaml"
  
app:
  version: 1.0.0
  internal-config: "これはWAR内部の基本設定です"
  
logging:
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %logger{36} - %msg%n"
```

環境別設定 (WAR内部)

src/main/resources/application-d1.yaml

```yaml
spring:
  profiles: d1
  datasource:
    url: jdbc:h2:mem:d1db
    username: sa
    password: ""
  jpa:
    hibernate:
      ddl-auto: create-drop

app:
  environment: "開発環境1 (d1)"
  api:
    base-url: "https://api-d1.example.com"
  internal-only: "WAR内部のd1設定"
```

src/main/resources/application-d2.yaml

```yaml
spring:
  profiles: d2
  datasource:
    url: jdbc:postgresql://localhost:5432/d2db
    username: d2_user
    password: d2_pass
  jpa:
    hibernate:
      ddl-auto: update

app:
  environment: "開発環境2 (d2)"
  api:
    base-url: "https://api-d2.example.com"
  internal-only: "WAR内部のd2設定"
```

src/main/resources/application-prod.yaml

```yaml
spring:
  profiles: prod
  jpa:
    hibernate:
      ddl-auto: validate

app:
  environment: "本番環境 (prod)"
  api:
    base-url: "https://api.example.com"
  internal-only: "WAR内部のprod設定"
```

2. WAR外部の設定ファイル

共通外部設定 (/opt/wildfly/standalone/conf/application-common.yaml)

```yaml
# 全環境共通の外部設定
spring:
  jpa:
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        show_sql: false
        format_sql: true

app:
  external-config: "これは外部共通設定です"
  security:
    jwt-expiration: 86400000
```

環境別外部設定

/opt/wildfly/standalone/conf/application-d1.yaml

```yaml
spring:
  profiles: d1
  datasource:
    jndi-name: java:jboss/datasources/D1DS
  mail:
    host: smtp-d1.example.com
    port: 587

app:
  external-d1-config: "外部d1設定"
  database:
    schema: d1_schema
  logging:
    level: DEBUG
```

/opt/wildfly/standalone/conf/application-d2.yaml

```yaml
spring:
  profiles: d2
  datasource:
    jndi-name: java:jboss/datasources/D2DS
  mail:
    host: smtp-d2.example.com
    port: 587

app:
  external-d2-config: "外部d2設定"
  database:
    schema: d2_schema
  logging:
    level: INFO
```

/opt/wildfly/standalone/conf/application-prod.yaml

```yaml
spring:
  profiles: prod
  datasource:
    jndi-name: java:jboss/datasources/ProdDS
  mail:
    host: smtp.company.com
    port: 587
    username: ${SMTP_USERNAME}
    password: ${SMTP_PASSWORD}

app:
  external-prod-config: "外部prod設定"
  database:
    schema: prod_schema
  security:
    admin-users: "admin@company.com,superuser@company.com"
  monitoring:
    enabled: true
    endpoint: "/actuator/prometheus"
```

3. JBoss設定

standalone.xml のシステムプロパティ

```xml
<system-properties>
    <!-- 環境ごとに変更するプロパティ -->
    <property name="app.environment" value="d1"/>
    <property name="spring.profiles.active" value="d1"/>
    <property name="spring.config.import" 
              value="optional:file:/opt/wildfly/standalone/conf/application-common.yaml,
                     optional:file:/opt/wildfly/standalone/conf/application-${app.environment}.yaml"/>
    
    <!-- 機密情報は環境変数から -->
    <property name="SMTP_USERNAME" value="${env.SMTP_USERNAME}"/>
    <property name="SMTP_PASSWORD" value="${env.SMTP_PASSWORD}"/>
</system-properties>
```

データソース定義 (standalone.xml)

```xml
<datasources>
    <!-- d1環境用データソース -->
    <datasource jndi-name="java:jboss/datasources/D1DS" pool-name="D1DS">
        <connection-url>jdbc:postgresql://d1-db.example.com:5432/d1db</connection-url>
        <driver>postgresql</driver>
        <security>
            <user-name>${DB_D1_USERNAME}</user-name>
            <password>${DB_D1_PASSWORD}</password>
        </security>
    </datasource>
    
    <!-- d2環境用データソース -->
    <datasource jndi-name="java:jboss/datasources/D2DS" pool-name="D2DS">
        <connection-url>jdbc:postgresql://d2-db.example.com:5432/d2db</connection-url>
        <driver>postgresql</driver>
        <security>
            <user-name>${DB_D2_USERNAME}</user-name>
            <password>${DB_D2_PASSWORD}</password>
        </security>
    </datasource>
    
    <!-- prod環境用データソース -->
    <datasource jndi-name="java:jboss/datasources/ProdDS" pool-name="ProdDS">
        <connection-url>jdbc:postgresql://prod-db.example.com:5432/proddb</connection-url>
        <driver>postgresql</driver>
        <security>
            <user-name>${DB_PROD_USERNAME}</user-name>
            <password>${DB_PROD_PASSWORD}</password>
        </security>
    </datasource>
</datasources>
```

4. JVMオプション設定

standalone.conf の設定

```bash
# 環境判定
if [ -z "$APP_ENVIRONMENT" ]; then
    APP_ENVIRONMENT="d1"
fi

# Spring Boot設定
JAVA_OPTS="$JAVA_OPTS -Dapp.environment=$APP_ENVIRONMENT"
JAVA_OPTS="$JAVA_OPTS -Dspring.profiles.active=$APP_ENVIRONMENT"
JAVA_OPTS="$JAVA_OPTS -Dspring.config.import=optional:file:/opt/wildfly/standalone/conf/application-common.yaml,optional:file:/opt/wildfly/standalone/conf/application-${APP_ENVIRONMENT}.yaml"

# ログ設定
JAVA_OPTS="$JAVA_OPTS -Dlogging.config=file:/opt/wildfly/standalone/conf/logback-${APP_ENVIRONMENT}.xml"
```

5. Spring Bootアプリケーション

メインアプリケーションクラス

```java
@SpringBootApplication
public class Application extends SpringBootServletInitializer {
    
    private static final Logger logger = LoggerFactory.getLogger(Application.class);
    
    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
        return application.sources(Application.class)
                .profiles(detectActiveProfiles())
                .properties(getDefaultProperties());
    }
    
    public static void main(String[] args) {
        SpringApplication application = new SpringApplication(Application.class);
        application.setAdditionalProfiles(detectActiveProfiles());
        application.run(args);
    }
    
    private static String[] detectActiveProfiles() {
        String env = System.getProperty("app.environment", "d1");
        logger.info("検出された環境: {}", env);
        return new String[]{env};
    }
    
    private Properties getDefaultProperties() {
        Properties props = new Properties();
        props.put("spring.config.import", 
            "optional:file:/opt/wildfly/standalone/conf/application-common.yaml," +
            "optional:file:/opt/wildfly/standalone/conf/application-${app.environment}.yaml");
        return props;
    }
}
```

設定確認コントローラー

```java
@RestController
@RequestMapping("/api/config")
public class ConfigController {
    
    @Autowired
    private Environment environment;
    
    @Value("${app.environment:不明}")
    private String appEnvironment;
    
    @Value("${app.internal-config:不明}")
    private String internalConfig;
    
    @Value("${app.external-config:不明}")
    private String externalConfig;
    
    @GetMapping("/info")
    public Map<String, Object> getConfigInfo() {
        Map<String, Object> configInfo = new HashMap<>();
        configInfo.put("activeProfiles", environment.getActiveProfiles());
        configInfo.put("appEnvironment", appEnvironment);
        configInfo.put("internalConfig", internalConfig);
        configInfo.put("externalConfig", externalConfig);
        configInfo.put("configLocations", environment.getProperty("spring.config.import"));
        
        // 環境固有の設定を収集
        Arrays.stream(environment.getActiveProfiles()).forEach(profile -> {
            configInfo.put("internal-" + profile, 
                environment.getProperty("app.internal-only", "未設定"));
            configInfo.put("external-" + profile, 
                environment.getProperty("app.external-" + profile + "-config", "未設定"));
        });
        
        return configInfo;
    }
}
```

6. 環境ごとの起動方法

d1環境で起動

```bash
export APP_ENVIRONMENT=d1
export DB_D1_USERNAME=d1_user
export DB_D1_PASSWORD=d1_password
./standalone.sh -c standalone.xml
```

d2環境で起動

```bash
export APP_ENVIRONMENT=d2
export DB_D2_USERNAME=d2_user
export DB_D2_PASSWORD=d2_password
./standalone.sh -c standalone.xml
```

prod環境で起動

```bash
export APP_ENVIRONMENT=prod
export DB_PROD_USERNAME=prod_user
export DB_PROD_PASSWORD=prod_password
export SMTP_USERNAME=smtp_user
export SMTP_PASSWORD=smtp_password
./standalone.sh -c standalone.xml
```

7. 設定の優先順位確認

この設定により、以下の優先順位で設定が読み込まれます：

1. JVMオプション (-D パラメータ)
2. 環境変数
3. WAR外部の環境別YAML (/opt/wildfly/standalone/conf/application-{env}.yaml)
4. WAR外部の共通YAML (/opt/wildfly/standalone/conf/application-common.yaml)
5. WAR内部の環境別YAML (src/main/resources/application-{env}.yaml)
6. WAR内部の基本YAML (src/main/resources/application.yaml)

8. 確認方法

アプリケーション起動後、以下のエンドポイントで設定を確認できます：

```
GET /api/config/info
```

この設定一式により、d1、d2、prod環境でWAR内部と外部の設定を柔軟に組み合わせて使用できます。機密情報は環境変数で管理し、環境固有の設定は外部YAMLで、アプリケーションの基本設定はWAR内部で管理する構成になっています。