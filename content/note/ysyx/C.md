---
title: "C阶段"
date: 2026-11-02T16:25:54+08:00
draft: false
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





