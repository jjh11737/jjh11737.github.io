# 关于ld脚本
> 学习时碰到链接脚本，因此准备了解一下这玩意如何工作的
>
> 自然是RTFM，我看的是[官方文档](https://ftp.gnu.org/old-gnu/Manuals/ld-2.9.1/html_chapter/ld_1.html)

`ld`是一个链接工具，把各种目标和archive文件结合起来做重定位和符号解析，形成可执行文件。一般我们编译程序最后一步就是用`ld`。它接收的是`Linker Command Language`文件，

`BFD(Binary File Descripter)`库，它定义了一套接口和例程用来统一处理各种目标文件（无论是何种格式），而真正的细节被后端藏了起来，而`ld`本身则只需要关注canonical form就可以工作
