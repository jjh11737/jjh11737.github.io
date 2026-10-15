# 个人主页（Hugo + PaperMod）

独立于知识库（VitePress 那个站点）的个人主页 / 博客。两者互不依赖，各自部署，互不影响。

Hugo 站点、PaperMod 主题、本地 Fuse.js 搜索、RSS 全站 + 按 section 输出。

## 快速开始

```bash
# 1. 依赖：Hugo extended >= 0.146（本机装的是 0.168，在 ~/.local/bin/hugo）
hugo version

# 2. 把发布脚本挂到 PATH
ln -s "$PWD/scripts/blog" ~/.local/bin/blog

# 3. 本地预览（含草稿和未来日期的内容）
blog preview
```

## 日常写作流程

```bash
blog new posts "标题" "标签1,标签2"   # 新建长文，自动打开 nvim
blog note "一句话"                    # 短记：写完立刻提交推送
blog new reading "《书名》"           # 阅读条目（再手填 author / status / rating）
blog new music "曲名"                 # 音乐条目（再手填 artist / link）
blog publish                          # 提交并推送 content/ 下的全部改动
blog preview                          # 本地预览
blog build                            # 本地构建检查
blog tags                             # 标签统计
```

nvim 里（配置见 `nvim/blog.lua`）：

| 键位 | 动作 |
| --- | --- |
| `<leader>bp` | 保存当前文件并提交推送 |
| `<leader>bn` | 交互式新建内容 |
| `<leader>bs` | 打开本地预览 |

推送 → GitHub Actions 构建 → Pages 上线，中间没有别的步骤。没配 remote 时脚本会提交到本地并提示你。

## 内容类型

四种类型各占一个 section，可以分别有各自的 frontmatter 字段：

| 类型 | 目录 | 专属字段 | 列表页样式 |
| --- | --- | --- | --- |
| 长文 | `content/posts/` | `tags` `categories` `summary` | 主题默认卡片 |
| 短记 | `content/notes/` | `tags` | 按月分组的时间线（`layouts/notes/list.html`） |
| 阅读 | `content/reading/` | `author` `status` `rating` `link` | 按 在读/想读/读完 分组，底部信息卡 |
| 音乐 | `content/music/` | `artist` `link` | 列表 + 底部信息卡 |

通用字段：`title` `date` `draft` `tags`。

- `date` 写完整时间戳（`2026-10-15T08:00:00+08:00`），RSS 的排序和时区才准
- `status` 只认 `在读` / `想读` / `读完` 三个值，其他值会落到"未标注"分组
- `rating` 是 0-5 的整数，0 表示不打分

标签和分类由 Hugo 自动生成页面：`/tags/` `/tags/<tag>/` `/categories/`，每个 tag 还有自己的 RSS。

## 首页

首页由两部分拼成，都在配置里可调：

1. `hugo.toml` 的 `[params.profileMode]`：头像、标题、副标题、按钮
2. `layouts/_partials/home_recent.html`：把四种类型混成一条"最近"动态流，条数看 `params.homeRecentCount`

## RSS

| 地址 | 内容 |
| --- | --- |
| `/index.xml` | 全站，按时间倒序混合四种类型 |
| `/posts/index.xml` `/notes/index.xml` … | 分类型 |
| `/tags/<tag>/index.xml` | 按标签 |

- 全文输出：`params.ShowFullTextinRSS = true`，阅读器里直接能读完整篇
- 条数上限：`[services.rss] limit`
- 不想进 feed 的页面加 `hiddenInRss: true`（`about.md` 就是这么做的）
- 页面 `<head>` 里已经有 `rel="alternate"` 自动发现，阅读器能直接订阅

## 搜索

PaperMod 用本地 Fuse.js，没有任何外部服务：

- 索引是构建时生成的 `/index.json`，内容是全部页面的标题 + 正文纯文本
- 不想被搜到的页面加 `searchHidden: true`
- 正文量大之后 `index.json` 会变大（现在是几 KB 级），如果哪天到几百 KB，就把 `[params.fuseOpts]` 的 `keys` 里的 `content` 去掉，只搜标题

## 部署

`.github/workflows/deploy.yml` 会在 `main` 分支推送后构建并发布到 GitHub Pages。

上线前要改的只有一处：

```toml
# hugo.toml
baseURL = "https://你的域名/"
```

它影响 RSS 里的绝对链接、sitemap 和图片地址，所以别忘了。域名在仓库的 Settings → Pages 里填，并在 `static/` 下放一个 `CNAME` 文件（内容是你域名）会更省事。

## 主题

主题是 git submodule，不参与本仓库的代码：

```bash
git submodule update --init --recursive   # 首次拉取
git submodule update --remote --merge     # 升级主题
```

自定义的地方都放在站点侧，没有直接改主题文件：`layouts/` `assets/css/extended/custom.css`。升级主题不会冲突。

## 已知的坑

- **日期在未来的文章不会渲染**。Hugo 默认不构建未来的内容，这是官方的"定时发布"机制。推送后如果发现文章没上线，先看 `date`。预览加 `-F` 就能看到（`blog preview` 已经带了）。
- **`draft: true` 不会上线**。它只活在 `blog preview` 里，`blog publish` 会提醒你。
- **发过的文章不要改 slug / 文件名**。RSS 的 GUID 是永久链接，改了就相当于重新推一篇。
- **图片建议放 `static/images/`，用 `![x](/images/xxx.png)` 这种绝对路径**。`layouts/_markup/render-image.html` 已经把页面资源转成绝对 URL，但外部图床/相对路径在 RSS 阅读器里仍然容易挂。
- **样张内容**：`content/posts/2026-10-15-split-homepage.md`、`content/notes/2026-10-1*.md`、`content/reading/`、`content/music/` 下的示例可以直接删，删完 `blog publish` 一次即可。

## 目录结构

```
content/          四种内容 + about / search / archives
layouts/          首页动态流、短记时间线、阅读音乐列表、图片渲染钩子
assets/css/extended/custom.css   自己的样式（会被自动拼接进主题样式表）
archetypes/       blog new 之外的 hugo new 模板
scripts/blog      发布 CLI
nvim/blog.lua     nvim 集成示例
.github/workflows/deploy.yml     构建 + 部署
```
