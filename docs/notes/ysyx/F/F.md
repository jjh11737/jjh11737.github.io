# F阶段

## f3 数字电路基础

CMOS不必多说，模电学过的

logisim 跑在jvm上面，所以得强制使用英文

```bash
java -Duser.language=en -Duser.country=US -jar logisim.jar
```



### 组合逻辑

与非门是最基础的电路，实现逻辑很简单，首先我们得保证两个都是1时才能为0，所以两个NMOS串联到地面，而有一个是1就必须为VCC，所以另一端的两个PMOS必须并联
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260418150449331.png" alt="image-20260418150449331" style="zoom:50%;" />

**或非门**，同样的道理，只有两个都为0才输出1，它其实就是与非门反一下N和P罢了
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260418152328392.png" alt="image-20260418152328392" style="zoom:50%;" />

**传输门**：n和p管并联而成，它的左右其实就是耦合，相当于一个电平跟随器
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260418152206392.png" alt="image-20260418152206392" style="zoom:50%;" />![image-20260418152224723](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260418152206392.png)
**异或门**：A ^ B = (~A & B) | (A & ~B)（a取0b取1或a取1b取0，抄表即可)

而涉及复杂逻辑电路时

使用最少晶体管搭建一个同或门：一种方法是跟异或门一样，B=1输出A，B=0输出~A，所以我们只需要一个非门来提取，之后两个传输门来控制导通即可，一共6个

**对等设计原则**：`0`和`1`的电气特性必须是一样的，即$I_{Y=1} = - I_{Y=0}$，$V_{CC}-V_{Y=1}=V_{Y=0}-V_{GND}$
这样我们就不用去管那些电气特性，只考虑逻辑了

但是很显然，我们比如与非门它拓扑结构是不对称的，因为电路一遍是通过串联，一边是并联，产生的压降都不一样。。。
那么在这个例子里面，我们就可以调整N管，让每个N管电阻变为原来的一半（比如调整面积，并联2个硅管）

那么因此门电路的实际面积：

```
#T(nand) = #T(P1) + #T(P2) + #T(N1) + #T(N2) = 1 + 1 + 2 + 2 = 6
#T(not) = 2
#T(and) = #T(not)+#T(nand)
```

**三输入与非门**：一个与门级联一个与非门
N输入与非门：(N - 2)个与门级联一个与非门

```
#T(nand3) = #T(and) + #T(nand) = 8 + 6
#T(nandN) = (N-2)#T(and) + #T(nand) = 8N - 10
#T(andN) = 8(N-1)
```

但是从晶体管层面考虑，依旧我们需要考虑对等原则，实际上我们只需增加一个输入即可，此时就得更多晶体管串联来保证电气特性相同了
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260418163353644.png" alt="image-20260418163353644" style="zoom:67%;" /><img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260418163353644.png" alt="image-20260418163413872" style="zoom:50%;" />
原则如下：

- 以晶体管实现，面积和输入数量二次相关（n个nmos，每个nmos偏偏还得是原来n个并联在一起）
- 以二输入门电路为例，则是线性相关的

**进位计数法**

以上我们只考虑了单个bit，但是现在需要考虑的是多bit情况，没啥好说的

**译码器：n选1译码器**（也就是所谓“分线器”）

比如2-4译码器，就是输入10则把第3位置1，其余置0。一般来说实现就是<u>n个非门和2^n个n输入与门</u>（这不是显然的吗，只有每一位都符合我们想要的条件我们才输出这个数字，而我们每一位只可能有它和它非作为状态），那么计算如下：

```
#T(10-1024 dec) = 10#T(not) + 1024#T(and10) = 10 * 2 + 1024 * (10 - 1) * 8 = 73748
```

比如nixie，就是一个译码器

**编码器：**根据独热码输出真值，同样我们每个值需要2^n个非门和2^n个n输入与门以及n个或门
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419073822991.png" alt="image-20260419073822991" style="zoom:50%;" />

剩下的就是**未定义输出**，这些是不符合定义的。而**设计者不需要对这些负责，**换句话说就是使用者必须保证输入是规定好的，而且也不会让后续电路可能处理未定义输出，那电路完全可以化简了，比如2-4译码器:

```
#T(4-2 enc) = 2 #T(or) = 16
```

**优先编码器：**支持独热码之外的输入，**输出最高位1的位置**，但是全0则输出为X未定义

**多路选择器：**根据选择端选择一路作为输入
位宽M，N选1的多路选择器，则这个$log_2N-N$译码器的值可以被M个N选1路多路选择器复用，效果一样（因为位宽M不过就是M个并联罢了）
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419074907590.png" alt="image-20260419074907590" style="zoom:67%;" /><img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419074907590.png" alt="image-20260419074923826" style="zoom:50%;" />
当然用传输门实现更加简单， 比如2选1的多位选择器，完全可以只需要一个非门作为输入，然后每一位都是2个传输门来决定是否导通

**比较器：**检查是不是每一位都一致，显然n个同或门通过一个n输入与门即可
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419080115273.png" alt="image-20260419080115273" style="zoom:67%;" />

**加法器：**

- 半加器HA：无进位的加法，就是异或

- 全加器FA：一样的，就是我们需要再加一个异或，进位时只可能是输入全是1，或者上一位有进位而这一位有一个1

  ```RTL
  S = A ^ B ^ Cin 
  Cout = (A & B) | (Cin & (A ^ B))
  ```

- 多位加法器（RCA，行波进位加法器）：级联罢了

但是让RCA处理原码肯定是不现实的，你会发现总是在处理一正一负时多一个1，那么因此提出补码，也就是取反+1，这样计算的时候无论如何，最后都是2 ^ (n)  - (原码)，这就保证了相加后最后和是一个刚好溢出的值 ，这个目的主要是为了抵消原码那个-0。

换一个方式理解，其实就是我们把二进制数头尾连接好了
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419082847738.png" alt="image-20260419082847738" style="zoom:50%;" />
相比，原码在0那里不连续，而反码则重复了
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419083135871.png" alt="image-20260419083135871" style="zoom:50%;" />

### 时序逻辑：

我们希望电路可以更新电路的状态

**交叉配对反相器：**

Q和~Q经过两个反相器后保持自身的值。如果两个一开始相等，那么电路亚稳态发生震荡，所以不实用
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419085200358.png" alt="image-20260419085200358" style="zoom:67%;" />
**SR锁存器**
两个或非门连着，
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419085909406.png" alt="image-20260419085909406" style="zoom:67%;" />

| S    | R    | Q                    |
| ---- | ---- | -------------------- |
| 0    | 0    | 不变                 |
| 0    | 1    | 写入0                |
| 1    | 0    | 写入1                |
| 1    | 1    | X未定义（此时都是0） |

那么很显然我们得把写入和值进行解耦，由此就得到了：

**D锁存器：**额外加了两个与门，把我们输入限制为了3种合法输入，WE=0时保证两个输入一定是0，WE=1时输入S=D，R = ~D，就直接写入了
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419090925565.png" alt="image-20260419090925565" style="zoom:50%;" />

| WE   | D    | S    | R    | Q     |
| ---- | ---- | ---- | ---- | ----- |
| 0    | 0    | 0    | 0    | 不变  |
| 0    | 1    | 0    | 0    | 不变  |
| 1    | 0    | 0    | 1    | 写入1 |
| 1    | 1    | 1    | 0    | 写入0 |

还可以用与非门来完成这个D锁存器
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419091125114.png" alt="image-20260419091125114" style="zoom:50%;" />

SoP/PoS，即2种真值表化简方法



而为了让复杂系统能够有顺序的执行，达成一种同步，我们就需要时钟信号

**同步电路**就是通过全局的时钟信号实现同步关系的，存储单元只会在时钟边沿到达时写入数据，在后续的稳定电平时才稳定的读出数据

而**异步电路**则是模块之间的局部通信实现同步关系

无论如何，**D锁存器**是不能实现我们想要的功能的，因为输入马上就可以到达输出，D和Q是同步的，它是一种**电平触发元件**，而我们需要的是**边缘触发**的

因此我们就需要所谓的**D触发器（D-Flip-Flop）**：它的原理就是两个锁存器，主锁存器在低电平时先存好值，然后Q通到下一级D，之后下一个高电平时就把主锁存器的值读到从锁存器里面，这就完成了上升沿的读取，而高电平时维持状态
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419092411266.png" alt="image-20260419092411266" style="zoom:50%;" />
**带复位端的D触发器**：resetn就是低电平有效的复位信号，resetn为1时就是D触发器，而为0时则写入0（必须要保持到上升沿到来才能成功完成复位）
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419093129076.png" alt="image-20260419093129076" style="zoom:50%;" />
显然，这不够方便，所以我们希望这个过程是异步的，就是下面这个异步复位的D触发器，它的本质就是把resetn直接引入了输入部分，再原有的D触发器基础上，我们把D输入端和resetn一起，然后resetn又接入了主触发器的D触发器的~Q的输入端保证置零，这样此时主触发器输出的就是0了（因为D触发器是同步的），然后我们再让从触发器的R端输入resetn为0，此时就保证~Q必须为1，而由于上一级主触发器给出的输入端此时为0，那么最终结果就是从触发器置零，完全reset。（而与非门保证输入1对电路不干扰）
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419093419442.png" alt="image-20260419093419442" style="zoom:50%;" />

**带使能端的D触发器**：现在的触发器保证可以在时钟上升沿输入信号，但是不够灵活，所以我们再引入一个`en`保证只有EN置1才允许更新，这就更简单了，只需要EN控制一个2路选择器（两个传输门）即可，这就是最基础的寄存器了
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260419094639550.png" alt="image-20260419094639550" style="zoom:50%;" />

把他们共用一个`EN`，那么就形成了一个基本的寄存器。当然对等原则会要求添加更多反相器





关于二进制转bcd：

double dabble：即把此二进制数字右移4位然后加3，实际含义就是输入1个4位的旧的二进制，然后我们想要对它模10，而进位部分要乘以16，所以实际上就是先把它*2，判断是不是大于9，如果大于9（要进位），那么就把它+6，这就直接进位了。那么反过来，我们可以先给判定是不是大于等于5，如果是那么+3，然后移位（那输入15呢？显然变成18，移位后就是36 = 2 



## f4 状态机模型

基本来说，所谓的状态机定义如下：

- 一个状态计划S
- 激励事件E
- 状态转移规则：S * E -> S
- 初始状态S 

那么数字电路本身就是一个状态机，它的输入就是激励事件

而编译器干的事情就是把C程序翻译成为一个状态机，处理器则是用数字电路实现ISA

|              | ISA      | 数字电路       | C         |
| ------------ | -------- | -------------- | --------- |
| 状态         | {PC,R,M} | 时序逻辑       | {PC, V}   |
| 激励事件     | 执行指令 | 组合逻辑电路   | C语句语义 |
| 状态转移规则 | 指令语义 | 组合电路的逻辑 | C标准手册 |

$S_C = S_{ISA} = S_{CPU}$





## f5 简单处理器的实现

目前只实现最最简单的一个，PC位宽4(addr)

指令周期：

1. 取指(fetch)

   - 一个pc寄存器（简单的就行）

   - 存储器 = 可寻址的存储单元的集合

     - 每行对应一个存储字
       - 地址 = 行编号， 行数 = 存储器深度
     - 一行存储多位数据，也就是位宽

     （我们这里只有取指需要访问存储，用ROM足矣）

   - ROM的结构：
     ![image-20260425112504755](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260425112504755.png)

2. 译码(decode)

   - GPR也是存储器，不过需要作为目的被写入，也就是RAM

     - 读操作：很显然没啥区别，和rom差不多
       ![image-20260425113355008](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260425113355008.png)

     - 写操作：需要写使能和选择的路同时满足才允许写入
       ![image-20260425113441851](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260425113441851.png)
     - 整体结构：
       ![image-20260425113716580](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260425113716580.png)
     - 单端口RAM：同一时刻只允许用一个地址访问一个存储字
     - 多端口RAM：同一时刻可以用多个地址同时访问多个存储字

3. 执行(execute)

4. 更新PC：
   不考虑跳转，那么目前只需要简单的计数器自增就好了

那现在我们除了`li`还需要一个`add`指令
具体执行的时候，首先译码时我们显然需要专门对`opcode`进行译码
其次add需要同时访问两个数值来源，换句话说我们需要2个读端口raddr1 / rdata1

写端口则需要: `waddr` / `wdata` / `wen` / `clk`

而执行的时候很显然，我们要根据指令`opcode`来决定我们写入/读取的源，

然后条件跳转指令`ber0`，显然就是一个比较器，如果相等那么直接PC更新为目标`addr`，否则更新为`PC+1`。

那么审视cpu的设计：

1. 分析指令的预期行为
2. 根据指令的行为，在数据流动的方向上依次添加需要的部件
3. 如果多条指令通路出现冲突。那么就得引入一些额外的电路控制数据流
   - 保证每条指令符合`ISA`的规范
   - 这些额外的电路要符合CPU的控制逻辑
   - 这些被称为`控制信号`

| 指令 | wdata       | wen  | raddr1 | PC   |
| ---- | ----------- | ---- | ------ | ---- |
| add  | adder的输出 | 1    | rs1    | PC++ |
| li   | 立即数      | 1    | X      | PC++ |
| ber0 | X           | 0    | 0      | addr |

## f6 RISC-V 处理器

**RTFW：**

关于RISCV：设计理念就是越简洁/越普适越好，不能因为特定处理器而针对设计

首先作为一个ISA，我们要明确这里只讨论`unpreviledged instructions`即可以用户直接调用而无需kernel监管的CPU指令。



然后就是考虑实现一个基本的处理器`minirv`。我们已经编译层面上把指令压缩成为了8个最基本的指令：

- `add`
- `addi`
- `lui`
- `lw`
- `lbu`
- `sw`
- `sb`
- `jalr`

而剩下的细节则是：

- PC初始值为0
- GPR同rv32E（简化版的32I）， 16个
- 其他isa细节同RV32I

具体来说，RV32I显然是32位的，同时它的`X0`寄存器是0只读的，外来任何改变都不会被接受，32个32位的寄存器，还有一个PC。它没有专门指定栈顶指针/子过程返回地址寄存器。但是标准规范还是规定`X1`作为返回地址的寄存器，`x5` ，`x2`作为栈顶指针的寄存器

![the list of isa](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260502235629987.png)

首先很显然，这个ISA的低7位作为opcode,
而且很独特的一点是几乎每条指令都是由`opcode(操作码)`和`funct(功能码)`决定，前者决定我们操作的大类，后者指定具体操作
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
<    imm                         >  <    rs1    >  < fc3 >  < rd      > <   opcode  > 
< fc 3> refers to: ADDI / SLTI[U] / ANDI / ORI / XORI
那么指令就很清晰了，< fc3 > < fc7 > < opcode > 都是要解码的部分，那么我们考虑做一个多级的解码？



list：

- [x] LUI
- [x] JALR
- [x] LW
- [ ] LBU
- [ ] SB
- [ ] SW
- [x] ADDI
- [ ] ADD

 addi: 0000 0000 0001 0000 1000 0000 1001 001

测试指令：0x108093(rs1 = rd1 = x1, 即x1++)

JALR: (jump and link register):

它的计算和addi很像，先计算出来imm1 + rs1，把它作为跳转值，同时这个值+4存入rd

0x100067(rs1 = rd = x0, imm = 1, 即跳转到0x1指令的位置)

LUI：LOAD UPPER IMMEDIATE
输入一个32位的常数（需要位扩展后移位）到rd

0000 0000 0000 0000 0000000 0000 0000 0000 0001 0001 10110111（rs1 = x3, imm[32:12] = 0x1 << 12）

LW： LOAD WORD
从内存加载一个32位的数到rd，地址是rs1 + imm（需符号扩展）
0000 0000 0000 0000 0010 0001 1000 0011（imm[11:0] = 0, rs1 = x0, rd = x3）

整体来说，除了U形指令我们都是符号扩展的

LBU是U型指令，采用零扩展，输入一个字节扩展为32位
