---
draft: false
hiddenInRss: false
searchHidden: false
robotsNoIndex: false
sitemap:
  disable: false
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

## D5 设备和I/O

所谓访问设备，就是读出数据+写入数据+控制状态（实际上单片机基本上就是在干这件事）

而想要实现输入输出，有：

1. 端口映射IO： 也就是我们通过port访问，CPU使用专门的I/O指令对设备进行访问，而设备的地址就是**端口号**，这样只需要给出端口号给IO指令就可以直接完成访问

2. 内存映射(MMIO)：很显然，端口映射不是一种很好的方法，因为端口是写死在指令集里面的，如果I/O设备更多那就会出问题，因此更好的方法是我们直接把对应的设备编址为内存物理地址
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

> 我们之前就接触过了，`mainargs`被传送到`main`里面，但是具体是如何传输的?
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
嗯，前面我们对每个文件都生成了`.o`的可重定位目标文件，其中`CFLAGS`里面就包含了替换操作，也就是说它会找到所有名为``的然后替换为对应的内容，而刚好它就在`trm.c`里面：
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



