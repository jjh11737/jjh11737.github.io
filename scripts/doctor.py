#!/usr/bin/env python3
"""体检：扫一遍 content/，报告常见的 frontmatter / 路由问题。

    python3 scripts/doctor.py        # 也可以直接跑 blog doctor

只报不改。发现的问题分两类：
  错误  必须修，否则页面上会出问题（空标题、进不了归档、日期解析不了）
  提醒  不一定要改（草稿、未来日期、缺标签），知道就行
"""

import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
KNOWN_DIRS = ("posts", "post", "ub")

errors, warnings = [], []


def read(path):
    """保留原始换行读入，只把 CRLF 归一成 LF、丢掉孤立 CR"""
    raw = open(path, encoding="utf-8", newline="").read()
    return raw.replace("\r\n", "\n").replace("\r", "")


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else None


def field(fm, key):
    m = re.search(r"^%s:\s*(.*)$" % re.escape(key), fm, re.M)
    if not m:
        return None
    val = m.group(1).strip()
    return val if val else None


def check(rel, text):
    fm = frontmatter(text)
    if fm is None:
        errors.append("%s：没有 frontmatter（页面标题、日期都会是空的）" % rel)
        return

    # search / archives 这类"工具页"本来就不需要标题和日期
    layout = field(fm, "layout")
    if layout and layout.strip("\"'") in ("search", "archives"):
        return

    title = field(fm, "title")
    if title is None:
        errors.append("%s：缺少 title（页面上会是空标题）" % rel)
    elif not (title.startswith('"') and title.endswith('"') and len(title) > 1):
        errors.append('%s：title 不是一行完整字符串（当前 %r），多半是被换行拆开了' % (rel, title[:30]))

    date = field(fm, "date")
    if date is None:
        errors.append("%s：缺少 date（不会进归档页，RSS 排序也会乱）" % rel)
    else:
        raw_date = date.strip('"').strip("'")
        try:
            when = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            if when > datetime.now(timezone.utc):
                warnings.append("%s：date 在未来（%s），正式构建不会发布它" % (rel, raw_date))
        except ValueError:
            errors.append("%s：date 解析不了（%r）" % (rel, raw_date))

    if re.search(r"^draft:\s*true", fm, re.M):
        warnings.append("%s：是 draft，线上不会出现" % rel)

    parts = rel.split(os.sep)
    if len(parts) > 2 and parts[1] not in KNOWN_DIRS:
        warnings.append("%s：不在已知栏目目录里（%s），可能放错地方了" % (rel, " / ".join(KNOWN_DIRS)))
    if len(parts) > 1 and parts[1] == "post":
        if not re.search(r"^noteTags:", fm, re.M):
            warnings.append("%s：还没有 noteTags（可以跑 blog tag --apply 生成）" % rel)
    if " " in os.path.basename(rel):
        warnings.append("%s：文件名里有空格，URL 会带 %20" % rel)


def main():
    count = 0
    for base, _dirs, files in os.walk(CONTENT):
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            path = os.path.join(base, f)
            rel = os.path.relpath(path, ROOT)
            if os.path.basename(rel) == "_index.md":
                continue
            count += 1
            check(rel, read(path))

    for e in errors:
        print("× " + e)
    for w in warnings:
        print("· " + w)
    print("\n检查了 %d 个内容文件：错误 %d，提醒 %d" % (count, len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
