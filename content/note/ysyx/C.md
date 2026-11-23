---
title: "C阶段"
date: 2026-11-02T16:25:54+08:00
draft: false
noteTags: ["ysyx"]
---

# C阶段记录

## PA2-2 基础设施

### TRACE
1. iringbuf：

    也就是说在我们程序HIT BAD TRAP的地方，把前后的指令打印出来

    这个没啥难的，唯一叫我讨厌的大概是对齐了...因为用了制表符，如果偏偏前面指令名长度差异太大就会最后hex部分没法对齐

    这里出现链接错误了，看来是我rtfsc不充分，那就需要看看make发生了什么
    ```bash
    正在读入 makefiles...
    make: 进入目录“/mnt/data1/0ysyx/ysyx-workbench/nemu”
    正在更新 makefile....
    更新目标....
     文件“run”不存在。
      文件“run-env”不存在。
       文件“/mnt/data1/0ysyx/ysyx-workbench/nemu/build/riscv32-nemu-interpreter”不存在。
      必须重新制作目标“/mnt/data1/0ysyx/ysyx-workbench/nemu/build/riscv32-nemu-interpreter”。
    + LD /mnt/data1/0ysyx/ysyx-workbench/nemu/build/riscv32-nemu-interpreter
    /usr/bin/ld: /mnt/data1/0ysyx/ysyx-workbench/nemu/build/obj-riscv32-nemu-interpreter/src/cpu/cpu-exec.o: in function `cpu_exec':
    cpu-exec.c:(.text+0x5ad): undefined reference to `disassemble'
    collect2: error: ld returned 1 exit status
    make: *** [/mnt/data1/0ysyx/ysyx-workbench/nemu/scripts/build.mk:55：/mnt/data1/0ysyx/ysyx-workbench/nemu/build/riscv32-nemu-interpreter] 错误 1
    make: 离开目录“/mnt/data1/0ysyx/ysyx-workbench/nemu”
    ```
    问题是在我关闭ITRACE后发现的，那就说明这个问题应该和它相关的选项有关，查看一下：
    ```bash
    nemu/include/cpu/decode.h
    26:  IFDEF(CONFIG_ITRACE, char logbuf[128]);
    
    nemu/Makefile
    51:CFLAGS_TRACE += -DITRACE_COND=$(if $(CONFIG_ITRACE_COND),$(call remove_quote,$(CONFIG_ITRACE_COND)),true)
    
    nemu/src/utils/filelist.mk
    16:ifeq ($(CONFIG_ITRACE)$(CONFIG_IQUEUE),)
    
    nemu/src/monitor/monitor.c
    131:  IFDEF(CONFIG_ITRACE, init_disasm());
    ```
    看来是我忘记改filelist.mk了，这里disasm.c只有在需要的时候才会被编译进来... 也就是说大概我还得单独写一个`IRINGBUF`。而且这里的`monitor.c`也需要修改，否则会报错的



2. mtrace：
    这个反正加两句log和Kconfig即可
3. ftrace

    首先是确定如何识别call和ret，在risv32里面能做到这件事的只有`jal`/`jalr`

    根据calling convention，一般在call之前都会先存好`%ra`(x1)这个返回地址，对jal / jalr都一样，而ret必须是jalr，往往rd是zero，跳转的来源是`0(ra)`

    但是好像还有麻烦... 因为我们知道riscv是有C扩展的，比如我的电脑里面用riscv32-unknown-linux-gnu-gcc生成的`ret`是压缩指令`0x8082`，所以还得回去看看AM的编译器`march`，看起来应该只开了`zicsr`。那么处理就方便多了。
    > 尽管如此，不知道为什么在我自己尝试的时候发现总是不对，我用`riscv32-unknown-linux-gnu-gcc`明明指定了`march`不包含C扩展，也在objdump时没开`-M no-aliases`，但是还是出现了`c.jr`的指令？我看了一下`.o`文件却没有使用任何C扩展的指令，这好奇怪啊

    算了，先实现再说，我们在`monitor.c`里面已经有了parse_arg，所以只需要把名字变一下就是我们需要的elf文件了。我认为并不需要我们再专门开一个数据结构记录这些，毕竟符号表已经摆在那里了不是吗？需要时直接通过fd找一下就好了，因此我们只需要第一遍读取时定位到.symtab和关联的字符串表.strtab即可

    那么第一步就是读取对应的elf文件，然后根据Section Table定位到symtab，根据它建立我们的映射表即可。
    > 我感觉只看`man 5 elf`帮助很有限，`elf.h`效果也一般，为什么不读读别人的实现呢？比如[这个](https://github.com/TheCodeArtist/elf-parser.git)（虽然我认为这个代码写的有些地方也有些糟糕）
    根据ELF头，查手册知道:
    ```c
   #define EI_NIDENT 16
   
   typedef struct {
       unsigned char e_ident[EI_NIDENT];
       uint16_t      e_type;
       uint16_t      e_machine;
       uint32_t      e_version;
       ElfN_Addr     e_entry;
       ElfN_Off      e_phoff;
       ElfN_Off      e_shoff;
       uint32_t      e_flags;
       uint16_t      e_ehsize;
       uint16_t      e_phentsize;
       uint16_t      e_phnum;
       uint16_t      e_shentsize;
       uint16_t      e_shnum;
       uint16_t      e_shstrndx;
   } ElfN_Ehdr;
   ```
    首先我们自然要先判断这个开头的魔数对不对了，总之就是先`pread`进来看看就行。我们知道ELF的魔数就是`7f`开头，剩下几个数字刚好就是`ELF`对应的ASCII码，只需要检验到：`  Magic:   7f 45 4c 46`前四位即可！为了方便起见，我就直接`strncmp`再利用转义字符了。
    > 可以直接用`"\177ELF"`和前4位对比即可

    然后则是定位到Section Table，它由`e_shoff`定义，也就是说只需要读取到对应的偏移即可，而`e_shentsize`则定义了一条Section Table条目的大小，那么基于此我们就可以依次遍历整个Section Table来寻找我们的.symtab了:
    ```c
   typedef struct {
       uint32_t   sh_name;
       uint32_t   sh_type;
       uint32_t   sh_flags;
       Elf32_Addr sh_addr;
       Elf32_Off  sh_offset;
       uint32_t   sh_size;
       uint32_t   sh_link;
       uint32_t   sh_info;
       uint32_t   sh_addralign;
       uint32_t   sh_entsize;
   } Elf32_Shdr;
    ```
    只需要遍历整个section table，找到匹配`SHT_SYM`的就行，至于`.strtab`则压根不用找，因为我们知道`sh_link`指向的就是和它关联的符号表，总之逐个比较`sh_type`即可

    然后就是函数调用的追踪了，在`inst.c`里面执行指令时判定即可，实际上看反汇编发现确认ret只需要保证当前指令为`0x8067`即可（所以还是开了C扩展？），call判定`rd==1`即可。需要注意由于ret和call不一定匹配，所以实际上ret时应该首先遍历函数确定当前语句在哪个函数内部才能确定，这个我们只需要在一开始遍历符号表时记录一下函数的size即可，因为它定义为：
    ```c
   typedef struct {
       uint32_t      st_name;
       Elf32_Addr    st_value;
       uint32_t      st_size;
       unsigned char st_info;
       unsigned char st_other;
       uint16_t      st_shndx;
   } Elf32_Sym;
    ```

### 基础设施

我们之所以在AM中引入native，正是因为机器永远是对的。我们的AM本身应该是架构无关的，那么先在native上找到am的问题才会更方便我们确定问题（因为nemu和am都是我们自己实现的），这就是difftest的思路，借助一个我们可以相信为“永远是对的”（native真机）来通过差分测试找到问题所在！

关于KLIB链接的实现：






## 实现单周期RV32ENPC

首先仍然需要先搭建好完善的基础设施，我想我们已经很清楚了基础设施能帮助我们更加高效地debug，可以对比一下在F阶段通过logisim搭建处理器...我个人认为的确是很不方便的





首先先RTFM，RV32E的标准是：

- 通用寄存器为0~15
- 除此之外和RV32I一致



关于具体的硬件设计：

- 加法器采用CLA即可，不过可以分组CLA
- 移位可以用桶形移位寄存器
- 


## PA3

总算到PA3了！

### 批处理系统

程序之间的执行流切换是OS带来的新的需求。不过从根本来说，执行流切换的本质就是修改PC和上下文即可。而显然操作系统需要尽可能不崩溃，那么仅仅依赖`call`/`ret`来进行操作系统和用户进程之间的切换就很不足了，因为我们并不希望用户程序能自由地将执行流切换到操作系统中的任意函数，也就是说我们需要对入口进行限制

为了实现这一点，就引入了保护机制，所谓特权级。只有高特权级的程序才能执行一些系统级别的操作，如果有特权较低的程序尝试执行它没有权限执行的操作，CPU就会抛出一个异常信号来阻止这一非法行为的发生。

而RISC-V提供了3个特权级别：机器模式M / 监控者模式S / 用户模式U。而CPU想要判定权限，只需要在硬件上维护一个用于标识当前特权模式的寄存器，然后在访问高特权级才能访问的资源时进行检查，如果检查不通过则被判定非法并抛出异常信号，随后这个例外就会被处理，将会跳转到操作系统约定好的内存位置

一般而言，操作系统运行在S模式，有权限访问所有代码和数据，而一般的程序运行在受限的U mode，只要软件运行在硬件上，它就无法访问那些被禁止访问的资源

> 当然了，详细请见.... riscv的priviledged spec

### 异常响应机制

riscv32提供的自陷指令是`ecall`，并提供一个`mtvec`寄存器来存放异常入口，为了保存程序当前的状态，riscv就需要实现特殊的系统寄存器了，就是所谓的CSR了！

尽管理论上有4096个可分配的地址（12位），但是这里我们仅仅使用3个CSR：

- `mepc`， 也就是SEPC保留抛出异常指令的pc
- `mstatus`，也就是存放处理器当前特权状态的
- `mcause`，存放触发异常的原因

而riscv32触发异常后响应过程如下：（当然了这只是一个简化版）

1. 将当前PC保存到mepc

2. 在mcause设置异常号

3. 从mtvec取出异常入口地址

4. 跳转到异常入口地址

> 为何不让软件来保存... 这很显然啊，用软件保存的话此时pc已经切换到别的地方执行os提供的例程了，怎么可能知道发生异常时的状态？

那么之后就会让OS的例程来接管了。如果不杀死这个程序，那么就通过`mret`指令从异常处理返回，并根据mepc寄存器恢复PC

### 状态机视角下的异常响应机制

显然就像前面说的，程序就是一个状态机`S=<R,M>`。不过考虑到此时的异常响应机制需要更多的信息，那么此时的`R`$\to$`R = {GPR, PC, SR}`，而`M`显然和我们的异常响应机制无关。

而关于状态的转移，我们暂时仅仅考虑用户程序本身，那么实际它的状态转移就可以描述为一条指令的“失败”。而判定它是否失败无论如何也只有两种情况，那么就可以暂时简化为`fex: s->{0,1}`，那么引入异常响应机制并不会增加系统的不确定性

同时另一方面自然要对我们的ISA进行扩展了，riscv引入了`mret` / `csrrw`之类的...


不过既然这样，我们完全可以将上下文的管理抽象为一类NEMU的新的API，也即Context Extension

那么之后的问题就是如何抽象了，显然，无论什么架构，都需要处理这些信息：

- 引发这次执行流切换的原因

- 程序的上下文


> AM提供了多大的栈空间？
> 实际上看一眼链接脚本就知道了：
> ```ld
>   _stack_top = ALIGN(0x1000);
>   . = _stack_top + 0x8000;
>   _stack_pointer = .;
> ```
> 也就是说我们提供了0x8000个字节大小的栈空间！看起来还挺小的...


那么只需要把它们统一表示就可以定义出对应的API了，实现在`am.h`如下：

```c
// An event of type @event, caused by @cause of pointer @ref
typedef struct {
  enum {
    EVENT_NULL = 0,
    EVENT_YIELD, EVENT_SYSCALL, EVENT_PAGEFAULT, EVENT_ERROR,
    EVENT_IRQ_TIMER, EVENT_IRQ_IODEV,
  } event;
  uintptr_t cause, ref;
  const char *msg;
} Event;
```

而显然上下文就没法抽象了，毕竟是具体的pc和寄存器，不同的ISA之间是没法统一的，名称为`Context`统一了一下。

以及两个统一的API：

- `bool cte_init(Context* (*handler)(Event ev, Context *ctx))`用于进行CTE相关的初始化工作，其中它还接收一个来自操作系统的事件处理函数的回调指针，当发生事件时，CTE会将事件和相关的上下文作为参数来调用它


- `yield`，实际上就是触发`EVENT_YIELD`事件，通过一个`ecall`：
    ```c
    void yield() {
    #ifdef __riscv_e
      asm volatile("li a5, -1; ecall");
    #else
      asm volatile("li a7, -1; ecall");
    #endif
    }
    ```

> RISC-V官方的SBI手册有规范过，calling convention规定了ecall调用时用`a7`传递EID，`a6`传递FID，返回值放在`a0`/`a1`，其余为被调用者保存

可以看到，这不过就是一个常见的系统调用罢了。不过这里对RV32E有专门的实现，因为`a6`/`a7`分别对应实际物理寄存器`x16`/`x17`，而RV32E仅16个寄存器不存在，AM就只能使用`a5`对应`x15`了。

> 不过说到这里，实际上官方也说过RV32E是不支持跑一个类Unix的OS的，不过跑一跑RTT还是可以的！

需要注意的是，上文介绍的异常和事件是两个层次的概念，异常是硬件层面的机制，而事件是AM对异常的封装

同时为了简化ISA，处理器往往只会提供一条自陷指令，具体做什么则是软件的事情了

> 不过SBI层面同样还是约定了不同EID的事件



我们首先可以先跑一下`am-tests`的`yield test`，我开了iringbuf，最后显示的是：

```text
[src/cpu/cpu-exec.c:158 cpu_exec] nemu: ABORT at pc = 0x800014dc
[src/cpu/cpu-exec.c:167 cpu_exec]   --> 0x800014dc: csrw        mtvec, a4                        30 57 10 73
[src/cpu/cpu-exec.c:167 cpu_exec]       0x8000116c: ret                                  00 00 80 67
[src/cpu/cpu-exec.c:167 cpu_exec]       0x80001068: jal 0x50                             05 00 00 ef
[src/cpu/cpu-exec.c:167 cpu_exec]       0x800010b8: ret                                  00 00 80 67
[src/cpu/cpu-exec.c:167 cpu_exec]       0x8000106c: jal 0x208                            20 80 00 ef
[src/cpu/cpu-exec.c:167 cpu_exec]       0x80001274: ret                                  00 00 80 67
[src/cpu/cpu-exec.c:167 cpu_exec]       0x80001070: lw  ra, 0xc(sp)                      00 c1 20 83
[src/cpu/cpu-exec.c:167 cpu_exec]       0x80001074: addi        a0, zero, 1                      00 10 05 13
[src/cpu/cpu-exec.c:167 cpu_exec]       0x80001078: addi        sp, sp, 0x10                     01 01 01 13
[src/cpu/cpu-exec.c:167 cpu_exec]       0x8000107c: ret                                  00 00 80 67
[src/cpu/cpu-exec.c:167 cpu_exec]       0x80000114: auipc       a0, 0                            00 00 05 17
[src/cpu/cpu-exec.c:167 cpu_exec]       0x80000118: addi        a0, a0, 0x478                    47 85 05 13
[src/cpu/cpu-exec.c:167 cpu_exec]       0x8000011c: jal 0x13b4                           3b 40 10 ef
[src/cpu/cpu-exec.c:167 cpu_exec]       0x800014d0: mv  a5, a0                           00 05 07 93
[src/cpu/cpu-exec.c:167 cpu_exec]       0x800014d4: auipc       a4, 0                            00 00 07 17
[src/cpu/cpu-exec.c:167 cpu_exec]       0x800014d8: addi        a4, a4, 0x2c                     02 c7 07 13
```

嗯，问题在于我们还没实现这些相关的特权指令！死在了`cte.c`里面最基本的`cte_init`上了

当然了，RISC-V的实现不像X86那么复杂，这里第一件事设置异常入口地址，我们需要做的实际上就是针对这条指令直接把这个地址设置到`mtvec`寄存器即可，而这条指令正是Zicsr扩展里面实现的6条CSR操作指令之一


之后则是进入了测试的`hello_intr()`，它首先调用`iset(1)`（但是它目前是空的），然后就是循环不断调用`yield()`进行自陷，同时里面加了一个超长的循环来防止调用频率过高输出太快

为了支撑自陷操作，同时测试异常入口地址是否已经正确设置，需要在NEMU中实现`isa_raise_intr()`来模拟前面提到的异常响应机制。不过显然我们压根就没有划分特权级别，所以压根就不用管



#### RTFM

然后分别看各个csr的要求

mepc：

最低位保持为0，不过因为不支持16位宽的指令，所以应该是低2位

是一个WARL寄存器，永远不能被赋予无效的地址！

当一个trap要陷入M-mode时，它就会被写入这条指令的虚拟地址

mcause：

同样是M-mode，最高位代表是否是中断，剩下的就是Exception Code了：

![image-20261113211434258](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261113211434258.png)

对应的Exception Code：

![image-20261113210648287](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261113210648287.png)

嗯... 或许应该传入11？因为只有M mode的硬件it

mstatus

结构如下：

![image-20261113211527437](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261113211527437.png)

看着好烦啊，暂时不管它好了。反正我们ecall的时候只需要硬编码11作为cause即可，我们并没有别的mode只有Mmode



mtvec

![image-20261113211744362](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261113211744362.png)

- 必须被实现，但是它可以是一个硬连线的只读的值

- 如果可写，它可以被写的值的范围取决于实现，BASE部分的值必须按照4字节对齐，而Mode则决定了该怎么要求：
  ![image-20261113212213538](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261113212213538.png)
  也就是说如果是1的话我们还需要专门检查mcause的最高位看看是不是中断，不是就还是直接使用PC，否则需要加上4 * cause作为偏置！

那么实现时在读取mtvec的时候，需要配合mcause！

```c
word_t isa_raise_intr(word_t NO, vaddr_t epc) {
  	word_t ret = cpu.mtvec & ~(word_t)0x3u;
    cpu.mcause = NO;
    cpu.mepc = epc;
    return (NO >> 31) ? ret : ret + 4 * (NO << 2);
}


```



然后再看相关的pri

![image-20261113213231158](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261113213231158.png)



`mret`的要求，根据官方手册只需要将PC设定为mepc即可

而需要注意的是，这里`ecall`时我可以直接设定mcause为11，因为nemu并不在乎特权级别，全都跑在M-mode上，而需要返回的应该是需要跳转到的地址，之后就更新pc好了。



同时还需要实现整个zicsr扩展，它的指令如下：

![image-20261114132134689](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261114132134689.png)

> 我一直很奇怪为什么要把zicsr扩展的说明放在unpriv里面...

- `csrrw`：原子地读写CSR

  - 读取CSR的旧值，然后零扩展到XLEN位，再写入`rd`。之后将`rs1`的值写入CSR

  - 如果`rd`为x0，则不读CSR并且也不能产生任何读CSR带来的side effect，仅仅把新值写入

- `csrrs`：Atomic Read and Set Bits in CSR

  - 读取CSR的值，零扩展到XLEN位，然后写入`rd`寄存器，在`rs1`里面的初值会被当作位掩码表明需要被置位的CSR位，前提是这个位是可写的

- `csrrc`：Atomic Read and Clear Bits in CSR

  - 读取CSR零扩展.... 和前面一样只是需要置0罢了
  - 如果`rs1`是x0则不允许写CSR也不能产生任何因此而来的side effect，也不能抛出对只读存储器非法访问的错误。但是读的side effect必然会产生

- `csrrwi` / `csrrsi`/`csrrci`：

  - 功能上和前三者很像，但是它们是通过将`rs1`段直接作为一个立即数零扩展到32位来作为CSR的src1。

  - 对`csrrsi`/`csrrci`，如果这个立即数是0，同样不允许进行写操作和side effect
  - 对`csrrwi`，如果`rd`为x0，那么同样

总结的行为如下：

<table>
  <thead>
    <tr>
      <th colspan="5">Register operand</th>
    </tr>
    <tr>
      <th>Instruction</th>
      <th><i>rd</i> is x0</th>
      <th><i>rs1</i> is x0</th>
      <th>Reads CSR</th>
      <th>Writes CSR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>CSRRW</td>
      <td>Yes</td>
      <td>-</td>
      <td>No</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>CSRRW</td>
      <td>No</td>
      <td>-</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>CSRRS/CSRRC</td>
      <td>-</td>
      <td>Yes</td>
      <td>Yes</td>
      <td>No</td>
    </tr>
    <tr>
      <td>CSRRS/CSRRC</td>
      <td>-</td>
      <td>No</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
  </tbody>
  <thead>
    <tr>
      <th colspan="5">Immediate operand</th>
    </tr>
    <tr>
      <th>Instruction</th>
      <th><i>rd</i> is x0</th>
      <th><i>uimm</i> = 0</th>
      <th>Reads CSR</th>
      <th>Writes CSR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>CSRRWI</td>
      <td>Yes</td>
      <td>-</td>
      <td>No</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>CSRRWI</td>
      <td>No</td>
      <td>-</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>CSRRSI/CSRRCI</td>
      <td>-</td>
      <td>Yes</td>
      <td>Yes</td>
      <td>No</td>
    </tr>
    <tr>
      <td>CSRRSI/CSRRCI</td>
      <td>-</td>
      <td>No</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
  </tbody>
</table>



那么只需要实现对应的指令即可，不过很显然我们这里只有这3个寄存器，没有什么副作用，所以也就先不区分好了，反正此时AM侧还没做：

```bash
AM Panic: Unhandled event @ /mnt/data1/0ysyx/ysyx-workbench/am-kernels/tests/am-tests/src/tests/intr.c:12
[src/cpu/cpu-exec.c:158 cpu_exec] nemu: HIT BAD TRAP at pc = 0x80000f68
```





