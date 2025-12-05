# 大規模Pythonプロジェクトにおけるコーディング規約

## 1. 基本方針

### 1.1 一般原則
- **PEP 8** に準拠する
- **一貫性**を最優先する
- プロジェクト全体で**統一された規約**を適用する
- **可読性**を重視する

### 1.2 ツールと自動化
```python
# 推奨ツール
# フォーマッター: black, yapf
# リンター: flake8, pylint, ruff
# 型チェッカー: mypy, pyright
# Docstringチェック: pydocstyle, darglint
```

## 2. コードスタイル

### 2.1 命名規則
```python
# 変数・関数・メソッド: snake_case
variable_name = "value"
def calculate_total_amount():
    pass

# クラス: PascalCase
class DataProcessor:
    pass

# 定数: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
API_ENDPOINT = "/v1/data"

# プライベート変数/メソッド: _leading_underscore
_private_variable = "hidden"
def _internal_method():
    pass

# モジュール名: short_lowercase
# パッケージ名: short_lowercase
```

### 2.2 インデントとスペース
- **4スペース**を使用（タブ禁止）
- 1行の長さ: **100文字**（black推奨）または 120文字
- 演算子の前後にはスペース
```python
# Good
result = calculate(a, b) + process(c, d)

# Bad
result=calculate(a,b)+process(c,d)
```

### 2.3 インポート規則
```python
# 1. 標準ライブラリ
import os
import sys
from typing import Dict, List, Optional

# 2. サードパーティ
import requests
from django.db import models

# 3. ローカル/アプリケーション
from .utils import helper_function
from models.user import User

# 各グループ内はアルファベット順
# 絶対インポートを優先
# ワイルドカードインポート禁止
```

## 3. Docstring規約

### 3.1 フォーマット: Googleスタイル（推奨）
```python
def process_data(source: str, threshold: float = 0.5) -> List[Dict]:
    """データを処理し、閾値を超える結果を返す。
    
    この関数は外部APIからデータを取得し、加工して返します。
    エラー発生時はログに記録し、空のリストを返します。
    
    Args:
        source (str): データソースのURL
        threshold (float, optional): フィルタリング閾値. Defaults to 0.5.
        
    Returns:
        List[Dict]: 処理されたデータのリスト
        
    Raises:
        ConnectionError: API接続に失敗した場合
        ValueError: 不正な閾値が指定された場合
        
    Examples:
        >>> data = process_data("http://api.example.com", 0.7)
        >>> len(data) > 0
        True
        
    Note:
        キャッシュを使用するため、同じソースへの連続呼び出しは高速です。
    """
    pass
```

### 3.2 別の選択肢: NumPy/SciPyスタイル
```python
def calculate_statistics(data: np.ndarray) -> Dict[str, float]:
    """
    データの統計量を計算する。
    
    Parameters
    ----------
    data : np.ndarray
        入力データ配列。1次元または2次元。
    
    Returns
    -------
    Dict[str, float]
        統計量の辞書。以下のキーを含む:
        - 'mean': 平均値
        - 'std': 標準偏差
        - 'min': 最小値
        - 'max': 最大値
    
    Raises
    ------
    ValueError
        入力データが空の場合。
    """
    pass
```

### 3.3 クラスDocstring
```python
class DataProcessor:
    """データ処理パイプラインの基底クラス。
    
    このクラスは様々なデータソースからのデータを処理するための
    共通インターフェースを提供します。
    
    Attributes:
        config (Dict): プロセッサ設定
        logger (Logger): ロギングインスタンス
        cache (Cache): キャッシュインスタンス
        
    Examples:
        >>> processor = DataProcessor(config={"timeout": 30})
        >>> result = processor.process("data.csv")
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """DataProcessorの初期化。
        
        Args:
            config: 設定辞書
        """
        self.config = config or {}
```

### 3.4 モジュールDocstring
```python
"""
データ処理モジュール。

このモジュールは、様々なデータソースからのデータを処理するための
クラスと関数を提供します。主な機能:
- データの読み込みと検証
- データの変換と加工
- 処理結果の出力

使用方法:
    >>> from data_processor import DataProcessor
    >>> processor = DataProcessor()
    >>> processor.load("data.csv")

注意事項:
    このモジュールはPython 3.8以上を必要とします。
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"
```

## 4. 型ヒント

### 4.1 基本規則
```python
from typing import List, Dict, Tuple, Optional, Union, Any, Callable

def process_items(
    items: List[str],
    weights: Optional[Dict[str, float]] = None,
    callback: Callable[[str], bool] = None
) -> Tuple[List[str], int]:
    """型ヒントの例"""
    pass

# Python 3.9+ では built-in types が使用可能
def process_items_v2(
    items: list[str],
    weights: dict[str, float] | None = None
) -> tuple[list[str], int]:
    pass
```

### 4.2 複雑な型定義
```python
from typing import TypeVar, Generic
from dataclasses import dataclass
from pydantic import BaseModel

T = TypeVar('T')

class Response(BaseModel):
    """APIレスポンス用モデル"""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]

@dataclass
class ProcessingResult:
    """処理結果データクラス"""
    input_data: List[str]
    output_data: List[Dict]
    processing_time: float
    success: bool = True
```

## 5. エラー処理

### 5.1 例外定義
```python
class ProjectBaseError(Exception):
    """プロジェクト基底例外"""
    pass

class DataValidationError(ProjectBaseError):
    """データ検証エラー"""
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)

class APIConnectionError(ProjectBaseError):
    """API接続エラー"""
    pass
```

### 5.2 例外処理パターン
```python
def safe_operation():
    try:
        result = risky_operation()
    except DataValidationError as e:
        logger.warning(f"Validation failed: {e}")
        return None
    except (APIConnectionError, TimeoutError) as e:
        logger.error(f"Connection failed: {e}")
        raise  # 上位レイヤーで処理させる
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise ProjectBaseError(f"Operation failed: {e}") from e
    else:
        logger.debug(f"Operation succeeded: {result}")
        return result
    finally:
        cleanup_resources()
```

## 6. テストコード規約

### 6.1 テスト構造
```python
# tests/test_module/test_feature.py
import pytest
from unittest.mock import Mock, patch

class TestDataProcessor:
    """DataProcessorクラスのテスト"""
    
    @pytest.fixture
    def processor(self):
        """テスト用プロセッサのフィクスチャ"""
        return DataProcessor(config={"test_mode": True})
    
    def test_process_valid_data(self, processor):
        """有効なデータ処理テスト"""
        # Arrange
        test_data = ["item1", "item2"]
        
        # Act
        result = processor.process(test_data)
        
        # Assert
        assert len(result) == 2
        assert "processed" in result[0]
    
    @pytest.mark.parametrize("input_data,expected", [
        ([1, 2, 3], 6),
        ([], 0),
        ([10], 10),
    ])
    def test_calculate_sum(self, input_data, expected):
        """パラメータ化テスト"""
        result = calculate_sum(input_data)
        assert result == expected
```

## 7. ディレクトリ構成例
```
project/
├── src/
│   ├── package/
│   │   ├── __init__.py
│   │   ├── core/
│   │   ├── utils/
│   │   └── models/
│   └── scripts/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── .pre-commit-config.yaml
├── pyproject.toml
├── setup.cfg
├── requirements.txt
└── README.md
```

## 8. 設定ファイル例

### pyproject.toml (black, isort, mypy用)
```toml
[tool.black]
line-length = 100
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

## 9. コードレビュー指針

### チェックリスト
- [ ] Docstringが適切に書かれているか
- [ ] 型ヒントが適切か
- [ ] エラー処理は適切か
- [ ] テストが書かれているか
- [ ] パフォーマンス上の問題はないか
- [ ] セキュリティ上の懸念はないか
- [ ] ロギングは適切か

## 10. ベストプラクティス追加項目

### 10.1 ロギング
```python
import logging
from logging.config import dictConfig

# 構造化ロギングの推奨
logger = logging.getLogger(__name__)

def process_with_logging():
    logger.info("処理を開始", extra={"step": "start"})
    try:
        result = do_work()
        logger.info("処理成功", extra={"result_count": len(result)})
        return result
    except Exception:
        logger.exception("処理失敗")
        raise
```

### 10.2 設定管理
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """設定管理クラス"""
    api_url: str
    timeout: int = 30
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

---

この規約はプロジェクトの規模やチームの好みに応じて調整してください。重要なのは**一貫性を保つこと**です。新しいメンバーが参加した際には、この規約とともにプロジェクトのコードベースをレビューする時間を設けることを推奨します。
