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

> 这看起来似乎很美好...但是实际上位数越多就需要对应的与运算，因为多位的与运算是级联的，我们发现这好像也没有改变关键路径的长度。。。似乎还是$O(n)$？因此实际上我们实际设计里面不会简单地直接连接...而想要改变这一点，就是所谓道prefix adder了，这种我们为什么不能用树的结构呢？

### 流水线

本质：我们把操作重叠起来
