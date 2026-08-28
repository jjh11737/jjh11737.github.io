

# E阶段

记录了我E阶段的学习笔记，具体的调试就不放了

## E2 

关于语法方面，可能有一些值得注意的点

- `{N{M}}` ：把M重复N次拼在一起

- `{a, b}`：位拼接，这个很基础

- `#(parameter a, ...)`Overriding Parameter，这种参数可以被新的值覆写，放在模块里面就可以接收外部的输入参数，而不必直接内部`parameter`写死。用于模块模板

- `#N`：让当前模块在这里停下N个周期，而`#0`虽然无延迟，则是把这个事件放到$R_2$里面延后执行

- `initial`块（不过用verilator压根用不到它）：不可被综合（综合器会忽略它），往往只适合写testbench(RTL里面不可能用)，用法：

  - 初始化信号
  - 生成激励
  - 产生时钟
  - 打开文件
  - 控制仿真，使用`$finish`来结束（它告诉仿真器可以结束这次仿真了）

  那么你就可以在这里使用`#N`了，自己控制在开始后指定的周期修改状态：

  > ```verilog
  > module tb;
  >     reg [1:0] a, b;
  > 
  >     initial begin
  >         a = 2'b10;              // Time 0: a assigned immediately
  >         #10 b = 2'b00;          // Time 10: b assigned after 10-unit delay
  >         #20 a = 2'b01;          // Time 30: a reassigned after additional 20 units
  >         #5 $display("Time=%0t a=%b b=%b", $time, a, b); // Time 35: display values
  >     end
  > endmodule
  > ```

  - 一个模块的`initial`的块可以为任意个

- task任务，其实就是你明确规定了一个输入输出的行为模式

  - 特别地还有很多系统专用的systemtask:

  - 常见 System Task / Function 总表

    | 系统任务/函数    | 类型          | RTL 综合 | Testbench | 作用                                   |
    | ---------------- | ------------- | -------- | --------- | -------------------------------------- |
    | `$clog2`         | function      | ✅        | ✅         | 向上取整的 log₂，常用于计算位宽        |
    | `$signed`        | function      | ✅        | ✅         | 转为有符号表达                         |
    | `$unsigned`      | function      | ✅        | ✅         | 转为无符号表达                         |
    | `$floor`         | function      | ⚠️        | ✅         | 向下取整；Vivado 主要支持参数/常量场景 |
    | `$ceil`          | function      | ⚠️        | ✅         | 向上取整；Vivado 主要支持参数/常量场景 |
    | `$rtoi`          | function      | ✅        | ✅         | real → integer                         |
    | `$itor`          | function      | ✅        | ✅         | integer → real                         |
    | `$display`       | task          | ⚠️*       | ✅         | 打印信息    $R_1$                      |
    | `$write`         | task          | ❌        | ✅         | 打印，不自动换行                       |
    | `$strobe`        | task          | ❌        | ✅         | 打印 $R_4$                             |
    | `$monitor`       | task          | ❌        | ✅         | 信号变化时自动打印                     |
    | `$finish`        | task          | ❌        | ✅         | 结束仿真                               |
    | `$stop`          | task          | ❌        | ✅         | 暂停仿真                               |
    | `$time`          | function      | ❌        | ✅         | 获取仿真时间                           |
    | `$realtime`      | function      | ❌        | ✅         | 获取实数形式仿真时间                   |
    | `$timeformat`    | task          | ❌        | ✅         | 设置时间打印格式                       |
    | `$random`        | function      | ❌        | ✅         | 产生仿真随机数                         |
    | `$urandom`       | function      | ❌        | ✅         | SystemVerilog 无符号随机数             |
    | `$urandom_range` | function      | ❌        | ✅         | 指定范围随机数                         |
    | `$fopen`         | function      | ❌        | ✅         | 打开文件                               |
    | `$fclose`        | task          | ❌        | ✅         | 关闭文件                               |
    | `$fdisplay`      | task          | ❌        | ✅         | 向文件打印                             |
    | `$fwrite`        | task          | ❌        | ✅         | 向文件写入                             |
    | `$fstrobe`       | task          | ❌        | ✅         | 向文件 strobe                          |
    | `$fmonitor`      | task          | ❌        | ✅         | 监视信号并写文件                       |
    | `$fgets`         | function/task | ❌        | ✅         | 从文件读取一行                         |
    | `$fscanf`        | function      | ❌        | ✅         | 从文件格式化读取                       |
    | `$readmemh`      | task          | **✅**    | ✅         | 从 hex 文件初始化 memory               |
    | `$readmemb`      | task          | **✅**    | ✅         | 从 binary 文件初始化 memory            |





## E4 

预处理就是包含：

- 包含头文件
- 宏替换
- 去掉注释
- 连接因`\`拆分的字符串
- 处理条件编译
- 处理字符串化操作符`#`
- 处理标识符连接操作符`##`

通过加上`-E`即可展示预处理结果
```bash
gcc -E a.c
```

干的事情和预期一样，把各种头文件/函数原型替换了原本的头文件声明，
```bash
$ gcc -E testcc.c  --verbose > /dev/null 
Using built-in specs.
COLLECT_GCC=gcc
OFFLOAD_TARGET_NAMES=nvptx-none:amdgcn-amdhsa
OFFLOAD_TARGET_DEFAULT=1
Target: x86_64-linux-gnu
Configured with: ../src/configure -v --with-pkgversion='Debian 14.2.0-19' --with-bugurl=file:///usr/share/doc/gcc-14/README.Bugs --enable-languages=c,ada,c++,go,d,fortran,objc,obj-c++,m2,rust --prefix=/usr --with-gcc-major-version-only --program-suffix=-14 --program-prefix=x86_64-linux-gnu- --enable-shared --enable-linker-build-id --libexecdir=/usr/libexec --without-included-gettext --enable-threads=posix --libdir=/usr/lib --enable-nls --enable-bootstrap --enable-clocale=gnu --enable-libstdcxx-debug --enable-libstdcxx-time=yes --with-default-libstdcxx-abi=new --enable-libstdcxx-backtrace --enable-gnu-unique-object --disable-vtable-verify --enable-plugin --enable-default-pie --with-system-zlib --enable-libphobos-checking=release --with-target-system-zlib=auto --enable-objc-gc=auto --enable-multiarch --disable-werror --enable-cet --with-arch-32=i686 --with-abi=m64 --with-multilib-list=m32,m64,mx32 --enable-multilib --with-tune=generic --enable-offload-targets=nvptx-none=/build/reproducible-path/gcc-14-14.2.0/debian/tmp-nvptx/usr,amdgcn-amdhsa=/build/reproducible-path/gcc-14-14.2.0/debian/tmp-gcn/usr --enable-offload-defaulted --without-cuda-driver --enable-checking=release --build=x86_64-linux-gnu --host=x86_64-linux-gnu --target=x86_64-linux-gnu --with-build-config=bootstrap-lto-lean --enable-link-serialization=3
Thread model: posix
Supported LTO compression algorithms: zlib zstd
gcc version 14.2.0 (Debian 14.2.0-19) 
COLLECT_GCC_OPTIONS='-E' '-v' '-mtune=generic' '-march=x86-64'
 /usr/libexec/gcc/x86_64-linux-gnu/14/cc1 -E -quiet -v -imultiarch x86_64-linux-gnu testcc.c -mtune=generic -march=x86-64 -fasynchronous-unwind-tables -dumpbase testcc.c -dumpbase-ext .c
ignoring nonexistent directory "/usr/local/include/x86_64-linux-gnu"
ignoring nonexistent directory "/usr/lib/gcc/x86_64-linux-gnu/14/include-fixed/x86_64-linux-gnu"
ignoring nonexistent directory "/usr/lib/gcc/x86_64-linux-gnu/14/include-fixed"
ignoring nonexistent directory "/usr/lib/gcc/x86_64-linux-gnu/14/../../../../x86_64-linux-gnu/include"
#include "..." search starts here:				
#include <...> search starts here:					# 寻找头文件
 /usr/lib/gcc/x86_64-linux-gnu/14/include
 /usr/local/include
 /usr/include/x86_64-linux-gnu
 /usr/include
End of search list.
COMPILER_PATH=/usr/libexec/gcc/x86_64-linux-gnu/14/:/usr/libexec/gcc/x86_64-linux-gnu/14/:/usr/libexec/gcc/x86_64-linux-gnu/:/usr/lib/gcc/x86_64-linux-gnu/14/:/usr/lib/gcc/x86_64-linux-gnu/
LIBRARY_PATH=/usr/lib/gcc/x86_64-linux-gnu/14/:/usr/lib/gcc/x86_64-linux-gnu/14/../../../x86_64-linux-gnu/:/usr/lib/gcc/x86_64-linux-gnu/14/../../../../lib/:/lib/x86_64-linux-gnu/:/lib/../lib/:/usr/lib/x86_64-linux-gnu/:/usr/lib/../lib/:/usr/lib/gcc/x86_64-linux-gnu/14/../../../:/lib/:/usr/lib/
COLLECT_GCC_OPTIONS='-E' '-v' '-mtune=generic' '-march=x86-64'
```

让gcc包含当前目录`-I./`，写了一个stdio.h：`echo nulll > ./stdio.h`，重新执行预处理：

```bash
$ nvim stdio.h
jjh@debian:/mnt/data1/0ysyx/.tmp$ gcc -I./ -E testcc.c 
# 0 "testcc.c"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 0 "<command-line>" 2
# 1 "testcc.c"
# 1 "./stdio.h" 1
nulll
# 2 "testcc.c" 2


int main() {
  printf("Hello World!\n" );



  printf("RISC-V");
  return 0;
}
```

我把这两个输出都作为了`.log`文件输出了，然后试着`diff`了一下，发现基本上头文件名字都是差不多的，无非是来源不一样











## E5

### Verilog的仿真行为&编码风格

阅读[verilog标准手册](http://staff.ustc.edu.cn/~songch/download/IEEE.1364-2005.pdf)，

#### 关于执行：

> 11.1 Execution of a model 
> The balance of the clauses of this standard describe the behavior of each of the elements of the language. This clause gives an overview of the interactions between these elements, especially with respect to the scheduling and execution of events. 
>
> The elements that make up the Verilog HDL can be used to describe the behavior, at varying levels of abstraction, of electronic hardware. An HDL has to be a parallel programming language. The execution of certain language constructs is defined by parallel execution of blocks or processes. It is important to understand what execution order is guaranteed to the user and what execution order is indeterminate. 
>
> Although the Verilog HDL is used for more than simulation, the semantics of the language are defined for simulation, and everything else is abstracted from this base definition.

Verilog是在各种的抽象层面描述电路硬件的行为，而HDL是一种并行编程语言，部分语言成分的执行被定义为代码块 / 过程的并行执行。因此**需要明确什么执行顺序是被保证的**。它是为了仿真而定义的

#### 基于事件的仿真

继续看手册下一部分：

> The Verilog HDL is defined in terms of a discrete event execution model.

基于离散事件的执行模型我们定义的verilog

> A design consists of connected threads of execution or processes.
>  Processes are objects that can be evaluated, that may have state, and that can respond to changes on their inputs to produce outputs. Processes include primitives, modules, initial and always procedural blocks, continuous assignments, asynchronous tasks, and procedural assignment statements.

Verilog里面的**过程**是可以被求值的对象，它们有状态，也可以响应输入变化产生输出。
而所谓**过程** 包含：`primitive`原语(如`add(y, a, b)`) / 模块 / `initial` / `always` 过程块 / 连续赋值 / 异步任务 / 过程赋值语句

> Every change in value of a net or variable in the circuit being simulated, as well as the named event, is considered an update event. 
> Processes are sensitive to update events. When an update event is executed, all the processes that are sensitive to that event are evaluated in an arbitrary order. The evaluation of a process is also an event, known as an evaluation event. 

仿真电路的线网 / 变量的值的变化 / 命名事件，都会被视为一个**更新事件。**
**过程对更新事件敏感**，执行一个更新事件后对该事件敏感的所有过程都会被求值，求值顺序是任意的，一个过程的求值也被视为一个事件，称为**求值事件**

> Events can occur at different times. In order to keep track of the events and to make sure they are processed in the correct order, the events are kept on an event queue, ordered by simulation time. Putting an event on the queue is called scheduling an event.

事件可以在不同时间(仿真时间)出现，为了保证事件的顺序和追踪事件，它们会被放到一个由仿真器确定顺序事件队列里面，这称为**“事件的调度”**

显然可以发现，**Verilog语言成分的语义都和事件有关**，仿真的过程就是按照正确的顺序处理这些事件的过程。处理的过程中电路中对象的状态会发生改变，需要的就是这符合我们的预期

#### 层次化事件队列

在下一章11.3就介绍了分层的事件队列，划分为5个区域：

- **激活事件(Active event)**：记录为$R_1$，存放发生在当前仿真时刻且能被处理的事件。
  	这就是我们一个simulation time 执行的东西
- **未激活事件(Inactive event)**：记录为$R_2$，存放在当前仿真时刻但是不能被立即处理，需要先把$R_1$内处理空才行
- **非阻塞赋值更新事件(nonblocking assign update event NBA)**区域：记录为$R_3$，存放在之前仿真时刻已经完成的求值，但需要在当前仿真时刻结束时才能进行赋值的事件，也就是需要$R1, R2$为空才可处理
- **监控事件(monitor event)**区域：$R_4$存放监控操作相关的事件，需要$R_1,R_2,R_3$全空才可以
- **未来事件(future event)**区域：$R_5$存放在未来仿真时刻才处理的事件

**一个仿真循环指的就是对所有激活事件的处理**
而verilog未定义的主要了来源就是激活事件的自由处理

一个具体的事件会按照类别被添加到不同的区域，按照一定的规则转移到$R_1$，被处理后从事件队列中移出。
一些事件的生成规则如下：

- 显式零延迟`#0`，使对应过程挂起，产生一个$R_2$事件 （你可以有意地调整执行顺序）
- 非阻塞赋值产生一个$R_3$事件
- 系统任务`$monitor` / `$strobe`会在每个仿真时刻产生一个$R_4$事件
- PLI例程的求值(如`vpi_register_cb(cbReadWriteSynch)`)会产生一个$R_2$事件

因此标准手册在11.4就给出了一个简单的事件处理引擎伪代码：
```pseudocode
while (there are events) {
  if (no active events) {
    if (there are inactive events) {
      activate all inactive events;
    } else if (there are nonblocking assign update events) {
      activate all nonblocking assign update events;
    } else if (there are monitor events) {
      activate all monitor events;
    } else {
      advance T to the next event time;
      activate all inactive events for time T;
    }
  }
  E = any active event;
  if (E is an update event) {
    update the modified object;
    add evaluation events for sensitive processes to event queue;
  } else { /* shall be an evaluation event */
    evaluate the process;
    add update events to the event queue;
  }
}
```

具体讲一下它的流程：

- $R_1$中有事件，取出这个事件`E`
  - `E`是一个更新事件：
    - 更新被修改的对象
    - 把 <u>对该事件敏感的过程的求值</u> 作为求值事件添加到事件队列中
  - 否，`E`是一个求值事件：
    - 对过程进行求值
    - 把赋值行为再作为更新事件添加到事件队列中
- 否，$R_1$空
  - $R_2$不空，把$R_2$所有事件放入$R_1$
  - 否，$R_2$也空，那就把$R_3$中所有事件放入$R_1$
  - 否，$R_3$也空，把$R_4$所有事件放入$R_1$
  - 否，那么：
    - 把仿真时刻前进一个单位
    - 把$R_5$中所有当前仿真时刻的事件按照类型转移为$R_1$ / $R_3$

因此很明显，我们写的Verilog本质会被转变为一个个事件，仿真器则是按照标准手册约定的某种顺序来处理这些事件，通过处理过程的结果反映出硬件电路的整体行为从而实现建模

#### 赋值操作的事件调度

第11.6节：赋值操作会转换为等价的过程从而产生相应的事件，来被仿真器处理：

- 连续赋值（`assign`）：对应一个对表达式源操作数都敏感的过程，一旦表达式的值发生变化就会产生一个更新事件添加到$R_1$中，特别地，连续赋值过程会产生一个`0`时刻的求值事件以此实现常量的传播
- 过程中的阻塞赋值：先使用对象的当前值计算赋值表达式右边的值，然后马上计算赋值表达式左边的赋值目标对象，对其进行更新，并产生由此更新导致的事件。执行过程可以继续按顺序执行下一条语句，也可以去处理其他激活事件。
- 过程中的非阻塞赋值：同样是先使用对象的当前值计算好右边的值和左边的赋值目标对象，但是产生一个$R_3$的事件

阻塞和非阻塞的区别就是阻塞是每次求值完了立刻会紧跟着更新操作，而非阻塞则是会把求值和更新操作分离，更新事件被放到了$R_3$事件里面，必须要前面两个$R_1 /R_2$搞定了才行

> 一个例子：
> ```verilog
> always @(posedge clk) begin
>     b = a;1
>     c <= b;1
>     d = c;3
>     e <= d;3
>     a = e;5
> end
> ```
>
> 如果当前时刻`a=1, b=2, c=3, d=4, e=5`，下一刻：
> b=1,d=3,a=5,c=1,e=3

##### 端口连接

对于输入端口`.a(expr)`，实际上等价于`assign a = expr`这条连续赋值语句；对于输出端口的连接`.b(net)`，会被视为`assign net = b`来处理

#### 事件处理顺序

事件处理的顺序并非完全确定，就像手册里面说的有2个来源：

- 事件序列中**多个激活事件的处理顺序是任意的**

- **行为模块中不带时间控制(`#`/`@`)的语句不必作为一整个事件来处理**

  对行为模块中的一条语句进行求值时，仿真器<u>可以随时挂起这条语句的执行</u>，并将剩下的执行操作作为事件队列中的一个激活事件，这样可以允许不同的过程交织执行。（尽管顺序不确定也不可控）

为什么要引入这些不确定性？因为**硬件电路本身就是并行性的**

- 从电路行为模型和真实电路的一致性来看，**并不存在规定这些组件之间先后顺序**的理由（你压根就没办法规范一个顺序出来）

- 从仿真器的软件本质来看，**仿真器却只能以串行方式处理不同的事件**

  因此我们引入不确定性，本身其实就是对事件处理顺序的放松
  仿真器甚至可以用一些并行优化技术来处理那些没有依赖关系的事件来更好地模拟电路组件间的并行性

为了全面地理解Verilog代码的行为，我们还需要考虑**事件处理顺序的确定性（上面的那个事件处理引擎还是隐含了顺序要求的）**

> 我们用A$\to$B表示先后顺序

- `顺序规则1`：如果处理过程中A生成B，则有：$A\to B$
- `顺序规则2`：如果在仿真过程中某一时刻，有$A \in R_i, B\in R_j$ 而且$i<j$，则$A\to B$. 这是因为事件处理引擎会在$R_i$中的事件都处理完后才会处理$R_j$的事件
- `顺序规则3` ：`begin`-`end`语句块中的语句需要按语句顺序执行. 也即, 对于同一个`begin`-`end`语句块中的两个语句$S_i$和$S_j$, 若$i<j$, 则$S_i \to S_j$.
- `顺序规则4` ：非阻塞赋值操作需要按语句的执行顺序来进行. 也即, 若$A, B \in R_3$, 相应的赋值表达式求值操作分别为$A'$和$B'$, 且有$A' \to B'$, 则$A \to B$.

比如标准手册的例子：
```verilog
initial begin
  a <= 0; // (1)
  a <= 1; // (2)
end
```

我们把这个操作拆解：$E_1:eval(0)$ ，$E_2:update(a)$，$E_3:eval(1) , E_4:update(a)$。

那么通过已有的规则我们知道：必须要有$E_1 \to E_2 , E_3 \to E_4$ （1），$E_1, E_3 \to  E_2, E_4$（2），$E_1 \to E_3$（3），$E_2 \to E_4$（4），那么唯一的组合就是$E_1 \to E_3 \to E_2 \to E_4$，最后结果就是先0后1

#### 仿真器和仿真程序

回顾流水灯的例子，分析事件处理顺序：
```verilog
module light(
  input clk,
  input rst,
  output reg [15:0] led
);
  reg [31:0] count;
  always @(posedge clk) begin
    if (rst) begin led <= 1; count <= 0; end
    else begin
      if (count == 0) led <= {led[14:0], led[15]};
      count <= (count >= 5000000 ? 32'b0 : count + 1);
    end
  end
endmodule

```

我们还是列出事件：E1-eval(1),E2-update(led), E3-eval(0), E4-update(counter), E5-eval({led[14:0], led[15]}), E6-update(led), E7-eval(count >= 5000000 ? 32'b0 : count + 1), E8-update(count)

那么根据规则，我们分情况讨论：

- `rst = 1`：自然是E1 E3 E2 E4
- `rst = 0, count = 0`：E5E7E6E8
- 剩下的：E7E8

那么我们可以用C代码来直接实现这个顺序：（这里`CONCAT`宏代表把这两个名字连在一起）
```c
#define EVAL(c, name, val) do { \
                             c->CONCAT(name, _next) = (val); \
                             c->CONCAT(name, _update) = 1; \
                           } while (0)
#define UPDATE(c, name)    do { \
                             if (c->CONCAT(name, _update)) { \
                               c->name = c->CONCAT(name, _next); \
                             } \
                           } while (0)

static void cycle(Circuit *c) {
  c->led_update = 0;
  c->count_update = 0;
  if (c->rst) {
    EVAL(c, led, 1);
    EVAL(c, count, 0);
  } else {
    if (c->count == 0) {
      EVAL(c, led, (BITS(c->led, 14, 0) << 1) | BITS(c->led, 15, 15));
    }
    EVAL(c, count, c->count >= 5000000 ? 0 : c->count + 1);
  }
  UPDATE(c, led);
  UPDATE(c, count);
}
```

这当然能仿真，但是不符合“事件队列”的概念，这里的C代码完全是按顺序平铺的，而非从一个队列中取出的，但是顺序本身却符合约定。而实际上Verilog官方手册对事件队列的定义是**逻辑上**的：（也就是说能达到相同的结果就行）

> The Verilog event queue is logically segmented into five different regions. 
> Events are added to any of the five regions, but are only removed from the active region.

上面把事件平铺的方法就叫**周期仿真(cycle simulation)**，以周期为粒度进行，顺序在仿真前就决定好了，属于事件的**静态调度**，这样压根就不需要调度，节省了调度开销也可以通过编译器进一步优化。显然这样不支持时序信息，只能用于同步电路的功能验证。verilator就是这种

> 看了看Verilator生成的代码，以流水灯为例：
> Vtop.h里面是对应的接口定义，在类`alignas`里面提供了对外的接口，内容在另一个Vtop___024root.h里面，不过我更关注事件本身，看起来似乎有一个事件队列的样子？

而完全符合我们上文提到的标准手册的事件处理引擎的实现则是“事件仿真”，仿真的过程中才确定了电路的求值顺序，属于动态调度，需要更多开销来维护事件队列和调度。但是优点就是能够更用于同步电路/异步电路/混合电路的功能验证和时序验证，开源的iVerilog / 商用的VCS之类的都是这种

#### 数据竞争

一个有效的真实电路在各个组件并行工作的情况下都应该得到一致的输出，但是如果存在两种不同的事件处理顺序导致仿真结果不一致，那么就是存在数据竞态的(race condition，和并发编程里面的可能也没差多少？本身就是并行的电路)

> ```verilog
> always @(posedge clk or negedge rstn) begin
>   if (!rstn) a = 1'b0;
>   else a = b; // (1)
> end
> 
> always @(posedge clk or negedge rstn) begin
>   if (!rstn) b = 1'b1;
>   else b = a; // (2)
> end
> ```
>
> 很显然这回有竞态，因为你当rst!=0的时候a=b和b=a都需要eval后立即update，都是$R_1$事件。
>
> 但是我们如果修改为非阻塞赋值就不会竞态了：
> ```verilog
> always @(posedge clk or negedge rstn) begin
>     if (!rstn) a <= 1'b0;
>   	else a <= b; // (1)
> end
> 
> always @(posedge clk or negedge rstn) begin
>     if (!rstn) b <= 1'b1;
>   	else b <= a; // (2)
> end
> ```
>
> 因为update一定是在eval之后的，所以只会交换对方的值（当然了肯定是非阻塞更符合寄存器的机制）

甚至和电路无关也会导致竞态：

> ```verilog
> always @(posedge clk or negedge rstn) begin
>   if (!rstn) a = 1'b0;
>   else a = 1;
> end
> 
> always @(posedge clk) begin
>   $display("a = %d", a);
> end
> ```
>
> 这里的问题就是如果原本a=0, rstn=1, clk上升沿到来，此时update(a)为1和$display(a)是会产生竞态的

 



**消除90%以上的数据竞争:**

1. **时序电路建模时, 用非阻塞赋值.**
2. **锁存器电路建模时, 用非阻塞赋值.**
3. **用`always`块建立组合逻辑模型时, 用阻塞赋值.**
4. **在同一个`always`块中建立时序和组合逻辑电路时, 用非阻塞赋值.**
5. **在同一个`always`块中不要既用非阻塞赋值又用阻塞赋值.**
6. **不要在一个以上的`always`块中为同一个变量赋值.**
7. **用`$strobe`系统任务来显示用非阻塞赋值的变量值.**
8. **在赋值时不要使用`#0`延迟.**



> **回答问题**：在这一小节的最开始提到了若干条Verilog的编码建议或描述, 但其中有一些是不正确的. 请尝试找出它们, 并分析它们为什么不正确:
>
> 1. 使用`#0`可以将赋值操作强制延迟到当前仿真时刻的末尾.
>
>    错误，只是变成了$R_2$变成Inactive，后面还有别的..
>
> 2. 在同一个`begin`-`end`语句块中对同一个变量进行多次非阻塞赋值, 结果是未定义的.
>
>    错误，同一个begin-end里面顺序严格规定，你只能从上往下执行，还是最后的NBA生效
>
> 3. 用`always`块描述组合逻辑元件时, 不能使用非阻塞赋值.
>
>    错误，你其实可以这么做，always后面里面跟的只是敏感的事件或变量，不用是为了我们减少数据竞态的可能性。我们只是不推荐这么做，你最好还是用`=`，要不然仿真推迟到$R_2$那就可能会反直觉
>
> 4. 不能在多个`always`块中对同一个变量进行赋值.
>
>    正确，它们不在一个begin-end里面，你无法约束谁先发生
>
> 5. 不建议使用`$display`系统任务, 因为有时候它无法正确输出变量的值.
>
>    错误，它本身应该是能输出的吧？你得防止竞态，因为它本身也是$R_1$的Active
>
> 6. `$display`无法输出非阻塞赋值语句的结果.
>
>    正确，NBA非阻塞更新被放在了$R_3$，还是$R_4$的`$strobe`更好（除非你要输出旧值）

### 综合器

使用yosys来synthesize，通过给的yosys-sta可以生成网表

#### parsing

```bash
$ yosys ./vsrc/lights.v 

 /----------------------------------------------------------------------------\
 |  yosys -- Yosys Open SYnthesis Suite                                       |
 |  Copyright (C) 2012 - 2026  Claire Xenia Wolf <claire@yosyshq.com>         |
 |  Distributed under an ISC-like license, type "license" to see terms        |
 \----------------------------------------------------------------------------/
 Yosys 0.68+132 (git sha1 13b43f8c8-dirty, Release, Clang /usr/bin/clang++ 21.1.8)

-- Parsing `./vsrc/lights.v' using frontend ` -vlog2k' --

1. Executing Verilog-2005 frontend: ./vsrc/lights.v
Parsing Verilog input from `./vsrc/lights.v' to AST representation.
Storing AST representation for module `$abstract\lights'.
Successfully finished Verilog frontend.
yosys>
```

#### 细化











#### 生成IR

格式.rtlil



#### 关于行为建模

对于初学者最好不要乱用行为建模， 下面的问题可以帮助大家测试自己是否已经掌握Verilog的本质:

- 在硬件描述语言中, "执行"的精确含义是什么?

  > 
  
- 是谁在执行Verilog的语句? 是电路，综合器，还是其它的?

  > 

- if的条件满足, 就不执行else后的语句, 这里的"不执行"又是什么意思? 和描述电路有什么联系?

  > 
  
- 有"并发执行", 又有"顺序执行", 还有"任何一个变量发生变化就立即执行", 以及"在任何情况下都执行", 它们都是如何在设计出来的电路中体现的?

  > 

而实际上对于真实的电路，无非就是告诉综合器如何连线而已，我们以二选一mux来说明这个问题：

- **结构化建模**：关注电路由什么组成，直接描述电路由模块和线的连接，最原始但是也最不可能出错的方法，比如：

  ```verilog
  module mux21(
  	input a,
      input b,
      input sel,
      output y
  );
      wire n1, n2;
      and(n1, a, ~sel);
      and(n2, b, sel);
      or(y, n1, n2);
  endmodule
  ```

  这里就是直接通过逻辑门和接线来描述了这个mux，很直观也没有歧义，但是有些麻烦

- **数据流建模**：关注数据如何传输，这个最好理解，比如：

  ```verilog
  module mux21(
  	input a,
      input b,
      input sel,
      output y
  );
      y = sel ? b : a;
  endmodule
  ```

  这个则是让综合器来自己推断结构，又比如说：`assign sum = a + b;`也是如此。

- **行为建模**：关注在某些事件发生时，状态如何变化
  最经典的就是：

  ```verilog
  always @(posedge clk)
      begin
          if(reset)
              q <= 0;
          else
              q <= 1'b1;
      end
  ```

  这当然很方便，但是你得清楚你在写什么。当然我们完全可以用最基本的结构化建模来做这件事，但是为了方便，我们才引入了`always`这种抽象，让综合器来帮我们处理细节。但是还是我们需要明白这是否对应一个真实的电路。。
  一个经典的案例就是：

  ```verilog
  always @(posedge clk) begin
      if(a)
          x <= m;
      if(b)
          x <= n;
  ```

  很可能你会认为这是顺序执行的，但是这个电路本身有歧义，你不能明确具体的先后顺序，也不知道谁覆盖谁，那就是未定义的。

  > 如果你一定要用，记住只用一个posedge不要和negedge混用，很麻烦，你这样会影响整块SoC的时序



通用的模板：
```verilog
// 触发器模板
module Reg #(WIDTH = 1, RESET_VAL = 0) ( 	 // #() 代表传入参数而非接线
  input clk,
  input rst,
  input [WIDTH-1:0] din,
  output reg [WIDTH-1:0] dout,
  input wen
);
  always @(posedge clk) begin
    if (rst) dout <= RESET_VAL;
    else if (wen) dout <= din;
  end
endmodule

// 使用触发器模板的示例
module example(
  input clk,
  input rst,
  input [3:0] in,
  output [3:0] out
);
  // 位宽为1比特, 复位值为1'b1, 写使能一直有效
  Reg #(1, 1'b1) i0 (clk, rst, in[0], out[0], 1'b1);
  // 位宽为3比特, 复位值为3'b0, 写使能为out[0]
  Reg #(3, 3'b0) i1 (clk, rst, in[3:1], out[3:1], out[0]);
endmodule
```





### 南京大学数字电路实验：

#### 实验2：译码器和解码器

首先是解码器，懒得写好几次，我直接写了一个模板在`top.v`里面引用：
```verilog
module Decoder #(parameter INPUT_WIDTH=2) (
  input [INPUT_WIDTH-1:0] in,
  input en,
  output reg [(1<<INPUT_WIDTH)-1:0] out
);
always @(*) begin
    if (en) begin
        out = 0;
        out[in] = 1'b1;
    end
end
endmodule

```

由于不太好放到nvboard上面，我就用gtkwave来验证了：
![image-20260827164016983](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260827164016983.png)

> 官方的写法是：
> ```verilog
> always @(x or en) begin ...
> ```
>
> 但是其实现在的写法是：
>
> ```verilog
> always @(*) begin ...
> ```
>
> 这样就不会漏，直接把所有有用的输入放入敏感列表

---

> 以及其实还可以写for循环，它就是把这个循环展开后的作为结果：
> ```verilog
> module decode38(x,en,y);
>   input  [2:0] x;
>   input  en;
>   output reg [7:0]y;
>   integer i;
> 
>   always @(x or en)
>     if (en) begin
>       for( i = 0; i <= 7; i = i+1)
>           if(x == i)
>                 y[i] = 1;
>           else
>                 y[i] = 0;
>     end
>     else
>       y = 8'b00000000;
> 
> endmodule
> ```
>
> 因此这种机制甚至可以用来生成多个模块，即所谓**`generate-for`**，用`genvar`声明index变量：
>
> ```verilog
> genvar i;
> generate
>     for(i=0;i<8;i=i+1) begin
>         Decoder dec(
>             .x(x[i]),
>             .y(y[i])
>         );
>     end
> endgenerate
> ```
>
> 既然如此，为什么`generate-for`需要专门声明为`genvar`，而不仅仅是`integer`呢？
>
> 因为这和普通语句在仿真器看来是不同的，`generate-for`是相当于写多个语句`Decoder ...`，实际执行仿真时压根就没有i了。但是普通语句仿真时还是真的需要一个index来执行语句的。对于综合器同样如此，综合器面对普通语句会尝试把整个for翻译为对应的逻辑门，但是`generate-for`则是直接生成多个实例



然后是编码器，同样我写了一个模板：（都是从高到低扫的）

> `$clog2`是systemVerilog里面的，不过这里也支持

```verilog
// 优先编码器
module Encoder #(parameter INPUT_WIDTH,parameter OUTPUT_WIDTH = (INPUT_WIDTH <= 1) ? 1 : $clog2(INPUT_WIDTH)) (
  input [INPUT_WIDTH-1:0] in,
  input en,
  output reg [OUTPUT_WIDTH-1:0] out,
  output reg  valid
);
integer i;
always @(*) begin
 out = 0;
 if(en) begin
     valid = en && (|in) && (in & (in - 1) == 0);       // 保证有且仅有1个1
     for(i = INPUT_WIDTH-1; i >= 0; i = i - 1) begin 
       if(in[i]) 
         out = i;
     end
 end
end

endmodule
// 普通编码器
module PriorEncoder #(parameter INPUT_WIDTH,parameter OUTPUT_WIDTH = (INPUT_WIDTH <= 1) ? 1 : $clog2(INPUT_WIDTH)) (
  input [INPUT_WIDTH-1:0] in,
  input en,
  output reg [OUTPUT_WIDTH-1:0] out,
  output reg  valid
);
integer i;
always @(*) begin
 out = 0;
 valid = 1'b0;
 for(i = INPUT_WIDTH - 1; i >= 0; i = i - 1) begin
   if(!valid && in[i]) begin
     out = i;
     valid = 1'b1;
   end
 end
end

endmodule

```

后者验证结果是：
![image-20260827183616967](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260827183616967.png)

而数码管：
```verilog
module bcd7seg(
  input [3:0] b,
  output reg [7:0] h
);
// NVBoard 约定：h[7:0] = {A,B,C,D,E,F,G,DP}，低电平点亮（0 = 亮，1 = 灭）
always @(*) begin
  case(b)
    4'b0000 : h = 8'h03;
    4'b0001 : h = 8'h9f;
    4'b0010 : h = 8'h25;
    4'b0011 : h = 8'h0d;
    4'b0100 : h = 8'h99;
    4'b0101 : h = 8'h49;
    4'b0110 : h = 8'h41;
    4'b0111 : h = 8'h1f;
    4'b1000 : h = 8'h01;
    4'b1001 : h = 8'h09;
    4'b1010 : h = 8'h11;
    4'b1011 : h = 8'hc1;
    4'b1100 : h = 8'h63;
    4'b1101 : h = 8'h85;
    4'b1110 : h = 8'h61;
    4'b1111 : h = 8'h71;
    default: h = 8'hff;
  endcase
end
endmodule

```



![image-20260827201554900](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260827201554900.png)







#### 实验3：加法器 & ALU

Adder用了之前做Data Lab时额外查到的方法：
```verilog
module Adder #(parameter WIDTH = 4) (
  input [WIDTH-1:0] in1,
  input [WIDTH-1:0] in2,
  input sign,               // sub=1 add=0
  output [WIDTH-1:0] out_s,
  output out_c
);
  assign {out_c, out_s} = in1 + (in2 ^ {WIDTH{sign}}) + sign;
endmodule
```

![image-20260827204635795](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260827204635795.png)

Alu：
```verilog
module Alu #(parameter WIDTH = 4) (
  input [2:0] mode,
  input [WIDTH-1:0] a,
  input [WIDTH-1:0] b,
  output reg [WIDTH-1:0] out,
  output reg iszero,              // 是否为0
  output reg iscarry,            // 是否进位unsigned
  output reg isoverflow         // 是否溢出signed
);
always @(*) begin
  out = 0;
  iscarry = 0;
  isoverflow = 0;
  iszero = 0;
case (mode)
  3'b000: begin       // add
    {iscarry, out} = {1'b0, a} + {1'b0, b};
    isoverflow = (a[WIDTH-1] == b[WIDTH-1]) && (out[WIDTH-1] != a[WIDTH-1]); 
  end
  3'b001: begin     // sub
    {iscarry, out} = {1'b0, a} + {1'b0, ~b} + {{WIDTH{1'b0}},1'b1};
    isoverflow = (a[WIDTH-1] != b[WIDTH-1]) && (out[WIDTH-1] != a[WIDTH-1]);
  end
  3'b010: begin     // not
    out = ~a;
  end
  3'b011: begin     // and
    out = a & b;
  end
  3'b100: begin     // or
    out = a | b;
  end
  3'b101: begin     // xor
    out = a ^ b;
  end
  3'b110: begin     // a < b
    out = {{(WIDTH-1){1'b0}}, ($signed(a) < $signed(b))};
  end
  3'b111: begin
    out = {{(WIDTH-1){1'b0}}, (a == b)};
  end
endcase
    iszero = ~|out;
end

endmodule
```

为了验证我test_bench穷举了所有可能的情况

![image-20260828104145417](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260828104145417.png)



#### 实验4：计数器/时钟

一个简单的计数器（我加入了步长和计数方向的输入）：
```verilog
module Counter #(
  parameter WIDTH=4
) (
  input clk,
  input rst,
  input en,
  input sub,                    // 0 add 1 sub
  input [WIDTH-1:0] step,
  output reg [WIDTH-1:0] out
);
wire [WIDTH-1:0] next_out;
wire tmp;
Adder #(
  .WIDTH(WIDTH)) c_adder(
  .in1(out),
  .in2(step),
  .sign(sub),
  .out_s(next_out),
  .out_c(tmp)
);
always @(posedge clk) begin      // 同步复位
  if (rst) out <= 0;
  else if (en)  out <= next_out;
end

endmodule

```



![image-20260828125533317](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260828125533317.png)















































