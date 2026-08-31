

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

把这两个输出都作为了`.log`文件输出，然后试着`diff`了一下，发现基本上头文件名字都是差不多的，无非是来源不一样











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

#### 解析 Parsing

这一步是把高层级的RTL翻译为AST

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

#### 细化 Elaboration

细化阶段工作包括：

- 解析模块间实例化关系
- 计算模块实力的参数
- 完成模块实例化的实例名和端口名绑定

开展细化工作：（意思是我们指定一个顶层模块，yosys以这个顶层模块为起点，依次展开所有实例化的子模块，从而确定整个设计的边界，并且删除不需要的模块
这把整个设计的AST转换为yosys的一种中间语言RTLIL(就是一种IR)

```bash
yosys> hierarchy -check -top lights

2. Executing HIERARCHY pass (managing design hierarchy).

3. Executing AST frontend in derive mode using pre-parsed AST for module `\lights'.
Generating RTLIL representation for module `\lights'.

3.1. Analyzing design hierarchy..
Top module:  \lights

3.2. Analyzing design hierarchy..
Top module:  \lights
Removing unused module `$abstract\lights'.
Removed 1 unused modules.

```

#### 语义分析

这玩意可以干类似编译器的语义分析工作

#### 查看生成IR

```bash
yosys> dump
	// or
yosys> write_rtlil counter.rtlil

autoidx 6

attribute \src "lights.v:1.1-14.10"
attribute \top 1
attribute \hdlname "lights"
module \lights

  attribute \src "lights.v:2.9-2.12"
  wire input 1 \clk

  attribute \src "lights.v:3.9-3.12"
  wire input 2 \rst

  attribute \src "lights.v:4.21-4.24"
  wire width 16 output 3 \led

  attribute \src "lights.v:6.14-6.19"
  wire width 32 \count

  attribute \src "lights.v:7.3-13.6"
  wire width 16 $0\led[15:0]

  attribute \src "lights.v:7.3-13.6"
  wire width 32 $0\count[31:0]

  attribute \src "lights.v:10.11-10.21"
  wire $eq$lights.v:10$2_Y

  attribute \src "lights.v:11.17-11.33"
  wire $ge$lights.v:11$3_Y

  attribute \src "lights.v:11.44-11.53"
  wire width 32 $add$lights.v:11$4_Y

  attribute \src "lights.v:11.17-11.53"
  wire width 32 $ternary$lights.v:11$5_Y

  attribute \src "lights.v:10.11-10.21"
  cell $eq $eq$lights.v:10$2
    parameter \A_SIGNED 0
    parameter \B_SIGNED 0
    parameter \A_WIDTH 32
    parameter \B_WIDTH 32
    parameter \Y_WIDTH 1
    connect \A \count
    connect \B 0
    connect \Y $eq$lights.v:10$2_Y
  end

  attribute \src "lights.v:11.17-11.33"
  cell $ge $ge$lights.v:11$3
    parameter \A_SIGNED 0
    parameter \B_SIGNED 0
    parameter \A_WIDTH 32
    parameter \B_WIDTH 32
    parameter \Y_WIDTH 1
    connect \A \count
    connect \B 5000000
    connect \Y $ge$lights.v:11$3_Y
  end

  attribute \src "lights.v:11.44-11.53"
  cell $add $add$lights.v:11$4
    parameter \A_SIGNED 0
    parameter \B_SIGNED 0
    parameter \A_WIDTH 32
    parameter \B_WIDTH 32
    parameter \Y_WIDTH 32
    connect \A \count
    connect \B 1
    connect \Y $add$lights.v:11$4_Y
  end

  attribute \src "lights.v:11.17-11.53"
  cell $mux $ternary$lights.v:11$5
    parameter \WIDTH 32
    connect \A $add$lights.v:11$4_Y
    connect \B 0
    connect \S $ge$lights.v:11$3_Y
    connect \Y $ternary$lights.v:11$5_Y
  end

  attribute \src "lights.v:7.3-13.6"
  process $proc$lights.v:7$1
    assign $0\led[15:0] \led
    assign $0\count[31:0] \count
    attribute \src "lights.v:8.5-12.8"
    switch \rst
    attribute \src "lights.v:8.9-8.12"
      case 1'1
        assign $0\led[15:0] 16'0000000000000001
        assign $0\count[31:0] 0
    attribute \src "lights.v:9.5-9.9"
      case 
        assign $0\count[31:0] $ternary$lights.v:11$5_Y
        attribute \src "lights.v:10.7-10.51"
        switch $eq$lights.v:10$2_Y
        attribute \src "lights.v:10.11-10.21"
          case 1'1
            assign $0\led[15:0] { \led [14:0] \led [15] }
          case 
        end
    end
    sync posedge \clk
      update \led $0\led[15:0]
      update \count $0\count[31:0]
  end
end

```

> 补充一下[官方文档](https://yosyshq.readthedocs.io/projects/yosys/en/latest/yosys_internals/formats/rtlil_rep.html#)的总结：关于rtlil
>
> 除了使用AST的高等级前端表示（用于生成RTLIL前面的一步），其他都是用RTLIL来表示的
> 为了避免重复，这些RTLIL的类直接参考他们的C++全名，也就是说会包含`RTLIL::`这个命名空间前缀
>
> 下图是一个简单的ER图，只有一个激活的`RTLIL::Design`对象，其包含若干个`RTLIL::module`对象，这就是具体的module了
> ![image-20260829020414329](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260829020414329.png)

- `attribute`用于标识一些属性，例如`attribute \src "lights.v:7.3-13.6"`标识的是相应元素在源文件的位置（7行3列到13行6列）
- `wire width 16 $0\led[15:0]`表示定义了一个16位宽的信号，名称为`$0\led[15:0]`（注意这一整个才是名称）
- `  cell $add $add$lights.v:11$4`标识实例化一个类型为`$add`的单元，名称为`$add$lights.v:11$4`，参数用`parameter`标识，`parameter \A_SIGNED 0`标识A无符号，`parameter \A_WIDTH 32`标识位宽；` connect \A \count`标识把A连接到`count`
- `process`标识一个行为描述过程，`assign`就代表信号的赋值，`switch-case`则是条件性对信号的值赋值，`sync`标识满足条件时更新信号

由此看来虽然形式不一样但是还是存在对应关系的，只不过我们这里运算符被`cell`取代了，而这里的`$add`属于[Internal cell lib](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cell_index.html)

显然这里已经描述了电路的拓扑关系和行为过程，我们可以用`Graphviz dot`类型文件的查看工具`xdot`，随后在yosys执行`show`即可自动调用`xdot`等工具查看：（保存在`~/.yosys_show.dot`

![image-20260829111413636](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260829111413636.png)

#### 粗粒度综合

粗粒度综合阶段负责基于设计的“粗粒度表示”处理，这里粗粒度表示指采用字级单元(word-level cells)描述设计，它是yosys内部单元库的其中一部分。这些单元处于相对较高的抽象层次，尚且还支持多位宽和参数的功能。
命名风格：字级单元统一用`$`作为prefix

我们上面elaborating已经建立了结构部分，就像`$add`/`$mux`这种，但是`always`产生的时序控制行为还在`process`中，还没有变成cell那种粗粒度表示，我们需要`proc`pass来彻底降低为结构化RTLIL，以方便我们进行相关的处理工作。
```bash 
yosys> proc

5. Executing PROC pass (convert processes to netlists).

5.1. Executing PROC_CLEAN pass (remove empty switches from decision trees).
Cleaned up 0 empty switches.

5.2. Executing PROC_RMDEAD pass (remove dead branches from decision trees).
Marked 1 switch rules as full_case in process $proc$lights.v:7$1 in module lights.
Removed a total of 0 dead cases.

5.3. Executing PROC_PRUNE pass (remove redundant assignments in processes).
Removed 1 redundant assignment.
Promoted 0 assignments to connections.

5.4. Executing PROC_INIT pass (extract init attributes).

5.5. Executing PROC_ARST pass (detect async resets in processes).

5.6. Executing PROC_ROM pass (convert switches to ROMs).
Converted 0 switches.
<suppressed ~2 debug messages>

5.7. Executing PROC_MUX pass (convert decision trees to multiplexers).
Creating decoders for process `\lights.$proc$lights.v:7$1'.
     1/2: $0\count[31:0]
     2/2: $0\led[15:0]

5.8. Executing PROC_DLATCH pass (convert process syncs to latches).

5.9. Executing PROC_DFF pass (convert process syncs to FFs).
Creating register for signal `\lights.\led' using process `\lights.$proc$lights.v:7$1'.
  created $dff cell `$procdff$14' with positive edge clock.
Creating register for signal `\lights.\count' using process `\lights.$proc$lights.v:7$1'.
  created $dff cell `$procdff$15' with positive edge clock.

5.10. Executing PROC_MEMWR pass (convert process memory writes to cells).

5.11. Executing PROC_CLEAN pass (remove empty switches from decision trees).
Found and cleaned up 2 empty switches in `\lights.$proc$lights.v:7$1'.
Removing empty process `lights.$proc$lights.v:7$1'.
Cleaned up 2 empty switches.

5.12. Executing OPT_EXPR pass (perform const folding).
Optimizing module lights.
<suppressed ~1 debug messages>


```

`proc`命令其实是一条宏命令(macro command), 它会依次调用一系列子命令来完成过程描述的转换:

| 步骤 |       子命令       |                          说明                          |
| :--: | :----------------: | :----------------------------------------------------: |
|  1   |    `proc_clean`    |                移除空分支和空的过程描述                |
|  2   |   `proc_rmdead`    |                 移除不可达的`case`分支                 |
|  3   |    `proc_prune`    |        移除冗余的赋值操作(被后续赋值操作所覆盖)        |
|  4   |    `proc_init`     |  将过程描述中的`init`操作转换为相应信号上的`init`属性  |
|  5   |    `proc_arst`     |                      识别异步复位                      |
|  6   |     `proc_rom`     |      将过程描述中的`switch`操作在适合时转换为ROM       |
|  7   |     `proc_mux`     | 将过程描述中的`switch`操作转换为`$mux`单元(多路选择器) |
|  8   |   `proc_dlatch`    |      将过程描述中的锁存器转换为D锁存器类型的单元       |
|  9   |     `proc_dff`     |      将过程描述中的触发器转换为D触发器类型的单元       |
|  10  |    `proc_memwr`    |      将过程描述中的存储器写操作转换为`$memwr`单元      |
|  11  |    `proc_clean`    |                移除空分支和空的过程描述                |
|  12  | `opt_expr -keepdc` |                  进行表达式相关的优化                  |

再次`show`一次：（很显然这里原本的`proc`被彻底取代为了对应的`cell`，`dump`一下也会发现后面改变）
![image-20260829113857095](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260829113857095.png)

#### 优化

我们可以进一步优化来化简这个网络结构（上面那个一看就很丑）
```bash
yosys> opt

7. Executing OPT pass (performing simple optimizations).

7.1. Executing OPT_EXPR pass (perform const folding).
Optimizing module lights.

7.2. Executing OPT_MERGE pass (detect identical cells).
Finding identical cells in module `\lights'.
Computing hashes of 9 cells of `\lights'.
Finding duplicate cells in `\lights'.
Removed a total of 0 cells.

7.3. Executing OPT_MUXTREE pass (detect dead branches in mux trees).
Running muxtree optimizer on module \lights..
  Creating internal representation of mux trees.
  Evaluating internal representation of mux trees.
  Analyzing evaluation results.
Removed 0 multiplexer ports.
<suppressed ~6 debug messages>

7.4. Executing OPT_REDUCE pass (consolidate $*mux and $reduce_* inputs).
  Optimizing cells in module \lights.
Performed a total of 0 changes.

7.5. Executing OPT_MERGE pass (detect identical cells).
Finding identical cells in module `\lights'.
Computing hashes of 9 cells of `\lights'.
Finding duplicate cells in `\lights'.
Removed a total of 0 cells.

7.6. Executing OPT_DFF pass (perform DFF optimizations).
Adding SRST signal on $procdff$14 ($dff) from module lights (D = $procmux$9_Y, Q = \led, rval = 16'0000000000000001).
Adding EN signal on $auto$ff.cc:337:slice$16 ($sdff) from module lights (D = { \led [14:0] \led [15] }, Q = \led).
Adding SRST signal on $procdff$15 ($dff) from module lights (D = $add$lights.v:11$4_Y, Q = \count, rval = 0).

7.7. Executing OPT_CLEAN pass (remove unused cells and wires).
Finding unused cells or wires in module \lights..
Removed 4 unused cells and 9 unused wires.
<suppressed ~5 debug messages>

7.8. Executing OPT_EXPR pass (perform const folding).
Optimizing module lights.

7.9. Rerunning OPT passes. (Maybe there is more to do..)

7.10. Executing OPT_MUXTREE pass (detect dead branches in mux trees).
Running muxtree optimizer on module \lights..
  Creating internal representation of mux trees.
  No muxes found in this module.
Removed 0 multiplexer ports.

7.11. Executing OPT_REDUCE pass (consolidate $*mux and $reduce_* inputs).
  Optimizing cells in module \lights.
Performed a total of 0 changes.

7.12. Executing OPT_MERGE pass (detect identical cells).
Finding identical cells in module `\lights'.
Computing hashes of 6 cells of `\lights'.
Finding duplicate cells in `\lights'.
Removed a total of 0 cells.

7.13. Executing OPT_DFF pass (perform DFF optimizations).

7.14. Executing OPT_CLEAN pass (remove unused cells and wires).
Finding unused cells or wires in module \lights..

7.15. Executing OPT_EXPR pass (perform const folding).
Optimizing module lights.

7.16. Finished fast OPT passes. (There is nothing left to do.)

```

和上文介绍的`proc`类似, `opt`也是一条宏命令, 它会依次调用一系列子命令来开展各种优化:

| 步骤 |       子命令       |                     说明                     |
| :--: | :----------------: | :------------------------------------------: |
|  1   |     `opt_expr`     |           常量合并和简单表达式改写           |
|  2   | `opt_merge -nomux` |   合并相同的单元, 但不合并选择器类型的单元   |
|      |        `do`        |                   开始循环                   |
|  3   |   `opt_muxtree`    |         移除嵌套选择器中的不可达分支         |
|  4   |    `opt_reduce`    |        简化多输入的选择器, 与门和或门        |
|  5   |    `opt_merge`     |                合并相同的单元                |
|  6   |    `opt_share`     | 合并输入相同, 类型相同, 且不会同时激活的单元 |
|  7   |     `opt_dff`      |     D触发器的常量优化和时钟复位信号合并      |
|  8   |    `opt_clean`     |             移除无用的单元和线网             |
|  9   |     `opt_expr`     |           常量合并和简单表达式改写           |
|      | `while (changed)`  |    若设计发生变化, 则跳转到第3步继续循环     |

很明显这个电路被大大化简了：
![image-20260829114206013](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260829114206013.png)

一些常见的优化技术：

- 常量合并和简单表达式改写(第一步`opt_expr`)：

  显然有些表达式写的很可能不是最简单的，比如：
  ```verilog
  //          优化前              |            优化后
    wire a, b, c, x, y, z;       |    wire a, b, c, x, y, z;
    // ......                    |    // ......
    assign x = a != a;           |    assign x = 1'0;
    assign y = b | x;            |    assign y = b;
    assign z = c == x;           |    assign z = ~c;
  ```

  这里首先`a!=a`是结果可以直接判定为0，故可优化为`assign x = 1'b0`，进一步应用常量传播优化技术，表达式`b | x`的结果必然是b，就可以优化为`assign y=b`，而`c==x`=`~c`也是如此

- 合并相同单元(`opt_merge`)：

  对于多个功能和输入都相同的单元，可以合并为一个单元，让其输出驱动原来的各输出信号，进而减少单元数量
  ```verilog
  //          优化前              |            优化后
    wire a, b, x, y;             |    wire a, b, x, y;
    // ......                    |    // ......
    assign x = a + b;            |    assign x = a + b;
    assign y = b + a;            |    assign y = x;
  ```

  > 但是这种优化不是没有代价的！
  >
  > 具体来说，你这样会增加了这个单元的扇出，学过数字电路就知道扇出大会影响性能，增大电路延迟（高频下MOS等效寄生电容会比较明显，充电到完成翻转需要时间）

- 移除嵌套选择器里面的不可达分支（`opt_muxtree`）：

  某些分支其实在嵌套选择里面根本不可能达到，比如一个极端案例：
  ```verilog
  //          优化前              |            优化后
    wire a, b, c, d, x;             |    wire a, b, c, d, x;
    // ......                       |    // ......
    assign x = a ? (a ? b : c) : d; |    assign x = a ? b : d;
  ```

  显然这里根本就不可能达到c，`(a?b:c)`只可能是b

- 简化多输入选择器 / 与或门(`opt_reduce`)：

  主要是输入有可能相同，可以合并消除：（比如下面这个符号扩展）
  ```verilog
  //          优化前              |            优化后
    wire [31:0] inst, imm;          |    wire [31:0] inst, imm;
    wire sel, x;                    |    wire sel, x;
    // ......                       |    // ......
    assign imm = !sel ? 32'b0 :     |    assign imm[11:0] = !sel ? 12'b0 : inst[31:20];
      {{20{inst[31]}}, inst[31:20]};|    assign imm[31:12] = {20{imm[11]}};
    assign x = &imm;                |    assign x = &imm[11:0];
  ```

  这里我们发现，`imm`的高20位似乎只和它的第11位有关，换句话说压根用不到那么宽的位宽，只需要先计算出低12位后把imm[11]扩展自动就是我们的最终答案（因为前面选择的时候已经发现这一点了

- D触发器常量优化(`opt_dff`)：

  如果D触发器的数据输入端为常量，我们完全可以直接把它替换为常量，从而移除不必要的D触发器单元，比如：
  ```verilog
  //          优化前              |            优化后
    reg [31:0] r;                   |    wire [31:0] r;
    // ......                       |    // ......
    always @ (posedge clk)          |    assign r = 32'hdeadbeef;
      r <= 32'hdeadbeef;            |
  ```

- 移除无用的单元和线网(`opt_clean`)：

  如果某些单元和线网不影响模块的输出，就可以移除
  ```verilog
  //          优化前              |            优化后
    module m(                       |    module m(
      input a, b;                   |      input a, b;
      output x;                     |      output x;
    );                              |    );
      wire t;                       |      assign x = a + b;
      assign x = a + b;             |    endmodule
      assign t = a & b;             |
    endmodule                       |
  ```

[更详细的内容](https://yosyshq.readthedocs.io/projects/yosys/en/latest/using_yosys/synthesis/opt.html)

#### fsm的识别

复杂的FSM中可能包含一些冗余 / 可合并状态，输入输出，这在运算符类别的字集单元上很难发现，所以综合器一般会在字级单元上识别出FSM，然后在FSM的语义上对其分析优化，最后在映射回字级单元

```verilog
yosys> fsm

10. Executing FSM pass (extract and optimize FSM).

10.1. Executing FSM_DETECT pass (finding FSMs in design).

10.2. Executing FSM_EXTRACT pass (extracting FSM from design).

10.3. Executing FSM_OPT pass (simple optimizations of FSMs).

10.4. Executing OPT_CLEAN pass (remove unused cells and wires).
Finding unused cells or wires in module \lights..

10.5. Executing FSM_OPT pass (simple optimizations of FSMs).

10.6. Executing FSM_RECODE pass (re-assigning FSM state encoding).

10.7. Executing FSM_INFO pass (dumping all available information on FSM cells).

10.8. Executing FSM_MAP pass (mapping FSMs to basic logic).
```

显然这还是一个macro，主要的处理步骤包括:

1. `fsm_detect` - FSM检测, 根据一定的规则在RTLIL中**识别**出FSM, 并用特殊属性**标记**相关单元

2. `fsm_extract` - FSM抽取, 将标记的相关单元用`$fsm`单元**替代**, 并解析出**状态转移表**

3. `fsm_opt` - FSM优化, 根据状态转移表对FSM进行优化

   > 包括移除无用的输出信号, 合并上游相同的输入信号, 合并相同状态下输出相同的不同输入, 根据常量输入简化状态等

4. `fsm_recode` - FSM重编码, 使用独热码对状态信号进行重新编码

5. `fsm_map` - 单元映射, 将处理后的`$fsm`单元映射回字级单元

当然我们可以说任何一个RTL都可以看作一个FSM，但是这太麻烦了（状态转移表过分庞大 + 难以优化）

#### 存储器的识别处理

另一种需要特殊处理的单元就是存储器了：
```bash
yosys> memory

11. Executing MEMORY pass.

11.1. Executing OPT_MEM pass (optimize memories).
Performed a total of 0 transformations.

11.2. Executing OPT_MEM_PRIORITY pass (removing unnecessary memory write priority relations).
Performed a total of 0 transformations.

11.3. Executing OPT_MEM_FEEDBACK pass (finding memory read-to-write feedback paths).

11.4. Executing MEMORY_BMUX2ROM pass (converting muxes to ROMs).

11.5. Executing MEMORY_DFF pass (merging $dff cells to $memrd).

11.6. Executing OPT_CLEAN pass (remove unused cells and wires).
Finding unused cells or wires in module \lights..

11.7. Executing MEMORY_SHARE pass (consolidating $memrd/$memwr cells).

11.8. Executing OPT_MEM_WIDEN pass (optimize memories where all ports are wide).
Performed a total of 0 transformations.

11.9. Executing OPT_CLEAN pass (remove unused cells and wires).
Finding unused cells or wires in module \lights..

11.10. Executing MEMORY_COLLECT pass (generating $mem cells).

11.11. Executing MEMORY_MAP pass (converting memories to logic and flip-flops).
```

相关处理包含 将上下游的触发器合并到存储器的读写单元，将存储器的多个读写单元合并为一个多端口的存储器单元等等

对于FPGA，由于存储器件类型很少（LUT  RAM / BLOCK RAM / FF），FPGA综合器就可以通过上述方法自己在RTL中识别出存储器并根据识别出的存储器属性映射到物理的存储器器件。**综合器可以按需分配存储器器件**

对于ASIC，并没有可编程的存储器单元，而是由**标准单元库提供的若干种确定规格的存储器**供RTL开发者选择，而因此却可能**有不同的面积 / 性能 / 功耗**。

> 比如想要64 * 64，选择64\*64的面积小但是读延迟略高，而用两个32\*64则是读延迟小面积大

而且不同的存储器规格也有不同形状，对后续布局布线有各种影响
因此综合器此时很难自动进行存储器的识别和映射（需要开发者自己按需选择存储器规则，并在RTL代码中手动以子模块的方式实例化存储器单元



#### 细粒度综合(Fine-grain synthesis)

细粒度综合阶段负责基于设计的“细粒度表示”进行处理。

所谓细粒度表示就采用门级单元来描述设计，这就要用到了内部单元库里面的[gate-level cells](https://yosyshq.readthedocs.io/projects/yosys/en/latest/cell/index_gate.html)，它们使用`$_XXX_`的形式命名（大写以同字级区分）

那么首先我们需要将设计的粗粒度表示转化为细粒度表示：
```bash
yosys> techmap

12. Executing TECHMAP pass (map to technology primitives).

12.1. Executing Verilog-2005 frontend: /opt/oss-cad-suite/lib/../share/yosys/techmap.v
Parsing Verilog input from `/opt/oss-cad-suite/lib/../share/yosys/techmap.v' to AST representation.
Generating RTLIL representation for module `\_90_simplemap_bool_ops'.
Generating RTLIL representation for module `\_90_simplemap_reduce_ops'.
Generating RTLIL representation for module `\_90_simplemap_logic_ops'.
Generating RTLIL representation for module `\_90_simplemap_compare_ops'.
Generating RTLIL representation for module `\_90_simplemap_various'.
Generating RTLIL representation for module `\_90_simplemap_registers'.
Generating RTLIL representation for module `\_90_shift_ops_shr_shl_sshl_sshr'.
Generating RTLIL representation for module `\_90_shift_shiftx'.
Generating RTLIL representation for module `\_90_fa'.
Generating RTLIL representation for module `\_90_lcu_brent_kung'.
Generating RTLIL representation for module `\_90_alu'.
Generating RTLIL representation for module `\_90_macc'.
Generating RTLIL representation for module `\_90_alumacc'.
Generating RTLIL representation for module `$__div_mod_u'.
Generating RTLIL representation for module `$__div_mod_trunc'.
Generating RTLIL representation for module `\_90_div'.
Generating RTLIL representation for module `\_90_mod'.
Generating RTLIL representation for module `$__div_mod_floor'.
Generating RTLIL representation for module `\_90_divfloor'.
Generating RTLIL representation for module `\_90_modfloor'.
Generating RTLIL representation for module `\_90_pow'.
Generating RTLIL representation for module `\_90_demux'.
Generating RTLIL representation for module `\_90_lut'.
Generating RTLIL representation for module `$connect'.
Generating RTLIL representation for module `$input_port'.
Successfully finished Verilog frontend.

12.2. Continuing TECHMAP pass.
Using extmapper simplemap for cells of type $reduce_or.
Using extmapper simplemap for cells of type $sdff.
Using extmapper simplemap for cells of type $sdffe.
Using extmapper simplemap for cells of type $logic_not.
Running "alumacc" on wrapper $extern:wrap:$ge:Y_WIDTH=1:B_WIDTH=32:A_WIDTH=32:B_SIGNED=0:A_SIGNED=0:394426c56d1a028ba8fdd5469b163e04011def47.
Using template $extern:wrap:$ge:Y_WIDTH=1:B_WIDTH=32:A_WIDTH=32:B_SIGNED=0:A_SIGNED=0:394426c56d1a028ba8fdd5469b163e04011def47 for cells of type $extern:wrap:$ge:Y_WIDTH=1:B_WIDTH=32:A_WIDTH=32:B_SIGNED=0:A_SIGNED=0:394426c56d1a028ba8fdd5469b163e04011def47.
Running "alumacc" on wrapper $extern:wrap:$add:Y_WIDTH=32:B_WIDTH=32:A_WIDTH=32:B_SIGNED=0:A_SIGNED=0:394426c56d1a028ba8fdd5469b163e04011def47.
Using template $extern:wrap:$add:Y_WIDTH=32:B_WIDTH=32:A_WIDTH=32:B_SIGNED=0:A_SIGNED=0:394426c56d1a028ba8fdd5469b163e04011def47 for cells of type $extern:wrap:$add:Y_WIDTH=32:B_WIDTH=32:A_WIDTH=32:B_SIGNED=0:A_SIGNED=0:394426c56d1a028ba8fdd5469b163e04011def47.
Using extmapper simplemap for cells of type $not.
Using extmapper simplemap for cells of type $or.
Using extmapper simplemap for cells of type $reduce_and.
Using template $paramod$fbc7873bff55778c0b3173955b7e4bce1d9d6834\_90_alu for cells of type $alu.
Using extmapper simplemap for cells of type $xor.
Using template $paramod\_90_fa\WIDTH=32'00000000000000000000000000100000 for cells of type $fa.
Using template $paramod\_90_lcu_brent_kung\WIDTH=32'00000000000000000000000000100000 for cells of type $lcu.
Using extmapper simplemap for cells of type $pos.
Using extmapper simplemap for cells of type $mux.
Using extmapper simplemap for cells of type $and.
No more expansions possible.
<suppressed ~597 debug messages>
```

`techmap`把当前设计替换为指定单元库中的单元来实现，如果未指定就采用内置的门极单元库

替换为门级单元后，还需要对一些多位的线网和端口进行拆分，否则可能会在RTLIL里面有多余的位抽取和位拼接操作：
```bash
yosys> splitnets -ports
13. Executing SPLITNETS pass (splitting up multi-bit signals).
```

再执行`opt -full`开展优化，消除无用单元和线网，`show`

（此时就是一张超大的门电路关系图，太大了放不下）

#### 工艺映射(Technology mapping)

工艺映射就是把工艺无关的电路表示映射到具体工艺的实现，这里工艺映射阶段负责将设计的细粒度表示映射到目标工艺的标准单元。我们看官方手册的一个简单的示例标准单元库：
```
library(demo) {
  cell(BUF) {
    area: 6;
    pin(A) { direction: input; }
    pin(Y) { direction: output;
              function: "A"; }
  }
  cell(NOT) {
    area: 3;
    pin(A) { direction: input; }
    pin(Y) { direction: output;
              function: "A'"; }
  }
  cell(NAND) {
    area: 4;
    pin(A) { direction: input; }
    pin(B) { direction: input; }
    pin(Y) { direction: output;
             function: "(A*B)'"; }
  }
  cell(NOR) {
    area: 4;
    pin(A) { direction: input; }
    pin(B) { direction: input; }
    pin(Y) { direction: output;
             function: "(A+B)'"; }
  }
  cell(DFF) {
    area: 18;
    ff(IQ, IQN) { clocked_on: C;
                  next_state: D; }
    pin(C) { direction: input;
                 clock: true; }
    pin(D) { direction: input; }
    pin(Q) { direction: output;
              function: "IQ"; }
  }
}
```

它以文本文件描述了标准单元的属性，包括：

- area：面积，单位$\mu m^2$
- 端口pin：标识了方向(direction)，对于输出端口还包含了功能(function)属性，以逻辑表达式给出；对于触发器的时钟输入端口，还会包含时钟(clock)属性

yosys的工艺映射过程分为2步：

1. 对时序逻辑单元进行工艺映射：
   ```
   yosys> dfflibmap -liberty cell.lib
   
   16. Executing DFFLIBMAP pass (mapping DFF/DLATCH cells to sequential cells from liberty file).
     cell DFF (noninv, pins=3, area=18.00) is a direct match for cell type $_DFF_P_.
     final dff/dlatch cell mappings:
       unmapped dff/dlatch cell: $_DFF_N_
       \DFF _DFF_P_ (.C( C), .D( D), .Q( Q));
       unmapped dff/dlatch cell: $_DFF_NN0_
       unmapped dff/dlatch cell: $_DFF_NN1_
       unmapped dff/dlatch cell: $_DFF_NP0_
       unmapped dff/dlatch cell: $_DFF_NP1_
       unmapped dff/dlatch cell: $_DFF_PN0_
       unmapped dff/dlatch cell: $_DFF_PN1_
       unmapped dff/dlatch cell: $_DFF_PP0_
       unmapped dff/dlatch cell: $_DFF_PP1_
       unmapped dff/dlatch cell: $_DFFE_NN_
       unmapped dff/dlatch cell: $_DFFE_NP_
       unmapped dff/dlatch cell: $_DFFE_PN_
       unmapped dff/dlatch cell: $_DFFE_PP_
       unmapped dff/dlatch cell: $_DFFSR_NNN_
       unmapped dff/dlatch cell: $_DFFSR_NNP_
       unmapped dff/dlatch cell: $_DFFSR_NPN_
       unmapped dff/dlatch cell: $_DFFSR_NPP_
       unmapped dff/dlatch cell: $_DFFSR_PNN_
       unmapped dff/dlatch cell: $_DFFSR_PNP_
       unmapped dff/dlatch cell: $_DFFSR_PPN_
       unmapped dff/dlatch cell: $_DFFSR_PPP_
       unmapped dff/dlatch cell: $_DLATCH_N_
       unmapped dff/dlatch cell: $_DLATCH_P_
       unmapped dff/dlatch cell: $_DLATCH_NN0_
       unmapped dff/dlatch cell: $_DLATCH_NN1_
       unmapped dff/dlatch cell: $_DLATCH_NP0_
       unmapped dff/dlatch cell: $_DLATCH_NP1_
       unmapped dff/dlatch cell: $_DLATCH_PN0_
       unmapped dff/dlatch cell: $_DLATCH_PN1_
       unmapped dff/dlatch cell: $_DLATCH_PP0_
       unmapped dff/dlatch cell: $_DLATCH_PP1_
       unmapped dff/dlatch cell: $_DLATCHSR_NNN_
       unmapped dff/dlatch cell: $_DLATCHSR_NNP_
       unmapped dff/dlatch cell: $_DLATCHSR_NPN_
       unmapped dff/dlatch cell: $_DLATCHSR_NPP_
       unmapped dff/dlatch cell: $_DLATCHSR_PNN_
       unmapped dff/dlatch cell: $_DLATCHSR_PNP_
       unmapped dff/dlatch cell: $_DLATCHSR_PPN_
       unmapped dff/dlatch cell: $_DLATCHSR_PPP_
   
   16.1. Executing DFFLEGALIZE pass (convert FFs and LATCHes to types supported by the target).
   Mapping DFF/DLATCH cells in module `\lights':
     mapped 48 $_DFF_P_ cells to \DFF cells.
   
   ```

   此时门级单元`#_SDFFE_PPOP_`被替换为了`DFF`（标准单元库`cell.lib`里面的标准单元）和一些`$_MUX_`，而之所以有这么多`$_MUX_`本质是因为`cell.lib`里面没有和`$_SDFFE_PPOP`功能完全相同的标准单元（根据手册这玩意功能是："带高有效同步复位信号和高有效使能信号的正边沿D触发器"），这里的`DFF`只是一个简单的D触发器，只能通过引入一些额外的组合逻辑单元来实现两个功能

   ![image-20260829150232512](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260829150232512.png)
   问题是这里的DFF的本应该的输出端`Q`却被代表输入端放在了左侧，原因是我们的`cell.lib`对yosys是一个外部单元库，`show`命名默认没有关于`DFF`这个标准单元的信息，为了修复这个问题，我们可以先让yosys读入`cell.lib`这个标准单元库：

   ```
   read_liberty -lib cell.lib
   ```

   ![image-20260829150539416](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260829150539416.png)

   之后通过`abc`对组合逻辑单元进行工艺映射：
   ```
   yosys> abc -liberty cell.lib 
   
   15. Executing ABC pass (technology mapping using ABC).
   
   15.1. Extracting gate netlist of module `\lights' to `<abc-temp-dir>/input.blif'..
   
   15.1.1. Executed ABC.
   Extracted 281 gates and 332 wires to a netlist network with 49 inputs and 48 outputs.
   Running ABC script: <abc-temp-dir>/abc.script
   ABC: UC Berkeley, ABC 1.01 (compiled Aug 27 2026 10:15:41)
   ABC: abc 01> empty
   ABC: abc 01> source <abc-temp-dir>/abc.script
   ABC: + read_blif <abc-temp-dir>/input.blif 
   ABC: + read_scl /tmp/yosys-liberty-scl-cache/yosys_merged_f40c952a.scl 
   ABC: + strash 
   ABC: + &get -n 
   ABC: + &fraig -x 
   ABC: + &put 
   ABC: + scorr 
   ABC: Warning: The network is combinational (run "fraig" or "fraig_sweep").
   ABC: + dc2 
   ABC: + dretime 
   ABC: + strash 
   ABC: + &get -n 
   ABC: + &dch -f 
   ABC: + &nf 
   ABC: + &put 
   ABC: + write_blif <abc-temp-dir>/output.blif 
   ABC: 
   ABC: YOSYS_ABC_DONE 
   
   15.1.2. Re-integrating ABC results.
   ABC RESULTS:              NAND cells:      105
   ABC RESULTS:               NOR cells:      106
   ABC RESULTS:               NOT cells:       45
   ABC RESULTS:          _const0_ cells:        9
   ABC RESULTS:        internal signals:      235
   ABC RESULTS:           input signals:       49
   ABC RESULTS:          output signals:       48
   Removing temp directory.
   Removing global temp directory.
   ```

   `abc`就是调用外部工具`ABC`进行组合逻辑单元的工艺映射工作，所有门级单元都会被替换为标准单元库`cell.lib`里面的标准单元，最后通过`clean`清除无用的接线就得到了最终的网表

   > show一下会看到此时彻底转化为了最基本的单元

#### 网表和报告生成

最后可以直接通过`write_verilog`把网表写入文件，通过`stat`命令输出所用的标准单元信息：
```
yosys> write_verilog netlist.v

17. Executing Verilog backend.

17.1. Executing BMUXMAP pass.

17.2. Executing DEMUXMAP pass.
Dumping module `\lights'.

yosys> stat -liberty cell.lib 

18. Printing statistics.

=== lights ===

        +----------Local Count, excluding submodules.
        |        +-Local Area, excluding submodules.
        |        | 
      645        - wires
      645        - wire bits
       50        - public wires
       50        - public wire bits
       18        - ports
       18        - port bits
      304     1843 cells
       48      864   DFF
      105      420   NAND
      106      424   NOR
       45      135   NOT

   Chip area for module '\lights': 1843.000000
     of which used for sequential elements: 864.000000 (46.88%)
```



#### Verilog的RTL综合语义

将什么样的RTL代码转换为什么样的标准单元，需要考虑RTL综合的语义，但是我们前面看的那本标准手册定义的是Verilog的仿真语义，不适用，用 [Verilog RTL综合标准手册](https://0x04.net/~mwk/vstd/ieee-1364.1-2002.pdf)描述了Verillog语言在综合场景下的语义.
 综合器干的事情就是读入Verilog代码然后跟据这一标准手册描述的语义，将其缓缓为语义等价的标准单元

> **背景(1.1节)**
> This standard defines a set of modeling rules for writing Verilog® HDL descriptions for synthesis. Adherence to these rules guarantees the interoperability of Verilog HDL descriptions between register-transfer level synthesis tools that comply to this standard. The standard defines how the semantics of Verilog HDL are used, for example, to describe level- and edge-sensitive logic. It also describes the syntax of the language with reference to what shall be supported and what shall not be supported for interoperability. 
> Use of this standard will **enhance the portability of Verilog-HDL-based designs** across synthesis tools conforming to this standard. In addition, it will **minimize the potential for functional mismatch** that may occur between the RTL model and the synthesized netlist.

---

##### 阅读手册第五章：Modeling hardware elements

本部分条款介绍的是如何对各种各样的硬件元素建模，这里的硬件接口不需要考虑任何优化和转换，换句话说只要你综合出来的网表有相同的功能性就行

5.1 组合逻辑建模

组合逻辑应该通过连续赋值 / net declaration assignment(wire / assign) / always声明

而当我们用always时，需要**避免边沿触发事件(posedge / negedge)**，虽然事件列表不会影响综合的网表，但是为了保证仿真和综合一致，建议还是把所有读的变量都写入这个列表里面。

一个在表达式右边的变量不是一定要被放入事件列表的，（就比如如果他在同一个`always`里面的前面的语句已经被阻塞赋值了 ，显然我们依赖的是这个来源）

你其实可以用隐式的方法：`@(*)`

> 例子：
> ```verilog
> always @(in1 or in2)
>     out  = in1 + in2;
> // 没问题
> always @(posedge a or b)
>     // 有问题，这不是组合逻辑...
>     ...;
> always @(in)
>     if (ena)
>         out = in;
> 	else 
>         out = 1'b1;
> // 支持，但是仿真可能会不对（因为它注意不到ena的更新事件），建议加入list
> always @(in1 or in2 or sel)
>     begin
>        out = in1;
>         if (sel)
>             out <= in2;
>     end
> // 不支持，混用了，除非你真的明白自己在做什么
> ```

###### **5.2 边缘触发的时序逻辑建模**

这个你只能用always了，把edge event放入敏感事件列表，语法就不说了

**对边缘触发的存储设备建模：**

一个边缘触发的存储设备应该被建模为一个在always块里面赋值的变量（且有边沿事件），建议使用非阻塞的过程赋值以避免竞态

但是这并不绝对，实际上你可以用阻塞赋值，对应的情况是你这里面有一个临时的变量，你想用它来在同一个always里面继续使用
```verilog
assign @(posedge clk) begin
   tmp = a + b;
    c <= tmp;
end
// 这样就可以！因为我们需要把`tmp`的赋值放到R_1事件里面
```

还是看几个例子：
```verilog
always @(posedge clk) begin
    out <= 0;
    @(posedge clk);
    out <= 1;
end
// 不合法...不允许多个敏感事件列表
```



**对异步复位的边沿触发存储设备的建模：**

这里敏感事件列表里面你绝对不能放电平相关的

同时你得有`if` / `else if`之类的来组织你的代码，`else`部分才放你的时钟同步逻辑，这是规范的写法（你的每一个异步控制的信号都需要对应一个else if）
![image-20260829162448365](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260829162448365.png)

```verilog
always @(posedge clk or posedge rst)
    out <= in;
// 错误，你的if呢
always @(posedge clk or negedge clear) begin
    if (~clear)
        out <= 0;
    else if (ping)			 // 同步逻辑开始
    	out <= in;
    else if (pong)
        out <= 8'hFF;
    else
        out <= pdata;
end
// 这是一个很好的例子，只有第一个~clear那里是异步的，剩下的都是同步的，根据非边沿触发的信号
```



###### **5.3 对电平触发的存储设备的建模(latch)**

你需要在这种情况下采用电平触发的建模：

- 这个变量在一个无边沿敏感事件的always块里面被赋值（组合逻辑建模方式）
-  有一些间接的变量赋值在always块里面

比如：
```verilog
always @(enable or d)
    if (enable)
        q <= d;
// 这里必须enable为1才可能通过d修改值，因此如果没激发那就不能修改（这就是implicit assignment）
always @(enable or d) 
    if (enable)
        q <= d;
    else
        q <= 1'b0;
// 
```

**非阻塞过程赋值应该被用于这种电平敏感的存储设备，以此防止竞态；而同时阻塞赋值则可以被用于那些中间被赋值的临时变量（并且它们只会被在相同always里面使用）**

###### **5.4 三态的仿真**

`z`不同于`x`，它是有综合意义的，代表高组态，不参与驱动。比如释放总线 / 3态驱动

也就是包含了值`z`，这个`z`的赋值无法在变量赋值时传播（意思是你`assign b = s ? data : 8'bx`时如果还要`assign a  = b`，那么a不会有这种`x`的释放的意思。

```verilog
module ztest (test2, test1, test3, ena);
    input [0:1] ena;			// 换了一个位编号方向(ena[0]=1,ena[1]=0,ena=2'b10)
    input [7:0] test1, test3;
    output [7:0] test2;
    wire [7:0] test2;
    assign test2 = (ena == 2'b01) ? test1 : 8'bz;
    assign test2 = (ena == 2'b10) ? test3 : 8'bz;
endmodule
```

```verilog
module ztest;
    wire test1, test2, test3;
    input test2;
    output test3;
    assign test1 = 1'bz;
    assign test3 = test1 & test2;
endmodule    
// 这里的test3永远都不会被赋值为`z`
```

```verilog
always @(in)
    begin
        tmp = 1'bz;
        out = tmp;
    end
// 这里同样不能用一个3态的驱动器来驱动out,因为不会传播
```

```verilog
always @(q or enb)
    if (!enb)
        out <= 'bz;
	else
        out <= q;
// out 此时就是一个3态的驱动器
```

```verilog
always @(posedge clk)
    q <= din;
assign out = enb ? q : 1'bz;
// 这里赋值1'bz就是代表“这里什么也不做”
```

```verilog
always @(posedge clk)
    if (!enb)
        out <= 1'bz;
	else 
        out <= din;
```



###### **5.5 对x和z的支持**

- `x`可以被放在赋值的RHS，这告诉综合器压根不在乎这里是什么值，随便优化
- 同样`x`也可以放到case 里面的条目表达式，但是这是直接匹配（如: `4'b01x0`必须对应同样的）；在`casex`里面被认为是`don't-care`，你这位是谁都好
- `x`不可以和别的等式混在一起或者作为一个操作数
- `z`可用于赋值的RHS表示一个3态驱动器
- `z`(or `?`)也可以用于case的条目；对casex casez都行
- 同样z也不能被作为操作数或混合使用

> `casex`-认为x和z `?`都是随便；`casez`-只认`z` / `?`
> 换句话说casex 比casez更wildcard



###### **5.6 对ROM的建模**

一个异步ROM应按照以下任一组合逻辑建模：

- 一维数组形式，data放在case语句里面
- 二维数组，data放到initial语句里面
- 二维数组，data放到文本文件里面

**`rom_block`应该被用于标识应该被建模为ROM的变量.**
**而`logic_block`的话则是说根本不需要ROM，那么就是使用组合逻辑**

注意：

- 如果你没有一个`rom_block` / `logic_block`的分配，综合器**会随便选一种**
- 这个标准**并不定义这些ROM的值应该如何存以及被存在哪里**（当`rom_block`分配使用时）
- 很可能在仿真时一开始会有mismatch（还没跑到那里）

1. **一维数组的形式放到case里面**：

   ```verilog
   module rom_case(
       (* synthesis, rom_block = "ROM_CELLXYZ01" *)
       output reg [3:0] z,
       input wire [2:0] a
   );
       always @*
           case (a)
               3'b000: z = 4'b1011;
               3'b001: z = 4'b0001;
               3'b100: z = 4'b0011;
               3'b110: z = 4'b0010;
               3'b111: z = 4'b1110;
               default: z = 4'b0000;
           endcase
   endmodule
   ```

   

2. **二维数组初始化，在initial里面**
   你需要在这块**存储的声明处确定好这个ROM的地址宽度和数据宽度**

   而**ROM值的分配应该通过inital块来搞定**，未被初始化的值则会被隐式地`dont-care`赋值。
   显然initial块里面不可能只有赋值，还会有别的综合声明（甚至有loop/ if /case），唯一的要求就是你对RAM的赋值（data还是addr），必须是静态可计算的

   这样的存储只能被别的过程块读，写会出错

   ```verilog
   module rom_2dimarray_initial (
       output wire [3:0] z,
       input wire [2:0] a
   );
   // Declare a memory rom of 8 4-bit regs. The indices are 0~7
       (*synthesis, rom_block = "ROM_CELL XYZ01" *) reg [3:0] rom[0:7];
       // or if you want logic block: 
       // (* synthesis, logic_block *) reg [3:0] rom[0:7];
       initial begin
           rom[0] = 4'b1011;
           rom[1] = 4'b1001;
           rom[2] = 4'b0001;
           rom[3] = 4'b1011;
           rom[4] = 4'b1011;
           rom[5] = 4'b1011;
           rom[6] = 4'b1011;
           rom[7] = 4'b1011;
       end
       assign Z = rom[a];
   endmodule
   ```

3. **二维数组放到文本文件里面**

   和上一个差不多，唯一区别就是改用了system task：
   ```verilog
   module rom_2dimarray_initial_readmem (
       output wire [3:0] z,
       input wire [2:0] a
   );
       (* synthesis, rom_block = "ROM_CELL XYZ01" *) reg [3:0] rom[0:7];
       initial $readmemb("rom.data", rom);
       assign z = rom[a];
   endmodule
   ```



###### 5.7 建模RAM

一个RAM的建模应该使用Verilog memory，分配了`ram_block`最合适。一个RAM的元素可以被建模为边缘触发存储单元或者一个电平触发的存储元素。

```verilog
module ram_test (
    output wire [7:0] q,
    input wire [7:0] d,
    input wire [6:0] a,
    input wire clk, we
);
    (* synthesis, ram_block *) reg [7:0] mem [127:0];
    always @(posedge clk) if (we) mem[a] <= d;
    assign q = mem[a];
endmodule
// a latch version
module ramlatch(
    output wire [7:0] q,
    input wire [7:0] d,
    input wire [6:0] a,
    input wire we
);
    (* synthesis, ram_block *) reg [7:0] mem [127:0];
    always @* if (we) mem[a] <= d;
    assign q = mem[a];
endmodule
```

注意：

- 同样我们还是可以用`logic_block`
- 没有分配，会随机选一种

---



由于仿真和综合的语义不完全一致，很可能出现同一份代码仿真和综合下行为不一致...

但是我们还是**以综合为准**，我们**需要尽可能避免仿真和综合不一致的代码**

----

#### Annex B功能不匹配

##### 未定义行为(往往就是race condition)

```verilog
always @(posedge clk) begin
    a = 0;
    a = 1;
end
always @(posedge clk)
    b = a;
```

##### Pragmas编译指示

Pragmas可以决定综合器如何翻译这个结构，正因为如此你应该避免它做一些和仿真器不同的事情

###### 1 `full_case`属性

`full_case`属性引导综合器将所有未定义的case 条目当作`don't-care`。而仿真器直接会忽略未定义的case条目

```verilog
module decode4_fc (output reg [3:0] y, input [1:0] a, input en);
    always @* begin
        y = 4'b0;
        (* synthesis, full_case *)	// tell the synthesizer to ignore undefined cases
        case ({en, a})
            3'b1_00: y[a] = 1'b1;
            3'b1_01: y[a] = 1'b1;
            3'b1_10: y[a] = 1'b1;
            3'b1_11: y[a] = 1'b1;
        endcase
endmodule
```

这种情况下在输入是比如`en=0`时就会







----

### 开源EDA工具评估电路-PPA

网表中的标准单元就是可制造的了（有物理属性），那么得到网表后就可以对电路的好坏做一个初步评估。

衡量有多个维度，常用的三个维度是**PPA（Performance Power Area）**

#### 面积评估Area

最简单的是面积评估，我们引用的`.lib`文件给出了标准单元的面积属性，综合器只需要统计处每个标准单元在网表的实例化次数就可以计算出当前设计的总面积

#### 性能评估Performance

主要用频率来衡量（每秒能工作多少次），而这又是取决于完成一次工作需要花的时间。我们把“一次工作”定义为”时序逻辑元件在时钟信号驱动下更新状态，因为这些指标和时间相关，因此分析的过程称为**时序分析(timing analysis)**

而状态更新时组合逻辑的计算由于门电路的延迟，我们时钟频率不能太小否则两次时钟之间无法容纳足够的延迟。

正因为如此，**评估电路的性能 = 通过评估电路中组合逻辑的延迟来推算电路的最高频率**

而电路中的工作频率往往会受限于所有组合逻辑里面路径延迟最长的那一条，这就是电路的**关键路径(critical path)**。为了找到这条关键路径，EDA需要从标准单元库中读出标准单元的延迟信息

不过我们这里的ICsprout55的标准单元库已经提供了完整的标准单元延迟信息，

sta报告(sta.log)：（2.1GHz）

> +----------------------------+-------------+------------+------------+---------------+-------+-------+-----------+
> | Endpoint                   | Clock Group | Delay Type | Path Delay | Path Required | CPPR  | Slack | Freq(MHz) |
> +----------------------------+-------------+------------+------------+---------------+-------+-------+-----------+
> | m_lights.count_17__reg_p:D | core_clock  | max        | 0.447r     | 1.973         | 0.000 | 1.526 | 2108.824  |
> | m_lights.count_16__reg_p:D | core_clock  | max        | 0.441r     | 1.973         | 0.000 | 1.532 | 2136.004  |
> | m_lights.count_15__reg_p:D | core_clock  | max        | 0.441r     | 1.973         | 0.000 | 1.532 | 2136.008  |
> | m_lights.count_16__reg_p:D | core_clock  | max        | 0.423f     | 1.956         | 0.000 | 1.533 | 2139.912  |
> | m_lights.count_15__reg_p:D | core_clock  | max        | 0.423f     | 1.956         | 0.000 | 1.533 | 2139.912  |
> | m_lights.count_22__reg_p:D | core_clock  | min        | 0.109f     | -0.007        | 0.000 | 0.116 | NA        |
> | m_lights.count_17__reg_p:D | core_clock  | min        | 0.115f     | -0.006        | 0.000 | 0.122 | NA        |
> | m_lights.count_21__reg_p:D | core_clock  | min        | 0.121f     | -0.007        | 0.000 | 0.128 | NA        |
> | m_lights.count_16__reg_p:D | core_clock  | min        | 0.123f     | -0.007        | 0.000 | 0.131 | NA        |
> | led[0]_reg_p:D             | core_clock  | min        | 0.122f     | -0.009        | 0.000 | 0.131 | NA        |
> +----------------------------+-------------+------------+------------+---------------+-------+-------+-----------+ 

事实上这个时序报告并不能完全反应流片的芯片的频率，因为网表只包含标准单元及其拓扑信息，不包含标准单元间的物理位置信息，还会有**线延迟(net delay)**。而标准单元库中的标准单元的延迟属性之嗯嗯反应信号经过标准单元本身的延迟，这是所谓**逻辑延迟(logic delay)**，只有等到布线后我们才能得到更接近流片场景的频率信息

但是并非毫无意义：

- 起码给出了**频率的上限**，可以反映出RTL逻辑设计阶段的某些问题（太复杂），以供优化
- 开展物理设计需要时间

此外，对处理器显然频率不是衡量性能的唯一因素。需要看每个周期执行指令数IPC(Instruction Per Cycle)

#### 功耗评估Power

这需要评估电路中标准单元的功耗之和，同样还是从标准库里面读出标准单元的功耗信息，计算出每个标准单元的功耗从而计算电路的总功耗

> | Power Group   | Internal Power | Switch Power | Leakage Power | Total Power | (%)       |
> | combinational | 5.152e-04      | 0.000e+00    | 1.914e-07     | 5.154e-04   | (79.727%) |
> | sequential    | 1.307e-04      | 0.000e+00    | 3.104e-07     | 1.311e-04   | (20.273%) |

这里有3种功耗：

- `Internal Power`：内部功耗

  就是**短路功耗**，当NMOS和PMOS均导通时形成从电源端到地端的短路电流，产生的功耗也就是所谓内部功耗。这属于动态功耗(dyanmic power)的一部分

- `Switch Power`：翻转功耗

  电平翻转的时候由于寄生电容需要进行充放电，这部分也算动态功耗

- `Leakage Power`：漏电功耗

  `I_{CBO}`，截止时的漂移电流

这里没法计算翻转电流，因为要计算这个寄生电容不仅和标准单元有关，走线拓扑和长度也很重要，这需要你完成后端物理设计

> 关于FPGA：
>
> - `yosys`的综合流程是面向ASIC设计的，FPGA流程的原理和ASIC不同，无法替代；即使FPGA流程正确，规范的AISC流程仍需要进行网表的功能仿真和时序仿真
>
> - 而FPGA的主要作用是仿真加速，只有方针任务需要花费大量时间时使用FPGA才有优势，需要满足
>
> $$
> T_{FPGA.syn} + T_{FPGA.impl} + T_{FPGA.run} < T_{Sim.compile} + T_{Sim.run}
> $$
>
> 其中$T_{FPGA.syn} + T_{FPGA.impl}$ 往往要达到小时级别，而complie只需要几分钟完成。因此除非  $T_{Sim.run}$达到小时级上述才可能成立
>
> - FPGA的调试手段很有限，远不如软件灵活

### PDK和标准单元库

刚刚的`cell.lib`只是一个标准单元库的简单示例，介绍一下ICsprout55这个**PDK(Process Design Kit)**，网表里面实例化的都是它的标准单元

#### PDK的内容

PDK包含了特定工艺节点下的器件模型，设计规则，工艺约束，验证文件和标准单元库等一系列资源。其中标准单元库是标准单元及其属性的集合，属性包含逻辑功能/晶体管结构/时序/功耗/物理尺寸等信息，以多种文件形式分布在PDK的多种文件格式中

> ```bash
> $ tree ./IP
> ./IP
> ├── IO
> │   └── ICsprout_55LLULP1233_IO_251013
> │       ├── cdl
> │       │   └── ICSIOA_N55_3P3.cdl
> │       ├── cell_list
> │       │   └── ICSIOA_N55_3P3.txt
> │       ├── doc
> │       │   └── ICSIOA_N55_3P3_Application_Datasheet_1P6M.pdf
> │       ├── lef
> │       │   └── ICSIOA_N55_3P3_1P6M1TM.lef
> │       ├── liberty
> │       │   ├── ICSIOA_N55_3P3_ff_1p32_3p63_125c.lib
> │       │   ├── ICSIOA_N55_3P3_ff_1p32_3p63_m40c.lib
> │       │   ├── ICSIOA_N55_3P3_ff_1p32_3p63v_0c.lib
> │       │   ├── ICSIOA_N55_3P3_ss_1p08_2p97_125c.lib
> │       │   ├── ICSIOA_N55_3P3_ss_1p08_2p97_m40c.lib
> │       │   └── ICSIOA_N55_3P3_tt_1p2_3p3_25c.lib
> │       └── verilog
> │           └── icsIOA_N55_3P3.v
> └── STD_cell
>     └── ics55_LLSC_H7C_V1p10C100
>         ├── ics55_LLSC_H7CL
>         │   ├── cdl
>         │   │   └── ics55_LLSC_H7CL.cdl
>         │   ├── cell_list
>         │   │   └── ics55_LLSC_H7CL.txt
>         │   ├── doc
>         │   │   └── ics55_LLSC_H7CL_TYPICAL_V1P2_T25.pdf
>         │   ├── lef
>         │   │   ├── ics55_LLSC_H7CL_ant.lef
>         │   │   ├── ics55_LLSC_H7CL_ieda.lef
>         │   │   └── ics55_LLSC_H7CL.lef
>         │   ├── liberty
>         │   │   ├── ics55_LLSC_H7CL_ss_rcworst_1p08_125_nldm.lib
>         │   │   └── ics55_LLSC_H7CL_typ_tt_1p2_25_nldm.lib
>         │   └── verilog
>         │       └── ics55_LLSC_H7CL.v
>         └── ics55_LLSC_H7CR
>             ├── cdl
>             │   └── ics55_LLSC_H7CR.cdl
>             ├── cell_list
>             │   └── ics55_LLSC_H7CR.txt
>             ├── doc
>             │   └── ics55_LLSC_H7CR_TYPICAL_V1P2_T25.pdf
>             ├── lef
>             │   ├── ics55_LLSC_H7CR_ant.lef
>             │   ├── ics55_LLSC_H7CR_ieda.lef
>             │   └── ics55_LLSC_H7CR.lef
>             ├── liberty
>             │   └── ics55_LLSC_H7CR_typ_tt_1p2_25_nldm.lib
>             └── verilog
>                 └── ics55_LLSC_H7CR.v
> 
> ```

当前这个开放的标准单元库名称：`ics55_LLSC_H7C_V1p10C100`，`LLSC`=`Low Leakage standard Cell`，`H7`=标准单元的高度为7个轨道，`C`表示大版本号，后面是小版本号

而实际上不同设计阶段会用这里面不同的文件：
综合阶段会读入`.lib`文件，根据标准单元的逻辑功能，将逻辑上功能等价的子电路映射到相应的标准单元进行网表仿真时会读入`.v`文件
网表仿真时则需要读入`.v`文件，让RTL仿真器进行标准单元级别的仿真，从而验证综合后的网表功能符合预期
布局时需要读入`.lef`文件，根据标准单元的尺寸等信息决定美国标准单元的位置

#### 工艺视角的芯片结构

实际上芯片的物理结构是分层的，比如某种工艺的芯片侧视图如下图：

![](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/chip_level.png)

- 最底层的是硅衬底(silicon substrate)，包含晶体管的源极和漏极；

- 其上是绝缘层(dielectric)，栅氧层；

- 多晶硅层(poly-silicon)，作为晶体管的栅极

- 上方是多个金属层，利用导电性质实现信号的传输，以此连接不同的晶体管和实现不同的门电路 / 标准单元功能

  连接方式：

  - 内连接：在同一个金属层进行走线
  - 跨层连接：通过不同金属层之间的通孔(via)进行连接

  也就是说我们逻辑设计里面各个元件的连接关系物理上是通过金属层提供的连接功能实现的

为了区分不同的金属层，从低到高编号：

| 金属层 | 线宽 | 走线间距 |             走线特性             |                    作用                    |
| :----: | :--: | :------: | :------------------------------: | :----------------------------------------: |
|  低层  |  小  |    小    |  电阻大, 传输距离短, 布线密度高  | 连接不同的晶体管, 从而构成门电路和标准单元 |
|  中层  |  中  |    中    | 电阻中, 传输距离中等, 布线密度中 |   连接不同的标准单元, 实现芯片的主要逻辑   |
|  高层  |  大  |    大    |  电阻小, 传输距离长, 布线密度低  |                    电源                    |

不同的制造工艺会有不同的金属层数量，比如上图的工艺结构简称`1P7M`，1poly7metal。
这里的金属层则用了M1作为底层金属层，M7为高层金属层，5层中间层用于实现标准单元之间的连接

在连接不同的标准单元的信号中，时钟信号和数据信号有所不同，因为需要连接大量的触发器，线路比一般的数据信号要长，通常采用更大的线宽，后端工程师会在EDA工具里面制定线宽的参数。
同时后端工程师也会制定慈爱用哪一层金属层来实现时钟信号（理论上任何一层都可以不过习惯上用高层下面一层）

通常先进工艺会提供更多金属层，比如`1P9M`,`1P11M`等等，它们能提供更丰富的空间用于标准单元之间的连接，但是缺点就是需要用更多的金属掩膜(mask)，成本更高

金属层的属性记录在PDK的工艺LEF文件当中，它以`.lef`为后缀，采用`Library Exchange Format`格式，文本描述了相应工艺的<u>金属层 / 通孔 / 布局规则</u> 等物理层信息

查看`pdk/icsprout55/prtech/techLEF/N551P6M.lef`：

```
LAYER MET1
  TYPE ROUTING ;					// 该层用于布线
  DIRECTION HORIZONTAL ;			// 
  PITCH 0.2 0.2 ;						// 最小走线间距		
  WIDTH 0.09 ;						// 最小线宽
  OFFSET 0 0 ;						
  AREA 0.042 ;
  SPACING 0.09 ;
  MAXWIDTH 10 ;
  MINENCLOSEDAREA 0.18 ;
  RESISTANCE RPERSQ 0.1122 ;
  DCCURRENTDENSITY AVERAGE 1.5 ;
END MET1
```

> [关于lef](https://www.ispd.cc/contests/18/lefdefref.pdf)

这里也有LAYER POLY，不过只有声明：

```
LAYER POLY
  TYPE MASTERSLICE ;
END POLY
```

原因在于多晶硅联通绝缘层衬底共同用于实现晶体管，而晶体管的参数由工艺决定，这对后端物理设计过程是相对固定的，不像金属层呢养可以让EDA工具根据设计需求进行动态布线，因此在LEF文件中只需要声明其存在即可（而绝缘层和硅衬底从功能上与多晶硅层紧密绑定，甚至不需要在LEF文件中出现）

> 根据LEF文件似乎有5层金属层，分别的线宽和走线间距：
>
> |      | PITCH | WIDTH |
> | ---- | ----- | ----- |
> | MET1 | 0.2   | 0.09  |
> | MET2 | 0.2   | 0.1   |
> | MET3 | 0.2   | 0.1   |
> | MET4 | 0.2   | 0.1   |
> | MET5 | 0.2   | 0.1   |
>
> 显然MET1应该对应最底层的，走线密集，但是各层线宽差不多，有些难以分辨...

而如果处理器的规模复杂，标准单元之间则会存在较多连线，使得布线阶段压力变大，走线就需要迂回，这不仅增加了芯片的面积，还增加了线延迟，会降低芯片的频率，还可能因为过分拥堵使得布线失败，因而难以制造出功能正常的芯片。因此高性能处理器的设计往往选择金属层多的工艺，通过更丰富的布线空间来环节布线阶段的压力。

> 比如香山处理器在设计过程中尝试将工艺从`1P9M`切换到`1P11M`，无需改变RTL代码即可降低线延迟提升处理器主频

> 实际上并非所有工艺都是只有1层多晶硅层，根据不同的应用场景会有更多层，比如闪存的存储单元采用浮栅晶体管，是一种包含2个栅极的晶体管，一个是浮栅(floating gate)，分为存储和未存储电荷两种状态，分别表示0和1；另一个是控制栅(control gate)，

#### 标准单元的属性

PDK提供的标准单元库通常包含很多标准单元，为了方便得知标准单元的属性，标准单元的命名通常会遵循一定的规范，在ICsprout55中，标准单元的命名**遵循`功能+驱动能力+H+轨道数+阈值电压`的方式**.

> 例如`NAND2X1H7L`表示该标准单元的功能为二输入的与非门, 驱动能力为`X1`, 即1倍标准驱动能力, 其高度为7个轨道, 阈值电压为LVT;
>   `OR3X0P5H7R`表示该标准单元的功能为三输入或门, 驱动能力为`X0P5`, 即0.5倍标准驱动能力(`P`表示小数点), 其高度为7个轨道, 阈值电压为RVT.

我们以`NAND2X1H7L`为例：

##### lib文件-功能/时序/功耗

查看`/pdk/icsprout55/IP/STD_cell/ics55_LLSC_H7C_V1p10C100/ics55_LLSC_H7CL/liberty/ics55_LLSC_H7CL_typ_tt_1p2_25_nldm.lib`：

```
  cell (NAND2X1H7L) {
    area : 1.12;
    cell_footprint : "NAND2X1H7L";
    cell_leakage_power : 0.434974;
    pg_pin (VDD) {
      pg_type : primary_power;
      voltage_name : "VDD";
    }
    pg_pin (VSS) {
      pg_type : primary_ground;
      voltage_name : "VSS";
    }
    leakage_power () {
      value : 0.312371;
      when : "(A * B * !Y)";
      related_pg_pin : VDD;
    }
    leakage_power () {
      value : 0;
      when : "(A * B * !Y)";
      related_pg_pin : VSS;
    }
    leakage_power () {
      value : 0.82883;
      when : "(A * !B * Y)";
      related_pg_pin : VDD;
    }
    leakage_power () {
      value : 0;
      when : "(A * !B * Y)";
      related_pg_pin : VSS;
    }
    leakage_power () {
      value : 0.565379;
      when : "(!A * B * Y)";
      related_pg_pin : VDD;
    }
    leakage_power () {
      value : 0;
      when : "(!A * B * Y)";
      related_pg_pin : VSS;
    }
    leakage_power () {
      value : 0.0333159;
      when : "(!A * !B * Y)";
      related_pg_pin : VDD;
    }
    leakage_power () {
      value : 0;
      when : "(!A * !B * Y)";
      related_pg_pin : VSS;
    }
    leakage_power () {
      value : 0.434974;
      related_pg_pin : VDD;
    }
    leakage_power () {
      value : 0;
      related_pg_pin : VSS;
    }
    pin (Y) {
      direction : output;
      function : "(!A) + (!B)";
      output_voltage : default_VDD_VSS_output;
      power_down_function : "(!VDD) + (VSS)";
      related_ground_pin : VSS;
      related_power_pin : VDD;
      max_capacitance : 0.055;
      timing () { ......  }
      timing () { ......  }
      internal_power () { ...... }
      internal_power () { ...... }
      internal_power () { ...... }
      internal_power () { ...... }
    }
    pin (A) {
      direction : input;
      driver_waveform_fall : "PreDriver20.5:fall";
      driver_waveform_rise : "PreDriver20.5:rise";
      input_voltage : default_VDD_VSS_input;
      related_ground_pin : VSS;
      related_power_pin : VDD;
      max_transition : 0.795659;
      capacitance : 0.000898206;
      rise_capacitance : 0.000898206;
      rise_capacitance_range (0.000705173, 0.000898206);
      fall_capacitance : 0.000888785;
      fall_capacitance_range (0.000696354, 0.000888785);
      internal_power () { ...... }
      internal_power () { ...... }
    }
    pin (B) {
      direction : input;
      driver_waveform_fall : "PreDriver20.5:fall";
      driver_waveform_rise : "PreDriver20.5:rise";
      input_voltage : default_VDD_VSS_input;
      related_ground_pin : VSS;
      related_power_pin : VDD;
      max_transition : 0.795659;
      capacitance : 0.000953054;
      rise_capacitance : 0.000953054;
      rise_capacitance_range (0.000589512, 0.000953054);
      fall_capacitance : 0.000952783;
      fall_capacitance_range (0.000588209, 0.000952783);
      internal_power () { ...... }
      internal_power () { ...... }
    }
  }
```

能看懂的：

- 面积(area)：

  我们假设将芯片水平放置，那么标准单元的面积就是指它在平面xOy投影的面积，对应芯片工艺结构就是其在多晶硅层和低层金属层所占的面积

- leakage power

- internal power

- pin：包含direction/capacitance/等等，对于输出端口还会包含：

  - 功能(function)，通过逻辑表达式给出，可以从该属性了解该标准单元的功能
  - 时序(timing)，包含标准单元在各种情况下的延迟

从上述属性可以看到，LIB文件主要用于综合/时序分析/功耗分析

> 例如yosys会在进行工艺映射时读入LIB文件，根据标准单元`function`字段决定将哪些子电路映射为何种标准单元，从而保证网表所描述的电路逻辑和RTL等价
>
> iSTA工具会根据标准单元的`timing`字段，计算各种情况下每个标准单元的逻辑延迟

> 建议查询：sta/pdk/icsprout55/IP/STD_cell/ics55_LLSC_H7C_V1p10C100/ics55_LLSC_H7CL/doc/ics55_LLSC_H7CL_TYPICAL_V1P2_T25.pdf
>
> 以及条目：
> [Liberty Timing File Manual Suite](https://media.c3d2.de/mgoblin_media/media_entries/659/Liberty_User_Guides_and_Reference_Manual_Suite_Version_2017.06.pdf)

##### Verilog文件-行为模型

为了验证综合后的网表和综合前的RTL等价，一种方法是进行网表仿真，即结合标准单元的行为再次对网表进行仿真
虽然我们的.lib的`function`字段已经描述了标准单元的行为，但是RTL仿真器通常无法识别LIB文件，标准单元库因此会提供标准单元的Verilog行为模型

在ICsprout55中，标准单元的Verilog行为模型位于：` yosys-sta/pdk/icsprout55/IP/STD_cell/ics55_LLSC_H7C_V1p10C100/ics55_LLSC_H7CL/verilog/ics55_LLSC_H7CL.v`：
```verilog
module NAND2X1H7L (Y, A, B);
output Y;
input A, B;

  nand (Y, A, B);


`ifdef functional // functional //
`else // functional //
specify
if (B==1'b1)
(A => Y) = (1.0,1.0);
if (A==1'b1)
(B => Y) = (1.0,1.0);

endspecify
`endif // functional //
endmodule //NAND2X1H7L
```

可以看到，这只不过是用Verilog把标准单元的功能又实现了一遍...（用了内建的primitive原语`nand`来实现了二输入与门的功能)

将网表文件 + 这个行为模型文件 输入RTL仿真器，它会按照模型文件中的模块定义对王表文件的标准单元进行实例化，从而开展网表层次的仿真工作

除了功能仿真，这里的`specify`语句也给出了丰富的时序信息，可以支持用户开展网表层次的时序仿真

##### LEF文件-物理几何信息

除了上文那种和工艺相关的LEF文件，还有一种和标准单元相关的LEF文件**专门用于描述标准单元的物理几何信息**

我们看`yosys-sta/pdk/icsprout55/IP/STD_cell/ics55_LLSC_H7C_V1p10C100/ics55_LLSC_H7CL/lef/ics55_LLSC_H7CL.lef`：
````
MACRO NAND2X1H7L
  CLASS CORE ;
  ORIGIN 0 0 ;
  FOREIGN NAND2X1H7L 0 0 ;
  SIZE 0.8 BY 1.4 ;
  SYMMETRY X Y ;
  SITE core7 ;
  PIN A
    DIRECTION INPUT ;
    USE SIGNAL ;
    PORT
      LAYER MET1 ;
        RECT 0.055 0.425 0.23 0.59 ;
    END
  END A
  ... // 其他的PIN
END NAND2X1H7L
````

其中：

- `SYMMETRY X Y`表示标准单元可以沿X或Y轴方向对称放置，从而优化布局的效果（比如到某端口的线延迟
- `PIN`字段用于描述指定引脚的一些属性，这里包含`DIRECTION`方向和`PORT`端口几何形状（
- `SITE`给出了标准单元在放置时需要对齐的规则，此处字段`core7`表示引用流另一处的对齐规则





##### CDL文件-晶体管结构描述

所谓**CDL就是Circuit Description Language**，用文本的方式**描述了标准单元的晶体管结构**

CDL里面对晶体管的结构描述格式如下：

```cdl
.SUBCKT 子电路名称 端口1 端口2...
晶体管实例名称 漏极 栅极 源极 衬底 晶体管类型 沟道宽度 沟道长度
...
.ENDS
```

比如这种：
```
.SUBCKT NAND2X1H7L A B VDD VSS Y
*.PININFO A:I B:I Y:O VDD:B VSS:B
MMN0 Y B net6 VSS nm1p2_lvt_lp W=210n L=60n m=1
MMN1 net6 A VSS VSS nm1p2_lvt_lp W=210n L=60n m=1
MMP1 Y B VDD VDD pm1p2_lvt_lp W=270n L=60n m=1
MMP0 Y A VDD VDD pm1p2_lvt_lp W=270n L=60n m=1
.ENDS
```

这里`*`那行是注释，其他的：

- `MMNx`：实例化了一个名为`MMN0`的晶体管，源极连接端口Y，栅极连接端口B，源极和线网`net6`相连，衬底和端口`VSS`相连，采用的晶体管类型为`nm1p2_lvt_lp`，沟道的W=210nm，L=60nm

>  画出这个标准单元的结构：的确是典型的与非门两个输入一个是一起从VSS串Y，一个是并联通过VDD连接到Y（画的太丑了就不放了）

CDL描述的晶体管结构信息主要用于进行晶体管层次的SPICE仿真，以及用于检查GDS版图与网表的逻辑一致性（即LVS - Layout Versus Schematic）

##### GDS文件 - 物理版图

GDS文件包含了制造标准单元所需的所有物理和工艺新消息，这个并不是文本文件爱你，需要专门的工具进行解析（ICsprout55的暂时尚未开放）

#### 标准单元的分类

根据功能分类，前5类单元和时钟缓存器是必须的。通过提供其他类型的单元，用户可以针对指定的场景设计出更优的电路，或更方便的芯片调试功能

##### 逻辑门单元

> 复杂逻辑门单元：OAI22X1H7L，确实挺复杂的，.lib文件里面很长
>
> 有A0 A1 B0 B1的输入和一个output Y，找到pin (Y)，看到对应的内容：
> ```
>  pin (Y) {
>       direction : output;
>       function : "(!A0 * !A1) + (!B0 * !B1)";
>       output_voltage : default_VDD_VSS_output;
>       power_down_function : "(!VDD) + (VSS)";
>       related_ground_pin : VSS;
>       related_power_pin : VDD;
>       max_capacitance : 0.0296464;
>       timing () {
>         related_pin : "A0";
>         sdf_cond : "(~A1 & B0 & B1)";
>         timing_sense : negative_unate;
>         timing_type : combinational;
>         when : "(!A1 * B0 * B1)";
>         cell_rise (delay_template_7x7) {
>           index_1 ("0.0121961, 0.024473, 0.0490972, 0.0985337, 0.197642, 0.396563, 0.795659");
> 
> ```
>
> 显然它是一个bool函数：(~a0 & ~a1) | (~b0 & ~b1) = !((A0 | A1) & (B0 | B1))

显然这就是两个二输入或门，一个二输入与门加一个非门，这种逻辑门称为复杂门(complex gate)。

为什么要做复杂门？因为面积更小，实现相同的的真值表完全可以通过晶体管的串联和并联来实现“与”“或”的逻辑功能往往比通过与或门来实现代价要低得多，这是PPA三方面的优势，正因为如此我们的标准库才需要引入各种的复杂逻辑门单元

> 看看对应的晶体管，看CDL文件：
>
> ```
> ************************************************************************
> * Library Name: ICSN55H7LVT
> * Cell Name:    OAI22X1H7L
> * View Name:    schematic
> ************************************************************************
> 
> .SUBCKT OAI22X1H7L A0 A1 B0 B1 VDD VSS Y
> *.PININFO A0:I A1:I B0:I B1:I Y:O VDD:B VSS:B
> MNM4 net8 A1 VSS VSS nm1p2_lvt_lp W=210n L=60n m=1
> MNM3 net8 A0 VSS VSS nm1p2_lvt_lp W=210n L=60n m=1
> MMN5 Y B0 net8 VSS nm1p2_lvt_lp W=210n L=60n m=1
> MNM5 Y B1 net8 VSS nm1p2_lvt_lp W=210n L=60n m=1
> MMP5 Y A1 net046 VDD pm1p2_lvt_lp W=270n L=60n m=1
> MPM3 net046 A0 VDD VDD pm1p2_lvt_lp W=270n L=60n m=1
> MPM5 Y B1 net049 VDD pm1p2_lvt_lp W=270n L=60n m=1
> MPM4 net049 B0 VDD VDD pm1p2_lvt_lp W=270n L=60n m=1
> .ENDS
> ```
>
> 显然，这里用了8个晶体管，看看具体的晶体管构造                                                                                                      
>
> （我在想用rust写一个可视化脚本？）











#### 关于行为建模

对于初学者最好不要乱用行为建模， 下面的问题可以帮助大家测试自己是否已经掌握Verilog的本质:

- 在硬件描述语言中, "执行"的精确含义是什么?

  > 
  
- 是谁在执行Verilog的语句? 是电路，综合器，还是其它的?

  > 严格来说，并没有一个执行的主体。在综合器层面它的作用是用于描述RTL的结构，以供综合器匹配对应的标准单元，而在电路层面Verilog压根就不存在了，剩下的只是电路自己运行而已。只有仿真器可以说是“执行”，但是对仿真器层面Verilog只是描述了一个事件模型，也不算所谓执行？

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















































