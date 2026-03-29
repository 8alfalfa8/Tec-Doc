#!/usr/bin/env python3
"""
Markdownファイルの目次を自動生成・更新するスクリプト
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import markdown
from bs4 import BeautifulSoup


class MarkdownTOCUpdater:
    """Markdownファイルの目次を更新するクラス"""
    
    def __init__(self, heading_level: str = "##"):
        """
        初期化
        
        Args:
            heading_level: 目次に含める見出しレベル（例: "##", "###"）
        """
        self.heading_level = heading_level
        # 見出しレベルの深さ（#の数）
        self.level_depth = heading_level.count('#')
        
        # 目次の開始/終了マーカー
        self.toc_start_marker = "<!-- TOC_START -->"
        self.toc_end_marker = "<!-- TOC_END -->"
        
        # 目次に戻るリンクのテキスト
        self.back_to_top_text = "[🔙 目次に戻る](#index)"
    
    def extract_headings(self, content: str) -> List[Tuple[int, str, str]]:
        """
        Markdownから見出しを抽出する
        
        Args:
            content: Markdownの内容
            
        Returns:
            (レベル, 見出しテキスト, アンカーID) のリスト
        """
        headings = []
        lines = content.split('\n')
        
        for line in lines:
            # 見出し行を検出
            match = re.match(r'^(#{1,6})\s+(.+?)(?:\s*\{#(.+?)\})?\s*$', line)
            if match:
                level_hash = match.group(1)
                heading_text = match.group(2)
                custom_id = match.group(3)
                
                level = len(level_hash)
                
                # 指定されたレベル以下の見出しのみ対象
                if level >= self.level_depth:
                    # アンカーIDの生成
                    if custom_id:
                        anchor_id = custom_id
                    else:
                        # テキストからIDを生成（小文字化、スペースをハイフンに変換、記号除去）
                        anchor_id = heading_text.lower()
                        anchor_id = re.sub(r'[^\w\s-]', '', anchor_id)
                        anchor_id = re.sub(r'[\s]+', '-', anchor_id)
                        anchor_id = re.sub(r'[-]+', '-', anchor_id)
                        anchor_id = anchor_id.strip('-')
                    
                    headings.append((level, heading_text, anchor_id))
        
        return headings
    
    def generate_toc(self, headings: List[Tuple[int, str, str]]) -> str:
        """
        目次を生成する
        
        Args:
            headings: 見出し情報のリスト
            
        Returns:
            目次のMarkdown文字列
        """
        if not headings:
            return ""
        
        toc_lines = [
            f'<a id="index"></a>📖 目次',
            ''
        ]
        
        current_level = self.level_depth
        
        for level, text, anchor_id in headings:
            # インデントを計算
            indent = "  " * (level - self.level_depth)
            # 見出しテキストからHTMLタグを除去
            clean_text = re.sub(r'<[^>]+>', '', text)
            toc_lines.append(f'{indent}- [{clean_text}](#{anchor_id})')
        
        return '\n'.join(toc_lines)
    
    def add_back_to_top_links(self, content: str, headings: List[Tuple[int, str, str]]) -> str:
        """
        各見出しの後に「目次に戻る」リンクを追加する
        
        Args:
            content: Markdownの内容
            headings: 見出し情報のリスト
            
        Returns:
            リンクが追加されたMarkdown文字列
        """
        lines = content.split('\n')
        new_lines = []
        
        # 見出しの位置を記憶
        heading_positions = []
        for i, line in enumerate(lines):
            match = re.match(r'^(#{1,6})\s+', line)
            if match:
                level = len(match.group(1))
                if level >= self.level_depth:
                    heading_positions.append(i)
        
        # 各見出しの後ろにリンクを追加
        i = 0
        while i < len(lines):
            new_lines.append(lines[i])
            
            # 見出し行の後ろにリンクを追加
            if i in heading_positions:
                # 次の行が空行でない場合は空行を追加
                if i + 1 < len(lines) and lines[i + 1].strip():
                    new_lines.append('')
                new_lines.append(self.back_to_top_text)
                new_lines.append('')
            
            i += 1
        
        return '\n'.join(new_lines)
    
    def update_markdown_file(self, filepath: Path) -> bool:
        """
        Markdownファイルの目次を更新する
        
        Args:
            filepath: Markdownファイルのパス
            
        Returns:
            更新が行われたかどうか
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 見出しを抽出
            headings = self.extract_headings(content)
            
            if not headings:
                print(f"  ⚠️  {filepath.name}: 見出しが見つかりませんでした")
                return False
            
            # 目次を生成
            new_toc = self.generate_toc(headings)
            
            # 既存の目次を置き換え
            if self.toc_start_marker in content and self.toc_end_marker in content:
                # マーカーがある場合：マーカー間の内容を置き換え
                pattern = f'{re.escape(self.toc_start_marker)}.*?{re.escape(self.toc_end_marker)}'
                replacement = f'{self.toc_start_marker}\n{new_toc}\n{self.toc_end_marker}'
                updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            else:
                # マーカーがない場合：最初の見出しの前に挿入
                # 最初の見出しを検索
                first_heading_match = re.search(r'^(#{1,6})\s+', content, re.MULTILINE)
                if first_heading_match:
                    insert_pos = first_heading_match.start()
                    toc_block = f'{self.toc_start_marker}\n{new_toc}\n{self.toc_end_marker}\n\n'
                    updated_content = content[:insert_pos] + toc_block + content[insert_pos:]
                else:
                    # 見出しがない場合は先頭に挿入
                    toc_block = f'{self.toc_start_marker}\n{new_toc}\n{self.toc_end_marker}\n\n'
                    updated_content = toc_block + content
            
            # 「目次に戻る」リンクを追加
            updated_content = self.add_back_to_top_links(updated_content, headings)
            
            # 変更があった場合のみファイルに書き込む
            if updated_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"  ✅ {filepath.name}: 目次を更新しました")
                return True
            else:
                print(f"  ℹ️  {filepath.name}: 変更はありませんでした")
                return False
                
        except Exception as e:
            print(f"  ❌ {filepath.name}: エラーが発生しました - {e}")
            return False
    
    def process_all_markdown_files(self, root_dir: Path = Path('.')) -> None:
        """
        ディレクトリ内のすべてのMarkdownファイルを処理する
        
        Args:
            root_dir: 検索するルートディレクトリ
        """
        md_files = list(root_dir.rglob('*.md'))
        
        # .githubディレクトリ以下は除外
        md_files = [f for f in md_files if '.github' not in str(f)]
        
        print(f"🔍 {len(md_files)}個のMarkdownファイルを検出しました")
        
        updated_count = 0
        for md_file in md_files:
            if self.update_markdown_file(md_file):
                updated_count += 1
        
        print(f"\n📊 更新完了: {updated_count}/{len(md_files)} ファイルが更新されました")


def main():
    """メイン関数"""
    # 環境変数から見出しレベルを取得（デフォルト: "##"）
    heading_level = os.environ.get('TOC_HEADING_LEVEL', '##')
    
    print(f"🚀 目次更新ツールを開始します（見出しレベル: {heading_level}）")
    
    updater = MarkdownTOCUpdater(heading_level=heading_level)
    updater.process_all_markdown_files()


if __name__ == '__main__':
    main()
