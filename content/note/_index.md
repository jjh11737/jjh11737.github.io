---
title: "note"
description: "公开的笔记"
# 旧的隐藏区前缀，老书签仍可用（生成一个跳转页）
aliases: ["/n7k4xq/"]
# HTML 给栏目页，NotesJSON 给只搜笔记的搜索索引，RSS 是这一区自己的 feed
outputs: ["HTML", "NotesJSON", "RSS"]
# 这一页是公开栏目，所以自己要被收录；下面的 cascade 才是“默认藏起来”
hiddenInRss: true
robotsNoIndex: false
sitemap:
  disable: false
# 告诉 layouts/rss.xml：这一区单独出一份 feed
noteFeed: true
cascade:
  hiddenInRss: true     # 默认：不进任何 feed（被 blog vis 设成 public 的会变 false，但主页 feed 仍然不收笔记）
  searchHidden: true    # 默认：不进全站搜索索引
  robotsNoIndex: true   # 默认：输出 <meta name="robots" content="noindex, nofollow">
  math: true            # 加载自托管 KaTeX
  badge: "note"          # 公开后在首页“最近”流里显示的徽标
  sitemap:
    disable: true       # 默认：不进 sitemap.xml
---

这里列出的都是被设为公开的笔记。

> 如果你真想看我不想公开的...点下面这个
