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

### 6.1 依存性注入
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

## 7. テスト規約

### 7.1 テストクラス構成
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

## 8. ドキュメント生成

### 8.1 Javadoc生成設定（pom.xml）
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

### 8.2 OpenAPI/Swagger設定
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

## 9. コード品質チェック

### 9.1 Checkstyle設定例（checkstyle.xml）
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

### 9.2 静的解析ツール
- **SpotBugs**: 潜在的なバグ検出
- **PMD**: コード品質チェック
- **SonarQube**: 総合的なコード品質管理

## 10. Gitコミット規約

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
