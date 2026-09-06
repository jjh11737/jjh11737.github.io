---
title: 关于校园网无法正常通过ssh协议push到github
date: '2026-09-06'
---

# 关于校园网无法正常通过ssh协议push到github
不知道为什么，每次用校园网不管开不开代理，push的时候总是会卡在：
```bash
$ strace -p 9680
strace: Process 9680 attached
read(5,
```
查一下就知道这是socket
