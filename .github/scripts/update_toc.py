#!/usr/bin/env python3
"""
Markdownファイルの目次を自動生成・更新するスクリプト
- 目次は最初の見出し項目の先頭に配置
- 「目次に戻る」リンクは各見出しセクションの最後に配置
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional


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
    
    def extract_headings(self, content: str) -> List[Tuple[int, str, str, int]]:
        """
        Markdownから見出しを抽出する
        
        Args:
            content: Markdownの内容
            
        Returns:
            (レベル, 見出しテキスト, アンカーID, 開始行番号) のリスト
        """
        headings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
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
                        # テキストからIDを生成
                        anchor_id = heading_text.lower()
                        anchor_id = re.sub(r'[^\w\s-]', '', anchor_id)
                        anchor_id = re.sub(r'[\s]+', '-', anchor_id)
                        anchor_id = re.sub(r'[-]+', '-', anchor_id)
                        anchor_id = anchor_id.strip('-')
                    
                    headings.append((level, heading_text, anchor_id, i))
        
        return headings
    
    def find_section_end(self, lines: List[str], start_idx: int, headings: List[Tuple[int, int]]) -> int:
        """
        見出しセクションの終了位置を特定する
        
        Args:
            lines: 全行のリスト
            start_idx: セクション開始位置（見出し行のインデックス）
            headings: (レベル, 開始位置) のリスト
            
        Returns:
            セクション終了位置（次の見出しの直前、またはファイルの終端）
        """
        current_level = None
        for i in range(len(headings)):
            if headings[i][1] == start_idx:
                current_level = headings[i][0]
                # 次の見出しを探す
                for j in range(i + 1, len(headings)):
                    if headings[j][0] <= current_level:
                        return headings[j][1] - 1
                break
        
        # 次の見出しが見つからない場合はファイルの終端
        return len(lines) - 1
    
    def generate_toc(self, headings: List[Tuple[int, str, str, int]]) -> str:
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
        
        for level, text, anchor_id, _ in headings:
            # インデントを計算
            indent = "  " * (level - self.level_depth)
            # 見出しテキストからHTMLタグを除去
            clean_text = re.sub(r'<[^>]+>', '', text)
            toc_lines.append(f'{indent}- [{clean_text}](#{anchor_id})')
        
        return '\n'.join(toc_lines)
    
    def add_back_to_top_links(self, content: str, headings: List[Tuple[int, str, str, int]]) -> str:
        """
        各見出しセクションの最後に「目次に戻る」リンクを追加する
        
        Args:
            content: Markdownの内容
            headings: 見出し情報のリスト
            
        Returns:
            リンクが追加されたMarkdown文字列
        """
        lines = content.split('\n')
        
        # 各見出しのレベルと位置を抽出
        heading_positions = [(level, pos) for level, _, _, pos in headings]
        
        # セクションの終了位置を特定
        sections = []
        for i, (level, start_pos) in enumerate(heading_positions):
            # 次の見出しを探す
            end_pos = len(lines) - 1
            for j in range(i + 1, len(heading_positions)):
                if heading_positions[j][0] <= level:
                    end_pos = heading_positions[j][1] - 1
                    break
            sections.append((start_pos, end_pos))
        
        # 各セクションの最後にリンクを追加
        # 後ろから追加していく（インデックスがずれるのを防ぐ）
        for start_pos, end_pos in reversed(sections):
            # セクションの終了位置を見つける（次の見出しの直前）
            # 空行を考慮して、適切な位置に挿入
            insert_pos = end_pos
            
            # 終了位置以降の空行をスキップして、実際のコンテンツの最後を探す
            while insert_pos >= start_pos and lines[insert_pos].strip() == '':
                insert_pos -= 1
            
            # リンクを追加（セクションの最後に）
            if insert_pos >= start_pos:
                # リンク行と空行を追加
                lines.insert(insert_pos + 1, '')
                lines.insert(insert_pos + 2, self.back_to_top_text)
                lines.insert(insert_pos + 3, '')
        
        return '\n'.join(lines)
    
    def find_first_heading_position(self, content: str) -> Optional[int]:
        """
        最初の見出しの位置を検索する
        
        Args:
            content: Markdownの内容
            
        Returns:
            最初の見出しの開始位置（文字インデックス）、見つからない場合はNone
        """
        match = re.search(r'^(#{1,6})\s+', content, re.MULTILINE)
        return match.start() if match else None
    
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
            
            # 最初の見出しの位置を取得
            first_heading_pos = self.find_first_heading_position(content)
            
            if first_heading_pos is None:
                print(f"  ⚠️  {filepath.name}: 見出しが見つかりません")
                return False
            
            # 既存の目次を削除または置き換え
            if self.toc_start_marker in content and self.toc_end_marker in content:
                # マーカーがある場合：マーカー間の内容を置き換え
                pattern = f'{re.escape(self.toc_start_marker)}.*?{re.escape(self.toc_end_marker)}'
                replacement = f'{self.toc_start_marker}\n{new_toc}\n{self.toc_end_marker}'
                content_with_toc = re.sub(pattern, replacement, content, flags=re.DOTALL)
            else:
                # マーカーがない場合：最初の見出しの直前に挿入
                toc_block = f'{self.toc_start_marker}\n{new_toc}\n{self.toc_end_marker}\n\n'
                content_with_toc = (
                    content[:first_heading_pos] + 
                    toc_block + 
                    content[first_heading_pos:]
                )
            
            # 「目次に戻る」リンクを追加
            updated_content = self.add_back_to_top_links(content_with_toc, headings)
            
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
    print("📌 設定: 目次は最初の見出しの直前に配置")
    print("📌 設定: 「目次に戻る」リンクは各見出しセクションの最後に配置")
    
    updater = MarkdownTOCUpdater(heading_level=heading_level)
    updater.process_all_markdown_files()


if __name__ == '__main__':
    main()
