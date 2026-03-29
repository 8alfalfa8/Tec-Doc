#!/usr/bin/env python3
"""
Markdown 目次（TOC）自動生成・更新スクリプト

機能:
  - 指定された見出しレベルをベースに目次を生成
  - <a id="index"></a> タグを目次セクションに挿入
  - 各対象セクションの末尾に「目次に戻る」リンクを追加
  - 既存の目次・「目次に戻る」を検出して上書き更新

使用方法:
  python update_toc.py --files "file1.md file2.md" --level 2 --back-label "🔙 目次に戻る"
"""

import re
import sys
import argparse
import unicodedata
from pathlib import Path


# ─── 定数 ───────────────────────────────────────────────────────────────────
TOC_ANCHOR      = "index"
TOC_START_MARK  = "<!-- TOC_START -->"
TOC_END_MARK    = "<!-- TOC_END -->"
BACK_LINK_RE    = re.compile(
    r'\[.*?目次.*?\]\(#index\)'
    r'|'
    r'\[.*?Back.*?\]\(#index\)',
    re.IGNORECASE
)
HR_RE = re.compile(r'^---+\s*$')


# ─── ユーティリティ ─────────────────────────────────────────────────────────
def slugify(text: str) -> str:
    """
    GitHub 互換のアンカーIDを生成する。
    - 英小文字化
    - スペース → ハイフン
    - 記号除去（ただし日本語・漢字・ひらがな・カタカナはそのまま残す）
    """
    text = text.strip()
    # インライン要素（コード、リンク）を除去
    text = re.sub(r'`[^`]*`', '', text)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # HTML タグ除去
    text = re.sub(r'<[^>]+>', '', text)
    # 小文字化
    text = text.lower()
    # スペース → ハイフン
    text = text.replace(' ', '-')
    # 記号のうち ASCII 範囲のみ除去（日本語文字は保持）
    result = []
    for ch in text:
        cat = unicodedata.category(ch)
        if ch in ('-', '_'):
            result.append(ch)
        elif ch.isdigit() or ch.isalpha():
            result.append(ch)
        elif cat.startswith('L') or cat.startswith('N'):
            # Unicode 文字（漢字、ひらがな等）
            result.append(ch)
        # その他の記号は除去
    return ''.join(result)


def heading_text(line: str) -> str:
    """行から見出しテキストを抽出（<a> タグなど HTML を除去）"""
    text = re.sub(r'<[^>]+>', '', line).strip()
    # マークダウンのインライン要素を平文化
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    return text.strip()


# ─── 目次生成 ────────────────────────────────────────────────────────────────
def parse_headings(lines: list[str], base_level: int) -> list[dict]:
    """
    base_level 以上の見出しを抽出する。
    戻り値: [{"level": int, "text": str, "anchor": str}, ...]
    """
    headings = []
    in_code_block = False

    for line in lines:
        # コードブロック内はスキップ
        if line.startswith('```') or line.startswith('~~~'):
            in_code_block = not in_code_block
        if in_code_block:
            continue

        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if not m:
            continue
        level = len(m.group(1))
        if level < base_level:
            continue

        raw_text = m.group(2)
        text = heading_text(raw_text)
        # 目次セクション自体はスキップ
        if re.search(r'目次|table of contents', text, re.IGNORECASE):
            continue

        anchor = slugify(text)
        headings.append({"level": level, "text": text, "anchor": anchor})

    return headings


def build_toc_lines(headings: list[dict], base_level: int) -> list[str]:
    """目次の Markdown 行リストを生成する"""
    lines = []
    for h in headings:
        indent = "  " * (h["level"] - base_level)
        lines.append(f"{indent}- [{h['text']}](#{h['anchor']})")
    return lines


# ─── ファイル書き換え ─────────────────────────────────────────────────────────
def find_toc_section(lines: list[str]) -> tuple[int, int] | None:
    """
    既存の目次セクションを探す。
    マーカーコメント優先、なければ '<a id="index">' を含む ## 見出しを探す。
    戻り値: (開始行インデックス, 終了行インデックス+1) or None
    """
    # マーカーで囲まれた範囲
    start = end = None
    for i, line in enumerate(lines):
        if TOC_START_MARK in line:
            start = i
        elif TOC_END_MARK in line and start is not None:
            end = i + 1
            return start, end

    # マーカーなし → <a id="index"> を含む行を探す
    for i, line in enumerate(lines):
        if f'<a id="{TOC_ANCHOR}">' in line or f"<a id='{TOC_ANCHOR}'>" in line:
            # 見出し行を探す（前後1行）
            for j in range(max(0, i - 1), min(len(lines), i + 2)):
                if re.match(r'^#+\s', lines[j]):
                    start = j
                    break
            else:
                start = i

            # 次の ## 見出しか --- の前まで
            for k in range(start + 1, len(lines)):
                if re.match(r'^##\s', lines[k]) and not re.search(r'目次|index', lines[k], re.IGNORECASE):
                    end = k
                    break
                if HR_RE.match(lines[k]) and k > start + 2:
                    end = k + 1
                    break
            else:
                end = len(lines)
            return start, end

    return None


def remove_back_links(lines: list[str], back_label: str) -> list[str]:
    """既存の「目次に戻る」リンク行（前後の --- も含む）を除去する"""
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        is_back = BACK_LINK_RE.search(line) or (
            back_label and back_label.replace('🔙 ', '') in line and '#index' in line
        )
        if is_back:
            # 直前の空行 / --- を除去
            while result and result[-1].strip() in ('', '---'):
                result.pop()
            i += 1
            # 直後の空行 / --- をスキップ
            while i < len(lines) and lines[i].strip() in ('', '---'):
                i += 1
            continue
        result.append(lines[i])
        i += 1
    return result


def insert_back_links(
    lines: list[str],
    headings: list[dict],
    base_level: int,
    back_label: str,
    back_link: str,
) -> list[str]:
    """
    base_level の見出し（目次除く）それぞれのセクション末尾に
    「目次に戻る」リンクを挿入する。
    """
    # base_level の見出し行インデックスを収集
    top_heading_indices = []
    in_code = False
    for i, line in enumerate(lines):
        if line.startswith('```') or line.startswith('~~~'):
            in_code = not in_code
        if in_code:
            continue
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m and len(m.group(1)) == base_level:
            text = heading_text(m.group(2))
            if not re.search(r'目次|table of contents', text, re.IGNORECASE):
                top_heading_indices.append(i)

    if not top_heading_indices:
        return lines

    result = list(lines)
    offset = 0  # 挿入によるインデックスずれ

    for idx, heading_idx in enumerate(top_heading_indices):
        adjusted = heading_idx + offset
        # 次の同レベル見出し or ファイル末尾
        if idx + 1 < len(top_heading_indices):
            next_idx = top_heading_indices[idx + 1] + offset
        else:
            next_idx = len(result)

        # セクション末尾（次の見出しの直前）を探す
        insert_pos = next_idx
        # 末尾の空行・--- をスキップして手前に挿入
        while insert_pos > adjusted + 1 and result[insert_pos - 1].strip() in ('', '---'):
            insert_pos -= 1

        back_lines = [
            '\n',
            f'[{back_label}](#{TOC_ANCHOR})\n',
            '\n',
        ]
        result[insert_pos:insert_pos] = back_lines
        offset += len(back_lines)

    return result


def update_file(
    path: Path,
    base_level: int,
    back_label: str,
) -> bool:
    """
    ファイルを読み込み、目次と「目次に戻る」を更新して上書き保存する。
    変更があった場合 True を返す。
    """
    original = path.read_text(encoding='utf-8')
    lines = original.splitlines(keepends=True)

    # 見出しを解析
    headings = parse_headings(lines, base_level)
    if not headings:
        print(f"  → 見出し（レベル {base_level}+）が見つかりません。スキップ: {path}")
        return False

    # ① 既存の「目次に戻る」を除去
    lines = remove_back_links(lines, back_label)

    # ② 目次セクションを構築
    toc_content_lines = build_toc_lines(headings, base_level)

    toc_block = (
        [f'## <a id="{TOC_ANCHOR}"></a>📖 目次\n', '\n']
        + [l + '\n' for l in toc_content_lines]
        + ['\n']
    )

    # ③ 既存の目次を探して置換 or 先頭 ## 見出しの前に挿入
    toc_range = find_toc_section(lines)
    if toc_range:
        start, end = toc_range
        # 前後の --- を含めて置換範囲を調整
        new_start = start
        if new_start > 0 and HR_RE.match(lines[new_start - 1]):
            new_start -= 1
        new_end = end
        if new_end < len(lines) and HR_RE.match(lines[new_end]):
            new_end += 1

        lines = lines[:new_start] + ['\n---\n\n'] + toc_block + ['---\n', '\n'] + lines[new_end:]
    else:
        # 最初の ## 見出し (base_level) の直前に挿入
        insert_idx = None
        for i, line in enumerate(lines):
            if re.match(r'^#{%d}\s' % base_level, line):
                insert_idx = i
                break
        if insert_idx is None:
            insert_idx = 0

        lines = lines[:insert_idx] + ['\n---\n\n'] + toc_block + ['---\n', '\n'] + lines[insert_idx:]

    # ④ 「目次に戻る」を挿入
    lines = insert_back_links(lines, headings, base_level, back_label, f'[{back_label}](#{TOC_ANCHOR})')

    new_content = ''.join(lines)

    if new_content == original:
        print(f"  → 変更なし: {path}")
        return False

    path.write_text(new_content, encoding='utf-8')
    print(f"  → 更新完了: {path}")
    return True


# ─── エントリーポイント ───────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Markdown 目次自動生成・更新')
    parser.add_argument('--files',      default='', help='スペース区切りの対象ファイルパス')
    parser.add_argument('--level',      type=int, default=2, help='目次の基準見出しレベル（デフォルト: 2）')
    parser.add_argument('--back-label', default='🔙 目次に戻る', help='「目次に戻る」リンクのラベル')
    parser.add_argument('--exclude',    default='', help='除外ファイルパターン（カンマ区切り）')
    args = parser.parse_args()

    file_list = [f.strip() for f in args.files.split() if f.strip()]
    exclude_list = [e.strip() for e in args.exclude.split(',') if e.strip()]

    if not file_list:
        print("対象ファイルが指定されていません。")
        sys.exit(0)

    updated = 0
    for file_str in file_list:
        path = Path(file_str)
        if not path.exists() or path.suffix.lower() != '.md':
            continue
        # 除外チェック
        if any(path.match(ex) or path.name == ex for ex in exclude_list):
            print(f"  → 除外: {path}")
            continue
        print(f"処理中: {path}")
        if update_file(path, args.level, args.back_label):
            updated += 1

    print(f"\n完了: {updated} ファイルを更新しました。")


if __name__ == '__main__':
    main()
