# 计算机组成

> 笔记参考**《1》** ，同时也参考了袁春风那一本

很多CSAPP里面有了所以我只看没看的东西（因此我们从第2章开始）：![9](http://five-embeddev.com/riscv-user-isa-manual/Priv-v1.12/instr-table_05.svg)



## 第2章 有关指令

> 这里主要原因是读这本书时我不完全熟悉risc-v的指令，这本书似乎是基于RV64I的？32个寄存器，$2^{61}$个存储字，因此一个字为8字节

这是ISA的比较简单基础的一部分

| Category             | Instruction                          | Example             | Meaning                      | Comments                                                     |
| -------------------- | ------------------------------------ | ------------------- | ---------------------------- | ------------------------------------------------------------ |
| Arithmetic           | Add                                  | `add x5, x6, x7`    | `x5 = x6 + x7`               | Three register operands; add                                 |
| Arithmetic           | Subtract                             | `sub x5, x6, x7`    | `x5 = x6 - x7`               | Three register operands; subtract                            |
| Arithmetic           | Add immediate                        | `addi x5, x6, 20`   | `x5 = x6 + 20`               | Used to add constants                                        |
| Data transfer        | Load doubleword                      | `ld x5, 40(x6)`     | `x5 = Memory[x6 + 40]`       | Doubleword from memory to register                           |
| Data transfer        | Store doubleword                     | `sd x5, 40(x6)`     | `Memory[x6 + 40] = x5`       | Doubleword from register to memory                           |
| Data transfer        | Load word                            | `lw x5, 40(x6)`     | `x5 = Memory[x6 + 40]`       | Word from memory to register                                 |
| Data transfer        | Load word, unsigned                  | `lwu x5, 40(x6)`    | `x5 = Memory[x6 + 40]`       | Unsigned word from memory to register                        |
| Data transfer        | Store word                           | `sw x5, 40(x6)`     | `Memory[x6 + 40] = x5`       | Word from register to memory                                 |
| Data transfer        | Load halfword                        | `lh x5, 40(x6)`     | `x5 = Memory[x6 + 40]`       | Halfword from memory to register                             |
| Data transfer        | Load halfword, unsigned              | `lhu x5, 40(x6)`    | `x5 = Memory[x6 + 40]`       | Unsigned halfword from memory to register                    |
| Data transfer        | Store halfword                       | `sh x5, 40(x6)`     | `Memory[x6 + 40] = x5`       | Halfword from register to memory                             |
| Data transfer        | Load byte                            | `lb x5, 40(x6)`     | `x5 = Memory[x6 + 40]`       | Byte from memory to register                                 |
| Data transfer        | Load byte, unsigned                  | `lbu x5, 40(x6)`    | `x5 = Memory[x6 + 40]`       | Byte unsigned from memory to register                        |
| Data transfer        | Store byte                           | `sb x5, 40(x6)`     | `Memory[x6 + 40] = x5`       | Byte from register to memory                                 |
| Data transfer        | Load reserved                        | `lr.d x5, (x6)`     | `x5 = Memory[x6]`            | Load; 1st half of atomic swap                                |
| Data transfer        | Store conditional                    | `sc.d x7, x5, (x6)` | `Memory[x6] = x5; x7 = 0/1`  | Store; 2nd half of atomic swap                               |
| Data transfer        | Load upper immediate                 | `lui x5, 0x12345`   | `x5 = 0x12345000`            | Loads 20-bit constant shifted left 12 bits                   |
| Logical              | And                                  | `and x5, x6, x7`    | `x5 = x6 & x7`               | Three reg. operands; bit-by-bit AND                          |
| Logical              | Inclusive or                         | `or x5, x6, x8`     | `x5 = x6 \| x8`              | Three reg. operands; bit-by-bit OR                           |
| Logical              | Exclusive or                         | `xor x5, x6, x9`    | `x5 = x6 ^ x9`               | Three reg. operands; bit-by-bit XOR                          |
| Logical              | And immediate                        | `andi x5, x6, 20`   | `x5 = x6 & 20`               | Bit-by-bit AND reg. with constant                            |
| Logical              | Inclusive or immediate               | `ori x5, x6, 20`    | `x5 = x6 \| 20`              | Bit-by-bit OR reg. with constant                             |
| Logical              | Exclusive or immediate               | `xori x5, x6, 20`   | `x5 = x6 ^ 20`               | Bit-by-bit XOR reg. with constant                            |
| Shift                | Shift left logical                   | `sll x5, x6, x7`    | `x5 = x6 << x7`              | Shift left by register                                       |
| Shift                | Shift right logical                  | `srl x5, x6, x7`    | `x5 = x6 >> x7`              | Shift right by register                                      |
| Shift                | Shift right arithmetic               | `sra x5, x6, x7`    | `x5 = x6 >> x7`              | Arithmetic shift right by register                           |
| Shift                | Shift left logical immediate         | `slli x5, x6, 3`    | `x5 = x6 << 3`               | Shift left by immediate                                      |
| Shift                | Shift right logical immediate        | `srli x5, x6, 3`    | `x5 = x6 >> 3`               | Shift right by immediate                                     |
| Shift                | Shift right arithmetic immediate     | `srai x5, x6, 3`    | `x5 = x6 >> 3`               | Arithmetic shift right by immediate                          |
| Conditional branch   | Branch if equal                      | `beq x5, x6, 100`   | `if (x5 == x6) go to PC+100` | PC-relative branch if registers equal                        |
| Conditional branch   | Branch if not equal                  | `bne x5, x6, 100`   | `if (x5 != x6) go to PC+100` | PC-relative branch if registers not equal                    |
| Conditional branch   | Branch if less than                  | `blt x5, x6, 100`   | `if (x5 < x6) go to PC+100`  | PC-relative branch if registers less                         |
| Conditional branch   | Branch if greater or equal           | `bge x5, x6, 100`   | `if (x5 >= x6) go to PC+100` | PC-relative branch if registers greater or equal             |
| Conditional branch   | Branch if less, unsigned             | `bltu x5, x6, 100`  | `if (x5 < x6) go to PC+100`  | PC-relative branch if registers less, unsigned               |
| Conditional branch   | Branch if greater or equal, unsigned | `bgeu x5, x6, 100`  | `if (x5 >= x6) go to PC+100` | PC-relative branch if registers greater or equal, unsigned   |
| Unconditional branch | Jump and link                        | `jal x1, 100`       | `x1 = PC+4; go to PC+100`    | PC-relative procedure call                                   |
| Unconditional branch | Jump and link register               | `jalr x1, 100(x5)`  | `x1 = PC+4; go to x5+100`    | Procedure return; indirect call（call完返回的时候可以直接返回到PC+4也就是下一条指令的位置） |

而riscv的字段实际上是这个结构：

| funct7 | rs2  | rs1  | funct3 | rd   | opcode |
| ------ | ---- | ---- | ------ | ---- | ------ |
| 7      | 5    | 5    | 3      | 5    | 7      |



### 关于过程

我们约定：

- `x10` ~ `x17`：这8个寄存器负责参数传递和返回值
- `x1`：返回地址寄存器
- `x5` ~ `x7`/ `x28` ~ `x31`：临时寄存器，调用者保存
- `x8` ~ `x9` / `x18` ~ `x27`：被调用者保存寄存器



比如如果我们想实现一个递归嵌套过程：
```c
long long int fact (long long int n){
    if (n < 1) return 1;
    else return (n * fact(n-1));
}
```

那么它的汇编：
```assembly
fact:
	addi sp, sp, -16		// stack for return addr and argument n, these are all needed when returned
	sd	x1, 8(sp)			// return addr
	sd	x10, 0(sp)			// n
	addi x5, x10, -1
	bge x5, x0, L1			// n-1 >= 0, jmp2L1, prepare to call the target function
	
	addi x6, x10, 0			// mov the returned val to x6
    ld x10, 0(sp)			// restore n
    ld x1, 8(sp)			// restore return addr
    addi sp, sp, 16			// restore the stack pointer
    mul x10, x10, x6		// return n * fact(n-1)
    jalr x0, 0(x1)
L1:
	addi x10, x10, -1		// set n-1 as the argument to be passed
	jal x1, fact			// call fact
```



算了这好像没啥好说的



### 2.10 并行性与指令：同步

我们需要同步来防止data race，我们会使用**加锁(lock)**和**解锁(unlock)**来实现同步操作，而这可以用于创建一个同一时刻只允许一个处理器的一个执行流进入的区域（这实际上还是通过atomic来实现的，当然atomic真正保证了相关操作不会被并发执行流观察为拆开的，而实际上决定多核之间不出现冲突的还是缓存一致性协议，因为每个都有一套cache，需要保证它们对同一个内存位置的状态保持一致），也就是**互斥区(mutual exclusion)**

而在多处理器实现同步的关键是一组能够提供原子方式读取和修改内存单元的能力的硬件原语（ISA提供的），这样我们就能**保证在内存单元的读取和写入不会被插入任何其他的操作而打断。**

我们从**原子交换(atomic exchange / swap)**说起，它是构建同步机制的一种典型操作，用于将寄存器的值和存储器中的值交换

而具体来说，比如我们想构建一个锁变量，那么处理器就会尝试把寄存器里面的1和内存地址的值交换：

- 寄存器获取到0 那就是没加锁！那么很好，我们就获得锁了，而此时内存里面对应1代表占用
- 寄存器获取到1,那就说明被占用

关键在于交换是不可分割的，硬件会对两个同时发生的交换进行排序

> 但是我们还是要说，多处理器的关键在于cache coherence，也就是说当一个处理器想要执行exchange的时候，它必须先获得这个cache line的独占权限，如果获取到了，那么别的同样缓存了这个内存地址的数据的处理器对应的cache line就会被标记无效，它就必须要再次获取，此时才能去进行相应的操作

另一种方法是使用**指令对**（这还是ISA层面规定的），其中第二条指令返回一个值，然后通过分支跳转的指令来决定要不要重试（当然了处理器本身才不在乎呢）。只要任何处理器执行的所有其他操作都发生在该对指令外面，那么这就是原子的

而在RISC-V中，对应的就是**`lr.w`(保留加载-load reserved)** / **`sc.w`（条件存储-store conditional)**，它干的事情是：如果保存加载指令指定的内存位置的内容和条件存储指令看到的值不一样，那么指令就会失败不会写入内存

> 而关键在于lr.w之所以叫reservation，就说明这个hart会监视这块缓存，如果别的核也写入了同样的内存位置，那么缓存一致性协议就会让这个reservation失效，而如果是自己写那么写的时候就会失效了

一般汇编如下：

```assembly
again: 	lr.w x10, (x20)
		sc.w x11, x23, (x20)
        bne x11, x0, again
```

指令对的优点就在于我们可以更方便地构建原语，这是它的灵活性带来的好处

比如我们想要实现一个自旋锁：

```rust
		addi x12, x0, 1
again: 	lr.w x10, (x20)
		bne x10, x0, again		// 读不到0我就再读一遍
		sc.w x11, x12, (x20)
		bne x11, x0, again
```













## 第3章 算术运算

基础的加法器自然不必多说，不过实际上我们可以考虑并行地完成加法的计算？而不是一定要按顺序地等待也就是纹波加法器那种。

### 加减法

#### CLA

我们仔细想一下，不能并行本质原因在于我们需要进位，而一般的加法器我们必须知道上一位的结果才能知道这一位要不要加上进位，这极其低效，因而我们分析一下进位本身：
$C_1 = X_1 Y_1 + (X_1 + Y_1) C_0$ ，满足这样的递推关系，而我们可以进一步代入展开：
$C_2=X_2Y_2+(X_2+Y_2)C_1=X_2Y_2+(X_2+Y_2)X_1Y_1+(X_2+Y_2)(X_1+Y_1)C_0$，,以此类推，显然我们发现实际上我们需要的只有$P_i=X_i+Y_i$，$G_i=X_iY_i$这两个是我们需要的数据，而进位本身是可以满足递推关系的，化简后是：
$$
C_1=G_1+P_1C_0 \\
C_2=G_2+P_2G_2+P_2P_1C_0 \\
C_3=G_3+P_3G_3+P_3P_2G_1+P_3P_2P_1C_0 \\
...
$$
只要$C_0$和$X_iY_i$同时到达，我们几乎就可以同时算出所有的进位！那么各位的计算就是并行的了，实现这种功能的电路称为先行进位器(Carry Lookahead Unit，CLU)，而这样实现的就是全先行进位加法器(Carry Lookahead Adder，CLA)

> 这看起来似乎很美好...但是实际上位数越多就需要对应的与运算，因为多位的与运算是级联的，我们发现这好像也没有改变关键路径的长度。。。似乎还是$O(n)$？而且更糟糕的是，这太浪费硬件了... 因此实际上我们实际设计里面不会简单地直接连接...而想要改变这一点，就是所谓prefix adder了，这种我们为什么不能用树的结构呢？

### 乘法

对于有符号的乘法，我们只需要先记录符号确定最终的符号，然后先全部转换为正数执行乘法后再转换即可

#### 快速乘法

虽然你也可以结合移位和加法器来快速实现，但是似乎没有必要？更好的方法是我们直接分治，把这个循环展开：
![image-20261003180944357](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261003180944357.png)

这需要5层，虽然看起来不太好，但是我们很容易发现这种结构天然适合流水线化！

##### csa

而且实际上这甚至可以比单纯的五次加法叠加还快，因为我们可以引入**CSA(carry Save Adder)**，把次数再压缩一下

> CSA的思路：
>
> 比如我们要做3个数的乘法，那么一般会需要：
>
> 1. a+b = x
> 2. x+c = s
>
> 而我们认为第一步的carry propagation是不必要的，因为我们明明可以三个数一起看：
> ![csa](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/v2-fbb759fe5e9551256d1618a78d5d743b_1440w.jpg)
>
> 那么原本3个数的相加就变成两个数相加了，也就是说它可以压缩加法树

但是仔细一想，这肯定还是不够好的... 因为我们不是单独做好几个不同数的加法，我们是计算同一个数的移位的加法啊...

##### booth

这就要引入我们的booth算法了！我们为什么一定要做这么多次移位的产物？有没有什么方法我们保证能确定用更少的？因为我们可以发现似乎这总是有一个上限的，一旦位数过多，我们总是可以用更好的方法取代它，就像：0111 不就是1000 - 0001吗？

一种很朴素的想法是：我们可以找连续的1 ，然后把它转化为一个单独的1和一个减法，这很蠢，因为没法有对应的硬件实现。那么换一个思路，我们可以在一个局部的空间里面确定吗？

我们首先可以想到，对于一串连续的1 ，我们压根就不需要关注那些中间的1... 因为只有1到0的转换我们才关心，不是吗？那么我们可以这样想：

- 找到01代表这个位置有一个+A
- 找到10代表这个位置有一个-A

那么这就是所谓`radix-2`了，但是既然可以这样，那为什么不我们一次多看几位？也就是说我们把相邻的两个booth bit合并，那么我们可以想到radix4是什么样的：

公式是：$d_i = b_{2i} + b_{2i-1} - 2b_{2i+1}$

这实际上很好推导，我们从radix-2出发，我们已经知道一个booth bit的计算实际上就是：
$$
c_i = b_{i-1} - b_i
$$
那么我们想要两个一起看，就是
$$
d_i = 2c_{2i+1} + c_{2i} \\
d_i = 2(b_{2i} - b_{2i-1}) + (b_{2i-1} - b_{2i})
$$
那么写成表就是：

| 数字 | 产生结果 |
| ---- | -------- |
| 000  | 0        |
| 001  | +A       |
| 010  | +A       |
| 011  | +2A      |
| 100  | -2A      |
| 101  | -A       |
| 110  | -A       |
| 111  | 0        |

先对数字右侧补零，然后每次这个窗口左移2位，这样我们就可以直接确定移位

既然如此，那么我们其实只需要一般的partial product就能完成任务，这个树因此可以进一步压缩



### 除法

这就更麻烦了，一般比较笨的方法是我们把除数最低位和被除数高位对齐，每次比大小，如果除数更小那就减去的同时给商写1 ，写回再右移，否则写零直接右移，最后就能得到余数和商了

而有符号的除法就麻烦了，因为商的值会取决于我们被除数和除数的符号！因为
$$
-(x / y) \neq (-x) / y
$$

#### 快速除法

这个，大概就是SRT之类的？我懒得了解了，反正明白除法这件事很麻烦就是了





### 浮点数

关于浮点数的定义就不必赘述了，ieee 754

#### 浮点加法

1. 将指数较小的数移动使它和较大指数的数指数相同
2. 将两个数的有效位数相加
3. 加法后要对和移位调整指数，因为此时我们得到的往往是非规格化的，让它变成规格化的形式
4. 对结果进行舍入

![image-20261003200719033](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261003200719033.png)



#### 浮点乘法

1. 指数相加（不过别忘了！我们的指数是带偏移量的！所以相加后记得减去偏移量）
2. 逐位相乘，和整数乘法差不多
3. 规格化、
4. 舍入
5. 别忘了符号



#### 精确算术

我们很清楚，浮点数是不可能精确表示的（我想你在程序设计里面已经碰到过了），有无穷个数字，而我们的双精度浮点数却只能精确表示$2^{53}$个数

因此IEEE 754还提供了专门的舍入方法，在中间计算时总是会在右边保留两个额外的位：**保护位(Guard)**和**舍入位(Round)**（还会有个Sticky bit，是后面所有位取或），目的主要是告诉我们剩下被丢弃的是多大

而ulp(unit in the last place)就是我们最后的那位的精度，我们会保证误差在半个ulp内









### 谬误与陷阱

- 右移不等价于除一个2的幂次（很显然，问题在于有符号数，我们之前说过了）
- 浮点加法不满足结合率（因为精度有限）
- 













## 处理器



### 流水线

本质：通过各级之间加上一层寄存器（往往会加上有效位），我们得以让每个阶段的单元只需要关注自己下一步要做什么，这好处最大就体现在我们的关键路径变短了，因为两个时钟周期之间我们只需要跑完一级流水线的内容就可以了
