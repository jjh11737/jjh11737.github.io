#!/usr/bin/env python3
"""按规则表为内容补充标签，并检查 note 的标签。

    python3 scripts/tag.py --dry              # 预览（默认）
    python3 scripts/tag.py --apply [文件...]  # 补充并写进 frontmatter
    python3 scripts/tag.py --check [文件...]  # 检查标签，不修改文件
    python3 scripts/tag.py --clear [文件...]  # 删掉自动写的标签 key

规则表：scripts/tag-rules.tsv（格式见文件内注释）。
note 栏（content/note/）写的是 noteTags —— 这是一个普通字段，不是 Hugo 分类法，
所以不会生成公开的标签页；其他区域写 tags，会生成 /tags/ 页面和对应的 feed。
手写在 frontmatter 里的标签会被保留，规则表只负责补上缺失的自动标签。
"""

import ast
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, "scripts", "tag-rules.tsv")
NOTES_PREFIX = "content/note/"
THRESHOLD = 3  # 关键词只在正文里出现时，至少要命中这么多次
MAX_TAGS = 6


def load_rules(path):
    rules = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                rules.append((parts[0], parts[1], parts[2]))
    return rules


def read_text(path):
    """读取时保留原始换行，只把 CRLF 归一成 LF、丢掉孤立的 CR。
    不这么做的话，Windows 换行（CRLF）里的 \\r 会在改 frontmatter 时被当成换行，
    把某个字段（比如 title）拆成两行 —— 之前就踩过这个坑。"""
    raw = open(path, encoding="utf-8", newline="").read()
    return raw.replace("\r\n", "\n").replace("\r", "")


def collect_targets(paths):
    if paths:
        out = []
        for p in paths:
            p = p if os.path.isabs(p) else os.path.join(os.getcwd(), p)
            p = os.path.relpath(p, ROOT)
            if os.path.isfile(os.path.join(ROOT, p)):
                out.append(p)
        return out
    out = []
    for base, _dirs, files in os.walk(os.path.join(ROOT, "content")):
        for f in files:
            if f.endswith(".md") and f != "_index.md":
                out.append(os.path.relpath(os.path.join(base, f), ROOT))
    return sorted(out)


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text, ""
    return m.group(1), text[m.end():], text[:m.end()]


def fm_get(fm, key):
    m = re.search(r"^%s:\s*(.*)$" % re.escape(key), fm, re.M)
    return m.group(1).strip() if m else None


def parse_inline_tags(raw):
    """解析一行 YAML/JSON 风格标签数组，不依赖 PyYAML。"""
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            try:
                value = ast.literal_eval(raw)
            except (SyntaxError, ValueError):
                if not raw.endswith("]"):
                    raise ValueError("标签数组没有以 ] 结束")
                rows = next(csv.reader([raw[1:-1]], skipinitialspace=True))
                value = [row.strip().strip("\"'") for row in rows if row.strip()]
    elif "," in raw:
        rows = next(csv.reader([raw], skipinitialspace=True))
        value = [row.strip().strip("\"'") for row in rows if row.strip()]
    else:
        value = [raw.strip("\"'")]
    if not isinstance(value, list):
        raise ValueError("标签必须是数组")
    return value


def fm_tags(fm, key):
    """读取 inline 或 block-list 形式的标签字段。"""
    lines = fm.split("\n")
    for i, line in enumerate(lines):
        m = re.match(r"^%s:\s*(.*)$" % re.escape(key), line)
        if not m:
            continue
        raw = m.group(1).strip()
        if raw:
            return parse_inline_tags(raw)
        tags = []
        for child in lines[i + 1:]:
            if not child.strip():
                continue
            item = re.match(r"^[ \t]+-\s+(.+?)\s*$", child)
            if item:
                tags.append(item.group(1).strip("\"'"))
                continue
            if child.startswith((" ", "\t")):
                raise ValueError("标签列表项必须以 - 开头")
            break
        return tags
    return []


def normalize_tags(tags):
    out = []
    for tag in tags:
        if not isinstance(tag, str):
            raise ValueError("标签必须是字符串")
        tag = tag.strip()
        if not tag:
            raise ValueError("标签不能为空")
        out.append(tag)
    return out


def merge_tags(existing, generated):
    """已有手写标签时完全保留；规则只给缺少标签的文档补默认值。"""
    tags = []
    for tag in normalize_tags(existing):
        if tag not in tags:
            tags.append(tag)
    if tags:
        return tags
    for tag in normalize_tags(generated):
        if tag not in tags and len(tags) < MAX_TAGS:
            tags.append(tag)
    return tags


def classify(rel, fm, body):
    """返回 (标签列表, 每个标签的命中次数)。目录标签优先，关键词标签按命中次数排。"""
    title = fm_get(fm, "title") or ""
    m = re.search(r"^#\s+(.+)$", body, re.M)
    head = (title + " " + (m.group(1) if m else "")).lower()
    low = body.lower()

    path_tags, kw_tags, hits = [], [], {}
    for kind, pattern, tag in rules:
        if kind == "path":
            if rel.startswith(pattern) and tag not in path_tags:
                path_tags.append(tag)
        elif kind == "kw":
            pat = pattern.lower()
            # 纯 ASCII 的关键词按整词匹配，避免 sed 命中 used / based 这种
            if pat.isascii():
                n = len(re.findall(r"(?<![0-9a-z_])%s(?![0-9a-z_])" % re.escape(pat), low))
            else:
                n = low.count(pat)
            in_head = pat in head
            if in_head or n >= THRESHOLD:
                if tag not in kw_tags:
                    kw_tags.append(tag)
                hits[tag] = n + (50 if in_head else 0)

    order = {t: i for i, t in enumerate(kw_tags)}
    kw_tags.sort(key=lambda t: (-hits.get(t, 0), order[t]))
    ordered = path_tags + [t for t in kw_tags if t not in path_tags]
    return ordered[:MAX_TAGS], hits


def write_frontmatter(text, key, tags=None):
    fm, rest, _ = split_frontmatter(text)
    if fm is None:
        return None
    lines, skipping = [], False
    for line in fm.split("\n"):
        if re.match(r"^%s:" % re.escape(key), line):
            skipping = True
            continue
        if skipping and line.startswith((" ", "\t")):
            continue
        skipping = False
        lines.append(line)
    while lines and not lines[-1].strip():
        lines.pop()
    if tags:
        encoded = ", ".join(json.dumps(t, ensure_ascii=False) for t in tags)
        lines.append("%s: [%s]" % (key, encoded))
    return "---\n" + "\n".join(lines) + "\n---\n" + rest


def main():
    argv = sys.argv[1:]
    mode = "--dry"
    notes_only = False
    paths = []
    for a in argv:
        if a in ("--dry", "--dry-run"):
            mode = "--dry"
        elif a == "--apply":
            mode = "--apply"
        elif a == "--check":
            mode = "--check"
        elif a == "--clear":
            mode = "--clear"
        elif a == "--notes":
            notes_only = True
        else:
            paths.append(a)

    targets = collect_targets(paths)
    if notes_only:
        targets = [t for t in targets if t.startswith(NOTES_PREFIX)]
    changed, skipped = 0, 0
    errors = []
    checked = 0
    width = max((len(t) for t in targets), default=10)

    for rel in targets:
        path = os.path.join(ROOT, rel)
        text = read_text(path)
        fm, body, _ = split_frontmatter(text)
        if fm is None:
            skipped += 1
            continue
        layout = fm_get(fm, "layout")
        if layout and layout.strip("\"'") in ("search", "archives"):
            skipped += 1
            continue

        key = "noteTags" if rel.startswith(NOTES_PREFIX) else "tags"
        tags, hits = classify(rel, fm, body)
        if mode == "--check" and rel.startswith(NOTES_PREFIX):
            checked += 1
        try:
            existing = fm_tags(fm, key)
        except ValueError as exc:
            errors.append("%s：%s" % (rel, exc))
            skipped += 1
            continue
        effective = merge_tags(existing, tags)

        if mode == "--check":
            if rel.startswith(NOTES_PREFIX):
                if not existing:
                    errors.append("%s：没有 noteTags" % rel)
                elif len(existing) != len(set(existing)):
                    errors.append("%s：noteTags 有重复项" % rel)
            continue

        if mode == "--dry":
            mark = "有" if existing else "  "
            print("%s %-*s %s" % (mark, width, rel, ", ".join(effective) if effective else "(无命中)"))
            continue

        if mode == "--apply":
            if not effective:
                skipped += 1
                continue
            if existing == effective:
                skipped += 1
                continue
            new = write_frontmatter(text, key, effective)
        else:  # --clear
            new = write_frontmatter(text, key, None)

        if new is not None and new != text:
            open(path, "w", encoding="utf-8").write(new)
            changed += 1

    if mode == "--check":
        for error in errors:
            print("× " + error, file=sys.stderr)
        print("检查了 %d 篇 note：错误 %d" % (checked, len(errors)))
        return 1 if errors else 0
    for error in errors:
        print("× " + error, file=sys.stderr)
    if errors:
        return 1
    if mode == "--dry":
        print("\n（预览模式，什么都没写。确认后跑 blog tag --apply）")
    else:
        print("处理 %d 个文件，改动 %d 个，跳过 %d 个" % (len(targets), changed, skipped))
    return 0


if __name__ == "__main__":
    rules = load_rules(RULES)
    sys.exit(main())
