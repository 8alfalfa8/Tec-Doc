# 大規模SpringBootプロジェクトにおけるコーディング規約

## 1. 基本原則

### 1.1 一貫性の保持
- プロジェクト全体で同じ規約を厳守
- 既存のコードスタイルに合わせる
- チーム全体での定期的なコードレビュー実施

### 1.2 可読性優先
- 自己説明的なコードを書く
- 複雑なロジックにはコメントを追加
- マジックナンバーは定数化

## 2. パッケージ構成規約

```java
// 推奨構成
com.company.project
├── application              // アプリケーション層
│   ├── controller          // RESTコントローラー
│   ├── dto                 // データ転送オブジェクト
│   └── service             // アプリケーションサービス
├── domain                  // ドメイン層
│   ├── model              // エンティティ
│   ├── repository         // リポジトリインターフェース
│   └── service            // ドメインサービス
├── infrastructure         // インフラストラクチャ層
│   ├── persistence        // JPAエンティティ/リポジトリ実装
│   ├── external           // 外部サービス連携
│   └── config             // 設定クラス
└── common                 // 共通ライブラリ
    ├── exception          // 例外クラス
    ├── util               // ユーティリティ
    └── constant           // 定数クラス
```

## 3. 命名規約

### 3.1 クラス・インターフェース
```java
// パスカルケース（アッパーキャメルケース）
@RestController
public class UserManagementController { }

@Service
public class UserServiceImpl implements UserService { }

@Entity
public class UserAccount { }

// DTO
public class UserCreateRequest { }
public class UserResponse { }

// 例外
public class UserNotFoundException extends BusinessException { }
```

### 3.2 メソッド
```java
// 動詞 + 名詞（キャメルケース）
public UserResponse getUserById(Long id) { }
public void createUser(UserCreateRequest request) { }
public boolean isValidPassword(String password) { }

// クエリメソッド（Repository）
List<User> findByEmailAndActiveTrue(String email);
Optional<User> findFirstByOrderByCreatedAtDesc();
```

### 3.3 変数・定数
```java
// ローカル変数（キャメルケース）
String userName;
List<Product> productList;
int retryCount;

// 定数（スネークケース大文字）
public static final int MAX_RETRY_COUNT = 3;
private static final String ERROR_MESSAGE_PREFIX = "ERR_";
```

## 4. コーディング規約

### 4.1 インデント・フォーマット
```java
// インデント: 4スペース（タブ禁止）
// 行長: 120文字以内
public class ExampleService {
    
    private final UserRepository userRepository;
    private final EmailService emailService;
    
    @Transactional
    public UserResponse createUser(UserCreateRequest request) {
        // バリデーション
        validateRequest(request);
        
        // エンティティ作成
        User user = User.builder()
            .username(request.getUsername())
            .email(request.getEmail())
            .build();
        
        // 保存
        user = userRepository.save(user);
        
        // イベント発行
        emailService.sendWelcomeEmail(user);
        
        return UserResponse.from(user);
    }
}
```

### 4.2 Null安全
```java
// Optionalの活用
public Optional<User> findUser(Long id) {
    return userRepository.findById(id);
}

// Nullチェック
public void processUser(User user) {
    if (user == null) {
        throw new IllegalArgumentException("User must not be null");
    }
    // 処理
}

// @NonNullアノテーション
public void updateUser(@NonNull User user) {
    // userはnullではないことが保証
}
```

### 4.3 例外処理
```java
// カスタム例外の定義
public class BusinessException extends RuntimeException {
    private final ErrorCode errorCode;
    
    public BusinessException(ErrorCode errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }
}

// 例外処理例
@Service
@Transactional
public class OrderService {
    
    public Order processOrder(Long orderId) {
        try {
            Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new OrderNotFoundException(orderId));
            
            return process(order);
            
        } catch (DataAccessException e) {
            log.error("Database error while processing order: {}", orderId, e);
            throw new SystemException("DATABASE_ERROR", e);
        }
    }
}
```

## 5. Javadoc規約

### 5.1 クラス・インターフェース
```java
/**
 * ユーザー管理を行うサービスインターフェース。
 * <p>
 * ユーザーの登録、更新、削除などのビジネスロジックを提供します。
 * </p>
 *
 * @author 開発者名
 * @since 1.0
 * @version 1.1
 */
public interface UserService {
    
    /**
     * 指定されたIDのユーザー情報を取得します。
     * <p>
     * ユーザーが存在しない場合は{@link UserNotFoundException}をスローします。
     * </p>
     *
     * @param userId ユーザーID（null不可）
     * @return ユーザー情報
     * @throws UserNotFoundException ユーザーが存在しない場合
     * @throws IllegalArgumentException userIdがnullの場合
     * @see UserResponse
     */
    UserResponse getUserById(Long userId);
}
```

### 5.2 メソッド
```java
/**
 * 新規ユーザーを登録します。
 * <p>
 * 以下のバリデーションを実施します：
 * <ul>
 *   <li>メールアドレスの形式チェック</li>
 *   <li>パスワードの複雑さチェック</li>
 *   <li>メールアドレスの重複チェック</li>
 * </ul>
 * </p>
 *
 * @param request ユーザー登録リクエスト
 * @return 登録されたユーザー情報
 * @throws DuplicateEmailException メールアドレスが既に登録されている場合
 * @throws InvalidParameterException リクエストパラメータが不正な場合
 */
@Transactional
public UserResponse registerUser(UserRegistrationRequest request) {
    // 実装
}
```

### 5.3 複雑なロジックのコメント
```java
public PaymentResult processPayment(PaymentRequest request) {
    // ステップ1: 支払い情報のバリデーション
    validatePaymentRequest(request);
    
    // ステップ2: 決済プロバイダーへのリクエスト作成
    PaymentProviderRequest providerRequest = 
        createProviderRequest(request);
    
    // ステップ3: 外部API呼び出し（リトライロジック付き）
    PaymentProviderResponse providerResponse = 
        paymentProviderClient.executeWithRetry(
            providerRequest, 
            MAX_RETRY_COUNT, 
            RETRY_DELAY_MS
        );
    
    // ステップ4: レスポンスの検証と変換
    return convertToPaymentResult(providerResponse);
}
```

## 6. Spring Boot固有の規約

### 6.1 依存性注入（DI）
```java
// コンストラクタインジェクションを推奨
@Service
@Transactional(readOnly = true)
public class UserServiceImpl implements UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuditService auditService;
    
    // @Autowiredは省略可能（コンストラクタが1つの場合）
    public UserServiceImpl(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            AuditService auditService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.auditService = auditService;
    }
}
```

### 6.2 トランザクション管理
```java
@Service
public class OrderService {
    
    @Transactional
    public Order createOrder(OrderRequest request) {
        // メインの処理（すべてのDB操作が同一トランザクション内）
    }
    
    @Transactional(readOnly = true)
    public Order getOrder(Long id) {
        // 参照のみの処理
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void auditLog(AuditEvent event) {
        // 独立したトランザクションで実行
    }
}
```

### 6.3 コントローラー規約
```java
@RestController
@RequestMapping("/api/v1/users")
@Validated
@Slf4j
public class UserController {
    
    private final UserService userService;
    
    @GetMapping("/{id}")
    @Operation(summary = "ユーザー情報取得", description = "IDでユーザー情報を取得します")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "成功"),
        @ApiResponse(responseCode = "404", description = "ユーザー不存在")
    })
    public ResponseEntity<UserResponse> getUser(
            @PathVariable @Min(1) Long id) {
        log.debug("Getting user with id: {}", id);
        UserResponse user = userService.getUserById(id);
        return ResponseEntity.ok(user);
    }
    
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ResponseEntity<UserResponse> createUser(
            @RequestBody @Valid UserCreateRequest request) {
        log.info("Creating new user: {}", request.getEmail());
        UserResponse createdUser = userService.createUser(request);
        
        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(createdUser.getId())
            .toUri();
            
        return ResponseEntity.created(location).body(createdUser);
    }
}
```
## 7. DTOとエンティティ

### 7.1 エンティティクラス
```java
package com.example.project.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * ユーザー情報を表すエンティティ
 * 
 * <p>データベースのusersテーブルとマッピングされる</p>
 */
@Entity
@Table(name = "users")
@Getter
@Setter
public class User {
    
    /**
     * ユーザーID（主キー）
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /**
     * ユーザー名（必須）
     */
    @Column(nullable = false, unique = true, length = 50)
    private String username;
    
    /**
     * メールアドレス（必須）
     */
    @Column(nullable = false, unique = true, length = 100)
    private String email;
    
    /**
     * アカウント有効フラグ
     */
    @Column(nullable = false)
    private boolean enabled = true;
    
    /**
     * レコード作成日時
     */
    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    /**
     * レコード更新日時
     */
    @UpdateTimestamp
    @Column(nullable = false)
    private LocalDateTime updatedAt;
}
```

### 7.2 DTOクラス
```java
package com.example.project.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * ユーザー作成リクエストのDTO
 */
@Data
@Schema(description = "ユーザー作成リクエスト")
public class CreateUserRequestDto {
    
    /**
     * ユーザー名（3〜50文字）
     */
    @NotBlank(message = "ユーザー名は必須です")
    @Size(min = 3, max = 50, message = "ユーザー名は3〜50文字で入力してください")
    @Schema(description = "ユーザー名", example = "john_doe", requiredMode = Schema.RequiredMode.REQUIRED)
    private String username;
    
    /**
     * メールアドレス
     */
    @NotBlank(message = "メールアドレスは必須です")
    @Email(message = "有効なメールアドレスを入力してください")
    @Schema(description = "メールアドレス", example = "john@example.com", requiredMode = Schema.RequiredMode.REQUIRED)
    private String email;
    
    /**
     * パスワード（8文字以上）
     */
    @NotBlank(message = "パスワードは必須です")
    @Size(min = 8, message = "パスワードは8文字以上で入力してください")
    @Schema(description = "パスワード", example = "password123", requiredMode = Schema.RequiredMode.REQUIRED)
    private String password;
}
```

## 8. テスト規約

### 8.1 テストクラス構成
```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private PasswordEncoder passwordEncoder;
    
    @InjectMocks
    private UserServiceImpl userService;
    
    @Test
    @DisplayName("有効なリクエストでユーザーが正常に作成されること")
    void shouldCreateUser_WhenRequestIsValid() {
        // Given
        UserCreateRequest request = UserCreateRequest.builder()
            .email("test@example.com")
            .password("ValidPass123!")
            .build();
            
        User savedUser = User.builder()
            .id(1L)
            .email(request.getEmail())
            .build();
            
        when(passwordEncoder.encode(anyString()))
            .thenReturn("encodedPassword");
        when(userRepository.save(any(User.class)))
            .thenReturn(savedUser);
        
        // When
        UserResponse result = userService.createUser(request);
        
        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getEmail()).isEqualTo("test@example.com");
        
        verify(userRepository).save(any(User.class));
        verify(passwordEncoder).encode("ValidPass123!");
    }
    
    @ParameterizedTest
    @ValueSource(strings = {"weak", "123456", "password"})
    @DisplayName("弱いパスワードで例外がスローされること")
    void shouldThrowException_WhenPasswordIsWeak(String weakPassword) {
        // Given
        UserCreateRequest request = UserCreateRequest.builder()
            .email("test@example.com")
            .password(weakPassword)
            .build();
        
        // When & Then
        assertThatThrownBy(() -> userService.createUser(request))
            .isInstanceOf(InvalidPasswordException.class)
            .hasMessageContaining("パスワードが弱すぎます");
    }
}
```

## 9. ロギング規約

```java
@Slf4j  // Lombokのアノテーション
@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    
    /**
     * ユーザー情報を更新する
     */
    @Transactional
    public UserResponseDto updateUser(UpdateUserRequestDto request) {
        log.info("ユーザー更新開始: userId={}", request.getId());
        
        try {
            User user = userRepository.findById(request.getId())
                    .orElseThrow(() -> {
                        log.warn("ユーザーが見つかりません: userId={}", request.getId());
                        return new UserNotFoundException(request.getId());
                    });
            
            user.update(request);
            
            log.debug("ユーザー情報を更新しました: {}", user);
            return UserMapper.toDto(user);
            
        } catch (Exception e) {
            log.error("ユーザー更新中にエラーが発生しました: userId={}", request.getId(), e);
            throw e;
        } finally {
            log.info("ユーザー更新終了: userId={}", request.getId());
        }
    }
}
```

## 10. 設定ファイル規約

### 10.1 application.yml
```yml
# 環境ごとの設定ファイル命名
# application.yml          # 共通設定
# application-local.yml    # ローカル開発環境
# application-dev.yml      # 開発環境
# application-prod.yml     # 本番環境

spring:
  application:
    name: example-project
  
  datasource:
    url: jdbc:mysql://localhost:3306/example_db
    username: ${DB_USERNAME:root}
    password: ${DB_PASSWORD:password}
    driver-class-name: com.mysql.cj.jdbc.Driver
  
  jpa:
    hibernate:
      ddl-auto: validate  # 本番では 'validate' または 'none'
    show-sql: false       # 本番では false
    properties:
      hibernate:
        format_sql: true
        dialect: org.hibernate.dialect.MySQL8Dialect

# カスタム設定
app:
  security:
    jwt:
      secret: ${JWT_SECRET:defaultSecretKey}
      expiration-ms: 86400000  # 24時間
  pagination:
    default-page-size: 20
    max-page-size: 100

# ロギング設定
logging:
  level:
    com.example.project: DEBUG
    org.springframework.web: INFO
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql.BasicBinder: TRACE
```

## 11. ドキュメント生成

### 11.1 Javadoc生成設定（pom.xml）
```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-javadoc-plugin</artifactId>
            <version>3.4.0</version>
            <configuration>
                <show>private</show>
                <nohelp>true</nohelp>
                <charset>UTF-8</charset>
                <encoding>UTF-8</encoding>
                <docencoding>UTF-8</docencoding>
                <tags>
                    <tag>
                        <name>apiNote</name>
                        <placement>a</placement>
                        <head>APIノート:</head>
                    </tag>
                </tags>
            </configuration>
        </plugin>
    </plugins>
</build>
```

### 12.2 OpenAPI/Swagger設定
```java
@Configuration
public class OpenApiConfig {
    
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("User Management API")
                .version("1.0")
                .description("ユーザー管理システムのREST API")
                .contact(new Contact()
                    .name("開発チーム")
                    .email("dev@company.com")))
            .addSecurityItem(new SecurityRequirement().addList("bearerAuth"))
            .components(new Components()
                .addSecuritySchemes("bearerAuth",
                    new SecurityScheme()
                        .type(SecurityScheme.Type.HTTP)
                        .scheme("bearer")
                        .bearerFormat("JWT")));
    }
}
```

## 13. コード品質チェック

### 13.1 Checkstyle設定例（checkstyle.xml）
```xml
<?xml version="1.0"?>
<!DOCTYPE module PUBLIC "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN"
        "https://checkstyle.org/dtds/configuration_1_3.dtd">
<module name="Checker">
    <module name="TreeWalker">
        <!-- Javadocチェック -->
        <module name="JavadocMethod">
            <property name="scope" value="public"/>
            <property name="allowMissingParamTags" value="false"/>
        </module>
        
        <!-- 命名規約 -->
        <module name="ConstantName"/>
        <module name="LocalFinalVariableName"/>
        <module name="LocalVariableName"/>
        <module name="MethodName"/>
        <module name="PackageName"/>
        <module name="ParameterName"/>
        <module name="StaticVariableName"/>
        <module name="TypeName"/>
        
        <!-- インポートルール -->
        <module name="AvoidStarImport"/>
        <module name="UnusedImports"/>
    </module>
</module>
```

### 13.2 静的解析ツール
- **SpotBugs**: 潜在的なバグ検出
- **PMD**: コード品質チェック
- **SonarQube**: 総合的なコード品質管理

## 14. Gitコミット規約

```
feat: 新機能追加
fix: バグ修正
docs: ドキュメントのみの変更
style: コードフォーマット変更（機能に影響なし）
refactor: リファクタリング
test: テスト追加・修正
chore: ビルドプロセス、ツールチェイン変更
```

---

この規約はプロジェクトの要件に応じて適宜調整してください。特に重要なのは、チーム全体で規約を共有し、定期的に見直しを行うことです。
