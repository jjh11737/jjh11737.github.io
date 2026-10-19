---
title: "操作系统"
date: 2026-10-01T11:38:58+08:00
draft: true
---

# 操作系统

> 结合OSTEP，jyyOS和OS2EDU的学习笔记

我们关注3个主题：

- 虚拟化
- 并发
- 持久性


## 硬件视角下的操作系统

我们都知道，firmware在启动时会执行CPU reset，那么是如何实现的？

riscV版：
```asm
.globl _start

_start:
    # SBI system shutdown (sbi_ext_base = 0x10, sbi_ext_base_shutdown = 0x08)
    # a7 = SBI extension ID (0x10 for base)
    # a6 = function ID (0x08 for shutdown)
    li a7, 0x10
    li a6, 0x08
    j go

go:
    ecall

    # Should never reach here
1:
    wfi
    j 1b
```
这里就是先给`a6/a7`赋值，然后通过`ecall`从`M-mode`进入`S-mode`，所谓SBI就是这个接口



## 虚拟化

所谓虚拟化就是把一份物理资源变成多份虚拟资源，让每个程序都以为自己独占一份





## 并发

实际上，单个线程就是一个栈帧，每一个有自己单独的PC和局部变量，而自然全局变量和heap很自然地是共享的，用状态机模型理解就会很简单

每个线程都有自己的TLS(thread local storage)，那是如何实现的呢？







