#!/usr/bin/env python3
"""
Markdownファイルの目次を自動生成・更新するスクリプト
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


# ==================== 設定 ====================
# デフォルトの見出しレベル（'##' または '###' など）
DEFAULT_HEADING_LEVEL = '##'

# 目次のアンカーID（HTMLアンカー）
TOC_ANCHOR_ID = 'index'

# 目次に戻るリンクのテキスト
BACK_TO_TOC_TEXT = '[🔙 目次に戻る](#{})'.format(TOC_ANCHOR_ID)

# 見出しのパターン（マークダウン）
HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)


# ==================== 関数 ====================

def extract_headings(content: str, min_level: int, max_level: int) -> List[Tuple[int, str, str]]:
    """
    指定されたレベルの見出しを抽出する
    戻り値: [(レベル, 見出しテキスト, アンカーID), ...]
    """
    headings = []
    lines = content.split('\n')
    
    for line in lines:
        match = HEADING_PATTERN.match(line)
        if match:
            level = len(match.group(1))  # #の数
            if min_level <= level <= max_level:
                heading_text = match.group(2).strip()
                # アンカーIDを生成
                anchor_id = generate_anchor_id(heading_text)
                headings.append((level, heading_text, anchor_id))
    
    return headings


def generate_anchor_id(text: str) -> str:
    """
    見出しテキストからアンカーIDを生成する
    """
    text = text.strip()
    
    # 先頭の数字とピリオドを処理（例: "1. " を "1-" に）
    match = re.match(r'^(\d+)\.\s+(.+)$', text)
    if match:
        num = match.group(1)
        rest = match.group(2)
        # 数字部分はそのまま、残りはハイフン変換
        rest_id = re.sub(r'[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\-]+', '-', rest)
        rest_id = re.sub(r'-+', '-', rest_id).strip('-')
        return f"{num}-{rest_id}" if rest_id else num
    
    # 通常の変換
    anchor = re.sub(r'[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\-]+', '-', text)
    anchor = re.sub(r'-+', '-', anchor).strip('-')
    return anchor.lower()


def generate_toc(headings: List[Tuple[int, str, str]], base_level: int) -> str:
    """
    見出しリストから目次を生成する
    base_level: 目次に含める最小の見出しレベル（#の数）
    """
    if not headings:
        return ""
    
    toc_lines = []
    toc_lines.append(f'## <a id="{TOC_ANCHOR_ID}"></a>📖 目次')
    toc_lines.append('')
    
    # 階層構造を表現
    for level, text, anchor_id in headings:
        # インデント計算（現在のレベルに基づく）
        indent = level - base_level
        indent_str = '  ' * indent
        
        # 目次エントリ
        toc_lines.append(f'{indent_str}- [{text}](#{anchor_id})')
    
    toc_lines.append('')
    toc_lines.append('---')
    toc_lines.append('')
    
    return '\n'.join(toc_lines)


def insert_back_to_toc(content: str, headings: List[Tuple[int, str, str]], 
                       base_level: int, max_level: int) -> str:
    """
    各セクションの末尾に「目次に戻る」リンクを挿入する
    """
    lines = content.split('\n')
    new_lines = []
    
    # 見出しの位置を記録
    heading_positions = []
    for j, line in enumerate(lines):
        match = HEADING_PATTERN.match(line)
        if match:
            level = len(match.group(1))
            if base_level <= level <= max_level:
                heading_positions.append((j, level, match.group(2)))
    
    if not heading_positions:
        return content
    
    # 各見出しセクションの終了位置を特定
    section_ends = []
    for idx, (pos, level, text) in enumerate(heading_positions):
        # 次の見出しの位置を探す（同じレベル以上の見出しが出現するまで）
        next_pos = len(lines)
        for next_idx in range(idx + 1, len(heading_positions)):
            next_level = heading_positions[next_idx][1]
            if next_level <= level:  # 同じレベル以上の見出しで終了
                next_pos = heading_positions[next_idx][0]
                break
        section_ends.append((pos, next_pos, level, text))
    
    # セクションの末尾に「目次に戻る」を追加
    i = 0
    last_end = 0
    for pos, end_pos, level, text in section_ends:
        # 前のセクションから現在の見出しまでを追加
        new_lines.extend(lines[last_end:pos])
        
        # 見出し行を追加
        new_lines.append(lines[pos])
        i = pos + 1
        
        # セクション内のコンテンツを追加
        section_content = lines[i:end_pos]
        
        # セクションの最後の非空行を探す
        if section_content:
            # 末尾の空行を除去
            while section_content and section_content[-1].strip() == '':
                section_content.pop()
            
            # 「目次に戻る」リンクが既にあるかチェック
            has_back_link = False
            for line in section_content:
                if BACK_TO_TOC_TEXT in line:
                    has_back_link = True
                    break
            
            if not has_back_link:
                # セクションの末尾に「目次に戻る」を追加
                section_content.append('')
                section_content.append(BACK_TO_TOC_TEXT)
                section_content.append('')
            
            new_lines.extend(section_content)
        
        last_end = end_pos
        i = end_pos
    
    # 残りのコンテンツを追加
    new_lines.extend(lines[last_end:])
    
    return '\n'.join(new_lines)


def find_toc_position(content: str) -> Optional[int]:
    """
    既存の目次セクションの位置を探す
    戻り値: 目次セクションの開始行インデックス（見つからない場合はNone）
    """
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if f'<a id="{TOC_ANCHOR_ID}"></a>' in line and '目次' in line:
            return i
    return None


def process_markdown_file(filepath: str, min_level: int, max_level: int) -> bool:
    """
    マークダウンファイルを処理し、目次を生成・挿入する
    戻り値: 変更があったかどうか
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 見出しを抽出
    headings = extract_headings(content, min_level, max_level)
    
    if not headings:
        print(f"  {filepath}: 該当する見出しがありません")
        return False
    
    # 新しい目次を生成
    new_toc = generate_toc(headings, min_level)
    
    # 既存の目次を探す
    toc_start = find_toc_position(content)
    
    if toc_start is not None:
        # 既存の目次を置き換える
        lines = content.split('\n')
        
        # 目次セクションの終了位置を探す（次の見出しまたは「---」まで）
        toc_end = toc_start
        for i in range(toc_start + 1, len(lines)):
            if lines[i].startswith('#') or lines[i].strip() == '---':
                toc_end = i
                break
            toc_end = i + 1
        
        # 目次セクションを置き換え
        new_lines = lines[:toc_start] + new_toc.split('\n') + lines[toc_end:]
        content = '\n'.join(new_lines)
    else:
        # 目次がない場合、ファイルの先頭付近に挿入
        lines = content.split('\n')
        insert_pos = 0
        
        # YAMLフロントマターがある場合はその後に挿入
        if lines and lines[0].strip() == '---':
            yaml_end = 1
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    yaml_end = i + 1
                    break
            insert_pos = yaml_end
        else:
            # 最初の見出しを探す
            for i, line in enumerate(lines):
                if HEADING_PATTERN.match(line):
                    insert_pos = i
                    break
        
        # 目次を挿入
        lines.insert(insert_pos, new_toc)
        content = '\n'.join(lines)
    
    # 「目次に戻る」リンクを挿入
    content = insert_back_to_toc(content, headings, min_level, max_level)
    
    # 変更があれば保存
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ {filepath}: 更新しました")
        return True
    else:
        print(f"  {filepath}: 変更はありません")
        return False


def parse_heading_level(level_str: str) -> Tuple[int, int]:
    """
    見出しレベル指定をパースする
    戻り値: (min_level, max_level)
    """
    if ',' in level_str:
        parts = level_str.split(',')
        min_level = int(parts[0].strip())
        max_level = int(parts[1].strip()) if len(parts) > 1 else min_level
        return min_level, max_level
    
    # #の数で指定（例: "##"）
    level_str = level_str.strip()
    if level_str.startswith('#'):
        level = len(level_str)
        return level, level
    
    # 数字で指定
    level = int(level_str)
    return level, level


def get_target_files(target_pattern: str, exclude_pattern: str, changed_files: str = None) -> List[str]:
    """
    処理対象のファイルリストを取得する
    """
    if changed_files:
        # 変更されたファイルのみ処理
        files = [f for f in changed_files.split('\n') if f and f.endswith('.md')]
    else:
        # すべてのマークダウンファイルを処理
        import glob
        files = glob.glob(target_pattern, recursive=True)
    
    # 除外パターンがある場合
    if exclude_pattern:
        exclude_patterns = [p.strip() for p in exclude_pattern.split(',')]
        files = [f for f in files 
                 if not any(f.endswith(p) or p in f for p in exclude_patterns)]
    
    return files


def main():
    """メイン関数"""
    # 環境変数から設定を読み込む
    heading_level = os.environ.get('INPUT_HEADING_LEVEL', DEFAULT_HEADING_LEVEL)
    target_pattern = os.environ.get('INPUT_TARGET_PATTERN', '**/*.md')
    exclude_pattern = os.environ.get('INPUT_EXCLUDE_PATTERN', '')
    changed_files = os.environ.get('CHANGED_FILES', '')
    
    # 見出しレベルをパース
    min_level, max_level = parse_heading_level(heading_level)
    
    print(f"見出しレベル: {min_level} 以上 {max_level} 以下")
    print(f"対象パターン: {target_pattern}")
    
    # 処理対象ファイルを取得
    files_to_process = get_target_files(target_pattern, exclude_pattern, changed_files)
    
    print(f"\n処理対象ファイル: {len(files_to_process)}件")
    
    updated_files = []
    for filepath in files_to_process:
        if os.path.isfile(filepath):
            if process_markdown_file(filepath, min_level, max_level):
                updated_files.append(filepath)
    
    # 更新されたファイルがある場合は結果を出力
    if updated_files:
        print(f"\n更新されたファイル: {len(updated_files)}件")
        for f in updated_files:
            print(f"  - {f}")
        
        # GitHub Actionsの出力に設定
        github_output = os.environ.get('GITHUB_OUTPUT')
        if github_output:
            with open(github_output, 'a') as f:
                f.write(f"updated_files={','.join(updated_files)}\n")
    else:
        print("\n更新されたファイルはありません")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
