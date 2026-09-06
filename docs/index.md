---
layout: home

hero:
  name: "jjh's wiki"
  text: "一个简陋的博客"
  tagline: ""

  actions:
    - theme: brand
      text: Posts
      link: /posts/

    - theme: alt
      text: GitHub
      link: https://github.com/jjh11737

    - theme: alt
      text: Notes
      link: /notes/

  features:
    - title: Learning Notes
      details: 课程/教材等阅读时整理的笔记
---

## 最近更新

<PostList :limit="6" />

<div class="all-posts">
  <a href="/posts/">查看全部文章 →</a>
</div>
