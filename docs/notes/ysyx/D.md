# D阶段记录

>  D1 $\to$ PA2阶段1
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

```assembly
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
