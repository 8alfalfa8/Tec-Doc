#!/usr/bin/env python3
"""
Markdown TOC (Table of Contents) updater.
Adds/updates a TOC and "back to TOC" links in Markdown files.
"""

import re
import sys
import argparse
from pathlib import Path


# ── anchor generation ────────────────────────────────────────────────────────

def heading_to_anchor(text: str) -> str:
    """
    GitHub-flavored Markdown heading → anchor slug.
    Rules:
      1. lowercase
      2. keep letters, digits, spaces, hyphens
      3. replace spaces with hyphens
      4. strip leading/trailing hyphens
    """
    text = text.lower()
    # keep Unicode letters/digits, ASCII space and hyphen; drop everything else
    text = re.sub(r'[^\w\s\-]', '', text, flags=re.UNICODE)
    text = re.sub(r'\s+', '-', text.strip())
    text = text.strip('-')
    return text


# ── heading extraction ────────────────────────────────────────────────────────

def extract_headings(lines: list[str], max_level: int) -> list[dict]:
    """
    Return list of {level, text, anchor} for headings up to max_level (## = 2).
    Headings inside fenced code blocks are skipped.
    """
    headings = []
    in_fence = False
    fence_pat = re.compile(r'^\s*(`{3,}|~{3,})')

    for line in lines:
        m = fence_pat.match(line)
        if m:
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        hm = re.match(r'^(#{1,6})\s+(.*)', line)
        if not hm:
            continue
        level = len(hm.group(1))
        if level > max_level:
            continue

        raw_text = hm.group(2).strip()
        # strip inline markdown (bold, italic, code, links, emoji colons)
        anchor_text = re.sub(r'!\[.*?\]\(.*?\)', '', raw_text)
        anchor_text = re.sub(r'\[([^\]]*)\]\(.*?\)', r'\1', anchor_text)
        anchor_text = re.sub(r'[*_`]', '', anchor_text)
        anchor_text = re.sub(r':[a-z_]+:', '', anchor_text)   # :emoji:

        headings.append({
            'level': level,
            'text': raw_text,
            'anchor': heading_to_anchor(anchor_text),
        })

    return headings


# ── TOC block builders ────────────────────────────────────────────────────────

TOC_START = '<!-- TOC_START -->'
TOC_END   = '<!-- TOC_END -->'
BACK_LINK = '[🔙 目次に戻る](#index)'

def build_toc_block(headings: list[dict], top_level: int) -> list[str]:
    """Return lines that make up the TOC block (including sentinel comments)."""
    lines = [TOC_START, '', '## 📖 目次', '', '<a id="index"></a>', '']

    for h in headings:
        indent = '  ' * (h['level'] - top_level)
        lines.append(f"{indent}- [{h['text']}](#{h['anchor']})")

    lines += ['', TOC_END]
    return lines


def build_back_link_lines() -> list[str]:
    return ['', BACK_LINK, '']


# ── file processing ───────────────────────────────────────────────────────────

def find_section_boundaries(lines: list[str], max_level: int) -> list[dict]:
    """
    For each heading (up to max_level), find the index of the last line of
    its "leaf section" — i.e. just before the next heading of equal or lesser
    level (or end of file).
    """
    boundaries = []
    in_fence = False
    fence_pat = re.compile(r'^\s*(`{3,}|~{3,})')
    heading_indices = []

    for i, line in enumerate(lines):
        m = fence_pat.match(line)
        if m:
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        hm = re.match(r'^(#{1,6})\s+', line)
        if hm and len(hm.group(1)) <= max_level:
            heading_indices.append((i, len(hm.group(1))))

    for idx, (line_idx, level) in enumerate(heading_indices):
        # find next heading of same or lesser depth
        end = len(lines)
        for j in range(idx + 1, len(heading_indices)):
            if heading_indices[j][1] <= level:
                end = heading_indices[j][0]
                break
        boundaries.append({'line': line_idx, 'level': level, 'end': end})

    return boundaries


def strip_existing_back_links(lines: list[str]) -> list[str]:
    """Remove all existing 'back to TOC' links."""
    result = []
    for line in lines:
        if BACK_LINK in line:
            continue
        result.append(line)
    # clean up double blank lines that might appear after removal
    cleaned = []
    prev_blank = False
    for line in result:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue
        cleaned.append(line)
        prev_blank = is_blank
    return cleaned


def strip_existing_toc(lines: list[str]) -> list[str]:
    """Remove the existing TOC block if present."""
    start = end = None
    for i, line in enumerate(lines):
        if line.strip() == TOC_START:
            start = i
        if line.strip() == TOC_END and start is not None:
            end = i
            break
    if start is None:
        return lines
    return lines[:start] + lines[end + 1:]


def insert_toc(lines: list[str], toc_lines: list[str], top_level: int) -> list[str]:
    """
    Insert TOC just before the first heading of top_level.
    If no such heading exists, insert after the first paragraph block.
    """
    in_fence = False
    fence_pat = re.compile(r'^\s*(`{3,}|~{3,})')

    for i, line in enumerate(lines):
        m = fence_pat.match(line)
        if m:
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r'^#{%d}\s' % top_level, line):
            # insert before this heading, keeping blank lines clean
            before = lines[:i]
            # ensure one blank line before TOC
            while before and before[-1].strip() == '':
                before.pop()
            before.append('')
            return before + toc_lines + [''] + lines[i:]

    # fallback: append at end
    return lines + [''] + toc_lines


def insert_back_links(lines: list[str], max_level: int) -> list[str]:
    """
    Insert a 'back to TOC' link after the last content line of every
    leaf-level section (sections whose level == max_level).
    """
    boundaries = find_section_boundaries(lines, max_level)
    # only insert for leaf sections (deepest heading level found, or == max_level)
    leaf_boundaries = [b for b in boundaries if b['level'] == max_level]

    # work from the bottom up to preserve indices
    result = list(lines)
    for b in reversed(leaf_boundaries):
        end = b['end']
        # walk back from end to find last non-blank line
        insert_at = end
        for k in range(end - 1, b['line'], -1):
            if result[k].strip() != '':
                insert_at = k + 1
                break
        back = ['', BACK_LINK, '']
        result = result[:insert_at] + back + result[insert_at:]

    return result


def process_file(path: Path, max_level: int, dry_run: bool = False) -> bool:
    """
    Process a single Markdown file.
    Returns True if the file was (or would be) modified.
    """
    original = path.read_text(encoding='utf-8')
    lines = original.splitlines(keepends=False)

    # 1. strip old back-links and TOC
    lines = strip_existing_back_links(lines)
    lines = strip_existing_toc(lines)

    # 2. extract headings
    headings = extract_headings(lines, max_level)
    if not headings:
        print(f'  [skip] no headings found in {path}')
        return False

    top_level = min(h['level'] for h in headings)

    # 3. build TOC block
    toc_lines = build_toc_block(headings, top_level)

    # 4. insert TOC
    lines = insert_toc(lines, toc_lines, top_level)

    # 5. insert back-links
    lines = insert_back_links(lines, max_level)

    new_content = '\n'.join(lines)
    # ensure single trailing newline
    new_content = new_content.rstrip('\n') + '\n'

    if new_content == original:
        print(f'  [unchanged] {path}')
        return False

    if dry_run:
        print(f'  [dry-run] would update {path}')
        return True

    path.write_text(new_content, encoding='utf-8')
    print(f'  [updated] {path}')
    return True


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Add/update TOC and back-links in Markdown files.'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Markdown files to process (default: all *.md in current directory tree)',
    )
    parser.add_argument(
        '--level', '-l',
        type=int,
        default=2,
        help='Maximum heading level for TOC and back-links (default: 2 = ##)',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without writing files',
    )
    args = parser.parse_args()

    if args.files:
        paths = [Path(f) for f in args.files]
    else:
        paths = list(Path('.').rglob('*.md'))

    changed = 0
    for p in paths:
        if not p.exists():
            print(f'  [missing] {p}')
            continue
        if process_file(p, args.level, dry_run=args.dry_run):
            changed += 1

    print(f'\nDone. {changed}/{len(paths)} file(s) {"would be " if args.dry_run else ""}updated.')
    sys.exit(0)


if __name__ == '__main__':
    main()