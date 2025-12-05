# 大規模TypeScriptプロジェクト開発におけるコーディング規約

## 1. 基本原則

### 1.1 一貫性の維持
- プロジェクト全体で一貫したコーディングスタイルを採用
- 既存のコードスタイルに合わせて新規コードを記述
- チーム全体で規約を共有・遵守

### 1.2 型安全の最大化
- `any` 型の使用を最小限に制限
- 明示的な型注釈を適切に使用
- 厳格なTypeScriptコンパイラオプションを有効化

## 2. プロジェクト構成

### 2.1 ディレクトリ構造
```
src/
├── core/           # コアビジネスロジック
├── domains/        # ドメイン層 (DDD)
├── application/    # アプリケーション層
├── infrastructure/ # インフラ層
├── shared/         # 共有ユーティリティ
├── types/          # グローバル型定義
└── index.ts        # エントリーポイント
```

### 2.2 ファイル命名規則
- コンポーネント: `PascalCase.tsx`
- ユーティリティ: `camelCase.ts`
- 型定義: `PascalCase.types.ts`
- 定数: `SCREAMING_SNAKE_CASE.ts`
- テスト: `*.test.ts` または `*.spec.ts`

## 3. コードスタイル規約

### 3.1 命名規則
```typescript
// インターフェース - 先頭に I を付けない（TypeScript公式推奨）
interface UserProfile {
  id: string;
  name: string;
}

// 型エイリアス
type UserRole = 'admin' | 'user' | 'guest';

// クラス
class UserService {
  private readonly authToken: string;
  
  public async getUser(id: string): Promise<User> {
    // ...
  }
}

// 定数
const MAX_RETRY_COUNT = 3;
const DEFAULT_CONFIG = { timeout: 5000 };

// 列挙型 - const enum を推奨（バンドルサイズ削減）
const enum HttpStatus {
  OK = 200,
  NOT_FOUND = 404,
}
```

### 3.2 型定義
```typescript
// 明示的な戻り値型を指定
function calculateTotal(price: number, quantity: number): number {
  return price * quantity;
}

// ジェネリック型の適切な使用
interface Repository<T> {
  findById(id: string): Promise<T | null>;
  save(entity: T): Promise<void>;
}

// Utility型の活用
type PartialUser = Partial<User>;
type ReadonlyConfig = Readonly<Config>;
type UserKeys = keyof User;

// Discriminated Union
type ApiResponse =
  | { status: 'success'; data: User }
  | { status: 'error'; message: string };
```

## 4. 厳格なコンパイラオプション

### 4.1 推奨tsconfig.json設定
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "target": "ES2022",
    "module": "ESNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

## 5. エラーハンドリング

### 5.1 例外処理
```typescript
// カスタムエラークラス
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500
  ) {
    super(message);
    this.name = 'AppError';
  }
}

// Result型の活用
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E };

async function fetchData(): Promise<Result<UserData>> {
  try {
    const data = await api.get<UserData>('/user');
    return { success: true, data };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error : new Error('Unknown error')
    };
  }
}
```

## 6. 非同期処理

### 6.1 Promise/Async Await
```typescript
// async関数には明示的な戻り値型を指定
async function getUserData(userId: string): Promise<UserData> {
  const [user, profile] = await Promise.all([
    userRepository.findById(userId),
    profileRepository.findByUserId(userId)
  ]);
  
  if (!user) {
    throw new AppError('User not found', 'USER_NOT_FOUND', 404);
  }
  
  return { user, profile };
}

// 並行処理の最適化
async function processBatch(items: Item[]): Promise<Result[]> {
  const batchSize = 5;
  const results: Result[] = [];
  
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(
      batch.map(item => processItem(item))
    );
    results.push(...batchResults);
  }
  
  return results;
}
```

## 7. テスト規約

### 7.1 テスト構造
```typescript
describe('UserService', () => {
  let userService: UserService;
  let mockRepository: jest.Mocked<UserRepository>;
  
  beforeEach(() => {
    mockRepository = {
      findById: jest.fn(),
      save: jest.fn(),
    } as jest.Mocked<UserRepository>;
    
    userService = new UserService(mockRepository);
  });
  
  describe('#getUser', () => {
    it('存在するユーザーIDを指定するとユーザーデータを返すこと', async () => {
      // Arrange
      const userId = '123';
      const expectedUser: User = { id: userId, name: 'Test User' };
      mockRepository.findById.mockResolvedValue(expectedUser);
      
      // Act
      const result = await userService.getUser(userId);
      
      // Assert
      expect(result).toEqual(expectedUser);
      expect(mockRepository.findById).toHaveBeenCalledWith(userId);
    });
    
    it('存在しないユーザーIDを指定するとnullを返すこと', async () => {
      // Arrange
      mockRepository.findById.mockResolvedValue(null);
      
      // Act
      const result = await userService.getUser('invalid-id');
      
      // Assert
      expect(result).toBeNull();
    });
  });
});
```

## 8. パフォーマンス最適化

### 8.1 バンドルサイズ対策
```typescript
// ダイナミックインポート
const loadHeavyModule = async () => {
  const { HeavyComponent } = await import('./HeavyComponent');
  return HeavyComponent;
};

// バレルファイルの適切な使用
// 悪い例: すべてをエクスポート
export * from './module1';
export * from './module2';

// 良い例: 必要なものだけエクスポート
export { ComponentA } from './components/ComponentA';
export { UtilityB } from './utils/UtilityB';
```

## 9. ドキュメンテーション

### 9.1 JSDocコメント
```typescript
/**
 * ユーザー情報を取得します
 * @param userId - ユーザーID（UUID形式）
 * @param options - 取得オプション
 * @returns ユーザー情報。存在しない場合はnull
 * @throws {AppError} ネットワークエラー時に発生
 * @example
 * ```typescript
 * const user = await getUser('123e4567-e89b-12d3-a456-426614174000');
 * ```
 */
async function getUser(
  userId: string,
  options?: GetUserOptions
): Promise<User | null> {
  // 実装
}
```

## 10. Gitワークフロー

### 10.1 コミット規約
```
feat: 新機能
fix: バグ修正
docs: ドキュメントのみの変更
style: コードの意味に影響しない変更（空白、フォーマットなど）
refactor: バグ修正や機能追加ではないコード変更
perf: パフォーマンス改善
test: テストの追加・修正
chore: ビルドプロセスやツールの変更
```

## 11. コードレビューチェックリスト

### 11.1 必須チェック項目
- [ ] 型安全性が保たれているか
- [ ] テストが追加/更新されているか
- [ ] パフォーマンスへの影響はないか
- [ ] セキュリティリスクはないか
- [ ] ドキュメントが更新されているか
- [ ] エラーハンドリングが適切か
- [ ] コードの重複はないか

## 12. ツール設定

### 12.1 推奨開発環境
- **ESLint**: コード品質チェック
- **Prettier**: コードフォーマット
- **Husky**: Gitフック
- **lint-staged**: ステージングされたファイルのみリント
- **Jest**: テストフレームワーク

### 12.2 .eslintrc.js 例
```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'import'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'plugin:import/recommended',
    'plugin:import/typescript',
  ],
  rules: {
    '@typescript-eslint/explicit-function-return-type': 'error',
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'import/order': ['error', {
      'groups': ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
      'newlines-between': 'always'
    }]
  }
};
```

この規約はプロジェクトの規模やチームの状況に応じて調整してください。重要なのは、チーム全体で一貫したルールを守り、定期的に見直し・改善することです。
