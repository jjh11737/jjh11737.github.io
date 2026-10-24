---
title: "D阶段记录"
date: 2026-10-23T00:14:50+08:00
draft: false
hiddenInRss: false
searchHidden: false
robotsNoIndex: false
sitemap:
  disable: false
noteTags: ["ysyx", "Makefile", "汇编"]
---
# D阶段记录

>  D1 -> PA2阶段1
>
> 这部分就不展示了...

## D2 程序的机器级表示

32位常数的装入

我们对于过大的数字，往往会拆为两部分，不可能一步到位（指令本身不允许，所以我们的方法是先lui再addi微调

64位常数的装入

我们会发现有些时候可能还不如写到elf里面直接ld把它装入来的合适

> 指令太多并不好：乱序执行的高性能cpu中，取指令的代价远大于取数据
>
> - 流水线中，指令是数据的上游
> - 从内存取数据只需要让取数逻辑等待即可，可以先去执行别的无关指令
> - 而从内存取指本身需要整条流水线等待...这样会空转的
>
> > 没有新的uop产生我们啥也做不了...

而在rv32中我们干的事情是用两个32位寄存器联合存放一个64位数据



不对齐的变量分配会降低访问效率... 

> 这很简单，支持不对齐访问的硬件会需要更复杂的电路，需要2个周期以上，而用软件支持就需要异常来搞

而rv32处理64位加法，编译器干的事情是把两个寄存器一起看，先低位相加看看有没有溢出（具体判断方法是先提前存好a0然后用sltu处理进位,最后把这个carry加入高位即可）



##### 注意UB

如果发生UB，语义完全等价但可能有不一样的结果

- 有符号整数加法的溢出（不同机器对不同有符号数表示方法的不同导致的，我们难以统一一个确切行为）

- 移位结果超出表示范围

- 整数除零

  > 对于riscv不会报错，给出的是-1...但是对x86这种ISA这是会抛出异常的，此时会报错FPE

而应对UB，正确的应对方法是**sanitizer**（相当于编译器自动插入`assert`），可以在运行时检查问题

> 详见`man gcc`的`fsanitize`





> 关于qemu:
>
> 以及yzh用的是qemu跑的？为了方便我干脆自己也搞了一套
>
> 先[安装toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain)，我这里就装了rv32的，然后用qemu执行时还得指明sysroot：
>
> ```bash
> $ qemu-riscv32 -L /opt/riscv/sysroot ./a.out
> ```

### 函数调用

函数调用需要考虑更多问题，比如：

- 是其他编译器编译的
- 动态链接库
- 汇编代码

显然这很麻烦，我们得考虑用一套共同的约定来约束函数调用在机器级表示的实现细节，这就是所谓**调用约定(calling convention)**，它是ABI的一部分，包含：

- 参数和返回值如何传递
- 控制权如何转移
- 都需要寄存器，如何协商

#### 1 参数和返回值

我们知道$S_{isa}=\{<R,M>\}$，

- 通过$M$传递：

  我们需要一个支持嵌套调用 / 后进先出的数据结构，显然是栈

- 通过$R$传递：

  显然不太好，因为寄存器资源有限，不过$RISC$指令集往往GPR资源丰富，如果能用$R$传递那就优先用它

- RISC-V的[整数调用约定](https://github.com/riscv-non-isa/riscv-elf-psabi-doc/blob/master/riscv-cc.adoc)： `a0`~`a7`用于参数传递，`a0`/`a1`传递返回值

  | 参数长度  |    首选传递方式    |
  | :-------: | :----------------: |
  | `<=XLEN`  |   寄存器, 值传递   |
  | `2*XLEN`  | 一对寄存器, 值传递 |
  | `>2*XLEN` |  寄存器, 引用传递  |

  也就是说我们会优先放到寄存器，如果参数过多就放到栈里面。
  而如果我们RV32想要传递`uint64_t`，只能用一对寄存器了...

  > 低位放在编号较小的寄存器，高位放到编号较大的寄存器，返回值放在`a0`+`a1`

  > 当然同样地RV64里面你也可以用同样方法传递`uint128_t`

  那如果更长一点呢？比如RV32传`long double`，显然我们就必须用栈了

  而关于可变参数，看看这个例子：

  > `stdargs.h`专门用于操作可变参数

  ```c
  #include <stdint.h>
  #include <stdarg.h>
  uint64_t sum(int n, ...) {
    va_list ap;
    va_start(ap, n);
    uint64_t sum = 0;
    for (int i = 0; i < n; i ++) {
      sum += va_arg(ap, uint64_t);
    }
    va_end(ap);
   return sum;
  }
  uint64_t g1() { return sum(1, 0ull); }
  uint64_t g2() { return sum(3, 1ull, 2ull, 3ull); }
  uint64_t g3() { return sum(4, 10ull, 20ull, 30ull, 40ull); }
  ```

  我们看看汇编：
```asm
sum:
.LFB0:
	.cfi_startproc
	addi	sp,sp,-80
	.cfi_def_cfa_offset 80
	sw	ra,44(sp)
	sw	s0,40(sp)
	.cfi_offset 1, -36
	.cfi_offset 8, -40
	addi	s0,sp,48
	.cfi_def_cfa 8, 32
	sw	a0,-36(s0)
	sw	a1,4(s0)
	sw	a2,8(s0)
	sw	a3,12(s0)
	sw	a4,16(s0)
	sw	a5,20(s0)
	sw	a6,24(s0)
	sw	a7,28(s0)
	addi	a5,s0,32
	sw	a5,-40(s0)
	lw	a5,-40(s0)
	addi	a5,a5,-28
	sw	a5,-32(s0)
	sw	zero,-24(s0)
	sw	zero,-20(s0)
	sw	zero,-28(s0)
	j	.L2
.L3:
	lw	a5,-32(s0)
	addi	a5,a5,7
	andi	a5,a5,-8
	addi	a4,a5,8
	sw	a4,-32(s0)
	lw	a0,0(a5)
	lw	a1,4(a5)
	lw	a2,-24(s0)
	lw	a3,-20(s0)
	add	a4,a2,a0
	mv	a6,a4
	sltu	a6,a6,a2
	add	a5,a3,a1
	add	a3,a6,a5
	mv	a5,a3
	sw	a4,-24(s0)
	sw	a5,-20(s0)
	lw	a5,-28(s0)
	addi	a5,a5,1
	sw	a5,-28(s0)
.L2:
	lw	a4,-28(s0)
	lw	a5,-36(s0)
	blt	a4,a5,.L3
	lw	a4,-24(s0)
	lw	a5,-20(s0)
	mv	a0,a4
	mv	a1,a5
	lw	ra,44(sp)
	.cfi_restore 1
	lw	s0,40(sp)
	.cfi_restore 8
	.cfi_def_cfa 2, 80
	addi	sp,sp,80
	.cfi_def_cfa_offset 0
	jr	ra
	.cfi_endproc
.LFE0:
	.size	sum, .-sum
	.align	1
	.globl	g1
	.type	g1, @function
```


#### 2 控制权的转移

- 函数调用：伪指令`jal offset` 等价于`jal ra,offset`，直接跳转到PC+offset，如果目标函数距离大于1MB则需要`auipc+jalr`两条指令（就像我们`lui+addi`一样）
- 函数返回：伪指令`ret`，等价于`jalr zero, ra, 0`，把返回地址`PC+4`写入`$0` ，当然这是无效的，跳转到`ra+0`也就是我们调用后的那个地址



#### 3 寄存器？

我们不能破坏之前的状态，那么有3种状态：

- 用`f`在`g`调用前保存将来会被使用的寄存器到$M$的栈上，也就是调用者保存

  > 显然我们这样全部保存会浪费栈空间，不划算

- 用`g`在使用寄存器前保存，也就是被调用者保存

  > 同上

- 为什么非得这样？我们完全可以规定好保存的责任嘛，一半一半

  > 这是最常用的方案

所以就需要规定调用者保存寄存器 / 被调用者保存寄存器：（下表来自前面提到的官方文档）

| Name      | ABI Mnemonic | Meaning                | Preserved across calls? |
| --------- | ------------ | ---------------------- | ----------------------- |
| x0        | zero         | Zero                   | — (Immutable)           |
| x1        | ra           | Return address         | No                      |
| x2        | sp           | Stack pointer          | Yes                     |
| x3        | gp           | Global pointer         | — (Unallocatable)       |
| x4        | tp           | Thread pointer         | — (Unallocatable)       |
| x5 - x7   | t0 - t2      | Temporary registers    | No                      |
| x8 - x9   | s0 - s1      | Callee-saved registers | Yes                     |
| x10 - x17 | a0 - a7      | Argument registers     | No                      |
| x18 - x27 | s2 - s11     | Callee-saved registers | Yes                     |
| x28 - x31 | t3 - t6      | Temporary registers    | No                      |

我们来解释一下：

- 若生命周期很短，我们就优先使用**临时(temporary) / 参数(argument)**寄存器
- 如果跨越了函数调用，我们优先分配在保存寄存器



顺便复习一下栈：（如果忘了建议读一下CSAPP）

1. 准备阶段：

   - 通过减小`sp`申请栈帧（如果不缺页那就没问题，否则OS要处理缺页异常）
   - 如果需要，保存好调用者保存寄存器的内容到栈帧
   - 若需要，为下一个函数的局部 / 临时变量分配空间

2. 执行阶段：

   如果要调用别的函数，把`ra`保存到栈帧，同时把部分临时寄存器放到保存寄存器，重复第一步

3. 结束阶段：

   - 若需要，从栈帧中恢复保存寄存器和`ra`
   - 增加`sp`释放栈帧
   - `ret`



看一个例子：

```c
#include <stdio.h>
#define N 10
int array[N] = {2, 6, 9, 3, 8, 4, 7, 5, 10, 1};
int min(int *a, int len, int left) { // 叶子函数, 即不会调用其他函数 -> 无需保存ra
  int m = left;                      // 优先使用临时/参数寄存器 -> 无需保存s0~s11
  for (int i = left; i < len; i ++)  // 因此准备阶段无需申请栈桢
    if (a[i] < a[m]) { m = i; }      // 结束阶段只有ret
  return m;
}
void sort(int *a, int len) {      // 非叶子函数, 会调用其他函数
  for (int i = 0; i < len; i++) { // a, len和i在调用min()后仍继续使用
    int m = min(a, len, i);       // 需要将a和len从a0和a1移到保存寄存器
    int tmp = a[i];               // 优先将i分配在保存寄存器
    a[i] = a[m];                  // 因此准备阶段申请栈桢, 保存ra和要用的保存寄存器
    a[m] = tmp;                   // 结束阶段要恢复ra和之前保存的寄存器, 释放栈桢
  }
}
void print_msg() {     // 尾调用(调用后直接返回), 优化成无条件跳转
  printf("output:\n"); // 将ra的保存和恢复工作交给目标函数
}                      // 由目标函数直接返回到当前函数的调用者:
                       // main ==(jal)=> print_msg ==(j)=> printf ==(ret)=> main
void print_array() {            // i在调用printf()后仍继续使用, 优先分配在保存寄存器
  for (int i = 0; i < N; i++)   // 将字符串和array的地址读入到保存寄存器, 在调用printf()后继续使用
    printf("%d\n", array[i]);   // 因此准备阶段申请栈桢, 保存ra和要用的保存寄存器
}                               // 结束阶段要恢复ra和之前保存的寄存器, 释放栈桢
int main () {  // 准备阶段申请栈桢, 保存ra
  sort(array, N); print_msg(); print_array();
  return 0;   // 结束阶段要恢复ra, 释放栈桢
}

```

反汇编结果：（这里没有启用`-M no-aliases`选项）

```asm
0000002c <sort>:
  2c:	04b05863          	blez	a1,7c <.L8>
  30:	8eaa                	mv	t4,a0
  32:	4e01                	li	t3,0

00000034 <.L10>:
  34:	000eaf03          	lw	t5,0(t4)
  38:	87f6                	mv	a5,t4
  3a:	88f2                	mv	a7,t3
  3c:	867a                	mv	a2,t5
  3e:	8772                	mv	a4,t3
  40:	8876                	mv	a6,t4
  42:	00be4963          	blt	t3,a1,54 <.L12>
  46:	a01d                	j	6c <.L13>

00000048 <.L18>:
  48:	0705                	addi	a4,a4,1
  4a:	00650833          	add	a6,a0,t1
  4e:	0791                	addi	a5,a5,4
  50:	00e58e63          	beq	a1,a4,6c <.L13>

00000054 <.L12>:
  54:	4394                	lw	a3,0(a5)
  56:	00289313          	slli	t1,a7,0x2
  5a:	883e                	mv	a6,a5
  5c:	fec6d6e3          	bge	a3,a2,48 <.L18>
  60:	88ba                	mv	a7,a4
  62:	0705                	addi	a4,a4,1
  64:	8636                	mv	a2,a3
  66:	0791                	addi	a5,a5,4
  68:	fee596e3          	bne	a1,a4,54 <.L12>

0000006c <.L13>:
  6c:	00cea023          	sw	a2,0(t4)
  70:	01e82023          	sw	t5,0(a6)
  74:	0e05                	addi	t3,t3,1
  76:	0e91                	addi	t4,t4,4
  78:	fbc59ee3          	bne	a1,t3,34 <.L10>

0000007c <.L8>:
  7c:	8082                	ret
```



#### 4 RISCV的浮点调用约定

和整数调用差不多，`ft0`-`ft11`, `fs0`-`fs11`, `fa0`-`fa7`，但没有`zero`, `ra`, `sp`, `gp`, `tp`

两个编译选项：

- `-march`指定是否使用相应指令和寄存器（决定可以在哪些硬件运行，如果硬件不支持就会抛出“非法指令”异常）
- `-mabi`指定参数传递和引用方式（决定可以链接哪些软件，否则会UB）

> 详细请见：
> [march+mabi+mtune](https://www.sifive.com/blog/all-aboard-part-1-compiler-args)
>
> 

相关约定：

| march\ mabi |                    lp64                     |                    lp64f                    |                    lp64d                    |
| :---------: | :-----------------------------------------: | :-----------------------------------------: | :-----------------------------------------: |
|    rv64i    | f: 软件模拟, 整数传参 d: 软件模拟, 整数传参 |                    非法                     |                    非法                     |
|   rv64if    | f: 硬件指令, 整数传参 d: 软件模拟, 整数传参 | f: 硬件指令, 浮点传参 d: 软件模拟, 整数传参 |                    非法                     |
|   rv64ifd   | f: 硬件指令, 整数传参 d: 硬件指令, 整数传参 | f: 硬件指令, 浮点传参 d: 硬件指令, 整数传参 | f: 硬件指令, 浮点传参 d: 硬件指令, 浮点传参 |





关于结构体：

如果结构体大小不超过XLEN，就按值传递；而如果大小超过了2*XLEN就按引用传递

> look familiar？这其实和之前的传递规则是一样的，如果恰好是在中间我们就通过一对寄存器来传递

以及就像调用时的alignment一样，我们结构体的访问也是要以`word_t`长度为单位对齐的，这个和x86的行为一样

> 为什么要这样？
>
> 很简单，就是效率，如果不对齐，那么后续的数据就可能支离破碎的，需要两个周期可能才能读完一个字段，这蠢透了

关于联合体：

所有成员的地址共享一个，无非就是用何种方式来解析这个地址，这当然就不存在所谓对齐和插空了



我们来分析一个复杂的例子：

可以使用`-ggdb3`这个选项

> 实际上就是`-g`调试，`gdb`代表采用`gdb`的形式，`3`代表级别，这是最高级别

```assembly
test_type.o:     file format elf32-littleriscv


Disassembly of section .text:

00000000 <f>:
typedef union node {
  struct { unsigned char data1[4]; long *ptr; } node1;
  struct { long data2; union node *next; } node2;
} node_t;  // 定义一个包含两种节点类型的链表
void f(node_t *p) {
  p->node2.next->node2.data2 = *(p->node2.next->node1.ptr) + p->node1.data1[2];
   0:	4158                	lw	a4,4(a0)
   # a4 = next

00000002 <.LM4>:
   2:	435c                	lw	a5,4(a4)
   # a5 = next->node1->ptr

00000004 <.LM5>:
   4:	00254683          	lbu	a3,2(a0) 
   # a3 = p->node1.data1[2]

00000008 <.LM6>:
   8:	439c                	lw	a5,0(a5)
   # a5 = *(a5)
   a:	97b6                	add	a5,a5,a3
   # ans
   

0000000c <.LM7>:
   c:	c31c                	sw	a5,0(a4)

0000000e <.LM8>:
//  p->node2.next->node2.data2
//    =
//    *(p->node2.next->node1.ptr)
//    +
//    p->node1.data1[2];
}
   e:	8082                	ret
```



> D2到此结束~



## D3 

现在的处理器已经超复杂了

> 比如我的cpuinfo：
> ```bash
> flags           : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca 
> cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopo
> logy nonstop_tsc cpuid aperfmperf tsc_known_freq pni pclmulqdq dtes64 monit
> or ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid sse4_1 sse4_2 
> x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault intel_ppin ssbd ibrs ibpb stibp ibrs_enhanced t
> pr_shadow flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep b
> mi2 erms invpcid rdt_a rdseed adx smap clflushopt clwb intel_pt sha_ni xsav
> eopt xsavec xgetbv1 xsaves split_lock_detect user_shstk avx_vnni lam wbnoinvd dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp hwp_pkg_re
> q hfi vnmi umip pku ospke waitpkg gfni vaes vpclmulqdq rdpid bus_lock_detec
> t movdiri movdir64b fsrm md_clear serialize arch_lbr ibt flush_l1d arch_cap
> abilities
> 
> ```

怎么设计出来的？自然是一步步迭代出来的

发展的历程：

图灵机

> 我觉得可以参考一下[这篇文章](https://plato.stanford.edu/entries/turing-machine/?utm_source=chatgpt.com#DefiTuriMach)，然后就可以看[图灵的那篇论文](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)，不过Sipser的Ch3也可以看看？
>
> 这篇论文提出了通用图灵机UTM，还证明了计算机领域的能力上限，也就是所谓图灵停机问题：我们无法用一个通用的程序判断任意程序是否会陷入死循环
>
> > 总会有一个`g`让`f`这个判断程序无法正确地判断

冯·诺伊曼计算机

真正可以控制和操作的机器，不再是理论上的计算模型



计算机系统可以说总是有2个诀窍：

- 抽象：我们引入一个抽象层，把复杂性保留在本层级，对上层只需要通过api之类的就能做事情，无须关心这些细节和机制
- 模块化：把机制分模块实现



抽象带来的好处：

- 裸机程序更容易开发，无须关注硬件细节可以和有宿主环境一样

- 更容易懂OS，我们可以先关注核心的东西

  > [Berkeley Boot Loader](https://github.com/riscv-software-src/riscv-pk)，光一个Bootloader就够麻烦了

- 更好调试







## D4 简单的minirv

回顾minirv的ISA规范:

- PC初值为`0`
- GPR数量与RV32E中定义的GPR数量一致
- 支持如下8条指令: `add`, `addi`, `lui`, `lw`, `lbu`, `sw`, `sb`, `jalr`
- 其他的ISA细节与RV32I相同

从指令类型来看, minirv的指令涵盖的功能包括加法, 位拼接, 访存和跳转. 我们可以根据这些功能, 结合处理器的工作流程给NPC划分模块:

- IFU(Instruction Fetch Unit): 负责根据当前PC从存储器中取出一条指令
- IDU(Instruction Decode Unit): 负责对当前指令进行译码, 准备执行阶段需要使用的数据和控制信号
- EXU(EXecution Unit): 负责根据控制信号控制ALU, 对数据进行计算
- LSU(Load-Store Unit): 负责根据控制信号控制存储器, 从存储器中读出数据, 或将数据写入存储器
- WBU(WriteBack Unit): 将数据写入寄存器, 并更新PC

而现在主要是我不想那么复杂，我想指令应该就到IDU这一层，再往后的模块就不要管这方面的内容了！那我的想法是我为什么不自己定义一套内部的微操作的set呢？这样只需要让后续的EXU / LSU / WBU只接受到关于我该如何使用这些数据的事情，而不必关注整条指令，这很明显有很多优势啊？而且再想一下，会发现我们要做的事情总是相同的。而且更进一步，我们把这几个模块分开我认为本身就是为了让他们“干不同的事情”，那么一个很显然的思路就是我完全不应该让这3个模块互相关注别人在做什么，我觉得可以单独为他们各自定义一套指令集合


OK! 现在搞定了我们的minirv，也的确作为npc跑通sum.hex和测试了,那么下一步就是接入am-machine了

首先我先想看看`make ARCH=minirv-npc ALL=dummy run`的结果，不过似乎报错了:
```bash
  + OBJCOPY -> build/dummy-minirv-npc.bin
  /bin/sh: 1: python: not found
  make[1]: *** [.../abstract-machine/scripts/platform/npc.mk:21: insert-arg] Error 127
  test list [1 item(s)]: dummy
  [         dummy] ***FAIL***
```
嗯...这反而是好事，我可以直接找到npc.mk这个文件了，问题在于它用的是`python`但是我电脑上只有`python3`,改一下就好了，看一下`npc.mk`:
```makefile
AM_SRCS := riscv/npc/start.S \
           riscv/npc/trm.c \
           riscv/npc/ioe.c \
           riscv/npc/timer.c \
           riscv/npc/input.c \
           riscv/npc/cte.c \
           riscv/npc/trap.S \
           platform/dummy/vme.c \
           platform/dummy/mpe.c

CFLAGS    += -fdata-sections -ffunction-sections
LDSCRIPTS += $(AM_HOME)/scripts/linker.ld
LDFLAGS   += --defsym=_pmem_start=0x80000000 --defsym=_entry_offset=0x0
LDFLAGS   += --gc-sections -e _start

MAINARGS_MAX_LEN = 64
MAINARGS_PLACEHOLDER = the_insert-arg_rule_in_Makefile_will_insert_mainargs_here
CFLAGS += -DMAINARGS_MAX_LEN=$(MAINARGS_MAX_LEN) -DMAINARGS_PLACEHOLDER=$(MAINARGS_PLACEHOLDER)

insert-arg: image
	@python3 $(AM_HOME)/tools/insert-arg.py $(IMAGE).bin $(MAINARGS_MAX_LEN) $(MAINARGS_PLACEHOLDER) "$(mainargs)"

image: image-dep
	@$(OBJDUMP) -d $(IMAGE).elf > $(IMAGE).txt
	@echo + OBJCOPY "->" $(IMAGE_REL).bin
	@$(OBJCOPY) -S --set-section-flags .bss=alloc,contents -O binary $(IMAGE).elf $(IMAGE).bin

run: insert-arg
	echo "TODO: add command here to run simulation"

.PHONY: insert-arg
```
这里显然`run`就是一个空壳，当我们在`cpu-test`里面调用run的时候实际上就是在调用这里的`run`，而它仅仅是打印一句而已，那么就需要考虑实现

但是问题在于前面的image生成的是`bin`/`elf`/`txt`，那么我们就不用那么麻烦地先转换为hex文件了，完全可以直接fread读取对应的bin文件
具体来说要干这几件事：

- 把ALL每次作为参数传入我们的verilator生成的可执行文件里面
- 修改rtl代码，把pc_init改为0x80000000
- 修改TRM的halt，变成ebreak
    > 这个可以用`asm volatile`搞定

好吧我这里写错了，这里实际上并没有ALL，而是后来被转换为了NAME，对应Makefile.<NAME>，因为Makefile这么写的：
```makefile
Makefile.%: tests/%.c latest
	@/bin/echo -e "NAME = $*\nSRCS = $<\ninclude $${AM_HOME}/Makefile" > $@
```
也就是说，实际上最终可以被接受到的是NAME，那么我们就可以这样传入对应的`.bin`文件了:`$(MAKE) -C $(NPC_HOME) $(CURDIR)/build/$(NAME)-riscv-npc.bin`。
而另一个就是halt，这个在`riscv/npc/trm.c`里面，应该实现为`asm volatile("ebreak)`; 不过还需要判断code，所以应该是`if code==0 ebreak`，否则`while(1)`,调用它的是trap.h里面的check

但是还是老是段错误... 为了方便调试，我直接加了个地址转换的函数`guest_to_host`，它会在错误访问时返回地址
然后我发现居然此时`pc`是0！这就是说明我们还没初始化... 换句话说问题在于我们的verilator还没跑到初始化完成的时候就已经开始试图访问了，所以对于地址为0的情况需要单独处理，可以忽略
```c
static inline uint32_t guest_to_host(uint32_t paddr) {
  if (paddr < BASE) return 0;
  uint32_t off = paddr - BASE;
  if ((off >> 2) >= SIZE_OF_MEM) {
    fprintf(stderr, "ERROR:out-of-bound: addr=0x%08x\n", paddr);
    exit(1);
  }
  return off >> 2;
}

int pmem_read(int addr){
  return MEM[guest_to_host((uint32_t)addr)];
}
void pmem_write(int waddr, int wdata, int wmask){
  uint32_t idx = guest_to_host((uint32_t)waddr);
  uint32_t mask = 0;
  if (wmask & 8) mask |= 0xff000000u;
  if (wmask & 4) mask |= 0x00ff0000u;
  if (wmask & 2) mask |= 0x0000ff00u;
  if (wmask & 1) mask |= 0x000000ffu;
  MEM[idx] &= ~mask;
  MEM[idx] |= (wdata & mask);
}
int fetch_command(int pc){
  return MEM[guest_to_host((uint32_t)pc)];
}
```

而关于判断`HIT GOOD/BAD TRAP`，我的方法比较粗暴，直接看轮数是不是太多了，超过了上限就代表卡死了，或许可以用别的方法？我的想法大概是比如直接统一`ebreak`并且置位寄存器给出返回值

---
> 我之前搞错了！
> 读了一下`nemu.h`，发现正确的`halt`可能还是看返回值合适！（因为我现在的代码只要是碰到`ebreak`就`HIT GOOD TRAP`，这...当然能通过了
> 那么正确的代码应该是：
> ```c
> void halt(int code) {
> //  while (1);
>   asm volatile("mv a0, %0; ebreak" : :"r"(code));   // 参考nemu.h的
>   while(1);
> }
> ```
> 而在rtl里面我们则需要引出寄存器`rf[10]`也就是`a0`的值到顶层，这样最后判断它的值就可以确定对错了
> 不过为了防止死循环，我还是保留了原来的轮数上限的判断

---


## D5 设备和I/O

所谓访问设备，就是读出数据+写入数据+控制状态（实际上单片机基本上就是在干这件事）

而想要实现输入输出，有：

1. **端口映射IO** ： 也就是我们通过port访问，CPU使用专门的I/O指令对设备进行访问，而设备的地址就是**端口号**，这样只需要给出端口号给IO指令就可以直接完成访问

2. **内存映射(MMIO)** ：很显然，端口映射不是一种很好的方法，因为端口是写死在指令集里面的，如果I/O设备更多那就会出问题，因此更好的方法是我们直接把对应的设备编址为内存物理地址
    这样的好处就很大了，我们可以随时扩展，而且几乎不可能需要担心I/O地址的空间不够用，因此risc架构仅支持MMIO的方法

### 状态机视角下的I/O

很显然，I/O的过程关注的就是2个状态，计算机本身的状态机`S=<R,M>`和外部的设备数字电路的状态`D`。后者可以则是通过外部的模拟电路和物理交互的，很显然它不适合建模，而是仅仅对输入输出相关指令的行为本身进行建模：

- 执行普通指令时，状态机按照TRM的模型进行状态转移
- 执行设备输出的相关指令时，状态机除了更新PC什么也不做，而只有设备的状态发生变化
- 执行设备输入的指令时，状态机此时就会branch，因为它的状态不再唯一，必须取决于执行这条指令时设备的状态
![IOE](https://ysyx.oscc.cc/docs/assets/ioe.0b2155cc.png)

无论如何，设备的输入输出都是通过CPU的寄存器来进行数据交互的，输入输出对程序的影响也仅仅体现在输入时会进行一次不能提前确定的状态转移。除此之外对处理器就没有什么别的了

> 当然很显然不是所有数据都要走CPU，就比如通过DMA我们完全可以直接从M搬运到D里面

### NEMU的输入输出

#### 映射方式

NEMU实现了端口映射和内存映射，但无论如何本质都是映射，我们可以统一管理

- 为映射定义了一个结构体类型`IOMap`:
    ```c
    typedef struct {
      const char *name;
      // we treat ioaddr_t as paddr_t here
      paddr_t low;
      paddr_t high;
      void *space;
      io_callback_t callback;
    } IOMap;
    ```
    在`nemu/src/device/io/map.c`里面实现
- `map_read()` / `map_write()`用于将地址`addr`映射到`map`所指示的目标空间并进行访问，会触发响应的回调函数，用于更新对应设备和目标空间的状态
    > 由于nemu本身是单线程的，只能串行地模拟整个计算机系统的工作

#### 设备

`nemu/src/device/device.c`里面包含和SDL库相关的代码，其中`init_device`
- `init_map`初始化
- 对设备进行初始化
- `init_alarm`设置定时器

另一方面，`cpu_exec()`在执行每条指令后都会调用`device_update()`来更新设备状态

### 输入输出抽象为IOE

NEMU的VGA显存放在物理地址`0xa10000000,0xa1080000`范围，但是这是一个不可访问的非法区间(对于native)，这件事应该让AM来管，我们同样只能通过对应的API实现，也即IOE，三个API在`src/native/ioe.c`里面
```c
bool ioe_init() {
  panic_on(cpu_current() != 0, "call ioe_init() in other CPUs");
  panic_on(ioe_init_done, "double-initialization");
  __am_has_ioe = true;
  return true;
}
void ioe_read (int reg, void *buf) { do_io(reg, buf); }
void ioe_write(int reg, void *buf) { do_io(reg, buf); }
```
后两个用于从编号为`reg`的寄存器里面读出内容到缓冲区`buf`，但是这个寄存器并非真实的设备的寄存器，仅仅是作为抽象

- 在`am/include/amdev.h`里面明确了常见设备的寄存器编号和结构
- 在`klib-macros.h`里面进一步把 `ioe_read / write` 封装为了`io_read/write`的宏:
    ```c
    #define io_read(reg) \
      ({ reg##_T __io_param; \
        ioe_read(reg, &__io_param); \
        __io_param; })
    
    #define io_write(reg, ...) \
      ({ reg##_T __io_param = (reg##_T) { __VA_ARGS__ }; \
        ioe_write(reg, &__io_param); })
    ```

因此我们只需要在`abstract-machine/am/src/platform/nemu/ioe/`里面实现一份即可全部共享

#### 串口

最简单的输出设备，`nemu/src/device/serial.c`里面模拟了串口的功能，这里只保留了最基本的数据寄存器，初始化的时候会注册`0x3f8`处长度为8个字节的端口，以及`0xa00003f8`的8字节的MMIO空间，它们都会被映射到串口的数据寄存器上，当cpu向数据寄存器里面写入数据时，它就会将数据传送到主机的stderr里面
> 但是我们之前为什么TRM里面也有自己的putchar? 因为哪怕是图灵机也是需要输出的啊...

`abstract-machine/am/src/platform/nemu/trm.c`里面`putch`就会把字符输出到串口里面

#### `mainargs`是如何传输的
我们之前就接触过了，`mainargs`被传送到`main`里面，但是具体是如何传输的?
实际上我们先前已经接触过了，还记得那个`python`的调用吗？使用的脚本是`abstract-machine/tools/insert-arg.py`:
（它在`abstract-machine/scripts/platform/npc.mk`还是`nemu.mk`里面都调用了一句：
```makefile
17:MAINARGS_PLACEHOLDER = the_insert-arg_rule_in_Makefile_will_insert_mainargs_here
20:insert-arg: image
21:     @python3 $(AM_HOME)/tools/insert-arg.py $(IMAGE).bin $(MAINARGS_MAX_LEN) $(MAINARGS_PLACEHOLDER) "$(mainargs)"
```
这里就是让python来替换，告诉了目标的`.bin`文件/最大长度/placeholder(?)/参数，我们看看它的脚本：
```python
#!/usr/bin/env python3

from sys import argv

bin = argv[1]
max_len = int(argv[2])
placeholder = argv[3]
mainargs = argv[4]

if len(mainargs) >= max_len:
    print("Error: mainargs should not be longer than {0} bytes\n".format(max_len))
    exit(1)
print("mainargs={0}".format(mainargs))

fp = open(bin, 'r+b')
data = fp.read()
idx = data.find(str.encode(placeholder))
if idx == -1:
    print("Error: placeholder not found!\n")
    exit(1)
fp.seek(idx)
mainargs_pad = str.encode(mainargs) + ((max_len - len(mainargs)) * str.encode("\0"))
if len(mainargs_pad) != max_len:
    print("Error: len(mainargs_pad) != max_len\n")
    exit(1)
fp.write(mainargs_pad)
fp.close()
```
我应该看懂了，似乎就是搜索一个占位符，而且可以预期这个就是一个长度固定的静态编译期常量数组，把它当作`main`的输入，而这个脚本干的事情就是在这个已经经过处理后的二进制文件里面找到这个同名的。但是有点不对，这个`.mk`里面的字符串，我`wc -m`了一下，明明长度是57个？前面加了:
```makefile
MAINARGS_MAX_LEN = 64
MAINARGS_PLACEHOLDER = the_insert-arg_rule_in_Makefile_will_insert_mainargs_here
CFLAGS += -DMAINARGS_MAX_LEN=$(MAINARGS_MAX_LEN) -DMAINARGS_PLACEHOLDER=$(MAINARGS_PLACEHOLDER)
```
这个倒是很明确，就是编译时先去替换一下这些内容，但是我还是想搞明白具体发生了什么...
那么就再次`rg`一下，我们知道这里`image: image-dep`要求一个东西，它就在`abstract-machine/Makefile`里面，发现就是`image-dep: $(IMAGE).elf`！也就是说我们需要先生成一个`elf`目标文件，然后在`image`里面`objdump`->`.txt`/`objcopy`->`.bin`，后者应该是经过处理去掉elf头之类的纯粹的指令和只读数据
再看是如何生成`$(IMAGE).elf`的：
```makefile
$(IMAGE).elf: $(LINKAGE) $(LDSCRIPTS)
	@echo \# Creating image [$(ARCH)]
	@echo + LD "->" $(IMAGE_REL).elf
ifneq ($(filter $(ARCH),native),)
	@$(CXX) -o $@ -Wl,--whole-archive $(LINKAGE) -Wl,-no-whole-archive $(LDFLAGS_CXX)
else
	@$(LD) $(LDFLAGS) -o $@ --start-group $(LINKAGE) --end-group
endif
```
 前面我们对每个文件都生成了`.o`的可重定位目标文件，其中`CFLAGS`里面就包含了替换操作，也就是说它会找到所有名为``的然后替换为对应的内容，而刚好它就在`trm.c`里面：
```c
12:static const char mainargs[MAINARGS_MAX_LEN] = TOSTRING(MAINARGS_PLACEHOLDER); // defined in CFLAGS
25:void _trm_init() {
26:  int ret = main(mainargs);
27:  halt(ret);
28:}
```
这方法确实很妙啊！我们这样最后在`_trm_init`里面调用`main`把参数传入就好了！

> 而且实际上，我们最后链接时ld压根就不关心你实现的是什么... 毕竟符号解析时只知道有一个叫`main`的东西然后把它替换为地址罢了，比如一个很搞笑的例子：
> ```c
> // file1.c
> int f(int x);
> int main(){
>     printf("f(1)=%d", f(1));
> }
> // file2.c
> int f(int x, int y, int z){
>     return x + y + z;
> }
> ```
> 我们先分别编译然后链接，然后你就会发现结果完全是随机的...

--------

但是`native`的实现似乎不太一样，这是当然，都跑在linux里面了，直接一个`getenv()`就行了，在`native/platform.c`里面

#### 时钟

不知道为什么，我一开始运行时发现什么都不输出
一开始我认为是我`printf`实现的问题，毕竟我还没有实现`%02d`的匹配，但是我在读取时钟前后分别加了个很简单的`printf`，结果发现就不对了，第二个没有打印，也就是说，我的程序卡在读取这一步了？
```c
  while (1) {
    printf("0\n");
    while(io_read(AM_TIMER_UPTIME).us / 1000000 < sec) ;        // 看来卡在这里了
    rtc = io_read(AM_TIMER_RTC);
    printf("1\n");
```
> 仅仅输出0

 那就得看到底是如何获取了
```c
static void rtc_io_handler(uint32_t offset, int len, bool is_write) {
  assert(offset == 0 || offset == 4);
  if (!is_write && offset == 4) {
    uint64_t us = get_time();
    rtc_port_base[0] = (uint32_t)us;
    rtc_port_base[1] = us >> 32;
  }
}
```
显然，它需要这个`offset==4`，否则就不会读取...? 换句话说，想要触发更新，我们就必须读一次高位才行... 换句话说，即使我们是riscv32,但是为了方便必须先读高位然后不用，再读低位
> 为什么要这样设计？
好吧我还是不太清楚这个到底是如何被调用的，我看了同文件后面，有一句：
```c
43:  add_pio_map ("rtc", CONFIG_RTC_PORT, rtc_port_base, 8, rtc_io_handler);
45:  add_mmio_map("rtc", CONFIG_RTC_MMIO, rtc_port_base, 8, rtc_io_handler);
```
 然后就是回去看`add_mmio_map`了，依旧`rg`：
```c
/* device interface */
void add_mmio_map(const char *name, paddr_t addr, void *space, uint32_t len, io_callback_t callback) {
  assert(nr_map < NR_MAP);
  paddr_t left = addr, right = addr + len - 1;
  if (in_pmem(left) || in_pmem(right)) {
    report_mmio_overlap(name, left, right, "pmem", PMEM_LEFT, PMEM_RIGHT);
  }
  for (int i = 0; i < nr_map; i++) {
    if (left <= maps[i].high && right >= maps[i].low) {
      report_mmio_overlap(name, left, right, maps[i].name, maps[i].low, maps[i].high);
    }
  }

  maps[nr_map] = (IOMap){ .name = name, .low = addr, .high = addr + len - 1,
    .space = space, .callback = callback };
  Log("Add mmio map '%s' at [" FltMT_PADDR ", " FMT_PADDR "]",
      maps[nr_map].name, maps[nr_map].low, maps[nr_map].high);

  nr_map ++;
}
```
很显然，这里是给它绑定了一个`callback`,我们再找一下：
```c
nemu/src/device/io/map.c
45:static void invoke_callback(io_callback_t c, paddr_t offset, int len, bool is_write) {
59:  invoke_callback(map->callback, offset, len, false); // prepare data to read
69:  invoke_callback(map->callback, offset, len, true);
```

无论如何，`time.c`里面的写法确定了，我们可以先读高位然后丢掉，把低位返回：
```c
void __am_timer_uptime(AM_TIMER_UPTIME_T *uptime) {
  inl(RTC_ADDR + 4);
  uptime->us = inl(RTC_ADDR);
}
```

但是很显然... 此时还不能完整显示，因为`%02d`我的`printf`还不能处理（以及`printf`本身也压根没实现）

我的`printf`写法：
为了方便起见，我修改了`stdio.h`的实现，原本的`internal_formatter()`只能往字符串写，而现在我准备传入一个函数指针和另一个指针，这样统一调用这个函数我们就可以复用代码了：
```c
typedef void (*sink_t) (char ch, void *ctx);
static void inline sink_dump(char ch, void *ctx){
  putch(ch);
}
static void inline sink_buf(char ch, void *ctx) {
  *(char *)ctx = ch;
}
static int internal_formatter(sink_t out, void *ctx, size_t n, const char *fmt, va_list ap){
```

----
> 好吧我承认我的实现有问题... 如果一个个的写入，怎么想都会很麻烦啊，虽然我写好了对应的format的parse部分，但是碰到输出部分我可是一点也不想写了... 在连续3天打开一点也不想动之后，我决定还是改一下好了

然后先处理decimal的输出，大概要注意的规则：
- 有了`-`左对齐/ 指定了precision时， `0`会自动失效，也就是说补零只会在左边
总算实现了！



然后就是想办法让几个演示程序运行起来，嗯... 要求是借助提供的堆实现，而`malloc`的行为应该就是：如果没有初始化那就初始化为`heap.start`，否则变成上一次分配内存的尾部。
无论如何，最重要的还是RTFSC，先找一下`heap`：
```bash
abstract-machine/am/src/platform/nemu/trm.c
4:extern char _heap_start;
7:Area heap = RANGE(&_heap_start, PMEM_END);
```
在看一下`Area`：
```bash
abstract-machine/klib/include/klib-macros.h
7:#define RANGE(st, ed)       (Area) { .start = (void *)(st), .end = (void *)(ed) }
abstract-machine/am/include/am.h
// Memory area for [@start, @end)
typedef struct {
  void *start, *end;
} Area;
```


#### 实现Dtrace：
这个很简单，反正每次调用时打印一下就好了，一路找过去我感觉还是`map.c`里面合适：
```c
word_t map_read(paddr_t addr, int len, IOMap *map) {
  assert(len >= 1 && len <= 8);
  check_bound(map, addr);
  paddr_t offset = addr - map->low;
  invoke_callback(map->callback, offset, len, false); // prepare data to read
  word_t ret = host_read(map->space + offset, len);
  #if  defined (CONFIG_DTRACE)
    printf("READING: %s, DATA: %-d, LENGTH: %d\n", map->name, ret, len); 
  #endif 
  return ret;
}
void map_write(paddr_t addr, int len, word_t data, IOMap *map) {
  assert(len >= 1 && len <= 8);
  check_bound(map, addr);
  #if  defined (CONFIG_DTRACE)
    printf("WRITING: %s, DATA: %-d, LENGTH: %d\n", map->name, data, len); 
  #endif 

  paddr_t offset = addr - map->low;
  host_write(map->space + offset, len, data);
  invoke_callback(map->callback, offset, len, true);
}
```

#### 键盘

还是要实现一个对应的函数，我们还是先看看宏是怎么定义的：
```c
abstract-machine/am/include/amdev.h
#define AM_DEVREG(id, reg, perm, ...) \
  enum { AM_##reg = (id) }; \
  typedef struct { __VA_ARGS__; } AM_##reg##_T;
AM_DEVREG( 8, INPUT_KEYBRD, RD, bool keydown; int keycode);
```
根据宏的定义这里就很显然了，这个`AM_INPUT_KEYBRD`的结构体含有`keydown`和`keycode`

但是如何读取呢？首先在`keyboard.c`里面我们发现好像只有一个函数不是`static`的...
```c
void send_key(uint8_t scancode, bool is_keydown) {
  if (nemu_state.state == NEMU_RUNNING && keymap[scancode] != NEMU_KEY_NONE) {
    uint32_t am_scancode = keymap[scancode] | (is_keydown ? KEYDOWN_MASK : 0);
    key_enqueue(am_scancode);
  }
}
```
它干的事情就是把这个按键入队，那何时读取的？
实际上在device.c里面的`device_update`里面。反正无论如何跟我们无关了，应该是通过SDL实现的，总之就是SDL碰到按键的事件

```c
// nemu/src/device/device.c 这是在`device_update`里面的
#ifdef CONFIG_HAS_KEYBOARD
      // If a key was pressed
      case SDL_KEYDOWN:
      case SDL_KEYUP: {
        uint8_t k = event.key.keysym.scancode;
        bool is_keydown = (event.key.type == SDL_KEYDOWN);
        send_key(k, is_keydown);
        break;
      }
#endif
```
而同样它也是最后调用了：
```c
  add_mmio_map("keyboard", CONFIG_I8042_DATA_MMIO, i8042_data_port_base, 4, i8042_data_io_handler);
```
额... 好吧，应该还是通过类似的方法读取吧？很显然这里只是一个长度为4也就是32bit的数据，在am里面用`inl`就能读取
但是我怎么识别呢...我感觉我的上下文不够用了

----
那就先理一下思路！首先我们要先搞清楚整个设备初始化的流程：
首先，任何设备的初始化都是从这里开始的：
```c
// nemu/src/device/device.c
void init_device() {
  IFDEF(CONFIG_TARGET_AM, ioe_init());
  init_map();

  IFDEF(CONFIG_HAS_SERIAL, init_serial());
  IFDEF(CONFIG_HAS_TIMER, init_timer());
  IFDEF(CONFIG_HAS_VGA, init_vga());
  IFDEF(CONFIG_HAS_KEYBOARD, init_i8042());
  IFDEF(CONFIG_HAS_AUDIO, init_audio());
  IFDEF(CONFIG_HAS_DISK, init_disk());
  IFDEF(CONFIG_HAS_SDCARD, init_sdcard());

  IFNDEF(CONFIG_TARGET_AM, init_alarm());
}
```
它会在`monitor.c`里面被调用，而他本身又调用了am里面的`ioe_init()`，它干的事情是检查一下`lut`查找表，把不需要的项设为`fail`（这样如果碰到访问就会报错），然后初始化一些设备

---

然后还是回到keyboard上，我们首先看一下这个宏吧？
```c
// nemu/src/device/keyboard.c
#define NEMU_KEYS(f) \
  f(ESCAPE) f(F1) f(F2) f(F3) f(F4) f(F5) f(F6) f(F7) f(F8) f(F9) f(F10) f(F11) f(F12) \
f(GRAVE) f(1) f(2) f(3) f(4) f(5) f(6) f(7) f(8) f(9) f(0) f(MINUS) f(EQUALS) f(BACKSPACE) \
f(TAB) f(Q) f(W) f(E) f(R) f(T) f(Y) f(U) f(I) f(O) f(P) f(LEFTBRACKET) f(RIGHTBRACKET) f(BACKSLASH) \
f(CAPSLOCK) f(A) f(S) f(D) f(F) f(G) f(H) f(J) f(K) f(L) f(SEMICOLON) f(APOSTROPHE) f(RETURN) \
f(LSHIFT) f(Z) f(X) f(C) f(V) f(B) f(N) f(M) f(COMMA) f(PERIOD) f(SLASH) f(RSHIFT) \
f(LCTRL) f(APPLICATION) f(LALT) f(SPACE) f(RALT) f(RCTRL) \
f(UP) f(DOWN) f(LEFT) f(RIGHT) f(INSERT) f(DELETE) f(HOME) f(END) f(PAGEUP) f(PAGEDOWN)

#define NEMU_KEY_NAME(k) NEMU_KEY_ ## k,

enum {
  NEMU_KEY_NONE = 0,
  MAP(NEMU_KEYS, NEMU_KEY_NAME)
};
```
而我们知道`MAP`宏是长这样的：
```c
#define MAP(c, f) c(f)
```

当我们这里调用`MAP(NEMU_KEYS, NEMU_KEY_NAME)`时，它首先被展开为了：
```c
NEMU_KEYS(NEMU_KEY_NAME)
```
而再被继续展开：
```c
NEMU_KEY_NAME(ESCAPE) NEMU_KEY_NAME(F1)....
```
而再被展开：
```c
NEMU_KEY_ESCAPE, NEMU_KEY_F1, ...
```
结果实际上就是在`enum`里面定义了一系列枚举罢了。而在AM里面也有一套自己的：
```c
#define AM_KEYS(_) \
  _(ESCAPE) _(F1) _(F2) _(F3) _(F4) _(F5) _(F6) _(F7) _(F8) _(F9) _(F10) _(F11) _(F12) \
  _(GRAVE) _(1) _(2) _(3) _(4) _(5) _(6) _(7) _(8) _(9) _(0) _(MINUS) _(EQUALS) _(BACKSPACE) \
  _(TAB) _(Q) _(W) _(E) _(R) _(T) _(Y) _(U) _(I) _(O) _(P) _(LEFTBRACKET) _(RIGHTBRACKET) _(BACKSLASH) \
  _(CAPSLOCK) _(A) _(S) _(D) _(F) _(G) _(H) _(J) _(K) _(L) _(SEMICOLON) _(APOSTROPHE) _(RETURN) \
  _(LSHIFT) _(Z) _(X) _(C) _(V) _(B) _(N) _(M) _(COMMA) _(PERIOD) _(SLASH) _(RSHIFT) \
  _(LCTRL) _(APPLICATION) _(LALT) _(SPACE) _(RALT) _(RCTRL) \
  _(UP) _(DOWN) _(LEFT) _(RIGHT) _(INSERT) _(DELETE) _(HOME) _(END) _(PAGEUP) _(PAGEDOWN)

#define AM_KEY_NAMES(key) AM_KEY_##key,
enum {
  AM_KEY_NONE = 0,
  AM_KEYS(AM_KEY_NAMES)
};
```
完全一致！也就是说，我们只需要通过它的`keycode`就能直接得知！

那`am_test`里面的`key_board.c`是怎么输出的？
```c
#define NAMEINIT(key)  [ AM_KEY_##key ] = #key,
static const char *names[] = {
  AM_KEYS(NAMEINIT)
};
```
注意到这里的`#key`，它的作用就是把一个符号转换为字符串。换句话说这样我们就生成了一个查找表！！

> NEMU的宏确实用的超好啊

那还剩最后有一个问题了, 我该如何解析呢？
实际上还是要回到`send_key`函数，它会把这个`code`或上`KEYDOWN_MASK`
所以我们解析时先得处理`KEYDOWN_MASK`，然后把它送给`AM_INPUT_KEYBRD_T *kbd`
看一下同目录的`include/nemu.h`：
```c
#define KBD_ADDR        (DEVICE_BASE + 0x0000060)
```
然后读取自然就是调用对应ISA的读取的函数了，riscv就是在`riscv/riscv.h`：
```c
static inline uint8_t  inb(uintptr_t addr) { return *(volatile uint8_t  *)addr; }
static inline uint16_t inw(uintptr_t addr) { return *(volatile uint16_t *)addr; }
static inline uint32_t inl(uintptr_t addr) { return *(volatile uint32_t *)addr; }
```
再看一下`amdev.h`，里面注册时给的是:
```c
AM_DEVREG( 8, INPUT_KEYBRD, RD, bool keydown; int keycode);
```
那么代码就是：
```c
void __am_input_keybrd(AM_INPUT_KEYBRD_T *kbd) {
    uint32_t event = inl(KBD_ADDR);
    kbd->keydown = !!(event & KEYDOWN_MASK);
    kbd->keycode = event & ~KEYDOWN_MASK;
}
```


#### VGA

在`amdev.h`里面定义了5个：
```c
AM_DEVREG( 9, GPU_CONFIG,   RD, bool present, has_accel; int width, height, vmemsz);
AM_DEVREG(10, GPU_STATUS,   RD, bool ready);
AM_DEVREG(11, GPU_FBDRAW,   WR, int x, y; void *pixels; int w, h; bool sync);
AM_DEVREG(12, GPU_MEMCPY,   WR, uint32_t dest; void *src; int size);
AM_DEVREG(13, GPU_RENDER,   WR, uint32_t root);
```

但是VGA还有2个寄存器，屏幕大小寄存器和同步寄存器，我们需要实现它们，但是... 我还是不太明白nemu和am是怎么交互的，所以依旧RTFSC！

首先是关于VGA的大小，我们可以很明显地看到现在的am里面并没有正确地实现，也就是`__am_gpu_config`里面，初始化给的还是0！那么我们看nemu里面的确已经实现了，`vga.c`里面有这个相关的实现并且已经在`init_vga`里面实现了！那么接下来的想法就是怎么让am知道？
先RTFSC，看一下`init_vga`：
```c
void init_vga() {
  vgactl_port_base = (uint32_t *)new_space(8);
  vgactl_port_base[0] = (screen_width() << 16) | screen_height();
#ifdef CONFIG_HAS_PORT_IO
  add_pio_map ("vgactl", CONFIG_VGA_CTL_PORT, vgactl_port_base, 8, NULL);
#else
  add_mmio_map("vgactl", CONFIG_VGA_CTL_MMIO, vgactl_port_base, 8, NULL);
#endif

  vmem = new_space(screen_size());
  add_mmio_map("vmem", CONFIG_FB_ADDR, vmem, screen_size(), NULL);
  IFDEF(CONFIG_VGA_SHOW_SCREEN, init_screen());
  IFDEF(CONFIG_VGA_SHOW_SCREEN, memset(vmem, 0, screen_size()));
}
```
很明显，这个作为mmio被注册为`CONFIG_VGA_CTL_MMIO`，这看起来像是Kconfig定义的，那么我们应该`rg`搜索`VGA_CTL_MMIO`！
```bash
src/device/Kconfig
78:config VGA_CTL_MMIO
79:  hex "MMIO address of the VGA controller"
80:  default 0xa0000100
```
回到`nemu.h`里面，发现刚好就是这个地址！（但是这样设计我一方改了不会出问题吗）
```c
#define VGACTL_ADDR     (DEVICE_BASE + 0x0000100)
```
那么就很简单了，我们只需要读取`VGACTL_ADDR`即可获取！
但是`height`和`width`知道了，size怎么算呢？nemu里面定义的是`screen_width()*screen_height()*sizeof(uint32_t)`，而且我们现在也的确没有地方消费这个`.vmemsz`，和nemu保持一致就好

```c
void __am_gpu_config(AM_GPU_CONFIG_T *cfg) {
  uint32_t wh = inl(VGACTL_ADDR); 
  *cfg = (AM_GPU_CONFIG_T) {
    .present = true, .has_accel = false,
    .width = (wh >> 16), .height = (wh & 0xffff),
    .vmemsz = (wh >> 16) * (wh & 0xffff) * sizeof(uint32_t)
  };
}
```
然后就是实现同步了，这个在am里面已经搞定了，要做的是在nemu里面检查`sync`是否就绪，我们知道在AM里面写的是：
```c
void __am_gpu_fbdraw(AM_GPU_FBDRAW_T *ctl) {
  if (ctl->sync) {
    outl(SYNC_ADDR, 1);
  }
}
```
`SYNC = VGACTL_ADDR + 4 = CONFIG_VGA_CTL_MMIO + 4 = vgactl_port_base[1]`，那么我们只需要管这一位即可
然后就是`__am_gpu_init`了！显然因为是`init`，我们不能像`am_test`里面一样依赖`io_read`读取GPU config，所以正确的做法还是和刚才一样读取`VGACTL_ADDR`

最后显示如下：
![image-20261023111545705](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261023111545705.png)

这些都搞定了，那么接下来就是真正实现`__am_gpu_fbdraw`了，因为我们这里仅仅是判断了`sync`，并没有真正做什么，所以很自然`am_test`不会生效。而它传入的是：`AM_DEVREG(11, GPU_FBDRAW,   WR, int x, y; void *pixels; int w, h; bool sync);`，这部分没啥好说，照着写就好了：

```c
void __am_gpu_fbdraw(AM_GPU_FBDRAW_T *ctl) {
  // first we should check the validness of input
  if (ctl->pixels != NULL && ctl->w > 0 && ctl->h > 0) {
    // then, get the screen size
    int wh = inl(VGACTL_ADDR);
    int screen_w = wh >> 16;
    int screen_h = wh & 0xffff;
    // then, get the i/o buffer
    uint32_t *fb = (uint32_t *)(uintptr_t)FB_ADDR;
    uint32_t *src = ctl->pixels;
    // draw!
    for(int r = 0; r < ctl->h; r++){
      int y = r + ctl->y;
      if (y < 0 || y >= screen_h) continue;
      for(int c = 0; c < ctl->w; c++){
         int x = c + ctl->x;
         if(x < 0 || x >= screen_w) continue;
         fb[y * screen_w + x] = src[r * ctl->w + c];
      }
    }
  }
  if (ctl->sync) {
    outl(SYNC_ADDR, 1);
  }
}
```

最后还是：

![image-20261023114101291](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261023114101291.png)

就可以跑mario了，不过注意要把debug的选项关掉，否则会超级卡！
![image-20261023115412410](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261023115412410.png)


#### 声卡

先看NEMU侧:

首先我们还是通过SDL库的api来实现，想要播放音频需要：
- `SDL_OpenAudio()`初始化音频子系统，需要提供频率/格式
- 初始化后，就会调用注册时的回调函数

而NEMU的简单声卡会在初始化时注册`0xa0000200`处的24字节的MMIO空间，它们都会映射到寄存器里面，而流缓冲区作为MMIO被注册在了`0xa1200000`长度为64KB
```c
// nemu.h
#define AUDIO_ADDR      (DEVICE_BASE + 0x0000200)
#define AUDIO_SBUF_ADDR (MMIO_BASE   + 0x1200000)
```

再看AM侧:
`amdev.h`定义了这几个抽象寄存器：
```c
AM_DEVREG(14, AUDIO_CONFIG, RD, bool present; int bufsize);
AM_DEVREG(15, AUDIO_CTRL,   WR, int freq, channels, samples);
AM_DEVREG(16, AUDIO_STATUS, RD, int count);
AM_DEVREG(17, AUDIO_PLAY,   WR, Area buf);
```
看一下测试里面调用的函数：
```c
void audio_test() {
  if (!io_read(AM_AUDIO_CONFIG).present) {
    printf("WARNING: %s does not support audio\n", TOSTRING(__ARCH__));
    return;
  }

  io_write(AM_AUDIO_CTRL, 8000, 1, 1024);               

  extern uint8_t audio_payload, audio_payload_end;
  uint32_t audio_len = &audio_payload_end - &audio_payload;
  int nplay = 0;
  Area sbuf;
  sbuf.start = &audio_payload;
  while (nplay < audio_len) {
    int len = (audio_len - nplay > 4096 ? 4096 : audio_len - nplay);
    sbuf.end = sbuf.start + len;
    io_write(AM_AUDIO_PLAY, sbuf);
    sbuf.start += len;
    nplay += len;
    printf("Already play %d/%d bytes of data\n", nplay, audio_len);
  }

  // wait until the audio finishes
  while (io_read(AM_AUDIO_STATUS).count > 0);
}
```

很显然我们应该先从NEMU侧开始，先看`Kconfig`：
```Kconfig
if HAS_AUDIO
config SB_ADDR
  hex "Physical address of the audio stream buffer"
  default 0xa1200000

config SB_SIZE
  hex "Size of the audio stream buffer"
  default 0x10000

config AUDIO_CTL_MMIO
  hex "MMIO address of the audio controller"
  default 0xa0000200
endif # HAS_AUDIO
```
然后看看`device/audio.c`，我觉得这里有一个地方写的很有意思，枚举的最后一个刚好就等于寄存器的数量
```c
enum {
  reg_freq,
  reg_channels,
  reg_samples,
  reg_sbuf_size,
  reg_init,   
  reg_count,
  nr_reg        // 相当于就是寄存器的数量！
};
```
而看一下，`audio_io_handler()`作为回调函数还是一个空壳，而`init_audio()`里面仅仅是完成了MMIO的分配，前三个和`reg_init`我们没法初始化，毕竟是用户指定后才行
那我们应该只需要把`reg_sbuf_size`设为`CONFIG_SB_SIZE`，把`reg_count`设为0表示还没有数据

那么之后的`audio_io_handler`负责的应该就是对不同寄存器的读写做出反应。首先很显然就是先得搞定初始化，我们定义好了写入`init`就代表可以进行初始化了，可以参考`native`里面的实现，首先我们看一下被`SDL_OpenAudio`要求的`SDL_AudioSpec`：
```c
typedef struct SDL_AudioSpec
{
    int freq;                   /**< DSP frequency -- samples per second */
    SDL_AudioFormat format;     /**< Audio data format */
    Uint8 channels;             /**< Number of channels: 1 mono, 2 stereo */
    Uint8 silence;              /**< Audio buffer silence value (calculated) */
    Uint16 samples;             /**< Audio buffer size in sample FRAMES (total samples divided by channel count) */
    Uint16 padding;             /**< Necessary for some compile environments */
    Uint32 size;                /**< Audio buffer size in bytes (calculated) */
    SDL_AudioCallback callback; /**< Callback that feeds the audio device (NULL to use SDL_QueueAudio()). */
    void *userdata;             /**< Userdata passed to callback (ignored for NULL callbacks). */
} SDL_AudioSpec;
```
那么主要是`callback`，它的描述是给音频设备喂数据，我们看一下这个函数的接口定义：
```c
typedef void (SDLCALL * SDL_AudioCallback) (void *userdata, Uint8 * stream, int len);
```
嗯，它的行为看起来就是搬运数据，而我们还是参考native的实现，就不把`sbuf`作为userdata对外暴露，而看看native给的实现：（我就不去官方源码里面找要求了）
```c
static void audio_play(void *userdata, uint8_t *stream, int len) {
  int nread = len;
  if (count < len) nread = count;
  int b = 0;
  while (b < nread) {
    int n = read(rfd, stream, nread);
    if (n > 0) b += n;
  }

  count -= nread;
  if (len > nread) {
    memset(stream + nread, 0, len - nread);
  }
}
```
具体来说，就是先确定要读取的长度，这个和native是一致的，然后同样是循环队列里面读取直到读了`nread`个，之后判断如果还不够，剩下的全置零，但是要注意还得让`reg_count`更新，否则am不知道这里被消费了，总之我这么写：
```c
static void audio_play(void *userdata, uint8_t *stream, int len){
  int nread = audio_base[reg_count];
  if(len < nread) nread = len;
  int b = 0;
  while (b < nread) {
    // 保证不越界访问同时次数小于等于剩余要写的次数
    int num = CONFIG_SB_SIZE - read_pos;
    if ((nread - b) < num) num = nread - b;
    memcpy(stream + b, sbuf + read_pos, num);
    b += num;
    read_pos = (read_pos + num) % CONFIG_SB_SIZE;
  }
  audio_base[reg_count] -= nread;
  if (len > nread){
    memset(stream + nread, 0, len - nread);
  }
}
```
