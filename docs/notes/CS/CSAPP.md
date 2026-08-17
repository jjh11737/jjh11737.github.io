## 一、计算机系统漫游

### 1-1 程序的生命周期

一个程序生命周期为创建、编译、运行、退出

以GNU为例：编译包含**预处理**（Pre-Processor即**cpp**，看预处理指令，读取头文件的内容并直接插入源程序，得到另外一个c程序，再处理得到**.i**文本文件）、**编译**（Compiler即**cc1**，把C的语言翻译为汇编语言**.s**文件）、**汇编**（Assembler即**as**把.s翻译为机器码变成可重定位的**.o**文件）、**链接**（Linker用**ld**，把其他相关的.o比如我们调用了printf函数，那么printf.o[一个提前编译好的目标文件，来自标准库比如libc]连接到我们输出的.o文件，正是因为要对输出的.o文件进行调整，所以才叫可重定位文件）

![image-20260120235710612](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260120235710612.png)

### 1-2 操作系统的硬件结构

CPU里面最重要的就是**PC**，它存储下一条指令的地址，长度等于CPU的字长，比如64位那他就是8字节，其实就是寻址空间；其次是**寄存器**，高速读取的临时变量存储器；**ALU**用于与寄存器配合进行逻辑、算数运算；内存则是DRAM，你认为是一个大数组就行了，中间通过总线连接，那么为了处理IO我们就要有一个IO bridge

![image-20260121010550452](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121010550452.png)

> 比如以我们运行./hello这个可执行文件为例，键盘输入直接可以通过外部中断进入，通过总线进入寄存器，再搬运到我们的内存当中（因为数据量很小不用DMA），然后PC从内存当中加载指令，之后就是从硬盘之中加载hello这个可执行文件到内存当中，可以用DMA来传输，之后再加载到寄存器不断执行，最后输出到图形适配器上

### 1-3 存储结构层次、虚拟地址空间

然后是存储结构，越靠上寻址速度越快但是自然寻址内容就会越小

![image-20260121012020788](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121012020788.png)

操作系统本质就是应用与硬件之间的中间层，对底层进行抽象，具体来说，**文件是对一切IO外设的抽象，虚拟内存是对内存+IO设备的抽象，进程则是对包含处理器在内的一切资源的抽象**

![image-20260121012637542](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121012637542.png)

而具体来说我们以一个简单的**进程调用**为例，我们有一个shell的进程和一个hello的进程在并发，shell收到指令之后会通过system call调用把控制权移交给hello，此时就需要一次上下文切换（保存shell的上下文同时创建一个新的hello进程及其上下文），之后hello执行完毕又会恢复shell进程的上下文。而实际来说，一个进程往往需要由多个线程构成

> **<u>上下文</u>**本身就是记录进程的状态信息（快照），主要包含这个进程接下来执行所必须的信息：
>
> - A 寄存器状态 ：保存PC、栈指针、寄存器
> - B用户级状态  ：虚拟地址空间（代码段、数据段、堆、指针）、页表（虚拟地址到物理地址的映射关系）
> - C 内核级状态 ：进程控制块（PCB）、文件描述符表
>
> 它最终会被临时存储在内存里面，进程虚拟地址空间的顶部

**虚拟地址空间**，其实是由多级存储一起构成的，不仅仅是DRAM主存，而它通过页表把虚拟的地址映射到实际的地址当中，而且往往我们可以通过复用用更少的物理内存（RSS---Real Set Size）来让进程获得更大的（VSS--Virtual Set Size），对于不同的进程之间往往逻辑上这些虚拟内存本身是隔离的。

> 以一个64位的CPU为例，实际上往往只会使用48位来寻址，而<u>对每一个进程，它的虚拟地址空间都是2^48字节，也就是256TiB</u>（其中用户空间为2^47字节，约128TiB）！即使我们实际上可能加起来也就8GB，如果不够，一般主要就是复用或者用磁盘临时代替

![image-20260121024850465](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121024850465.png)

一个**经典的虚拟地址空间**，以64位为例是2^48个字节（256TiB），我们从底向上介绍：

- **Program start**，从0到这里我们必须要预留一个Zero Page（零页），我们目的是防止指针为Null时直接就访问我们的0地址，而是以此触发空页异常来捕捉空指针，同时有时候如果指针被作为一个结构体地址

  ```c
  struct User {
      int id;      // 偏移 0
      int age;     // 偏移 4
  };
  struct User *u = NULL;
  printf("%d", u->age); // 访问的是地址 4
  ```

  此时我们就得考虑这个偏移量来保证触发段错误从而捕捉空指针

- **Read-only code and data**，存储只读的代码和常量，

- **Read/Write data**，这里存储的是全局变量
- **Memory Allocate**(堆)，这里就是程序通过malloc分配的内存，他是向上增长的
- **Memory-mapped region for shared libraries**，存放的是共享库（标准库、数学库之类的），他也是向上增长的，位于堆与栈之间
- **User Stack**用户栈，进程可访问的最顶端，这就是我们调用函数时产生的，因为函数调用本质就是在压栈
- **Kernel Memory**最顶部是给内核用的，他就包含我们前面说的上下文等一系列内核需要的内容，不允许进程本身去访问它

**文件**就是字节序列，任何IO设备包括网络都可以视为文件，系统中的所有输入输出都是通过使用一小组称为 Unix I/O 的系统函数调用读写文件来实现的。它的作用就是让我们可以

### 1-4 重要主题（并发并行）

先介绍一下**Amdahl's Law**，他讲的就是我们对系统的某一部分进行加速时加速效果主要取决于我们**被加速部分的重要性**和**加速程度**。这个公式是显然的，a是加速重要度占比，k是加速的倍数，显然当k->无穷时，S=1/(1-a)，所以如果我们想把一个系统加速到一个较高的倍数，就必须要优化大部分的组件

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121030943466.png" alt="image-20260121030943466" style="zoom:33%;" align = left />

那么如果我们想要提高效率，主要有三种途径

- **线程级并发**  Thread-Level Concurrency
- **指令级并行**  Instruction-Level Parallelism
- **单指令多数据并行**  Single-Instruction Multiple-Data Parallelism

指令级并行则代表需要多个处理器并行同步处理，就像下面这个融合了哈弗架构与冯诺依曼架构的结构一样，L1分为数据和指令是为了让CPU处理起来不会出现结构冲突，而L2、L3因为原理处理器可以同时存储二者以提高泛化能力。

![image-20260121033421781](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121033421781.png)

而这就引入了另一个概念，也就是所谓的**超线程**，具体来说就是在单处理器内部的线程级别我们也引入一个并行的概念，因为时常会有一些资源是需要公用的（FPU之类的），往往就会配备多个PC、寄存器组之类的来同时为多个线程配置工作，就可以并发执行多个线程

![image-20260121035103471](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121035103471.png)

**单指令多数据（SIMD Single Instruction Multiple Data）**：一条指令产生多个数据操作，主要是为了提高视频、声音这类信号的处理速度



由此我们可以进一步抽象也就是所谓的**虚拟机是对整个计算机系统的抽象**

**<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121035348088.png" alt="image-20260121035348088" style="zoom:33%;" />**

**<u>抽象</u>**的要素，就是：

- **隔离 (Isolation)：** 让你觉得你独占了资源，不用担心被别人干扰。

- **映射 (Mapping)：** 你在“幻觉”里操作的资源，被一个透明的层转换成“现实”中的物理资源。

- **虚拟化 (Virtualization)：** 提供的资源可以超过物理上限（比如利用磁盘扩展内存，或者在 8 核 CPU 上跑 16 个虚拟机）。

## 二、信息的表示和处理

二进制的存储方法：**大端法**就是一个数字的**高位字节放在存储地址的低位**上，**小端法**反过来把**低位字节放在低位上**（也就是端是大的还是小的）

位移有两种，**逻辑位移**右移直接高位补0就行了，低位舍弃；而**算数位移**大体一样，但是<u>**右移时如果原本最高位为1，则最高位补1，如果原本最高位是0，右移最高位补0。（目的是保证符号性与数值不变）**</u>

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

原因很显然，<u>想要把一个大数据类型的数字转换为小数据类型的数字是不可能不改变值的(unsigned int -> int)</u>，但是反过来却是很轻松的

> 具体来说，如果一个unsigned char -> unsigned short，显然我们只要补0就行了，而对于有符号的char -> short，**如果最高位为1即负的则在前面补1，**因为这是很显然的，我们**只关注这个数字与1111 1111（-1）或 1111的差值**！！（当然实际上是要+1才能得到绝对值的，但是逻辑上没区别），当然用数学归纳法可以很轻松的证明（因为加一位是等价的）

### 加减法

而计算的时候也可能发生**溢出**，正溢出或者无符号直接减去2^w即可，负溢出加回去
对于无符号数，逆元与它的和就是2^w
对有符号数，一般不等于Tmin最小值就只要取相反数，但是Tmin也就是1000 0000是与其他不对称的(最大值的绝对值比最小值的绝对值差了1,一个是127,一个是-128)，这个就不能单纯取反，我们只能定义它等于它自身（-2^w + -2^w = -2(w+1) = 0）

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260123083817861.png" alt="image-20260123083817861" style="zoom:50%;" align = left /><img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs//image-20260123092531787.png" alt="image-20260123092531787" style="zoom:50%;"  align = left/>

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260123093624775.png" alt="image-20260123093624775" style="zoom:50%;" align= left/><img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs//image-20260123093541641.png" alt="image-20260123093541641" style="zoom:45%;" align=left/>

### 乘除

无符号的我们没啥好说的，主要是有符号的补码，特别地**<u>有符号和无符号最后截断得到的结果向量是一致的</u>**
（原因很显然，因为正的有符号数自然和无符号是一样的，而负的有符号我们就是减去2^w，结果显然是(a - 2^w) * b = a * b - b * 2^w，显然b是整数，那么与a * b是一样的，因为我们只不过要取模罢了）
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260123095157797.png" alt="image-20260123095157797" style="zoom:50%;" />

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125155701246.png" alt="补码的除法" style="zoom:50%;" align = left />

### 浮点数

定点数很简单，就是2的各次幂之和来表示，但是显然精度是固定的

因此我们考虑引入浮点数，IEEE 754的标准如下：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125161955650.png" alt="image-20260125161955650" style="zoom:50%;" align = left /> 













显然，我们只需要一个符号位`s`，阶数`exp`，以及剩下的小数字段`frac`即可表示，**精度低就用float** 32位（1符号8阶码23小数），**精度高就用double**（1符号11阶码52小数）
那么我们就可以知道显然这个**frac小数必须是在1～2之间**（阶数不能为0，但是要小于2否则就不是小数了），而且这是动态调整的，那么很显然**最高位一定是1，那就不用显式的表示**了

​	基本来说，f从高位到低位是2^-1, 2^-2....
而实际上浮点数分为3类：

- **<u>规格化(Normalized)</u>**：阶码不全为0或1
  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125164614541.png" alt="image-20260125164614541" style="zoom:67%;" />
  阶码e：1～255表示的不是真的阶数，真正阶数**<u>E = e - Bias</u>** 需要减去一个偏置量（取决于阶码位数[2^(el-1)]，float为[2^(8-1)-1]=127，double为[2^(11-1)-1]=1023），因此我们可知float范围就是[-126,127]
  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125172834651.png" alt="image-20260125172834651" style="zoom:45%;" align = middle />
  小数frac：就像前面说的，最高位永远是1,所以我们就省略这一位，**<u>M = f + 1</u>**
- **<u>非规格化(De-normalized)</u>**：阶码全为0
  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125164829781.png" alt="image-20260125164829781" style="zoom:67%;" />
  - 表示了0，e与f全为0。**<u>s=0为+0（正零），s=1为-0（负零）</u>**
  - 表示非常接近0的数，注意**<u>这里并没有一个被省略的1</u>**(显然)，以及**<u>E = 1-Bias</u>**，
  - 非常巧的是，这里非规格化的f如果向上溢出刚好就直接到e，刚好就是正常溢出的值
- **<u>特殊值(Special)</u>**：阶码全为1，分为2类，一种表示无穷大/无穷小，另一种表示不是一个数NaN
  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125164941328.png" alt="image-20260125164941328" style="zoom:67%;" />
  - Infinity：阶码全1，小数字段全为0，无穷大，**s=0为正无穷大，s=1为负无穷大**
    ![image-20260125174847806](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125174847806.png)
  - NaN：阶码全1，但小数字段非0，Not a Number
- 舍入：四舍六入五成双

> 举例环节：

为了方便我们用8位来代替之

- 首先是非规格化，那么E = 1 - bias，bias = 2^(4-1) - 1，因此E = -6，而小数就是直接的Frac = f * 2^(fl)
  fl代表f阶数

  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125175824320.png" alt="image-20260125175824320" style="zoom:50%;" /> 

- 然后是规格化：此时E = e - bias，bias = 7，frac = 1 + f * 2 ^ (-fl)。

  注意最大时我们只能去e = 1110,因为不能全1（特殊值）
  ![image-20260125180449344](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260125180449344.png)

### Data Lab

这个lab不算太难，不过尤其是浮点数需要多留意

易错点：

- isLessOrEqual：
  注意！！**<u>如果异号时相减会发生溢出</u>**！！此时不能用符号位
- 关于浮点数：
  - **<u>浮点数的frac部分溢出进位刚好就是到e，无缝衔接</u>**
  - **<u>比较正浮点数时可以直接用整数比较器，</u>**
    （这是因为指数在前，而且采用偏移量所以哪怕是负指数也还是满足这个排序！！）



## 三、汇编和机器

### 3.2 程序编码

1 机器级别编程采用了2个抽象：

- **ISA（Instruction Set Architecture）**，指令集架构，多数ISA包括X86-64都是好像描述成指令是顺序执行的，但是处理器硬件更多是并发地执行指令，但是可以保证整体行为和ISA指定的顺序是一致的
- **虚拟地址空间**，内存模型看起来就像一个巨大的数组

2 基本寄存器：

- **程序计数器PC**，在X86-64里面为%rip，给出下一条指令在内存的地址
- **整数**（通用寄存器，存储地址和整数数据）
- **条件码寄存器**，保存最近执行过的算术或逻辑指令的状态信息，用来实现控制/数据流的条件变化，比如if/while这些语句
- 一组**向量寄存器**，存放一个或多个整数/浮点数值

>```bash
>gcc -Og -o <prog_name> a.c b.c
> 	优化等级g			所有文件
>```
>
>-Og是告诉编译器生成符合原始C代码整体结构的机器码的优化等级，一般我们用-O1就行了，太高的优化等级会导致代码变形

#### 3.2.2 代码实例

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
 生成汇编文件p.s
```

这会使 GCC 运行编译器，产生一个汇编文件 mstore.s，但是不做其他进一步的工作。（通常情况下，它还会继续调用汇编器产生目标代码文件）。

汇编代码文件包含各种声明，包括下面几行：
（**<u>所有以.开头的指令都是指导计算机的，我们可以直接忽略</u>**）

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

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127170958252.png" alt="image-20260127170958252" style="zoom:53%;" />

我们先介绍两个概念：

##### **调用者保存寄存器 / 被调用者保存寄存器**

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127172049768.png" alt="image-20260127172049768" style="zoom:50%;" />

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

#### 3.2.3 数据格式

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127173646496.png" alt="image-20260127173646496" style="zoom:50%;" />

word在x86中表示16位，32位称为双字（double word），64位称为四字（quad word）

> 比如**数据移动（Data Movement Instructions）**：
> movb -> Move byte（1字节）；
> movw -> Move word（2字节）；
> movl -> Move double word（4字节）；
> movq -> Move quad word（8字节）；



### 3.3 寄存器

#### 3.3.1 基本寄存器

16个整数寄存器，他们本身是规定好具体的功能的
注意这里关于参数只有6个寄存器，如果传递参数>6则需要压栈而会严重拖慢速度，所以一般限制在6个参数以内

![image-20260127181423992](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127181423992.png)

#### 3.3.2 Instruction指令

而实际上**<u>指令</u>**一般都是由**操作码（operation code）**和**操作数（operation num）**组成的。操作数有3种：**<u>立即数/寄存器/内存引用</u>**

```assembly
Opration code 				Operands
movq						(%rdi), %rax
addq						$8, %rsx
subq						%rdi, %rax
xorq
```

![image-20260127214912909](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260127214912909.png)

##### Memory Reference

一个内存引用由 ` Imm(立即数)`，`rb(基址寄存器)`，` ri(Index Register)`，`s(scale)`，地址：
$$
Imm(rb, ri, s) = Imm + rb + ri *s.
$$
其中s = 1, 2, 4, 8，s实际就是所谓的步长（数据长度）

##### `MOV`指令：

他有两个操作数，`Source`和`Dest`，其中

- `Source`可以为立即数/内存引用/寄存器	（一个值，待移动）
- `Dest`可以为内存引用/寄存器          （因为它就是我们`Source`要移动到的地方）
- `Source`和`Dest`**<u>不可同时为内存引用</u>**（防止太慢）
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
  而如果立即数是一个64位的，我们就需要用另一条指令movabsq（**<u>它针对源是一个64位立即数时</u>**）

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

  注意，只有**<u>movl会把目标寄存器的高32位清空</u>**（x86-64规定，为了兼容32位操作）

  ------

- 源操作数位数 < 目标操作数位数，需要用**<u>零扩展</u>**或**<u>符号扩展</u>**

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

> > **练习3.4 强制类型转换**
>
> ```c
> src_t	*sp;
> dest_t	*dp;
> 返回：
>     *dp = (dest_t) *sp;
> 思路很简单，我们就是先从参数1寄存器放入
> ```
>
> ```assembly
> src_t			dest_t			code
> long 			long			movq	(%rdi),	%rax		#param1 -> ret
> 								movq	%rax,	(%rsi)		#ret -> param2
> char			int				movsbl	(%rdi), %eax		#保留符号
> 								movl	%eax, 	(%rsi)		#movl自动清零高32位
> char 			unsigned		movzbl	(%rdi), %eax
> 								movl	%eax, 	(%rsi)
> unsigned char	long			movzbl	(%rdi), %eax		#movl自动补0
> 								movl	%eax, 	(%rsi)
> int				char			movl	(%rdi),	%rax
> 								movb	%al,	(%rsi)
> unsigned		unsigned char	movl	(%rdi), %eax
> 								movb	%al,	(%rsi)		#直接截断即可
> char 			short			movsbw	(%rdi), %ax
> 								movb	%ax,	(%rsi)
> ```
>

注意事项：

- **<u>大转小</u>**不用movz/movs，直接mov即可
- 以及一般的**mov指令必须要求前后寄存器长度是一致的**！
- `movl` / `movzbl`都是会**自动高位清零**的（特别注意byte需要先补0）
- **CPU同时拉伸数据长度和写入内存是不可能完成的**！可以善用MOVL自动清高位性质

- 注意！X86-64是小端的！我们从地址开始取的是低位！因此如果原本数据是int(l)，要转换为char(b)，我们直接movb即可，movb意思就是从地址开始抓

### 3.4 栈/数据传输

#### 数据传输

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

- **<u>局部变量一般是保存在寄存器里面的</u>**，而非内存
- 指针就是地址，间接引用指针就是把指针放到寄存器作为内存引用

>**习题 3.5**：把汇编代码翻译回C
>
>```c
>void d1(long *xp, long *yp, long *zp){
>    long x = *xp, y = *yp, z = *zp;
>    long *tp1 = &x, *tp2 = &y, *tp3 = &z;
>    *xp = *tp2;
>    *yp = *tp3;
>    *zp = *tp1;
>}
>```
>

汇编翻译回C是有豁免的，你不用管什么那个变量先后定义，<u>只要逻辑功能是一样的汇编代码理想上就是一样的</u>

#### 栈

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
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128204648432.png" alt="image-20260128204648432" style="zoom:50%;" />



### 3.5 算术和逻辑运算指令

整体来说，整数运算命令有以下几个：![image-20260128204923391](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128204923391.png)

- 除了leaq(毕竟地址长度就是q64)其他指令都有不同的长度变种。
- 操作分为4组：加载有效地址 / 一元运算 / 二元运算 / 移位

#### ` leaq`指令

他的功能其实就是`movq`的变形，但是不同的是他是直接把一个有效地址写入目的操作数。
特别需要注意的是，**<u>地址运算本身其实可以实现简单的算术操作</u>**。
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

> **常数乘法优化**（）
> 比如153 x = (10011001) x = (x << 7 + x << 4) + (x << 3 + x)
> 		  = y << 4 + y
> 从这里也可以看出，我们的次数是与1的个数有关的，怎么简化？
>
> ->可以转换为**正则有符号数编码CSD**：
> 也就是把连续的1转换为<u>溢出一位</u>和<u>1位补码</u>代替（相当于-）
> 比如`11 1100 1110 1111`就可以转换为<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128224655226.png" alt="image-20260128224655226" style="zoom:60%;" />，从低位扫描：
> <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128224747919.png" alt="image-20260128224747919" style="zoom:50%;" />
> 就转化为了 x<<14 - x<<10 +x<<8 -x<<4 -x

----



#### 一元操作

| Instruction | Effect        |
| ----------- | ------------- |
| INC D       | D++    自增   |
| DEC D       | D--      自减 |
| NEG D       | -D       取负 |
| NOT D       | ~D      取反  |

一元操作只关心这个地址的值

#### 二元操作

| Instruction | Effect                              |
| ----------- | ----------------------------------- |
| ADD S, D    | D <-  D+S  加                       |
| SUB S, D    | D <-  D-S   减                      |
| IMUL S, D   | D <-  D*S   乘<u>**(注意顺序**</u>) |
| XOR S, D    | D <-  D^S   异或                    |
| OR X, D     | D <-  D\|S   或                     |
| AND S, D    | D <-  D&S  与                       |

这里S就是源，类型不限；但是D既是源又是目的，所以不能是立即数

**习题3.8**：
![image-20260128225733986](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260128225733986.png)

| 指令 | 目的 | 执行后该处的值 |
| --- | --- | --- |
| `addq %rcx, (%rax)` | `0x100` | `0xFF + 0x1 = 0x100` |
| `subq %rdx, 8(%rax)` | `0x108` | `0xAB - 0x3 = 0xA8` |
| `imulq $16, (%rax,%rdx,8)` | `0x118` | `0x31 * 16 = 0x310` |
| `incq 16(%rax)` | `0x110` | `0x14 + 1 = 0x15` |
| `decq %rcx` | `%rcx` | `0x1 - 1 = 0x0` |
| `subq %rdx, %rax` | `%rax` | `0x100 - 0x3 = 0xFD` |

注意：

- (%reg)在这里是一个地址，我们相加的是地址指向的值
- 地址是16进制！！！`0x108` + `0x8` = `0x110`

#### 位移操作

| Instruction | Effect                         |
| ----------- | ------------------------------ |
| SAL k, D    | D <- (D<<k)算术左移            |
| SHL k, D    | D <- (D<<k)逻辑左移（与SAL等价 |
| SAR k, D    | D <- (D>>ak) 算术右移          |
| SHR k, D    | D <- (D>>lk) 逻辑右移          |

特别的，**<u>k只能是 移位寄存器`%cl`/ 立即数！</u>**
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

#### 特殊算术操作

下面是针对`八字(oct word)`描述的运算符

| Instruction | Description  |
| :---------: | :----------: |
|   imulq S   | 有符号全乘法 |
|   mulq S    | 无符号全乘法 |
|    cqto     |  转换为8字   |
|    idivq    |  有符号除法  |
|    divq     |  无符号除法  |

一般来说`mulq` / `imulq`本来是作为2操作数的，此时结果也是4字64位的

##### 128位乘法：

而主要问题是我们乘法如果是两个64位，为了不丢失精度，结果应该是**<u>128位</u>**的。
因此`mulq`/`imulq`采用了`%rax`作为第64位，`%rdx`作为高64位，二者构成寄存器对。此时这两个指令只有一个操作数`%reg`，等价于: **<u>（这两条指令一个数字必定在%rax，另一个作为S给出）</u>**
`%rdx(高)`|`rax(低)` <- `%reg` * `%rax`
**e.g.**

```c
 include <inttypes.h>
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

##### 除法 / 取模

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
	movq	%rdx,	%r8		;copy qp
	movq	%rdi,	%rax	;x -> lower 8 bytes of dividend
	cqto					;sign-extend to upper 8 bytes of dividend
	idivq	%rsi			;有符号除法：rdx:rax / y
	movq	%rax,	(%r8)	;商在rax,保存到%r8存好的*qp地址
	movq	%rdx,	(%rcx)	;余数
	ret
```

但是实际应用的时候我们不太会碰到这种现象，因为正常都是结果是long * long = long。只有在高精度计算和安全检查时才会使用

**习题 3.12**





### 3.6 控制流

#### 3.6.1 条件码寄存器

##### 条件码寄存器：

是一组单位寄存器，用于描述最近一条算数或逻辑操作的属性，可以检测这些寄存器来执行条件分支指令

- **CF**：进位标志，最近的操作触发了一次进位，可用于检查无符号溢出
- **ZF**：零标志。最近操作结果为0
- **SF**：符号标志位。最近结果为负数
- **OF**：溢出标志位。最近出现了一个补码溢出（正 / 负溢出）

除了`leaq`之外其他我们说过的那些3.5的指令都会设置条件码。

##### 算术/逻辑操作的影响：

- XOR会自动把溢出/进位标志位置零
- 移位时进位标志将会被设置为最后一个被移出的位，溢出标志为0
- INC/DEC会设置溢出和零标志，但是不会影响进位标志位（这是因为我们要方便处理循环，因为INC往往就是用于循环，如果循环时触发进位那就会影像我们内部的运算，比如一个256位的加法

##### 专门设置条件码的寄存器：

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

#### 3.6.2 访问条件码

条件码一般不会需要直接读取，常见使用方法：

1. **<u>根据条件码的某种组合，把一个字节设置为0/1</u>**

2. **<u>条件跳转到程序的某个部分</u>**

3. **<u>有条件地传递数据</u>**

#### 3.6.1 `SET` 指令

针对的是情况1，这组指令的区别就是他们考虑的条件码组合是什么，不同的后缀指明了它们所考虑的条件码组合。
功能：一条`SET`指令的目的操作数是一个**<u>低位单字节</u>**寄存器元素 / 一字节内存，指令会读取状态寄存器把这个这个字节设置为0 / 1

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



#### 3.6.4 条件指令

##### 条件跳转

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

##### 条件传送

![image-20260210140743091](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260210140743091.png)



注意，**<u>基于条件传送的指令往往比基于条件跳转的指令效率要高！！</u>**

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

这是因为**<u>条件跳转指令需要处理器去预测各分支的结果，但是条件传送不需要</u>**，因为这涉及流水线，CPU不会等一条指令跑完再下一条，而是把指令分为多个阶段提前处理，因此碰到跳转时CPU不清楚是要执行跳转还是非跳转的代码，因此会猜测一个方向提前处理，但如果猜错这个方向的提前处理就必须放弃，需要整个回滚。而**<u>条件传送就是把两个方向需要的计算都算好根据条件搬运数据，流水线始终是满载的，不会出问题</u>**

##### 循环

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
	movl $1, %eax
	.L1:
		imulq %rdi, %rax
		decq %rdi
		cmpq $1, %rdi
		jg	.L1
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

**<u>关于编译器优化：</u>**

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

##### switch语句

通过整数索引值实现多条分支，通过跳转表实现，事实上无论switch有多少种选项，**<u>只要执行一次跳转指令就可以处理复杂分支跳转情况</u>**，因此它比一堆if-else要高效。
跳转表是一个数组，i是一个代码段的地址，代码段就是开关索引值等于i时采取的操作，

下面给出一个程序，它的汇编代码实际功能和右边的C代码一致：
![image-20260213162521123](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213162521123.png)
这里的`&&`符号是GCC作者创建的一个指向代码位置的运算符，相当于直接变成一张表，0～6，缺省的我们直接替换为default，下面是汇编代码：
![image-20260213162658729](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213162658729.png)

这里的`*`是间接跳转的意思，也就是告诉程序去`.L4 + 8 * %rsi`的位置，8是因为这里地址数是8字节的（64位），
跳转表如下：
![image-20260213164206566](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213164206566.png)
它告诉我们在`.rodata`（只读数据区)里面会有下面这张表，`.quad`告诉要预留长度8字节的空间放地址

我们可以总结一下，一般来说就是<u>几个常规的情况对应标号，一个作为default，另一个作为跳出switch的标号</u>

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

### 3.7 过程

过程是一种抽象，它提供一种封装代码的方法，用一组指定的参数和返回值实现功能，以供别处调用。过程的形式多样：函数(function)/方法(method)/子例程(subroutine)/ 处理函数(handler)等等

#### 3.7.1 运行时栈

一旦有一个过程需要的空间超过寄存器的大小，就需要在栈(stack)上面分配空间，称为**栈帧（stack fram）**<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260213171705960.png" alt="image-20260213171705960" style="zoom:67%;" align = "left" />.前面说过栈是从高地址向下增长的，栈指针`%rsp`指向栈顶元素。
比如P调用Q时，会把返回地址压入栈中，指明当Q返回的时候要从哪里继续执行，他是P的一部分

















#### 3.7.2 转移控制

##### 返回地址

将控制从函数 P 转移到函数 Q 只需要简单地<u>把程序计数器(PC)设置为 Q 的代码的起始位置。</u>
但是显然从Q返回时需要知道继续执行P代码的位置，在x86架构里面这是通过<u>call Q调用来记录的</u>，他会把<u>地址A(P的返回地址)</u>压栈，同时把PC设置为Q的起始位置，而`ret`的时候会把PC重新设为A.（从栈顶`%rsp`弹出，写入指令寄存器`rip`，也就是x86-64里面对应的PC寄存器）
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



##### 参数传递

**传递寄存器顺序：**
![image-20260302082904636](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302082904636.png)
就像前面说的，`%rdi`,`rsi`,`rdx`,`rcx`,`r8`,`r9`

**压栈**

一旦参数超过6个就会需要通过栈，**<u>而在栈当中每个参数的地址就需要按8字节对齐，无论其长度多少</u>**
先把1~6号传递到寄存器，然后把剩下的放到寄存器里面（参数7在栈顶），这部分就是所谓的**<u>“参数构造区”</u>**，它属于调用者A的栈帧，但是也可以被所调用者B使用（只要movq 8(%rsp), %rax就能访问参数7，因为他就在这个位置)，等B完成后返回此时A会把栈顶指针加上长度把这部分内容丢弃

另一个规则是，**<u>在 call 指令执行前，x86-64 要求 %rsp 的地址是 16 的倍数！！！</u>**（call 会压入 8 字节返回地址，因此被调函数入口处 %rsp 是 8 mod 16；有时候会额外 `subq $8, %rsp` 来凑对齐）。

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

#### 3.7.4 栈上局部存储

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

### 栈上的访问：

**<u>x86-64数据永远是小端的</u>**，也就是低位数据存储在更低的地址，而且**<u>数据的地址就是最低那位的地址</u>**，读取数据时是**<u>从低位往高位读取</u>**

call指令会自动加8字节，这个内容放的就是%rsp之后的返回地址

----

#### 3.7.5 寄存器上的局部存储

我们必须保证寄存器活动时被调用者不会覆盖调用者的寄存器，因此有惯例的。

**<u>`%rbx`,`rbp`，`r12`~`r15`为被调用者保存寄存器</u>**，当P调用Q时，Q必须保证这些寄存器不被改变。
显然想要不改变要么不动要么就把他们压栈。因此只需要P提前把内容放入这几个寄存器就可以保证不被影响

**<u>其他的所有寄存器都被划分为调用者保存寄存器（栈指针 %rsp 除外，被调用者返回前必须把它恢复原样）</u>**，这表明任何过程都可以改变它们，**保证它们没问题是P的责任**（所以为“调用者保存”）

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

#### 3.7.6 递归过程

前面的规则已经保证递归可以自然执行

### 3.8 数组分配

比如一个数组E，它的起始地址放在`rdx`里面，i放在`rcx`里面，若他是int类型，那么直接：

```c
movl	(%rdx, %rcx, 4), %eax
```

#### 3.8.2 指针运算

C对指针的运算是根据指针引用的数据类型的大小伸缩的，比如`p + i`实际上等于`xp + L * i`（L是数据的字节数），同时A[i]等价于*(A + i)

#### 3.8.3 嵌套数组

`&A[i][j] = (Xa + L * (i * C + j))`，

#### 3.8.4 定长数组

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

#### 3.8.5 变长数组

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





### 3.9 异质数据结构

#### 3.9.1 struct

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

#### 3.9.2 union

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



#### 3.9.3 数据对齐

**对齐原则**就是**任何K字节大小的基本对象**的**<u>地址必须是K的倍数</u>**

![image-20260302111937701](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302111937701.png)
而一旦有对不起的情况，编译器就会自动预留空间给它补齐

比如在**结构体**里面，要有两条规则：

- **<u>成员对齐</u>**（内部偏移量）：每个成员的起始地址只要求是它自身长度的整倍数
  ![image-20260302113256646](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302113256646.png)
- **<u>整体对齐</u>**（末尾填充）：每个结构体的总大小必须是它里面最长那个元素长度的整倍数
  ![image-20260302113249181](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302113249181.png)

**<u>因此声明结构体的时候我们往往把短的放到后面，减少偏移量带来的问题</u>**

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

### 3.10 内存越界与缓冲区溢出

![image-20260302141936234](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302141936234.png)

#### 3.10.3 内存越界/缓冲区溢出

C对数组引用的边界不会进行任何检查，局部变量与状态都放在栈里面，那么数组越界的写会破坏栈里面的状态信息，此时ret就会碰到问题。

下面是一个很经典的例子：
![image-20260302142514533](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302142514533.png)
GCC给出汇编代码如下：
![image-20260302142803912](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302142803912.png)

显然我们可以使用的只有16字节，一旦超限，它就会进入调用者的返回地址，会让rsp跳转到不知道的地方：
![image-20260302142930215](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302142930215.png)
同时缓冲区溢出更大的问题是他会让程序执行它本来不想执行的函数，通常我们输入一个字符串，它包含一些可执行程序的字节编码(exploit code)，另外还有一些字节会用一个指向攻击代码的指针覆盖返回地址，那么ret时就会跳转过去。因此任何对外的接口都必须做好保护。

#### 3.10.4 对抗缓冲区溢出

##### 1.栈随机化

让栈的位置在每次运行时都会变化，实现的方法是程序开始前在栈上面分配一段随机大小的空间，不使用它。
在linux里面这已经成为标准行为，它属于**<u>地址空间布局随机化（ASLR）</u>**，它使得运行时程序的不同部分（代码/库代码/栈/全局变量/堆等）会被加载到内存的不同区域。

但是显然这会被穷举破解，比如用一堆nop指令序列，它的作用就是让PC++，指向下一指令，只要能猜中这段序列中的某个地址就能跳转到想要的地址

##### 2. 栈破坏检测（金丝雀）

在缓冲区与栈状态内容间加入一个金丝雀的随机值，一旦发生改变就可以停止。
![image-20260302145117808](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302145117808.png)

我们先从内存读出一个随机值，把他存入%rsp偏移8的位置，`%fs:40`表示它使用段寻址（原本指的是一个附加寄存器fs，现在已经没有了，它就是一个指针，被放在每个线程的本地存储TLS里面）把这个值放到一个只读段里面放置更改。

##### 3. 限制可执行代码区域

即限制哪些内存区域能够存放可执行代码，其余部分只允许读写。
虚拟内存本身就是分页的，2048/4096字节，操作包含读/写/执行。

但是显然这是不安全的，AMD引入了NX（No-execute）位，区分了读和执行访问模式。栈此时只能读写，不可执行

#### 3.10.5 支持变长栈帧

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

显然，如果栈帧本身是动态长度的，我们就不可以直接通过rsp找到返回地址以及各种<u>局部变量（这是主因，因为生成汇编代码时**我们不知道局部变量相对于rsp的偏移，也就无法生成高效的代码**）</u>，为了管理变长的栈帧，x86-64使用**`%rbp`寄存器**作为<font color="red">**<u>帧指针（frame/base pointer）</u>**</font>，这也是为什么叫bp。
它的作用就是作为一个固定的地址指针，时刻指向当前栈帧的底部，之后rsp无论怎么动我们都可**<u>直接通过rbp找回局部变量的位置</u>**（他们一般都是挨着rbp的，而变长数组会靠近栈顶指针rsp）。

那么再来解释一下上面这个代码的几个地方，先压栈保存rbp，然后把rbp变成当前栈顶指针rsp的位置作为之后的栈底（返回地址则是rbp+8处），之后先分配给i空间，我们知道**<u>调用 call 前 %rsp 必须是 16 的倍数</u>**，之前push q导致现在地址是16n+8，而int是8,现在应该是16的倍数，但是call本身又会+8,为了保证之后调用其他函数不出问题我们这里才先额外分配个8字节。之后先把rax变成22 + 8 * n（**<u>这里的22= 23 = 8 + 15 - 1，8给的是金丝雀，15是为了刚好向上取整，最关键的是这个1,因为事实上一个8的倍数加上22或23再去掉低16位是等价的！！</u>**），再通过地址掩码（16 = 0x0001 0000,-16就是取反加一0x1111 0000，**清空了低4位**)，这就相当于向上取整保证了结果是16的倍数，这么做还是保证rsp的16倍问题。



---

**向上取整公式**（2的次方）：(x + ALIGN - 1) & ALIGN

**<u>rsp</u>**必须保证是**<u>16n - 8</u>**（除了call后那一段）

**leave**是专门用于变长栈帧的指令，它把rsp恢复为rbp的位置，rbp再从栈里面弹出上一个rbp的位置，之后ret时rsp直接就是可以执行跳转

同时我们发现**循环里面计数变量自增时一般用add 1而不是INC指令**，这是因为INC不会修改CF,这样流水线时会影响速度，因为必须计算完前面的才可以，而且inc前面需要一个前缀，并不简洁

----



### 3.11 浮点代码

Pentium和MMX出现使得AMD/Intel都引入了媒体指令以支持图像处理，本意是让多个操作以并行的方式执行，称为**单指令多数据(SIMD)**，它允许对多个数据进行同一个操作，之后从MMX到SSE（streaming SIMD Extension,流式SIMD扩展），以及最新的AVX（Advanced Vector EX）。SSE2的媒体指令开始包括对标量浮点数的操作指令，提供了一组专门的寄存器和指令。

接下来讲的是基于AVX2的。命令行参数给定-mavx2时GCC就会生成AVX2代码，使用ATT格式表述。

如下图所示，AVX浮点体系结构允许数据存储于16个YMM寄存器中，他们的名字是`%ymm0`~`%ymm15`，每个YMM是256位也就是32字节。当对标量数据（单个数据）操作时，这些寄存器只保存浮点数，而且只使用低32位(float)或64位(double)，汇编代码把他们称为`%xmm0`~`%xmm15`，也就是ymm的低128位（16字节）

![image-20260302211958287](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302211958287.png)

#### 3.11.1 浮点传送和转换

1. 下面是浮点数传送的代码，引用内存的指令是标量指令，意味着只能对单个而不是一组封装好的数据操作。数据只可能在内存或者其他的XMM寄存器（X）当中。这些指令不要求内存对齐，不过一般还是建议64位8字节对齐好，<u>内存的引用方式（间接寻址）和整数的MOV是一样的</u>。
   ![image-20260302213250194](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302213250194.png)
   GCC只用标量传送操作从内存传递数据到XMM或XMM传递到内存，而如果在XMM之间传送则会使用最后的向量传送也就是`vmovaps`（单精度)和`vmovapd`（双精度)。这里的'a'表示aligned也就是对齐的，他们必须保证是满足16字节对齐的，换言之这两条指令如果被用于内存时也要求这一点

   比如下面这个例子：

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260302213919934.png" alt="image-20260302213919934" style="zoom: 77%;" />

```assembly
 v1 in %xmm0, src in %rdi, dst in %rsi
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

具体来说，**<u>“向0舍入”意思就是直接把小数点丢弃</u>**，因为浮点数是1.f * 2^E，显然就是对f位移罢了。
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
      意义其实是为了**<u>避免伪依赖</u>**，因为`vcvtss2sd`只操作寄存器的低位，很容易让CPU认为高位是需要保留的，换句话说它必须做完所有对此寄存器的操作后才运行这条指令执行，而这么交叉一下（就很像寄存器先自己异或一下自己一样，**<u>告诉CPU这个寄存器过去的值对我无所谓</u>**）

      2）双精度转单精度也是差不多的：

      ```assembly
      vmovddup	%xmm0, %xmm0		;duplicate lower bits
      vcvtpd2psx	%xmm0, %xmm0		;
      ```

      `vmovddup`(duplicat)，先<u>把寄存器的低位扩展，</u>[x1, x0] -> [x0, x0]，同样是告诉CPU高位我不在乎（方便流水），之后`vcvtpd2psx`功能则是把两个double转换为两个float放到低位，高位清零
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
   	vmovsd	%xmm1, (%rdx)
   	vunpcklps	%xmm0, %xmm0, %xmm0	;交叉数据，告诉CPU抛弃过去
       vcvtps2pd	%xmm0, %xmm0		;扩展float->double
       ret
   ```

#### 3.11.2 过程中的浮点

和原来差不多：

- %xmm0 ～7可以传递8个浮点参数，多的压栈
- 用%xmm0返回浮点值
- %xmm所有都是调用者保存的，对所有被调用者它们都是全新的

同时指针和整数还是属于通用寄存器的

#### 3.11.3 浮点运算

AVX2的简单的标量浮点运算指令：（注意**<u>S1寄存器和内存都可以，S2/D必须是XMM寄存器）</u>**![1](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303103245077.png)
比如一个简单的函数：
![image-20260303103554924](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303103554924.png)

```assembly
 a in %xmm0, x in %xmm1, b in %xmm2, i in %edi
funct:
	vunpcklps	%xmm1, %xmm1, %xmm1		
	vcvtps2pd	%xmm1, %xmm1
	vmulsd	%xmm1, %xmm0
	vcvtsi2sd	%edi, %xmm1, %xmm1
	vdivsd	%xmm1, %xmm2, %xmm2
	vsubsd	%xmm2, %xmm0, %xmm0
	ret
```

#### 3.11.4 浮点常数

编译器对浮点数是没法用随机数的，那么只能在内存里面为常量分配和初始化对应的存储空间：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303104535650.png" alt="image-20260303104535650" style="zoom:67%;" />

#### 3.11.5 浮点代码的位操作

这里注意，这些位操作是针对整个XMM寄存器的所有位
![image-20260303104827697](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303104827697.png)

#### 3.11.6 浮点比较操作

AVX这俩和COMP基本上相似的，也是S2 - S1
![image-20260303105110804](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303105110804.png)
比较3个条件码，零标志位`ZF`，进位标志位`CF`和奇偶`PF`（寄存器和前面的算是共用的)。
前面没讲奇偶是因为他不太常见（一般就是整数如果是偶校验也就是偶数个1触发)
而**<u>对于浮点数则是只要S1/S2有一个是NaN就触发奇偶`pf`</u>**
具体规则如下了：
![image-20260303105616333](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303105616333.png)

**<u>条件跳转</u>**：

- 通常来说，只要一个是`NaN`就是无序，此时通过`jp(jump on parity)`就可以在无序时跳转
- 大于是`ja`，小于`jb`，等于`je`

比如：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260303110007319.png" alt="image-20260303110007319" style="zoom:67%;" />

```assembly
  x in %xmm0
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

<u>**GCC喜欢在每一个条件跳转前面先比较一次**</u>





### Bomb Lab

gdb:

先 break <func_name>在函数前面打断点再run

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

整体来说不算太麻烦，花点时间基本上都能搞定







## 四、处理器体系结构

### 4.1 指令集

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

#### 异常

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











## 五、优化程序性能

### 1、最安全的优化

GCC比如-O1的优化等级，他会**主动预设出现最差的情况**，进行最安全的优化

> 譬如如果出现两个指针引用，它就会默认会出现两个指针相同的情况，
>
> 同时函数调用如果不知道其副作用，它就会预设调用本身是有用的。 

### 2、内联函数：

编译器会**把函数调用替代为函数内容本身展开黏贴**，之后再考虑优化

> （譬如预测函数的副作用，再以更简单的方法替换）

### 3、描述程序性能：

通过时钟周期来描述

### 4、消除循环带来的低效率：

- 显然每次循环都会需要对**测试条件**本身进行求值，所以你最好把它固定下来（虽然理想情况是他可以识别出来）
- for的初值无所谓，但是判断条件以及循环尾很重要
- 一般来说只要确定次数且次数不大其实倒是会**循环展开**
- **<u>总之：**你**一定要让边界尽可能在循环前明确</u>**

### 5、减少过程调用：

比如这个代码：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260316064320200.png" alt="image-20260316064320200" style="zoom:67%;" />
我们这里把这个调用函数获取内容的代码替换成直接通过数组的形式访问，事实上向量本身就是通过数组而非链表的形式存在的
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260316064525731.png" alt="image-20260316064525731" style="zoom:67%;" />
但是奇怪的是这并没有引入多少性能提升，这说明我们的内循环里面存在其他瓶颈

### 6、消除**非必要的内存引用**：

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260316065318624.png" alt="image-20260316065318624" style="zoom:50%;" />
（上面这个代码每次就是在累乘，但是每次偏偏都要读写内存。显然上一次的rbx存的就是这一次从内存读出来的，完全没必要先读出来再放回去。）
我们可以优化这个问题，这个问题本质是因为使用的是这个dest，它本身是指向内存的，但是如果你**使用一个临时变量acc来积累这个过程，那寄存器就可以处理了**（换句话说如果你不需要一个全局的值来存储它，**用局部变量完全更快**）
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260316070124016.png" alt="image-20260316070124016" style="zoom:50%;" />

### 7、现代处理器：

由于指令级并行以及分支结构的流水线冒险，性能大大提高。但是如果指令本身有严格的先后依赖关系，指令本身会产生**延迟界限**：即**<u>下一条指令开始之前这条指令必须先结束</u>**

**<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260324091636618.png" alt="image-20260324091636618" style="zoom:50%;" />**

#### 1）**超标量处理器**

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

而在ICU里面，**退役单元**用来记录正在进行的处理，保证它们遵守机器级程序的顺序语义，，换句话说其实就是控制寄存器的更新（包括通用、浮点、SSE/AVX）。具体来说，指令译码时相关信息就会被放在一个FIFO队列里面，直到<u>(1)指令完成且分支预测正确->退役，相关对程序寄存器的更新可以被提交执行</u>/(2)<u>指令完成但是分支预测错误->清空指令，丢弃所有结果</u>。

那么很显然，**任何对程序寄存器的更新只发生在指令退役时刻**。

而另一方面，为了加速一条指令到另一条指令的传送以及提交，采用了**寄存器重命名**（就是一个映射表），这样执行单元就可以直接把结果发送给对方了。（这本身也解耦了物理寄存器和我们抽象的程序寄存器，保证可以乱序执行不会冲突）
具体来说，当一条更新寄存器r的指令被译码后，就会有产生一个对操作本身的标记t，得到一个指向该操作结果的唯一标识符(r,t)，这个条目被放入映射表（维护每个寄存器r与更新该寄存器的操作的标记t），随后发送到操作单元时就会包含t作为操作数源的值。而当某个执行单元完成第一个操作时，就会生成结果$(v,t)$，说明操作t会产生v的值，此时所有等待t作为操作源的操作便都可以以v作为源值，这就是一种形式的数据转发（事实上这个过程是<u>EU直接把值存入一个物理寄存器，然后广播这个寄存器和标识符</u>），这样就不必等这个指令退役才开始执行下一个等待资源的操作，保证了乱序和分支预测的执行

#### 2）功能单元的性能

我们用三个指标来刻画运算的性能：**延迟**---运算本身需要的时间、**发射**时间---两个连续同类型运算间需要的时钟周期、**容量**---能够执行该运算的数目
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260325170828116.png" alt="image-20260325170828116" style="zoom:67%;" />
我们发现加法与乘法远远快于除法（所以编译器一般会把常数除法直接替换为乘法+移位），整数快于浮点数。
而且更重要的是乘法与加法发射时间都为1，这代表<u>每个时钟周期都可以开始执行一个新的运算</u>。这是通过**流水线**实现的，**<u>流水线化的功能单元实现为一系列的阶段，每个阶段完成一部分运算</u>**（比如浮点加法包含3个阶段：处理指数值、小数相加、结果舍入）。算数运算可以连续地通过各个阶段，不用等待一个操作完成后再开始下一个，当然前提是要执行的运算是连续的且相互独立。**发射时间为1代表这个功能完全流水线化**。

而**除法器显然是不完全流水线化的，**而且**发射时间等于延迟，说明开始新的运算之前必须完成整个除法**（这是显然的，因为除法器他其实就是一个迭代减法器（暂时不说SRT算法），算完上一位余数才知道下一位要不要减）。

表示发射时间的另一个指标是**最大吞吐量**，即**容量除以发射周期**。比如图中加法吞吐量就是4，单周期可以处理4个新的加法

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260325173833559.png" alt="image-20260325173833559" style="zoom:50%;" />

这里加法器是被加载单元限制了，每个周期只能读取2个数据，而乘法器因为延迟为3个周期，没有受到影响

#### 3）处理器操作的抽象模型--数据流

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

### 8 循环展开

主要就是可以减少不直接操作有助于程序结果的操作数量，同时也可以减少整个计算中关键路径上面的操作数量。还是那个程序，就是求向量累乘的，以下是采用"2*1循环展开"的版本。
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260401171807288.png" alt="image-20260401171807288" style="zoom:50%;" />
我们不能保证输入向量是2的整倍数，所以我们设置上限为n-1，最后来个循环来处理尾部单个数字。
以此类推，如果是$k * 1$的因子，那么上线就得是$ n - (k - 1)$，之后再处理尾部，它最多执行$k-1$次。

显然，这样展开后CPE会变小一些，主要是减少了整数加法的次数，但是其他情况并没有性能提高，因为已经达到了EU的延迟界限
![image-20260401172443843](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260401172443843.png)
而-O3一般编译器就可以自动进行循环展开了

### 9 提高并行性----打破依赖链

我们以上的写法还是存在问题，因为加法和乘法本身的EU在这里已经是完全流水线化的，换句话说每个时钟周期可以开始一个新操作，而且操作本身可以被多个功能单元执行，但这里代码却不能利用这种能力，因为我们把累积值全部放到了一个单独的变量`acc`里面，前面的计算完成之前都不能计算新的`acc`，我们要做的就是打破这种顺序相关。

#### 1） 多个累积变量

如果一个合并运算本身是可交换可结合的，那么就可以把这个运算本身分解为多个部分，最后整体合并来提高性能
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260401173949423.png" alt="image-20260401173949423" style="zoom:50%;" />
这里就是这样，就是所谓的$2*2$循环展开，此时我们就可以打破延迟界限，逐渐达到吞吐界限。
当k足够大的时候，程序在几乎所有情况下都能达到吞吐量界限。

但是我们要注意==**这可能会引入舍入误差！！**==，比如如果奇数元素全部都是接近0.0，偶数全部很大，那就很麻烦

#### 2）重新结合交换

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



### 10 其他限制因素

#### 1） 寄存器溢出

如果我们的<u>并行度超过了可用的寄存器数</u>量，编译器就会诉诸<u>**溢出(spilling)**，把某些临时值放到内存里面，通常是在运行时堆栈上分配空间。</u>

比如下面这种情况，如果并行度太高，结果反而性能还下降了，因为x86-64用16个YMM保存浮点数，16个通用寄存器，这样导致**处理器还得先把内容放到内存里面再取出来**反反复复
![image-20260401180623473](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260401180623473.png)

#### 2）分支预测和预测错误处罚

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

   包含加载操作的程序性能显然会依赖于<u>加载单元的延迟</u>&<u>流水线的能力</u>
   一般情况下，加载和存储都是完全流水线化的（CPE = 1.00），








## 六、存储器层次结构

存储系统是一个层次结构，就像我们最开始那张图里面描述的那样：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260121012020788.png" alt="image-20260121012020788" style="zoom:40%;" />

### 1 存储技术

#### 随机访问存储器(RAM)

##### **静态SRAM**

- 更快更贵，用作高速缓存
- 每个位存储在一个双稳态的存储器单元内，可以无限期地保留在两个不同的电压配置/状态，其它任何状态都是不稳定的（在亚稳态看起来似乎可以稳定(震荡)，但是一点点扰动就足以导向一个状态，只要有电就永远可以保存这个值）
- 6T RAM，也就是6个晶体管，其实看下面就是一个交换配对反相器
  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260714101904384.png" alt="image-20260714101904384" style="zoom: 33%;" />
  它有3个工作状态：standby/reading/writing
  - standby也就是WL低电平，此时两个均截止无法读写
  - writing，比如写入1，那么就得$BL=1/\bar {BL}=0$，WL=1，就完成写入了
  - reading，同理

##### 动态DRAM

DRAM把每个位存储作为对一个电容的充电（一般是$30\times10^{-15}f$），DRAM可以被制造的非常密集，每个单元由一个电容和一个访问晶体管组成，但是不同于SRAM，DRAM存储单元对干扰非常敏感，一旦电压被扰乱就永远不可能恢复，暴露在光线下会导致电压改变（实际上数码照相机里面就是DRAM阵列）

很多原因会导致DRAM在10~100ms内失去电荷，但是由于计算机运行以ns为周期，因此只需要周期性地读出内存，然后重写刷新即可，同时为了避免错误，有的会采用纠错码纠正（比如64位编码成72位）

|      | 晶体管 | 相对访问时间 | 持续 | 敏感 | 相对花费 | 应用          |
| ---- | ------ | ------------ | ---- | ---- | -------- | ------------- |
| SRAM | 6      | 1            | 是   | 否   | 1000     | 高速缓存      |
| DRAM | 1      | 10           | 否   | 是   | 1        | 主存/帧缓冲区 |

##### 传统的DRAM

DRAM芯片中的单元被分为$d$个**超单元($supercell$)，**每个超单元由$w$个DRAM单元组成，超单元被组织成一个$r$ 行$c$列的长方形阵列($rc=d$)，用$(i,j)$表示地址

每个DRAM芯片被连接到被称为**内存控制器**的电路，它可以一次传送$w$位到每个DRAM芯片或一次从每个DRAM芯片传出$w$ 位，为了读取$(i,j)$的，内存控制器发送行地址$i$称为**RAS（Row Access Strobe行访问脉冲）**请求，列地址$j$称为**CAS（Column Access Strobe列访问脉冲）**请求，RAS和CAS请求共享相同的DRAM地址引脚

> （比如说我们要从DRAM读取超单元$(2,1)$，内存控制器发送行地址2，则DRAM把行2整个内容直接复制到一个内部行缓冲区，之后内存控制器再发送列地址1，那么DRAM的响应就是从行缓冲区复制出超单元$(2,1)$中的8位，发送到内存控制器）

##### 内存模块

DRAM芯片封装在内存模块，它插到主板的扩展槽上。比如Core i7使用的240引脚的双列直插内存模块，以64位为块和内存控制器传输数据
下图展示了一个内存模块的基本思想：示例模块用8个64Mbit的$8M\times 8$DRAM芯片，总存储64MB，而这8个DRAM同一个位置存储一个数据字的不同字节，比如一个64位的字，那么DRAM0对应的就是最低的字节，以此类推（这样可以提高并行度，比如想要读取一个数据只需要对所有DRAM芯片发送同样的RAS/CAS即可）
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260714112719347.png" alt="image-20260714112719347" style="zoom:50%;" />

##### 增强的DRAM

- **快页模式DRAM（Fast Page Mode---FPM DRAM）**。传统DRAM将超单元的一整行复制到它的内部行缓冲区，使用一个，然后丢弃剩余的；而它则运行对同一行连续地访问从行缓冲区得到服务（比如传统的想要读取一行的4个超单元必须发送4个RAS/CAS请求，而这种就只需要1个RAS和3个CAS请求即可）

- **扩展数据输出DRAM（Extended Data Out---EDO DRAM）**，它是FPM的一个增强形式，通过重叠操作周期允许各个CAS信号时间上更加紧密

- **同步DRAM（Synchronous---SDRAM）**，常规的都是异步的，而SDRAM用与驱动内存控制器相同的外部时钟信号的上升沿代表控制信号（这样的优点就是内部的任何操作都是和外部时钟统一的，CPU不需要等待它完成操作，因为周期是确定的，而以前则会CPU空转等待完成读写，流水线就停下来了）

- **双倍数据速率同步DRAM（Double Data-Rate Synchronous---DDR SDRAM）**，对SDRAM的一种增强，通过使用两个时钟沿作为控制信号从而使DRAM的速度翻倍

- **视频RAM（VRAM）**，它用于图形系统的帧缓冲区，思想和FPM类似，区别在：
  1. VRAM的输出是通过依次对内部缓冲区的整个内容进行位移得到的
  2. VRAM运行对内存并行地读写（也就是说可以在系统写入下一次更新值的同时读出帧缓冲区刷屏）


##### 非易失性存储器

上面的RAM在掉电的时候都会丢失信息，也就是说他们是易失的(volatile)，而非易失性存储器相反。虽然ROM有些类型支持读写，但整体上还是被称为只读存储器

- PROM：熔丝作为单元，只能编程一次
- EPROM：可擦ROM，每个单元有透明的石英窗，紫外线照射即可清零。而电可擦EEPROM则不需要特殊的设备来编程，因此可以直接被印刷在电路板
- flash闪存：基于EEPROM的存储技术，固态硬盘SSD就是基于闪存技术的

存储在ROM设备中的程序通常被称为固件firmware，当一个计算机系统通电后会运行存储在ROM的固件（以一些系统会在固件提供少量基本的IO函数，比如BIOS），而图形卡/磁盘驱动控制器也依赖固件翻译来自CPU的IO请求

##### 访问主存

数据流通过**总线(bus)**的共享电流在处理器和DRAM之间传输数据，传输的步骤被称为**总线事务(bus transaction)**。 read transaction:$CPU \to 主存$ write transaction:$CPU \to 主存$

总线是一组并行的导线，可以携带地址/数据/控制信号两个以上的设备也可以共享统一总线，控制线携带的信号会同步事务，并标识出当前正在被执行的事务的类型（比如读写，数据/地址，目标）

![image-20260715073523798](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260715073523798.png)

上面图中，核心是cpu,以及被称为I/O桥的芯片组和DRAM形成的主存，它们被一对总线连接：**系统总线**连接CPU和I/O桥，**内存总线**连接I/O桥和主存

当我们执行

```assembly
move A, %rax
```

总线接口(bus interface)在总线上发起读事务：

1. CPU把地址A放到系统总线上，I/O桥把信号送到内存总线上
2. 主存收到信号，读取地址，从DRAM里面取出数据写入内存总线，I/O桥把内存总线信号翻译为系统总线信号传入系统总线
3. CPU收到系统总线的数据，读取并拷贝到寄存器上

反过来，当我们执行：
```assembly
movq %rax, A
```

同样总线接口先发起一个写事务：

1. CPU把地址放到系统总线上，主存从内存总线读取地址后等待数据到达
2. CPU从`%rax`复制数据到系统总线
3. 主存从内存总线读取数据并存入DRAM

#### 磁盘存储

磁盘是一种存储大量信息的高性能(workhorse?)存储设备，它存储远大于RAM的数据，花费毫秒级别的时间来从磁盘读取信息，是DRAM的十万倍，SRAM的百万倍。

![image-20260716075420639](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260716075420639.png)

##### 磁盘构造(Disk Geometry)

磁盘由**盘片(platter)**构成，每个盘片有两个**表面(surface)**，中心是一个可以旋转的**主轴(spindle)**，以固定的旋转速率(rotational rate)旋转，通常是5400~15000 **RPM(Revolution Per Minute)**，磁盘通常包含多个盘片封装在密闭容器内
每个表面是一组称为**磁道(track)**的同心圆构成，每个磁道被划分为一组**扇区(sector)**，每个扇区包含相等数量的数据位（通常512字节），数据编码在扇区上的磁性材料，扇区间由间隙(gap)隔开，间隙存储用来标识扇区的格式化位
磁盘由这些盘片组成，封装起来，整个装置称为磁盘驱动器(disk drive)，即磁盘(disk)。被称为旋转磁盘(rotating disk)以区别于基于闪存的SSD.
而柱面(cylinder)则描述的是多个盘片驱动器的构造，指的是所有盘片表面到主轴中心距离相等的磁道的集合

##### 磁盘容量

一个磁盘上可以记录的最大位数称为最大容量(capacity)，取决于：

- **记录密度(recording density**，单位: $bits/in$ )：一段一英寸磁道可以塞入的位数
- **磁道密度(track density**，单位: $tracks/in$)：从盘心出发半径一英寸的段上可以塞入的位数
- **面密度(Areal density**，单位: $bits/in^2$)：记录密度与磁道密度的乘积，也就是位的面密度

原本面密度小的时候，每个磁道被分为数码相同的扇区，扇区数目取决于最靠内侧磁道所能记录的扇区数，因此越往外间隙越大；而随着面密度增大，间隙已经不可接受了，因此引入了**多区记录(mutiple zone recording)**的技术
而一个磁盘容量的计算公式如下：（`#*`表示变量）
$$
Capacity=\frac {\#bytes}{sector}\times\frac{average\#sector}{track}\times \frac{\#tracks}{surface}\times\frac{\#surfaces}{platter}\times\frac{\#platters}{disk}
$$
比如我们已知一个磁盘有5个盘片，每个扇区512字节，每个表面有20,000个磁道，平均每个磁道有300个扇区，那么计算就是：
$$
Capacity = 512 \times 300 \times 20,000 \times 2 \times 5 \\
= 30.72GB
$$

##### 磁盘操作

磁盘用读写头(read/write head)来读写存储在磁性表面的位，而读写头连接到一个**传动臂(actuator arm)**的一端，通过沿着半径轴前后移动这个传动臂，驱动器可以把读写头定位在盘面上的任意磁道，这个机械运动叫作**寻道(seek)**。有多个盘面的磁盘自然有分别的读写头，而读写头都是共柱面的，垂直放置统一行动
![image-20260716082105583](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260716082105583.png)
读写头隔着一层薄薄的气垫(0.1 micron)上移动，速度达到80km/h，显然只要有一点的微粒都会如同巨石一般，碰到读写头就会发生**读写头冲撞(head crash)**，因此磁盘必须密封包装
磁盘以扇区大小的块来读写数据，对扇区的**访问时间(access time)**由3个主要部分构成：

- **寻道时间(seek time)**：即把读写头定位到磁道的时间，依赖于读写头初始位置和传动臂在盘面上的移动速度。$T_{avg~seek}$则通过几千次对随即扇区的寻道求平均值，通常为3~9 ms，最大时间高达20 ms
- **旋转延迟(rotational latency)**：读写头定位到期望的磁道时，等待目标扇区第一个位旋转到读写头下的时间。依赖于读写头到达目标扇区时盘面的位置和RPM，最坏的情况下我们要转一整圈，此时$T_{max~rotation}=\frac1{RPM}\times\frac{60s}{1min}$
- **传送时间(transfer time)**：目标扇区的第一个位到达读写头下，读写的速度(也就是一整个扇区过完一遍的时间)：$T_{avg~transfer}=\frac1{RPM}\times\frac1{averag\#sectors/track}\times\frac{60s}{1min}$

举个例子，针对一个磁盘参数为：

| Parameter      | Val         |
| -------------- | ----------- |
| 转速           | $7,200 RPM$ |
| $T_{avg~seek}$ | $9 ms$      |
| 平均扇区/磁道  | 400         |

那么分别计算：
$$
\begin{align*}
T_{avg~rotation}&=0.5\times T_{max~rotation}\\&= 0.5\times \frac {60secs}{7,200 RPM}\times 1,000ms/sec \\&=4ms\\
T_{avg~transfer}&=60/7,200RPM \times 1/400 sectors/track \times 1,000ms/sec \\&=0.02ms\\
T_{access}&= 9 + 4 + 0.02 = 13.02ms
\end{align*} 
$$
从这个例子中可以看出，磁盘访问时间主要取决于**寻道时间**和**旋转延迟**，同时因为这俩差不多，我们往往直接把寻道时间乘2作为访问时间

##### 逻辑磁盘块（簇）

为了向操作系统隐藏实际磁盘构造的复杂性，往往把扇区简化为逻辑块的序列，内部封装有一个小的硬件/固件设备，称为**磁盘控制器**（维护实际与逻辑块的映射关系）
操作系统要执行一个IO操作时，会发送一个命令到磁盘控制器，让它读写某个逻辑块号，而控制器的固件执行一个表查找，把**逻辑块号**翻译为**（盘面，磁道，扇区）**的三元组，它唯一地标识了对应的物理扇区。而控制器再解释它进行读写

（磁盘控制器必须对磁盘进行格式化后才能存储数据，这个过程包括：

- 用标识扇区的信息填写扇区间的间隙

> 练习6.4 假设1MB的文件由512个字节的逻辑块组成，存储在下面这个磁盘中：
>
> | 参数            | 值          |
> | --------------- | ----------- |
> | 转速            | 10, 000 RPM |
> | $T_{avg~seek}$  | 5ms         |
> | 平均扇区数/磁道 | 1000        |
> | 表面            | 4           |
> | 扇区大小        | 512字节     |
>
> 分别估算两种情况：
>
> 1. 最好的情况，即是按顺序连续的映射，估计最优时间：
>    显然，这个文件由2048个逻辑块构成，最优情况需要seek 一次，然后没有旋转时间，传送时间为$60/10,000\times2,048=12.288ms$，总共17.288ms
> 2. 平均的情况，即逻辑块是随机分布的，那么我们认为每次都是重新寻道，算的时候只能每个扇区分别计算，需要一个寻道时间，旋转时间取一半为3ms，而传送时间为0.006ms，总共为8.006ms，那么1MB就是16.4s





##### 连接IO设备

IO设备都是通过**IO总线**，比如intel的**外围设备互联总线（PCI，Peripheral Component Interconnect）**连接到CPU和主存的。不同于与CPU相关的系统总线和内存总线，IO总线和CPU是不相关的。
而IO总线虽然更慢，但是它可以兼容各种IO设备，比如下图这个就有3种总线和它连接：

1. Universal Serial Bus（通用串行总线USB）控制器：所有连接到USB总线上的设备的中转

2. graphic card/adapter(图形卡)：包含硬件和软件逻辑，代表cpu在显示器上画像素

3. host bus adapter(主机总线适配器)：将若干个磁盘连接到IO总线，使用一个主机总线接口定义的通信协议，两种常用的磁盘接口是SCSI("scuzzy")和SATA("sat-uh")，SCSI更快更贵，支持多个磁盘，而SATA只支持一个

4. 而其他设备比如网络适配器，可以通过将适配器插入主板上空的扩展槽连接到IO总线，它们提供了到总线的直接电路连接

   <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260717032750400.png" alt="image-20260717032750400" style="zoom:60%;" />

##### 访问磁盘

CPU使用**内存映射I/O技术(memory-mapped I/O MMIO)**向I/O设备发送命令。在这样一个系统中， 任何设备的读写都是映射到地址空间上的，这个地址就称为**IO端口(port).**

> 比如一个磁盘驱动器分配到地址为0xa0，那么为了存储CPU就得发3条指令：
>
> 1. 第一条告诉磁盘驱动器**开始读取**（包含参数如是否读取完毕发送中断到cpu）
> 2. 第二条指明应该读的**逻辑块号**
> 3. 第三条之名应该存储磁盘扇区内容的主存地址
>

当CPU发完请求后，磁盘执行读，CPU就可干别的事情（因为读取一次需要16ms，而cpu周期以ns计算的话，可以执行千万条指令）
磁盘控制器接受来自CPU的读命令后，把逻辑块号翻译为对应的扇区地址，读取内容后传送到主存（通过**DMA传递(DMA transfer)**)
DMA传送完成后，磁盘扇区的内容就在主存里面了，此时磁盘控制器发送一个中断信号通知CPU（中断信号到芯片一个外部引脚，导致其停下当前工作跳转到操作系统的一个例程，记录IO完成后返回）

> PCI 模型中，系统所有设备共享总线，同一时刻只有一台设备访问线路，而现代系统使用 **PCIe（PCI Express）** 取代，它是一组高速串行、通过开关连接的点到点链路，最大吞吐率为 16GB/s，远快于 PCI 的 533MB/s

##### 冗余磁盘阵列（补充）

RAID(redundant arrays of inexpensive disks，廉价磁盘冗余阵列)：

基本想法：用多个独立的磁盘驱动器组成磁盘阵列，增加容量

- RAID0：无冗余盘无校验
- RAID1：镜像盘一对一冗余，两个一样的，读的时候取最快的那个，写的时候两个需要一起写（因此写取决于最慢的那个）
- RAID2：使用海明校验生成多个冗余校验盘
- 

#### 固态磁盘

一个SSD封装：

- **闪存芯片**，代替旋转磁盘的机械驱动器
- **闪存翻译层(flash translation layer)**，硬件/固件设备，相当于磁盘控制器，翻译请求为物理访问

![image-20260717115253954](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260717115253954.png)
从下图可以看出，读SSD比写更快（这一性能差别取决于底层闪存的基本属性，因为读什么时候都可以，写需要在特定时钟），一个闪存由$B$个快的序列组成，每个块由$P$页组成，通常页的大小是512Byte~4KB，块的大小是16KB～512KB。数据以页为单位读取，只有一页所属的块整个被擦除后才能写入这一页。（一般是全部置1）
![image-20260717115521854](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260717115521854.png)
而随机写很慢两个原因：（尽管制造商在翻译层通过逻辑尽可能减小代价)

1. 擦除块本身需要较长的时间(1ms)
2. 如果写操作试图修改一个包含已有数据的页p，那么这个块所有有用数据的页都必须复制到一个新的块（擦除过的），再进行写入

特点：

- 没有机械转动，因此随机访问时间快于旋转磁盘，低能耗而且结实
- 反复写后闪存块会磨损，闪存翻译层会通过平均磨损逻辑(wear leveling)来把磨损尽可能平摊
- 每字节比旋转磁盘贵30倍，因此常用的存储容量比旋转磁盘小100倍

>习题6.5 我们假设
>
>

#### 存储技术趋势

几个重要的思想：

- 不同存储技术有不同的价格和性能折中
- 不同的存储技术有不同的发展速度
- DRAM和磁盘的性能滞后于CPU的需求

正因为如此，现在的cpu往往尽可能利用基于SRAM的高级缓存（当然下一章就会提到）

### 2 局部性

#### 局部性原理

一个好的计算机程序往往具有良好的**局部性（locality）**：

- **时间局部性**：一个有良好时间局部性的程序，被引用一次的同一个内存位置很可能很快再被多次引用

- **空间局部性**：如果一个内存位置被引用一次，那很可能它会很快引用附近的一个内存位置

##### 为什么需要局部性？

因为数据是以块为单位在缓存层次间传递的，如果连续那么只需要传输更少的块就可以完成

#### 对程序数据引用的局部性

> 考虑一个例子：
> ```c
> int sumVec(int v[N]){
>     int i, sum = 0;
>     for (i = 0; i < N; i++)
>         sum += v[i];
> 	return sum;
> }
> ```
>
> 这里`sum`每次循环都会访问，所以它有时间局部性，又因为它是标量，所以它不具有空间局部性
> 而对于向量`v[N]`，它有良好的空间局部性，但是不具有好的时间局部性

像`sumVec`函数这样顺序访问向量每一个元素，具有**步长为1的引用模式(stride-1 reference pattern**，也称**顺序引用模式-sequential reference pattern)**，一个连续向量，每隔k个元素访问则称为步长k的引用模式，随着步长增加，空间局部性下降

而对于多维数组，步长同样重要：

> 比如：
> ```c
> int sumArrayRows(int a[M][N]){
>     int i, j, sum = 0;
>     for (i = 0; i < M; i++)
>         for (j = 0; j < N; j++)
>             sum += a[i][j];
>     return sum;
> }
> ```

`sumArrayRows`中双重嵌套循环按照**行优先顺序**读数组的元素。
而如果我们仅仅改变一下嵌套的顺序，就会发现对局部性有很大的影响，下面这个就是stride-N reference pattern：

>```c
>int sumArrayRows(int a[M][N]){
>    int i, j, sum = 0;
>    for (j = 0; j < N; j++)
>    	for (i = 0; i < M; i++)
>            sum += a[i][j];
>    return sum;
>}
>```

#### 取指的局部性

如果同样的指令被多次执行（比如在 `for` 循环里面），那么它就有**时间局部性**；而相邻指令按顺序反复取指，体现的是**空间局部性**。
唯一和数据的区别就是代码不可更改

### 3 存储器层次结构

我们前面描述了，不同存储技术访问时间差异很大，而良好的程序倾向于有良好的局部性，它们的互补产生了所谓的存储器层次结构(memory hierarchy)，越往下越慢/便宜/大
![image-20260719090813264](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260719090813264.png)
L0是CPU寄存器，可以在1个时钟周期内访问；基于SRAM的cache，在个位数的时钟周期里访问；基于DRAM的主存，可以在几十上百个时钟周期内访问；最底层则是一些远程的服务器上的存储，比如AFS安德鲁文件系统/网络文件系统NFS

#### 缓存

**高速缓存**(cache，"cash")是小而快的，使用高速缓存的过程叫作**缓存(caching)**
存储器层次结构核心思想就是<u>**位于k层的更快更小的存储设备是k+1层更大更慢的存储设备的缓存**</u>
第k+1层的存储器被划分为连续的数据对象**组块(chunck)**，称为**块(block)**，它的地址唯一确定，大小往往固定(也可以是可变的)
![image-20260719091556879](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260719091556879.png)
而第k层存储器被划分为较少的块的集合，数据总是以**块**为**传送单元(transfer unit)**在k和k+1层进行传输的

##### 缓存命中

当程序需要第k+1层的数据对象d时，<u>它首先会在第k层的块内查找数据。</u>
<u>如果它正好被缓存在了k层</u>，那么就称为**缓存命中(cache hit)**。

##### 缓存不命中

<u>如果k层没有要找的数据对象</u>就是**缓存不命中(cache hit)**。
此时k层缓存就会从k+1层缓存取出包含d的那个块，如果满了就会覆盖已有的块，这个覆盖的过程称为**替换(replace)/驱逐(evict)**这个块，而决定哪个被替换的就是**替换策略(replacement policy)**

#####  缓存不命中的分类

如果缓存本身为空（**冷缓存cold cache**），那么一定发生未命中，称之为**冷不命中/强制性不命中**，是一个短暂的事件，在缓存暖身后不会发生

硬件缓存通常使用的是更严格的放置策略，**<u>一般来说k+1层的某个块会被限制在k层的一个更小的子集中</u>**（比如i mod 4，可以类比为散列）

而这种限制性的放置策略会引发一种不命中，称为**冲突不命中(conflict miss)**，此时虽然缓存本身足够大，但是由于限制仍会发生不命中（比如mod4，如果反复请求块0和4那么永远都是不命中）
程序通常是按照一系列阶段运行的，每个阶段访问缓存块的某个相对稳定不变的集合，这个块的集合称为这个阶段的**工作集(working set)**，工作集超过缓存大小时就必然会出现缓存不命中

##### 缓存管理

每一层上的逻辑必须管理缓存，也就是要把缓存划分为块，在不同层之间传送块，判定命中与否并处理。

> 比如编译器管理寄存器文件L0，决定发生不命中时何时发生/加载，以及确定哪个寄存器来存放数据。
> L1/L2/L3则完全是内置在缓存的硬件逻辑来管理的。
> 而在一个有虚拟内存的系统中，DRAM作为存储在磁盘上数据块的缓存，是由操作系统软件和CPU上的地址翻译硬件共同管理的。



![image-20260719111032170](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260719111032170.png)

### 4 高速缓存存储器

最早实际上只有CPU/DRAM主存/磁盘，但是由于CPU和主存差距逐渐拉大，因此在之间又引入了SRAM高速缓存。

#### 通用的Cache结构

考虑一个m位的机器，它的cache就是一个$S=2^s$的缓存组(cache set)，每个组内有$E$个缓存行(cache line)，每个行包含：

1. $B=2^b$的块
2. 有效位(valid bits)表明是否有数据
3.  $t=m-b-s$的标签位，专门标识被存储的块

而一个缓存的组织可以被元组$(S,E,B,m)$描述，高速缓存的大小$C=S\times E\times B$，描述的是包含所有块的位数之和
CPU从主存A加载一个字时，地址A被发送到cache，如果高速缓存包含那个字的副本，就会把这个字发送给CPU，判断方法如下：
S和B将m个地址位划分为3个字段，s部分代表这个字应该被存入哪个组，而t则代表这个组中的哪一行包含这个字，而b 则给出了在B个字节的数据块中的字偏移

![image-20260719111621268](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260719111621268.png)


#### 直接映射高速缓存

根据每个组的高速缓存行数E,高速缓存被分为不同的类，每组只有一行的被称为**直接映射高速缓存(direct-mapped cache)**，这是最容易实现最简单的

> 假如一个系统有CPU/L1cache/主存，CPU执行读内存字w的命令，它向L1缓存请求，如果有这个副本就是L1高速缓存命中，失败了则需要向主存请求，而此时CPU必须等待，而之后再通过L1返回CPU

高速缓存**确定一个请求是否命中**然后抽取被请求的字的过程分为三步：1. 组选择 2. 行匹配 3. 字抽取

##### 1 直接映射cache中的组选择(Set Selection in Directed-mapped caches)

首先高速缓存从w的地址中抽出s个组索引位，它们被解释为一个对应于一个组号的无符号整数，作为索引确定组号i

##### 2  直接映射cache中的行匹配(Line Matching in Directed-mapped caches)

确认组i之后，接下来就是确认是否有字w的一个副本存储在组i包含的一个高速缓存行中，当且仅当<u>行设置了有效位</u>且<u>高速缓存行中的标记和w的地址中的标记相匹配</u>时确认命中

> 我们举的例子是直接映射，这个组的一行有效位被设置了，而高速缓存行中的标记位Tag和这一行匹配，那么通过块偏移我们就可以找到数据块
> ![image-20260720005350488](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260720005350488.png)

---

> 这里就有个问题，Tag是如何确定的，为什么能保证行匹配时不会出现Tag冲突？
>
> 实际上非常简单，Tag就是我们去掉s和b部分剩下的内容。
> 比如CPU想要申请一个地址0x1234(16位地址，cache line为16B，4个set，2-way组相联)，它的二进制就是`0x0001 0010 0011 0100`
>
> | 10-Tag       | 2-Set index | 4-block offset |
> | ------------ | ----------- | -------------- |
> | 0001 0010 00 | 11          | 0100           |
>
> 为什么它是唯一的？因为是同一个物理地址在不同cache层次用相应的S和B进行切分得到的，如果Tag相同而且Set也相同，那么它们自然就一定在同一个块里面。就像我们前面说的那样(S,E,B,m)这个元组本身就可以唯一描述一个地址，实际上这就是一个典型的hash bucket

##### 3 直接映射cache中的字选择

一旦命中，我们就知道w在块的某个地方，最后一步确认的是字在块的位置，这就由Block offset决定，它代表所在字的第一个字节的偏移，比如`0b100`就代表第4位开始是这个字的位置

##### 4 直接映射cache不命中时的行替换

如果不命中，它就需要从存储器层次结构下一层取出被请求的块，再把新的块存储在组索引位指示的一个缓存行里面。而如果一个组内全是有效行，此时就得逐出一行。（而这里是直接映射，因此直接替换即可）

##### 5 综合：运行中的直接映射cache

我们用具体的案例来解释：一个缓存描述如下(S, E, B, m)=(4, 1, 2, 4)
就像前面说的一样(Tag, Index, Offset)便唯一构成了我们的地址，其中：

- 标记位和索引位便共同唯一确定了一个块
- 因为我们有8个块却只有4个缓存组，因此只能多个块映射到一起(比如0和4都会被放入0组里面)
- 映射到同一个组内的块由Tag唯一标识

![image-20260720013530288](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260720013530288.png)





> **为什么要用中间的位作索引？**
>
> 原因很简单，如果用最高位，那么会导致连续的块被分配到一起，显然这不利于我们顺序引用模式；
> 而如果用最低几位。。。Block Offset才能保证我们可以更精细地访问具体的位，只能放在中间了

#### 组相联高速缓存

所谓组相联(set associative)其实就是组里面多几行罢了，一个$1 < E < C/B$的高速缓存称为E路组相联高速缓存

##### 1 组相联高速缓存的组选择

它的组选择与直接映射一样

##### 2 组相联高速缓存的行匹配和字选择

组相联高速缓存的行匹配还需要检查多个行的有效位和标记位以确认是否有。每个组可以被看作相联存储器，它是一个$(key, val)$对的数组，以key为输入，返回与输入key相匹配的对中的val值。

##### 组相联高速缓存不命中时的行替换

如果CPU请求的字不再组的任何一行就是缓存不命中，就需要采用替换策略，最简单的是随机替换，而复杂一些的则利用了局部性原理，如LFU和LRU

#### 全相联高速缓存

全相联高速缓存(fully associative cache)是一个由所有包含所有高速行的组组成的($E=C/B$)
工作机制和前面的没什么区别，因为就一组所以没必要专门选择组
![image-20260720084757262](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260720084757262.png)
由于高速缓存电路必须并行地搜索Tag匹配，显然想要更大就会更昂贵，因此只能用作小的高速缓存，如虚拟内存中的翻译备用缓冲区(TLB)

#### 关于写

写比读更复杂，如果想要写一个已经缓存了的字w(*write hit*)，在高速缓存更新了它的w的副本之后，想要更在层次结构更低一级的副本，就得通过**直写(write through)**，也就是立即将w的高速写到紧接着的低一层中（优点是快而且简单，缺点是增加了复杂性），高速缓存必须为每一个高速缓存行维护一个额外的**脏位(dirty bit)**表明这个高速缓存块是否被修改过

而处理写不命中：

- 一种方法是**写分配(write-allocate)**，加载相应更低一层的块到高速缓存中，然后更新这个高速缓存块，这种方法试图利用写的空间局部性，但显然只要不命中就导致要从低一层传送到高速缓存
- 另一种是**非写分配(not-write-allocate)**，避开高速缓存直接把这个字写入低一层

### 编写高速缓存友好的代码

基本方法：

- **让最常见的情况运行最快。**

  关注核心函数的循环，忽略其他部分

- **尽量减少每个循环内部的缓存不命中数量**

  

### 综合：高速缓存对程序性能的影响

#### 存储器山

程序从存储系统读数据的速率称为读吞吐量(read throughput)，也称读带宽(read bandwidth)，通常以MB/s作为单位
如果一个程序从一个紧密的程序循环中发出一系列读请求，那么读吞吐量就能反映对于这个读序列的存储系统性能

```c
long data[MAXELEMS];
int test(int elems, int stride){
    long i, sx2 = stride * 2, sx3 = stride *3, sx4 = stride * 4;
    long acc0 = 0, acc1 = 0, acc2 = 0, acc3 = 0;
    long length = elems;
    long limit = length - sx4;
    for (i = 0; i < limit; i+=sx4){
        acc0 += data[i];
        acc1 += data[i+stride];
        acc2 += data[i+sx2];
        acc3 += data[i+sx3];
    }
    for (; i < length; i+=stride)
        acc0 += data[i];
    return ((acc0 + acc1) + (acc2 + acc3));
}
double run(int size, int stride, double Mhz){
    double cycles;
    int elems = size / sizeof(double);
    test(elems, stride);
    cycles = fcyc2(test, elems, stride, 0);
    return (size / stride) / (cycles / Mhz);
}
```

`test`函数里面采用了$4\times4$展开提高并行性，`run`则返回函数的运行时间(以CPU周期为单位)，`run`函数的参数`size`对应工作集控制时间局部性，`stride`对应空间局部性，通过不同的`size`和`run`调用即可得到一个二维表称为存储器山(memory mountain)
![image-20260725091005582](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260725091005582.png)



> 这里有一个可能会搞混的地方，从各级cache到DRAM主存，始终用的都是一个地址空间，各级虽然缓存但是都是从下一级缓存上来的，而至于磁盘则有自己的地址空间，这是磁盘控制器负责的





## 七、链接

**链接(linking)**是将代码和数据片段收集组合成为一个单一文件的过程，这个文件可以被加载到内存并执行。链接可以执行于**编译时(complie time)**，也就是源代码翻译为汇编的时候；也可以执行于**加载时(load time)**即程序加载到内存的时候；甚至可以执行于**运行时(run time)**，也就是由应用程序执行。现代系统的链接是由链接器来执行的

有什么用？

- 有助于构建大型程序：缺少库、模块、版本不兼容，只有理解链接器如何解析引用、何为库等等才能解决
- 有助于避免危险的编程错误：Linux链接器

### 7.1 编译器驱动程序

比如我们想要编译一个程序

```bash
gcc -Og -o prog main.c sum.c   # 如果想要查看具体步骤，加上 -v 选项运行
```

### 7.2 静态链接

静态链接器(static linker)
以一组可重定位目标文件和命令行参数作为输入，
生成一个完全链接的/可以加载运行的可执行文件作为输出。
输入的可重定位目标文件由各种不同的代码和数据节(section)构成，每一节都是一个连续的字节序列。

为了构造可执行文件，链接器需要完成2个主要任务：

- **符号解析(symbol resolution)**。目标文件定义和引用符号，每个符号对应函数/全局变量/静态变量，符号解析的目的是将每个符号引用正好和一个符号定义关联
- **重定位(relocation)**。编译器和汇编器生成从0地址开始的代码和数据节，链接器把每个符号定义关联到一个内存位置，也就是重定位这些节，然后修改所有对符号的引用使它们指向这个内存位置。链接器使用汇编器产生的重定位条目(relocation entry)的详细指令

### 7.3 目标文件

目标文件分为：

- **可重定位目标文件**：二进制代码和数据，其形式可以在编译时与其他可重定位目标文件合并，创建一个可执行目标文件
- **可执行目标文件**：二进制代码和数据，形式可以直接被复制到内存执行
- **共享目标文件**：特殊的可重定位目标文件，在加载和运行时被动态地加载进内存并链接

编译器和汇编器生成的是可重定位目标文件，链接器生成可执行目标文件。
一个目标模块(object module)就是一个字节序列，而一个目标文件(object file)就是一个以文件形式存储在磁盘内的目标模块

> 贝尔实验室一开始使用的是a.out格式，windows使用可移植可执行(Portable Executable, PE)格式，MacOS使用Mach-O格式，现代x86-64linux和Unix使用可执行可链接(Executable and Linkable Format, ELF)格式。

### 7.4 可重定位目标文件

一个典型的ELF文件结构如下：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260728165322156.png" alt="image-20260728165322156" style="zoom:70%;" />

**ELF头**以一个16字节序列开始，描述了生成该文件系统的字的大小和字的顺序，剩下的部分包含帮助链接器语法分析和解释目标文件的信息，其中包含<u>ELF头的大小/目标文件类型(3类)/机器类型/节头部表（section header table)的文件偏移/节头部表中条目大小和数量</u>。 不同节的位置和大小是由节头部表描述的，每个节都有对于固定大小的条目

而在ELF头和节头部表中间的就是节，典型如下：

- `.text`：已编译程序的机器码
- `.rodata`：只读数据（如`printf`的格式串/开关语句的跳转表）
- `.data`：`已初始化的全局/静态变量`（局部的只需要作为寄存器/压栈就可以了）
- `.bss`：`未初始化的静态变量`+`初始化为0的全局/静态变量`（注意不包含`未初始化的全局变量`）
  由于这一点，目标文件中这个节本身不占据实际空间，而是作为占位符。（这也是我们区分`.data`和`.bss`的原因）

  > 虽然一开始在IBM704是作为Block Storage Start的缩写，不过你可以认为它是Better Saving Space
- `.symtab`：一个符号表，存放在程序内定义引用的函数和全局变量的信息。

  > 实际上不需要-g选项编译也是有符号表的，只不过ELF内的符号表不会包含局部变量的条目

- `.rel.text`：一个`.text`节中位置的列表，功能就是它的名字也就是用于重定位，当链接器把目标文件和其他文件组合时需要修改这些位置。（当然只需要改变对外部函数/全局变量引用的指令

- `.rel.data`：被模块引用/定义所有全局变量的重定位信息

- `.debug`：调试符号表，这个才是`-g`生成的

- `.line`：原始C程序行号和`.text`中机器指令之间的映射，同样是`-g`生成

- `.strtab`：一个字符串表，内容包含`.symtab`/`.debug`中的符号表，以及节头部中的节名字

  > 为什么需要它？
  > `.symtab`和`.debug`里面不可能直接存原始字符串，而是存储偏移量，这是为了节省空间，因为字符串作为名字只有在：1. 链接阶段 2. 动态链接 3. 调试信息	
  > 这三个情况会有用，而运行时删除当然不影响
  > （以及很显然它本身并不会存比如printf的字符串，这些只会被放在.rodata）

### 7.5 符号和符号表

每个可重定位目标模块$m$都有一个**符号表**，包含它的定义和引用的符号信息，链接器的上下文中有3种不同的符号：

- 由模块$m$定义并能被其他模块引用的**全局符号**
  （对应非静态的C函数(没有用static修饰，可以跨文件调用)/全局变量）
- 由其他模块定义并被模块$m$引用的全局符号，被称为**外部符号**
- 只被模块$m$定义和引用的**局部符号**

很显然，本地链接器符号和本地程序变量不同，因为链接器不关心本地非静态程序变量，它们由栈管理

而要注意，带有static属性的本地过程变量无法在栈里面管理，需要编译器在`.data`/`.bss`中分配空间，并且在符号表内创建一个有唯一名字的本地链接器符号

> 比如这个例子，在一个模块的两个函数各自定义了一个静态全局变量：
> ```c
> int f(){
>     static int x = 0;
>     return x;
> }
> int g(){
>     static int x = 1;
>     return x;
> }
> ```
>
> 那么编译器就会向汇编器输出两个不同名字的局部链接器符号，因为对于编译器它们是2个不同的东西，例如：x.1 和 x.2

##### static：

（实际上用一句简单的话来总结，就是用static修饰会使得这个变量/函数本身都变成该模块/函数作用域私有的，而对这个作用域内它就是静态的）

| 定义位置                 | 含义             | 是否共享       |
| ------------------------ | ---------------- | -------------- |
| 文件外层 `static int x;` | 模块私有全局变量 | 同一文件共享   |
| 函数内 `static int x;`   | 函数私有持久变量 | 只有该函数共享 |
| 普通局部 `int x;`        | 自动变量         | 每次调用新建   |
| 普通全局 `int x;`        | 外部全局变量     | 整个程序共享   |

符号表是由汇编器构造的，用的是编译器输出到汇编.s文件的符号，被放到`.symtab`，这张表包含一个数组，每个条目格式为：![image-20260729180510770](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260729180510770.png)

`name`是字符串表中的字节偏移，指向符号的以`null`结尾的字符串
`value`是符号的地址： 1. 对可重定位模块，是距离定义目标的节的起始位置的偏移 2. 对可执行目标文件，是一个绝对运行时地址
`size`是目标大小
`type`即区分数据和函数，当然符号表也包含各个节的条目以及对应原始源文件的路径名的条目，类型也会有不同
`binding`字段表示符号是本地/全局的
`section`字段表示每个符号被分配到目标文件的某个节，它也是一个到节头部表的索引。但是这个字段不一定表示实际的模块里面的节，有3个**伪节(pseudosection)**：1. **ABS** 无需重定位的符号（因为别的符号需要重定位加上偏移量） 2. **UNDEF** 未定义符号（在本模块引用但是在其他地方定义，告诉链接器需要自己寻找，找不到就会link error） 3. **COMMON**表示还未被分配位置的未初始化的数据目标（它的意思就是：我有这个符号定义，但是我想之后在统一分配，比如如果有多个COMMON的话就合并）

COMMON和`.bss`的区分在于：（这样绝对区分原因在于符号解析的方式）

| COMMON   | 未初始化的全局变量                              |
| -------- | ----------------------------------------------- |
| **.bss** | **未初始化的静态变量+初始化为0的全局/静态变量** |

想要查看目标文件可以用`readelf`，比如我们对一个目标文件查看符号表最后3个条目：
![image-20260729190741809](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260729190741809.png)
main是一个在`.text`节(Ndx=1)偏移为0的24字节函数
array是一个在`.data`节(Ndx=3)偏移为0的8字节目标
sum则是一个外部符号的引用

> 练习7.1对每个在swap.o中定义/引用的符号，指出是否在swap.o的symtab节里面有条目:
> ![image-20260729191154051](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260729191154051.png)
>
> | 符号  | .symtab? | 符号类型 | 定义在哪个模块 | 节     |
> | ----- | -------- | -------- | -------------- | ------ |
> | buf   | true     | 外部     | m.c            | UND    |
> | bufp0 | true     | 全局     | swap.c         | .data  |
> | bufp1 | true     | 全局     | swap.c         | COMMON |
> | swap  | true     | 全局     | swap.c         | .text  |
> | temp  | false    | 局部     | /              | /      |
>
> 

### 7.6 符号解析

链接器解析符号引用的方法：将每个引用与它输入的可重定位目标文件的符号表中的一个确定的符号关联起来。
对于和引用定义在相同模块的局部符号的引用，符号解析自然很简单，
而对于全局符号的引用解析则不同：
当编译器发现一个不在当前模块定义的符号时，会假设它定义于其他模块，生成一个链接器符号表条目交给链接器，而如果链接器在任何输入模块都找不到被引用符号的定义，就会报错终止
当多个目标文件定义相同名字的全局符号，链接器要么报错，要么选出一个定义丢掉别的

> 而在C++/Java里面都允许重载方法，虽然它们源码名字相同却有不同的参数列表，而此时编译器就会把每个唯一的方法和参数列表组合编码得到一个符号名（由于方法名和参数唯一确定一个函数所以分别编译后只需要处理依赖关系匹配即可）这个过程叫重整mangling，而反过来叫恢复demangling

#### 链接器解析多重定义的全局符号

链接器的输入是一组可重定位的目标模块，有些是局部的(只对本模块可见)，有些全局(其他模块可见)
在编译的时候，编译器向汇编器输出每个全局符号，**强(strong)/弱(weak)**。这是汇编器隐含地编码在可重定位目标文件的符号表里的：
**<u>函数和已初始化的全局变量是强符号，</u>**
**<u>未初始化的全局变量是弱符号</u>**

根据强弱符号的定义，Linux的链接器采用以下规则处理多重定义的符号名：

1. **不允许有多个同名的强符号**
2. **如果有一个强符号和多个弱符号同名，选择强符号**
3. **如果多个弱符号同名，任意选择一个**

比如如果我们定义了两个main函数在不同的模块，那么就会报错。同理定义了两个强的全局变量也会报错。
但如果发生规则2/3的出现，此时链接器不会表明检测到多个定义！！因此这回造成一些难以察觉的运行时错误

> 比如下面这个案例，我们错误地定义了不同类型的x：
>
> ```c
> /* foo5.c */
> #include <stdio.h>
> void f();
> 
> int y = 15212;
> int x = 15213;
> 
> int main (){
>     f();
>     printf("x = 0x%x,  y = 0x%x \n", x, y);
>     return 0;
> }
> /* bar5.c */
> double x;
> 
> void f(){
>     x = -0.0;
> }
> ```
>
> （不过现代的gcc好像跟书上产生的是不同的效果，我自己用gcc编译，它就发现错误了：
> ```bash
> $ gcc -Wall -Og -o foobar5 foo5.c bar5.c
> >>>/usr/bin/ld: /tmp/ccoEBqBs.o:(.bss+0x0): multiple definition of `x'; /tmp/cc6p8xTj.o:(.data+0x0): first defined here
> >>>collect2: error: ld returned 1 exit status
> ```
>
> 原因似乎是现代的GCC默认开启了`-fno-common`选项，事实上改为下面就对了：
> ```bash
> $ gcc -fcommon -Wall -Og -o foobar5 foo5.c bar5.c
> >>> /usr/bin/ld: warning: alignment 4 of normal symbol `x' in /tmp/ccWtS5UU.o is smaller than 8 used by the common definition in /tmp/ccMzszLO.o
> >>> /usr/bin/ld: warning: NOTE: alignment discrepancies can cause real problems.  Investigation is advised.
> 
> $ ./foobar5 
> >>> x = 0x0,  y = 0x80000000 
> 
> ```
>

#### 与静态库链接

以上我们都是假设链接器读取一组可重定位目标文件，把它们链接然后形成输出的可执行程序
而实际上编译系统会提供一种机制，把所有相关目标模块打包为一个单独的文件称为**静态库(static library)**，可以作为链接器的输入，而只需要复制被引用的目标模块即可

而如果没有静态库：
一种方法是像Pascal一样让编译器辨认出对标准函数的调用并生成相应代码，但是C标准定义了大量标准函数，这不仅麻烦而且每次修改一个标准函数就需要一个新的编译器版本；

另一种方法则是把所有C标准函数放在一个单独的可重定位目标文件，应用程序员可以把这个模块链接到可执行文件中：

```bash
$ gcc main.c /usr/lib/libc.o
```

这种方法优点是编译器和具体的函数实现解耦了，但是显然这样每个可执行文件都需要一个完整的标准函数集合副本，这会造成磁盘空间/内存的浪费。而且同样每次修改标准函数需要重新编译整个源文件。

进一步，考虑把这些标准函数分开创建独立的可重定位文件，但是很显然这又需要程序员显式地把目标模块链接到可执行文件，这很麻烦：
```bash
$ gcc main.c /usr/lib/printf.o /usr/lib/scanf.o
```

因此我们提出来静态库，它<u>把相关函数编译为独立的目标模块，再封装为一个单独的静态库文件</u>，只需要指定单独的文件名即可完成链接：

```bash
$ gcc main.c /usr/lib/libm.a /usr/lib/libc.a
```

在Linux系统，静态库以一种称为**存档(archive)**的特殊文件格式存放在磁盘，它是一组连接起来的可重定位目标文件的集合，有一个头部描述每个成员目标文件的大小和位置，由后缀`.a`标识

> 比如下面两个例程，我们对每一个例程定义在它自己的目标模块当中，对两个输入向量进行一个向量操作：
> ```c
> /* code/link/addvec.c */
> int addcnt = 0;
> void addvec (int *x, int *y, int *z, int n){
>     int i;
>     addcnt++;
>     for (i = 0; i < n; i++)
>         z[i] = x[i] + y[i];
> }
> /* code/link/multvec.c */
> int multcnt = 0;
> void multvec (int *x, int *y, int *z, int n){
>     int i;
>     multcnt++;
>     for (i = 0; i < n; i++)
>        	z[i] = x[i] + y[i];
> }
> ```
>
> 想要创建这些函数的一个静态库，就可使用AR工具：
> ```bash
> $ gcc -c addvec.c multvec.c
> $ ar rcs libvector.a addvec.o multvec.o
> ```
>
> 那么使用它，我们这里在`vector.h`里面定义了`libvector.a`的函数原型：
> ```c
> #include <stdio.h>
> #include "vector.h"
> int x[2] = {1, 2};
> int y[2] = {3, 4};
> int z[2];
> int main(){
>     addvec(x, y, z, 2);
>     printf("z = [%d %d]\n", z[0], z[1]);
>     return 0;
> }
> ```
>
> 那么再o建可执行文件：
> ```bash
> $ gcc -c main2.c
> $ gcc -static -o prog2c main2.o ./libvector.a
> # 也可以是：
> $ gcc -static -o prog2c main2.o -L. -lvector
> ```
>
> 这里的参数：
>
> - -static：链接器要构建一个静态的/完全链接的可执行目标文件(直接加载)
> - -lvector：参数`libvector.a`的缩写
> - `-L.`参数告诉链接器在当前目录下查找
>
> 

#### 链接器使用静态库解引用{U,E,D}

在符号解析阶段，链接器从左到右按照它们在编译器驱动程序命令行上出现的顺序来扫描可重定位目标文件/存档文件，扫描时链接器维护：**<u>一个可重定位目标文件集合E</u>** / **<u>一个未解析符号集合U</u>** / **<u>一个前面输入文件已定义的符号集合D</u>**。

- 初始状态下三者均为空
- 对每个输入文件f,先判断是目标文件还是存档文件
- f为目标文件，添加f到E，修改U和D来输入f中的符号定义和引用
- f为存档文件，尝试匹配U中未解析符号和f定义的符号，如果一个存档文件成员m定义了一个符号解析U中的一个引用，那么m加入E并且相对应地调整U和D反应这一映射关系，直到二者都不发生变化，此时丢弃所有不包含在E当中的成员目标文件，继续处理下一个输入
- 如果完成扫描后U非空，那么就是出现了链接错误。
  如果为空，则合并和重定位E中的目标文件并进一步构建输出的可执行
  理想情况是E和U都空了

但是这种算法有一个明显的缺陷，就是命令行里面必须引用这个目标文件必须在这个库之前，否则就会链接失败

> 比如这里：
> ```bash
> $ gcc -static ./libvector.a main2.c
> ```
> 
>这里很明显，处理libvector时U是空的

那么因此一般的准则是把所有库放在命令的结尾，而如果库之间没有依赖关系，就可以以任意顺序放置在命令结尾，否则就需要排序，保证被引用的存档文件必须在后面
而实际上也可能出现循环依赖关系，这种时候要么加上选项`--start-group`，要么就满足依赖关系地写一遍：（当然，我们往往可以把这两个存档文件合并为一个存档）

```bash
$ gcc foo.c libx.a liby.a libx.a
```

> 练习7.3
>
> ```bash
> gcc p.o libx.a liby.a libx.a p.o
> ```

### 7.7 重定位

符号解析保证了引用和符号定义的关联，此时链接器确认了输入目标模块的代码节和数据节的具体大小，下一步就是重定位，先合并输入模块，并为每个符号分配运行时地址，重定位由2步组成：

1. **重定位节和符号定义**

   链接器将相同类型的节**合并为一个聚合节**，然后将运行时内存地址赋给这个新的聚合节（以及输入模块定义的每一个符号），结束时每条指令和全局变量都有唯一的运行时地址

2. **重定位节中的符号引用**

   修改代码节和数据节对每个符号的引用，保证他们指向正确的运行时地址，这一步链接器依赖于可重定位目标模块中的**重定位条目(relocation entry)**

#### 重定位条目

无论何时汇编器遇到对最终位置未知的目标引用，就会生成一个重定位条目，告诉链接器在将目标文件合并为可执行文件时如何修改此引用，而这就对应我们先前的`.rel.text`和`.rel.data`（分别对应代码和已初始化数据）

重定位条目的格式：

```c
typedef struct{
    long offset;		/*节的偏移*/
    long type: 32,		/*重定位类型（采用何种计算规则）*/
    	 symbol: 32;	/*被修改引用指向的符号*/
    long addend;		/*有符号常数，偏移调整*/
} Elf64_Rela;
```

而一共有32种type，这里我们只关注2种最基本的重定位类型：

- `R_X86_64_PC32`：重定位一个使用32位PC相对地址的引用，把PC相对地址加到PC上面
- `R_X86_64_32`：重定位一个32位绝对地址的引用

这两条支持的是x86-64小型代码模型，对应小于2GB的，再大就得使用`-mcmodel=medium`和`-mcmodel=large`来编译

#### 重定位符号引用

我们先展示一段重定位算法的伪代码：
```pseudocode
foreach section s{
	foreach relocation entry r {
		refptr = s + r.offset;		/*ptr to reference to be relocated*/
		if (r.type = R_X86_64_PC32){
			refaddr = ADDR(s) + r.offset;	/* the ref's runtime addr*/
			*refptr = (unsigned) (ADDR(r.symbol) + r.addend - refaddr);							/*PC跳转的相对量=引用指向的地址+偏移-引用本身的地址*/
		}
		if (r.type == R_X86_64_32)
			*refptr = (unsigned) (ADDR(r.symbol) + r.addend);
	}
}
```

它在每个节s和相关联的重定位条目r上迭代执行。
具体来说，每个节我们假设为一个字节数组，r则是类型为`Elf64_Rela`的结构，那么当算法运行时，链接器已经位每个节/符号选择了运行时地址`(ADDR(r.symbol))`

举个例子：（这里给出objdump-dx main.o产生的反汇编）
![image-20260801101044336](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260801101044336.png)
`main`引用了2个全局符号`array`/`sum`，为每个引用产生一个重定位条目在引用的后面一行上

> 一个可能会混淆的点：
> 我们决定引用的地址是在.rel部分描述的，因此不应该管这里命令里面的具体数字，它们仅仅是占位用的，在链接后会被替换

##### 重定位PC相对引用

`sum`定义在`sum.o`，call指令开始于节偏移0xe包括1字节操作码0xe8，后面跟的是对目标`sum`的32位PC相对引用的占位符
相应描述的重定位条目：

```pseudocode
r.offset = 0xf
r.symbol = sum
r.type = R_X86_64_PC32
r.addend = -4
```

现在假设链接器已经确定：`ADDR(s)=ADDR(.text)=0x4004d0`/`ADDR(r.symbol)=ADDR(sum)=0x4004e8`，那么使用上面那个算法，链接器首先计算出引用的运行时地址：`refaddr = ADDR(s)+r.offset = 0x4004d0 + 0xf = 0x4004df`，然后更新该引用使它运行时指向sum：*refptr = (unsigned)(ADDR(r.symbol)+r.addend -refaddr) = 0x5

而由于得到的可执行目标文件，`call`指令有重定位形式：
```assembly
callq 4004e8 <sum>  #sum()
```

那么执行时自然就是先把PC压栈然后把PC更新为pc+5

##### 重定位的绝对引用

这就简单多了，还是看那个代码，第4行`mov`把`array`地址复制到寄存器`%edi`，后面跟着的就是对`array`的绝对引用占位符

```pseudocode
r.offset = 0xa
r.symbol = array
r.type = R_X86_64_32
r.addend = 0
```

那么计算方式是一样的，我们假设ADDR(r.symbol) = ADDR(array) = 0x601018，那么那么*refptr = ADDR(r.symbol)，也就有了重定义形式：
```assembly
mov $0x601018, %edi
```

那么就可以得到最终可执行目标文件：
![image-20260801105808010](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260801105808010.png)

> 练习7.5 
>
> 考虑一目标文件：
> ```assembly
> callq e <main+0xe>	swap()
> 
> # 重定位条目
> r.offset = 0xa
> r.symbol = swap
> r.type = R_X86_64_PC32
> r.addend = -4
> ```
>
> 那么跳转的相对PC地址为：
> ADDR(r.symbol) + r.addend -(ADDR(s)+r.offset)



### 7.8 可执行目标文件

可执行目标文件文件形式：（和可重定位略有不同）
![image-20260801110826443](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260801110826443.png)

类似于可重定位，只是ELF头还包含了程序的**入口点(entry point)**，要执行的第一条指令的地址，而不同的在`.init`还定义了一个函数叫做`_init`，因为它已经完全链接所以不需要`.rel`节。

显然ELF文件设计本身就适合被加载到内存，连续的块chunk映射到连续的内存段，这由**程序头部表(program header table)**描述：

> OBJDUMP得到的头部表：
> ![image-20260801111823306](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260801111823306.png)
> 第1/2行告知第一个段具有读/执行权限，开始于0x400000，大小0x69c，它包含比如.init/.text/.rodata/程序头部表/ELF头
>
> 第3/4行告诉第二个段有读写访问权限，开始于地址0x600df8,大小0x230,从目标偏移0xdf8处开始的.data中0x228个字节初始化，剩下的8个字节对应于.bss

对任何段s,链接器必须选择一个起始地址`vaddr`，使得：(也就是要对齐（这是因为我们用了虚拟内存）)
```pseudocode
vaddr mod align = off mod align
```



### 7.9 加载可执行目标文件

当我们输入`$ ./prog`的时候，shell认为它是一个可执行文件，就会调用某个在存储器中的加载器`loader`的操作系统代码来运行它，当然任何linux程序都可以调用`execve`函数来调用加载器。
所谓加载就是把可执行目标文件从磁盘复制到内存，通过跳转到程序的入口点来运行
加载后，虚拟内存保证对每一个程序都有一个运行时内存映像，它的结构就无需赘述了
当加载器运行时，创建这样的内存映像，在程序头部表引导下，加载器将可执行文件的chunk复制到代码段和数据段，之后加载器把PC跳转到程序的入口点，即`_start`函数的地址，它在系统目标文件`ctrl.o`统一定义，它再调用系统启动函数`__libc_start_main`，它定义在`libc.so`，初始化执行环境，调用用户层的`main`并处理返回值，在需要时切换回内核态



### 7.10 动态链接共享库

静态库也有明显的缺点：

1. 和所有软件一样，它需要被维护
2. 很多功能几乎每个程序都需要使用，比如标准I/O函数，如果把这些代码对每个进程都复制一遍，这是对内存极大的浪费

而共享库(共享目标)就是为了补充这些缺陷，它是一个目标模块，在运行时可以加载到任意位置并和一个内存的程序链接起来，即动态链接，由动态链接器完成。
共享体现在2个层面：
首先对任何文件系统，一个库只有一个`.so`文件，因此所有引用它的可执行目标文件无需将其复制嵌入引用的可执行文件；
其次，内存中一个共享库的`.text`节的副本可以被多个进程共享

> 比如创建一个共享库`libvector.so：
> ```bash
> $ gcc -shared -fpic -o libvector.so addvec.c multvec.c
> ```
>
> 这里`-shared`选项即说明要构造一个共享库，而`-fpic`则说明生成的是与位置无关的代码，这样就可以链接了：（运行时可以直接链接libvector.so）
> ```bash
> $ gcc -o prog2l main2.c ./libvector.so
> ```

可执行文件中本身并没有真的复制相关的节，仅仅复制了重定位和符号表信息用于运行时对libvector.so的解析。
当加载器加载/运行可执行文件prog2l时，依旧先加载部分链接的可执行文件prog2l，然后就注意到其中的`.interp`节，它包含动态链接的路径名。
加载器此时不会把控制传递给应用，而是<u>先加载运行动态链接器</u>（当然<u>动态链接器本身也是一个共享目标(ld-linux.so)</u>），它会执行下面的重定位任务：

- 重定位`libc.so`的文本和数据到某个内存段
- 重定位`libvector.so`的文本和数据到另一个内存段
- 重定位prog2l中所有对前两者定义符号的引用

之后动态链接器才会把控制传递给应用，此时共享库的位置就固定了

### 在应用程序中加载和链接共享库

前面讨论的是应用加载后执行前的动态链接的加载。但是应用程序也可以在运行时让动态链接器进行加载/链接而无需在编译时链接。

> 动态链接的应用：
>
> - 分发软件：使用共享库来分发软件更新，用户只需要下载新的共享库版本，替换当前版本，下次运行就会自动链接加载新的共享库
> - 构建高性能Web服务器：比如生成动态内容，早期使用`fork`/`execve`创建子进程，在它的上下文运行CGI程序来生成内容。而现在的方法是把生成动态内容的函数打包放入共享库，一旦接收到Web请求它就会动态加载链接适当的函数进行调用，函数会一直缓存在服务器地址空间，这样就只需要函数调用一个开销就可以处理请求。而且无需停止服务器就可以更新已存在的函数

而Linux本身就提供了一个允许应用程序在运行时加载/链接共享库的接口
(dynamic link)

```c
#include <dlfcn.h>
void *dlopen(const char *filename, int flag);
/*成功则返回句柄的指针，失败返回NULL*/
// 选项：
// RTLD_LAZY: 当且仅当碰到被引用的符号被执行时才进行解析，会被环境变量覆写
// RTLD_NOW：立即解析所有对外部符号的引用（和LAZY至少有一个得存在）
```

`dlopen`函数加载链接共享库`filename`，用  [已经通过RTLD_GLOBAL选项打开的库]  解析`filename`中的外部符号，如果当前可执行文件是带`-rdynamic`选项编译的，那么它的全局符号对于符号解析也是可用的。

```c
#include <dlfcn.h>
void *dlsym(const char *handle, char *symbol);
/*返回符号的地址
成功则返回符号的指针，失败返回NULL*/
int dlclose(void *handle);
/*没有其他共享库使用这个共享库时就可以卸载
成功则返回0，失败返回-1*/
const char *dlerror(void);
/*前面有dlopen/dlsym/dlclose发生错误返回错误字符串，否则返回NULL*/
```

### 7.12 位置无关代码 PIC

我们发明共享库主要的目的就是想要<u>多个运行时的进程共享内存中相同库的代码</u>，以节约内存。
而想要实现这一点：
一种直白的方法就是直接给每个共享库分配一个预先准备好的专用地址空间片，要求加载器总是在这个地址加载共享库（但这会造成浪费且不好管理，因为不同库大小还不一样，修改了的话还要重新分配）；
显然这太蠢了，因此我们提出**位置无关代码(PIC- Position-Independent Code)**，<u>通过`-fpic`选项</u>指示GNU编译系统生成PIC代码，**<u>这是共享库编译必须的选项</u>**

#### PIC数据引用

因为无论我们加载到内存何处，**<u>数据段相对于代码段的偏移总是不变的</u>**，因此指令和变量之间的<u>偏移都是一个运行时常量</u>。
因此利用这一点，想要生成PIC的编译器就会在数据段开始的地方创建**<u>全局偏移量表(GOT - Global Offset Table)</u>**，每个被目标模块引用的全局数据目标都会有一个<u>8字节的地址条目</u>。
编译器还会为GOT的每个条目生成一个重定位记录，加载时动态链接器会重定位GOT的每个条目使之包含正确的绝对地址。
每个引用全局目标的目标模块都有自己的GOT。

> 示例`libvector.so`共享模块的GOT：
> ![image-20260801143159385](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260801143159385.png)
>
>
> 因为addcnt本身是`libvector.so`定义的，在同一个文件实际上完全不需要GOT使用相对PC地址就可以完成。不过由于C语言里面全局变量是有可能碰到`symbol interposition(符号介入)`的，所以还是选择了最通用的GOT来处理这个符号引用

#### PIC函数调用

调用一个共享库定义的函数，编译器没法预测它的运行时地址（因为共享库运行时可以加载到任意位置）。一般的方法是为该引用生成一条重定位记录，动态链接器在程序加载时对它解析，但这就不是PIC了，因为这需要链接器修改调用这个模块的代码片段。
GNU的解决方法是使用**lazy binding**，<u>**将过程地址的绑定推迟到过程首次被调用。**</u>这么做的动机是一个传统的应用只会调用库中很少部分的函数，那么函数地址的解析完全可推迟到它实际被调用的时候。这样第一次调用开销确实很大，但之后只有一条指令和间接寻址的开销。

而这一切通过两个数据结构的交互实现：（只要一个目标模块调用定义在共享库的函数，它就会有GOT和PLT）

- 过程链接表(PLT - Procedure Linkage Table)：

  一个数组，每个条目16字节代码，只要调用了库函数就会有它的PLT条目，每个条目都负责调用一个具体的函数。

  PLT[0]：跳转到动态链接器里面
  PLT[1]：调用系统启动函数`__libc_start_main`，它负责初始化执行环境，调用main并处理返回值
  从PLT[2]开始的条目是用户代码调用的函数

- 全局偏移量表(Global Offset Table)：

  和前面一样，还是一个8字节的地址条目，和PLT联合使用时：
  GOT[0]/GOT[1]包含动态链接器解析函数地址会用的信息
  GOT[2]是动态链接器在`ld-linux.so`模块的入口点。
  其余条目对应函数的调用，地址在运行时解析，每个条目都有匹配的PLT条目。



> 举例协同工作：
> 在addvec被首次调用时，延迟解析它的地址：
> ![image-20260801153414162](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260801153414162.png)
>
> 1. 不直接调用`addvec`，而是程序调用进入PLT[2]，即`addvec`的PLT条目
> 2. 第一条PLT指令通过GOT[4]间接跳转，显然初始化的时候我们GOT里面还不知道它对应的真实地址，所以默认GOT条目一开始指向的只能是它对应的PLT条目的下一条指令，换句话说第一次只能又跳回来
> 3. 此时我们把`addvec`的ID(0x1)（这个ID实际上是relocation index重定位表索引）压栈，从PLT[2]跳转到PLT[0]！
> 4. PLT[0]把一个动态链接器的参数通过GOT[1]间接压栈，然后通过GOT[2]间接跳转到动态链接器
>    而动态链接器使用两个栈条目来决定`addvec`的运行时地址，以此再覆写GOT[4]的地址，把控制移交给`addvec`
> 5. 之后再碰到外部调用，那么GOT会直接跳转到那个函数

也就是说整个过程是跳转进入动态链接器，它则会自动更新GOT对应的条目，这就完成了一次延迟解析： 首先运行时碰到调用一个外部的函数，先进入PLT对应的条目，而PLT条目第一条指令让PC先跳转到对应GOT条目写的地址，如果是初始状态并不清楚具体的运行时位置，因此默认GOT条目就指向对应PLT的下一条指令；而如果已经调用过那么直接跳转到GOT条目写的调用函数的内存位置即可。而下一条指令则把符号重定位表对应id压栈并跳转到PLT[0]统一处理符号解析，它首先把动态链接器的参数通过GOT[1]压栈，再通过GOT[2]跳转进入动态链接器，它则会自动更新GOT对应的条目，这就完成了一次延迟解析

### 7.13 库打桩机制

**库打桩(library interpositioning)**，允许截获对共享库函数的调用，用自己的代码取代。这不仅可以追踪对某个特定库函数的调用次数/验证追踪输入输出，还可以替换为一个完全不同的实现

**基本思想：**
对一个要打桩的目标函数，创建一个包装函数，其原型和目标函数一致，再利用机制就可以欺骗系统调用包装函数而非目标函数，一般来说包装函数会执行自己的逻辑，再调用目标函数，将目标函数的返回值传回调用者（也就是说对调用者来说加了一个中间层，从输入输出上来说似乎没有改变）

而打桩本身可以发生在编译/链接/加载/运行时，我们以一个统一的示例程序为例：
```c
/* int.c */
#include <stdio.h>
#include <malloc.h>
int main(){
  int *p = malloc(32);
  free(p);
  return 0;
}
```

##### 编译阶段的打桩：

```c
/* malloc.h */
#define malloc(size) mymalloc(size)
#define free(ptr) myfree(ptr)
void *mymalloc (size_t size);
void myfree (void *ptr);

/* mymalloc.c */
#ifdef COMPILETIME
#include <stdio.h>
#include <malloc.h>
/* 这里仅仅是加了个打印，从返回值和原型来说函数本身没改变 */
void *mymalloc(size_t size){
  void *ptr = malloc(size);
  printf("malloc(%d)=%p\n", (int)size, ptr);
  return ptr;
}
void myfree(void *ptr){
  free(ptr);
  printf("free(%p)\n", ptr);
}
#endif
```

我们可以这样：

##### 链接阶段的打桩：

```c
/*mymalloc.c*/
#ifdef LINKTIME
#include <stdio.h>

void *__real_malloc(size_t size);
void __real_free(void *ptr);
void *__wrap_malloc(size_t size){
  void *ptr = __real_malloc(size);
  printf("malloc(%d) = %p\n", (int)size, ptr);
  return ptr;
}

void __wrap_free(void *ptr){
  __real_free(ptr);
  printf("free(%p)\n",ptr);
}

#endif
```

那么编译：

```bash
$ gcc -DLINKTIME -c mymalloc.c

$ gcc -Wl,--wrap,malloc -Wl,--wrap,free -o intl int.o mymalloc.o
```

> gcc调用cc1编译，as汇编，ld链接。
> 这里`-Wl, xxxx`的作用就是把后面的内容传递给ld，也就是：
>
> ```bash
> ld --wrap malloc
> ```
>
> 而`--wrap`参数就是告诉ld寻找命名为`__wrap_func`来替代`func`，同时也需要定义`__real_func`作为原型以方便链接



##### 运行时的打桩

编译时的打桩需要程序源文件，而链接时的打桩需要对应的可重定位目标文件

而运行时打桩只需要访问可执行目标文件，基于动态链接器的`LD_PRELOAD`环境变量。
如果`LD_PRELOAD`环境变量被设置为一个共享库路径名的列表（以` `/`;`分隔），那么加载和执行一个程序需要解析未定义引用时，动态链接器会先搜索`LD_PRELOAD`库后再搜索其他库（也就是说加载和执行可执行目标文件时可以对任何共享库函数打桩，包括libc.so）

> 但是这里我同样的代码运行发生了段错误
> ```bash
> $ LD_PRELOAD="./mymalloc.so" ./intr
> 段错误 (核心已转储)
> ```
>
> 目前还没搞明白问题在哪里。。。
> 不过代码本身没有很复杂，先通过dlsym获取`malloc`/`free`的符号地址，然后通过符号本身进行调用函数（但是会不会因此发生循环调用？或许改名字好一点？）



### 7.14 处理目标文件的工具

- AR：创建静态库，插入/删除/列出/提取成员
- STRINGS：列出目标文件的所有可打印字符串
- STRIP：从目标文件删除符号表
- NM：列出一个目标文件的符号表定义的符号
- SIZE：列出目标文件节的名字和大小
- READELF：显示一个目标文件的完整结构，包括ELF头编码的信息（涵盖SIZE/NM的功能）
- OBJDUMP：反汇编`.text`节的指令
- LDD：列出一个可执行文件运行时的共享库



习题：

> 7.6 



### 总结一下：

想要链接，我们先需要有目标文件，分为可重定位目标文件/可执行目标文件和共享目标文件，对于所有`.elf`文件，都需要：elf头/`.data`/`.bss`/`.text`/`.rodata`/`.symtab`

而为了可以重定位，可重定位目标文件自然需要有专门的重定位条目，`.rel.data`/`.rel.text`

最基本的就是静态链接了，只做两件事：1. 符号解析 2.  重定位



## 八、异常控制流

异常控制流(Exceptional Control Flow ECF)，发生在各个层次。在硬件触发的事件会转移到异常处理程序，在操作系统层内核通过上下文切换将控制从一个用户进程转换到另一个用户进程；在应用层一个进程可以发送信号到另一个进程。

理解ECF的必要性：

- 操作系统本身就是一个异常事件驱动的状态机，I/O 进程 虚拟内存。。。都是基于这一点
- 应用程序通过trap/syscall的ECF形式向操作系统请求服务



### 8.1 异常

**异常(exception)**就是**控制流中的突变**，用于响应处理器状态中的某些变化。

当处理器状态中发生一个重要的变化时，处理器正在执行指令$I_{cur}$，状态被编码为不同的位和信号，状态变化被称为**事件(event)**

而一旦处理器检测到有事件发生，它就会通过**异常表(exceptional table)**，进行一个间接过程调用(即异常)，到一个专门用于处理这类事件的操作系统子程序（**异常处理程序 exception handler**），处理完成会产生3种情况：

- 处理程序把控制返还给当前指令$I_{cur}$
- 处理程序把控制返还給$I_{next}$，即没发生异常时将会执行的下一条指令
- 终止被中断的程序

#### 8.1.1 异常处理

系统给每种类型的异常都分配了一个唯一的非负整数**异常号(exception number)**

- 一部分由处理器设计者分配(包含零除、缺页、内存访问违例、断点和算术运算溢出)
- 一部分由操作系统内核分配(包含系统调用和来自外部IO设备的信号)

当系统启动的时候，OS会分配和初始化一张被称为**异常表**的跳转表，表目$k$包含异常$k$的处理程序的地址

在运行时，处理器检测到发生一个事件，并且确定了相应的异常号，随后处理器触发异常，执行间接过程调用，通过异常表的表目$k$转到相应的处理程序。异常号是异常表中的索引，异常表的起始地址放在**异常表基址寄存器(exception table base register)**当中

异常类似于过程调用，不同之处在于：

- 过程调用把返回地址压栈，**而异常返回地址只可能是下一条或者这一条指令**
- 处理器会把一些额外的寄存器状态压入栈中，因为在处理器返回时重新开始执行被中断的程序会**需要这些状态**，即**上下文**
- 控制从用户转向内核，则所有项目都会被压入内核栈而非用户栈
- 异常处理程序运行在内核模式下，对系统资源具有完全的访问权限



#### 8.1.2 异常的分类

只有interrupt是异步的，剩下都是同步，他们都是执行当前指令的结果，称为**故障指令(faulting instruction)**

| 类别          | 原因             | 同异步 | 返回行为     |
| ------------- | ---------------- | ------ | ------------ |
| 中断interrupt | I/O设备信号      | 异步   | 下一条       |
| 陷阱trap      | 有意的异常       | 同步   | 下一条       |
| 故障fault     | 潜在可恢复的错误 | 同步   | 可能当前指令 |
| 终止abort     | 不可恢复的错误   | 同步   | /            |

##### 中断interrupt

中断是异步发生的，来自处理器外部I/O设备的信号，与指令无关，对应的是**中断处理程序interrupt handler**
![image-20260802103625141](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260802103625141.png)

这可能来自磁盘驱动器/网络适配器/定时器芯片之类的，通过引脚拉高电平来将异常号放到系统总线触发中断

具体流程：

1. 当前指令完成，发现中断引脚电平拉高
2. 从系统总线读取异常号，调用对应的handler
3. 处理程序返回，控制移交下一条指令

##### 陷阱trap和系统调用syscall

**陷阱是有意的异常**，陷阱处理程序同样**将控制返回下一条指令**。

它的目的是在内核和用户程序之间提供一个类似过程的接口，叫做系统调用system call

具体来说，比如用户程序向内核请求服务：（read/fork/execve/exit），为了允许对内核服务的受控访问，处理器提供了syscall n指令（请求服务n），执行syscall会导致进入一个异常处理程序的trap，它解析函数并调用内核程序：
![](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260802104415232.png)
虽然从编写程序的角度似乎和过程一样，不同于过程在于它是工作在内核态而非用户态的（内核态允许系统执行特权指令/访问定义在内核的栈)



##### 故障 faults

故障由错误情况引起，同样会发生到故障处理程序的控制权的移交，但是返回有两种情况

- 处理程序能够修正这个错误情况：那么只需要把控制权返回引起故障的同一条指令(因为没有成功执行)
- 无法修正：返回内核的`abort`例程，终止引起故障的应用![image-20260802104809543](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260802104809543.png)

> 我们以缺页异常为例：
>
> 指令引用一个虚拟地址，而与该地址对应的物理页面不在内存中，因此需要从磁盘中取出，这就是故障。
> 因此调用缺页处理程序，它从磁盘加载对应的页面，然后再把控制移交回引起故障的指令，那么重新执行时对应的物理页面就已经在内存了



##### 终止 abort

不可恢复的致命错误(通常这来自硬件)，此时会直接把控制移交给abort例程，终止
![image-20260802105732712](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260802105732712.png)



#### 8.1.3 Linux x86-64系统的异常

共256种异常类型，0\~31由架构设计，32\~256由操作系统定义的中断和陷阱

| 异常号  | 描述         | 异常类别       |
| ------- | ------------ | -------------- |
| 0       | 除法错误     | fault          |
| 13      | 一般保护故障 | fault          |
| 14      | 缺页         | fault          |
| 18      | 机器检查     | abort          |
| 32\~256 | OS定义的异常 | interrupt/trap |

##### 1 Linux/x86-64 故障和终止

###### 除法错误 0

除零/除法指令结果溢出时，不会尝试恢复，而是往往直接移交给abort例程

一般会被作为`"Floating exceptions"`返回

###### 一般保护故障 13

许多原因都可能导致不为人知的一般保护故障，通常可能因为：

1. 程序引用了未定义的虚拟内存区域
2. 程序尝试向只读区域写入

同样Linux也不会尝试恢复这些故障，会被作为`"Segment fault"`返回

###### 缺页 14

处理程序会将适当的磁盘上虚拟内存的分页映射到物理内存的一个页面然后重新执行产生故障的指令

###### 机器检查 18

在导致故障的指令执行中碰到致命的硬件故障是发生，从不返回控制到应用程序

##### 2 linux/x86-64 系统调用

Linux有几百种系统调用，当应用程序请求内核服务时可以使用(read/write/fork)，每个系统调用都有一个专门的整数编号，对应于一个到内核跳转表的偏移量(注意这个跳转表可不是异常表)

> 早期的linux，`int 0x80`的确会先查询IDT再调用syscall()进入kernel
>
> 而现代为了降低开销实际上直接进入kernel的

虽然C程序通过`syscall()`函数可以直接调用任何系统调用，但是标准C库已经封装好了一组包装函数，会把参数打包到一起以适当的系统调用指令陷入内核

在x86-64系统上，系统调用是通过`syscall`这条trap指令来提供的，`%rax`包含返回值，如果为-4095\~-1代表发生错误，对应errno

| num  | name  | des    | num  | name   | des        |
| ---- | ----- | ------ | ---- | ------ | ---------- |
| 0    | read  | 读文件 | 33   | pause  |            |
| 1    | write | 写内存 | 37   | alarm  |            |
| 2    | open  |        | 39   | getpid | 获取pid    |
| 3    | close |        | 57   | fork   | 创建子进程 |
| 4    | stat  |        | 59   | execve | 加载新程序 |
| 9    | mmap  |        | 60   | _exit  |            |
| 12   | brk   |        | 61   | wait4  |            |
| 32   | dup2  |        | 62   | kill   |            |

> 我们以经典的hello为例：
>
> ```c
> int main(){
>     write(1, "hello, world\n", 13);
>     _exit(0);
> }
> ```
>
> 第一个参数指明I/O到stdout
>
> ```assembly
> .section .data
> string:
> 	.ascii "hello, world\n"
> string_end:
> 	.equ len, string_end - string
> .section .text
> .globl main
> main:
> 	# First, call write(1, "hello, world\n", 13)
> 	movq $1, %rax 		# write is system call 1
> 	movq $1, %rdi 		# Arg1: stdout has descriptor 1
> 	movq $string, %rsi 	# Arg2: hello world string
> 	movq $len, %rdx 	# Arg3: string length
> 	syscall 			# Make the system call
> 	# Next, call _exit(0)
> 	movq $60, %rax 	# _exit is system call 60
> 	movq $0, %rdi 	# Arg1: exit status is 0
> 	syscall 		# Make the system call
> ```
>
> 



### 8.2 进程

异常是允许OS提供进程概念的基本构造块

进程的经典定义是**<u>一个执行中程序的实例</u>**。
系统中的<u>每个程序都运行在某个进程的**上下文(context)**</u>中，**<u>上下文是由程序正确运行所需要的状态组成的</u>**。
这个状态包含：<u>存放在内存的代码/数据，栈/通用寄存器内容，PC，环境变量和打开文件描述符fd的集合</u>

每次用户向shell输入一个可执行目标文件的名字，运行程序时shell就会调用`execve`创建一个新的进程，在新进程的上下文运行这个可执行目标文件。应用程序也可以这么做

进程就是两个抽象：

- 一个独立的逻辑控制流
- 一个私有的地址空间

#### 8.2.1 逻辑控制流

进程对每个程序提供一种假象，好像它在独占处理器。如果使用调试器单步执行程序，会看到一系列的PC值，唯一地对应于包含在可执行目标文件的指令/运行时动态链接到程序的指令，这个PC值序列就是逻辑控制流

> 考虑一个运行着3进程的系统，处理器一个物理控制流被分为了三个逻辑流：

进程轮流使用处理器，每个进程执行它的流的一部分，然后被**抢占(preempted)**暂时挂起，再移交到其他进程。

#### 8.2.2 并发流

**并发流**指的是**<u>一个逻辑流的执行在时间上和另一个流重叠</u>**，它们就是并发地在运行。
而**<u>一个进程和其他进程轮流运行</u>**则称为**多任务。**一个进程执行它的控制流的一部分的每个时间段叫时间片，那么多任务也称时间分片(time slicing)

#### 8.2.3 私有地址空间

和私用地址空间里面相关联的内存字节是不能被其他进程读写的，结构还是之前那个结构



#### 8.2.4 用户态和内核态

处理器通过某个控制寄存器的**模式位**来限制一个应用可以执行的指令/访问的地址空间。设置了模式位进程就运行在内核态。

而未设置模式位就只能跑在用户态，此时无法执行特权指令(改变模式位/停止处理器/IO操作)，也不允许这样的进程直接引用地址空间中内核区域的代码/数据，这些只能通过系统调用接口间接地访问，也就是通过异常

Linux使用`/proc`文件系统，将内核数据结构内容输出为用户程序可以读的文本文件的层次结构，以此让用户模式的进程访问其内容。



#### 8.2.5 上下文切换

内核为每一个进程维持一个上下文，上下文就是内核重新启动一个被抢占的进程需要的状态。

而进程执行时，内核可以决定抢占当前的进程，重新开始一个被抢占的进程，这就是调度，通过内核的调度器来处理。

此时就需要上下文切换来转移控制：

1. 保存当前进程上下文
2. 恢复某个先前被抢占的进程被保存的上下文
3. 把控制传递给新恢复的进程

而内核代表用户执行系统调用时就可能发生上下文切换，如果系统调用因为等待事件而发生阻塞就可以这样，当然内核可以随时这么做

> 比如read读取需要很多时钟周期，此时就可以先运行另一个
> 而sleep系统调用则是显式地请求调用进程休眠

中断同样会触发上下文切换，比如定时器周期性触发中断就会让内核运行调度相关的例程进行切换

> 以磁盘读写为例：
> ![image-20260802130508607](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260802130508607.png)
>
> 进程A本身运行在用户态，而通过系统调用`read`陷入内核态，陷阱处理程序请求来自磁盘控制器的DMA传输，并且安排它在完成从磁盘到内存的数据传输后中断处理器。
> 而显然磁盘读取需要很多个时钟周期，因此从用户态陷入内核态的同时内核会执行从进程A到进程B的上下文切换。（从代表A变成代表B在用户态下执行指令）
> 进程B工作在用户态，碰到磁盘发出一个中断信号，表明数据已经缓存到了内存中，如果此时内核判定B已经执行足够长时间，则再次进行从B到A的上下文切换



### 8.3 系统调用错误处理

当Unix系统级函数碰到错误会返回-1，设置errno。

比如我们调用Unix fork：

```c
if ((pid = fork()) < 0){
    fprintf(stderr, "fork error: ", stderror(errno));
    exit(0);
}
```

但是这还是有些臃肿，那么统一用一个错误处理函数：
```c
void unix_error(char *msg){
    fprintf(stderr, msg, stderror(errno));
    exit(0);
}
/*usage*/
if ((pid = fork()) < 0)
    unix_error("fork error");
```

甚至可以通过使用错误处理包装函数进一步简化，一种方法比如对函数`foo`，定义一个有相同参数的包装函数`Foo`，包装函数调用基本函数/错误检查终止

```c
pid_t Fork(void){
    pid_t pid;
    if((pid = fork()) < 0)
        unix_error("Fork error");
    return pid;
}
```





### 8.4 进程控制

描述常用的Unix函数和使用

#### 8.4.1 获取进程ID

```c
#include <sys/types.h>
#include <unistd.h>

pid_t getpid(void);		// 返回调用进程的PID
pid_t getppid(void);	// 创建调用进程的进程/父进程的PID
/* 返回均为pid_t的整数值，linux的types.h定义为int */
```

#### 8.4.2 创建/终止进程(fork / exit)

##### 进程3种状态：(运行/停止/终止)

- **运行**：要么在处理器上执行，要么在等待被执行且最终会被内核调度

- **停止**：进程的行为被挂起(suspended)且不会被调度

  当收到**SIGSTOP/SIGTSTP/SIGTTIN/SIGTTOU**信号时进程停止，保持停止直到接收到**SIGCONT**

- **终止**：三种原因：

  1. 收到一个信号，其默认行为是终止进程
  2. 从主程序返回
  3. 调用`exit`

**exit**

以`status`退出状态终止进程，另一种设置退出状态的方法就是直接在主程序return这个数字

```c
#include <stdlib.h>
void exit(int status);
/* exit(0)等价于return 0;
*/
```

**fork**

父进程通过调用`fork`函数创建一个子进程：

```c
#include <sys/types.h>
#include <unistd.h>
pid_t fork(void);
/* 返回：子进程返回0，父进程返回子进程的PID，出错返回-1 */
```

子进程和父进程大体上相同：

- 得到父进程用户级虚拟空间相同且独立的一份副本（包含代码/数据段/堆/共享库/用户栈）
- 获得与父进程任何打开文件描述符相同的副本，也就是说父进程调用`fork`时子进程可以读写父进程打开的所有文件
- 最大的区别是PID

fork函数虽然被调用1次，却会返回2次：一次在**<u>父进程返回子进程PID</u>**，一次在<u>子进程返回0</u>（这是为了**<u>方便判断是在子进程还是父进程，因为进程PID非零</u>**）

> 举个例子：
> ```c
> #include <sys/types.h>
> #include <unistd.h>
> #include <stdlib.h>
> #include <stdio.h>
> #include <errno.h>
> #include <string.h>
> 
> pid_t Fork(){
>   pid_t pid;
>   if((pid = fork()) < 0){
>     fprintf(stderr, "fork error: %s", strerror(errno));
>   }
>   return pid;
> }
> int main(){
>   pid_t pid;
>   int x = 1;
>   pid = Fork();
>   if (pid == 0){
>     printf("child: x = %d\n", ++x);
>     x++;
>     exit(0);
>   }
>   printf("parent: x = %d\n", --x);
>   exit(0);
> }
> 
> ```
>
> 输出：
> ```bash
> $ ./fork
> parent: x = 0
> child: x = 2
> ```

这个简单的例子需要注意几点：

- 调用一次但是返回两次

- 并发执行，父进程和子进程是并发运行的独立进程，内核可以任意方式交替运行，因此不能假设哪个先完成

- 相同且独立的地址空间

  这两个进程有相同的地址空间，每个进程有相同的用户栈和本地变量值/堆/全局变量值和代码。

  >  也就是说**两个进程都可能执行fork之后的代码**，只是fork内部的内容是子进程独有的，但是我们这里只是`exit`提前退出了，如果不退出输出就会是：
  > ```bash
  > $ ./fork
  > parent: x = 0
  > child: x = 2
  > parent: x = 2
  > ```

  但是这两个进程的地址空间本身是独立的，也就是说它们做的改变是互不影响的

- 共享文件

  父进程和子进程都把输出放到stdout里面了，因为子进程继承了父进程打开的所有文件，当父进程调用`fork`时stdout已经打开，所以子进程同样指向这个输出



#### 8.4.3 回收子进程(waitpid)

一个子进程最后要么被信号停止，要么自身终止

一个进程终止时，内核不直接将其从系统清除，进程仅仅保持已终止的状态，此时被称为**僵死进程(zombie)**，直到被它的父进程**回收(reaped)**
回收时：内核把子进程的退出状态传递给父进程，然后抛弃已终止的进程，它就不存在了

但是如果父进程比子进程提前结束，内核就会安排`init`作为它的孤儿进程的养父，`init`进程的PID为1，由操作系统启动时在内核创建，它不会终止，是所有进程的祖先。

而我们接下来介绍的3个函数本质都是等待一个子进程的变化

**waitpid**

当然一个进程可以通过`waitpid`来**等待**子进程的停止/终止：（默认情况下是要等到结束才行，没有僵死进程就卡在那里）

(主要用于回收子进程和判断回收状态，不wait的话就是会有僵死进程)

```c
#include <sys/types.h>
#include <sys/wait.h>
pid_t waitpid(pid_t pid, int *statusp, int options);
/* 返回：成功为子进程的PID，WNOHANG时为0，其他错误为-1 
参数：	pid： 子进程pid
	  *statusp：子进程返回信息放在哪
	  options：选项*/
```

默认情况下(options = 0)，`waitpid`挂起调用进程的执行，<u>直到它的等待集合中的一个子进程终止</u>。此时**<u>直接返回其PID并且其被回收，删除所有痕迹</u>**

1.  **判定等待集合的成员**：

   由参数pid决定：

   - pid > 0：
     代表等待集合是一个单独的子进程，其PID等于pid
   - pid = -1：
     代表等待集合是所有父进程的子进程组成

   当然还支持别的类型的等待集合

2. **修改默认行为**：

   设置options为三种状态的组合来修改默认行为：

   - W<u>NOHANG</u>：如果等待集合里面没有已经终止的子进程，立即返回0。（主要用于在等待子进程时做别的工作）
   - W<u>UNTRACED</u>：挂起调用进程的执行，直到等待集合中的一个进程被停止/已终止，返回的PID为导致返回的那个进程的PID。（用于检查已终止/被停止的子进程）
   - WCONTINUED：挂起调用进程的执行，直到<u>等待集合中一个正在运行的终止</u>/<u>等待集合中一个被停止的进程收到SIGCONT信号重新开始执行</u>

   你可以把它们组合起来使用，比如`WNOHANG | WUNTRACED`

3. **检查已回收子进程的退出状态**：

   如果`statusp`非空，那么`waitpid`就会在那里放上关于导致返回的子进程的状态信息。`wait.h`定义了几个宏来解析`status`参数：

   - WIFEXITED(status)：如果子进程通过调用`exit`/一个`return`返回，则返回真
   - WEXITSTATUS(status)：返回一个正常终止的子进程的退出状态，只有WIFEXITED()返回真时才会定义它
   - WIFSGNALED(status)：如果子进程是因为一个未被捕获的信号终止的，返回真
   - WTERMSIG：返回导致子进程终止的信号的编号，同样需要WIFSGNALED()为真
   - WIFSTOPPED(status)：引起返回的子进程是停止的则为真
   - WSTOPSIG(status)：返回引起子进程停止的信号编号，需要WIFSTOPPED()为真
   - WIFCONTINUED(status)：子进程收到SIGCONT信号重新启动返回真

4. **错误条件**

   如果调用进程没有子进程，那么`waitpid`返回-1，设置errno为ECHILD
   如果`waitpid`被一个信号中断，返回-1，设置errno为EINTR

5. wait函数：

   就是`waitpid`的简化版本，等价于调用`waitpid(-1, &status, 0)`：
   ```c
   #include <sys/types.h>
   #include <sys/wait.h>
   pid_t wait(int *statusp);
   ```

6. 示例：



#### 8.4.4 让进程休眠(sleep /pause)

```c
#include <unistd.h>
unsigned int sleep(unsigned int secs);
// 把一个进程挂起一段指定时间
// 返回还要休眠的秒数
int pause(void);
// 让调用函数休眠 until 该进程接受到一个信号产生了行为
//
// 返回-1
```

**注意**！`pause`并不是看到信号本身的`pending`，而是说信号产生了对应的动作，在官方说明里面是：
![image-20260812195113144](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260812195113144.png)

<u>换言之**没有行为的信号是不会唤醒它的，必须改变控制流**</u>

> 练习8.5 
>
> 编写一个sleep的包装函数，多打印一条描述进程实际休眠的时间：
> ```c
> void snooze(unsigned int secs){
>     unsigned int left_secs = secs - sleep(secs);
>     printf("Slept for %d of %d secs\n", left_secs, secs);
> }
> ```



#### 8.4.5 加载并运行程序(execve / getenv / setenv)

`execve`函数在当前进程的上下文加载并运行一个新程序：
它一次调用不返回

```c
#include <unistd.h>
int execve(const char *filename, const char *argv[], const char *envp[]);
// 仅失败时返回-1，成功则不返回
```

此函数加载并运行可执行文件`filename`，参数列表`argv`和环境变量列表`envp`（均以NULL结尾的指针数组），其中环境参数列表格式应该为`name=value`对
![image-20260802154008127](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260802154008127.png)

在`execve`加载了`filename`后，调用start-up代码，建立栈并且把控制移交给新的程序的主例程，也就是所谓的`int main(int argc, char **argv[], char**envp);`

而main开始执行时**，用户栈**如下：（从栈底看）
![image-20260802154414122](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260802154414122.png)

- 最底部是以null结尾的环境变量/命令行字符串们，往上看则是以null结尾的指针数组，每个指针都指向栈中的一个环境变量字符串，而全局变量`environ`指向这些指针中的第一个`envp[0]`，紧接着环境变量数组后的就是以null结尾的参数变量指针数组，栈顶则是系统启动函数`libc_start_main`的栈帧

  > 这么设计原因：
  > 字符串长度不一致，而且也不连续，但是地址长度统一且连续放置，否则读取参数太麻烦

而`main`有3个参数：argc - argv[]非空指针数量，argv[]， envp[]

Linux提供操作环境数组的函数：

##### getenv/setenv

```c
#include <stdlib.h>
char *getenv(const char *name);
// 找名为name的环境变量，返回地址，没有为NULL
int setenv(const char *name, const char* newvalue, int overwrite);
// 添加一条环境变量。如果开了overwrite=1,会覆写已存在的name相同的
void unsetenv(const char *name);
// 删除这条环境变量
```

> 应该区分一下fork和execve：
>
> 程序是目标文件，存在磁盘上或作为段存在于地址空间，运行在某个进程的上下文中；而进程则是程序中一个具体的实例，**进程 = 执行流(线程/上下文)+内核资源+地址空间**；
>
> fork干的事情是在新的子进程里面运行完全相同的程序，**子进程只是父进程的一个复制品**（唯一能区分的就是PID了）
>
> 而execve在当前进程的上下文中加载并运行一个新的程序，它会覆盖当前进程的**用户态地址空间（内核态不涉及！！）**整个重新初始化一下，但是还是原来那个进程，原来那个PID。（也就是说它用一个新的程序来替代了旧的程序，但是这个进程本身不变，瓶子不变但装了新的东西）
>
> 但是这两个无论如何**都会保留原先已经打开的文件描述符fd**，因为它是保存在内核空间里面的



> 练习8.6
>
> 打印环境变量和参数
>
> ```c
> #include <stdlib.h>
> #include <stdio.h>
> int main(int argc, char **argv, char **envp){
>   printf("Commadline arguments:\n");
>   for (int i = 0; i < argc; i++){
>     printf("argv[%-2d]:%s\n", i, argv[i]);
>   }
>   printf("Environment variables:\n");
>   int i = 0;
>   for(char **tmp = envp; *tmp != NULL; tmp++){
>     printf("envp[%-2d]:%s\n", i++, *tmp);
>   }
>   exit(0);
> }
> 
> ```

#### 8.4.6 利用fork和execve运行程序

像Unix shell和Web服务器这样的应用大量使用了`fork`/`execve`这样的函数，shell是一个交互型应用程序，代表用户运行其他程序（$sh\to csh/tcsh/ksh/bash$），它执行一系列的读/求值步骤，然后终止。
读步骤来自用户的命令行，求值步骤解析命令行，并且代表用户运行程序，下面是一个简单shell的例程：

```c
#include "csapp.h"
#define MAXARGS 128

void eval(char *cmdline);
int parseline(char *buf, char **argv);
int builtin_command(char **argv);

int main(){
    char cmdline[MAXLINE];
    while(1){
        printf("> ");
        Fgets(cmdline, MAXLINE, stdin);
        if (feof(stdin))
            exit(0);
        
        eval(cmdline);
    }
}
```

我们再来看一下具体是如何求值的：

```c
void eval(char *cmdline){
    char *argv[MAXARGS];
    char buf[MAXLINE];
    int bg;
    pid_t pid;
    
    strcpy(buf, cmdline);
    bg = parseline(buf, argv);	// 先分割
    if (argv[0] == NULL)		// 空
        return ;
    
    if (!builtin_command(argv)){	//  不是内部指令
        if ((pid = Fork()) == 0){	// 子进程跑用户的程序
            if (execve(argv[0], argv, environ) < 0){
                printf("%s: Command not found.\n", argv[0]);
                exit(0);
            }
        }
        if(!bg){
            int status;
            if (waitpid(pid, &status, 0) < 0)	//保证子进程正常结束
                unix_error("waitfg: waitpid error");
        }else
            printf("%d %s", pid, cmdline);
    }
    return ;
}
int builtin_command(char **argv){
    if (!strcmp(argv[0], "quit"))
        exit(0);
    if (!strcmp(argv[0], "&"))
        return 1;
    return 0;
}
int parseline(char *buf, char **argv){
    
}
```

这个shell的缺陷在与它不回收它后台的子进程，我们因此需要引入信号来干这件事。

### 8.5 信号

目前位置我们已经了解过硬件和软件合作提供的基本异常机制，以及OS利用异常进行上下文切换的异常控制流形式。

下面我们介绍一种更高层的软件形式的异常，称为**信号(signal)**，你可以认为它是一种**软中断(有同步也有异步)**，**<u>允许内核和进程中断其他进程</u>**。

一条信号就是一条小消息，通知进程系统发生了某种类型事件

每种信号都对应某种系统事件，低层次的硬件异常由内核异常处理程序处理，一般来说对用户进程不可见。而**<u>信号提供的机制可以通知用户进程发生这些异常</u>**。

> 你可以用`kill`工具来发送信号，它自然也可以用来查看，如：
> ```bash
> kill -l
> ```
>
> ![image-20260803115816587](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260803115816587.png)
> 显然64个，恰好是64位，因为**信号就是用bitmap来表示的**，这样方便我们快速地处理

> ![image-20260803120520458](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260803120520458.png)
> 例如：一个进程试图除零，那么内核就会发送给它一个SIGFPE(8)；如果一个进程执行一条非法指令，内核会发送SIGILL(11)；非法内存引用，发送SIGSEGV；
> 而其他则对应内核/其他用户进程中高层软件事件，如进程运行在前台，键入`^C`那么内核就会发送一个SIGINT信号给这个前台进程组的每个进程；一个进程可以通过向另一个进程发送一个SIGKILL信号来强制终止它；当一个子进程终止时，内核会发送一个SIGCHLD给父进程



#### 信号术语

一个信号的传送分为2个步骤：

- **发送信号：**

  内核通过更新目的进程上下文的某个状态来发送一个信号给目的进程，发送信号有2种原因：

  1. **<u>内核检测到一个系统事件</u>**
  2. **<u>一个进程调用了`kill`函数</u>**，显式要求内核发送一个信号给目的进程（可以是自己）

- **接收信号：**

  **<u>目的进程被内核强迫以某种方式对信号的发送做出反应</u>**

  进程可以：
  
  1. 忽略这个信号
  2. 终止
  3. 执行signal handler的用户层函数捕获此信号
  
  ![image-20260805104049804](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260805104049804.png)

而一个被发出还没有被接收的信号称为**待处理信号**。
任何时候，一种类型至多有1个待处理信号。比如一个进程如果已经有一个类型为$k$的待处理信号，那么接下来所有发送到此进程类型为k的信号都不会排队等待，只会被简单丢弃。
一个进程可以有选择性地**阻塞**接收某种信号
一个待处理信号最多只能被接收1次:内核为每个进程在`pending`位向量中维护待处理信号的集合，在<u>**`block`位向量**</u>中维护这被阻塞的信号集合，只要传送率一个类型为k的信号，内核就会在`pending`中设置k位，只要接收了一个类型为k的信号就会清除它

#### 发送信号

Unix系统提供了大量的向进程发送信号的机制，所有机制都基于**进程组(process group)**这个概念。

##### 1 进程组(getpgrp / setpgid)

每个进程只属于一个进程组，由一个<u>正整数进程组ID</u>标识。
`getpgrp`函数返回当前进程的进程组ID

```c
#include <unistd.h>
pid_t getpgrp(void);
/* 返回：调用进程的进程组ID */
```

默认地，**<u>一个子进程和它的父进程同属于一个进程组</u>**，一个进程可以通过使用`setpgid`改变自己或其他进程的进程组：
```c
#include <unistd.h>
int setpgid(pid_t pid, pid_t pgid);
```

`setpid`函数**<u>把进程`pid`的进程组改为`pgid`</u>**：
如果`pid`为0那么就是用当前进程的PID；
如果`pgid`是0那么就用`pid`指定的进程的PID作为进程组ID

> 如进程1234调用`setpgid(0, 0);`就创建一个新的进程组，进程组ID为1234，然后把进程1234加入此进程组

##### 2 /bin/kill 程序发送信号

此程序可以发送任意信号，如下面就是向进程1234发送信号9(SIGKILL)：

```bash
/bin/kill -9 1234
```

##### 3 从键盘发送信号

Unix shell使用**作业(job)**这个抽象的概念标识<u>对一条命令行求值而创建的进程</u>
<u>**任何时候最多只有1个前台进程和若干个后台进程</u>**

>比如当我们键入：
>
>```bash
>ls | sort
>```
>
>会创建一个由2个进程组成的前台作业，它们通过Unix管道连接起来，一个运行`ls`一个运行`sort`。

shell为每个作业创建一个独立的进程组，进程组ID通常取自作业中父进程中的一个：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260805205450238.png" alt="image-20260805205450238" style="zoom:60%;" />

键盘上输入`Ctrl + C`使得内核发送一个`SIGINT`信号到前台进程组的每一个进程，默认情况下结果是终止前台作业。
而`Ctrl + Z`则是发送`SIGTSTP`信号到前台进程组的每个进程，默认情况结果是停止前台作业。

##### 4 用kill()发送信号

```c
#include <sys/types.h>
#include <signal.h>
int kill(pid_t pid, int sig);
/* 成功返回0,错误返回-1 */
```

- 如果`pid > 0`，那么`kill`会发送`sig`信号给进程`pid`
- 如果`pid = 0`，那么`kill`会发送信号`sig`给**<u>调用进程所在进程组</u>**的每个进程(包括调用者自身)
- 如果`pid < 0`，`kill`会发送`sig`给进程组`-pid`的每个进程

> 比如下面就是
> ```c
> #include "csapp.h"
> 
> int main(){
>     pid_t pid;
>     if((pid = Fork()) == 0) {	// child
>         Pause();				// wait for a signal to arrive
>         printf("control should never reach here");
>         exit(0);
>     }
>     Kill(pid, SIGKILL);
>     exit(0);
> }
> ```
>
> 





##### 5 用alarm()发送信号

在`secs`秒后向自己发送`SIGALRM`信号：
```c
#include <unistd.h>
unsigned int alarm(unsigned int secs);
/* 返回前一次闹钟剩余的秒数，没有则返回0 */
```

在任何情况下对`alarm`的调用都会取消任何待处理的(pending)闹钟



#### 8.5.3 接收信号

当内核把进程`p`从内核态切换到用户态，会检查进程`p`的**待处理信号集合**(pending & ~blocked)。如果为空，那么自然就把控制移交给p的逻辑控制流的$I_{next}$。

而如果非空，那么内核选择集合其中一个信号`k`让进程`p`接收，触发进程采取特定行为，一旦行为完成，那么控制还是会移交回`p`的$I_{next}$。

每个信号类型都有一个**预定义的默认行为**：

- **进程终止**
- **进程终止并转储内存**
- **进程停止直至被SIGCONT信号重启**
- **进程忽略该信号**

##### signal函数

进程可以通过`signal`修改和信号相关联的默认行为（除了SIGSTOP/SIGKILL）：
```c
#include <signal.h>
typedef void (*sighandler_t)(int);
sighandler_t signal(int signum, sighandler_t handler);
/* 成功返回指向前次处理程序的指针，
   出错为SIG_ERR，不会设置errno */
```

`signal`函数可以通过下列3种方法之一改变和信号`signum`关联的行为：

- `handler`是SIG_IGN，则需要忽略`signum`对应的信号

- `handler`是SIG_DFL，则把`signum`对应的信号行为恢复为默认行为

- 其余：将信号`signum`的行为设置函数`handler`信号处理程序(installing the handler)。

  调用信号处理程序就是所谓**捕获信号**，而执行处理程序就是**处理信号**

而具体来说，当一个进程捕获一个类型为`k`的信号时，调用为它设置的处理程序，一个整数参数被设置为k，这个参数运行同一个处理函数捕获不同类型的信号

当处理程序执行它的return语句时，<u>控制通常会移交回控制流中进程被信号接受中断位置处的指令</u>（当然某些系统里面被中断的系统调用是返回错误）

> 比如我们想要把键盘终止的行为修改为输出一条消息：
> ```c
> #include "csapp.h"
> 
> void sigint_handler(int sig){
>   printf("Caught SIGINT!\n");
>   exit(0);
> }
> 
> int main(){
>   if(signal(SIGINT, sigint_handler) == SIG_ERR)    // 
>     unix_error("signal error");
>   pause();
>   return 0;
> 
>   
> }
> 
> ```



> 练习8.7 
>
> 还是编写snooze，通过命令行参数调用snooze函数，然后终止，并且它可以被键盘中断
>
> ```c
> #include <csapp.h>
> 
> unsigned int total_secs = 0;
> unsigned int left_secs = 0;
> 
> unsigned int snooze(unsigned int secs){
>     unsigned int left_secs = sleep(secs);
>     printf("Slept for %d of %d secs.\n", secs - left_secs, secs);
>     return left_secs;
> }
> 
> void sigint_handler(){
>   printf("Slept for %d of %d secs.\n", total_secs - left_secs, total_secs);
>   exit(0);
> }
> 
> int main(int argc, char **argv){
>   if(argc != 2){
>     printf("wrong usage...\n");
>     exit(0);
>   }
>   total_secs = atoi(argv[1]);
>   if(signal(SIGINT, sigint_handler) == SIG_ERR)
>     unix_error("signal error");
>   snooze(total_secs);
>   return 0;
>   
> }
> ```
>
> 



#### 8.5.4 阻塞和解除阻塞信号

**隐式阻塞机制（相同的不接受）**：内核默认在阻塞任何处理程序正在处理相同类型的待处理信号

**显式阻塞机制**：应用程序使用`sigprocmask`函数和它的辅助函数明确地阻塞/解除阻塞信号

```c
#include <signal.h>
int sigprocmask(int how, const sigset_t *set, sigset_t *oldset);
int sigemptyset(sigset_t *set);
int sigfillset(sigset_t *set);
int sigaddset(sigset_t *set, int signum);
int sigdelset(sigset_t *set, int signum);
/* 成功0,失败-1 */
int sigismember(const sigset_t)
/* signum为set成员1,不是0,出错-1 */
```

1 . `sigprocmask` 会改变当前阻塞信号的集合（`blocked` 位向量），具体行为依赖于 `how`：

- SIG_BLOCK：`blocked = blocked | set`
- SIG_UNBLOCK：`blocked = blocked & ~set`
- SIG_SETMASK：`block = set`

如果`*oldset`非空， `blocked`之前的值保存在`oldset`里面

2 . `sigemptyset`初始化为空集
3 . `sigfillset`把set填满
4 . `sigaddset`把`signum`加入`set`
5 . `sigdelset`从`set`删除`signum`
6 . `sigismember`返回`signum`是否在`set`内

> 比如用sigprocmask屏蔽SIGINT：
> ```c
> sigset_t mask, prev_mask;
> Sigemptyset(&mask);
> Sigaddset(&mask, SIGINT);
> // block SIGINT
> Sigprocmask(SIG_BLOCK, &mask, &prev_mask);
> // unblock SIGINT
> Sigprocmask(SIG_SETMASK, &prev_mask, NULL);
> ```



#### 8.5.5 信号处理程序

处理程序有几个棘手的问题：

- 处理程序和主程序/其他信号处理程序都是并发存在的逻辑执行流，共享相同的全局变量，因此会出现相互干扰，你没法预测它们的顺序
- 如何/何时接收信号的规则是反直觉的
- 不同系统有不同的信号处理语义

> 不过这里书上比较有意思，虽然我们还是单线程的，但是从控制流的角度只要发生信号处理的异常就会有上下文切换而有控制流的改变，因此我们可以当它是并发的

##### 1 安全的信号处理(5条原则 & 异步信号安全的函数)

信号处理最麻烦的就在于它会，因为全局数据结构会被并发地访问，结果是不可预测的，因此我们给出一些保守的原则：

- G0. **处理程序要尽可能简单**

  （如只设置全局标志，所有与接收信号相关的处理部分都放到主程序执行，它来周期性检查标志）

- G1. **在处理程序中只调用异步信号安全的函数**
  
  （原因：要么是**<u>可重入的</u>**（也就是它不依赖共享的变量），要么是**<u>不能被信号程序打断的</u>**），如下表为Linux保证安全的系统级函数：
  ![image-20260808205101841](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260808205101841.png)

  > 当然你其实可以通过`man 7 signal-safety`来快速查看
  
  那么信号处理程序中产生输出唯一安全的方法是使用`write`函数（而`printf`/`sprintf`是不安全的）
  
  > 为了方便我们这里写了用来在信号处理程序里面打印信息的函数：
  > 我们已知`write`的原型：
  >
  > ```c
  >     ssize_t write(int fd, const void buf[.count], size_t count);
  > ```
  >
  > 那么我们想要写两个安全的IO函数就简单了：(不过这里问题是我们常用的标准库函数都不是异步信号安全的)
  > ```c
  > #include "csapp.h"
  > ssize_t sio_puts(char s[]){
  >  return write(STDOUT_FILEND, s, sio_strlen(s));
  > }
  > ssize_t sio_putl(long v){
  > 	char s[128];
  >     sio_ltoa(v, s, 10);
  >     return sio_puts(s);
  > }
  > void sio_error(char s[]){
  >     sio_puts(s);
  >     _exit(1);			// 立刻退出而非清理空间后退出
  > }
  > ```
  >
  > 就像我们之前写的哪个SIGINT的处理程序，那么他的安全版本就是：
  > ```c
  > void sigint_handler(int sig){
  >     Sio_puts("Caught SIGINT\n");
  >     _exit(0);
  > }
  > ```
  >
  > 
  
- G2. **保存和恢复`errno`**

  具体来说，许多的Linux异步信号安全的函数都会在出错返回时设置`errno`，但是显然这会干扰主程序里面其他依赖于`errno`的部分。那么我们解决方法就是设置一个局部变量来保存`errno`，退出时再恢复它（当然了如果你直接`_exit`的话就没必要了）

- G3. **阻塞所有信号，保护对共享全局数据结构的访问**

  如果和 主程序/其他处理程序 共享一个全局数据结构，那么访问此数据结构时，该处理程序和全局程序都需要暂时阻塞所有信号。

  原因是我们访问数据结构`d`时一定需要一系列的指令，而<u>如果此指令序列被打断</u>，那么就会出现<u>`d`的状态不一致</u>，得到不可预知的结果

- G4. **用`volatile`声明全局变量**

  这个问题主要是来源于编译器优化：
  假如我们 处理程序 和 主程序 共用一个全局变量`g`（比如一个flag），处理程序更新`g`，而主程序仅仅周期性读取`g`，那么优化编译器就会认为`main`里面的`g`从来没有变过，那么自然他就会用缓存在寄存器中`g`的副本来满足对`g`的每次引用。但是显然这样`main`函数就没法看到真正的改变了。

  **<u>那么使用`volatile`关键字，就是告诉编译器不要缓存这个变量，必须每次都从内存读取`g`的值</u>**。

  当然别忘了，还是要屏蔽所有其他信号的

- G5. **用`sig_atomic_t`声明标志**

  常见的处理程序会写全局标志记录信号的接收，主程序周期性读取/响应/清除标志。
  C提供整型变量`sig_atomic_t`，**<u>保证对它的读写是原子的（不可打断）</u>**

  结合上一条，那么就是：
  ```c
  volatile sig_atomic_t flag;
  ```

  正因为不可中断，所以我们可以直接安全地读写而无需阻塞信号

  > 我们这里保证“原子性”指的是写成汇编的单条指令，你要是写比如`flag++`显然是多条指令的。。。



##### 2 正确的信号处理

信号反直觉的就在于它们并没有排队，毕竟我们用的是bitmap，`pending`/`block`向量都只有1位代表1个信号。那么如果两个相同类型信号`k`发送给一个目的进程，如果正在执行`k`的处理程序，那么自然它就被阻塞了，直接丢掉第二个信号（也就是说存在一个未处理信号只代表至少有一个）

> 一个简单的例子：
>
> 基本结构是父进程创建一些子进程，它们各自独立运行一段时间然后终止，父进程必须回收子进程来避免在操作系统留下僵死进程，但同时在子进程运行时父进程是自由的，那么就决定使用SIGCHLD作为处理程序入口来回收子程序
> 下面是第一版（它有缺陷，因为它假设信号是排队的）
>
> ```c
> void handler1(int sig){
>  int olderrno = errno;
>  if ((waitpid(-1, NULL, 0)) < 0)	// waitpid回收一个已经结束的进程
>      sio_error("waitpid error");
>  Sio_puts("Handler reaped child\n");
>  Sleep(1);
>  errno = olderrno;
> }
> int main(){
>  int i, n;
>  char buf[MAXBUF];
>  if (signal(SIGCHLD, handler1) == SIG_ERR)
>      unix_error("signal error");
>  for (i = 0; i < 3; i++){
>      if (Fork() == 0){	// child
>          printf("Hello from child %d\n", (int)getpid());
>          exit(0);
>      }
>  }
>  if ((n = read(STDIN_FILENO, buf, sizeof(buf))) < 0)
>      unix_error("read");
>  printf("Parrent processing input...(fake)\n");
>  while(1);
>  exit(0);
> }
> ```
>
> 那么我们依旧运行一下看看：
> ```c
> $ ./signal_handler
> Hello from child 0
> Hello from child 1
> Hello from child 2
> Handler reaped child
> Handler reaped child
> cv
> Parrent processing input...(fake)
> ```
>
> 我们结合`ps`提供的进程快照来看看是怎么回事：
> ```bash
> $ ./signal_handler
> Hello from child 29190
> Hello from child 29191
> Hello from child 29192
> Handler reaped child
> Handler reaped child
> ^Z
> [2]+  已停止               ./signal_handler
> $ ps t
>  PID TTY      STAT   TIME COMMAND
> 24419 pts/4    Ss     0:00 bash
> 29189 pts/4    T      0:00 ./signal_handler
> 29192 pts/4    Z      0:00 [signal_handler] <defunct>
> 29212 pts/4    R+     0:00 ps t
> ```
>
> 很显然，这里child 3没有成功进入信号处理程序，没有成功回收。
>
> 
>
> **原因：**
>
> 处理程序还在处理第一个信号时，第二个信号就已经传送并添加到了待处理额定信号集合，此时由于正在处理SIGCHLD，那么第二个信号此时就被阻塞了放在`pending`里面待处理，而马上第三个信号又到达了，此时由于第二个信号已经置位`pending`了，那么第三个信号就会被丢弃
> 
>
> 那么就像我们刚才说的，**<u>这个程序最大的问题是：把信号理解为一个消息队列，但实际上这个信号模型更像一个状态机</u>**，`pending`里面有信号待处理只代表说发生了这件事情，你必须假设有若干个事件才可能保证完全处理
>
> **<u>我们可以得到教训：不可以用信号来对其他进程中发生的事件计数</u>**
>
> 比如这个案例，如果我们要修改的话可以改为：
> ```c
> void handler2(int sig){
>     int olderrno = errno;
>     int waiting = 
>     while(waitpid(-1, NULL, 0) > 0){
>         Sio_puts("Handler reaped child\n");
>     }
>     if (errno != ECHILD)
>         Sio_error("waitpid error");
>     Sleep(1);
>     errno = olderrno;
> }
> ```



> 练习8.8 脑测一下这个程序，输出什么？
>
> ```c
> volatile long counter = 2;
> 
> void handler1(int sig){
>     sigset_t mask, prev_mask;
> 	Sigfillset(&mask);							// all signal
> 	Sigprocmask(SIG_BL0CK, &mask, &prev_mask); /* Block sigs */
> 	Sio_putl(--counter);
> 	Sigprocmask(SIG_SETMASK, &prev_mask, NULL); /* Restore sigs */
> 	_exit(0);									// exit without cleaning usr space
> }
> int main(){
>     pid_t pid;
>     sigset_t mask, prev_mask;
> 
> 	printf("%ld", counter);
> 	fflush(stdout);
> 
> 	signal(SIGUSR1, handlerl);					// bind the user defined signal
> 	if ((pid = Fork()) == 0) {					// for children, they just stay here until receiving signal
>         while(1);
>     }
>     Kill(pid, SIGUSR1);							// for parent, it sends the signal to its children						
>     Waitpid(-1, NULL, 0);					
>     
>     Sigfillset(&mask);
>     Sigprocmask(SIG_BLOCK, &mask, &prev_mask);
>     printf("%ld", ++counter);
>     Sigprocmask(SIG_SETMASK, &prev_mask, NULL);
>     exit(0);
> }
> ```
>
> output:
>
> ```bash
> 2
> 1
> 3
> ```
>
> 它的流程图是：
> ```flowchart
>                  fork
>                   │
>         ┌─────────┴─────────┐
>         │                   │
>       父进程                子进程
>         │                   │
>         │                 while(1)
>         │                   │
>  kill(child, SIGUSR1) ──────┤
>         │                   │
>         │              收到 SIGUSR1
>         │                   ↓
>         │               handler1
>         │                   │
>         │              --counter
>         │                   │
>         │                _exit(0)
>         │                   │
>         │              子进程死亡
>         │                   │
>         └── waitpid() ◄─────┘
>         │
>      ++counter
>         │
>       exit(0)
> ```



##### 3 可移植的信号处理(sigaction())

Unix信号处理的另一个缺陷在于不同系统有不同的信号处理语义，包括：

- **`signal`函数的语义各有不同**

  例如老的Unix系统会在捕获信号`k`后把它的反应恢复为默认值，那么处理程序必须显示地重新调用`signal`设置自己

- **系统调用可以被中断**

  比如`read`/`write`/`accept`这些系统调用潜在地会阻塞进程一段时间，称为**慢速系统调用**
  在早期版本Unix中，当处理程序捕获到一个信号时，<u>被中断的慢速系统调用返回时不是继续，而是返回给用户一个错误条件，并将`errno`设置为EINTR</u>，也就是说我们此时还得手动重启被中断的系统调用代码

**sigaction()**

为了解决这些问题，Posix标准定义了一组**`sigaction`函数**，**<u>允许用户在设置信号处理时明确指定他们想要的信号处理语义</u>**（你可以认为是signal的统一版本）

 ```c
  #include <signal.h>
  int sigaction(int signum, struct sigaction *act, struct sigaction *oldact);
  // 返回：成功0错误-1
 ```

但是它使用的并不广泛，因为它要求用户设置一个复杂的条目

一个更简洁的方法是，定义一个包装函数`Signal`，调用`sigaction`来完成配置：
```c
handler_t *Signal(int signum, handler_t *handler){
    struct sigaction action, old action;
    action.sa_handler = handler;
    sigemptyset(&action.sa_mask);
    action.sa_flags = SA_RESTART;
    if(sigaction(signum, &action, &old_action) < 0)
        unix_error("Signal error");
    return (old_action.sa_handler);
}
```



#### 8.5.6 同步流以避免讨厌的并发错误

**如何编写读写相同储存位置的并发流程序**

一般而言，流可能交错的数量与指令的数量呈指数关系。
基本的问题是以某种方式同步并发流，从而得到最大可行的交错的集合，且每个可行的交错都能得到正确的结果

> （一段错误代码）
>
> 它干的事情是：父进程创建一个子进程就把它添加到作业列表里面，当父进程在SIGCHLD处理程序里面回收一个终止的子进程时，它就从作业列表里面删除这个子进程
>
> ```c
> void handler(int sig){
>     int olderrno = errno;
>     sigset_t mask_all, prev_all;
>     pid_t pid;
>     
>     Sigfillset(&mask_all);
>     while ((pid = waitpid(-1, NULL, 0)) > 0){	// if theres a zombie process
>         Sigprocmask(SIG_BLOCK, &mask_all, &prev_all);
>         deletejob(pid);							// delete the child from job list
>         Sigprocmask(SIG_SETMASK, &prev_all, NULL);
>     }
>         if (errno != ECHILD)
>             Sio_error("waitpid error");
>         errno = olderrno;
> }
> 
> int main(int argc, char **argv){
>         int pid;
>         sigset_t mask_all, prev_all;
>         Sigfillset(&mask_all);
>         Signal(SIGCHLD, handler);
>         initjobs();
>         while(1){
>             if ((pid = Fork()) == 0){			// child
>                 Execve("/bin/date", argv, NULL);
>             }
>         
>             Sigprocmask(SIG_BLOCK, &mask_all, &prev_all);
>             addjob(pid);						// add child to the job list
>             Sigprocmask(SIG_SETMASK, &prev_all, NULL);
>         }
>         exit(0);
> }
> ```
>
> 看起来问题不大，但是问题就出在我们从`Fork()`到`addjob`中间：
>
> 1. 父进程执行fork函数，内核调度新创建的子进程运行而非父进程
> 2. 在父进程能够再次运行前，子进程已经终止了，成为了一个zombie，问题是此时还没有把它加入作业列表
> 3. 父进程再次变成可运行，收到信号SIGCHLD，然后发现了这个进程，但是由于它还没被加入作业列表，`deletejob`什么都做不了
> 4. 父进程又把这个本就不存在的进程加入了作业列表，显然这个条目无法被清理

这就是一个称为**竞争(race)**的经典同步错误的示例，因为这里的`addjob`和`deletejob`之间存在竞争，这种错误非常难调试（因为它是不可预测的）

那么下面是一种消除竞争的方法：

> ```c
> void handler(int sig){
>     int olderrno = errno;
>     sigset_t mask_all, prev_all;
>     pid_t pid;
>     Sigfillset(&mask_all);
>     while ((pid = waitpid(-1, NULL, 0)) > 0) { // 回收一个僵死子进程
>         Sigprocmask(SIG_BLOCK, &mask_all, &prev_all);
>         deletejob(pid); // 从作业列表删除该子进程
>         Sigprocmask(SIG_SETMASK, &prev_all, NULL);
>     }
>     if (errno != ECHILD)
>         Sio_error("waitpid error");
>     errno = olderrno;
> }
> int main(int argc, char **argv){
>     int pid;
>     sigset_t mask_all, mask_one, prev_one;
>     Sigfillset(&mask_all);
>     Sigemptyset(&mask_one);
>     Sigaddset(&mask_one, SIGCHLD);		/////
>     Signal(SIGCHLD, handler);
>     initjobs();
>     
>     while(1){
>         Sigprocmask(SIG_BLOCK, &mask_one, &prev_one);
>         if ((pid = Fork()) == 0){			// child
>             Sigprocmask(SIG_SETMASK, &prev_one, NULL);
>              Execve("/bin/date", argv, NULL);
>          }
>         Sigprocmask(SIG_BLOCK, &mask_all, NULL);
>         addjob(pid);
>         Sigprocmask(SIG_SETMASK, &prev_one, NULL);
>     }
>     exit(0);
> }
> ```
>
> 这里while里面在开始之前先禁用SIGCHLD，直到`addjob`之后才取消它，这样保证直到`addjob`结束后才可能进入处理程序



#### 8.5.7 显式地等待信号(sigsuspend())

有时主程序需要显式地等待信号处理程序运行

比如shell创建一个前台作业时，必须等待作业终止，被SIGCHLD的处理程序回收后，才能接收下一条指令

> 下面给出了一个基本的思路：
>
> 一个无限循环，先把SIGCHLD给阻塞，然后把pid置0，取消阻塞，等待进入处理程序设置pid为子进程
>
> ```c
> #include "csapp.h"
> volatile sig_atomic_t pid;
> void sigchld_handler(int s){
>     int olderrno = errno;
>     pid = waitpid(-1, NULL, 0);
>     errno = olderrno;
> }
> void sigint_handler(int s){
>     
> }
> int main(){
>     sigset_t mask, prev;
>     Signal(SIGCHLD, sigchld_handler);
>     Signal(SIGINT, sigint_handler);
>     Sigemptyset(&mask);
>     Sigaddset(&mask, SIGCHLD);
>     while(1){
>         Sigprocmask(SIG_BLOCK, &mask, &prev);
>         if (Fork() == 0)
>             exit(0);
>         
>         pid = 0;		// 如果在这一步之前就终止了，那么pid = 0会覆盖，结果就是卡死，所以我们要加上阻塞
>         Sigprocmask(SIG_SETMASK, &prev, NULL);
>         while(!pid) ;
>         printf(".");
>     }
>     exit(0);
> }
> ```
>

显然循环会一直浪费处理器资源，为了解决我们在这里插入一个pause()让它休眠节省时间
```c
while(!pid) pause();	// 休眠进程
```

**但是这有问题**！`pause`就像前面说的，它只会检查`pending`的信号，那如果偏偏在while(!pid)之后，`pause()`之前，那么此时`while`检查时认为没有信号，决定调用`pause`，而立刻进入了处理函数，处理完成了，**到`pause`的时候，已经没有信号产生行为了，此时就会卡死**！这是很严重的竞争。

那么我们也可以考虑用`sleep`，比如：
```c
while(!pid) sleep(1);
```

不过这太蠢了，依旧如果发生竞争我们需要等1秒才会再次检查循环条件

**<u>问题事实上就在于我们取消阻塞SIGCHLD到我们pause的中间</u>**，那么既然我们需要它们中间不被打断，为什么不把它们变成原子的整体？

**sigsuspend**

`sigsuspend()`暂时用`mask`代替当前的阻塞集合，然后挂起该进程，直到收到一个信号并且产生行为，**<u>它是原子的！</u>**

````c
#include <signal.h>
int sigsuspend(const sigset_t *mask);
````

它实际上等价于：（只是原子属性）
```c
sigprocmask(SIG_SETMASK, &mask, &prev_mask);
pause();
sigprocmask(SIG_SETMASK, &prev_mask, &mask);
```

那么此时这个信号相当于只对`pause`存在，自然也就不可能存在竞争了

> 那么自然我们就可以很容易地修改了：
> ```c
> #include "csapp.h"
> volatile sig_atomic_t pid;
> void sigchld_handler(int s){
>     int olderrno = errno;
>     pid = Waitpid(-1, NULL, 0);
>     errno = olderrno;
> }
> void sigint_handler(int s){   
> }
> int main(){
>     sigset_t mask, prev;
>     Signal(SIGCHLD, sigchld_handler);
>     Signal(SIGINT, sigint_handler);
>     Sigemptyset(&mask);
>     Sigaddset(&mask, SIGCHLD);
>     while(1){
>         Sigprocmask(SIG_BLOCK, &mask, &prev);
>         if (Fork() == 0)
>             exit(0);
>         
>         pid = 0;
>         while(!pid) 
>             sigsuspend(&prev);
>         Sigprocmask(SIG_SETMASK, &prev, NULL);
>         printf(".");
>     }
>     exit(0);
> }
> ```
>
> 



### 8.6 非本地跳转(setjmp/longjmp)

C提供了一种用户级异常控制流形式，称为**非本地跳转(nonlocal jump)**
它将控制从一个函数直接移交给另一个正在执行的函数，而无需正常的调用-返回序列。

非本地跳转是通过`setjmp`/`longjmp`函数实现的：

```c
#include <setjmp.h>
int setjmp(jmp_buf env);
int sigsetjmp(sigjmp_buf env, int savesigs);
// 第一次调用setjmp时返回0,而从longjmp回来时返回非0
// sigsetjmp还会保存signal mask，savesigs=1时就是要保存信号
```

`setjmp`函数在`env`缓冲区保存当前**调用环境（PC/rsp/通用寄存器）**，以供后面的`longjmp`使用，并返回0。（而longjmp返回时它再返回非0值）

> `setjmp`的返回值**不可以被赋值给变量，但是可以被用于条件语句的判断条件**

```c
#include <setjmp.h>
void longjmp(jmp_buf env, int retval);
void siglongjmp(sigjmp_buf env, int retval);
```

`longjmp`从env缓冲区恢复调用环境，然后触发一个最近一次初始化`env`的`setjmp`调用的返回。再通过`setjmp`返回`retval`

- `longjmp`**允许跳过所有中间调用的特性可能产生意外的后果。**

> 也就是说可能会出问题，一个典型的例子就是如果中间函数调用中分配了某些数据结构，本来预期在函数结尾释放内存，那么就会**出现内存泄漏**（或者说所有资源管理都可能出问题，这是它很严重的一个缺陷）
>
> 另一个缺陷就是它对编译器优化特别敏感，往往我们写成volatile可能才会安全很多
>
> 以及longjmp的目标**必须还在调用链**之中，否则你返回时很可能会引用一个不存在的栈帧，比如这种情况：
> ```c
> jmp_buf env;
> 
> void f(void)
> {
>     setjmp(env);
> }  // f 返回
> 
> void g(void)
> {
>     longjmp(env, 1);  // 返回，结果发现栈帧不在了，换句话说就是rsp指向的已经无效了，自然无法还原原本的调用环境
> }
> ```
>
> 



**总之，`setjmp()`调用一次但多次返回，第一次是保存调用环境返回0，之后则是被`longjmp`调用返回非0的值；而`longjmp`不返回**



#### 应用

##### 1. 错误处理

非本地跳转的一个重要应用就是**<u>允许从一个深层嵌套的函数调用中立即返回，这通常是检测到某个错误时</u>**。这样我们就不用费时费力地去解开调用栈而是直接恢复到调用前的现场

> 一个典型的错误处理示例：
>
> ```c
> #include  "csapp.h"
> jmp_buf buf;
> int error1 = 0;
> int error2 = 0;
> void foo(void), bar(void);
> int main(){
>     switch(setjmp(buf)){
>         case 0:
>             foo();
>         	break;
>         case 1:
>             printf("Detected error1 in foo\n");
>             break;
>         case 2:
>             printf("Detected error2 in foo\n");
>             break;
>         default:
>             printf("Unknown error\n");
>     }
>     exit(0);
> }
> void foo(void){
>     if(error1)
>         longjmp(buf, 1);
>     bar();
> }
> void bar(void){
>     if(error2)
>         longjmp(buf, 2);
> }
> ```
>
> 流程：main先调用foo，foo调用bar，bar检测到error2就longjmp回setjmp的地方返回

##### 2. 信号处理

另一个重要应用就是使一个信号处理程序分支到一个特殊的代码区域，而不是被返回到被信号到达中断时的指令位置



> 如这个程序：
>
> ```c
> #include "csapp.h"
> sigjmp_buf buf;
> void handler(int sig){
>     siglongjmp(buf, 1);
> }
> int main(){
>     if(!sigsetjmp(buf, 1)){		//first time
>         Signal(SIGINT, handler);
>         Sio_puts("starting\n");
>     } else{
>         Sio_puts("restarting\n");	// 必须安全，否则如果在这里被打断，麻烦的就在于由于longjmp不会返回这里，你不原子的话就会出错
>     }
>     while(1){
>         Sleep(1);
>         Sio_puts("processing...\n");
>     }
>     exit(0);					// 不安全的exit(0)是不可达的
> }
> ```

**注意：**

1. 为了避免竞争，必须在sigsetjmp之后再设置Signal，因为我们需要先setjmp后longjmp

2. `sigjmp`/`longjmp`都不是异步信号安全的，因为它可以跳转到任意代码。因此**<u>我们要在`siglongjmp`可达的代码中调用安全的函数</u>**



### 8.7 操作进程的工具

这就多得很了：

strace：打印一个正在运行的程序和它的子进程调用的每个系统调用的轨迹，如果你编译时带上`-static`就会有更干净的trace

ps：列出当前系统的进程（包括僵死的）

pgrep：查找进程返回进程号

top：打印所有关于当前进程资源使用的信息

pmap：显示进程的内存映射

/proc：一个虚拟文件系统，以ascii格式输出内核数据结构的内容



### 课后习题：

`8.11 输出几行hello？`

```c
int main(){
    int i;
    for(i = 0; i < 2; i++)
        fork();
    printf("hello\n");
    exit(0);
}
```

主进程会fork出两个子进程，而其中一个子进程还会再fork一个自己的子进程，因此一共有3个子进程，那么就是输出4行

8.12 8个

8.13 x=4 x=3 x=2 / x=4 x=2 x=3 / x=2 x=4 x=3

8.14 3个

8.15 5个

8.16 counter = 2

8.18 对下列程序输出为何？

```c
#include "csapp.h"
void end(void){
    printf("2"); fflush(stdout);
}
int main(){
    if(Fork() == 0)
        atexit(end);	// add `end` so when we call `exit` it runs it
    if(Fork() == 0){
        printf("0"); fflush(stdout);
    }else {
        printf("1"); fflush(stdout);
    }
    exit(0);
}
```

主进程先产生进程1，1进行了atexit，它们各自fork：主进程->2，1->3(3也继承了)

主进程输出：1

1：12

2：0

3：02

故选择：A C E

（题外话：这里为什么要有`fflush`？因为我们需要刷新缓冲区，保证在我们fork之前缓冲区是干净的，否则很可能就是我们认为已经输出到屏幕了，但是实际上还在缓冲区，那么这个内容就会再被子进程输出一次）

8.19 下列函数打印多少行：

```c
void foo(int n){
    int i;
    for(i = 0; i < n; i++)
        Fork();
    printf("hello\n");
    exit(0);
}
```

显然是$2^n$，把循环展开就明白了，每次Fork就是翻倍

8.20 编写一个自己的ls程序，你可以execve调用/bin/ls，接收相同的命令行参数，解释同样的环境变量

```c
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
int main (int argc, char **argv, char **envp){
    if(execve("/bin/ls", argv, envp) < 0){
        perror("execve excuted failed");
        exit(1);
    }
    exit(0);
}
```

8.21 可能的输出序列：

```c
int main(){
    if(fork() == 0){
        printf("a"); fflush(stdout);
        exit(0);
    } else{
        printf("b"); fflush(stdout);
        waitpid(-1, NULL, 0);
    }
    printf("c"); fflush(stdout);
    exit(0);
}
```

abc/bac，`waitpid`约束了c必须在a后面

8.22 `自己编写一个system函数，通过调用`/bin/sh -c <command>`来执行，在command完成后返回，如果command正常退出，那么mysystem返回它的退出状态。（如：command调用exit(8)终止则返回8）。而如果是异常终止，那么mysystem返回shell返回的状态`

```c
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/wait.h>
#include <sys/types.h>
char **envp;
int mysystem(char *command){
    char *myargv[] = {
        "sh",
        "-c",
        command,
        NULL
    };
    pid_t pid = fork();
    if(!pid){
        execve("/bin/sh", myargv, envp);
        perror("execve");
        _exit(1);
    }else if (pid > 0){
        int status;
        waitpid(pid, &status, 0);
        if(WIFEXITED(status)){
          return WEXITSTATUS(status);
        }else if (WIFSIGNALED(status)){
          return WTERMSIG(status);
        }else if (WIFSTOPPED){
            ...
        }else{
          perror("unexpected error");
          return -1;
        }
    }else{
          perror("frok");
          return -1;
    }
}

```

这个如果你想要用键盘终止恐怕不太现实，因为这个信号会被同时发给我们正在用的比如bash的前台作业，除非你要是把SIGINT绑定为啥也不做，不过没必要，测试信号是否正常只需要：

```bash
$ ./mysystem -c "kill -TERM \$\$"
Terminated by signal 15
```

8.24

8.26 

`以下图的程序为起点，编写一个shell程序，必须有以下特性：`
![image-20260813150425880](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260813150425880.png)

- 用户输入的命令行由一个name + 0个或若干个参数组成。

  如果`name`是一个内置命令，那么shell就立刻处理它，并等待下一个命令行。
  否则shell就认为它是一个可执行文件，在一个初始的子进程的上下文中加载并运行它。作业进程组与子进程的PID相同

- 每个作业是由一个进程ID(PID) / 一个作业ID(JID)来标识的，它是由shell分配的任意的小正整数。JID在命令行上用前缀`%`标识，比如`%5`->JID=5，`5`->PID=5

- 如果命令行以`&`结束，那么就在后台运行这个作业，否则，shell在前台运行这个作业

- 输入Ctrl + C -> SIGINT，Ctrl + Z -> SIGTSTP，信号发送给shell，shell则会把它们转发给前台进程组的每个进程

- 内置命令`jobs`用于列出所有后台作业

- `bg job`发送一个SIGCONT信号来重启`job`，然后在后台运行它。`job`可以是PID / JIDz

- 内置命令`fg job`通过发送一个SIGCONT重启`job`然后在前台运行它

- shell回收它的所有僵死子进程，如果任何作业因为收到一个未捕获的信号而终止，那么shell就输出一条消息到终端，消息中包含该作业的PID和对该信号的描述

> 这是一道综合性的题目了，我觉得可以放在Shell Lab之前做，自己先想一想该如何设计，这个搞定之后再可以去对照Shell Lab的再进一步完成。
>
> 整体思路不复杂，就是先parse再builtin再eval
>
> 需要注意的点：
>
> - 显然我们要维护一个全局的job list，而就像之前说的那样，它在主程序和SIGCHLD的处理程序里面都需要访问，因此我们必须保证不会出现竞争（也就是说我们要先阻塞SIGCHLD才能访问）这个你就得保证fork之前就做好阻塞（当然书里面都讲了）
> - strsig函数不是异步信号安全的，我的解决方法就是自己写一个翻译的（这比较笨）
> - 别忘了errno
> - 前台运行时用sigsuspend而非pause,并且记得先解除阻塞
>
> 我的代码：
> ```c
> #include "csapp.h"
> #define MAXARGS 128
> #define MAXJOBS 64
> 
> // typedefs
> typedef enum STATE{
>   UNDEF,
>   FG,     // front ground
>   BG,     // back ground
>   ST      // stopped
> } state_t;
> typedef struct JOB{
>   pid_t pid;
>   state_t state;
>   char cmd[MAXLINE];
> } job_t;
> 
> // vars
> char **environ = NULL;
> job_t job_list[MAXJOBS + 1] = {0};
> sigset_t mask_SIGCHLD;
> 
> // func prototypes
> void eval(char *cmdline);
> int parseline(char *buf, char **argv);
> int builtin_command(char **argv);
> int pid_jid(pid_t pid);
> int fgjid();
> int addjob(pid_t pid, state_t state, char *cmd);
> void deletejob(int jid);
> char *sig_name(int sig){
>   switch(sig){
>     case SIGINT:
>       return "Interrupt";
>     case SIGTERM:
>       return "Terminated";
>     case SIGSEGV:
>       return "Segmentation fault";
>     case SIGABRT:
>       return "Aborted";
>     case SIGFPE:
>       return "Floating point exception";
>     case SIGILL:
>       return "Illegal instruction";
>     default:
>       return "Unknown signal";
>   }
> }
> 
> // signal handlers
> void sigchld_handler(int sig){
>   int olderrno = errno;
>   int status;
>   pid_t pid;
>   while((pid = waitpid(-1, &status, WNOHANG | WUNTRACED)) > 0){
>     int jid = pid_jid(pid);
>     if(jid == -1) continue;
>     if(WIFSIGNALED(status)){
>       Sio_puts("Job ");
>       Sio_putl((long)pid);
>       Sio_puts(" terminated by signal: ");
>       Sio_puts(sig_name(WTERMSIG(status)));
>       Sio_puts("\n");
>       // still we needs to recycle the terminated child proc
>       // but since in other handlers we dont access the job_list
>       // we dont need to block the signals
> 
>       deletejob(jid);
>     } else if(WIFSTOPPED(status)){ 
>       job_list[jid].state = ST; 
>     } else if(WIFEXITED(status)){
>      deletejob(jid); 
>     }
>   }
>   errno = olderrno;
> }
> void sigint_handler(int sig){
>   int olderrno = errno;
> 
>   for(int i = 0; i < MAXJOBS; i++){
>     if(job_list[i].state== FG){
>       kill(-job_list[i].pid, SIGINT);
>     }
>   }
>   errno = olderrno;
> }
> void sigtstp_handler(int sig){
>   int olderrno = errno;
> 
>   for(int i = 0; i < MAXJOBS; i++){
>     if(job_list[i].state == FG){
>       kill(-job_list[i].pid, SIGTSTP);
>     }
>   }
>   errno = olderrno;
> 
> }
> 
> // main func
> int main(int argc, char **argv, char **envp){
>   // initializing env
>   char cmdline[MAXLINE];
>   environ = envp;
>   // install signal handler
>   sigemptyset(&mask_SIGCHLD);
>   sigaddset(&mask_SIGCHLD, SIGCHLD);
>   Signal(SIGCHLD, sigchld_handler);
>   Signal(SIGINT, sigint_handler);
>   Signal(SIGTSTP, sigtstp_handler);
>   // main loop
>   while(1){
>     // read part:
>     printf("> ");
>     fflush(stdout);   // 防止重复输出
>     Fgets(cmdline, MAXLINE, stdin);
>     if(feof(stdin)) exit(0);
> 
>     // eval part:
>     eval(cmdline);
>   }
> }
> 
> // the realization of funcs
> int builtin_command(char **argv){
>   sigset_t prev_mask;
>   if (!strcmp(argv[0], "quit"))
>     exit(0);
>   if (!strcmp(argv[0], "&"))
>     return 1;
>   if (!strcmp(argv[0], "jobs")){
>     /// unrealized 
>     Sigprocmask(SIG_BLOCK, &mask_SIGCHLD, &prev_mask);
>     for(int i = 0; i < MAXJOBS; i++){
>       if(job_list[i].pid){
>         printf("[%d] %d %s %s", i, job_list[i].pid, ((job_list[i].state == ST) ? "Stopped" : "Running"), job_list[i].cmd);
>       }
>     }
>     Sigprocmask(SIG_SETMASK, &prev_mask, NULL);
>     return 2;
>   }
>   if (!strcmp(argv[0], "bg")){
>     // if is digit
>     int jid;
>     if(!argv[1]){
>       printf("Wrong usage: bg <proc>\n");
>       return 4;
>     }
>     if(isdigit(argv[1][0])){    // theres a problem
>       pid_t npid = (pid_t)atoi(argv[1]);
>       if((jid = pid_jid(npid)) == -1){
>         printf("%d: No such process\n", npid);
>         return 3;
>       }
>     }else{
>       printf("Wrong usage: bg <proc>\n");
>       return 3;
>     }
>     Sigprocmask(SIG_BLOCK, &mask_SIGCHLD, &prev_mask);
>     job_list[jid].state = BG;
>     kill(job_list[jid].pid, SIGCONT);
>     printf("[%d] %d %s", jid, job_list[jid].pid, job_list[jid].cmd);
>     Sigprocmask(SIG_SETMASK, &prev_mask, NULL);
>     return 3;
>   }
>   if (!strcmp(argv[0], "fg")){ 
>     int jid;
>     if(!argv[1]){
>       printf("Wrong usage: fg <proc>/<job>\n");
>       return 4;
>     }
>     if(isdigit(argv[1][0])){    // theres a problem, we just assume that argv[1] is all digital or not, and atoi cannot discover a mistake...
>       pid_t npid = (pid_t)atoi(argv[1]);
>       if((jid = pid_jid(npid)) == -1){
>         printf("%d: No such process\n", npid);
>         return 4;
>       }
>     }else if (argv[1][0] == '%' && isdigit(argv[1][1])) {
>       jid = atoi(argv[1] + 1);
>     }else{
>       printf("Wrong usage: fg <proc>/<job>\n");
>       return 4;
>     }
>     if(jid <= 0 || jid >= MAXJOBS || job_list[jid].pid == 0){
>       printf("No such job\n");
>       return 4;
>     }
>     Sigprocmask(SIG_BLOCK, &mask_SIGCHLD, &prev_mask);
>     job_list[jid].state = FG;
>     kill(job_list[jid].pid, SIGCONT); 
>     while(job_list[jid].state == FG)
>       Sigsuspend(&prev_mask);
>     Sigprocmask(SIG_SETMASK, &prev_mask, NULL);
>     // FG
> 
>     return 4;
>   } 
>   return 0;
> }
> 
> 
> int parseline(char *buf, char **argv){
>   char *delim;
>   int argc;
>   int bg;
>   // convert \n to ' ' and ignore the leading ' '
>   buf[strlen(buf)-1] = ' ';
>   while(*buf && (*buf == ' '))
>     buf++;
>   // split and save
>   argc = 0;
>   while((delim = strchr(buf, ' '))){ 
>     argv[argc++] = buf;
>     *delim = '\0';
>     buf = delim + 1;
>     while(*buf && (*buf == ' '))
>       buf++;
>   }
>   argv[argc] = NULL;
>   if(!argc) return 1;
>   if((bg = (*argv[argc-1] == '&')) != 0) argv[--argc] = NULL; //drop '&'
>   return bg;
> }
> 
> int pid_jid(pid_t pid){
>   for(int i = 0; i < MAXJOBS; i++){
>     if(job_list[i].pid == pid)
>       return i;
>   }
>   return -1;
> }
> int fgjid(){
>   for(int i = 0; i < MAXJOBS; i++){
>     if(job_list[i].state == FG)
>       return i;
>   }
>   return -1;
> }
> 
> int addjob(pid_t pid, state_t state, char *cmd){
>   // we just assume that no more than 64 jobs 
>   for(int i = 1; i <= MAXJOBS; i++){
>     if(!job_list[i].pid){
>       job_list[i].pid = pid;
>       job_list[i].state = state;
>       strcpy(job_list[i].cmd, cmd);
>       return i;
>     } 
>   }
>   printf("job list overflow\n");
>   exit(1);
> }
> 
> void deletejob(int jid){
>   job_list[jid].pid = 0;      //lazy 
>   job_list[jid].state =  UNDEF;
>   job_list[jid].cmd[0] = '\0';
> }
> 
> void eval(char *cmdline){
>   char *argv[MAXARGS];
>   char buf[MAXLINE];
>   int bg;
>   pid_t pid;
>   sigset_t prev_mask;
>   strcpy(buf, cmdline);  
>   bg = parseline(buf, argv);
> 
>   if(argv[0] == NULL)
>     return ;
>   if(!builtin_command(argv)){
> 
>     Sigprocmask(SIG_BLOCK, &mask_SIGCHLD, &prev_mask);
>     if ((pid = Fork()) == 0){ //child
>         setpgid(0, 0);    // set the pgid as its pid
>         Sigprocmask(SIG_SETMASK, &prev_mask, NULL);
>         execve(argv[0], argv, environ);
>         printf("%s: Command not found.\n", argv[0]);
>         exit(1);
>       }
> 
>     // parent
>     int jid = addjob(pid, bg ? BG : FG, cmdline);
>     if (!bg){ 
>       while(job_list[jid].state == FG)
>         Sigsuspend(&prev_mask);
>     } else{   
>       printf("[%d] %d %s", jid, pid, cmdline);
>     }
> 
>     Sigprocmask(SIG_SETMASK, &prev_mask, NULL);
>     }
> }
> 
> ```



### Shell Lab





## 九、虚拟内存

系统中的进程是与其他进程共享CPU和主存资源的，然而共享主存会带来挑战，内存很容易被破坏，而且还不够大

因此我们引入**虚拟内存(VM)**，作为对主存的抽象，它是硬件异常/硬件地址翻译/主存/磁盘文件/内核软件的完美交互，为每个进程提供一个大的/一致的/私有的地址空间，它提供了3个重要的能力：

- **主存被视为存储在磁盘上的地址空间的高速缓存**，在主存中只保存活动区域，根据需要来在主存和磁盘间来回传输数据，简化了内存管理
- **为每个进程提供了一致的地址空间**，简化了内存管理
- **保护每个进程的地址空间不被别的进程破坏**

虚拟内存之所以成功就在于它是自动地工作的，即便如此，程序员还需要理解它，因为：

- 虚拟内存是核心的。几乎你所有的工作都要和它打交道
- 虚拟内存是强大的
- 虚拟内存是危险的



### 9.1 物理和虚拟地址

主存被组织成M个连续的字节单元组成的数组，每字节都有唯一的物理地址(PA)，通过PA可以简单地寻址，称为**物理寻址**

而现代处理器使用虚拟寻址的形式，即CPU生成一个虚拟地址访问主存，其间虚拟地址先被转换为适当的物理地址，将虚拟地址转换为物理地址的任务称为**地址翻译(address translation)**，这同样需要CPU硬件和OS的紧密合作。CPU芯片上叫作**内存管理单元(MMU, Memory Management Unit)**专用硬件，利用存放在主存中的查询表来动态翻译虚拟地址，这个表由OS管理

### 9.2 地址空间

地址空间是一个非负整数地址的有序集合：`{0, 1, 2, ...}`
如果地址空间中整数是连续的，那么称它为一个线性地址空间（我们接下来都是假设线性的）。
在一个带虚拟内存的系统中，CPU从一个`N=2^n`的地址空间生成虚拟地址，称为**虚拟地址空间(virtual address space)**：`{0, 1, 2, ..., N}`，而其大小完全取决于我们表示最大地址的位数

而系统还有一个物理地址空间：`{0, 1, 2, ..., M}`，虽然它不一定是$2^m$，不过我们假设如此

地址空间清楚地区分了数据对象(字节)和它们的属性(地址)，有了这种区别，我们就可以将其推广，允许每个数据对象有多个独立的地址，其中每个地址都选自一个不同的地址空间

### 9.3 虚拟内存作为缓存工具

和存储层次结构的其他缓存一样，磁盘上的数据被分割为块，这些块作为磁盘和主存之间的传输单元。

而VM系统通过将虚拟内存分割为**虚拟页(VP, Virtual Page)**的大小固定的块来处理这个问题，每个虚拟页的大小为$P = 2^p$字节；类似地，物理内存也被分割为**物理页(PP, Physical Page，也称页帧page frame)**，大小同样为$P$字节

任意时刻，虚拟页面的集合都被分为**3个互不相交的子集**：

- **未分配**：VM系统还未分配的页，显然就没有和任何数据关联，自然不会占用任何磁盘空间
- **缓存的**：当前已缓存在物理内存中的已分配页
- **未缓存的**：未缓存在物理内存的已分配页

![image-20260816142704322](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816142704322.png)

#### 9.3.1 DRAM缓存的组织结构

> 为了有助于理解存储层次结构中不同的缓存概念，我们用**SRAM缓存**表示位于CPU和主存之间的L1/L2/L3高速缓存，用**DRAM缓存**表示虚拟内存系统的缓存，它则是在主存缓存虚拟页。

显然，DRAM比SRAM缓存慢了10倍，而磁盘比DRAM慢了$10^5$倍，那么**DRAM缓存不命中是比SRAM缓存不命中费时得多**。而同时 <u>从一个扇区读取第一个字节</u> 相比 <u>读扇区中连续的字节</u> 要慢约$10^5$倍。

正因为很大的不命中处罚和访问第一个字节的开销：

- **虚拟页往往很大，通常4KB~2MB**
- DRAM缓存是**全相联**的，任何虚拟页可以放在任何物理页地址。
- 不命中的替换策略需要更复杂。
- DRAM缓存总是使用**写回(writeback)而非直写(writethrough)**

> 解释一下：
>
> 1. 为什么要很大的虚拟页？
>
>    虚拟页大，页表条目就会更少 / 缺页异常次数也会更少 / 磁盘数据交换效率提升。太大则会浪费内存资源
>
> 2. 为什么全相连？
>
>    找的时候可以尽可能快地转换地址，而且必须要保证命中率，因为**未命中的处罚远大于查找本身带来的处罚**
>
> 3. 写回而非直写？
>
>    写回只需要写到这一层缓存就够了，而如果直写的话磁盘实在是太慢了，而且往往很多写操作需要之间局部性（比如我们可能刚写完又得读写），这些操作并不需要我们访问下一级的缓存



#### 9.3.2 页表

虚拟内存系统必须能判定某个虚拟页是否缓存在DRAM。如果命中还需要确定虚拟页放在哪个物理页；不命中则需要判断这个虚拟页放在磁盘的哪个位置。再根据替换策略将虚拟页从磁盘复制到DRAM中替换

这一切由：OS软件 / MMU的地址翻译硬件 / 存放在物理内存的叫做页表的数据结构 完成

页表将虚拟页映射到物理页，每次地址翻译硬件将一个虚拟地址翻译为物理地址时都需要读取页表，而OS负责维护页表的内容及在磁盘和DRAM之间来回传送页

事实上**页表(PT, page table)就是一个页表条目(PTE)的数组**，我们假设每个PTE是由一个有效位和一个n位地址字段组成的。
有效位表明了该虚拟页当前是否被缓存在DRAM里面：

- 如果设置了有效位，那么地址字段就表示DRAM相应的物理页的起始位置；

- 没设置：

  - 地址字段空就是未分配
  - 否则这里代表这个虚拟页在磁盘的起始位置

  注意：**我们这里接触的所有磁盘地址全是虚拟地址！！**

  > 磁盘上的数据和虚拟地址的联系，不是主要保存在页表里，而是保存在内核维护的 VMA 和文件/Swap 元数据里

> 比如这个例子：
> ![image-20260816142816771](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816142816771.png)
> 未分配：VP0 / VP5
> 未缓存：VP3 / VP6
> 缓存：VP1 / VP2 / VP4 / VP7

#### 9.3.3 页命中Page Hits

地址翻译硬件先将虚拟地址翻译为一个页表的索引，定位了对应的PTE，就可以直接从内存里面读取它了

#### 9.3.4 缺页 Page Fault

DRAM缓存不命中就称为缺页。

如果CPU引用了一个VP的字，它根据页表读取对应PTE，发现并没有被缓存，就会触发一个缺页异常。

此时便会陷入内核调用对应的缺页异常处理程序，它会选择牺牲一个页。如果这个要牺牲的页被修改了，那么它就会被复制回磁盘。而最终页表里面会把这个被牺牲的条目有效位取消

之后内核从磁盘复制到内存中，更新PTE，然后返回。此时就像之前说的，Fault会继续执行导致缺页的指令

> 由于虚拟内存是在1960年代被发明的，此时在内存和CPU存储的差距还没被拉得太大导致SRAM的产生，因此说法可能会有不同：
>
> - 块被成为页
> - 磁盘和内存间传送页的活动称为**交换(swapping)** / **页面调度(paging)**
> - 从磁盘**换入**DRAM，从DRAM**换出**磁盘
> - 发生不命中时才换入页面的策略成为**按需页面调度(demand paging)**，这是现代系统使用的方法

#### 9.3.5 分配页面

当操作系统分配一个新的虚拟内存页时，内核会在磁盘上创建空间并更新PTE，使它指向磁盘上新创建的这个页面

#### 9.3.6 依旧locality

显然上面的paging的效率似乎看起来很低，但实际上并非如此，因为我们还有locality。它保证了**任意时刻程序趋向于在一个较小的活动页面集合上进行工作**，也就是先前提到的**工作集(working set)** / **常驻集合(resident set)**。因此在初始开销之后，工作集页面被调度到内存中，那么之后对工作集的引用就会是命中的了

因此，只要我们程序具有良好的时间局部性，虚拟内存系统就能工作的很好，但是显然如果工作集大小超出了物理内存的大小，此时页面会不断地换进换出，也就是所谓**抖动(thrashing)**

> 如果你的程序慢的要死，有可能是这个原因
> 你可以用`<sys/resources.h>`的`getrusage`函数来监测缺页数量



### 9.4 虚拟内存作为内存管理的工具

虚拟内存大大地简化了内存管理，并提供了一种自然的保护内存的方法

实际上，操作系统为**每个进程都提供了独立的页表/独立的虚拟地址空间**，而且**多个虚拟页面可以映射到同一个共享物理页面上**

那么按需页面调度和独立的虚拟地址空间结合，就会带来各种好处：

- **简化了链接**

  **独立的地址空间保证了每个进程的内存映像采用相同的基本格式**，这样的一致性可以使得链接器直接生成完全连接的可执行目标文件

- **简化了加载**

  如果要把`.text` / `.data`加载到一个新创建的进程中，Linux的加载器为带按摩和数据段分配虚拟页，并把他们标记为无效（未缓存），再将页表条目指向elf文件中对应的位置。

  而需要注意，**加载器本身并不会把任何内容从磁盘复制到主存。**

  **每个页被初次引用要么是CPU取指引起，要么是正在执行的指令引用了一个虚拟内存位置**，此时会触发**缺页异常**。

  > 然后就是陷入内核，内核进入处理程序后会Sleep当前进程，进行调度，先切换到别的逻辑控制流直到DMA触发中断再进行上下文切换

> 把一组虚拟页映射到任意一个文件任意位置的表示法称为内存映射(memory mapping)，Linux的`mmap`系统调用就允许操作系统自己去做内存映射

- **简化共享**

  例如每个进程都需要调用相同的OS内核代码，每个C程序都需要调用标准库的程序，还包括共享链接库之类的。
  OS可以将不同进程的虚拟页映射到相同的物理页，从而安排多个进程共享这部分代码

- **简化内存分配**

  虚拟内存向用户提供了一个简单的分配额外内存的机制。

  比如当你调用malloc的时候，OS会分配一个适当数字个连续的虚拟内存页面，并把它们映射到物理内存中对应的页面，它们可以随机分布




### 9.5 虚拟内存作为内存保护的工具

现代系统需要提供手段来控制对内存系统的访问，不能允许一个用户进程去修改它的只读代码段，也不应该允许它读/修改任何内核中的代码和数据结构，不应该允许它读写其他进程的私有内存，不允许他修改任何和其它进程共享的虚拟页面（除非所有的共享者都显式地允许这么做）

提供独立的地址空间使得区分不同进程的私有内存变得容易。而事实上地址翻译机制本身可以扩展到提供更好的访问控制，因为每一次访问一个虚拟地址都需要读取对应的PTE，只需要在PTE上加上一些额外的许可位即可控制对一个虚拟页面内容的访问
![image-20260816160640256](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816160640256.png)

这个示例中，每个PTE已经添加了3个许可位。

- SUP：进程是否必须运行在内核模式下才能访问。

  对运行在内核模式的进程可以访问任何页面，而运行在用户模式的进程只允许访问那些SUP=0的页面

- READ/WRITE：读写权限

如果一条指令违反了这些许可条件，那么CPU就会触发一个一般保护故障，把控制传递给一个内核中的异常处理程序，一般就是所谓段错误

### 9.6 地址翻译

> 这里对硬件省略了大量的细节，尤其是时序
>
> 符号表：
> ![image-20260816162605106](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816162605106.png)

形式上来说，地址翻译是一个N元素的虚拟地址空间(VAS)的元素和一个M元素的物理地址空间(PAS)中元素之间的映射
$$
MAP: {VAS} \to PAS \or \emptyset \\
MAP(A)= \begin{cases}
A'-如果虚拟地址A处的数据在PAS的物理地址A'处 \\
\empty -如果虚拟地址A处的数据不在物理内存
\end{cases}
$$
CPU中的一个控制寄存器，**页表基址寄存器(PTBR, Page Table Base Register)**，指向当前页表。

n位的虚拟地址包含2个部分：

- p位的**虚拟页面偏移(Virtual Page Offset, VPO)**
- n-p位的**虚拟页号(Virtual Page Number, VPN)**

MMU根据VPN选择适当的PTE。

> 如VPN0$\to$PTE0，VPN1$\to$PTE1...

将页表条目中的**物理页号(PPN)**和虚拟地址中的VPO串联起来，就得到相应的物理地址。
注意到因为物理和虚拟页都是P字节的，所以**物理页面偏移(PPO, Physical Page Offset)**和VPO是一致的



当**页面命中**的时候，只需要硬件处理：

1. 处理器生成一个虚拟地址，把它传送给MMU
2. MMU生成PTE地址，并从高速缓存/主存请求得到它
3. 高速缓存/主存 向MMU返回PTE
4. MMU构造物理地址，把它传送给高速缓存/主存
5. 高速缓存/主存返回所请求的数据字给处理器

![image-20260816165546741](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816165546741.png)

而如果**未命中**，此时就需要OS内核协作：

1. 前三步相同
2. PTE的有效位为0，MMU触发异常，传递CPU的控制到OS内核的缺页异常处理程序
3. 缺页处理程序确认出物理内存中的牺牲页，如果它被修改了那么还需要把它换出到磁盘上
4. 缺页处理程序页面调入新页面，更新内存中的PTE
5. 缺页处理程序返回原来的进程，执行原本那条指令，此时CPI将再次把引起缺页的虚拟地址发送给MMU，因为虚拟页面已经缓存在物理内存中，就会发生命中

> 练习9.3,给定一个32位的虚拟地址空间和一个24位的物理地址空间，对给定的页大小P，填表：
>
> | P    | VPN位数 | VPO  | PPN  | PPO  |
> | ---- | ------- | ---- | ---- | ---- |
> | 1KB  | 14      | 18   | 6    | 18   |
> | 2KB  | 13      | 19   | 5    | 19   |
> | 4KB  | 12      | 20   | 4    | 20   |
> | 8KB  | 11      | 21   | 3    | 21   |

#### 9.6.1 结合高速缓存和虚拟内存

任何既使用高速缓存又使用虚拟内存的系统中，都会有到底是使用虚拟地址还是物理地址访问SRAM高速缓存的问题。大多数系统还是会使用**物理寻址**，因为：

- 多个进程同时在高速缓存用存储块和共享来自相同虚拟页面的块可以变得很简单
- 高速缓存本身无需保护，因为访问权限的检查已经在地址翻译里面做到了

![image-20260816170831809](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816170831809.png)
就像上图一样，MMU可以通过高速缓存的物理地址来寻址，也可以用PTEA来寻址，而无论是数据还是PTE条目都可以缓存在高速缓存里面

#### 9.6.2 使用TLB加速地址翻译

> 每次CPU产生一个虚拟地址，MMU就必须查阅一个PTE以便将虚拟地址翻译为物理地址。
> 最糟糕的情况下显然会需要从内存多取一次数据，代价是上百周期，但如果PTE缓存在L1 cache里面，开销就可以下降到1~2周期

为了试图消除这样的开销，在MMU中包括了一个关于PTE的小缓存，称为**翻译后备缓冲器(TLB, Translation Lockaside Buffer)**，我们这样可以

TLB是**一个小的/虚拟寻址的缓存，其中每一行都保存一个由单个PTE组成的块**。而且TLB往往有**很高的相联度**（甚至可能是全相联）。
![TLB条目格式](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816172105792.png)
还是经典的缓存结构，用于组选择和行匹配的索引和Tag是从虚拟地址的虚拟页号VPN中提取出来的。
**若TLB有$T=2^t$个组，那么TLBI就是由VPN低t位组成的，而TLBT是由VPN中剩余的位组成的**



**TLB命中：**

1. CPU产生一个虚拟地址
2. MMU从TLB取出对应的PTE
3. MMU将这个虚拟地址翻译为一个物理地址，把它发送给高速缓存 / 主存
4. 高速缓存 / 主存把所请求的数据字返回CPU

**未命中**：

别的不变，就是发送PTEA，之后MMU必须从L1缓存取出PTE，新的pte存放在TLB里面



#### 9.6.3 多级页表(节省主存)

目前我们都是使用单一页表进行翻译，但是比如我们假设一个系统：32位/4KB页/4字节PTE，那么即使我们的应用仅仅使用了虚拟地址空间的很小的一部分，仍然需要4MB的页表常驻在主存，这是很浪费的

因此我们引入使用层次结构的页表，为了方便理解还是用这个例子：

一级页表中每个PTE负责映射虚拟地址空间中的一个4MB的片(chunk)，每一个chunk则是由1024个连续的页面组成，那么对于一个4GB的地址空间来说，1024个这样的一级PTE就足以涵盖整个空间

而如果这个片中的每个页面都未被分配，那么一级的对应PTE就为空，未分配；否则就会指向一个二级页表的基址。

而二级页表中每个PTE就是直接负责一个4KB的虚拟缓存页面了，而如果使用4字节的PTE，那么每个一级和二级页表都是4KB，正好等于一个页面的大小
![多级页表](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816181725793.png)

这从两方面节省了内存：

1. 如果一级页表的一个PTE为空，**后面的二级页表根本不会存在**
2. **只有一级页表才需要总是在主存中**，虚拟内存可以在需要时创建/页面调入/调出二级页表，只有经常需要使用的二级页表才需要缓存在主存当中

那么此时的虚拟地址就可以用另一种方式来翻译（但是形式不变，只需要分段翻译即可）：
虚拟地址根据页表的级数$k$划分为$k$个VPN和1个VPO，每个VPN $i$都是一个到第$i$级页表的索引，而$i$级页表中的PTE指向$i+1$级中下一级页表的基址，而第$k$级页表的PTE指向的则是某个物理页面的PPN / 一个磁盘块的地址。在确认PPN之前，MMU必须访问k个PTE，而同样到最后VPO和PPO是一致的。
![image-20260816184035197](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816184035197.png)

#### 9.6.4 综合：端到端的地址翻译

综合一下刚刚我们讲的，用一个翻译示例，它有TLB和L1 d-cache，为了保证可管理性，做出如下假设：

- 内存是按字节寻址的
- 内存访问针对1字节的字
- 虚拟地址是14位的，n=14
- 物理地址是12位的，m=12
- 页面大小是64字节
- TLB四路组相联，16个条目
- L1 d-cache是物理寻址/直接映射的，行大小4字节，共16组

那么首先对于虚拟地址，VPO就是6位(64)，而VPN则需要14-6=8高位。物理地址则是高6位作为PPN
![image-20260816185209267](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816185209267.png)

同时我们还给出一张这个系统的快照：
![image-20260816185654210](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816185654210.png)

- TLB

  TLB利用VPN的位索引，又因为有4个组，我们以低2位作为组索引TLBI，剩下高6位作为标记TLBT，以此区分。
  这里TLB就是用TAG索引匹配对应的PPN

- 页表

  页表是一个单级设计，显然一共是$2^{14-6=8}=256$个PTE（只展示前面16个）。而破折号表示这里的地址无意义

- 高速缓存

  因为每个块都是4字节，低2位作为组偏移CO，而中间4为用作组索引CI，剩下6位作为标记CT

  

给定这样的初始设定，我们考虑CPU读地址0x03d4时发生什么事：
先给出这个VA的划分：

![VPN](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816191711781.png)
先根据VPN我们在TLB里面找，TLBI=3, TLBT=3，TLB命中。那么把缓存的PPN：0x0D返回给MMU。MMU把PPN和VPO连接起来，那么就是物理地址PA：0x354。
![PA](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260816192238933.png)
那么对应CI=0x05, CT=0x0d,缓存命中，而CO=0x0，那么就可以读出0x36返回MMU再返回CPU

> 练习9.4 寻址0x03d7,什么过程？
>
> 二进制：11,1101,0111，先虚拟地址，是1111,01 0111，VPO=0x17，VPN=0xf，再TLB，TLBI=0x3，TLBT=0X3，则命中！还是0d + 0x17，依旧CT=0xd,CI=0x5，CO=0x3，返回0x1d



### 9.7 案例：INTEL CORE I7 / LINUX

处理器封装包含4个核/1个大的所有核共享的L3高速缓存/1个DDR3内存控制器，每个核包含1个层次结构的TLB/1个层次结构的数据和指令高速缓存以及1组快速点到点链路（基于QuickPath技术），为了让一个核与其他核/外部IO桥直接通信。

TLB是虚拟寻址的，4路组相联的。
L1 / L2 / L3 cache是物理寻址的，块大小为64字节。
L1和L2是8路组相联的，L3是16路组相联的。页的大小可以是4KB或4MB，Linux使用的是4KB
![image-20260817103825836](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260817103825836.png)

#### 9.7.1 Core i7 地址翻译

这里Core i7采用4级页表，同样每个进程有自己的页表层次结构。当一个Linux进程运行时，与已分配的页相关的页表都是驻留在内存中的。其中CR3页表始终指向进程的第一级页表的起始位置，其值属于进程上下文的一部分。
![image-20260817103844538](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260817103844538.png)

> 这里描述了CPU地址翻译的整体过程，忽略了i-cache / iTLB / 和L2统一TLB

下面是前3级页表条目格式，P=1时地址字段就是一个40位PPN指向页表头，显然这要求物理页表必须4KB对齐
![image-20260817104208077](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260817104208077.png)
这里PTE控制了3种权限：

- R/W：只读/读写访问的权限
- U/S：用户 / 内核模式访问权限
- XD：禁止执行，禁止从内存页取指（限制只能执行只读部分）

而MMU翻译每一个地址时，都会更新另外两个内核缺页处理程序用到的位：

- 每次访问一个页后，MMU都会设置A位即**引用位(reference bit)**，内核可以以此更新实现它的页替换算法
- 每次写入一个页则会设置D位即**修改位/ 脏位(dirty bit)**，它告诉内核在替换页之前是否需要写回牺牲页
- 内核可以清除这两个位

整个索引过程还是这样的：
![image-20260817110020875](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260817110020875.png)

> **地址翻译优化**
>
> 我们前面讲的地址翻译是：
>
> 1. MMU把虚拟地址翻译为物理地址
> 2. 物理地址传送到L1高级缓存
>
> 但是实际上**步骤是可以部分重叠的**，**因为cache里面的寻址依赖于VPO，而只有最后Tag匹配要求有PPN**，就比如我们上面说的4KB页大小的Core i7的系统，有12位VPO / PPO，而我们的L1 cache是8路组相联+物理寻址，64个组和64字节的块，**本身就可以通过6个缓存偏移位和6个索引位来索引，可以直接由VPO部分来完成**，换句话说我们不用等MMU搞定再说，可以同时把VPN发给MMU，VPO发给L1 cache，那么在MMU向TLB请求页表条目时，L1 cache已经在通过VPO查询到相应的组了，并且读取了组内8个标记和相应的数据字，这样一旦MMU得到PPN，就可以立刻把它和L1 cache里面的Tag进行匹配



#### 9.7.2 Linux虚拟内存系统

> 这里仅仅是做一个基本的描述，有个大致理解

Linux为每个进程维护了一个地址空间，已经很熟悉这张图了，我们已经熟悉了代码/数据/共享库/堆/栈 段，就可以填入更多关于内核虚拟内存的细节：

![image-20260817111218142](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260817111218142.png)
内核虚拟内存包含了内核中的代码和数据结构：

其中的某些区域被映射为**所有进程共享的物理页面**，如内核的代码和全局数据结构。而Linux也将一组连续的虚拟页面映射到相应的一组连续的物理页面，这就让内核访问物理内存中任意位置更加方便（如访问页表/执行内存映射的IO操作之类的)

而剩下区域就是每个进程自己的数据，比如页表/内核在进程上下文中执行代码时使用的栈...

##### 1. Linux虚拟内存区域

Linux将虚拟内存组织为一些段 / 区域(area)的集合，一个区域就是已分配的虚拟内存的连续片chunk，每个存在的虚拟页面都保存在某个区域。
**不属于某个区域的虚拟页是不存在的，且不能被进程引用（这部分是非法的）因为还没有被分配为合法的VMA中的地址**。
这样**VMA就是可以有间隙的，内核无需记录不存在的虚拟页，也就无需额外占据任何资源**

下面是一个记录一个进程虚拟内存区域的内核数据结构：
![image-20260817130621382](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260817130621382.png)

内核为系统中每个进程维护一个单独的任务结构`task_struct`，而任务结构中的元素包含/ 指向内核运行该进程需要的所有信息（pid / rsp / 可执行目标文件 / PC ...）

`task_struct`里面的条目指向`mm_struct`，描述虚拟内存当前的状态，其中`pgd`就是进程pid，`mmap`指向一个`vm_area_structs`的链表，描述了当前虚拟空间的各个区域，当内核运行进程时，就把`pgd`存放于CR3，有以下字段：

- `vm_start`：指向区域的起始处
- `vm_end`：指向区域的结束处
- `vm_prot`：描述这个区域的所有页的读写权限
- `vm_flags`：区域页面是和其他共享还是私有
- `vm_next`：指向下一个区域的`vm_area_struct`

##### 2. Linux缺页异常处理

MMU触发一个page fault，那么步骤是：

1. 虚拟地址A本身合法吗？

   也就是查询区域结构的链表，和每一个区域结构的`vm_start`和`vm_end`比较，如果本身不合法，那么就会触发SIGSEGV.

   > 当然显然这样的开销是很大的，实际上Linux会在链表里面构建一棵树以此查找

2. 试图进行的内存访问本身是否合法？

   也就是说进程是否有对应访问的权限，如果不合法则会触发一个保护异常

3. 确认了这的确是合法的操作，开始进行替换

   选择一个牺牲页，如果这个页面是修改过的有脏位，那么就把它交换出去，换入新的页面并更新页表。此时再上下文切换返回引起缺页的指令，再次发送A到MMU就能正常翻译了



### 9.8 内存映射

Linux将一个虚拟内存区域与一个磁盘上的**对象(object)**关联起来，以此初始化这个虚拟内存区域的内容，称为**内存映射(memory mapping)**，虚拟内存区域可以映射到2种类型的对象的一种：

1. Linux文件系统的普通文件：

   一个区域可以映射到一个普通磁盘文件的连续部分，例如一个可执行目标文件。文件区(section)被分成页大小的片，每一片包含一个虚拟页面的初始内容
