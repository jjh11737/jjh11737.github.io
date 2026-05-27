### 一、计算机系统漫游

```shell
sudo apt update
sudo apt install wireshark
```

#### 1-1程序的生命周期

一个程序生命周期为创建、编译、运行、退出

我们以经典的GNU为例

而编译包含**预处理**（Pre-Processor即**cpp**，看预处理指令，读取头文件的内容并直接插入源程序，得到另外一个c程序，再处理得到**.i**文本文件）、**编译**（Compiler即**cc1**，把C的语言翻译为汇编语言**.s**文件）、**汇编**（Assembler即**as**把.s翻译为机器码变成可重定位的**.o**文件）、**链接**（Linker用**ld**，把其他相关的.o比如我们调用了printf函数，那么printf.o[一个提前编译好的目标文件，来自标准库比如libc]连接到我们输出的.o文件，正是因为要对输出的.o文件进行调整，所以才叫可重定位文件）

![image-20260120235710612](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260120235710612.png)

#### 1-2操作系统的硬件结构

讲一下操作系统，那就绕不开CPU，CPU里面最重要的就是**PC**，它存储下一条指令的地址，长度等于CPU的字长，比如64位那他就是8字节，其实就是寻址空间；其次是**寄存器**，高速读取的临时变量存储器；**ALU**用于与寄存器配合进行逻辑、算数运算；内存则是DRAM，你认为是一个大数组就行了，中间通过总线连接，那么为了处理IO我们就要有一个IO bridge

![image-20260121010550452](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121010550452.png)

比如以我们运行./hello这个可执行文件为例，键盘输入直接可以通过外部中断进入，通过总线进入寄存器，再搬运到我们的内存当中（因为数据量很小不用DMA），然后PC从内存当中加载指令，之后就是从硬盘之中加载hello这个可执行文件到内存当中，可以用DMA来传输，之后再加载到寄存器不断执行，最后输出到图形适配器上

#### 1-3 存储结构层次、虚拟地址空间

然后是存储结构，这就不用讲了吧，越靠上寻址速度越快但是自然寻址内容就会越小

![image-20260121012020788](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121012020788.png)

操作系统本质就是应用与硬件之间的中间层，对底层进行抽象，具体来说，**文件是对一切IO外设的抽象，虚拟内存是对内存+IO设备的抽象，进程则是对包含处理器在内的一切资源的抽象**

![image-20260121012637542](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121012637542.png)

而具体来说我们以一个简单的**进程调用**为例，我们有一个shell的进程和一个hello的进程在并发，shell收到指令之后会通过system call调用把控制权移交给hello，此时就需要一次上下文切换（保存shell的上下文同时创建一个新的hello进程及其上下文），之后hello执行完毕又会恢复shell进程的上下文。而实际来说，一个进程往往需要由多个线程构成

----------------------------------------------------------------------------------------------------------------------

** 上下文 **本身就是记录进程的状态信息（快照），主要包含这个进程接下来执行所必须的信息：

- A 寄存器状态 ：保存PC、栈指针、寄存器
- B用户级状态  ：虚拟地址空间（代码段、数据段、堆、指针）、页表（虚拟地址到物理地址的映射关系）
- C 内核级状态 ：进程控制块（PCB）、文件描述符表

它最终会被临时存储在内存里面，进程虚拟地址空间的顶部

-----------------------------------------------------------------------------------------------------------------------------

然后讲一下**虚拟地址空间**，他其实是由多级存储一起构成的，不仅仅是DRAM主存，而它通过页表把虚拟的地址映射到实际的地址当中，而且往往我们可以通过复用用更少的物理内存（RSS---Real Set Size）来让进程获得更大的（VSS--Virtual Set Size），对于不同的进程之间往往逻辑上这些虚拟内存本身是隔离的。

以一个64位的CPU为例，实际上往往只会使用48位来寻址，而 对每一个进程，它的虚拟内存都是2^48-1也就是128Tb的大小 ！即使我们实际上可能加起来也就8GB，如果不够，一般主要就是复用或者用磁盘临时代替

![image-20260121024850465](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121024850465.png)

一个**经典的虚拟地址空间**，以64位为例是2^48个bit，我们从底向上介绍：

- 程序开始的地址，从0到这里我们必须要预留一个Zero Page（零页），我们目的是防止指针为Null时直接就访问我们的0地址，而是以此触发空页异常来捕捉空指针，同时有时候如果指针被作为一个结构体地址

  ```c
  struct User {
      int id;      // 偏移 0
      int age;     // 偏移 4
  };
  struct User *u = NULL;
  printf("%d", u->age); // 访问的是地址 4
  ```

  此时我们就得考虑这个偏移量来保证触发段错误从而捕捉空指针

- Read-only code and data，存储只读的代码和常量，

- Read/Write data，这里存储的是全局变量
- Mem Allocate也就是堆，这里就是程序通过malloc分配的内存，他是向上增长的
- Memory-mapped region for shared libraries，存放的是共享库（标准库、数学库之类的），他也是向上增长的，位于堆与栈之间
- User Stack用户栈，进程可访问的最顶端，这就是我们调用函数时产生的，因为函数调用本质就是在压栈
- 最顶部是给内核用的，他就包含我们前面说的上下文等一系列内核需要的内容，不允许进程本身去访问它



**文件**就是字节序列，任何IO设备包括网络都可以视为文件，系统中的所有输入输出都是通过使用一小组称为 Unix I/O 的系统函数调用读写文件来实现的。它的作用就是让我们可以

#### 1-4 重要主题（并发并行）

先介绍一下**Amdahl's Law**，他讲的就是我们对系统的某一部分进行加速时加速效果主要取决于我们**被加速部分的重要性**和**加速程度**。这个公式是显然的，a是加速重要度占比，k是加速的倍数，显然当k->无穷时，S=1/(1-a)，所以如果我们想把一个系统加速到一个较高的倍数，就必须要优化大部分的组件

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121030943466.png" alt="image-20260121030943466" style="zoom:33%;" align = left />

那么如果我们想要提高效率，主要有三种途径

- 线程级并发  Thread-Level Concurrency
- 指令级并行  Instruction-Level Parallelism
- 单指令多数据并行  Single-Instruction Multiple-Data Parallelism

并发自然不用说，就是单处理器来回切换。

指令级并行则代表需要多个处理器并行同步处理，就像下面这个融合了哈弗架构与冯诺依曼架构的结构一样，L1分为数据和指令是为了让CPU处理起来不会出现结构冲突，而L2、L3因为原理处理器可以同时存储二者以提高泛化能力。

![image-20260121033421781](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121033421781.png)

而这就引入了另一个概念，也就是所谓的**超线程**，具体来说就是在单处理器内部的线程级别我们也引入一个并行的概念，因为时常会有一些资源是需要公用的（FPU之类的），往往就会配备多个PC、寄存器组之类的来同时为多个线程配置工作，就可以并发执行多个线程

![image-20260121035103471](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121035103471.png)

单指令多数据（SIMD Single Instruction Multiple Data）：一条指令产生多个数据操作，主要是为了提高视频、声音这类信号的处理速度



由此我们可以进一步抽象也就是所谓的**虚拟机是对整个计算机系统的抽象**

**![image-20260121035348088](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121035348088.png)**

我们总结一下** 抽象 **的要素，就是：

- **隔离 (Isolation)：** 让你觉得你独占了资源，不用担心被别人干扰。

- **映射 (Mapping)：** 你在“幻觉”里操作的资源，被一个透明的层转换成“现实”中的物理资源。

- **虚拟化 (Virtualization)：** 提供的资源可以超过物理上限（比如利用磁盘扩展内存，或者在 8 核 CPU 上跑 16 个虚拟机）。

### 二、信息的表示和处理

二进制的存储方法：大端法就是一个数字的高位字节放在存储地址的低位上，小端法反过来把低位字节放在低位上（也就是端是大的还是小的）

位移有两种，**逻辑位移**右移直接高位补0就行了，低位舍弃；而**算数位移**大体一样，但是 **右移时如果原本最高位为1，则最高位补1，如果原本最高位是0，右移最高位补0。（目的是保证符号性与数值不变）** 

需要注意的是，**一般编译器对有符号数在右移时使用算数右移，对无符号数采用逻辑右移**

![image-20260121074634431](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121074634431.png)

负数的表示：
![image-20260121075703213](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121075703213.png)

关系如下，实际上就是看正负，负数需要加上2^（位数）

![image-20260121085104340](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121085104340.png)

而在**比较**的时候，**如果一个是有符号数，一个是无符号数，此时会把有符号数当作无符号数处理**：

```c
int a = -1; unsigned int b = 0;
return a < b;
```

原因很显然， 想要把一个大数据类型的数字转换为小数据类型的数字是不可能不改变值的(unsigned int -> int) ，但是反过来却是很轻松的

具体来说，如果一个unsigned char -> unsigned short，显然我们只要补0就行了，而对于有符号的char -> short，**如果最高位为1即负的则在前面补1，**因为这是很显然的，我们**只关注这个数字与1111 1111（-1）或 1111的差值**！！（当然实际上是要+1才能得到绝对值的，但是逻辑上没区别），当然用数学归纳法可以很轻松的证明（因为加一位是等价的）

#### 加减法

而计算的时候也可能发生**溢出**，正溢出或者无符号直接减去2^w即可，负溢出加回去
对于无符号数，逆元与它的和就是2^w
对有符号数，一般不等于Tmin最小值就只要取相反数，但是Tmin也就是1000 0000是与其他不对称的(最大值的绝对值比最小值的绝对值差了1,一个是127,一个是-128)，这个就不能单纯取反，我们只能定义它等于它自身（-2^w + -2^w = -2(w+1) = 0）

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260123083817861.png" alt="image-20260123083817861" style="zoom:50%;" align = left /><img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs//image-20260123092531787.png" alt="image-20260123092531787" style="zoom:50%;"  align = left/>

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260123093624775.png" alt="image-20260123093624775" style="zoom:50%;" align= left/><img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs//image-20260123093541641.png" alt="image-20260123093541641" style="zoom:45%;" align=left/>

#### 乘除

无符号的我们没啥好说的，主要是有符号的补码
**乘法本质就是卷积**，然后截断到我们想要的位数，而特别地** 有符号和无符号最后截断得到的结果向量是一致的 **
（原因很显然，因为正的有符号数自然和无符号是一样的，而负的有符号我们就是减去2^w，结果显然是(a - 2^w) * b = a * b - b * 2^w，显然b是整数，那么与a * b是一样的，因为我们只不过要取模罢了）
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260123095157797.png" alt="image-20260123095157797" style="zoom:50%;" />

那么很自然，对于除法本质也就是一个移位卷积罢了，对无符号 / 有符号正就是右移补0，对补码就是右移补1（等价于先+2^k-1再右移）

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125155701246.png" alt="补码的除法" style="zoom:50%;" align = left />

#### 浮点数

定点数很简单，就是2的各次幂之和来表示，但是显然精度是固定的

因此我们考虑引入浮点数，IEEE 754的标准如下
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125161955650.png" alt="image-20260125161955650" style="zoom:50%;" align = left /> 显然，我们只需要一个符号位`s`，阶数`exp`，以及剩下的小数字段`frac`即可表示，精度低就用float 32位（1符号8阶码23小数），精度高就用double（1符号11阶码52小数）
那么我们就可以知道显然这个**frac小数必须是在1～2之间**（阶数不能为0，但是要小于2否则就不是小数了），而且这是动态调整的，那么很显然**最高位一定是1，那就不用显式的表示**了
	基本来说，f从高位到低位是2^-1, 2^-2....
而实际上浮点数分为3类：

- ** 规格化(Normalized) **：阶码不全为0或1
  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125164614541.png" alt="image-20260125164614541" style="zoom:67%;" />
  阶码e：1～255表示的不是真的阶数，真正阶数** E = e - Bias ** 需要减去一个偏置量（取决于阶码位数[2^(el-1)]，float为[2^(8-1)-1]=127，double为[2^(11-1)-1]=1023），因此我们可知float范围就是[-126,127]
  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125172834651.png" alt="image-20260125172834651" style="zoom:45%;" align = middle />
  小数frac：就像前面说的，最高位永远是1,所以我们就省略这一位，** M = f + 1 **
- ** 非规格化(De-normalized) **：阶码全为0
  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125164829781.png" alt="image-20260125164829781" style="zoom:67%;" />
  - 表示了0，e与f全为0。** s=1为+0正零，s=1为-0负零 **
  - 表示非常接近0的数，注意** 这里并没有一个被省略的1 **(显然)，以及** E = 1-Bias **，
  - 非常巧的是，这里非规格化的f如果向上溢出刚好就直接到e，刚好就是正常溢出的值
- ** 特殊值(Special) **：阶码全为1，分为2类，一种表示无穷大/无穷小，另一种表示不是一个数NaN
  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125164941328.png" alt="image-20260125164941328" style="zoom:67%;" />
  - Infinity：阶码全1，小数字段全为0，无穷大，**s=0为正无穷大，s=1为负无穷大**
    ![image-20260125174847806](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125174847806.png)
  - NaN：阶码全1，但小数字段非0，Not a Number
- 舍入：四舍六入五成双

举例环节：

为了方便我们用8位来代替之

- 首先是非规格化，那么E = 1 - bias，bias = 2^(4-1) - 1，因此E = -6，而小数就是直接的Frac = f * 2^(fl)
  fl代表f阶数

  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125175824320.png" alt="image-20260125175824320" style="zoom:50%;" /> 

- 然后是规格化：此时E = e - bias，bias = 7，frac = 1 + f * 2 ^ (-fl)。

  注意最大时我们只能去e = 1110,因为不能全1（特殊值）
  ![image-20260125180449344](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125180449344.png)

#### Data Lab

易错点：

- isLessOrEqual：
  注意！！** 如果异号时相减会发生溢出 **！！此时不能用符号位

- 关于浮点数：
  - ** 浮点数的frac部分溢出进位刚好就是到e，无缝衔接 **
  - ** 比较正浮点数时可以直接用整数比较器， **
    （这是因为指数在前，而且采用偏移量所以哪怕是负指数也还是满足这个排序！！）
  - 快速平方根倒数，伟大无需多言



### 三 汇编和机器

#### 3.2 程序编码

1 机器级别编程采用了2个抽象：

- ISA（Instruction Set Architecture），指令集架构，多数ISA包括X86-64都是好像描述成指令是顺序执行的，但是处理器硬件更多是并发地执行指令，但是可以保证整体行为和ISA指定的顺序是一致的
- 虚拟地址空间，内存模型看起来就像一个巨大的数组

2 基本寄存器：

- 程序计数器PC，在X86-64里面为%rip，给出下一条指令在内存的地址
- 整数（tong寄存器，包含16个命名的位置，存储地址和整数数据
- 条件码寄存器，保存最近执行过的算术或逻辑指令的状态信息，用来实现控制/数据流的条件变化，比如if/while这些语句
- 一组向量寄存器，存放一个或多个整数/浮点数值

```bash
gcc -Og -o <prog_name> a.c b.c
#	优化等级g			所有文件
```

-Og是告诉编译器生成符合原始C代码整体结构的机器码的优化等级，一般我们用-O1就行了，太高的优化等级会导致代码变形

##### 3.2.2 代码实例

假设我们写了一个 C 语言代码文件 **mstore.c**，包含如下的函数定义：

```c
long mult2(long, long);
void multstore(long x, long y, long *dest) {
    long t = mult2(x, y);
    *dest = t;
}
```

在命令行上使用 “-S” 选项，就能看到 C 语言编译器产生的汇编代码：

```bash
linux> gcc -Og -S mstore.c
#生成汇编文件p.s
```

这会使 GCC 运行编译器，产生一个汇编文件 mstore.s，但是不做其他进一步的工作。（通常情况下，它还会继续调用汇编器产生目标代码文件）。

汇编代码文件包含各种声明，包括下面几行：
（** 所有以.开头的指令都是指导计算机的，我们可以直接忽略 **）

```assembly
.file "010-mstore.c"
.text 
.globl multstore
.type multstore, @function
multstore:
  pushq   %rbx			#把rbx寄存器压入程序栈，q代表四字
  movq    %rdx, %rbx	#把rdx的值放到rbx里面
  call    mult2			#调用mult2
  movq    %rax, (%rbx)	#把rax放到内存，地址是rbx里面存的那个地址
  popq    %rbx			#pop出栈到rbx寄存器，q四字
  ret     				#函数返回
```

上面代码中每个缩进去的行都对应于一条机器指令。
比如，pushq 指令表示应该将寄存器％rbx 的内容压入程序栈中。这段代码中已经除去了所有关于局部变量名或数据类型的信息。

那为什么一开始要把rbx压栈呢？

首先X86-64会有16个通用目的寄存器，用来存放整数和指针

![image-20260127170958252](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127170958252.png)

我们先介绍两个概念：

###### **调用者保存寄存器 / 被调用者保存寄存器**

![image-20260127172049768](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127172049768.png)

A在运行的时候call也就是调用了B，A前后都操作%rbx寄存器，而B也会操作，那么逻辑上我们应该保证调用B之后这个寄存器内容不变。而想要实现就有两种方法

1. Caller-saved：我们在A也就是调用者里面先保存一次%rbx等调用B完之后恢复
2. Callee-saved：我们在B里面操作%rbx语句前后保存和恢复

而具体是Caller-saved还是Callee-saved，不同寄存器有不同的策略：

![image-20260127173156716](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127173156716.png)

因此我们就知道了，push就是在保存寄存器%rbx的内容，等mult2调用完毕，再用pop从栈里面弹出恢复%rbx
![image-20260127173416056](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127173416056.png)
注意，这里的q指的是long或char *，Intel用b/w/l/q/s表示类型那么现在我们应该就能搞懂这个程序在干啥了，当然我们也可以对生成的目标文件进行反汇编：

```bash
objdump -d a.out
```

![image-20260127180705618](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127180705618.png)
显然我们可以发现，反汇编和原本的汇编文件逻辑一样，但是在push/pop里面省略了q这些数据类型，而call和ret里面却又加上了q。一般来说q只是表示数据大小，多数时候是可以省略的

----

##### 3.2.3 数据格式

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127173646496.png" alt="image-20260127173646496" style="zoom:50%;" />

word表示的就是32位（对32位寄存器)，那么64为就是双字

比如**数据移动（Data Movement Instructions）**：
moveb -> Move byte(1)；
movew-> Move word(2)；
movel -> Move double word(4)；
moveq -> Move quad word(8)；

-----





#### 3.3 寄存器

##### 3.3.1 基本寄存器

16个整数寄存器，他们本身是规定好具体的功能的
注意这里关于参数只有6个寄存器，如果传递参数>6则需要压栈而会严重拖慢速度，所以一般限制在6个参数以内

![image-20260127181423992](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127181423992.png)

##### 3.3.2 Instruction指令

而实际上** 指令 **一般都是由**操作码（operation code）**和**操作数（operation num）**组成的。操作数有3种：** 立即数/寄存器/内存引用 **

```assembly
Opration code 				Operands
movq						(%rdi), %rax
addq						$8, %rsx
subq						%rdi, %rax
xorq
```

![image-20260127214912909](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127214912909.png)

###### Memory Reference

一个内存引用由 ` Imm(立即数)`，`rb(基址寄存器)`，` ri(Index Register)`，`s(scale)`，地址：
$$
Imm(rb, ri, s) = Imm + rb + ri *s.
$$
其中s = 1, 2, 4, 8，s实际就是所谓的步长（数据长度）

###### `MOV`指令：

他有两个操作数，`Source`和`Dest`，其中

- `Source`可以为立即数/内存引用/寄存器	（一个值，待移动）
- `Dest`可以为内存引用/寄存器          （因为它就是我们`Source`要移动到的地方）
- `Source`和`Dest`** 不可同时为内存引用 **（防止太慢）
  此时我们只能先搬到寄存器再搬到另一个内存地址
- 注意mov指令数据长度要与寄存器匹配

e.g. 

```assembly
movl	$0x4050,		%eax		#immediate -> register
movw	%bp,			%sp			#reg -> reg
movb	(%rdi, %rcx),	%al			#mem -> reg
movb	$-17,			(%rsp)		#imm -> mem
movq	%rax			-12(%rbp)	#reg -> mem
```

 特殊情况：

- **movq操作数为立即数时，它一定是32位2的补码形式，之后再进行符号扩展到64位**
  而如果立即数是一个64位的，我们就需要用另一条指令movabsq（** 它针对源是一个64位立即数时 **）

  ```assembly
  movabsq		$0x7f000000			#move absolute quad word
  ```

  ---

  举个例子：已知64位寄存器%rax，%al为其低8位(byte)，%ax为其低16位(word)，%eax为其低32位(double word)

  ```assembly
  movabsq		$0x0011223344556677,	%rax #rax=0x0011223344556677
  movb		$-1,					%al	 #rax=0x00112233445566ff
  movw		$-1,					%ax  #rax=0x001122334455ffff
  movl		$-1,					$eax #rax=0x00000000ffffffff ！
  ```

  注意，只有** movl会把目标寄存器的高32位清空 **（x86-64规定，为了兼容32位操作）

  ------

- 源操作数位数 < 目标操作数位数，需要用** 零扩展 **或** 符号扩展 **

  - **零扩展**：这里z后第一个是源操作数，第二个是目标操作数

    | 指令            | 效果            | 描述                         |
    | :-------------- | :-------------- | :--------------------------- |
    | MOVZ       S, R | R ← 零扩展（S） | 以零扩展进行传送             |
    | movzbw          |                 | 将做了零扩展的字节传送到字   |
    | movzbl          |                 | 将做了零扩展的字节传送到双字 |
    | movzwl          |                 | 将做了零扩展的字传送到双字   |
    | movzbq          |                 | 将做了零扩展的字节传送到四字 |
    | movzwq          |                 | 将做了零扩展的字传送到四字   |

    这里不需要MOVZLQ，因为MOVL前面说过就可以做到了

  - **符号扩展**（补0/1）：
    这里就会多一条MOVSLQ，以及还有一条`cltq`指定eax -> rax（eax是rax低32位，这条指令衔接MOVL %eax %rax即可完成正常的64位操作（符号扩展）

    | 指令             | 效果                    | 描述                              |
    | :--------------- | :---------------------- | :-------------------------------- |
    | MOVS        S, R | R ← 符号扩展（S）       | 传送符号扩展的字节  8             |
    | movsbw           |                         | 将做了符号扩展的字节传送到字 16   |
    | movsbl           |                         | 将做了符号扩展的字节传送到双字 32 |
    | movswl           |                         | 将做了符号扩展的字传送到双字      |
    | movsbq           |                         | 将做了符号扩展的字节传送到四字 64 |
    | movswq           |                         | 将做了符号扩展的字传送到四字      |
    | movslq           |                         | 将做了符号扩展的双字传送到四字    |
    | cltq             | %rax ← 符号扩展（%eax） | 把 %eax 符号扩展到 %rax           |

**练习3.4 强制类型转换**

```c
src_t	*sp;
dest_t	*dp;
返回：
    *dp = (dest_t) *sp;
思路很简单，我们就是先从参数1寄存器放入
```

```assembly
src_t			dest_t			code
long 			long			movq	(%rdi),	%rax		#param1 -> ret
								movq	%rax,	(%rsi)		#ret -> param2
char			int				movsbl	(%rdi), %eax		#保留符号
								movl	%eax, 	(%rsi)		#movl自动清零高32位
char 			unsigned		movzbl	(%rdi), %eax
								movl	%eax, 	(%rsi)
unsigned char	long			movzbl	(%rdi), %eax		#movl自动补0
								movl	%eax, 	(%rsi)
int				char			movl	(%rdi),	%rax
								movb	%al,	(%rsi)
unsigned		unsigned char	movl	(%rdi), %eax
								movb	%al,	(%rsi)		#直接截断即可
char 			short			movsbw	(%rdi), %ax
								movb	%ax,	(%rsi)
```

注意事项：

- ** 大转小 **不用movz/movs，直接mov即可
- 以及一般的**mov指令必须要求前后寄存器长度是一致的**！
- `movl` / `movzbl`都是会**自动高位清零**的（特别注意byte需要先补0）
- **CPU同时拉伸数据长度和写入内存是不可能完成的**！可以善用MOVL自动清高位性质

- 注意！X86-64是小端的！我们从地址开始取的是低位！因此如果原本数据是int(l)，要转换为char(b)，我们直接movb即可，movb意思就是从地址开始抓



#### 3.4	栈/数据传输

##### 数据传输

我们显然知道CPU想要处理信息就得把数据放到寄存器里面处理。

一般来说rdi存储第一个传递参数，之后是rsi/rdx/rcx/r8/r9.

**e.g.** 翻译到汇编：

```c
long exchange(long *xp, long y){
	long x = *xp;
	*xp = y;
	return x
}
```

```assembly
exchange:
	movq	(%rdi),	%rax		#Mem(p1) -> return reg
	movq	%rsi,	(%rdi)		#reg(p2) ->	Mem(p1)
	ret
```

这告诉我们两点：

- ** 局部变量一般是保存在寄存器里面的 **，而非内存
- 指针就是地址，间接引用指针就是把指针放到寄存器作为内存引用

**习题 3.5**：把汇编代码翻译回C

```c
void d1(long *xp, long *yp, long *zp){
    long *tp1, *tp2, *tp3;
    *tp1 = *xp;
    *tp2 = *yp;
    *tp3 = *zp;
    *xp = *tp2;
    *yp = *tp3;
	*zp = *tp1;
    return *tp3;
}
```

- 注意这里有一点，汇编翻译回C是有豁免的，你不用管什么那个变量先后定义， 只要逻辑功能是一样的汇编代码理想上就是一样的 

##### 栈

前面讲过，栈是向下增长的，换句话说栈顶永远是地址最低的那个
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128202438568.png" alt="image-20260128202438568" style="zoom:50%;" />

**e.g.** 我们要把%rax的值压栈/出栈：（0x123）

```assembly
pushq	%rax
它实际等价于:
	subq	$8,		%rsp		#栈顶指针寄存器-8即增长栈(-8字节)
	movq	%rax,	(%rsp)		#把rax压入栈
popq	%rax
它等价于:
	movq	(%rsp),	%rax
	addq	$8,		%rsp
```



**总结**以下：目前我们讲了这些
![image-20260128204648432](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128204648432.png)



#### 3.5 算术和逻辑运算指令

整体来说，整数运算命令有以下几个：![image-20260128204923391](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128204923391.png)

- 除了leaq(毕竟地址长度就是q64)其他指令都有不同的长度变种。
- 操作分为4组：加载有效地址 / 一元运算 / 二元运算 / 移位

##### ` leaq`指令

他的功能其实就是`movq`的变形，但是不同的是他是直接把一个有效地址写入目的操作数。
特别需要注意的是，** 地址运算本身其实可以实现简单的算术操作 **。
比如若`%rax` = x，那么`leaq 7(%rdx,%rdx,4),%rax` 就是令`%rax`=5*x+7
为了进一步说明，我们看看下面这个例子

```c
long scale(long x, long y, long z){
    long t = x + 4 * y + 12 *z;
    return t;
}
```

```assembly
leaq	S	D
scale:
	leaq	(%rdi, %rsi, 4),	%rax	#x+4y
	leaq	(%rdx, %rdx, 2),	%rdx	#z+2z = 3z
	leaq	(%rax, %rdx, 4),	%rax	#x+4y+4*(3z)
	ret
```

使用这种方法可以进行加法和有限形式的乘法，特别适合这种简单的式子，可以大大提高效率**e.g. **

```assembly
leaq	7(%rdx, %rdx, 4),	%rax
```

$$
Imm(rb, ri, s) = Imm + rb + ri *s.
$$

显然这里rax = 7 + 5x



-----

补充：**常数乘法优化**
比如153 x = (10011001) x = (x << 7 + x << 4) + (x << 3 + x)
		  = y << 4 + y
从这里也可以看出，我们的次数是与1的个数有关的，怎么简化？

->可以转换为**正则有符号数编码CSD**：
也就是把连续的1转换为 溢出一位 和 1位补码 代替（相当于-）
比如`11 1100 1110 1111`就可以转换为<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128224655226.png" alt="image-20260128224655226" style="zoom:60%;" />，从低位扫描：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128224747919.png" alt="image-20260128224747919" style="zoom:50%;" />
就转化为了 x<<14 - x<<10 +x<<8 -x<<4 -x

----



##### 一元操作

| Instruction | Effect        |
| ----------- | ------------- |
| INC D       | D++    自增   |
| DEC D       | D--      自减 |
| NEG D       | -D       取负 |
| NOT D       | ~D      取反  |

一元操作只关心这个地址的值

##### 二元操作

| Instruction | Effect                              |
| ----------- | ----------------------------------- |
| ADD S, D    | D <-  D+S  加                       |
| SUB S, D    | D <-  D-S   减                      |
| IMUL S, D   | D <-  D*S   乘 **(注意顺序** ) |
| XOR S, D    | D <-  D^S   异或                    |
| OR X, D     | D <-  D\|S   或                     |
| AND S, D    | D <-  D&S  与                       |

这里S就是源，类型不限；但是D既是源又是目的，所以不能是立即数

**习题3.8**：
![image-20260128225733986](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128225733986.png)

```assembly
指令							目的				值
addq  %rcx, (%rax)			0x100			0xFF+0x1
subq  %rdx, 8(%rax)			0x108			oxAB+0x3
imulq $16,(%rax,%rdx,8)		0x118			0x31
incq  16(%rax)				0x110			0x14
decq  %rcx					%rcx			0x0
subq  %rdx,%rax				%rax			0xFD
```

注意：

- (%reg)在这里是一个地址，我们相加的是地址指向的值
- 地址是16进制！！！`0x108` + `0x8` = `0x110`

##### 位移操作

| Instruction | Effect                         |
| ----------- | ------------------------------ |
| SAL k, D    | D <- (D<<k)算术左移            |
| SHL k, D    | D <- (D<<k)逻辑左移（与SAL等价 |
| SAR k, D    | D <- (D>>ak) 算术右移          |
| SHR k, D    | D <- (D>>lk) 逻辑右移          |

特别的，** k只能是 移位寄存器`%cl`/ 立即数！ **
注：`%cl`是`%rcx`的低8位

同时，对于数据位数2^m，移位量只取决于我们`%cl`的低m位
比如salb，操作数是8位，那么自然就是低3位决定![image-20260128232720482](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128232720482.png)

**习题3.9**

```c
long shift_left4_rightn(long x, long n){
    x <<= 4;
    x >>= n;
    return x;
}
```

```assembly
shift_left4_rightn:
	movq	%rdi, %rax	;Get x
	salq	$4,	%rax	;x <<= 4
    movl	%esi, %ecx	;Get n (4bytes)因为long
    sarq	%cl, %rax	;x >>= n
```

**e.g.**

```c
long arith(long x, long y, long z){
    long t1 = x ^ y;
    long t2 = z * 48;
    long t3 = t1 & 0x0F0F0F0F;
    long t4 = t2 - t3;
    return t4;
}
```

```assembly
arith:
	xorq	%rsi,	%rdi			;x <- x^y
	leaq	(%rdx, %rdx, 2),%rax	;z*=3
	salq	$4,	%rax				;z<<=4
	andl	$0x0F0F0F0F,	%rdi	;t1 & 0x...
	subq	%rdi,	%rax			;t2 - t3
	ret
```

**习题 3.10**

```assembly
arith2:
	orq		%rsi,	%rdi
	sarq	$3,		%rdi
	notq	%rdi
	movq	%rdx,	%rax
	subq	%rdi,	%rax
	ret
```

翻译为C：

```c
long arith2(long x, long y, long z){
    long t1 = y | x;
    long t2 = ~(t1 >> 3);
    long t3 = z;
    long t4 = t3 - t2;
    return t4;
}
```

**习题 3.11**

```assembly
xorq	%rdx,	%rdx
```

尽管C代码里面并没有异或操作，但是还是有这行代码，它的作用就是把寄存器清零，它等价于：

```assembly
leaq	$0,	%rdx
```

优点一方面是我们只需要关心这个寄存器本身，同时它会使用更少的字节数，因为立即数需要把`$0 = 0x00000000`存入指令，而异或只需要两个字节即可；同时现代CPU本身就会对`xor`优化，看到这个指令自动清零
而且事实上我们更多使用：

```assembly
xorl	%eax,	%eax
```

因为`xorl`也会自动把高位清零！

##### 特殊算术操作

下面是针对`八字(oct word)`描述的运算符

| Instruction | Description  |
| :---------: | :----------: |
|   imulq S   | 有符号全乘法 |
|   mulq S    | 无符号全乘法 |
|    cqto     |  转换为8字   |
|    idivq    |  有符号除法  |
|    divq     |  无符号除法  |

一般来说`mulq` / `imulq`本来是作为2操作数的，此时结果也是4字64位的

###### 128位乘法：

而主要问题是我们乘法如果是两个64位，为了不丢失精度，结果应该是** 128位 **的。
因此`mulq`/`imulq`采用了`%rax`作为第64位，`%rdx`作为高64位，二者构成寄存器对。此时这两个指令只有一个操作数`%reg`，等价于: ** （这两条指令一个数字必定在%rax，另一个作为S给出） **
`%rdx(高)`|`rax(低)` <- `%reg` * `%rax`
**e.g.**

```c
#include <inttypes.h>
typedef unsigned  __int128 uint128_t
void store_uprod(uint128_t *dest, uint64_t x, uint64_t y){
    *dest = x * (uint128_t) y;
}
```

```assembly
dest in %rdi, x in %rsi, y in %rdx
store_uprod:
	movq	%rsi,	%rax		;x -> rax（low）
	mulq	%rdx				;(%rdx << 64 | %rax) <- %rdx * %rax
	movq	%rax,	(%rdi)		;rax(low) -> (%rdi)
	movq	%rdx,	8(%rdi)		;rdx(high) -> (%rdi) + 8
	ret
```

###### 除法 / 取模

同样使用单操作数来实现，比如有符号`idivl`将`%rdx(high64)`与`%rax(low64)`合在一起作为被除数，除数是被指定的S，之后把商放到`%rax`，余数放到`%rdx`。如果是有符号的除法，还需要用指令cqto(无操作数，读出%rax的符号然后扩展到%rdx所有位)，无符号直接清零即可
**e.g.**

```c
void remdiv(long x, long y
			long *qp, long *rp){
	long q = x / y;	long r = x % y;
    *qp = q;		*rp = r;
}
```

```assembly
x in %rdi, y in %rsi, qp in %rdx, rp in  %rcx
remdiv:
	movl	%rdx,	%r8		;copy qp
	movl 	%rdi,	%rax	;x -> lower 8 bytes of dividend
	cqto					;sign-extend to upper 8 bytes of dividend
	idivq	%rsi			;有符号除法，参数y被除数
	movl	%rax	(%r8)	;商在rax,保存到%r8存好的*qp地址
	movl	%rdx	(%rcx)	;余数
	ret
```

但是实际应用的时候我们不太会碰到这种现象，因为正常都是结果是long * long = long。只有在高精度计算和安全检查时才会使用

**习题 3.12**





#### 3.6 控制流

##### 3.6.1 条件码寄存器

###### 条件码寄存器：

是一组单位寄存器，用于描述最近一条算数或逻辑操作的属性，可以检测这些寄存器来执行条件分支指令

- **CF**：进位标志，最近的操作触发了一次进位，可用于检查无符号溢出
- **ZF**：零标志。最近操作结果为0
- **SF**：符号标志位。最近结果为负数
- **OF**：溢出标志位。最近出现了一个补码溢出（正 / 负溢出）

除了`leaq`之外其他我们说过的那些3.5的指令都会设置条件码。

###### 算术/逻辑操作的影响：

- XOR会自动把溢出/进位标志位置零
- 移位时进位标志将会被设置为最后一个被移出的位，溢出标志为0
- INC/DEC会设置溢出和零标志，但是不会影响进位标志位（这是因为我们要方便处理循环，因为INC往往就是用于循环，如果循环时触发进位那就会影像我们内部的运算，比如一个256位的加法

###### 专门设置条件码的寄存器：

1. ###### compare比较指令

   根据`S2 - S1`修改条件码寄存器

   ```assembly
   cmp	s1,	s2	
   cmpq	%rax,	%rbx
   ```

2. test测试，根据`S1 & S2`来修改条件码寄存器

   ```assembly
   test	S1,	S2
   testq	%rax,	%rax	;判断%rax
   ```

   特别地，`S1 = S2`时可以专门用来检验寄存器的正/负/零；
   以及可以用掩码来筛选我们关注的位

##### 3.6.2访问条件码

条件码一般不会需要直接读取，常见使用方法：

1. ** 根据条件码的某种组合，把一个字节设置为0/1 **

2. ** 条件跳转到程序的某个部分 **

3. ** 有条件地传递数据 **

##### 3.6.1 `SET`指令

针对的是情况1，这组指令的区别就是他们考虑的条件码组合是什么，不同的后缀指明了它们所考虑的条件码组合。
功能：一条`SET`指令的目的操作数是一个** 低位单字节 **寄存器元素 / 一字节内存，指令会读取状态寄存器把这个这个字节设置为0 / 1

| Instruction | syntax | Effect                                                       | Condition |
| ----------- | ------ | ------------------------------------------------------------ | --------- |
| `sete  D`   | setz   | D<- ZF                                                       | 零/相等   |
| `setne  D`  | setnz  | D<- ~ZF                                                      | 非零/不等 |
| `sets  D`   |        | D<- SF                                                       | 负数      |
| `setns  D`  |        | D<- ~SF                                                      | 非负      |
| `setg  D`   | setnle | D<- ~(SF^OF)&~ZF                                             | 有符号>   |
| `setge  D`  | setnl  | D<- ~(SF ^ OF)                                               | 有符号>=  |
| `setl  D`   | setnge | D <- SF ^ OF<br />(注意溢出，不能同时溢出或者为负，保证必须为负) | 有符号<   |
| `setle  D`  | setng  | D <- (SF ^OF) \|ZF                                           | 符号<=    |
| `seta  D`   | setnbe | D <- ~(CF \| ZF)                                             | 无符号>   |
| `setae  D`  | setnb  | D <- ~CF                                                     | 无符号>=  |
| `setb  D`   | setnae | D <- CF<br />溢出了为负                                      | 无符号<   |
| `setbe  D`  | setna  | D <- CF \| ZF                                                | 无符号<=  |

**e.g.**

```c
int cmp(data_t a, data_t b){
    return a < b ;
}
```

```assembly
cmp:
	cmpq %rsi, rdi
	setl %al				;放入%rax低字节
	movzbl	%al, %eax		;0扩展
	ret
```



##### 3.6.4 条件指令

###### 条件跳转

使用`jmp Label`作为跳转：

![image-20260210135549091](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260210135549091.png)

事实上，跳转指令常用的都是PC-relative作为跳转编码，就是一个地址偏移量：

```assembly
movq	%rdi, %rax
jmp		.L2
.L3:
	sarq	%rax
.L2:
	testq	%rax, %rax	# %rax & %rax
	jg		.L3			# if > 0, jmp
	rep; ret
```

---

这里的rep本身是用于字符串操作的，但是如果跳转后只有一个ret指令的地址，处理器会难以预测分支，CPU不喜欢跳转目标是一个单字节的ret命令，而rep本身就是用来被忽略的，变成2字节，现在已经不需要了

----

反汇编代码为：
![image-20260210140320936](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260210140320936.png)

###### 条件传送

![image-20260210140743091](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260210140743091.png)



注意，** 基于条件传送的指令往往比基于条件跳转的指令效率要高！！ **

考虑以下两个函数：

```c
long absdiff(long x, long y){
    long res;
    if(x < y)
        res = y - x;
    else 
        res = x - y;
    return res;
}

long cmovdiff(long x, long y){
    long rval = y - x;
    long eval = x - y;
    long ntest = x >= y;
    if (ntest)	rval = eval;
    return rval;
}
```

它们的汇编代码分别如下：

```assembly
cmovdiff:
	movq	%rsi, %rax
	subq	%rdi, %rax
	movq	%rdi, %rdx
	subq	%rsi, %rdx	;分别计算x-y和y-x提高效率
	cmpq	%rsi, %rdi
	cmovge	%rdx, %rax	;if>=，%rax = %rdx
	ret
```

这是因为** 条件跳转指令需要处理器去预测各分支的结果，但是条件传送不需要 **，因为这涉及流水线，CPU不会等一条指令跑完再下一条，而是把指令分为多个阶段提前处理，因此碰到跳转时CPU不清楚是要执行跳转还是非跳转的代码，因此会猜测一个方向提前处理，但如果猜错这个方向的提前处理就必须放弃，需要整个回滚。而** 条件传送就是把两个方向需要的计算都算好根据条件搬运数据，流水线始终是满载的，不会出问题 **

###### 循环

**e.g**.：

```c
long fact_do(long n){
	long res = 1;
	do{
		res *= n;
		n--;
	}while(n > 1);
	return res;
}
```

```assembly
fact_do:
	movl $1, %rax
	.L1:
		imulq %rdi, %rax
		decq %rdi
		cmpq $1, %rdi
		jg	.L2
		rep ret
```

比较一下for 和 while产生的汇编代码：（以阶乘为例）

```c
long fact_for(long n){
	long i;
	long res = 1;
	for(i = 2; i <=n; i++){
		res *= i;
	}
	return res;
}
long fact_while(long n){
	long i = 2;;
	long res = 1;
	while(i <= n){
		res *= i;
		i++;
	}
	return res;
}
```

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213092519786.png" alt="image-20260213092519786" style="zoom:50%;" />

** 关于编译器优化： **

但是一般来说编译器会把循环体和测试部分分开：

这是 GCC 在**不开启优化（`-Og`）**时最喜欢的逻辑。

```c
while (i < n) {
    sum += i;
    i++;
}
```

```assembly
    jmp  test         # 先不管三七二十一，跳到末尾去检查条件
loop:
    addq %rax, %rcx   # 循环主体 (Body)
    incq %rax
test:
    cmpq %rdx, %rax   # 检查条件 (Test)
    jl   loop         # 如果满足，跳回上面的 Body
```

这是因为这符合一般编译器的思路

GCC**开启优化(-O1 / -O2**)的时候：

此时编译器会把while替换为if-do-while(guarded-do-while):

```c
if (i < n) {
    do {
        sum += i;
        i++;
    } while (i < n);
}
```

```assembly
    cmpq %rdx, %rax   # 1. 入口检查 (The Guard)
    jge  done         # 如果不满足直接滚蛋
loop:                 # 2. 循环主体开始
    addq %rax, %rcx   
    incq %rax
    cmpq %rdx, %rax   # 3. 循环结束检查
    jl   loop         # 满足则跳回 loop
done:
```

**为什么要分开？（核心原因）**

- **减少跳转：** 在这个结构里，一旦进入循环，每次循环只需要 **一次** 判断和跳转（`jl loop`）。而“跳转到中间”模式虽然也只跳一次，但逻辑上多了一个初始的 `jmp`。

- **分支预测更友好：** 这种结构形成了一个闭环。现代 CPU 非常擅长预测这种“一直往回跳”的循环。

- **循环展开的基础：** 把 Body 独立出来，编译器可以更方便地进行**循环展开（Loop Unrolling）**，比如一次性把 Body 复制四遍，减少判断次数。

而如果写在一起，一方面这回导致流水线的断裂，比如你把判断写在循环体中间只有判断后才知道后面要不要执行

###### switch语句

通过整数索引值实现多条分支，通过跳转表实现，事实上无论switch有多少种选项，** 只要执行一次跳转指令就可以处理复杂分支跳转情况 **，因此它比一堆if-else要高效。
跳转表是一个数组，i是一个代码段的地址，代码段就是开关索引值等于i时采取的操作，

下面给出一个程序，它的汇编代码实际功能和右边的C代码一致：
![image-20260213162521123](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213162521123.png)
这里的`&&`符号是GCC作者创建的一个指向代码位置的运算符，相当于直接变成一张表，0～6，缺省的我们直接替换为default，下面是汇编代码：
![image-20260213162658729](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213162658729.png)

这里的`*`是间接跳转的意思，也就是告诉程序去`.L4 + 8 * %rsi`的位置，8是因为这里地址数是8字节的（64位），
跳转表如下：
![image-20260213164206566](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213164206566.png)
它告诉我们在`.rodata`（只读数据区)里面会有下面这张表，`.quad`告诉要预留长度8字节的空间放地址

我们可以总结一下，一般来说就是 几个常规的情况对应标号，一个作为default，另一个作为跳出switch的标号 

**习题3.31**

我的答案：

```c
void switcher(long a, long b, long c, long *dest){
	long val;
	switch(a){
		case 5:
			c = (b ^ 15);
		case 0:
			val = 112 + c;
			break;
		case 2:
		case 7:
			val = (c + b) << 2;
			break;
		case 4:
			val = a;
		default:
			val = b;
	}
}
```

#### 3.7 过程

过程是一种抽象，它提供一种封装代码的方法，用一组指定的参数和返回值实现功能，以供别处调用。过程的形式多样：函数(function)/方法(method)/子例程(subroutine)/ 处理函数(handler)等等

##### 3.7.1 运行时栈

一旦有一个过程需要的空间超过寄存器的大小，就需要在栈(stack)上面分配空间，称为**栈帧（stack fram）**<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213171705960.png" alt="image-20260213171705960" style="zoom:67%;" align = "left" />.前面说过栈是从高地址向下增长的，栈指针`%rsp`指向栈顶元素。
比如P调用Q时，会把返回地址压入栈中，指明当Q返回的时候要从哪里继续执行，他是P的一部分

















##### 3.7.2 转移控制

###### 返回地址

将控制从函数 P 转移到函数 Q 只需要简单地 把程序计数器(PC)设置为 Q 的代码的起始位置。 
但是显然从Q返回时需要知道继续执行P代码的位置，在x86架构里面这是通过 call Q调用来记录的 ，他会把 地址A(P的返回地址) 压栈，同时把PC设置为Q的起始位置，而`ret`的时候会把PC重新设为A.（从栈顶`%rsp`弹出，写入指令寄存器`rip`，也就是x86-64里面对应的PC寄存器）
**call指令只要出现就会默认`%rsp`- 8开辟8字节的空间，这是给返回地址用的！！**
**而如果需要更大GCC会帮我们用`subq`完成额外的空间开辟**
**同时机器自己`ret`时只会盲目返回`%rsp`的地址，GCC会保证`ret`时刚好就是返回地址（ret目的就是直接返回栈顶指针的内容）**

![image-20260213210423999](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213210423999.png)
再举个例子，比如一个程序执行时的流程如下：
![image-20260213210950192](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213210950192.png)
一开始`%rsp`存储的是正常的位置，之后执行调用top函数，`%rsp`减小创建栈帧（这个大小是GCC编译器计算好的)，之后同理

**习题3.32**：

![image-20260213221414934](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213221414934.png)
![image-20260213221437318](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213221437318.png)
![image-20260213221449623](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213221449623.png)

| 标号 | PC       | 指令  | `%rdi` | `%rsi` | `%rax` | `%rsp`                                  | *`%rsp`  | 描述            |
| ---- | -------- | ----- | ------ | ------ | ------ | --------------------------------------- | -------- | --------------- |
| M1   | 0x400560 | callq | 10     | -      | -      | 0x7fffffffe820                          | -        | 调用first(10)   |
| F1   | 0x400548 | lea   | 10     | -      | -      | 0x7fffffffe818<br />（8字节给返回地址） | 0x400565 | %rsi = x+1      |
| F2   | 0x40054c | sub   | 10     | 11     | -      | 0x7fffffffe818                          | 0x400565 | %rsi -= 1       |
| F3   | 0x400550 | callq | 10     | 10     | -      | 0x7fffffffe818                          | 0x400565 | 调用last(10,10) |
| L1   | 0x400540 | mov   | 10     | 10     | -      | 0x7fffffffe810                          | 0x400555 | %rax = %rdi     |
| L2   | 0x400543 | imulq | 10     | 10     | 10     | 0x7fffffffe810                          | 0x400555 | %rax *= %rsi    |
| L3   | 0x400547 | ret   | 10     | 10     | 100    | 0x7fffffffe810                          | 0x400555 | 返回            |
| F4   | 0x400555 | ret   | 10     | 10     | 100    | 0x7fffffffe818                          | 0x400565 | 返回            |
| M2   | 0x400565 | mov   | -      | -      | 100    | 0x7fffffffe820                          | -        | %rax -> %rdx    |



###### 参数传递

**传递寄存器顺序：**
![image-20260302082904636](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302082904636.png)
就像前面说的，`%rdi`,`rsi`,`rdx`,`rcx`,`r8`,`r9`

**压栈**

一旦参数超过6个就会需要通过栈，** 而在栈当中每个参数的地址就需要按8字节对齐，无论其长度多少 **
先把1~6号传递到寄存器，然后把剩下的放到寄存器里面（参数7在栈顶），这部分就是所谓的** “参数构造区” **，它属于调用者A的栈帧，但是也可以被所调用者B使用（只要movq 8(%rsp), %rax就能访问参数7，因为他就在这个位置)，等B完成后返回此时A会把栈顶指针加上长度把这部分内容丢弃

另一个规则是，** 只要函数发生调用时，x86-64就强制要求%rsp的地址是16的倍数！！！ **（所以有时候会强制再来一个`subq $8, %rsp`)。

举一个例子：

```
long caller(){
	long arg1 = 534;
	long arg2 = 1057;
	long sum = swap(&arg1. &arg2);
	long diff = arg1 - arg2;
	return sum * diff;
}
long swap
```

##### 3.7.4 栈上局部存储

一般使用栈帧上面的局部存储是以下情况之一：

- 寄存器不够用了
- 使用了`&`符号，因为它必然会产生一个地址
- 局部变量是数组或结构

第一个例子：
![image-20260302085027685](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302085027685.png)

```assembly
caller:
	subq	$16, %rsp		;减去16位，创造参数构建区
	movq	$534, (%rsp)	;放到%rsp处，栈顶
	movq	$1057, 8(%rsp)	;放到%rsp+8也就是其次的位置
	leaq	8(%rsp), %rsi	;8+%rsp地址传递为第二个参数
	movq	%rsp, %rdi		;%rsp存储地址为第一个参数
	call	swap_add
	movq	%rsp, %rdx		;get arg1
	subq	8(%rsp), %rdx	;arg1 -= arg2
	imulq	%rdx, %rax		;rax *= rdx
	ret
```

第二个例子：
![image-20260302085751164](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302085751164.png)

```assembly
call_proc:
	subq 	$32, %rsp		;参数构建区，开辟32个字节在栈上（其实用不到，但是我们保证%rsp是16的倍数
	#先分配好当前的局部变量
	movq	$1, 24(%rsp)	;x1
	movl	$2, 20(%rsp)	;x2
	movw	$3, 18(%rsp)	;x3
	movb	$4, 17(%rsp)	;x4
	#接下来就是准备参数传递了
	leaq	17(%rsp), %rax	;&x4先存到寄存器里面，因为我们不能直接内存->内存
	movq	%rax, 8(%rsp)	;&x4 -> arg8
	movl	$4,	(%rsp)		;arg7
	leaq	18(%rsp), %r9	;arg6
	movl	$3, %r8			;arg5
	leaq	20(%rsp), %rcx	;arg4
	movl	$2, %rdx
	leaq	24(%rsp), %rdi
	movq	$1, %rsi		;arg1
	call 	proc
	movslq	20(%rsp), %rdx	;获取第一个参数X2，convert to long
	addq	24(%rsp), %rdx	;X1 += X2
	movswl	18(%rsp), %eax	;X3扩展为int，到rax
	movsbl	17(%rsp), %ecx	;X4扩int,rcx
	subl	%ecx, %eax
	cltq					;eax -> rax位扩展
	imulq	%rdx, %rax
	addq	$32, %rsp		;栈指针减去32，把构建区丢弃
	ret
```

-----

#### 栈上的访问：

** x86-64数据永远是小端的 **，也就是低位数据存储在更低的地址，而且** 数据的地址就是最低那位的地址 **，读取数据时是** 从低位往高位读取 **

call指令会自动加8字节，这个内容放的就是%rsp之后的返回地址

----

##### 3.7.5 寄存器上的局部存储

我们必须保证寄存器活动时被调用者不会覆盖调用者的寄存器，因此有惯例的。

** `%rbx`,`rbp`，`r12`~`r15`为被调用者保存寄存器 **，当P调用Q时，Q必须保证这些寄存器不被改变。
显然想要不改变要么不动要么就把他们压栈。因此只需要P提前把内容放入这几个寄存器就可以保证不被影响

** 其他的所有寄存器，包括`%rsp`都被划分为调用者保存寄存器 **，这表明任何过程都可以改变他们，**保证他们没问题是P的责任**（所以为“调用者保存”）

![image-20260302093147875](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302093147875.png)

```assembly
X IN RDI, Y IN RSI
P:		
	#P要使用被调用者保存寄存器，所以需要提前压栈
	pushq	%rbp
	pushq	%rbx
	subq  	$8, %rsp	;开辟8字节存储，保证调用前%rsp是16的倍数（因为call已经开辟了8）
	#这里因为x可能会被Q改变，所以我们需要先保存它
	movq	%rdi, %rbp
	movq 	%rsi, %rdi
	call Q
	#因为需要再次调用可能改变%rax，先保存%rax
	movq	%rax, %rbx
	movq	%rbp, %rdi	;取出X
	call Q
	addq	%rbx, %rax
	addq	$8, %rsp
	popq	%rbx
	popq 	%rbp
```

##### 3.7.6 递归过程

前面的规则已经保证递归可以自然执行

#### 3.8 数组分配

比如一个数组E，它的起始地址放在`rdx`里面，i放在`rcx`里面，若他是int类型，那么直接：

```c
movl	(%rdx, %rcx, 4), %eax
```

##### 3.8.2指针运算

C对指针的运算是根据指针引用的数据类型的大小伸缩的，比如`p + i`实际上等于`xp + L * i`（L是数据的字节数），同时A[i]等价于*(A + i)

##### 3.8.3 嵌套数组

`&A[i][j] = (Xa + L * (i * C + j))`，

##### 3.8.4 定长数组

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302105150977.png" alt="image-20260302105150977" style="zoom:67%;" />

比如我们要完成一个矩阵乘法（只算Ai行和Bk列的内积），编译器生成的反汇编后发现其实可以这样优化：

```assembly
int fix_prod_ele_opt(fix_matrix A, fix_matrix B, long i, long k){
	int *Aptr = &A[i][0];
	int *Bptr = &B[0][k];
	int *Bend = &B[N][k];
	int res = 0;
	do{
		res += *Aptr * *Bptr;
		Aptr ++;
		Bptr += N;
	}while(Bptr != Bend);
	return res
}
```

##### 3.8.5 变长数组

C99开始才引入了可以表达式求值的数组维度`int A[exp1][exp2]`
比如我们要访问n*n的数组：

```c
int var_ele(long n, int A[n][n], long i, long j)
    return A[i][j];
```

n必须在A前面才可以计算。

而GCC产生的代码如下：

```assembly
n IN RDI, A IN RSI, i IN RDX, j IN RCX
var_ele:
	imulq	%rdx, %rdi 				;n*i
	leaq	(%rsi, %rdi, 4), %rax	;Xa + 4 * n * i
	movl	(%rax, %rcx, 4), %eax	;+= 4 * j，访问后存到rax里面
	ret
```

另一个例子：
![image-20260302110330752](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302110330752.png)





#### 3.9 异质数据结构

##### 3.9.1 struct

比如下面这个例子：

```c
struct rec {
	int i;
	int j;
	int a[2];
	int *p;
}
```

这需要24个字节（4+4+4*2 +8):
![image-20260302110726854](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302110726854.png)

##### 3.9.2 union

比如这两个声明：

```c
struct S3{
    char c;
    int i[2];
    double v;
};
union U3{
    char c;
    int i[2];
    double v;
}
```

在x86-64 linux上编译：偏移量如下
![image-20260302111153097](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302111153097.png)

联合的作用：1、我们知道一个数据结构里面两个不同的字段是互斥的，比如一个二叉树它要么是父节点存储地址要么是叶子节点存储数据。（我们一般会加上一个标识判断类型）
2、针对强制类型转换，节省空间：

![image-20260302111733922](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302111733922.png)



##### 3.9.3 数据对齐

**对齐原则**就是**任何K字节大小的基本对象**的**地址必须是K的倍数**

![image-20260302111937701](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302111937701.png)
而一旦有对不起的情况，编译器就会自动预留空间给它补齐

比如在**结构体**里面，要有两条规则：

- **成员对齐**（内部偏移量）：每个成员的起始地址只要求是它自身长度的整倍数
  ![image-20260302113256646](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302113256646.png)
- **整体对齐**（末尾填充）：每个结构体的总大小必须是它里面最长那个元素长度的整倍数
  ![image-20260302113249181](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302113249181.png)

** 因此声明结构体的时候我们往往把短的放到后面，减少偏移量带来的问题 **

另一方面也可以**强制声明**要求机器分配的所有数据/代码以相同的长度对齐，比如**跳转表**里面：

```assembly
.section .rodata
.align 8          # 确保下面的跳转表从 8 的倍数地址开始
.L4:
    .quad .L1     # 每个地址占 8 字节，这样它们都在对齐的位置上
    .quad .L2
```

这一句`.align 8`只会对下一个产生的数据生效，加上这一句保证开始的必然是8的倍数

同时在**全局变量**里面也需要，汇编器自己是不会管这些的，加上这一句他才会检查是否是x的倍数。

#### 3.10

![image-20260302141936234](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302141936234.png)

##### 3.10.3 内存越界/缓冲区溢出

C对数组引用的边界不会进行任何检查，局部变量与状态都放在栈里面，那么数组越界的写会破坏栈里面的状态信息，此时ret就会碰到问题。

下面是一个很经典的例子：
![image-20260302142514533](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302142514533.png)
GCC给出汇编代码如下：
![image-20260302142803912](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302142803912.png)

显然我们可以使用的只有16字节，一旦超限，它就会进入调用者的返回地址，会让rsp跳转到不知道的地方：
![image-20260302142930215](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302142930215.png)
同时缓冲区溢出更大的问题是他会让程序执行它本来不想执行的函数，通常我们输入一个字符串，它包含一些可执行程序的字节编码(exploit code)，另外还有一些字节会用一个指向攻击代码的指针覆盖返回地址，那么ret时就会跳转过去。因此任何对外的接口都必须做好保护。

##### 3.10.4 对抗缓冲区溢出

###### 1.栈随机化

让栈的位置在每次运行时都会变化，实现的方法是程序开始前在栈上面分配一段随机大小的空间，不使用它。
在linux里面这已经成为标准行为，它属于** 地址空间布局随机化（ASLR） **，它使得运行时程序的不同部分（代码/库代码/栈/全局变量/堆等）会被加载到内存的不同区域。

但是显然这会被穷举破解，比如用一堆nop指令序列，它的作用就是让PC++，指向下一指令，只要能猜中这段序列中的某个地址就能跳转到想要的地址

###### 2. 栈破坏检测（金丝雀）

在缓冲区与栈状态内容间加入一个金丝雀的随机值，一旦发生改变就可以停止。
![image-20260302145117808](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302145117808.png)

我们先从内存读出一个随机值，把他存入%rsp偏移8的位置，`%fs:40`表示它使用段寻址（原本指的是一个附加寄存器fs，现在已经没有了，它就是一个指针，被放在每个线程的本地存储TLS里面）把这个值放到一个只读段里面放置更改。

###### 3. 限制可执行代码区域

即限制哪些内存区域能够存放可执行代码，其余部分只允许读写。
虚拟内存本身就是分页的，2048/4096字节，操作包含读/写/执行。

但是显然这是不安全的，AMD引入了NX（No-execute）位，区分了读和执行访问模式。栈此时只能读写，不可执行

##### 3.10.5 支持变长栈帧

比如alloca函数

因为不知道具体多长，只能分配在栈里面，返回时要释放这个栈帧
![image-20260302152725176](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302152725176.png)

```assembly
n in %rdi, idx in %rsi, q in %rdx
vframe:
	pushq	%rbp				;先保存rbp帧指针（被调用者保存）
	movq	%rsp, %rbp			;rbp变成当前的栈顶指针（作为栈底）
	subq	$16, %rsp			;开辟16字节给i(后8字节不用)，16的倍数时才能移动rsp
	leaq	22(,%rdi,8),%rax	;22+n*8 -> rax
	andq	$-16, %rax			;清空低4位，这一步是在向上取整（8 + 15），保证rsp=16n + 8
	subq	%rax, %rsp			;开辟空间给动态数组
	leaq  	7(%rsp), %rax		;rsp+7,目的是向上取整，清空给8字节
	shrq 	$3, %rax			;右移3位，因为地址是8字节的，必须取整
	leaq	0(, %rax, 8), %r8	;8 * rax也就是&p0的位置
	movq 	%r8, %rcx			;rcx变成p的起始位
	#到上面为止就已经创建好了一个数组了（至少8n的字节以供使用）
	#下面是循环部分：i in %rax, n in %rdi, p in %rcx, q in %rdx
	.L3:
		movq	%rdx, (%rcx, %rax, 8)	;q -> p[i]
		addq	$1, %rax				;rax ++
		movq	%rax, -8(%rbp)			;rbp - 8也就是i的位置
	.L2:
		movq	-8(%rbp), %rax
		cmpq	%rdi, %rax
		jl		.L3						;i < n 继续循环
		
		leave							;恢复rsp和rbp
		ret
```

显然，如果栈帧本身是动态长度的，我们就不可以直接通过rsp找到返回地址以及各种 局部变量（这是主因，因为生成汇编代码时**我们不知道局部变量相对于rsp的偏移，也就无法生成高效的代码**） ，为了管理变长的栈帧，x86-64使用**`%rbp`寄存器**作为** 帧指针（frame/base pointer） **，这也是为什么叫bp。
它的作用就是作为一个固定的地址指针，时刻指向当前栈帧的底部，之后rsp无论怎么动我们都可** 直接通过rbp找回局部变量的位置 **（他们一般都是挨着rbp的，而变长数组会靠近栈顶指针rsp）。

那么再来解释一下上面这个代码的几个地方，先压栈保存rbp，然后把rbp变成当前栈顶指针rsp的位置作为之后的栈底（返回地址则是rbp+8处），之后先分配给i空间，我们知道** 调用call后rsp必须要求是16的倍数 **，之前push q导致现在地址是16n+8，而int是8,现在应该是16的倍数，但是call本身又会+8,为了保证之后调用其他函数不出问题我们这里才先额外分配个8字节。之后先把rax变成22 + 8 * n（** 这里的22= 23 = 8 + 15 - 1，8给的是金丝雀，15是为了刚好向上取整，最关键的是这个1,因为事实上一个8的倍数加上22或23再去掉低16位是等价的！！ **），再通过地址掩码（16 = 0x0001 0000,-16就是取反加一0x1111 0000，**清空了低4位**)，这就相当于向上取整保证了结果是16的倍数，这么做还是保证rsp的16倍问题。



---

**向上取整公式**（2的次方）：(x + ALIGN - 1) & ALIGN

** rsp **必须保证是** 16n - 8 **（除了call后那一段）

**leave**是专门用于变长栈帧的指令，它把rsp恢复为rbp的位置，rbp再从栈里面弹出上一个rbp的位置，之后ret时rsp直接就是可以执行跳转

同时我们发现**循环里面计数变量自增时一般用add 1而不是INC指令**，这是因为INC不会修改CF,这样流水线时会影响速度，因为必须计算完前面的才可以，而且inc前面需要一个前缀，并不简洁

----



#### 3.11 浮点代码

Pentium和MMX出现使得AMD/Intel都引入了媒体指令以支持图像处理，本意是让多个操作以并行的方式执行，称为**单指令多数据(SIMD)**，它允许对多个数据进行同一个操作，之后从MMX到SSE（streaming SIMD Extension,流式SIMD扩展），以及最新的AVX（Advanced Vector EX）。SSE2的媒体指令开始包括对标量浮点数的操作指令，提供了一组专门的寄存器和指令。

接下来讲的是基于AVX2的。命令行参数给定-mavx2时GCC就会生成AVX2代码，使用ATT格式表述。

如下图所示，AVX浮点体系结构允许数据存储于16各YMM寄存器中，他们的名字是`%ymm0`~`%ymm15`，每个YMM是256位也就是32字节。当对标量数据（单个数据）操作时，这些寄存器只保存浮点数，而且只使用低32位(float)或64位(double)，汇编代码把他们称为`%xmm0`~`%xmm15`，也就是ymm的低128位（16字节）

![image-20260302211958287](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302211958287.png)

##### 3.11.1 浮点传送和转换

1. 下面是浮点数传送的代码，引用内存的指令是标量指令，意味着只能对单个而不是一组封装好的数据操作。数据只可能在内存或者其他的XMM寄存器（X）当中。这些指令不要求内存对齐，不过一般还是建议64位8字节对齐好， 内存的引用方式（间接寻址）和整数的MOV是一样的 。
   ![image-20260302213250194](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302213250194.png)
   GCC只用标量传送操作从内存传递数据到XMM或XMM传递到内存，而如果在XMM之间传送则会使用最后的向量传送也就是`vmovaps`（单精度)和`vmovapd`（双精度)。这里的'a'表示aligned也就是对齐的，他们必须保证是满足16字节对齐的，换言之这两条指令如果被用于内存时也要求这一点

   比如下面这个例子：

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302213919934.png" alt="image-20260302213919934" style="zoom: 77%;" />

```assembly
#v1 in %xmm0, src in %rdi, dst in %rsi
float_mov:					;返回值需要在xmm0里面
	vmovaps	%xmm0, %xmm1
	vmovss	(%rdi), %xmm0
	vmovss	%xmm1,	(%rsi)
	ret
```

2. 之后则是浮点与整数的转换：
   ![image-20260303093227945](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303093227945.png)
   上面这几条指令就是对浮点的值进行截断，向0舍入，存储入通用寄存器，区分了是32位还是64位寄存器

   我们把 `vcvtts2si` 拆解开来看：

- **v**: Vector（向量扩展，AVX 版本的指令前缀）。
- **cvt**: Convert（转换）。
- **t**: **Truncate（截断）** —— 这是你问题的核心。
- **s**: Scalar（标量，只处理一个数）。
- **s2**: Single precision to...（单精度浮点数转...）。
- **si**: Signed Integer（有符号整数）。

具体来说，** “向0舍入”意思就是直接把小数点丢弃 **，因为浮点数是1.f * 2^E，显然就是对f位移罢了。
而一旦溢出了最大上限，它就会返回一个整数不确定值`0x8000000000000000`（最小负数）

3. 把整数转化为浮点数：
   ![image-20260303094329333](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303094329333.png)
   第一个就是待转换的操作数（整数)，第二个如果我们只使用X而不是Y就无所谓，一般我们让源2等于目的，比如下面这条指令就是转化为double，将结果放入xmm1的低字节部分。

   ```assembly
   vcvtsi2sdq	%rax, %xmm1, %xmm1
   ```

   4. 最后是两种浮点格式之间的转换
      1) 如果我们想把一个单精度转换为双精度，自然觉得应该要用：

      ```assembly
      vcvtss2sd	%xmm0, %xmm0, %xmm0
      ```

      但GCC会生成下面的代码：

      ```assembly
      vunpcklps	%xmm0, %xmm0, %xmm0
      vcvtps2pd	%xmm0, %xmm0
      ```

      具体来说，单精度是32位的，xmm为128位，可以放4个float
      `vunpcklps`是用来交叉放置两个XMM寄存器的值到第三个寄存器的，比如S1 = [s3, s2, s1, s0]，S2 = [x3, x2, x1, x0]，那么D = [s1, x1, s0, x0]，经过这条指令，xmm0 = [x1, x1, x0, x0]，之后`vcvtps2pd`则是把源寄存器低位的两个float扩展为两个double，那么这时候低位就是我们扩展后的double。
      （但是GCC这么做好像没啥意义？
      意义其实是为了** 避免伪依赖 **，因为`vcvtss2sd`只操作寄存器的低位，很容易让CPU认为高位是需要保留的，换句话说它必须做完所有对此寄存器的操作后才运行这条指令执行，而这么交叉一下（就很像寄存器先自己异或一下自己一样，** 告诉CPU这个寄存器过去的值对我无所谓 **）

      2）双精度转单精度也是差不多的：

      ```assembly
      vmovddup	%xmm0, %xmm0		;duplicate lower bits
      vcvtpd2psx	%xmm0, %xmm0		;
      ```

      `vmovddup`(duplicat)，先 把寄存器的低位扩展， [x1, x0] -> [x0, x0]，同样是告诉CPU高位我不在乎（方便流水），之后`vcvtpd2psx`功能则是把两个double转换为两个float放到低位，高位清零
      当然也可以直接`vcvtsd2ss`

   ----

   关于返回值寄存器：

   | **返回值类型**              | **使用的寄存器**           |
   | --------------------------- | -------------------------- |
   | `int`, `long`, `char`, 指针 | **`%rax`**                 |
   | `float`, `double`           | **`%xmm0`**                |
   | `long double` (80位)        | 专门的栈寄存器 `%st(0)`    |
   | 包含两个 `double` 的结构体  | **`%xmm0`** 和 **`%xmm1`** |

   -----

   举个例子：
   ![image-20260303101226246](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303101226246.png)

   ```assembly
   # i in %edi, fp in %rsi, dp in %rdx, lp in %rcx, return %xmm0
   fcvt:
   	vmovss	(%rsi), %xmm0			;f = *fp
   	movq	(%rcx), %rax			;l = *lp
   	vcvttsd2siq	(%rdx), %r8			;d = *dp, cvt long
   	movq	%r8, (%rcx)				;*lp = d
   	vcvtsi2ss	%edi, %xmm1, %xmm1	;i(s int) -> (s float) => xmm1
   	vmovss	%xmm1, (%rsi)			;*fp = i
   	vcvtsi2sdq	%rax, %xmm1, %xmm1	;l(64) cvt double
   	vmovss	%xmm1, (%rdx)
   	vunpcklps	%xmm0, %xmm0, %xmm0	;交叉数据，告诉CPU抛弃过去
       vcvtps2pd	%xmm0, %xmm0		;扩展float->double
       ret
   ```

##### 3.11.2 过程中的浮点

和原来差不多：

- %xmm0 ～7可以传递8个浮点参数，多的压栈
- 用%xmm0返回浮点值
- %xmm所有都是调用者保存的，对所有被调用者它们都是全新的

同时指针和整数还是属于通用寄存器的

##### 3.11.3 浮点运算

AVX2的简单的标量浮点运算指令：（注意** S1寄存器和内存都可以，S2/D必须是XMM寄存器） **![1](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303103245077.png)
比如一个简单的函数：
![image-20260303103554924](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303103554924.png)

```assembly
#a in %xmm0, x in %xmm1, b in %xmm2, i in %edi
funct:
	vunpcklps	%xmm1, %xmm1, %xmm1		
	vcvtps2pd	%xmm1, %xmm1
	vmulsd	%xmm1, %xmm0
	vcvtsi2sd	%edi, %xmm1, %xmm1
	vdivsd	%xmm1, %xmm2, %xmm2
	vsubsd	%xmm2, %xmm0, %xmm0
	ret
```

##### 3.11.4 浮点常数

编译器对浮点数是没法用随机数的，那么只能在内存里面为常量分配和初始化对应的存储空间：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303104535650.png" alt="image-20260303104535650" style="zoom:67%;" />

##### 3.11.5 浮点代码的位操作

这里注意，这些位操作是针对整个XMM寄存器的所有位
![image-20260303104827697](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303104827697.png)

##### 3.11.6 浮点比较操作

AVX这俩和COMP基本上相似的，也是S2 - S1
![image-20260303105110804](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303105110804.png)
比较3个条件码，零标志位`ZF`，进位标志位`CF`和奇偶`PF`（寄存器和前面的算是共用的)。
前面没讲奇偶是因为他不太常见（一般就是整数如果是偶校验也就是偶数个1触发)
而** 对于浮点数则是只要S1/S2有一个是NaN就触发奇偶`pf` **
具体规则如下了：
![image-20260303105616333](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303105616333.png)

** 条件跳转 **：

- 通常来说，只要一个是`NaN`就是无序，此时通过`jp(jump on parity)`就可以在无序时跳转
- 大于是`ja`，小于`jb`，等于`je`

比如：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303110007319.png" alt="image-20260303110007319" style="zoom:67%;" />

```assembly
# x in %xmm0
find_range:
	vxorps	%xmm1, %xmm1, %xmm1	;低位清零
	vucomiss	%xmm0, %xmm1	;compare 0: x
	ja	.L5						0>x neg
	vucomiss	%xmm1, %xmm0	;再比较一次保险一些，这次判断x是正数还是NaN
	jp	.L8						;NaN, posornan，那么直接跳过下面的部分，此时只剩下>=0的可能了
	movl	$1, %eax			;result = ZERO
	je	.L3						;就是0,那就结束
	.L8							;无序或者>0
		vucomiss	.LC0(%rip), %xmm0	;全局变量0和x比较
		setbe	%al				;条件传送 x>0置零，NaN置1
		movzbl	%al, %eax		;0扩展
		addl	$2, %eax		;rax += 2, 如果是0+2就是pos,1+2是OTHER
		ret
	.L5:
		movl	$0, %eax
	.L3:
		rep; ret
```

 **GCC喜欢在每一个条件跳转前面先比较一次** 





Bomb Lab

gdb:

先 break 在函数前面打断点再run

可以layout asm打开汇编指令界面，layout regs实时查看寄存器

查看寄存器作为指针指向的地址可以: x/s $rsi

跳转表不是在程序汇编里面的，而是在数据区，所以你只能手动查看，比如你不知道指向哪个地址，原本代码为jmp *0x402470(, %rax, 8)，就是跳转到这个地方，为了查看，还是用x/指令，这次为：
x/8gx 0x402470，

sscanf第一个参数rdi是输入地址，第二个参数rsi是格式字符串，返回值rax就是输入的参数个数

`x/`指令，作用就是查看内存数据，格式：

```shell
x/<num><format><unit> 或者x/<num><unit><format> 后面两个可以互换
```

比如8gx意思就是
8：从指定地址开始显示8个单位
g：单位长度：

- b: byte 1字节

- h: Half word 2字节
- w: word 4
- g: giant 8

x：格式：

- x是hex
- d是Decimal十进制
- i是Instruction指令，disas就是x/i
- s是string字符串









### 处理器体系结构

#### 4.1 指令集

这部分书里单独定义了一个y86-64的指令集

我们同样定义了15个通用寄存器，只不过和x86-64比少了%r15
![image-20260310135752024](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260310135752024.png)
状态码Stat表明程序现在是正常运行还是有异常

Y86-64其实就是一个x86的子集，它仅仅包含8字节的整数操作/寻址方式少

- movq只有4种：irmovq/rrmovq/mrmovq/rmmovq，i=立即数，r=寄存器，m=内存
  同时我们也不支持第二变地址寄存器，只有简单的基地址和偏移量
  一样的，我们也不允许立即数/内存直接到内存
- Opq也就是我们的整数操作，分别是addq/subq/andq/xorq，他们仅仅对寄存器操作（x86可以是内存），同样他们也会设置条件码ZF/SF/OF即零/符号/溢出
- 跳转指令，就是jmp/jle/jl/je/jne/jge/jg
- 条件传送指令，就是cmovle/cmovl/cmove/cmovne/cmovge/cmovg，格式要求和movq一样
- call就是把函数返回地址入栈，再跳转到我们call的目标函数地址，一样ret
- pushq/popq
- halt则是可以停止一切指令的执行，等价于x86的hlt，但是x86不允许。
  这指令可以停止处理器并且修改状态码为HLT

这个图片就可以帮我们理解为什么不能立即数/内存到内存，因为要保证指令字节长度是统一的![image-20260310141121376](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260310141121376.png)

可以看到，每条指令第一个字节用来表示指令的类型，高4位是代码部分(code)，低4位是功能部分(function)，代码值在0～0xB之间。可以看到，rrmovq指令和条件传送指令共用代码部分，它就是一种'无条件'传送
![image-20260310144952449](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260310144952449.png)

而寄存器，是0～0xE对应的编号，也就是寄存器标识符reg ID，占半字节。
程序寄存器存在CPU的一个寄存器文件当中，它就是一个以寄存器ID作为地址的RAM。而如果需要指明不需要访问任何寄存器时就用0xF代替
![image-20260310142442723](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260310142442723.png)

有的指令只有单字节，也有长的，首先可能会有附加的寄存器标识符字节，指定1～2个寄存器（rA/rB），如果只需要一个寄存器的指令就会把另一个设置为0xF

而有的指令会使用一个附加的4字节常数字，可以作为irmovq的立即数，rmmovq/mrmovq的地址指示符偏移量，以及分支/调用指令的目的地址。
特别，分支和调用指令目的需要是一个绝对的地址而不能通过PC相对寻址

具体来说，就比如rmmovq %rsp, 0x123456789abcd(%rdx)，第一个字节是40，而rsp放在rA字段，基址寄存器在rB字段，这个字节就是42,之后把这个8字节常数补齐成为8字节的序列，但是我们机器是小端的，也就是小的数字要放在小地址也就是前面，因为指令是从左到右读取的，那么就是cd ab 89 67 45 23 01 00了，放到一起就是40 42 ....

特别注意，指令集的重要性质就是字节编码的解释必须唯一，也就是任意一个字节序列要么是一个唯一的指令序列编码，要么就不合法，这是通过我们第一个字节的唯一的代码+功能组合实现的。当然反过来如果不知道一段代买序列的起始位置，我们也就不能很容易地去确定指令序列的划分。

x86-64是典型的CISC也就是复杂指令集计算机，而与之对应的是RISC也就是精简指令集计算机，具体来说，RISC不允许直接操作内存，必须先load处理完后再store

##### 异常

它就是程序员可见的状态码，在Y86里面就是4种：
![image-20260310145842755](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260310145842755.png)
2代表halt指令产生，3ADR代表非法内存，会发生在取指令/读写的时候，原因是我们限制最大访问地址，一旦超限就会触发；而4INS表示非法指令。

这个指令集里面仅仅在异常的时候停止，但是更完善的设计中往往就得引入一个**异常处理程序**(exception handler)

比如下面这个程序：
![image-20260310152132765](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260310152132765.png)

```assembly
start in %rdi, count in %rsi
sum:
	irmovq	$8, %r8
	irmovq	$1, %r9	;因为计算只允许寄存器之间
	xorq	%rax, %rax
	andq	%rsi, %rsi	;Set CC，即检查Count是否为0到条件码
	jmp test
loop:
	mrmovq	(%rdi), %r10
	addq	%r10, %rax
	addq	%r8, %rdi		;*start ++
	subq	%r9, %rsi		;count --
test:
	jne	loop				;count != 0
	ret
```

相比而言，我们这个指令集要求必须先把常数加载到寄存器，同时从内存计算也需要加载寄存器，不过优点是我们的算术操作允许了条件码的设置

比如下面这个例子，就是一个使用
![image-20260310153738522](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260310153738522.png)

`.`开头的词是汇编器的伪指令，告诉汇编器调整地址以便产生代码或数据，`.pos 0`告诉他要从地址0开始产生代码，











### 5 优化程序性能

#### 1、最安全的优化

GCC比如-O1的优化等级，他会主动预设出现最差的情况，进行最安全的优化，譬如如果出现两个指针引用，它就会默认会出现两个指针相同的情况，同时函数调用如果不知道其副作用，它就会预设调用本身是有用的。

#### 2、内联函数：

编译器会把函数调用替代为函数内容本身展开黏贴，之后再考虑优化（譬如预测函数的副作用，再以更简单的方法替换）

#### 3、描述程序性能：

显然通过时钟周期时更加靠谱的

#### 4、消除循环带来的低效率：

- 显然每次循环都会需要对测试条件本身进行求值，所以你最好把它固定下来（虽然理想情况是他可以识别出来）
- for的初值无所谓，但是判断条件以及循环尾很重要
- 一般来说只要确定次数且次数不大其实倒是会循环展开
- 总之你**一定要让边界尽可能在循环前明确**

#### 5、减少过程调用：

比如这个代码：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260316064320200.png" alt="image-20260316064320200" style="zoom:67%;" />
我们这里把这个调用函数获取内容的代码替换成直接通过数组的形式访问，事实上向量本身就是通过数组而非链表的形式存在的
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260316064525731.png" alt="image-20260316064525731" style="zoom:67%;" />
但是奇怪的是这并没有引入多少性能提升，这说明我们的内循环里面存在其他瓶颈

#### 6、消除**非必要的内存引用**：

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260316065318624.png" alt="image-20260316065318624" style="zoom:50%;" />
（上面这个代码每次就是在累乘，但是每次偏偏都要读写内存。显然上一次的rbx存的就是这一次从内存读出来的，完全没必要先读出来再放回去。）
我们可以优化这个问题，这个问题本质是因为使用的是这个dest，它本身是指向内存的，但是如果你**使用一个临时变量acc来积累这个过程，那寄存器就可以处理了**（换句话说如果你不需要一个全局的值来存储它，**用局部变量完全更快**）
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260316070124016.png" alt="image-20260316070124016" style="zoom:50%;" />

#### 7、现代处理器：

由于指令级并行以及分支结构的流水线冒险，性能大大提高。但是如果指令本身有严格的先后依赖关系，指令本身会产生延迟界限，即下一条指令开始之前这条指令必须先结束

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260324091636618.png" alt="image-20260324091636618" style="zoom:50%;" />

##### 1）**超标量处理器**

它可以在单周期执行多个操作，而且是乱序的。分为两个单元：**指令控制单元ICU**和**执行单元EU**，前者读取指令并且根据指令序列生成一组针对程序设计的操作，后者执行。

**ICU从指令高速缓存里面先读出指令**，它包含最近要访问的指令。通常这发生在这条指令被执行很早之前，因为**取指需要译码才能发送EU**执行。
但是如果碰到**分支结构**，往往就会采用**分支预测**，再进行**投机执行**。也就是先假定这是对的，然后对相关的内容进行取指译码，甚至在到判断分支点之前就开始执行。但是一旦发现预测错误，状态就会回到这个分支点

而**指令译码**就是把指令转化为基本操作/微操作序列。每个操作都可以完成简单的计算任务。
具体来说，一条只含寄存器操作的指令，如`addq %rax, %rdx`，它显然就是一个操作；而你比如涉及内存引用，`addq %rax, 8(%rdx)`，这个就相当于三个操作，先从指定内存读取值到处理器，再和rax相加，最后送回内存地址。
而分解后就可以允许任务在硬件单元间进行分割，并行地执行多条指令不同部分。（单时钟周期EU接收，分派到一组功能单元里面）

读写内存是通过**加载、存储单元**完成的，加载单元处理的是内存读到处理器，存储器反过来，它们都需要加法器来计算地址。它们通过中间的**高速缓存(data cache**，一个高速存储器，存放最近的访问数据)来访问内存，主要是DRAM读取太慢，所以先预先读好可以快速获取。

**投机执行**(speculative execution)时，操作本身是在被求值的，但是最终结果直到处理器确定了应该执行这些指令时才会把结果存入寄存器/内存。分支操作被送往EU不是确定分支往哪里去，而是确定预测本身是否正确，如果预测错误，EU会直接丢弃之前计算的所有结果，并且告诉分支单元预测错误以及正确的分支目的，此时分支单元就得重新取指（显然这会带来很大的性能开销）
换句话说就是**ICU不管真实条件，只会盲猜分支，然后预取路径指令译码丢给EU乱序执行**，而**EU直到流水线达到分支需要的判定寄存器数值时才会确定这一步是否正确**，正确就直接提交到寄存器/内存，**错误**就**删除前面所有**的结果，告诉**ICU重新取指**（这就会让流水线空转，因此**我们必须减少前后依赖，保证这段时间EU可以执行别的操作**）

**功能单元**被设计为执行不同操作的部分，比如"算术运算"执行的就是整数和浮点操作的不同组合。（因为程序有不同的要求）
以Intel Core i7 Haswell为例，一套ICU会配备8个功能单元：
0-Integer arithmetic, floating-point multiplication, integer and floating-point division, branches 
1-Integer arithmetic, floating-point addition, integer multiplication, floating point multiplication 
2-Load, address computation 
3-Load, address computation 
4-Store 
5- Integer arithmetic 
6-Integer arithmetic, branches 
7-Store address computation

而在ICU里面，**退役单元**用来记录正在进行的处理，保证它们遵守机器级程序的顺序语义，，换句话说其实就是控制寄存器的更新（包括通用、浮点、SSE/AVX）。具体来说，指令译码时相关信息就会被放在一个FIFO队列里面，直到 (1)指令完成且分支预测正确->退役，相关对程序寄存器的更新可以被提交执行 /(2) 指令完成但是分支预测错误->清空指令，丢弃所有结果 。

那么很显然，**任何对程序寄存器的更新只发生在指令退役时刻**。

而另一方面，为了加速一条指令到另一条指令的传送以及提交，采用了**寄存器重命名**（就是一个映射表），这样执行单元就可以直接把结果发送给对方了。（这本身也解耦了物理寄存器和我们抽象的程序寄存器，保证可以乱序执行不会冲突）
具体来说，当一条更新寄存器r的指令被译码后，就会有产生一个对操作本身的标记t，得到一个指向该操作结果的唯一标识符(r,t)，这个条目被放入映射表（维护每个寄存器r与更新该寄存器的操作的标记t），随后发送到操作单元时就会包含t作为操作数源的值。而当某个执行单元完成第一个操作时，就会生成结果$(v,t)$，说明操作t会产生v的值，此时所有等待t作为操作源的操作便都可以以v作为源值，这就是一种形式的数据转发（事实上这个过程是 EU直接把值存入一个物理寄存器，然后广播这个寄存器和标识符 ），这样就不必等这个指令退役才开始执行下一个等待资源的操作，保证了乱序和分支预测的执行

##### 2）功能单元的性能

我们用三个指标来刻画运算的性能：**延迟**---运算本身需要的时间、**发射**时间---两个连续同类型运算间需要的时钟周期、**容量**---能够执行该运算的数目
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260325170828116.png" alt="image-20260325170828116" style="zoom:67%;" />
我们发现加法与乘法远远快于除法（所以编译器一般会把常数除法直接替换为乘法+移位），整数快于浮点数。
而且更重要的是乘法与加法发射时间都为1，这代表 每个时钟周期都可以开始执行一个新的运算 。这是通过**流水线**实现的，** 流水线化的功能单元实现为一系列的阶段，每个阶段完成一部分运算 **（比如浮点加法包含3个阶段：处理指数值、小数相加、结果舍入）。算数运算可以连续地通过各个阶段，不用等待一个操作完成后再开始下一个，当然前提是要执行的运算是连续的且相互独立。**发射时间为1代表这个功能完全流水线化**。

而**除法器显然是不完全流水线化的，**而且**发射时间等于延迟，说明开始新的运算之前必须完成整个除法**（这是显然的，因为除法器他其实就是一个迭代减法器（暂时不说SRT算法），算完上一位余数才知道下一位要不要减）。

表示发射时间的另一个指标是**最大吞吐量**，即**容量除以发射周期**。比如图中加法吞吐量就是4，单周期可以处理4个新的加法

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260325173833559.png" alt="image-20260325173833559" style="zoom:50%;" />

这里加法器是被加载单元限制了，每个周期只能读取2个数据，而乘法器因为延迟为3个周期，没有受到影响

##### 3）处理器操作的抽象模型--数据流

首先看一下刚刚那个`conbine4`函数测量的CPE值：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260326131042227.png" alt="image-20260326131042227" style="zoom:67%;" />
这说明这个函数本身的性能是主要取决于加、乘法运算的

1. **从机器代码到数据流图：**
   数据流表示并不正式，不过可以辅助我们描述：
   <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260326131503625.png" alt="image-20260326131503625" style="zoom:50%;" />
   这4行代码，我们用直线表示涉及寄存器存取的操作，弧线表示不涉及寄存器而是在操作间传递的数据
   那么对于循环，我们可以把被访问的寄存器分为4类：
   - **只读**：仅仅作为源值。（这里就是`%rax`
   - **只写**：仅仅作为数据传送操作的目的
   - **局部**：仅仅在循环内部被修改和使用，两次迭代之间不相关。（这个例子里面就是条件码寄存器
   - **循环**：对于循环，既作为源值又作为目的，一次迭代产生的值在另一次迭代中会被用到。（这里就是`%rdx`/`xmm0`）

   那么很显然，制约我们程序性能的主要就是寄存器之间的操作链
   <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260401163427639.png" alt="image-20260401163427639" style="zoom:50%;" />
   我们进一步精简，只看一个周期的数据依赖关系，很显然左边操作需要5n个周期（1+1+3），而右边需要n个周期执行，所以右边不制约程序性能
   显然这里最制约的是我们的浮点数乘法操作，因为它的延迟等于循环本身的CPE值

   延迟界限是最基本的限制，决定了合并运算的速度，下面我们就要重新调整操作结构，增强指令级并行，换句话说，我们希望程序唯一的限制是吞吐量界限，得到1.00左右的CPE

#### 8 循环展开

主要就是可以减少不直接操作有助于程序结果的操作数量，同时也可以减少整个计算中关键路径上面的操作数量。还是那个程序，就是求向量累乘的，以下是采用"2*1循环展开"的版本。
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260401171807288.png" alt="image-20260401171807288" style="zoom:50%;" />
我们不能保证输入向量是2的整倍数，所以我们设置上限为n-1，最后来个循环来处理尾部单个数字。
以此类推，如果是$k * 1$的因子，那么上线就得是$ n - (k - 1)$，之后再处理尾部，它最多执行$k-1$次。

显然，这样展开后CPE会变小一些，主要是减少了整数加法的次数，但是其他情况并没有性能提高，因为已经达到了EU的延迟界限
![image-20260401172443843](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260401172443843.png)
而-O3一般编译器就可以自动进行循环展开了

#### 9 提高并行性----打破依赖链

我们以上的写法还是存在问题，因为加法和乘法本身的EU在这里已经是完全流水线化的，换句话说每个时钟周期可以开始一个新操作，而且操作本身可以被多个功能单元执行，但这里代码却不能利用这种能力，因为我们把累积值全部放到了一个单独的变量`acc`里面，前面的计算完成之前都不能计算新的`acc`，我们要做的就是打破这种顺序相关。

##### 1） 多个累积变量

如果一个合并运算本身是可交换可结合的，那么就可以把这个运算本身分解为多个部分，最后整体合并来提高性能
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260401173949423.png" alt="image-20260401173949423" style="zoom:50%;" />
这里就是这样，就是所谓的$2*2$循环展开，此时我们就可以打破延迟界限，逐渐达到吞吐界限。
当k足够大的时候，程序在几乎所有情况下都能达到吞吐量界限。

但是我们要注意==**这可能会引入舍入误差！！**==，比如如果奇数元素全部都是接近0.0，偶数全部很大，那就很麻烦

##### 2）重新结合交换

这是另一种打破顺序相关从而把性能提高到延迟界限外的方法
我们看到$k*1$循环展开并没有从根本上改变我们合并向量元素中的操作，但是以下改动是可以根本上改变合并执行的方式的：

```c
original(combine5):
acc = (acc OP data[i]) OP data[i+1];
new(combine7):
acc = acc OP (data[i] OP data[i+1]);
```

就叫做"重新结合交换"，因为括号本身改变了向量元素和累积值`acc`的合并顺序，这里被称为"$2*1a$"的循环展开形式。

看起来这两个语句似乎是一样的，但是CPE却告诉我们它影响了乘法的速度，突破了延迟界限
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260401175338420.png" alt="image-20260401175338420" style="zoom:50%;" />
原因是只有一个mul操作涉及了循环寄存器之间的数据相关链路，因为$data[i]*data[i+1]$是不需要依赖的，换句话说完全可以处理器把这些不依赖的操作先添入流水线里面操作。
也就是说，这里我们==**降低了操作本身对循环寄存器的依赖**==，让他们更加独立。

当然了，SSE到AVX，SIMD让单指令操作整个向量数据成为可能，因此吞吐量可以进一步提高



#### 10 其他限制因素

##### 1） 寄存器溢出

如果我们的 并行度超过了可用的寄存器数 量，编译器就会诉诸 **溢出(spilling)**，把某些临时值放到内存里面，通常是在运行时堆栈上分配空间。 

比如下面这种情况，如果并行度太高，结果反而性能还下降了，因为x86-64用16个YMM保存浮点数，16个通用寄存器，这样导致**处理器还得先把内容放到内存里面再取出来**反反复复
![image-20260401180623473](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260401180623473.png)

##### 2）分支预测和预测错误处罚

对于条件转移要考虑是否选择分支，对间接跳转或者过程返回指令则需要预测目标地址

在一个投机执行的处理器里面，处理器会开始执行预测的分支目标处指令。尽可能避免修改内存和寄存器，直到确认实际结果，正确就提交，错误就丢弃并返回正确的位置重新开始取指（不过条件传送本身是可以作为流水线化处理的一部分，所有不会有猜测错误的处罚）

以下原则是通用的：

1. **不要过分关心可预测的分支**
   比如边界检查，很多时候处理器都会把循环结束作为预测分支，换言之延迟主要只会体现在最后一次循环

2. **尽量写适合条件传送的代码**
   换句话说就是**三目运算符，因为操作本身是流水线化**的。
   比如下面这个例子：

   ```c
   1:
   for(i = 0; i < n; i++){
       if(a[i] > b[i]){
           long t = a[i];
           a[i] = b[i];
           b[i] = t;
       }
   }
   2:
   for(i = 0; i < n; i++){
       min = (a[i] < b[i]) ? a[i] : b[i];
       max = (b[i] < a[i]) ? a[i] : b[i];
       a[i] = min;
       b[i] = max;
   }
   ```

   后者的CPE远小于前者。。。

   但是这样做前提是你的**a/b计算式本身不产生副作用**/**计算并不复杂（因为他会把两个都算一遍）**

   #### 11 理解内存性能

   所有现代处理器都会包含一个高速缓存存储器，应对少量的快速访问。这里我们只考虑所有数据都放在高速缓存里面的情况（存储和加载）。

   ##### 1）加载的性能

   包含加载操作的程序性能显然会依赖于 加载单元的延迟 & 流水线的能力 
   一般情况下，加载和存储都是完全流水线化的（CPE = 1.00）
