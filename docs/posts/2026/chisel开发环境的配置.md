# Chisel开发环境的配置
不知道为什么我根据[官方教程](https://www.chisel-lang.org/docs/installation)似乎并不太成功？由于ysyx官方似乎更喜欢使用mill,因此我最后还是借鉴了[A-Minimal-Chisel-Project](https://github.com/ucb-bar/A-Minimal-Chisel-Project)
## 具体步骤：
1. 安装好scala，[官方链接](https://www.scala-lang.org/download/)（建议开一下代理）
    ```bash
    curl -fL https://github.com/coursier/coursier/releases/latest/download/cs-x86_64-pc-linux.gz | gzip -d > cs && chmod +x cs && ./cs setup
    ```
2. 安装mill，[官方链接](https://mill-build.org/mill/cli/installation-ide.html)
    ```bash
    > sudo curl -L https://repo1.maven.org/maven2/com/lihaoyi/mill-dist/1.1.7/mill-dist-1.1.7-mill.sh -o /usr/local/bin/mill
    > sudo chmod +x /usr/local/bin/mill
    ```
