---
title: "关于校园网无法正常通过ssh协议push到github"
date: 2026-09-06T00:00:00+08:00
draft: false
tags: ["Git"]
---

不知道为什么，每次用校园网不管开不开代理，push的时候总是会卡在：
```bash
$ strace -p 9680
strace: Process 9680 attached
read(5,
```
查一下就知道这是socket

注意它是卡在`read`上而不是`connect`上，说明TCP已经连上了，只是一直等不到数据（要是连接阶段就不通，strace停住的会是`connect(...)`）

## 怎么定位

```bash
ssh -vT git@github.com       # -v能看到卡在哪一步
getent hosts github.com      # 解析出来的是v4还是v6
nc -vz github.com 22         # 22通不通
curl -I github.com           # 443通不通，用来对照
ssh -4 -T git@github.com     # 强制IPv4
ssh -6 -T git@github.com     # 强制IPv6
```

校园网里常见的原因就三类：IPv6半通不通（`-6`卡、`-4`通）；只挡了22端口；代理只覆盖了http，`git config http.proxy`只对https协议的remote生效，ssh协议根本不走它，所以开不开代理没区别

## 解法

1. 强制IPv4，我这边就是这么好的，写进`~/.ssh/config`：
```
Host github.com
    HostName github.com
    User git
    AddressFamily inet
```
临时的写法是`ssh -4 -T git@github.com`，要强制v6就是`AddressFamily inet6`

2. 22被掐就换443，GitHub在443上也有ssh入口：
```
Host github.com
    HostName ssh.github.com
    Port 443
    User git
```
先用`ssh -T -p 443 git@ssh.github.com`验证一下再往config里写

3. 让ssh也走代理，`nc`得是openbsd那个版本，没有就换`ncat --proxy 127.0.0.1:7890 --proxy-type http %h %p`：
```
Host github.com
    ProxyCommand nc -X connect -x 127.0.0.1:7890 %h %p
```

4. 或者干脆改成https协议，这样`http.proxy`就管用了：
```bash
git remote set-url origin https://github.com/<user>/<repo>.git
git config --global http.proxy http://127.0.0.1:7890
```

另外配个超时，免得一卡就是好几分钟：
```
Host *
    ConnectTimeout 10
    ServerAliveInterval 10
    ServerAliveCountMax 3
```

调试用`GIT_SSH_COMMAND="ssh -vvv" git push`；如果卡的是走https的push，那是另一回事，该用`GIT_CURL_VERBOSE=1`
