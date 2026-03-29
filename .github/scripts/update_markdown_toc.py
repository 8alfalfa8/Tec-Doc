#!/usr/bin/env python3
"""
Markdownファイルの目次を自動更新するスクリプト
GitHub Actionsから呼び出されることを想定
"""

import os
import re
import sys
from pathlib import Path


# 設定（デフォルト値）
DEFAULT_CONFIG = {
    'heading_level': '##',  # 目次対象の見出しレベル
    'toc_marker_start': '<!-- toc -->',
    'toc_marker_end': '<!-- tocstop -->',
    'back_to_toc': '[🔙 目次に戻る](#index)',
    'toc_title': '📖 目次',
}


def load_config():
    """設定を読み込む（環境変数またはデフォルト値）"""
    config = DEFAULT_CONFIG.copy()
    
    # 環境変数から上書き
    if os.environ.get('HEADING_LEVEL'):
        config['heading_level'] = os.environ['HEADING_LEVEL']
    
    return config


def extract_headings(content, heading_level):
    """指定されたレベルの見出しを抽出"""
    # 見出しパターン（例: ## 見出し）
    pattern = rf'^{re.escape(heading_level)}\s+(.+)$'
    headings = []
    
    for line in content.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            title = match.group(1).strip()
            # アンカーIDを生成
            anchor_id = title.lower()
            anchor_id = re.sub(r'[^\w\u3000-\u30FF\u3040-\u309F\u4E00-\u9FFF]+', '-', anchor_id)
            anchor_id = re.sub(r'[-]+', '-', anchor_id).strip('-')
            headings.append((title, anchor_id))
    
    return headings


def generate_toc(headings, config):
    """目次を生成"""
    if not headings:
        return ""
    
    toc_lines = [f"{config['heading_level']} {config['toc_title']}", ""]
    
    for title, anchor_id in headings:
        # 番号を除去してリンクテキストを作成
        # 例: "1. オブジェクト指向プログラミング" -> "1 オブジェクト指向プログラミング"
        link_text = re.sub(r'^(\d+)\.\s+', r'\1 ', title)
        toc_lines.append(f"- [{link_text}](#{anchor_id})")
    
    return "\n".join(toc_lines)


def add_back_to_toc_links(content, headings, back_link):
    """各見出しセクションの最後に「目次に戻る」リンクを追加"""
    lines = content.split('\n')
    result = []
    i = 0
    section_start = None
    current_heading = None
    
    while i < len(lines):
        line = lines[i]
        
        # 見出し行を検出
        if re.match(rf'^{re.escape(HEADING_LEVEL)}\s+', line.strip()):
            # 前のセクションが終了した場合、戻るリンクを追加
            if section_start is not None and current_heading is not None:
                # セクション内に既に戻るリンクがあるか確認
                section_content = '\n'.join(result[section_start:i])
                if back_link not in section_content:
                    # セクションの最後に戻るリンクを追加
                    if i > 0 and lines[i-1].strip() == '':
                        result.insert(i-1, back_link)
                        result.insert(i-1, '')
                        i += 2
                    else:
                        result.insert(i, back_link)
                        result.insert(i, '')
                        i += 2
            
            section_start = i
            current_heading = line
        
        result.append(line)
        i += 1
    
    # 最後のセクションに戻るリンクを追加
    if section_start is not None and current_heading is not None:
        section_content = '\n'.join(result[section_start:])
        if back_link not in section_content:
            if result and result[-1].strip() == '':
                result.insert(-1, back_link)
                result.insert(-1, '')
            else:
                result.append('')
                result.append(back_link)
                result.append('')
    
    return '\n'.join(result)


def update_markdown_toc(file_path, config):
    """Markdownファイルの目次を更新"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 既存の目次を検出して削除
        toc_pattern = rf'{re.escape(config["toc_marker_start"])}.*?{re.escape(config["toc_marker_end"])}'
        toc_section = re.search(toc_pattern, content, re.DOTALL)
        
        if toc_section:
            content = re.sub(toc_pattern, '', content, flags=re.DOTALL)
            content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 見出しを抽出
        headings = extract_headings(content, config['heading_level'])
        
        if not headings:
            print(f"  ⚠️ 見出しが見つかりません: {file_path}")
            return False
        
        # 新しい目次を生成
        new_toc = generate_toc(headings, config)
        
        # 目次を配置（最初の対象見出しの前に挿入）
        heading_pattern = rf'^{re.escape(config["heading_level"])}\s+'
        heading_match = re.search(heading_pattern, content, re.MULTILINE)
        
        if heading_match:
            insert_pos = heading_match.start()
            
            # アンカー用のindexを追加
            index_anchor = '<a id="index"></a>\n'
            
            # 目次セクションを作成
            if toc_section:
                toc_section_content = f"{config['toc_marker_start']}\n{new_toc}\n{config['toc_marker_end']}"
            else:
                toc_section_content = f"{new_toc}"
            
            new_content = (content[:insert_pos] + 
                         index_anchor + 
                         toc_section_content + 
                         "\n\n" + 
                         content[insert_pos:])
            
            # 各見出しセクションに「目次に戻る」を追加
            new_content = add_back_to_toc_links(new_content, headings, config['back_to_toc'])
            
            # ファイルに書き戻し
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ 更新完了: {file_path}")
            return True
        else:
            print(f"  ⚠️ 対象の見出しが見つかりません: {file_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ エラー: {file_path} - {str(e)}")
        return False


def main():
    """メイン処理"""
    # 設定を読み込み
    config = load_config()
    global HEADING_LEVEL  # 関数内で使用するため
    HEADING_LEVEL = config['heading_level']
    
    # 変更されたMarkdownファイルを取得
    changed_files = os.popen('git diff --name-only HEAD~1 HEAD').read().strip().split('\n')
    md_files = [f for f in changed_files if f.endswith('.md') and os.path.exists(f)]
    
    if not md_files:
        print("📝 変更されたMarkdownファイルはありません")
        sys.exit(0)
    
    print(f"📝 処理対象ファイル: {', '.join(md_files)}")
    print(f"⚙️  見出しレベル: {config['heading_level']}")
    print()
    
    updated = 0
    for md_file in md_files:
        print(f"📄 処理中: {md_file}")
        if update_markdown_toc(md_file, config):
            updated += 1
        print()
    
    print(f"✨ 完了: {updated}/{len(md_files)} ファイルを更新しました")
    
    # 更新があれば環境変数を設定
    if updated > 0:
        with open(os.environ['GITHUB_ENV'], 'a') as f:
            f.write('UPDATED=true\n')


if __name__ == "__main__":
    main()