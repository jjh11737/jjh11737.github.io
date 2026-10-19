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
这里就是先给`a6/a7`赋值，然后通过`ecall`从`M-mode`进入`S-mode`，所谓SBI就是这个接口，相关内容见[RISC-V ABI](https://www.scs.stanford.edu/~zyedidia/docs/riscv/riscv-sbi.pdf)，注释说这是shutdown，不过我可能之后还得看手册确认一下

### Firmware

功能：

- 完成硬件扫描/初始化/配置
- 加载OS


## 虚拟化

所谓虚拟化就是把一份物理资源变成多份虚拟资源，让每个程序都以为自己独占一份





## 并发

实际上，单个线程就是一个栈帧，每一个有自己单独的PC和局部变量，而自然全局变量和heap很自然地是共享的，用状态机模型理解就会很简单

每个线程都有自己的TLS(thread local storage)，那是如何实现的呢？

如果我们想进一步配置线程，我们这里已经用了`pthreads`的线程库，可以`man pthreads`

但是一个很自然的问题就产生了，当我们两个线程同时执行`x++`，如果不加锁，它的行为无法预测！
> 一个简单的例子
```c
#include "thread.h"

#define N 100000000

long sum = 0;

void T_sum() {
    for (int i = 0; i < N; i++) {
        sum++;

        // Won't work even if we force a single-instruction
        // increment.

        // asm volatile(
        //     "incq %0" : "+m"(sum)
        // );

        // On aarch64, there's no single instruction increment.
        // Must do a (ldr + add + str) combination.
    }
}

int main() {
    spawn(T_sum);
    spawn(T_sum);

    join();

    printf("sum = %ld\n", sum);
    printf("2*n = %ld\n", 2L * N);
}
```
结果：
```text
$ ./sum
sum = 119131823
```
显然远小于我们的预期

因为现代处理器本身不仅单处理器多线程（线程在运行时可能会被中断切换到另一个线程执行），而且多处理器核同时工作，导致线程本身就是并行执行的。

> [Dekker's Algorithm](https://en.wikipedia.org/wiki/Dekker%27s_algorithm)

但是很显然，我们刚才并没有编译优化
- O1: `R[eax]=sum; R[eax]+=N; R[eax]` 
- O2: `sum+=N`，也就是内联展开！


我们可以在代码中插入优化无法穿越的`barrier`
```c
int x = 0, y = 0;

void T1() {
  x = 1;
  asm volatile("" : : "memory"); // compiler barrier
  printf("y = %d\n", y);
}

void T2() {
  y = 1;
  asm volatile("" : : "memory"); // compiler barrier
  printf("x = %d\n", x);
}
```
这是GCC/CLANG支持的GNU C内联汇编语法，`volatile`这里是告诉编译器这段汇编不可以被优化掉，`""`汇编指令本身是空的，而`"memory"`则是声明一个编译器层面的内存屏障，告诉编译器这段代码可能读写内存


而且就像我们知道的，哪怕是ISA层面仍然不是最小的执行单元，因为处理器会把指令分解为uop：
- 每个周期向池子补充尽可能多的uop，多发射
- 每个周期执行尽可能的uop，乱序执行，通过ROB按序提交

而即使满足单处理器`eventual memory consistency`的执行，在多处理器上仍然可能无法序列化
就像刚刚那个程序，多处理器下仍然会都读到0，因为这不违背`cache coherence`，而且本身单个核还有自己的`store buffer`

### 宽松内存模型


