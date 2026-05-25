# HDL基础
## 基本语法

#### 最简单的

比如下面这个例子：

```verilog
module example(
input a,
input b,
input c,
output y
);
assign y = ~a & ~b & ~c
```

`module`-`endmodule`: 模块的开始和结束

`input`/`output`: 输入输出端，不声明默认一位，否则就要用[3:0]这种声明数据位。

`wire`表示线缆，它是一种数据类型，它只能赋值，不能存储值，但是它的值可以被引用（换句话说其实就是中间的一个计算的临时变量），与之相反的是`reg`可以存值

#### 与门：

```verilog
module and4(
    input	[3:0]	a,
    output			y
);
    assign y = &a;
    //which is equal to a[0] & a[1] & ...
```

- `a[0]`：我们可以直接提取其中的几位
- `&`：按位与/归并与操作。如果只有一个操作数代表所有位执行与操作

#### 全加器：

```verilog
module fulladder(
input	a,
input	b,
input	cin,
output	s,
output cout
);
wire	p, g; 		// internal nodes
assign	p = a ^ b;
assign	g = a & b;
assign	s = p ^ cin;
assign cout = g | (p & cin);

endmodule;
```

#### 三态门：

```verilog
module tristate(
    input	[3:0]	a,
    input 	en,
    input	[3:0]	y,
)
    assign y = en ? a : 4'bz
endmodule
```

这里说明一下：

- `z`：高阻态。有4状态：`0`/`1`/`x`/`z`，低/高/不确定/高阻态
- `4'bz`：4bit/binary/z

<img src="/images/image-20260506212955216.png" alt="image-20260506212955216" style="zoom:67%;" />

```verilog
//8位2路选择器
module	mux2(
    input	[3:0]	d0,
    input	[3:0]	d1,
    input			s,
    output	[3:0]	y,
);
    assign y = s ? d0 : d1;
endmodule
module mux2_8(
    input 	[7:0]	d0,
    input	[7:0]	d1,
    input			s,
    output	[7:0]	y
);
    mux2 lsbmux(d0[3:0], d1[3:0], s, y[3:0]);
    mux2 msbmux(
        .d0		(d0[7:4]),
        .d1		(d1[7:4]),
        .s		(s),
        .y		(y[7:4])
    );
endmodule
```

- **模块例化复用**，我们首先定义了`mux2`，然后在更顶层`mux2_8`里面把它实例化了，而实例化名称必须唯一。这里有两种实例化方法，第一种就是`lsbmux`里面的直接按顺序输入，另一种就是`msbmux`里面的`.<name>	<input>`的形式
- **位拼接**，也就是说我们输出的只要位不冲突且互补就是会自动拼接完成
比如下面这个例子, 对输入进行零/符号扩展（`16{1'b0}`表示生成16个连续的0）
```verilog
wire    [31:0]  out_32bitz = {{16{1'b0}}, in_16bit};
wire    [31:0]  out_32bits = {{16{in_16bit[15]}}, in_16bit};
```


#### D触发器：

它需要一个时钟源

```verilog
module	flop(
    input				clk,
    input		[3:0]	d,
    output	reg	[3:0]	q
);
    always@(posedge	clk)
        q <= d;
endmodule
```

- `always`：和`assign`地位相同的赋值关键字
  后面的`()`里面是敏感变量，即发生什么才触发此语句

  区别是`assign`只能处理单条组合逻辑，`always`可以处理时序逻辑和组合逻辑，而且可以进行多条赋值语句

- `reg`：寄存器，特别注意`always`块里面必须是`reg`，`assign`里面必须是`wire`

- `posedge`/`negedge`：`always @(posedge clk)`表示在clk上升沿时刻执行内部语句

- 阻塞/非阻塞赋值：`<=`与`=`
  ```verilog
  always@(posedge clk)
      begin
          b = a;
          c = b;
          d = c;
      end
  always@(posedge clk)
      begin
          b <= a;
          c <= b;
          d <= c;
      end
  ```

  <img src="/images/image-20260506222029193.png" alt="image-20260506222029193" style="zoom:50%;" />
  这两个结果完全不同

  因此我们同样规定：

  1. 组合逻辑使用阻塞式`=`
  2. 时序逻辑用非阻塞时`<=`
  3. 同一个`always`块内只能存在一种赋值方式（要不然两个就冲突了）
  4. 一个信号只能在一个`always`或`assign`语句下赋值
  5. `always`不允许实例化模块

#### 同步复位的D触发器：

```verilog
module flopr(
    input				clk,
    input	[3:0]		d,
    input 				reset,
    output	reg	[3:0]	q
);
    always@(posedge clk)
        begin
            if(reset)
                q <= 4'b0;
            else
                q <= d;
        end
endmodule
```

- `if`/`else`: 可以嵌套，有优先级（必须前面那个if被排除了才可能执行后面的`else`语句。因此我们需要把复位逻辑放在第一个`if`下，保证优先级最高。另一种条件语句`case`就没有优先级

#### 异步复位电路：

```verilog
module flopren(
    input				clk,
    input				reset,
    input				en,
    input		[3:0]	d,
    output	reg	[3:0]	q
);
    always@(posedge clk, posedge reset)
        begin
        if(reset)
            q <= 4'b0;
        else if(en)
          	q <= d;
        end
endmodule
```

- 这里敏感变量列表里面包含了`posedge clk`和`posedge reset`，只要有一个发生就会执行always块内的逻辑。当然这里我们还是得强调，复位必须是最高优先级

  当然也因此，我们完全可以用`always`实现组合逻辑：
  ```verilog
  always@(*)
      begin
          y1 = a&b;
          y2 = a|b;
      end
  ```



#### 有限状态机FSM：

就像之前说的那样， 计算机本质就是由状体机构成的，永远是现态+输入=>输出，而D flop 就是一个最基本的状态机

```verilog
module	divideby3FSM (
    input	clk,
    input	reset,
    output	1
);
    parameter	s0 = 2'b00;
    parameter 	s1 = 2'b01;
    parameter	s2 = 2'b10;
    reg	[1:0]	state;
    reg	[1:0]	nextstate;

    // state reg
    always@ (posedge clk, posedge reset)
    	if (reset)	state <= S0;
	else 		state <= nextstate;
    //next state
    always@ (*)
    	case (state)
		S0:	nextstate = S1;
		S1: 	nextstate = S2;
		S2:	nextstate = S0;
	endcase
    //	output
    assign q = (state == S0);
endmodule
```
### **参数传递**

我们在例化模块的时候可能有些参数需要改变，这时候就可以参数传递`#(parameter ...)`

```verilog
module mux2
#(parameter width = 8)
(
    input   [width-1:0] d0, d1,
    input               s,
    output  [width-1:0] y
);
assign y = s ? d1 : d0;
endmodule
// 如果我们实例化还是一个8位那就默认参数
mux2 muxer(d0, d1, s, out);
// 但是不一样就可以传递给它
mux2 #(12) losmux(d0, d1, s, out);
```

### **测试文件：**

为了仿真测试，我们需要有一个激励来看对应的输出波形，这就需要额外写一个`testbench`，当然因为它只是电脑端的仿真，所以比实际电路灵活得多，允许使用verilog里面一些不可综合的关键字: `initial`/ `#`/ `$display`/ `$readmemb`/ `forever`...

比如如果要实现$y = \overline{b}\overline{c} + a\overline{b}$:
```verilog
module foo(
    input a,
    input b,
    input c,
    output y
);
assign y = ~b & ~c | a & ~b;
endmodule
```
那么最简单的测试文件：
```verilog
module  testbench1();
reg     a, b, c;
wire y;
foo dut(a, b, c, y);
initial begin
    a = 0; b = 0; 
```
这里我们完全可以直接声明变量（因为他们都不对外）

#### **自检测试文件**
也就是说测试会自己判断是不是输出有问题，然后对结果进行判断，打印错误信息

#### **测试向量**

这是一种更好的方法，就是我们把输入信号的各种组合以及对应的结果构成一测试向量，每个向量都包含一种输入状态以及该状态下期望的输出结果
首先，我们可以先生成一个向量测试文件`example.tv`
```
000_1
001_0
010_0
011_0
100_1
101_1
110_0
111_0
```







### 题目

1. fsm ps2：
   代码如下：

   ```verilog
   module top_module(
       input clk,
       input [7:0] in,
       input reset,    // Synchronous reset
       output done); //
   
       parameter byte1=2'b00, byte2=2'b01, byte3=2'b10, doned=2'b11;
       reg [1:0] state_buffer;	
       reg [1:0] state;
       always@(*) begin
               case (state)
                   byte1: state_buffer = (in[3]) ? byte2 : byte1;
                   byte2: state_buffer = byte3;
                   byte3: state_buffer = doned;
                   doned: state_buffer = (in[3]) ? byte2 : byte1;
                   default: state_buffer = byte1;
               endcase
       end
       always@(posedge clk) begin
           if(reset) state <= byte1;
           else state <= state_buffer;
       end
       assign done = (state == doned);
   endmodule
   ```

   主要问题就是我们在处理复位的时候不能造成冲突，因此等于是我们需要先通过组合逻辑算出来我们下一个状态，但是需要在时序逻辑里面判断我们是采用这个值还是复位！

2. fsm ps2 packet parser and datapath：
   没啥难的，就是得看清楚这里out_bytes是一个wire类型！得另外搞一个reg

   ```verilog
   module top_module(
       input clk,
       input [7:0] in,
       input reset,    // Synchronous reset
       output [23:0] out_bytes,		// it's not a reg!
       output done); //
   
       // FSM from fsm_ps2
       parameter byte1=2'b00, byte2=2'b01, byte3=2'b10, doned=2'b11;
       reg [1:0] state_buffer;	
       reg [1:0] state;
       reg [23:0] outbytes_buffer;
       reg [7:0] last_buffer;
       always@(*) begin
               case (state)
                   byte1: state_buffer = (in[3]) ? byte2 : byte1;
                   byte2: state_buffer = byte3;
                   byte3: state_buffer = doned;
                   doned: state_buffer = (in[3]) ? byte2 : byte1;
                   default: state_buffer = byte1;
               endcase
       end
       always@(posedge clk) begin
           // we firstly determine the state
           if(reset) begin 
               state <= byte1;
               outbytes_buffer <= 0;		// clear
           end
           else 
               begin
               state <= state_buffer;
           // then we allocate num2different part
                   case (state)
                       byte1: outbytes_buffer[23:16] <= in;
                       byte2: outbytes_buffer[15:8] <= in;
                       byte3: outbytes_buffer[7:0] <= in;
                       doned: outbytes_buffer[23:16] <= in;
               endcase
               end
       end
       assign done = (state == doned);
       // New: Datapath to store incoming bytes.
       assign out_bytes = outbytes_buffer;
   
   endmodule
   ```

   







## fpga原理

具体来说，查找表就是一个1bit位宽的ram罢了

我们以Spartan6芯片为例，底层就是一个6输入查找表和2个D触发器结构，而Slice作为Xilinx FPGA的基本单元，包含4个6输入lut和8个D触发器
![image-20260513150729379](/images/image-20260513150729379.png)

CLB（configurable Logic Blocks）是Spartan的主要资源，包含2个slice

多个CLB加上丰富的互联开关就构成了核心框架

而它内部除了大量CLB资源，还有一些其他硬件资源，block ram,内存控制器，时钟管理（cmt），dsp端口控制单元（IOB）。


