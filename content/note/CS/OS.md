---
title: "操作系统"
date: 2026-10-01T11:38:58+08:00
draft: true
noteTags: ["计算机", "汇编"]
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


### 4 抽象：进程

操作系统通过虚拟化CPU来提供多CPU假象，即让一个进程运行一个时间片然后切换到其他进程，称为时分共享CPU技术。
而想要实现，操作系统就需要提供一些低级机制(mechanism)和高级的策略(policy)。前者是一些低级的方法/协议，比如说上下文切换。后者则是在操作系统内做出某种决定的算法。

#### 4.1 进程

操作系统为正在运行的程序提供的抽象就是所谓进程。

进程的状态机的一部分就是其可以访问的内存，也即地址空间。另一部分则是寄存器。以及剩下的则是I/O设备


#### 4.2 进程API

基本来说，任何操作系统都会提供这些API：

- 创建create
- 销毁destroy
- 等待wait
- 其他控制miscellaneous control：比如SIGCONT和SIGINT
- 状态statu：提供有关进程的状态信息


#### 4.3 进程创建

一个程序是如何转化为进程的？

1. 将代码和所有静态数据加载到内存里面
   
    现代操作系统的load是惰性的，只有在程序执行期间需要使用对应的代码和数据时才进行加载

2. 为程序的运行时栈/堆分配内存

3. 执行一些初始化任务，尤其是与IO相关的部分，比如文件描述符

4. 总之初始化完成之后，只需要启动程序了，跳转到入口`main`例程执行，将控制权移交给新的进程

#### 4.4 进程状态

一个进程可以处于以下状态：

- 运行running：进程正在处理器上运行
- 就绪ready：程序已经准备好运行，但是OS暂时不运行
- 阻塞block：一个进程执行了某种操作，直到发生特定事件才准备运行。（经典的例子就是IO访问磁盘了）

![image-20261116104614993](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261116104614993.png)

#### 4.5 数据结构

显然，想要跟踪进程的各个信息，我们就需要对应的数据结构，管理进程就需要进程表了

> 如xv6的proc.h：
>
> ```c
> // Saved registers for kernel context switches.
> struct context {
> uint64 ra;
> uint64 sp;
> 
> // callee-saved
> uint64 s0;
> uint64 s1;
> uint64 s2;
> uint64 s3;
> uint64 s4;
> uint64 s5;
> uint64 s6;
> uint64 s7;
> uint64 s8;
> uint64 s9;
> uint64 s10;
> uint64 s11;
> };
> 
> // Per-CPU state.
> struct cpu {
> struct proc *proc;      // The process running on this cpu, or null.
> struct context context; // swtch() here to enter scheduler().
> int noff;               // Depth of push_off() nesting.
> int intena;             // Were interrupts enabled before push_off()?
> };
> 
> extern struct cpu cpus[NCPU];
> 
> // per-process data for the trap handling code in trampoline.S.
> // sits in a page by itself just under the trampoline page in the
> // user page table. not specially mapped in the kernel page table.
> // uservec in trampoline.S saves user registers in the trapframe,
> // then initializes registers from the trapframe's
> // kernel_sp, kernel_hartid, kernel_satp, and jumps to kernel_trap.
> // prepare_return() and userret in trampoline.S set up
> // the trapframe's kernel_*, restore user registers from the
> // trapframe, switch to the user page table, and enter user space.
> struct trapframe {
> /*   0 */ uint64 kernel_satp;   // kernel page table
> /*   8 */ uint64 kernel_sp;     // top of process's kernel stack
> /*  16 */ uint64 kernel_trap;   // usertrap()
> /*  24 */ uint64 epc;           // saved user program counter
> /*  32 */ uint64 kernel_hartid; // saved kernel tp
> /*  40 */ uint64 ra;
> /*  48 */ uint64 sp;
> /*  56 */ uint64 gp;
> /*  64 */ uint64 tp;
> /*  72 */ uint64 t0;
> /*  80 */ uint64 t1;
> /*  88 */ uint64 t2;
> /*  96 */ uint64 s0;
> /* 104 */ uint64 s1;
> /* 112 */ uint64 a0;
> /* 120 */ uint64 a1;
> /* 128 */ uint64 a2;
> /* 136 */ uint64 a3;
> /* 144 */ uint64 a4;
> /* 152 */ uint64 a5;
> /* 160 */ uint64 a6;
> /* 168 */ uint64 a7;
> /* 176 */ uint64 s2;
> /* 184 */ uint64 s3;
> /* 192 */ uint64 s4;
> /* 200 */ uint64 s5;
> /* 208 */ uint64 s6;
> /* 216 */ uint64 s7;
> /* 224 */ uint64 s8;
> /* 232 */ uint64 s9;
> /* 240 */ uint64 s10;
> /* 248 */ uint64 s11;
> /* 256 */ uint64 t3;
> /* 264 */ uint64 t4;
> /* 272 */ uint64 t5;
> /* 280 */ uint64 t6;
> };
> 
> enum procstate { UNUSED, USED, SLEEPING, RUNNABLE, RUNNING, ZOMBIE };
> 
> // Per-process state
> struct proc {
> struct spinlock lock;
> 
> // p->lock must be held when using these:
> enum procstate state; // Process state
> void *chan;           // If non-zero, sleeping on chan
> int killed;           // If non-zero, have been killed
> int xstate;           // Exit status to be returned to parent's wait
> int pid;              // Process ID
> 
> // wait_lock must be held when using this:
> struct proc *parent; // Parent process
> 
> // these are private to the process, so p->lock need not be held.
> uint64 kstack;               // Virtual address of kernel stack
> uint64 sz;                   // Size of process memory (bytes)
> pagetable_t pagetable;       // User page table
> struct trapframe *trapframe; // data page for trampoline.S
> struct context context;      // swtch() here to run process
> struct file *ofile[NOFILE];  // Open files
> struct inode *cwd;           // Current directory
> char name[16];               // Process name (debugging)
> };
> ```
>
> 看一下这个的源码，还是很清晰的，xv6为每个进程记录了3个状态：
>
> - `context`也即上下文，我们看到就是被调用者保存寄存器（因为）以及ra和sp
>
>   > 因为





作业：

5. 同样运行一组进程：`3:0,5:100,5:100,5:100`，打开`SWTICH_ON_IO`，分别使用`IO_RUN_LATER`/`IO_RUN_IMMEDIATE`会有不同的结果！后者远远更快

   为什么立刻运行一个刚完成IO的进程往往更好？因为它可能还需要请求IO！而IO请求时对应进程阻塞，此时就可以更好地提升并行性

8. 运行一组随机生成的进程：`-s 1 -l 3:50,3:50,



### 5 进程API

api无须说明，不过问题是为何要这样设计？主要原因是在于可以帮助构建UNIX SHELL









### 6 机制：受限直接执行

#### 6.2 受限的操作

显然，为了让程序在CPU上直接运行时受限，这就要求我们引入特权级别。最基本的来说应该至少需要用户模式和内核模式。通过系统调用可以让用户程序进入内核模式，具体来说就是trap指令，跳入内核并将特权级别提升为内核模式，执行对应的特权操作，完成后在调用一个return-from-trap指令返回到发起调用的用户程序

> C库中进行系统调用的部分是用汇编手工编码的，因为对应的convention需要正确地处理参数和返回值以及特定的自陷指令

另一方面，想要确定运行指定位置的OS代码，就需要内核设定好对应的trap table。它需要做的第一件事就是告诉硬件在发生对应的异常时需要运行哪部分代码。而且显然能通过指令告诉硬件这个trap table的位置是一很强大的功能（因为暴露给用户程序就可以执行任意的例程了），所以这自然是一个特权指令了（实际上对应RISC-V就是`csrw mtvec,...`）

基本来说，可以总结出这样一个时间线：（我们假设每个进程都有一个内核栈，进出内核时进行GPR+PC的保存和恢复

![image-20261117130053056](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261117130053056.png)

> 但是我觉得这个表格有一部分让我觉得有点奇怪，硬件并不会自动帮我们将上下文保存到内核栈，而实际上做这件事的使我们内核写好的汇编例程，就像我们xv6的trampoline.S里面的`uservec`干的事情，硬件并不会自动完成这部分内容。
>
> 而当我们使用`ecall`时，实际上正是跳转到这个地方
>
> 不过比如xv6实际上设置了不同的trap处理，因为在内核和在用户态收到中断/异常时需要做的工作不同

这里实际上是两个阶段放到一起了：

1. 系统引导阶段，内核初始化陷阱表，让CPU记住它的位置以供之后使用。内核通过特权指令执行(csr)
2. 运行进程时，在使用陷阱返回指令开始执行进程之前（注意是第一次执行这个进程），则需要对进程进行初始化，在进程列表上分配条目以及分配好内存设置用户页表设置好程序栈（根据argv因为要把参数放到用户栈上）

#### 6.3 进程间切换

##### 协作式

早期的系统采用的是协作的方式，也就是说OS相信系统的进程会合理运行，运行事件过程的进程被假定会定期放弃CPU以便OS可以决定运行其他任务。而具体来说，多数进程实际上是通过系统调用来将CPU的控制权移交CPU的，除了一般有需求的系统调用外这样的系统也会包含一个显式的yield系统调用，不做任何事情仅仅移交控制权以便系统运行

> 处理程序的不当行为
>
> 非法访问内存（那自然是段错误了，段错误的本质就是非法的缺页异常） / 执行非法指令，这应该会让处理器自己触发异常，那么硬件还是按规矩来，和ecall系统调用实际上差不多，但是scause会不一样。而操作系统看到这个异常原因正常来说就会直接kill掉

##### 非协作

计算机系统实际上会采用**时钟中断**，它每隔几毫秒产生一次中断，此时当前正在运行时的进程停止，操作系统中预先配置好的中断处理程序则会运行。此时OS重新获得CPU的控制权，那么也就可以干它想干的事情了：切换进程

##### 保存和恢复上下文

因为切换进程时我们还需要让这个正执行的进程可以恢复，也就是说我们需要保存好上下文了：保存相关寄存器的值到内核栈，并为即将执行的进程恢复一些寄存器的值（从它的内核栈）。
而显然，为了做到这些事情，我们只能通过底层的汇编来搞定：

- 保存好GPR/PC/SP之类的Context
- 恢复Context
- 切换内核栈，供即将运行的进程使用

同样有一个timeline：

![image-20261117140544604](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261117140544604.png)

这个例子中，一开始进程A正在运行，然后被时钟中断，随后硬件首先完成对异常的处理工作（也就是设置好csr跳转+关中断之类的），之后根据汇编例程保存好它的相关上下文（以及别的工作，比如切换页表为内核页表，xv6为了防止直接切换出现段错误的解决方法是让内核页表和用户页表中trampoline的虚拟地址一致且为同一物理页映射），然后进入对应的处理例程（比如xv6的`usertrap()`）如果发现是时钟中断，那么就通过调度器之类的反正最终会调用`swtch`例程，进行上下文切换，再从陷阱返回恢复寄存器并开始运行它

> 这样解释太不清晰了！所以还是....
>
> RTFSC：（xv6的trampoline.S）
>
> ```asm
> #include "riscv.h"
> #include "memlayout.h"
> 
> .section trampsec
> .globl trampoline
> trampoline:
> .align 4
> .globl uservec
> uservec:    
> 	#
>         # trap.c sets stvec to point here, so
>         # traps from user space start here,
>         # in supervisor mode, but with a
>         # user page table.
>         #
> 
>         # save user a0 in sscratch so
>         # a0 can be used to get at TRAPFRAME.
>         csrw sscratch, a0
> 
>         # each process has a separate p->trapframe memory area,
>         # but it's mapped to the same virtual address
>         # (TRAPFRAME) in every process's user page table.
>         li a0, TRAPFRAME
>         
>         # save the user registers in TRAPFRAME
>         sd ra, 40(a0)
>         sd sp, 48(a0)
>         sd gp, 56(a0)
>         sd tp, 64(a0)
>         sd t0, 72(a0)
>         sd t1, 80(a0)
>         sd t2, 88(a0)
>         sd s0, 96(a0)
>         sd s1, 104(a0)
>         sd a1, 120(a0)
>         ...
>         sd a7, 168(a0)
>         sd s2, 176(a0)
>         ...
>         sd s11, 248(a0)
>         sd t3, 256(a0)
>         ...
>         sd t6, 280(a0)
> 
> 	# save the user a0 in p->trapframe->a0
>         csrr t0, sscratch
>         sd t0, 112(a0)
> 
>         # initialize kernel stack pointer, from p->trapframe->kernel_sp
>         ld sp, 8(a0)
> 
>         # make tp hold the current hartid, from p->trapframe->kernel_hartid
>         ld tp, 32(a0)
> 
>         # load the address of usertrap(), from p->trapframe->kernel_trap
>         ld t0, 16(a0)
> 
>         # fetch the kernel page table address, from p->trapframe->kernel_satp.
>         ld t1, 0(a0)
> 
>         # wait for any previous memory operations to complete, so that
>         # they use the user page table.
>         sfence.vma zero, zero
> 
>         # install the kernel page table.
>         csrw satp, t1
> 
>         # flush now-stale user entries from the TLB.
>         sfence.vma zero, zero
> 
>         # call usertrap()
>         jalr t0
> 
> .globl userret
> userret:
>         # usertrap() returns here, with user satp in a0.
>         # return from kernel to user.
> 
>         # flush icache, in case this is the first time
>         # we're running this proc on this hart.
>         fence.i
> 
>         # switch to the user page table.
>         sfence.vma zero, zero
>         csrw satp, a0
>         sfence.vma zero, zero
> 
>         li a0, TRAPFRAME
> 
>         # restore all but a0 from TRAPFRAME
>         ld ra, 40(a0)
>         ...
>         ld t6, 280(a0)
> 
> 	# restore user a0
>         ld a0, 112(a0)
>         
>         # return to user mode and user pc.
>         # prepare_return() sets up sstatus and sepc.
>         sret
> 
> ```
>
> - 首先，显然我们要存放进程的上下文在内核的TRAPFRAME，但是麻烦的是我们的GPR还没保存，但是还需要一个通用寄存器来帮我们lui后寻址进行load保存！因此就需要用到`xscratch`，它的功用就是在此时临时帮我们存放对应寄存器的值（对硬件来说它根本没用！）随后依次把寄存器值放入。然后再从这里面取出kernel的sp/satp/hartid之类的东西（放在一起正是因为此时还在用户态用的也是用户页表之类的），然后就准备切换页表为内核页表了，但是首先我们得保证之前的读写都搞定了（`sfence.vma`）防止出现不应该的缺页错误。之后就更新satp为新的内核页表，再次用`sfence.vma`则会让TLB里面的缓存失效，这样冲刷完成就可以调用`usertrap()`了
> - 从`usertrap()`返回后，刚好下一句就是`userret`，首先`fence.i`冲刷icache（保证icache和dcache一致，因为进程可能被内核修改了代码），然后切换页表为用户页表（同样的流程），然后反过来恢复好上下文，直接`sret`








































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


而且就像我们知道的，哪怕是ISA层面，一条指令仍然不是最小的执行单元，因为处理器会把指令分解为uop：
- 每个周期向池子补充尽可能多的uop，多发射
- 每个周期执行尽可能的uop，乱序执行，通过ROB按序提交
> 不过我还没学过那本体系结构... 之后会更加详细地补充的

而即使满足单处理器`eventual memory consistency`的执行，在多处理器上仍然可能无法序列化
就像刚刚那个程序，多处理器下仍然会都读到0，因为这不违背`cache coherence`，而且本身单个核还有自己的`store buffer`

### 宽松内存模型

几种ISA里面，可以说最严的就是x86了，其次是RISC-V和ARM







## 持久性
