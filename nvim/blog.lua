-- ============================================================
--  nvim 集成示例：放到 ~/.config/nvim/lua/blog.lua 然后在 init.lua 里
--    require('blog')
--
--  提供：
--    <leader>bp / :BlogPublish   保存并发布当前文件
--    <leader>bn / :BlogNew       新建内容（会自动打开编辑器）
--    <leader>bv / :BlogVis       切换当前文件的可见性（public/hidden/draft）
--    <leader>bs                  起本地预览
-- ============================================================

local M = {}

-- blog 脚本的位置：装了软链之后直接用 'blog' 即可
local BLOG = vim.fn.executable("blog") == 1 and "blog" or nil

local function notify(out, code)
  local level = code == 0 and vim.log.levels.INFO or vim.log.levels.ERROR
  vim.notify((out or ""):gsub("%s+$", ""), level, { title = "blog" })
end

function M.publish()
  local file = vim.fn.expand("%:p")
  if file == "" then
    return notify("当前 buffer 没有文件", 1)
  end
  if not BLOG then
    return notify("找不到 blog 命令，先把 scripts/blog 软链到 ~/.local/bin", 1)
  end
  vim.cmd("write")
  local out = vim.fn.system({ BLOG, "save", file })
  notify(out, vim.v.shell_error)
end

function M.new(type, title, tags)
  if not BLOG then
    return notify("找不到 blog 命令", 1)
  end
  local args = { BLOG, "new", type, title }
  if tags and tags ~= "" then
    table.insert(args, tags)
  end
  local out = vim.fn.system(args)
  notify(out, vim.v.shell_error)
end

function M.serve()
  vim.cmd("botright 12split | terminal " .. (BLOG or "blog") .. " preview")
end

function M.vis(mode)
  local file = vim.fn.expand("%:p")
  if file == "" then
    return notify("当前 buffer 没有文件", 1)
  end
  if not BLOG then
    return notify("找不到 blog 命令", 1)
  end
  local args = { BLOG, "vis", file }
  if mode and mode ~= "" then
    table.insert(args, mode)
  end
  notify(vim.fn.system(args), vim.v.shell_error)
end

function M.pick_vis()
  local modes = { "public", "hidden", "draft" }
  vim.ui.select(modes, {
    prompt = "可见性: ",
    format_item = function(item)
      return ({
        public = "public  收录（搜索/RSS/sitemap）",
        hidden = "hidden  不收录，链接可访问",
        draft = "draft   不发布",
      })[item]
    end,
  }, function(choice)
    if choice then
      M.vis(choice)
    end
  end)
end

vim.api.nvim_create_user_command("BlogPublish", M.publish, { desc = "保存并发布当前文件" })
vim.api.nvim_create_user_command("BlogNew", function(opts)
  local type, title = opts.args:match("^(%S+)%s+(.+)$")
  if not type then
    return notify("用法: :BlogNew posts 我的标题", 1)
  end
  M.new(type, title)
end, { nargs = "+", complete = function()
  return { "posts", "notes", "reading", "music" }
end, desc = "新建内容" })

vim.keymap.set("n", "<leader>bp", M.publish, { desc = "blog: 发布当前文件" })
vim.keymap.set("n", "<leader>bs", M.serve, { desc = "blog: 本地预览" })
vim.keymap.set("n", "<leader>bv", M.pick_vis, { desc = "blog: 切换可见性" })
vim.api.nvim_create_user_command("BlogVis", function(opts)
  M.vis(opts.args)
end, { nargs = "?", complete = function()
  return { "public", "hidden", "draft" }
end, desc = "设置当前文件可见性" })
vim.keymap.set("n", "<leader>bn", function()
  local type = vim.fn.input("类型 (posts/notes/reading/music): ")
  if type == "" then
    return
  end
  local title = vim.fn.input("标题: ")
  if title == "" then
    return
  end
  local tags = vim.fn.input("标签（逗号分隔，可空）: ")
  M.new(type, title, tags)
end, { desc = "blog: 新建内容" })

return M
