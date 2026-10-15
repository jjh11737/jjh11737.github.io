#!/usr/bin/env python3
"""按规则表给内容自动生成标签。

    python3 scripts/tag.py --dry              # 预览（默认）
    python3 scripts/tag.py --apply [文件...]  # 写进 frontmatter
    python3 scripts/tag.py --clear [文件...]  # 删掉自动写的标签 key

规则表：scripts/tag-rules.tsv（格式见文件内注释）。
笔记区（content/n7k4xq/）写的是 noteTags —— 这是一个普通字段，不是 Hugo 分类法，
所以不会生成公开的标签页；其他区域写 tags，会生成 /tags/ 页面和对应的 feed。
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, "scripts", "tag-rules.tsv")
NOTES_PREFIX = "content/n7k4xq/"
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
        lines.append("%s: [%s]" % (key, ", ".join('"%s"' % t for t in tags)))
    return "---\n" + "\n".join(lines) + "\n---\n" + rest


def main():
    argv = sys.argv[1:]
    mode = "--dry"
    paths = []
    for a in argv:
        if a in ("--dry", "--dry-run"):
            mode = "--dry"
        elif a == "--apply":
            mode = "--apply"
        elif a == "--clear":
            mode = "--clear"
        else:
            paths.append(a)

    targets = collect_targets(paths)
    changed, skipped = 0, 0
    width = max((len(t) for t in targets), default=10)

    for rel in targets:
        path = os.path.join(ROOT, rel)
        text = open(path, encoding="utf-8").read()
        fm, body, _ = split_frontmatter(text)
        if fm is None:
            skipped += 1
            continue
        if fm_get(fm, "layout") in ("search", "archives"):
            skipped += 1
            continue

        key = "noteTags" if rel.startswith(NOTES_PREFIX) else "tags"
        tags, hits = classify(rel, fm, body)

        if mode == "--dry":
            existing = fm_get(fm, key) or ""
            mark = "有" if existing else "  "
            print("%s %-*s %s" % (mark, width, rel, ", ".join(tags) if tags else "(无命中)"))
            continue

        if mode == "--apply":
            if not tags:
                skipped += 1
                continue
            new = write_frontmatter(text, key, tags)
        else:  # --clear
            new = write_frontmatter(text, key, None)

        if new is not None and new != text:
            open(path, "w", encoding="utf-8").write(new)
            changed += 1

    if mode == "--dry":
        print("\n（预览模式，什么都没写。确认后跑 blog tag --apply）")
    else:
        print("处理 %d 个文件，改动 %d 个，跳过 %d 个" % (len(targets), changed, skipped))


if __name__ == "__main__":
    rules = load_rules(RULES)
    main()
