# 关于tmux
记录一下我用tmux一些容易忘的点，借鉴[a quick&easy guide](https://hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/) / [cheat Sheet](http://tmuxcheatsheet.com/)

> 为什么用Tmux？
>
> 1. 服务器：比如你通过ssh连接到远程服务器上，如果连接断开，tmux当然会断联，但是仅此而已，这个会话包括所有相关进程仍然会在服务器后台执行，你只需要重新ssh一下然后连接到那个会话即可
> 2. 本地：同上。总之有2个强大的功能：
>    - 终端里面的窗口管理
>    - 会话管理

首先需要明确tmux有3个基本概念：

- session
- window
- panel



Session：

1. 创建一个session，只需要`tmux`即可：

   > 当然也可以是`tmux new` / `tmux new-session`

   ![image-20260907091507765](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260907091507765.png)

> 左下角：`[0] 0:bash*`：`[0]`代表当前所在窗口编号，后面是每个窗口的前台进程

2. 创建新会话 / 连接到既有的会话：`tmux new-session -A -s

- 创建一个新的窗口：一旦我们处于一个session里面时，就可以`prefix C`创建一个新的窗口。
  ![image-20260907092327661](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260907092327661.png)

> 和emacs一样，这里使用命令也是有一个prefix：`<C-b>`

- 窗口间来回切换：`prefix n`到下一个窗口
  				`prefix  0/1/...9`指定编号的切换
- 关闭窗口：`prefix &`关闭当前窗口
- panel：
  - 创建小的panel：`prefix %`创建横向的一个新的panel小窗口
                                 `prefix "`创建纵向的一个新的panel
  - 关闭小的panel：`C-d`关闭当前的panel
