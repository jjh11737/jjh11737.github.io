---
title: "chisel"
date: 2026-11-04T16:56:52+08:00
draft: false
noteTags: ["电子", "Chisel"]
---


# Chisel学习笔记

> [cookbook](https://www.chisel-lang.org/docs/cookbooks/cookbook)
> [Explanations](https://www.chisel-lang.org/docs/explanations)
> 我个人认为Explanations好用的多


尽管Chisel主要集中在数字逻辑，它也支持模拟量 / 三态（通过`Analog`type）
而且它也提供了DPI-C的机制！

## mill

> [Build Scala with Mill](https://mill-build.org/mill/scalalib/intro.html)


## Chisel语法

### 基本组件



1. 基本类型 /  常量
    - chisel提供了3个数据类型来表示连线/组合逻辑/寄存器：

        - Bits
        - UInt
        - SInt

        ```scala
        Bits(8.W)
        UInt(8.W)
        SInt(8.W)
        ```
        这里的`n.W`代表将一个数字通过方法转换为一个Chisel的宽度，同样你可以这样：
        ```scala
        n.W
        0.U
        -3.S
        ```

        同时由于Chisel继承了Scala的类型推断，很多时候压根不需要写类型，这对宽度也适用！就像我们写常数时代码会比verilog可读很多：

        ```scala
        "hff".U         // 0xff
        "0377".U        // oct(0xff)
        "b1111_1111".U  // 
        "h_dead_beaf".U
        ```
        但同时我们也可以用ASCII码！比如：
        ```scala
        val aChar = 'A'.U
       ```

    - Bool，需要将scala的Boolean转换为Chisel专门的Bool类型

        ```scala
        Bool()
        true.B
        false.B
        ```

2. 组合逻辑电路

    - 基本的运算，同样使用一般的符号即可，支持各种运算：
        ```scala
        val and = a & b
        val add = a + b
        val neg = -a
        val div = a / b
        ```
        结果的宽度取决于：

        - `+`/`-`：最长的操作数（不过使用`+&`/`-&`会更方便，它会自动括一位接收进位）
        - `*`：操作数长度之和
        - `/`/`%`：被除数的长度
    - 组合逻辑信号：
        ```scala
        val w = Wire(UInt())
        w := a & b
        ```
        说明一下：
        
        - Wire至少得声明里面的是什么东西
        - `:=`是更新操作

    - 提取位 / 位拼接：
        ```scala
        val sign = x(31)
        val lowByte = Word(7, 0)
        val Word = highByte ## lowByte
        ```

    - Mux：
        ```scala
        vak res = Mux(sel, a, b)    // sel should be bool
        ```

3. 寄存器
   
    实际上就是DFF
    声明一个寄存器：
    ```scala
    val reg  = RegInit(0.U(8.W))
    ```
     写入 / 读取它：
     ```scala
     reg := d
     val q = reg
     ```
     当然，你也可以在定义时就给它连接好输入，还可以指定初始值：
     ```scala
     val reg = RegNext(d)
     val reg_ini = RegNext(d, 0.U)
     ```

     > 一个例子：
     > 实现一个计数器：
     > ```scala
     > val cntReg = RegInit(0.U(8.W))
     > cntReg := Mux(cntReg === 9.U, 0.U, cntReg + 1.U)
        ```

4. Bundle和Vec

    - Bundle
      
        可以理解为struct，就是把不同的信号绑在一起，通过名字访问对应的field。

        - 定义：

        ```scala
        class Channel() extends Bundle {
            val data = UInt(32.W)
            val valid = Bool()
        }
        ```

        - 使用：

        这个就简单多了，因为Scala里面都是通过new搞定的：

        ```scala
        val ch = Wire(new Channel())
        ch.data := 123.U
        ch.valid := true.B
        val b = ch.valid
        val channel = ch
        ```

    - Vec
      
        可以理解为数组，相同的类型组合在一起

        1. Combinational Vec

            ```scala
            val v = Wire(Vec(3, UInt(4.W)))     // 生成一个长度3单个宽4的向量
            v(0) := 1.U
            v(1) := 3.U
            v(2) := 5.U
            val index = 1.U(2.W)
            val out = v(index)
            ```

            那么基于此，我们完全可以简单地实现一个Mux：
            
            ```scala
            val m = Wire(Vec(3, UInt(8.W)))
            m(0) := x
            m(1) := y
            m(2) := z
            val muxOut = m(select)
            ```

            当然，初始化可以再简单一点，通过`VecInit`即可，它会自动生成Chisel的硬件，所以无须再用`Wire`包裹它了！：

            ```scala
            val defVec = VecInit(1.U(3.W), 2.U, 3.U)
            when (cond) {           // 这里when就是if，等价于几个Mux
                defVec(0) := 4.U
                defVec(1) := 5.U
                defVec(2) := 6.U
            }
            val vecOut = defVec(sel)
            ```
            那么mux就可以更简单地实现了：
            ```scala
            val m = VecInit(x, y, z)
            val muxOut = m(select)
            ```

        2. Register Vec

            比如我们想实现32个32位的寄存器堆，只需要3行代码（我们暂时先忽略时钟和复位以及各种输入输出）
            ```scala
            val registerFile Reg(Vec(32, UInt(32.W)))
            registerFile(index) := dIn
            val dOut = registerFile(index)
            ```

            复位！

            但是很显然我们希望它能被复位，而我们知道Reg设定初值是`RegInit`，Vec设定初值则是`VecInit`，那么我们应该输入一串序列作为初值了，这就可以用到Scala的`Seq`的`fill`方法来初始化：
            ```scala
            val resetRegFile = RegInit(VecInit(Seq.fill(32)(0.U(32.W))))
            val rdRegFile = resetRegFile(sel)
            ```

            > 当然了，真实的并不那么简洁，但是也好很多：
            > ```scala
            > class RegFile extends Module {
            > val io = IO(new Bundle {
            > val rs1 = Input(UInt(5.W))
            > val rs2 = Input(UInt(5.W))
            > val rd = Input(UInt(5.W))
            > val wd = Input(UInt(32.W))
            > val wen = Input(Bool())
            > 
            > val rdata1 = Output(UInt(32.W))
            > val rdata2 = Output(UInt(32.W))
            > })
            >   val regs = RegInit(VecInit(Seq.fill(32)(0.U(32.W))))
            > 
            >   when (io.wen && io.rd =/= 0.U) {
            >     regs(io.rd) := io.wd
            >   }
            > 
            >   io.rdata1 := Mux(io.rs1 === 0.U, 0.U, regs(io.rs1))
            >   io.rdata2 := Mux(io.rs2 === 0.U, 0.U, regs(io.rs2))
            > }
            > ```

    - 结合起来！

        这很自然，因为我们经常要面对类似的情况：

        ```scala
        class BundleVec extends Bundle {
            val field = UInt(8.W)
            val vector = Vec(4, UInt(8.W))
        }
        // 或者反过来
        val vecBundle = Wire(Vec(8, Channel()))
        ```
        > pitfall：
        > 在Chisel3 里面，已经不支持分开赋值了！比如这段代码会在elaboration时报错
        > ```scala
        > val assignWord = Wire(UInt(16.W))
        > assignWord(7,0) := lowByte
        > assignWord(15,8) := highByte
        > ```
        > 这是因为我们用Bundle会更合适(？)虽然正常人应该都直接`##`吧



5. Wire / Reg / IO 
   
    很显然，我们的`UInt` / `SInt` / `Bits`本身没有对应的硬件，需要我们先把它们包装到`Wire` / `Reg` / `IO`端口来生成硬件












常见的数据类型：


| Chisel 类型  | 含义               | 位宽  | 示例                     |
| ------------ | ------------------ | ----- | ------------------------ |
| `UInt`       | 无符号整数         | 可变  | `UInt(8.W)`              |
| `SInt`       | 有符号整数（补码） | 可变  | `SInt(8.W)`              |
| `Bool`       | 布尔类型           | 1 bit | `Bool()`                 |
| `Clock`      | 时钟信号           | 1 bit | `Clock()`                |
| `Reset`      | 复位信号           | 1 bit | `Reset()`                |
| `AsyncReset` | 异步复位信号       | 1 bit | `AsyncReset()`           |
| `FixedPoint` | 定点数             | 可变  | `FixedPoint(16.W, 8.BP)` |
| `Analog`     | 双向模拟连接       | 可变  | `Analog(8.W)`            |


全部的Operator：

| Operation                                   | Explanation                                           |
| ------------------------------------------- | ----------------------------------------------------- |
| **Bitwise operators**                       | **Valid on:** SInt, UInt, Bool                        |
| `val invertedX = ~x`                        | Bitwise NOT                                           |
| `val hiBits = x & "h_ffff_0000".U`          | Bitwise AND                                           |
| `val flagsOut = flagsIn | overflow`         | Bitwise OR                                            |
| `val flagsOut = flagsIn ^ toggle`           | Bitwise XOR                                           |
| **Bitwise reductions.**（也就是自己的逐位运算）                     | **Valid on:** SInt and UInt. Returns Bool.            |
| `val allSet = x.andR`                       | AND reduction                                         |
| `val anySet = x.orR`                        | OR reduction                                          |
| `val parity = x.xorR`                       | XOR reduction                                         |
| **Equality comparison.**                    | **Valid on:** SInt, UInt, and Bool. Returns Bool.     |
| `val equ = x === y`                         | Equality                                              |
| `val neq = x =/= y`                         | Inequality                                            |
| **Shifts**                                  | **Valid on:** SInt and UInt                           |
| `val twoToTheX = 1.S << x`                  | Logical shift left                                    |
| `val hiBits = x >> 16.U`                    | Right shift (logical on UInt and arithmetic on SInt). |
| **Bitfield manipulation**                   | **Valid on:** SInt, UInt, and Bool.                   |
| `val xLSB = x(0)`                           | Extract single bit, LSB has index 0.                  |
| `val xTopNibble = x(15, 12)`                | Extract bit field from end to start bit position.     |
| `val usDebt = Fill(3, "hA".U)`              | Replicate a bit string multiple times.                |
| `val float = Cat(sign, exponent, mantissa)` | Concatenates bit fields, with first argument on left. |
| **Logical Operations**                      | **Valid on:** Bool                                    |
| `val sleep = !busy`                         | Logical NOT                                           |
| `val hit = tagMatch && valid`               | Logical AND                                           |
| `val stall = src1busy || src2busy`          | Logical OR                                            |
| `val out = Mux(sel, inTrue, inFalse)`       | Two-input mux where sel is a Bool                     |
| **Arithmetic operations**                   | **Valid on Nums:** SInt and UInt.                     |
| `val sum = a + b` *or* `val sum = a +% b`   | Addition (without width expansion)                    |
| `val sum = a +& b`                          | Addition (with width expansion)                       |
| `val diff = a - b` *or* `val diff = a -% b` | Subtraction (without width expansion)                 |
| `val diff = a -& b`                         | Subtraction (with width expansion)                    |
| `val prod = a * b`                          | Multiplication                                        |
| `val div = a / b`                           | Division                                              |
| `val mod = a % b`                           | Modulus                                               |
| **Arithmetic comparisons**                  | **Valid on Nums:** SInt and UInt. Returns Bool.       |
| `val gt = a > b`                            | Greater than                                          |
| `val gte = a >= b`                          | Greater than or equal                                 |
| `val lt = a < b`                            | Less than                                             |
| `val lte = a <= b`                          | Less than or equal                                    |





## 构建和测试

首先我们应该先明确，我们的Chisel在干什么？为什么它能生成verilog代码？

实际上标准的Chisel需要先被翻译为FIRRTL再翻译为具体的sv / v / vhdl之类的

整个Chisel的Tool Flow大体如此：
![image-20261104191225212](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261104191225212.png)

那么对我们来说，需要重点了解的还有就是[CIRCT的官方文档](https://circt.llvm.org/docs/)了


