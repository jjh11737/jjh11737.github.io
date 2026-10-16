---
title: "Rust_Learn"
date: 2026-08-17T00:00:00+08:00
draft: false
hiddenInRss: false
searchHidden: false
robotsNoIndex: false
sitemap:
  disable: false
noteTags: ["计算机", "Rust"]
---


# Notes for rust
the link of book: https://doc.rust-lang.org/book/ch01-03-hello-cargo.html

> 实话说我不认为这本教程有多好...学的时候总感觉作者不知道自己想表达什么

在这里记录我的Rust学习笔记

不过也可以看看[cheat sheet](https://cheats.rs/)...

[另一个](https://speedsheet.io/s/rust)

[Rust参考手册(zh-CN)](https://rustwiki.org/zh-CN/reference/attributes.html)

如果你想查询标准手册，你可以随时`rustup doc`，它会打开文档

找里面的API documentation部分就行了

> 不得不说Rust在手册这块做的其实相当好... 因为你甚至可以直接点进去读源码!
> 而另一方面我感觉写Rust确实需要天天查文档，反正我是记不住这么多方法和trait的



## 第一部分 瞎折腾

### 工具链

首先我们自然要搞清楚我们的工具链包含哪些？

- `rustc`：也就是rust的编译器，这玩意和`gcc`差不多，都是先通过parser生成AST，不过它有自己的`MIR`，再通过这个生成`LLVM IR`，之后只需要复用LLVM的后端即可

- `cargo`：包管理器 + 构建系统 + 项目管理工具

  > 它会看`Cargo.toml`这个配置文件，决定如何构建这个项目，然后解析依赖关系后建立依赖关系图，确定编译顺序交给rustc完成编译

- `crates.io`：专门用来存放依赖的，需要什么crates就可以从这里获取

- `rustup`：管理rust编译器本身的工具

- `clippy`：一个Linter，可以做静态分析

- `rust-analyzer`：Language Server，rust的LSP实现

- `rustdoc`：文档生成工具

- `rustfmt`：代码格式化工具

### 安装
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env     # 前提你用的是bash之类的
```
### 项目结构
一个典型的rust项目结构是：
```bash
├── Cargo.lock
├── Cargo.toml
├── src
│   └── main.rs
└── target
    ├── CACHEDIR.TAG
    └── debug
    ...
```
### 基本指令(Cargo)
- `cargo new` 创建一个新项目
- `cargo build` 编译这个项目
- `cargo run` 运行
- `cargo test`： 测试项目，会编译并且生成可执行文件，也会编译测试代码并执行测试程序
- `cargo check`：检查程序的各种问题（比build更快），判定能不能编译，但是不会生成可执行文件，只是分析而已
- `cargo doc` 创建一个文档，其中.html长这样：
  ![image-20260831182933059](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260831182933059.png)
- `cargo publish` 把一个库公开到`crates.io`
### 第一个程序
```bash 
cargo new guessing_game
```

> `new`出来的程序总是一个：
>
> ```rust
> fn main(){
>     println!("Hello World")
> }
> ```

```rust
use std::io;
fn main(){
    println!("Guess the num!");
    println!("Input your guess:");
    let mut guess = String::new();
    io::stdin()
        .read_line(&mut guess)
        .expect("Failed to readline...");
    println!("You guessed: {guess}");
}

```

##### 解释一下：

- 首先，我们需要通过io来完成输入输出，而`io`库来自于`std`，因此我们写：`use std::io`

  > 这实际上是把一个路径引入当前作用域，如果我们不加这个那就得变成：
  > ```rust
  > std::io::stdin()
  > ```
  >
  > 意思是让它把`io`解析为`std::io`

- 而同样我们知道程序需要一个入口，那么rust默认就是`main`，那么很显然，它肯定也是支持命令行参数和环境变量的（不过这里我们暂时不管这方面）、

- `println!`是一个宏，末尾加上`!`就是说明这是个宏而非函数调用

  > 既然是宏，那我们就得展开看看...
  > ```bash
  > $ rustc +nightly -Zunpretty=expanded main.rs
  > ```
  >
  > ```rust
  > #![feature(prelude_import)]
  > #![no_std]
  > extern crate std;
  > #[prelude_import]
  > use ::std::prelude::rust_2015::*;
  > use std::io;
  > fn main() {
  >     { ::std::io::_print(format_args!("Guess the num!\n")); };
  >     { ::std::io::_print(format_args!("Input your guess:\n")); };
  >     let mut guess = String::new();
  >     io::stdin().read_line(&mut guess).expect("Failed to readline...");
  >     { ::std::io::_print(format_args!("You guessed: {0}\n", guess)); };
  > }
  > ```
  >
  > 用nightly是为了使用`-Z`选项，因为这个在`stable`不支持
  >
  > > Rust有3部分：
  > > nightly$\to$beta$\to$stable，默认用的是`stable`

- `let`就是创建一个变量，但是rust和C不同的一点就是rust的变量声明后默认是`immutable`的，而我们想要后续看修改它就必须声明为`mut`：

  ```rust
  let mut a = 10;
  ```

  > 为什么要这样？
  >
  > Rust希望默认情况下一个binding创建后就不会再被重新赋值，这样的好处主要体现在读代码时，比如：
  >
  > ```rust
  > let x = something();
  > ```
  >
  > 那么我们就可以很放心地认为后续它就是这个值了。这是给编译器和开发者看的。
  >
  > 这和`const`又不一样...因为`mut`并不会让这个值变成编译期常量，具体来说：
  >
  > | 语句               | 含义                 |
  > | ------------------ | -------------------- |
  > | `let x = ...`      | 不允许给`x`重新赋值  |
  > | `let mut x = ...`  | 允许给`x`重新赋值    |
  > | `const X : T =...` | 编译期常量           |
  > | `let x: T`         | 先声明不过还不初始化 |
  >
  > 

- 处理输入：
  ```rust
      io::stdin()
          .read_line(&mut guess)
          .expect("Failed to readline...");
  ```

  这里调用了`io`模块的`stdin`函数来处理用户输入，之后我们调用了`.readline`方法，这里的`&mut guess`告诉`readline`应该放到哪个string里面。

  这里的`&`含义是引用，关于引用：

  | Rust     | 含义                                             |
  | -------- | ------------------------------------------------ |
  | `&x`     | 创建共享引用，借用`x`，不能通过它修改`x`         |
  | `&mut x` | 创建可变引用，可以通过它修改`x`，不能同时存在2个 |
  | `*r`     | 解引用                                           |
  | `&T`     | 类似`const T *`？                                |
  | `&mut T` | `T *`？                                          |

- placeholder：

  `{}`是用来占位的，它的作用是代表一个值，你可以这样使用：

  ```rust
  let x = 5;
  let y = 10;
  println!("x = {x} and y + 2 = {}", y + 2)
  ```

----

##### 加入随机数

而我们如果想要加上一个随机数呢？那就可以用`rand`这个crate了，我们加到`[dependencies]`的尾部

```bash
echo "rand=\"0.8.5\"" >> Cargo.toml
```

通过`SemVer(Semantic Versioning)`，我们可以保证各个包之间的依赖关系不出错，

而代码就可以变为：
```rust
use std::io;
use rand::Rng;
fn main(){
    println!("Guess the num!");
    println!("Input your guess:");
    let secret_num = rand::thread_rng().gen_range(1..=100);
    let mut guess = String::new();
    io::stdin()
        .read_line(&mut guess)
        .expect("Failed to readline...");
    println!("You guessed: {guess}, the number is: {secret_num}");
}
```

这里`Rng`就是一个trait，相当于一组API的接口，这是一个能力的规范。

- 为什么要这样？因为我们用到了`gen_range`这个属于函数`thread_rng()`的方法，如果我们直接`use rand::thread_rng()`的话结果就会报错，因为这是trait规定的方法。
- 而至于这个`thread_rng()`是根据线程来生成的随机数

----

##### 加入比较

我们先看这段代码：
```rust
use std::cmp::Ordering;
use std::io;

use rand::Rng;

fn main() {
    // --snip--

    println!("You guessed: {guess}");

    match guess.cmp(&secret_number) {
        Ordering::Less => println!("Too small!"),
        Ordering::Greater => println!("Too big!"),
        Ordering::Equal => println!("You win!"),
    }
}
```

你会发现它跑不起来：
```bash
error[E0308]: mismatched types
  --> src/main.rs:13:21
   |
13 |     match guess.cmp(&secret_num){
   |                 --- ^^^^^^^^^^^ expected `&String`, found `&{integer}`
   |                 |
   |                 arguments to this method are incorrect
   |
   = note: expected reference `&String`
              found reference `&{integer}`
note: method defined here
  --> /rustc/88d9e12ae178fab0fb5cc050a94da85685d449ea/library/core/src/cmp.rs:1000:7

For more information about this error, try `rustc --explain E0308`.
error: could not compile `guessing_game` (bin "guessing_game") due to 1 previous error
```

这个问题...主要是因为我们`guess`的类型还是`String`，那么自然我们调用`cmp`方法时就需要一个`String`类型了，所以我们得做一个类型转换：
```rust
let guess: u32 = guess.trim().parse().expect("Please type a number!");
```

- 这里利用的是rust的`Shadowing`，也就是说我们可以重新利用这个变量名（不过只是shadowing，不会跨作用域造成修改

**`let`创建新绑定，赋值修改旧绑定**。（let干的事情是创建一个新的名字绑定(binding)，让这个名字指向一个值）

- 而这里`guess.trim().parse()`，这里的`trim()`

- `let guess: u32`：这里的`:`就是说明我们要在这里声明变量类型了

  同时编译器也能从这里推断出`secret_num`是`u32`的

更进一步，我们其实可以不断比较直到猜对：
```rust
    loop {
        println!("Please input your guess.");

        // --snip--

        match guess.cmp(&secret_number) {
            Ordering::Less => println!("Too small!"),
            Ordering::Greater => println!("Too big!"),
            Ordering::Equal => {
                println!("You win!");
                break;
            },
        }
    }
```

---

##### 处理非法输入

```rust
        // --snip--

        io::stdin()
            .read_line(&mut guess)
            .expect("Failed to read line");

        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,			// 返回输入的num
            Err(_) => continue,		// 忽略输入
        };

        println!("You guessed: {guess}");

        // --snip--
```

这里`match`是一个返回值的语句，而这里的`Ok` / `Err`来自一个`Result`类型，它是一个枚举，只有`Ok` / `Err`两个变体
```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```





----

##### 编译的过程？

不过这样总是不太舒服！我想先看看对应的汇编代码是什么样的，这当然可以了：

```bash
rustc main.rs \
    --emit=mir,llvm-ir,asm,obj,link
# 生成mir / llvmIR / 汇编 / 可重定位目标文件 / 链接后的可执行目标文件
```

还可以看看不同优化程度生成的`.ll`代码的不同：
```bash
rustc -C opt-level=0 --emit=llvm-ir main.rs
rustc -C opt-level=3 --emit=llvm-ir main.rs
```

而且`rustc`还支持交叉编译（这不是当然的吗）,想要看看支持哪些目标可以：
```bash
rustc --print target-list
```

而编译的时候就可以指定对应的target了：
```bash
rustc --target riscv64gc-unknown-linux-gnu ...
```

----





## 第二部分 通用的东西

### 2.1 Variable & Mutability



| 语句               | 含义                       |
| ------------------ | -------------------------- |
| `let x = ...`      | 不允许给`x`重新赋值        |
| `let mut x = ...`  | 允许给`x`重新赋值          |
| `const X : T =...` | 编译期常量（需要声明类型） |

##### 声明常量：

1. 不能把`mut`和`const`一起用，因为常量必然是默认`immutable`的
2. 常量必须被赋值为常量表达式而不是一个运行时计算出的值

##### Shadowing

我们往往说后面一个`overshadow`了前面声明的binding，不过为了更好地理解这种关系，看看这个例子：
```rust
fn main() {
let x = 5;

    let x = x + 1;

    {
        let x = x * 2;
        println!("The value of x in the inner scope is: {x}");
    }

    println!("The value of x is: {x}");
}
```

- 后面声明的`let`会在同一个作用域内覆盖同名的`let`声明

- 无法跨作用域覆盖，覆盖仅在这个覆盖语句作用域内有效，离开这个作用域那么这个`shadowing`就自动失效了...

- 可以是不同的类型，因为我们声明的是binding

  > 这带来不少好处，好优化而且也很自然地完成shadowing

- 我们甚至可以复用shadowing之前的binding：
  ```rust
      let spaces = "   ";
      let spaces = spaces.len();
  ```

### 2.2 Data Types

有两个子集，scalar标量 / compound复合

#### Scalar Type：

##### Interger

| Length                                        | Signed  | Unsigned |
| --------------------------------------------- | ------- | -------- |
| 8-bit                                         | `i8`    | `u8`     |
| 16-bit                                        | `i16`   | `u16`    |
| 32-bit                                        | `i32`   | `u32`    |
| 64-bit                                        | `i64`   | `u64`    |
| 128-bit                                       | `i128`  | `u128`   |
| Architecture-dependent（与ISA规定的XLEN相关） | `isize` | `usize`  |

| Number literals  | Example       |
| ---------------- | ------------- |
| Decimal          | `98_222`      |
| Hex              | `0xff`        |
| Octal            | `0o77`        |
| Binary           | `0b1111_0000` |
| Byte (`u8` only) | `b'A'`        |

以及关于整数溢出，不同于C里面定义为UB(当然是singed)，rust需要考虑模式：

- **debug mode**：rust会检测到整数溢出然后在运行时**panic**

- **release mode**：也就是你加上`--release`标志时，此时rust不会包含对整数溢出的检测panic，而只是进行2的补码的环绕，也就是正常的加法而已

  > 换句话说，从这个角度rust并没有考虑那种超老的不使用补码的机器

- 如果你想显式地处理整数溢出的可能，有几种方法：

  - `wrapping_*`方法
  - `checked_*`方法
  - `overflowing_*`方法
  - `saturating_*`方法

---

##### Floating-Point

`f32`和`f64`，就是单精度和双精度，默认是`f64`因为现代的处理器都是这个位宽的：（当然是按照IEEE 754标准的）

```rust
fn main() {
    let x = 2.0; // f64

    let y: f32 = 3.0; // f32
}
```

----

##### Numeric Operations

```rust
fn main() {
    // addition
    let sum = 5 + 10;

    // subtraction
    let difference = 95.5 - 4.3;

    // multiplication
    let product = 4 * 30;

    // division
    let quotient = 56.7 / 32.2;
    let truncated = -5 / 3; // Results in -1

    // remainder
    let remainder = 43 % 5;
}
```

----

##### Boolean

Boolean是1byte大小

```rust
fn main() {
    let t = true;

    let f: bool = false; // with explicit type annotation
}
```

----

##### Char

这是Rust最独特的地方，`char`不是1byte字符，而是Unicode scalar value，大小固定4bytes，也就是说甚至可以这样：
```rust
fn main() {
    let c = 'z';
    let z: char = 'ℤ'; // with explicit type annotation
    let heart_eyed_cat = '😻';
}
```



#### Compound Types：

内建的复合类型（无须自定义即可）：tuple / array / struct / enum

##### tuple

类型可以不一样的集合，没啥好说，每个元素你可以单独定义类型，也可以直接赋值：

```rust
fn main() {
    let tup: (i32, f64, u8) = (500, 6.4, 1);
}
fn main() {
    let tup = (500, 6.4, 1);

    let (x, y, z) = tup;

    println!("The value of y is: {y}");
}
```

通过`.`加index访问：
```rust
fn main() {
    let x: (i32, f64, u8) = (500, 6.4, 1);

    let five_hundred = x.0;

    let six_point_four = x.1;

    let one = x.2;
}
```

而如果一个tuple没有任何值，它就是一个`unit`，它的值和类型都写作`()`，代表一个空值。表达式如果没有别的返回值就会返回`unit`。

##### Array 

```rust
fn main() {
    let a = [1, 2, 3, 4, 5];
    let months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
}
```

声明类型：

```rust
let a: [i32; 5] = [1, 2, 3, 4, 5];
```

也可以这样初始化：

```rust
let a = [3; 5];		// 5个3
```

访问和c一样，越界了的话会自己panic的（好处就是不会只有操作系统的段错误）



### 2.3 function

#### parameters

函数声明时，必须声明每个参数的类型：
```rust
fn main() {
    print_labeled_measurement(5, 'h');
}

fn print_labeled_measurement(value: i32, unit_label: char) {
    println!("The measurement is: {value}{unit_label}");
}
```

#### statements & expressions

我们需要区分二者：

- statement：执行某件事，但是不产生值
- expression：产生一个值

> 而Rust有趣的就在于几乎所有东西都是expression

因此显然这是不合法的：

```rust
let y = (let x = 10);
```

正因为如此，我们只能这么写：
```rust
let y = {
        let x = 3;
        x + 1
};
```



#### functions with return Values

如果有返回值：

- 必须加上`->`符号指明返回类型。

- 默认返回的就是最后一行的表达式

- 当然你也可以显式return

- 如果最后一行不是表达式没有值就返回`()`，而如果你恰好声明了`->`那就会报错，因为返回类型不匹配，编译错误

- 只要有值就行，换句话说还可以：

  - 控制流表达式：
    ```rust
    fn foo(x: bool) -> i32 {
        if x {
            1
        } else {
            2
        }
    }
    ```

    这是可以的，但是你不能写：
    ```rust
    fn foo(x: bool) -> i32 {
        if x {
            1
        }
    }
    ```

    因为没有`else`的`if`返回的是`()`

  - `loop`：

    如果内部有返回的值也是可以的：
    ```rust
    fn foo() -> i32 {
        loop {
            break 10;
        }
    }
    ```

  总之只要满足：
  ```rust
  fn foo() -> T {
      body
  }
  ```

  其中`body`返回值是T类型的即可

### 2.4 control flow

#### if：

- 是表达式，有返回值
- 给到`if`的必须是bool类型的。

- `if`可以用在`let`语句当中：（正因为是表达式）

  ```rust
  let condition = true;
  let number = if condition {5} else {6};
  ```

  但是你不能写：
  ```rust
  fn main() {
      let condition = true;
      let number = if condition { 5 } else { "six" };
      println!("The value of number is: {number}");
  }
  ```

  因为分支必须返回值类型一致，否则编译报错

- `else if`是从上往下检查短路的

#### loop：

- 很有趣的是，它不同于while / for，是一个表达式，可以通过break返回值！

- 也只能通过break退出，并且break只会退出最内的一层

- 如果你想直接退出外层，就需要给循环加个标签：
  ```rust
  'outer: loop {
      loop {
          break 'outer;
      }
  }
  ```

#### while：

- 没啥好说的，就是while

#### for：

- 最推荐的写法，因为可以防止越界，无须运行时检查，while还得手写

- 写法：
  ```rust
  for i in 0..10 {
  	// ...
  }
  ```

- 可以用迭代器（倒不如说这个`for`本质就是基于迭代器的语法糖）：
  ```rust
  let a = [10, 20, 30];
  
  for x in a.iter() {		// .iter()生成一个迭代器
      println!("{}", x);
  }
  ```

  

## 3 Ownership

写任何代码时，**一定要考虑好我们操作的是引用还是所有权！**！

**rust最重要的功能**，可以说对整个语言影响很大，它让rust实现内存安全检查而无需GC

> 所有权就是帮助我们管理动态内存分配，也就是堆，因为堆的分配显然是运行时决定的，而栈一方面是编译器管理的，而且操作在编译期就确定布局了，而且本身就和函数调用相关而且是LIFO，管理起来很简单。

我们简单地来说，所谓Ownership就是对应一个“资源”的唯一管理权，是一个绑定关系。我们当然也可以通过地址引用来访问这个对象，但是这样的访问无权决定这个资源的分配和释放的管理。它管理的就是一个生命周期和使用权限本身！

### what's ownership

#### 所有权的规则：

- 每个值都有一个owner
- 同一时间只能有一个owner
- 当owner不存在时（离开作用域 / 所有权被转移），值就会被释放(drop)

#### String作为例子

为了演示我们用最普遍的内存问题作为例子，而最合适的就是`String`了，关注它和所有权相关的部分

`String`类型就是为了把字符串操作封装起来，这样开发者就不用关注这些底层细节了：

```rust
let mut s = String::from("hello");
s.push_str(", world!");
println!("{}", s);
```

- 当我们调用`String::from`时，它的实现向内存分配器请求所需的内存

- 当我们用完`String`时需要将内存释放返回给内存分配器：

  - 如果有`GC`我们便不用关心，但是如果没有，我们就得花时间在考虑内存分配问题上，每个`malloc`必须配对一个`free`

  - Rust的方法是：内存在拥有它的变量离开作用域后自动被释放，比如这个例子：
    ```rust
    fn main() {
        {
            let s = String::from("hello"); // 从此处起，s 开始有效
            // 使用 s
        }                                  // 此作用域已结束，
                                           // s 不再有效
    }
    ```

    > 但是我个人认为这不是一个很好的例子，因为很显然这个`"hello"`字符串本身肯定是会被放到`.rodata`段的，而我们声明的`s`作为`String`在实际使用时又的确需要在堆上分配对应的内存（因为`String`本身的可变性就要求这一点），所以说其实不是一回事...

    当`s`离开作用域时，那么很自然这个内存就会被释放，Rust会调用一个叫作`drop`的函数

#### move

我们来看看这个例子：
```rust
let s1 = String::from("hello");
let s2 = s1;
```

当我们执行`let s2 = s1`时，我们是从栈上把指针 / 长度 / 容量都从`s1`拷贝给了`s2`，当然rust永远不会愚蠢地自动进行深拷贝。但是此时就出现问题了，有两个都指向这段内存，那么在离开作用域时我们岂不是会有**二次释放**？这会导致内存污染... 

而这实际上不会发生，因为当我们`let s2 = s1`时，我们就认为`s1`失效：
```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;

    println!("{}, world!", s1);
}

```

它会报错：
```rust
$ cargo run
   Compiling ownership v0.1.0 (file:///projects/ownership)
error[E0382]: borrow of moved value: `s1`
 --> src/main.rs:5:28
  |
2 |     let s1 = String::from("hello");
  |         -- move occurs because `s1` has type `String`, which does not implement the `Copy` trait
3 |     let s2 = s1;
  |              -- value moved here
4 | 
5 |     println!("{}, world!", s1);
  |                            ^^ value borrowed here after move

For more information about this error, try `rustc --explain E0382`.
error: could not compile `ownership` due to previous error

```

> 但是即便如此，我们其实只需要换个方法就好了，也就是通过引用：
>
> ```rust
> fn main() {
>     let s1 = String::from("hello");
>     let s2 = &s1;
>     println!("{}, world!", s1);
> }
> ```
>
> 这样就可以正确执行了！

#### clone

如果我们确实需要深拷贝也就是堆上的复制，那么就得使用`clone`这个方法：
```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1.clone();

    println!("s1 = {}, s2 = {}", s1, s2);
}
```

这样也没问题！

> 但是很蠢啊，浪费资源，没必要

#### copy / drop trait

- 如果一个类型实现了`Copy` trait，那么一个旧的变量在被赋值给其他变量后仍可以使用。允许隐式复制

- 而如果一个类型是`Drop`的，那么它就不能这样

- 这两个性质是互斥的

- 可以`Copy`的一些类型：
  - 所有的Scalar Type
  - 引用
  - 成员Copy的tuple / struct / array



#### 所有权和函数

按值传递给函数在语义上和给变量赋值差不多：
```rust
fn main() {
  let s = String::from("hello");  // s 进入作用域

  takes_ownership(s);             // s 的值移动到函数里 ...
                                  // ... 所以到这里不再有效

  let x = 5;                      // x 进入作用域

  makes_copy(x);                  // x 应该移动函数里，
                                  // 但 i32 是 Copy 的，所以在后面可继续使用 x

} // 这里, x 先移出了作用域，然后是 s。但因为 s 的值已被移走，
  // 所以不会有特殊操作

fn takes_ownership(some_string: String) { // some_string 进入作用域
  println!("{}", some_string);
} // 这里，some_string 移出作用域并调用 `drop` 方法。占用的内存被释放

fn makes_copy(some_integer: i32) { // some_integer 进入作用域
  println!("{}", some_integer);
} // 这里，some_integer 移出作用域。不会有特殊操作

```

- 这里调用`takes_ownership`后我们后续就不能再使用`s`了

  > 因此如果我们还想使用，就不能按值传递，而是把引用作为参数，这样就保证了ownership唯一而且还能继续使用了

- `x`由于是`Copy`的，因此传递给函数也不影响

#### 返回值和作用域

返回值本身也是会转移所有权的：
```rust
fn main() {
  let s1 = gives_ownership();         // gives_ownership 将返回值
                                      // 移给 s1
  let s2 = String::from("hello");     // s2 进入作用域
  let s3 = takes_and_gives_back(s2);  // s2 被移动到
                                      // takes_and_gives_back 中,
                                      // 它也将返回值移给 s3
} // 这里, s3 移出作用域并被丢弃。s2 也移出作用域，但已被移走，
  // 所以什么也不会发生。s1 移出作用域并被丢弃

fn gives_ownership() -> String {           // gives_ownership 将返回值移动给
                                           // 调用它的函数
  let some_string = String::from("yours"); // some_string 进入作用域
  some_string                              // 返回 some_string 并移出给调用的函数
}
// takes_and_gives_back 将传入字符串并返回该值
fn takes_and_gives_back(a_string: String) -> String { // a_string 进入作用域
  a_string  // 返回 a_string 并移出给调用的函数
}
```

当然如果我们想要获取多个返回值，就可以通过tuple来返回多个值：
```rust
fn main() {
    let s1 = String::from("hello");
    let (s2, len) = calculate_length(s1);
    println!("The length of '{}' is {}.", s2, len);
}

fn calculate_length(s: String) -> (String, usize) {
    let length = s.len(); // len() 返回字符串的长度
    (s, length)
}
```

> 但是还是前面所说，这样传递太麻烦了！

### references & borrowing

为了更方便地传递，我们很自然地想要用引用传递了：
```rust
fn main() {
    let s1 = String::from("hello");
    let len = calculate_length(&s1);
    println!("The length of '{}' is {}.", s1, len);
}

fn calculate_length(s: &String) -> usize {
    s.len()
}
```

这样传递时就不会move了，因为就没有拥有过，引用结束自然也不会调用`drop`，有效的作用域和函数参数还是一样的

将创建一个引用的行为称为**借用(borrowing)**

#### 可变引用

规则：

- `mut`加在`&`后面表示可变引用
- 可变引用只可以有一个，当存在可变引用时不允许存在任何别的引用（即使是不可变）

为了让我们可以修改被引用的对象，我们就需要加上`mut`了：
```rust
fn main() {
    let mut s = String::from("hello");
    change(&mut s);
}

fn change(some_string: &mut String) {
    some_string.push_str(", world");
}

```

而且关键在于我们**不能同时有两个对同一个对象的可变引用**，比如这个：
```rust
fn main() {
    let mut s = String::from("hello");
    let r1 = &mut s;
    let r2 = &mut s;
    println!("{}, {}", r1, r2);
}
```

这个限制的目的在于**防止data race**，它的发生需要**三个条件：**

- **多个指针同时访问统一数据**
- **至少一个指针被用于写入数据**
- **没有同步数据访问机制**

Rust不会编译存在数据竞争的代码！

而正因为如此，我们很自然地可以联想到这种情况也是不对的：
```rust
fn main() {
    let mut s = String::from("hello");
    let r1 = &s; // 没问题
    let r2 = &s; // 没问题
    let r3 = &mut s; // 大问题
    println!("{}, {}, and {}", r1, r2, r3);
}
```

因为**有了一个不可变的引用，这样就会发生数据竞态（因为访问可能是非原子而且没加锁的）**

---

#### 悬垂引用(dangling references)

对于有指针的语言，很可能明明一个内存已经被释放了但是还可以访问这部分内存，这就是所谓**悬垂指针dangling pointer**

这在rust里面是不可能的！这**会导致编译时错误**：
```rust
fn main() {
    let reference_to_nothing = dangle();
}

fn dangle() -> &String {
    let s = String::from("hello");
    &s
}
```

它会报错`missing lifetime specifier`：

> ```rust
> $ cargo run
>    Compiling ownership v0.1.0 (file:///projects/ownership)
> error[E0106]: missing lifetime specifier
>  --> src/main.rs:5:16
>   |
> 5 | fn dangle() -> &String {
>   |                ^ expected named lifetime parameter
>   |
>   = help: this function's return type contains a borrowed value, but there is no value for it to be borrowed from
> help: consider using the `'static` lifetime
>   |
> 5 | fn dangle() -> &'static String {
>   |                ^^^^^^^^
> 
> For more information about this error, try `rustc --explain E0106`.
> error: could not compile `ownership` due to previous error
> ```

这问题是显然的，当离开函数`dangle`的时候`s`已经离开作用域，而且偏偏我们返回的是引用，因此它就被`drop`了，而`main`里面得到的值就是个dangling pointer...

正确的做法是直接把所有权交出去：
```rust
fn no_dangle() -> String {
    let s = String::from("hello");
    s
}
```

### 切片Slice类型

这是另一个没有所有权的数据类型，它相当于用一种安全的方式包装了字符串的引用。

> 我们看一个例子：
>
> 编写一个函数，该函数接收一个字符串，并返回在该字符串中找到的第一个单词。如果函数在该字符串中并未找到空格，则整个字符串就是一个单词，所以应该返回整个字符串。

想一下它的签名？

```rust
fn first_word(s: &String) -> ?
```

行为不怎么复杂，但是该返回什么？我们可以返回这个词的结尾索引：

```rust
fn first_word(s: &String) -> usize {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return i;
        }
    }
    s.len()
}
```

> 具体来说，我们先调用`s.as_bytes()`把字符串转换为了字节数组。
>
> 之后使用`iter`方法在字节数组上创建了一个迭代器，`enumerate`方法则是包装了`iter`的返回，作为元组的形式，它返回的元组第一个元素是索引第二个是集合中元素的引用。因此我们解构模式用的就是`&`表示引用

这里返回的是一个索引，但是显然我们想得到的是一个string，但它是和`String`分离的...

#### 字符串slice

string slice是`String`中一部分值的引用：
```rust
fn main() {
    let s = String::from("hello world");
    let hello = &s[0..5];
    let world = &s[6..11];
}
```

Range的写法：

| 写法    | 类型             | 含义        |
| ------- | ---------------- | ----------- |
| `0..5`  | `Range`          | 0,1,2,3,4   |
| `0..=5` | `RangeInclusive` | 0,1,2,3,4,5 |
| `..5`   | `RangeTo`        | 开头到5之前 |
| `0..`   | `RangeFrom`      | 从0到结尾   |
| `..`    | `RangeFull`      | 全部        |

> 以及注意，slice range必须位于有效的UTF-8字符边界...

我们重写一下：

```rust
fn first_word(s: &String) -> &str {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' '{
            return &s[..i];
        }
    }
    &s[..]
}
```

由于slice是和`&String`绑定的，因此此时就会报错，因为slice是对字符串的一个不可变引用，而s.clear()方法的调用又是需要一个可变的引用的：（所以会有Comiling ownership时的报错）
```rust
fn main(){
    let s = String::from("hello world!");
    let word = first_word(&s);
    s.clear();
    println!("fw: {}", word);
}
```

#### 字符串字面量就是slice

而另一一方面字符串的字面量就是一个`slice`，比如这个`s`就是一个一`&str`类型的...

```rust
let s = "hlw";
```

#### slice作为参数

因此另一方面，我们完全可以换一个signature：

```rust
fn first_word(s: &str) -> &str {
```

这样的好处就是我们既可以传递整个`String`的引用也可以传递一个`slice`给我们的函数，更加通用

#### 其他的slice

实际上所有集合都可以使用slice



## 4  struct

先做个总览：

| Rust                  | C++/Java 等                  |
| --------------------- | ---------------------------- |
| `struct`              | `class` 的数据部分           |
| `impl`                | `class` 的方法部分           |
| `trait`               | interface / 抽象接口的一部分 |
| `impl Trait for Type` | 实现 interface               |
| `enum`                | Rust 特别强大的代数数据类型  |

#### 定义和说明

- 和C一样，你需要先定义结构体再去使用它，格式如下：

```rust
struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}
```

- 而我们也同样**可以用`.`访问结构体的成员**。如果想要更改里面的值就得设定为`mut`：

```rust
fn main() {
    let mut user1 = User {
        email: String::from("someone@example.com"),
        username: String::from("someusername123"),
        active: true,
        sign_in_count: 1,
    };
    user1.email = String::from("anotheremail@example.com");
}
```

- **注意：`mut`必须赋给整个实例，而不允许只给单个字段标记为可变**

- 作为参数传递（按引用）：
  ```rust
  fn area(rectangle: &Rectangle) -> u32 {
      rectangle.width * rectangle.height
  }
  ```

  

- 同样，我们可以在函数体的最后一个表达式构造一个结构体新实例来隐式地返回这个实例：
  ```rust
  fn build_user(email: String, username: String) -> User {
      User {
          email: email,
          username: username,
          active: true,
          sign_in_count: 1,
      }
  }
  // 因为参数名和字段名相同，你可以简化为：
  fn build_user(email: String, username: String) -> User {
      User {
          email,
          username,
          active: true,
          sign_in_count: 1,
      }
  }
  ```

- **结构体更新语法**：

  通过`..`我们可以直接指定剩余未显式设置值的字段与给定实例对应字段相同的值

  ```rust
  fn main() {
      // --snip--
  
      let user2 = User {
          active: user1.active,
          username: user1.username,
          email: String::from("another@example.com"),
          sign_in_count: user1.sign_in_count,
      };
      // 可以简化为：
      let user2 = User {
          email: String::from("another@example.com"),
          ..user1
      };
  }
  ```

  同样，**结构体更新语法还是等效为一个`=`的赋值**，此时：

  - `user1`不能再使用那些被拿出来更新的字段了
  - **只能使用那些没有被拿出来更新的字段**
  - **`user1`本身也不能被作为一个整体来使用了**
  - 当然`Copy`trait的除外
  - 注意！对于非copy的来说，它会采用move！因此必要时考虑clone

- **元组结构体(tuple struct)**：有结构整体的名字，但是没有具体的字段名

  > 当你想给整个元组取一个名字，并使元组成为与其他元组不同的类型时，元组结构体是很有用的，这时像常规结构体那样为每个字段命名就显得多余和形式化了。

  ```rust
  struct Color(i32, i32, i32);
  struct Point(i32, i32, i32);
  
  fn main() {
      let black = Color(0, 0, 0);
      let origin = Point(0, 0, 0);
  }
  ```

- **类单元结构体(unit-like structs)：**没有任何字段的结构体

  > 往往在你想要在某个类型上实现trait但是不需要在类型中存储数据时使用，这样做往往是我们想要实现一个泛型接口时

  ```rust
  struct AlwaysEqual;
  fn main(){
      let sub = AlwaysEqual;
  }
  ```

- **结构体数据的所有权：**

  注意到我们之前声明结构体字段时用的都是自身拥有所有权的`String`类型而非作为引用的`&str`类型。

  如果你想让结构体存储被其他对象拥有的数据引用，我们就得上**生命周期(life time)**了，否则编译器就会报错：`error[E0106]: missing lifetime specifier`

- **通过可派生的trait增加功能：**

  比如如果我们想要实现结构体的输出，这么写会报错：
  ```rust
  struct Rectangle {
      width: u32,
      height: u32,
  }
  
  fn main() {
      let rect1 = Rectangle {
          width: 30,
          height: 50,
      };
  
      println!("rect1 is {}", rect1);
  }
  
  ```

  ```bash
  error[E0277]: `Rectangle` doesn't implement `std::fmt::Display`
  ```

  这是因为`{}`告诉`println!`宏使用`Display`的格式，但是结构体并没有实现`Display`的trait，而编译器提示我们：
  ```bash
  help: the trait `std::fmt::Display` is not implemented for `Rectangle`
    --> src/main.rs:1:1
     |
   1 | struct Rectangle {
     | ^^^^^^^^^^^^^^^^
     = note: in format strings you may be able to use `{:?}` (or {:#?} for pretty-print) instead
  ```

  而当我们加上`{:?}`后又提示我们：
  ```bash
  help: consider annotating `Rectangle` with `#[derive(Debug)]`
     |
   1 + #[derive(Debug)]
   2 | struct Rectangle {
     |
  ```

  额...我们需要给它加上外部属性，让编译器帮我们实现这个trait：
  ```rust
  #[derive(Debug)]
  struct Rectangle {
      width: u32,
      height: u32,
  }
  
  fn main() {
      let rect1 = Rectangle {
          width: 30,
          height: 50,
      };
  
      println!("rect1 is {:?}", rect1);
  }
  ```

  > 这实际上等价于你自己手动实现：
  > ```rust
  > impl std::fmt::Debug for Rectangle {
  >     ...
  > }
  > ```
  >
  > 但是编译器就可以帮我干这件事

  当然用`dbg!`宏也可以，它会输出到`stderr`这个流：

  ```rust
  #[derive(Debug)]
  struct Rectangle {
      width: u32,
      height: u32,
  }
  
  fn main() {
      let scale = 2;
      let rect1 = Rectangle {
          width: dbg!(30 * scale),
          height: 50,
      };
  
      dbg!(&rect1);
  }
  ```

  


#### 方法语法

方法和函数类似，但是注意是**定义在struct / enum / trait上下文的**

比如：

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}
impl Rectangle {
    fn area(&self) -> u32{
        self.width * self.height
    }
}
fn main(){
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };
    println!(
    	"The area: {}",
        rect1.area()
    );
}
```



- 这里`&self`是`self: &Self`的缩写，这里就是为了不获取所有权

  > 但是尽管如此，你其实还是可以move的...此时方法还是可以正常返回的，但是显然你之后就不能调用了
  >
  > ```rust
  > ```
  >
  > 而且你甚至可以把自身返回，比如自己更新自己：
  > ```rust
  > struct User{
  >     name: String,
  > }
  > impl User{
  >     fn rename(mut self, name: &String) -> Self{
  >         self.name = name;
  >         self
  >     }
  > }
  > ```

- 我们可以让方法名称和结构的一个字段相同，这往往用于只返回字段中的值，被称为`getters`，这样的好处就是我们可以把字段变成私有的，但方法是公共的，相当于我们就让对字段的只读访问作为了该类型公共api的一部分

- 我们的`->`运算符到哪里了？不同于C/C++，Rust并没有这种相同的运算符，而是有一个叫作**自动引用和解引用`automatic referencing and dereferencing`**的功能，具体来说，当**我们调用方法`object.something()`的时候，Rust会自动为`object`添加`&`/`&mut`/`*`以便使`object`与方法签名匹配**，也就是说这两者是等价的：
  ```rust
  p1.distance(&p2);
  (&p1).distance(&p2);
  ```

  之所以能这么做：方法有一个明确的接收者，编译器**可以明确地确定方法是 读取(`&self`) / 修改(`&mut self`) / 获取所有权(`self`)**

- **传入别的参数：**

  ```rust
  impl Rectangle {
      fn area(&self) -> u32 {
          self.width * self.height
      }
      fn can_hold(&self, other: Rectangle) -> bool {
          self.width >= other.width && self.height >= other.height
      }
  }
  ```

- **关联函数(associated function)**：所有在`impl`块中定义的函数

  我们可以定义不以`self`为第一参数的关联函数（这自然不是方法了），而**关联函数经常被用于返回一个结构体新实例的构造函数**，比如这样：
  ```rust
  impl Rectangle{
      fn square(size: u32) -> Rectangle {
          Rectangle {
              width: size,
              height: size,
          }
      }
  }
  fn main(){
      let x = Rectangle::square(10);
  }
  ```

  我们使用`::`语法来调用这个关联函数（因为这个方法位于结构体的命名空间中）

- 你可以给一个结构体放多个`impl`块（尽管这没啥意义）



## 5 枚举&模式匹配

### 定义

```rust
enum IpAddrKind {
    V4,
    V6,
}
```

这里的`V4` / `V6`就是枚举的**成员(variants)**

同时**枚举本身的成员也可以关联相应的数据**：
```rust
enum IpAddr {
    V4(String),
    V6(String),
}
let home = IpAddr::V4(String::from("127:0:0:1"));
let loopback = IpAddr::V6(String::from("::1"));
```

> 这是在干嘛？实际上就是一个带标签的盒子，在`match`中会发挥作用

同时**枚举的成员每个可以处理不同类型 / 数量的数据**，比如这样：

```rust
enum IpAddr {
    V4(u8, u8, u8, u8),
    V6(String),
}
let home = IpAddr::V4(127, 0, 0, 1);
let loopback = IpAddr::V6(String::from("::1"));
```

而标准库实际上有这种定义：**（枚举成员可以放入任意类型的数据）**
```rust
struct Ipv4Addr {
    // --snip--
}
struct Ipv6Addr {
    // --snip--
}
enum IpAddr {
    V4(Ipv4Addr),
    V6(Ipv6Addr),
}
```

又一个例子：（`Move`关联了一个匿名结构体）
```rust
enum Message {
    Quit,
    Move { x:i32, y:i32},
    Write(String),
    ChangeColor(i32, i32, i32),
}
```

我们也可以用`imply`来同样声明方法

#### `Option`枚举

> [相关文档](https://rustwiki.org/zh-CN/std/option/enum.Option.html)

它非常有用，因为它**处理了一个经典的问题：一个值要么有值要么没值**，从类型系统的角度来说也就是编译器需要检查是否处理了所有应该处理的情况，这就可以避免了别的语言null带来的bug...

Rust没有空值，而是用了一个编码存在 / 不存在概念的枚举`Option <T>`：
```rust
enum Option<T> {
    None,
    Some(T),
}
```

- 因为它如此有用都被包含在了prelude当中，不需要显式将其引入作用域，它的成员也不需要使用`Option::`前缀来使用`Some` / `None`

- `<T>`是泛型类型参数

- 返回`None`值的时候，它的含义也是空值的含义：没有有效值。

- **优点在于`Option<T>`和`T`不是相同的类型**：

  ```rust
  let x: i8 = 5;
  let y: Option<i8> = Some(5);
  let sum = x + y;
  ```

  编译这段代码就会报错：
  ```rust
  error[E0277]: the trait bound `i8: std::ops::Add<std::option::Option<i8>>` is
  not satisfied
   -->
    |
  5 |     let sum = x + y;
    |                 ^ no implementation for `i8 + std::option::Option<i8>`
    |
  ```

  也就是说我们**在对`Option<T>`进行`T`的运算前必须先把它转换为`T`**。而因此**当我们使用值的时候就必须明确处理值为空的情况**，**只要一个值不是`Option<T>`类型我们就可以安全地认定它的值不为空**



### match

`match`是一个控制流运算符，允许我们将一个值与一系列的模式比较，根据相匹配的模式执行相应的代码。模式可以由字面量 / 变量 / 通配符 / ... 组成。它之所以强大在于它的模式的表现力和编译器检查。它会从上到下匹配，直到找到第一个符合的模式时进入

**注意！传入的时候如果不想要所有权要传入`& `**

比如这个：
```rust
enum Coin{
    Penny,
    Nickel,
    Dime,
    Quarter,
}
fn value_in_cnets(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel=> 5,
        Coin::Dime=>10,
        Coin::Quarter=>25,
    }
}
```

- `模式=>代码/值`

- 你也可以多行加上`{}`：

  ```rust
  fn value_in_cents(coin: Coin) -> u8 {
      match coin {
          Coin::Penny => {
              println!("Lucky penny!");
              1
          }
          // --snip--
      }
  }
  ```

#### 绑定值的模式

```rust
enum UsState {
    Alabama,
    Alaska,
    // --snip--
}
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter(UsState),
}
fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter(UsState) => {
            println!("State: {:?}", state);
            25
        }
    }
}
```



#### 匹配`Option<T>`

比如我们想处理`Option<T>`就可以：
```rust
fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        None => None,
        Some(i) => Some(i+1),
    }
}
let five = Some(5);
let six = plus_one(five);
let none = plus_none(None);
```



#### 匹配必须穷尽

**Rust的匹配是必须穷举的**。像这样的代码是无法编译的：

```rust
    fn plus_one(x: Option<i32>) -> Option<i32> {
        match x {
            Some(i) => Some(i + 1),
        }
    }
```

因为没有处理`None`的情况，而且由于这个bug是rustc知道的，它甚至会告诉你你漏了什么



#### 通配符和`_`占位符

但是很显然我们需要用比如`default`那种，一种方法是用变量：
```rust
    let dice_roll = 9;
    match dice_roll {
        3 => add_fancy_hat(),
        7 => remove_fancy_hat(),
        other => move_player(other),
    }

    fn add_fancy_hat() {}
    fn remove_fancy_hat() {}
    fn move_player(num_spaces: u8) {}
```

而另一方面如果我们不想通过统配模式获取值时，我们就可以使用`_`模式，匹配到任意值而不绑定：
```rust
    let dice_roll = 9;
    match dice_roll {
        3 => add_fancy_hat(),
        7 => remove_fancy_hat(),
        _ => reroll(),
        // 你甚至可以什么也不干：
		// _ => (),
    }

    fn add_fancy_hat() {}
    fn remove_fancy_hat() {}
    fn reroll() {}
```



#### if let

很多时候用`match`也会有点麻烦，因为我们可能指向匹配一种：
```rust
let some_u8_value = Some(0u8);
match some_u8_value {
    Some(3) => println!("three"),
    _ => (),
}
```

我们可以修改为下面的代码：

```rust
if let Some(3) = some_u8_value {
    println!("three");
}
```

同样它也可以有一个`else`：

```rust
let mut count = 0;
if let Coin::Quarter(state) = coin {
    println!("State quarter from {:?}", state);
} else {
    count += 1;
}
```



## 6 package / crate / module / path

**模块系统：**

- packages 包：Cargo的一个功能，允许构建 / 测试 / 分享crate
- `Crates`：模块的树形结构，形成了库 / 二进制项目
- 模块(module)和use：允许控制作用域和路径的私有性
- 路径(path)：一个命名

### 包和crate

- crate是一个二进制项 / 库，它是Rust的一个独立的编译单元，每个crate有自己的命名空间
- crate root是一个源文件，rustc以此为起点构建整个crate的根模块。

- 包是提供一系列功能的一个 / 多个crate，一个包会包含一个Cargo.toml来阐述如何构建这些crate



##### 关于crates:

当我们`cargo new`的时候，会创建一个`Cargo.toml`，里面不会提到`main.rs`，因为它是一个与包同名的二进制crate的根。

如果一个包同时有`src/main.rs`和`src/lib.rs`，那它就有2个crate：一个库和一个二进制项。而且名字都和包相同

如果想要多个二进制项，则需要放到`src/bin/`路径下，此时每个`src/bin`下的文件都会被编译为独立的binary crate（一个独立的编译 /链接目标）



>总体说一下：
>
>一个rust package的结构：[package layout](https://doc.rust-lang.org/cargo/guide/project-layout.html)：
>
>```bash
>.
>├── Cargo.lock
>├── Cargo.toml
>├── src/
>│   ├── lib.rs
>│   ├── main.rs
>│   └── bin/
>│       ├── named-executable.rs
>│       ├── another-executable.rs
>│       └── multi-file-executable/
>│           ├── main.rs
>│           └── some_module.rs
>├── benches/
>│   ├── large-input.rs
>│   └── multi-file-bench/
>│       ├── main.rs
>│       └── bench_module.rs
>├── examples/
>│   ├── simple.rs
>│   └── multi-file-example/
>│       ├── main.rs
>│       └── ex_module.rs
>└── tests/
>    ├── some-integration-tests.rs
>    └── multi-file-test/
>        ├── main.rs
>        └── test_module.rs
>```
>
>- 默认的library是`src/lib.rs`
>
>- 你当然可以自己定义几个模块，比如一个超简单的EMU：
>  ```bash
>  ./
>  ├── Cargo.lock
>  ├── Cargo.toml
>  ├── src
>  │   ├── cpu.rs
>  │   ├── main.rs
>  │   └── memory.rs
>  └── target
>      ├── CACHEDIR.TAG
>      └── debug
>          ├── a_test_of_pkg
>          ├── a_test_of_pkg.d
>          ├── build
>          ├── deps
>          │   ├── a_test_of_pkg-f994eabbc20b8489
>          │   └── a_test_of_pkg-f994eabbc20b8489.d
>          ├── examples
>          └── incremental
>              └── a_test_of_pkg-1pxm03uroh1br
>                  ├── s-hmqmjuk1jz-1m1ybai-6noqamg7z331xebrjxjqn7mrr
>  				...
>                  │   ├── dbneos8siwazh9v0pnskf2r9b.o
>                  │   ├── dep-graph.bin
>                  │   ├── eag998gmibt221pgmq1s74w4d.o
>                  │   ├── query-cache.bin
>                  │   └── work-products.bin
>                  └── s-hmqmjuk1jz-1m1ybai.lock
>  
>  10 directories, 31 files
>  
>  ```
>
>  我们这里在`main.rs`里面就把别的几个`.rs`当作了mod来用：
>
>  ```rust
>  mod cpu;
>  mod memory;
>  
>  use cpu::Cpu;
>  use memory::Memory;
>  
>  fn main() {
>      let mut cpu = Cpu::new();
>      let mut memory = Memory::new();
>  
>      memory.write(0, 42);
>  
>      cpu.step(&mut memory);
>  }
>  ```
>
>- 



### 定义模块来控制作用域与私有性

**模块**：

- 可以让我们将一个crate中的代码进行分组，提高可读性和重用性
- 控制项的**私有性**：public / private
- 用`mod`关键字定义一个模块

比如我们考虑这个例子：
```rust
#![allow(unused)]
fn main() {
mod front_of_house {
    mod hosting {
        fn add_to_waitlist() {}
        fn seat_at_table() {}
    }
    mod serving {
        fn take_order() {}
        fn serve_order() {}
        fn take_payment() {}
    }
}
}
```

> crate
>  └── front_of_house
>      ├── hosting
>      │   ├── add_to_waitlist
>      │   └── seat_at_table
>      └── serving
>          ├── take_order
>          ├── serve_order
>          └── take_payment

### 路径用于引用模块树中的项

我们想要在模块树中找到一个项，同样需要用路径的方式，有两种形式：

- **绝对路径**：从crate根部开始，以crate名 / 字面量`crate`开头
- **相对路径**：从当前模块开始，以`self` / `super`或当前模块的标识符来开头

我们使用`::`作为分割的标识符

```rust
mod front_of_house {
    mod hosting {
        fn add_to_waitlist(){}
    }
}
pub fn eat_at_rest(){
    // 绝对路径
    crate::front_of_house::hosting::add_to_waitlist();
    // 相对路径
    front_of_house::hosting::add_to_waitlist();
}
```

#### 使用`pub`暴露路径

但是上面这段代码是不对的，因为模块`hosting`和函数`add_to_waitlist`都是private的，模块定义了rust的私有性边界。我们**使用`pub`关键字来使子模块的内部部分暴露给上级模块**：

```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist(){}
    }
}
```

- 因为`eat_at_rest`和`front_of_house`定义于同一个模块当中，因此可以相互引用



#### 使用`super`作为`../`

这样我们就可以从父模块里面获取路径了：

```rust
fn serve_order() {}

mod back_of_house {
    fn fix_incorrect_order() {
        cook_order();
        super::serve_order();
    }

    fn cook_order() {}
}
```

#### 公有的结构体 / 枚举

当我们**在结构体的前面加上`pub`**，我们**只是公布了这个结构体，但是内部的字段还是私有的，我们需要确定每一个字段是否公有**：

```rust
mod back_of_house {
    pub struct Breakfast {
        pub toast: String,
        seasonal_fruit: String,
    }

    impl Breakfast {
        pub fn summer(toast: &str) -> Breakfast {
            Breakfast {
                toast: String::from(toast),
                seasonal_fruit: String::from("peaches"),
            }
        }
    }
}
```

> 需要注意... 字段的是否私有是相对于结构体的上层模块外的，`impl`作为方法和它在同一个module里面，因此就是可以完全访问的
>
> **Rust的可见性是以module为边界的（而非class / struct之类的）**

**而枚举只要整体加上`pub`那它的成员也是公有的（显然）**



### 使用use关键字将名称引入作用域

很明显，用一连串的调用路径很麻烦，所以我们直接用`use`把路径一次性引入作用域：
```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

use crate::front_of_house::hosting;

pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
}
```

我们习惯上不会一路指定到最里面的函数或者什么，因为这样可以清晰地表明函数不是在本地定义的同时保证完整路径的重复度最小化

#### 使用`as`提供新名称

```rust
use std::fmt::Result;
use std::io::Result as IoResult;
fn function1() -> Result {
    // --snip--
}

fn function2() -> IoResult<()> {
    // --snip--
}
```

#### 使用pub use重导出名称

`pub use`可以让这个命名空间对上层模块外也适用，相当于**把这个路径暴露给了上层**，这激素**重导出(re-exporting)**



#### 使用外部包

当我们在`Cargo.toml`里面这样写：
```toml
[dependencies]
rand = "0.8.3"
```

我们就可以通过它调用了。

以及`std`标准库对我们的`crate`也是外部的crate，但是因为它和Rust语言一起被分发，我们无须修改Cargo.toml来引入`std`，但是还是要`use`来引入路径的



#### 嵌套路径消除大量use行

```rust
use std::cmp::Ordering;
use std::io;
```

这等价于：
```rust
use std::{cmp::Ordering, io};
```

同时对于这种情况：
```rust
use std::io;
use std::io::Write;
```

这等价于：（我们用self即可）
```rust
use std::io::{self, Write};
```



#### glob运算符将所有公有定义引入作用域

```rust
use std::collections::*;
```

这样所有可以匹配它的公有的都会被引入

它经常被用于测试模块`test`里面



### 将模块分割进不同的文件

我们想把模块移动到单独的文件提高可读性，那么就可以移动到单独的`src`里面的`.rs`文件，**文件名就是mod名。**

比如这样：
```rust
// src/front_of_house.rs
pub mod hosting {
    pub fn add_to_waitlist() {}
}
// src/lib.rs
mod front_of_house;
pub use crate::front_of_house::hosting;
pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
}
```

你甚至可以更进一步，再拆一下：
```rust
// src/front_of_house.rs
pub mod hosting;
// src/front_of_house/hosting.rs
pub fn add_to_waitlist(){}
```





## 7 集合

定义于`std::collections`

Rust的集合可以分为4个类别：

- 序列: [`Vec`](https://rustwiki.org/zh-CN/std/vec/struct.Vec.html)、[`VecDeque`](https://rustwiki.org/zh-CN/std/collections/struct.VecDeque.html)、[`LinkedList`](https://rustwiki.org/zh-CN/std/collections/struct.LinkedList.html)
- Maps: [`HashMap`](https://rustwiki.org/zh-CN/std/collections/hash_map/struct.HashMap.html), [`BTreeMap`](https://rustwiki.org/zh-CN/std/collections/struct.BTreeMap.html)
- 集合: [`HashSet`](https://rustwiki.org/zh-CN/std/collections/hash_set/struct.HashSet.html)、[`BTreeSet`](https://rustwiki.org/zh-CN/std/collections/struct.BTreeSet.html)
- 混杂: [`BinaryHeap`](https://rustwiki.org/zh-CN/std/collections/struct.BinaryHeap.html)



### vector

`Vec<T>`，允许在单独的数据结构里面存储多个值，而所有值在内存里面相邻排列（这也是它的优势），它只能存储相同类型的值

#### 新建

通过`new`方法创建：

```rust
let v: Vec<i32> = Vec::new();
```

而如果你想初始化，更常见的方法是用宏：
```rust
let v = vec![1, 2, 3];
```

> 这里无须指定类型，因为提供的是`i32`可以自动推断

#### 更新

用push方法更新

```rust
let mut v = Vec::new();

v.push(5);
v.push(6);
v.push(7);
v.push(8);
```

#### 丢弃vector时会丢弃所有元素

#### 读取

用`get`方法即可读取：
```rust
let v = vec![1, 2, 3, 4, 5];

let third: &i32 = &v[2];
println!("The third element is {}", third);

match v.get(2) {
    Some(third) => println!("The third element is {}", third),
    None => println!("There is no third element."),
}
```

但是建议还是使用引用，接收一个vec：

```rust
fn largest_i32(list: &[i32]) -> i32 {
    let mut largest = list[0];
    for &item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}
```



#### 遍历

一方面可以通过迭代器，**遍历这个引用**
```rust
let v = vec![1,2,3]
for i in &v{
    println!("{}", i);
}
```

而另一方面通过**可变引用**对每一项的值修改：

```rust
let mut v = vec![1,2,3];
for i in &mut v{
    *i += 50;
}
```

这里很显然我们想要`+=`需要获取`i`的值，所以需要解引用

#### 使用枚举存储多种类型

虽然向量只能存储相同类型，但是我们其实可以使用enum作为一个统一的类型来定义一个vec

```rust
enum SpreadsheetCell{
    Int(i32),
    Float(f32),
    Text(String),
}
let row = vec![
    SpreadsheetCell::Int(3),
    SpreadsheetCell::Float(10.12),
    SpreadsheetCell::Text(String::from("blue")),
]
```



进一步了解详见:[module vec](https://doc.rust-lang.org/stable/std/vec/index.html)





### 字符串

`str`的方法官方手册:[Primitive Type str](https://doc.rust-lang.org/stable/std/primitive.str.html),

`string`官方手册：[module string](https://doc.rust-lang.org/stable/std/string/index.html)



**核心语言中其实只有一种字符串类型：`str`，字符串slice**，而`String`的类型是`std`提供的，它不属于核心语言部分



- 新建：

  - 调用`new`方法

  ```rust
  let mut s = String::new();
  ```

  - 也可以使用`to_string`，它用于任何实现了`Display` trait的类型

  ```rust
  let data = "initial";
  let s = data.to_string();
  let s = "initial".to_string();
  ```

  - 还可以通过`String::from`从字面量 / `&str`创建一个`String`

- 字符串是UTF-8编码的，因此只要符合都是有效的String值

- 更新：

  - `push_str` / `push`：把字符串 / 字符附加到String后面。
    `push_str`用的是`&str`所以没关系：

    ```rust
    let mut s = String::from("foo");
    s.push_str("bar");
    ```

  - 使用`+`运算符 / `fromat!`宏拼接字符串：

    ```rust
    let s1 = String::from("AS");
    let s2 = String::from("PUD");
    let s3 = s1 + &s2;
    ```

    `+`实际上调用了一个函数，它的签名大概是这样：（标准库里面是泛型）

    ```rust
    fn add(self, s: &str) -> String {
    ```

    而因此关键的是我们这里实际上是获取了`s1`的所有权！后面的作为`&str`参数罢了

    而更简单的方式是`format!`：
    ```rust
    let s = format!("{}={}", s1, s2);
    ```

- 索引字符串：

  `String`是不能直接索引的：

  ```rust
  let s = String::from("hello");
  let h = s1[0];
  ```

  这会报错：
  ```bash
  error[E0277]: the trait bound `std::string::String: std::ops::Index<{integer}>` is not satisfied
   -->
    |
  3 |     let h = s1[0];
    |             ^^^^^ the type `std::string::String` cannot be indexed by `{integer}`
    |
    = help: the trait `std::ops::Index<{integer}>` is not implemented for `std::string::String`
  ```

  原因是：

  - 我们的String可能有两种情况：
    ```rust
    let len1 = String::from("Hola").len();
    let len2 = String::from("Здра").len();
    ```

    看起来都是4个字符对吧？但是实际上前者返回4，后者返回8...

    也就是说当我们这样写：
    ```rust
    let hello = "Здравствуйте";
    let answer = &hello[0];
    ```

    返回第一个字符还是返回第一个字节都可能是不对的...因此rustc压根不会编译这样的代码

  - 字符串有3种理解方式：

    1. 字节
    2. 标量值
    3. 字形簇

  - 索引操作本身是机器级别的O(1)的访问，但是`String`压根就不能保证这样的性能，因为它需要从头到索引位置遍历确定多少个有效的字符

- 字符串slice

  使用slice来访问，这时候的语义就是确定的了：
  ```rust
  let hello = "Здравствуйте";
  let s = &hello[0..4];
  ```

  它会返回`Зд`

  而如果你试图访问`&hello[0..1]`，那就会panic了

- 而最好的遍历方法是调用方法：

  - `chars`方法提供的是Unicode标量
  - `byte`方法提供的是按字节的索引



### hash map

`HashMap<K, V>`提供了一个`K`到`V`的映射，通过一个哈希函数来实现。键和值都必须是统一的类型

[hashmap](https://doc.rust-lang.org/stable/std/collections/struct.HashMap.html)

#### 新建

先`new`后`insert`

```rust
use std:collections::HashMap;
let mut scores = HashMap::new();
scores.insert(String::from("Blue"), 10);
scores.insert(String::from("Yellow"), 50);
```

另一个方法是使用元组的`vector`的`collect`方法，使用一个元组的vector的`collect`



#### 访问hash map的值

可以用`get`方法来单独确认一个键对应的值：
```rust
    let team_name = String::from("Blue");
    let score = scores.get(&team_name).copied().unwrap_or(0);
```

它返回的是一个`Option<&V>`的类型，而之后`copied`方法则是得到一个`Option<i32>`，最后通过`unwrap_or`来在如果`scores`没有对应的键时设定为0

我们可以通过键值对作为迭代器访问hash map，就像vec一样：

```rust
for (key, val) in &scores {
    println!("{key}:{val}");
}
```



#### 管理所有权

当我们使用`insert`方法后，显然所有权就被交给这个map了：
```rust
    use std::collections::HashMap;

    let field_name = String::from("Favorite color");
    let field_value = String::from("Blue");

    let mut map = HashMap::new();
    map.insert(field_name, field_value);
    // field_name and field_value are invalid at this point, try using them and
    // see what compiler error you get!
```



#### 更新

显然一个键同时只能存在一个值，新值会覆盖旧值

##### 覆写

```rust
    use std::collections::HashMap;

    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Blue"), 25);

    println!("{scores:?}");
```

返回时就会是`{"Blue": 25}`，后面的覆盖率前面

##### 不存在时创建

我们很多时候希望只有一个新的键是不存在时才创建一个键值对，否则维持原样，我们用`entry`，它返回的是一个枚举

```rust
    use std::collections::HashMap;

    let mut scores = HashMap::new();
    scores.insert(String::from("Blue"), 10);

    scores.entry(String::from("Yellow")).or_insert(50);
    scores.entry(String::from("Blue")).or_insert(50);

    println!("{scores:?}");
```

##### 根据旧值更新

比如当我们想要统计单词出现的次数：
```rust
use std::collections::HashMap;
let text = "hello world wonderful world";
let mut map = HashMap::new();
for word in text.split_whitespace(){
    let count = map.entry(word).or_insert(0);
    *count += 1;
}
println!("{:?}", map);
```







#### hash函数

默认使用的是`SipHash`，它用于抵御DoS攻击。我们也可以用一个别的hasher，它是一个实现了`BuildHasher` trait的类型







> 注意声明周期：
> ```rust
> fn build_scores_table(results: String) -> HashMap<String, Team> {
>     // The name of the team is the key and its associated struct is the value.
>     let mut scores: HashMap<String, Team> = HashMap::new();
> 
>     for r in results.lines() {
>         let v: Vec<&str> = r.split(',').collect();
>         let team_1_name = v[0].to_string();
>         let team_1_score: u8 = v[2].parse().unwrap();
>         let team_2_name = v[1].to_string();
>         let team_2_score: u8 = v[3].parse().unwrap();
>         // TODO: Populate the scores table with details extracted from the
>         // current line. Keep in mind that goals scored by team_1
>         // will be the number of goals conceded from team_2, and similarly
>         // goals scored by team_2 will be the number of goals conceded by
>         // team_1.
>         let t1 = scores.entry(team_1_name).or_insert(Team {goals_scored: 0, goals_conceded: 0});
>         t1.goals_scored += team_1_score;
>         t1.goals_conceded += team_2_score;
>         let t2 = scores.entry(team_2_name).or_insert(Team {goals_scored: 0, goals_conceded: 0});
>         t2.goals_scored += team_2_score;
>         t2.goals_conceded += team_1_score;
>     }
>     scores
> }
> ```
>
> 如果我们混用的话就会同时存在`t1` `t2`两个mutable的引用，这是错误的，必须在使用第二个mutable之前干完前一个的事情
>
> 



## 8 错误处理

Rust要求你承认出错的可能性...分为两个类别：

- **可恢复错误**：代表向用户报告错误和重试操作是合理的情况
- **不可恢复错误**：也就是bug



### `panic!` 不可恢复错误

当出现`panic`时，程序会栈展开 / 终止：

- 默认开始**展开(unwinding)**，也就是它会**回溯栈并清理它遇到的每一个函数的数据**

- 另一个选择是**终止(abort)**，也就是不清理数据**让操作系统代劳**

  如果你想这么做，那就需要在`Cargo.toml`里面的`[profile]`部分增加`panic = 'abort'`，比如想在`release`模式中这么做：
  ```toml
  [profile.release]
  panic = 'abort
  ```

而我们可以这样调用它：
```rust
fn main(){
    panic!("crashed");
}
```

运行就会报错：
```rust
$ cargo run
   Compiling panic v0.1.0 (file:///projects/panic)
    Finished dev [unoptimized + debuginfo] target(s) in 0.25s
     Running `target/debug/panic`
thread 'main' panicked at 'crashed', src/main.rs:2:5
note: Run with `RUST_BACKTRACE=1` for a backtrace.
```



#### 使用panic!的backtrace

具体来说，实际上报错时会很清楚地展示是何错误以及`panic!`真正的地方

我们以缓冲区溢出为例：
```rust
fn main() {
    let v = vec![1, 2, 3];

    v[99];
}
```

他就会报错：
```rust
$ cargo run
   Compiling panic v0.1.0 (file:///projects/panic)
    Finished dev [unoptimized + debuginfo] target(s) in 0.27s
     Running `target/debug/panic`
thread 'main' panicked at 'index out of bounds: the len is 3 but the index is 99', libcore/slice/mod.rs:2448:10
note: Run with `RUST_BACKTRACE=1` for a backtrace.
```

我们可以设置`RUST_BACKTRACE`环境变量来得到一个backtrace，它是执行到目前位置的整个函数调用栈（就和你gdb里面看到的一样），向上是这部分代码调用的代码，向下是调用这部分代码的函数





### Result 可恢复的错误

`Result`是一个枚举，有2个成员：

```rust
enum Result<T,E> {
    Ok(T),
    Err(E),
}
```

- `T`：成功时返回的`Ok`的成员数据类型
- `E`：失败时返回的`Err`的成员数据类型



比如我们要打开一个文件：
```rust
use std::fs::File;
fn main(){
    let f = File::open("hello.txt");
}
```

我们如果用一个错误类型，就可以让编译器告诉我们是什么类型了：
```rust
error[E0308]: mismatched types
 --> src/main.rs:4:18
  |
4 |     let f: u32 = File::open("hello.txt");
  |                  ^^^^^^^^^^^^^^^^^^^^^^^ expected u32, found enum
`std::result::Result`
  |
  = note: expected type `u32`
             found type `std::result::Result<std::fs::File, std::io::Error>`
```

那么由此我们就可以尝试处理了：
```rust
use std::fs::file;
fn main(){
    let f = File::open("hello.txt");
    let f = match f{
        Ok(file) => file,
        Err(error) => {
            panic!("Problem opening the file: {:?}", error);
        },
    }
}
```

#### 匹配不同的错误

```rust
use std::fs::File;
use std::io::ErrorKind;
fn main(){
    let f = File::open("hello.txt");
    let f = match f {
        Ok(file) => file,
        Err(error) => match error.kind(){
            ErrorKind::NotFound => match File::create("hello.txt"){
                Ok(fc) => fc,
                Err(e) => panic!("Problem creating file: {:?}", e);
            },
            other_error => panic!("Problem opening file: {:?}", other_error),
        },
    };
}
```

当然用闭包会更方便

#### 失败时panic简写：unwrap / expect

两个干的事情都是：成功那就正常返回`Ok`的值，失败则调用`panic!`

比如这个：
```rust
use std::fs:File;
fn main(){
    let f = File::open("hello.txt").unwrap();
}
```

这是直接返回默认panic信息

而如果我们想加上自己的说明和参数，就用expect：
```rust
use std::fs::File;

fn main() {
    let f = File::open("hello.txt").expect("Failed to open hello.txt");
}
```



#### 传播错误

我们可以让调用者知道这个错误并决定如何处理，这就是所谓**传播错误**

```rust
use std::io;
use std::io::Read;
use std::fs::File;

fn read_username_from_file() -> Result<String, io::Error> {
    let f = File::open("hello.txt");

    let mut f = match f {
        Ok(file) => file,
        Err(e) => return Err(e),
    };

    let mut s = String::new();

    match f.read_to_string(&mut s) {
        Ok(_) => Ok(s),
        Err(e) => Err(e),
    }
}
```



#### 传播错误用?简写

```rust
use std::io;
use std::io::Read;
use std::fs:File;
fn read_username_from_file() -> Result<String, io::Error> {
    let mut f = File::open("hello.txt")?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s);
}
```

还可以简化！

```rust 
fn read_username_from_file() -> Result<String, io:Error> {
    let mut s = String::new();
    File::open("hello.txt")?.read_to_string(&mut s)?;
    Ok(s)
}
```

但其实只是我们为了展示，正常人都会写：
```rust
fn read_username_from_file() -> Result<String, io::Error> {
    fs::read_to_string("hello.txt")
}
```



#### 在main里面用?

```rust
use std::error::Error;
use std::fs:File;
fn main() -> Result<(), Box<dyn Error>> {
    let f = File::open("hello.txt")?;
    Ok(())
}
```

这里的`Box<dyn Error>`被称为trait object





### 何时用`panic!`

- 示例 / 代码原型 / 测试 都适合用panic
- 当我们确定永远也不会出现`Err`时，用`unwrap`就是可以接受的

指导原则：

- 代码可能以**有害状态**（一些假设 / 保证 / 协议 / 不可变性被打破时）结束时，建议让代码panic
- 有害状态是值一些意外的事情而非预期可能偶尔发生的事情（输入错误格式）
- 此后的代码必须摆脱这种有害状态，而不是每一步都检查







## 9 泛型 / trait / 生命周期

每个编程语言都有高效处理重复概念的工具，而在Rust其一就是**泛型(generics)**。它是具体类型（或其他属性）的抽象，由此我们就可以编写一些无须知道参数为何但是仍能正常工作的函数了



### 泛型

我们可以用泛型为函数签名 / 结构体 / 枚举 / 方法之类的创建定义

#### 函数定义的泛型

> 我们举这个例子：
> ```rust
> fn largest_i32(list: &[i32]) -> i32 {
>     let mut largest = list[0];
> 
>     for &item in list.iter() {
>         if item > largest {
>             largest = item;
>         }
>     }
> 
>     largest
> }
> 
> fn largest_char(list: &[char]) -> char {
>     let mut largest = list[0];
> 
>     for &item in list.iter() {
>         if item > largest {
>             largest = item;
>         }
>     }
> 
>     largest
> }
> ```
>
> 

处理这两种类型，完全可以用同一套代码，那么我们就可以使用泛型了

为了参数化这个新函数的类型，我们需要为类型参数取一个名字，我们惯用的是`T`。
而如果要在函数体中使用参数，就必须在函数签名中声明它的名字，而在函数签名中使用这个类型参数前我们又需要在更之前**声明它的名字**：

```rust 
fn largest<T>(list: &[T]) -> T {
```



那么我们就可以这样写：
```rust
fn largest<T>(list: &[T]) -> T {
    let mut largest = list[0];
    for &item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}
```

但是我们很快就能想到它会报错，因为**我们并没有指定`T`的trait**，换句话说当我们使用`item > largest`时，编译器实际上不知道你这样做是否合法：
```bash
error[E0369]: binary operation `>` cannot be applied to type `T`
 --> src/main.rs:5:12
  |
5 |         if item > largest {
  |            ^^^^^^^^^^^^^^
  |
  = note: an implementation of `std::cmp::PartialOrd` might be missing for `T`
```

>因此可以这么修改：
>```rust
>fn larges<T: PartialOrd>(list: &[T]) -> T {
>```
>
>但是还是会报错，因为问题在于`list[0]`这一句是认为这个T是`Copy`的！但是我们没有说明，只能加上：
>```rust
>fn larges<T: PartialOrd + Copy>(list: &[T]) -> T {
>```
>
>





#### 结构体定义的泛型

```rust
struct Point<T> {
    x: T,
    y: T,
}
fn main() {
    let integer = Point { x: 5, y: 10 };
    let float = Point { x: 1.5, y: 2.5};
}
```

编译器会根据泛型和给的数据推断出T然后生成对应的代码，这样的抽象实际上是零成本的

> 以及我们显然知道这里传入的参数类型不能不一样，因为我们定义里面给的都是`T`，否则就会冲突，除非你这么定义：
> ```rust
> struct Point<T, U> {
>     x: T,
>     y: U,
> }
> ```
>
> 



#### enum定义的泛型

```rust
enum Option<T> {
    Some(T),
    None,
}
```

又比如说：
```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```



#### 方法定义的泛型

```rust
struct Point<T> {
    x: T,
    y: T,
}
impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}
```

当然我们也不必为所有的`T`实现相同的方法，比如我们还是可以为具体的类型去实现对应的方法：
```rust
impl Point<f32> {
    fn distance_from_origin(&self) -> f32 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}
```

当然我们也是可以用不同于方法定义的泛型的：
```rust
struct Point<T, U> {
    x: T,
    y: U,
}

impl<T, U> Point<T, U> {
    fn mixup<V, W>(self, other: Point<V, W>) -> Point<T, W> {
        Point {
            x: self.x,
            y: other.y,
        }
    }
}

fn main() {
    let p1 = Point { x: 5, y: 10.4 };
    let p2 = Point { x: "Hello", y: 'c'};

    let p3 = p1.mixup(p2);

    println!("p3.x = {}, p3.y = {}", p3.x, p3.y);
}

```





#### 泛型代码的性能？

Rust的泛型抽象实际上没有任何的运行时的损耗，这很好理解，因为：

Rust会在编译时对泛型代码进行**单态化(monimorphization)**来保证效率。**单态化是一个通过填充编译时使用的具体类型将通用代码转换为特定代码的过程**

比如当我们写：

```rust
let integer = Some(5);
let float = Some(5.0);
```

编译器就会生成这样单态化版本的代码：
```rust
enum Option_i32 {
    Some(i32),
    None,
}

enum Option_f64 {
    Some(f64),
    None,
}

fn main() {
    let integer = Option_i32::Some(5);
    let float = Option_f64::Some(5.0);
}
```



### trait: 定义共享的行为

trait告诉编译器某个特定类型拥有可能与其他类型共享的功能

- 可以**通过trait以一种抽象的方式定义共享行为**
- 可以**通过trait bounds指定泛型是任何拥有特定行为的类型**



#### 定义trait

一个类型的行为由其可供调用的方法构成，而**trait定义就是一种将方法签名组合起来的方法**，**目的是定义一个实现某些目的必需的行为的集合**

> 比如一个例子：
>
> 我们有两种结构体，`NewsArticle`存放发生于世界各地的新闻故事，而`Tweet`最多只能存放280个字符的内容，我们想要创建爱你一个多媒体聚合库来显示存储在这两个实例中的数据的总结，那就可以这样定义：
> ```rust
> pub trait Summary {
>     fn summarize(&self) -> String;
> }
> ```
>
> 



#### 为类型实现trait

使用`imply ... for ...`来为类型实现具体的trait功能

```rust
pub trait Summary {
    fn summarize(&self) -> String;
}

pub struct NewsArticle {
    pub headline: String,
    pub location: String,
    pub author: String,
    pub content: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

pub struct Tweet {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub retweet: bool,
}

impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}
```

这里因为两个结构体在同一个crate里面定义了，所以没关系。但如果别的想要利用我们的crate的功能为自己的库的作用域实现，那就需要先把这个trait引入作用域，并且确保这个trait是公有的

**只有当trait / 要实现trait的类型 位于crate的本地作用域时，才能为该类型实现该trait**



#### 默认实现

很多时候我们**可以在trait里面先定义好默认的行为**，这样就不必要为每一个类型都去实现了

- 如果我们想要某个**类型使用默认定义的行为**，就可以指定一个空的`impl`块：
  ```rust
  impl Summary for NewsArticle {};
  ```

- 默认实现允许**调用相同trait里面的其他方法**（即使它们没有默认实现）：
  ```rust
  pub trait Summary {
      fn summarize_author(&self) -> String;
      fn summatize(&self) -> String {
          format!("Read more from {}...", self.summarize_author())
      }
  }
  ```





#### trait作为参数

##### imply Trait 语法

明白了这些，我们就可以利用trait来接受多种不同类型的参数了：

```rust
pub fn notify(item: impl Summary) {
    println!("Breaking news! {}", item.summarize());
}
```

这里的含义是：我们的函数接收任何实现了`Summary`这个trait的类型

##### Trait Bound 语法

更适合泛型的语法：（这样我们就不用每个参数都`impl`一遍了）
```rust
pub fn notify<T: Summary>(item :T) {
```

##### 用`+`指定多个Trait：

```rust
pub fn notify<T: Summary + Display>(item: T){
pub fn notify(item: impl Summary + Display) {
```

##### `where`简化trait bound：

```rust
fn some_function<T: Display + Clone, U: Clone + Debug>(t: T, u: U) -> i32 {
```

可以被简化为：
```rust
fn some_function<T, U>(t: T, u: U) -> i32
	where T: Display + Clone
		  U: Clone + Debug
{
```



#### 返回实现了`trait`的类型

我们可以返回一个指定trait的类型，但是**它必须返回某个确定的类型！！**

也就是你可以写：
```rust
fn returns_summarizable() -> impl Summary {
    Tweet {
        username: String::from("horse_ebooks"),
        content: String::from("of course, as you probably already know, people"),
        reply: false,
        retweet: false,
    }
}
```

但是绝对不能写：
```rust
fn returns_summarizable(switch: bool) -> impl Summary {
    if switch {
        NewsArticle {
            headline: String::from("Penguins win the Stanley Cup Championship!"),
            location: String::from("Pittsburgh, PA, USA"),
            author: String::from("Iceburgh"),
            content: String::from("The Pittsburgh Penguins once again are the best
            hockey team in the NHL."),
        }
    } else {
        Tweet {
            username: String::from("horse_ebooks"),
            content: String::from("of course, as you probably already know, people"),
            reply: false,
            retweet: false,
        }
    }
}
```

> 此时就只能用`dye`了



#### 用trait bound有条件地实现方法

我们**通过trait bound作为限制，就可以控制只为那些实现了指定trait的类型实现方法：**

```rust
use std::fmt::Display;
struct Pair<T> {
    x: T,
    y: T,
}
impl<T> Pair<T> {
    fn new(x: T, y:T) -> Self {
        Self {
            x,
            y,
        }
    }
}
impl<T: Display + PartialOrd> Pair<T> {
    fn cmp_display(&self) {
        if self.x >= self.y {
            println!("The largest member is x={}", self.x);
        } else {
            println!("The largest member is y={}", self.y);
        }
    }
}
```

甚至可以进一步，**为满足特定trait bound的类型实现trait**，这被称为**blanket implementations**，比如：
```rust
impl<T: Display> ToString for T{
    
}
```







### 生命周期 & 引用有效性

Rust的每一个引用都有其**生命周期(lifetime)**，就是引用保持有效的作用域



#### Dangling References

生命周期的一个主要目的就是防止dangling references，也就是防止程序引用它本不想引用的数据

> ```rust
> fn main() {
>     let r;
>     {
>         let x = 5;
>         r = &x;
>     }
>     println!("r: {r}");
> }
> ```
>
> 它会报错：
> ```rust
> error[E0597]: `x` does not live long enough
>   --> src/main.rs:7:5
>    |
> 6  |         r = &x;
>    |              - borrow occurs here
> 7  |     }
>    |     ^ `x` dropped here while still borrowed
> ...
> 10 | }
>    | - borrowed value needs to live until here
> ```





#### borrow checker

借用检查器，它比**较作用域来确保所有引用的借用都是有效的**

我们来描述一下刚刚那个例子的生命周期：

```rust
{
    let r;                // ---------+-- 'a
                          //          |
    {                     //          |
        let x = 5;        // -+-- 'b  |
        r = &x;           //  |       |
    }                     // -+       |
                          //          |
    println!("r: {}", r); //          |
}                         // ---------+
```

`'a` / `'b`是生命周期的标注

**rustc比较这两个生命周期的大小，发现它引用了一个生命周期比它小得多的对象，这就会报错。**

因此正确的方法是：
```rust
{
    let x = 5;            // ----------+-- 'b
                          //           |
    let r = &x;           // --+-- 'a  |
                          //   |       |
    println!("r: {}", r); //   |       |
                          // --+       |
}                         // ----------+
```



#### 函数中的泛型生命周期



比如我们想要实现一个函数：

```rust
fn longest(x: &str, y: &str) -> &str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

这会报错：
```bash
error[E0106]: missing lifetime specifier
 --> src/main.rs:1:33
  |
1 | fn longest(x: &str, y: &str) -> &str {
  |                                 ^ expected lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but the
signature does not say whether it is borrowed from `x` or `y`
```

这里的问题是函数压根不知道返回的是谁，换句话说它压根不知道这个返回引用的生命周期....结果就是报错，那么我们就需要告诉编译器



#### 标注生命周期

- 生命周期的**标注本身不改变任何引用的生命周期的长短**
- 标注**描述的是多个引用生命周期相互的关系**
- 本身没有什么意义，只是告诉Rust多个引用的泛型生命周期参数如何相互联系的

```rust
&i32        // 引用
&'a i32     // 带有显式生命周期的引用
&'a mut i32 // 带有显式生命周期的可变引用
```



#### 函数签名中的生命周期标注

我们来看看这个例子：

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str{
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

- 这里的含义就是函数会获取两个参数，它们的生命周期都和`'a`一样长，返回的也是一个生命周期同`'a`一样长的。
- 实际含义：`'a`取的是传入函数的生命周期的交集，也就是**和最快结束生命周期的那个一致**
- 我们实际上并没有改变任何传入值 / 返回值的生命周期，**只是指出任何不满足这个约束条件的值都会被borrow checker拒绝**

> 比如这个例子：
> ```rust
> fn main() {
>     let string1 = String::from("long string is long");
>     let result;
>     {
>         let string2 = String::from("xyz");
>         result = longest(string1.as_str(), string2.as_str());
>     }
>     println!("The longest string is {}", result);
> }
> 
> ```
>
> 由于`string2`的生命周期在离开作用域时就结束了，因此同时`result`的生命周期也就结束了，后续再调用（即使我们觉得好像可以是对的），也会报错：
> ```bash
> error[E0597]: `string2` does not live long enough
> ```



#### 深入理解生命周期

生命周期是用于将函数的多个参数与其返回值相关联的

> 比如这个就是有问题的：
>
> ```rust
> fn longest<'a>(x: &str, y: &str) -> &'a str {
>     let result = String::from("really long string");
>     result.as_str()
> }
> ```
>
> 问题在于`result`在`longest`函数的结尾将离开作用域并被清理，而我们却要返回一个对它的引用，结果就是我们无法指定生命周期而被迫返回一个dangling reference，报错也就不奇怪了



#### 结构体定义的生命周期标注

我们之前只定义过有所有权的类型的结构体，但实际上我们也可以定义包含引用的结构体，不过我们需要为每个引用添加生命周期标注

```rust
struct ImportantExcerpt<'a> {
    part: &'a str,
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.')
        .next()
        .expect("Could not find a '.'");
    let i = ImportantExcerpt { part: first_sentence };
}
```

这里的含义同样，我们的`ImportantExcerpt`不能比它最早结束生命周期的引用成员死的更晚



#### 生命周期省略 Lifetime Elision

虽然我们知道了生命周期，但是有些时候是可以省略的：
```rust
fn main() {
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }

    &s[..]
}
```

为什么可以编译？

因为只有早期版本不允许，但是现在有了**生命周期省略规则**：

- 每一个是引用的参数都有它自己的生命周期参数
- 如果只有一个输入生命周期参数，那么它被赋予所有输出生命周期参数
- 如果方法有多个生命周期参数并且其中一个参数是`&self` / `&mut self`（也就是说是对象的方法），那么所有输出生命周期的参数都会被赋予`self`的生命周期

> 那么据此我们分析一下刚刚的例子：
>
> 首先输入的s有一个生命周期，而只有这一个输入的生命周期参数，那么输出`&str`就会被自动赋予这个生命周期参数
>
> 而先前的：`fn longest(x: &str, y: &str) -> &str {`就自然不对了，因为我们只能先假设每个引用参数都有自己的生命周期，而第2 / 3规则都不适用，换句话说编译器无法计算出返回值的生命周期



#### 方法定义中的生命周期标注

当为带有生命周期的结构体实现方法时，其语法和泛型的语法也是差不多的：

- **需要在`impl`后面声明结构体字段的生命周期**，因为这是结构体类型的一部分

```rust
impl<'a> ImportantExcerpt<'a>{
    fn level(&self) -> i32 {
        3
    }
}
```





#### 静态生命周期`'static`

特殊的生命周期`'static`，

- **这个引用的生命周期可以存活于整个程序**

- 所有字符串字面量都有`'static`的生命周期（这很显然，因为放在`.rodata`段之类的嘛）





## 10 自动化测试



### 如何编写测试

测试函数是用于验证非测试代码是否按照期望的方式运行的，它通常执行以下操作：

1. **设置任何所需的数据 / 状态**
2. **运行待测代码**
3. **断言其结果是我们期望的**

> 比如这个例子：
>
> ```rust
> #[cfg(test)]		// test 模式启用（条件编译）
> mod tests {
>     #[test]
>     fn it_works() {
>         assert_eq!(2 + 2, 4);
>     }
> }
> ```
>
> 没啥好说的

- 你同样可以用`panic!`来主动失败

- `assert!`接收一个Bool类型的输入判断对错
- `assert_eq!` / `assert_neq!`分别测试相等 / 不相等

- 任何`assert!` / `assert_eq!` / `assert_neq!`后的**多余的参数都会传递给`format!`宏**

  > 比如这个：
  > ```rust
  > #[test]
  > fn greeting_contains_name() {
  >     let result = greeting("Carol");
  >     assert!(
  >         result.contains("Carol"),
  >         "Greeting did not contain name, value was `{}`", result
  >     );
  > }
  > ```

#### `should_panic`确定是否能够panic

我们也会想测试是否按期望错误处理，使用`# [should_panic]`就可以证明这一点了

> 比如这个：
> ```rust
> fn main() {}
> pub struct Guess {
>     value: i32,
> }
> 
> impl Guess {
>     pub fn new(value: i32) -> Guess {
>         if value < 1 || value > 100 {
>             panic!("Guess value must be between 1 and 100, got {}.", value);
>         }
> 
>         Guess {
>             value
>         }
>     }
> }
> 
> #[cfg(test)]
> mod tests {
>     use super::*;
> 
>     #[test]
>     #[should_panic]
>     fn greater_than_100() {
>         Guess::new(200);
>     }
> }
> ```
>
> 那么它就能通过测试：
> ```bashs
> running 1 test
> test tests::greater_than_100 ... ok
> 
> test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
> ```

我们甚至可以检查是否是我们想要的panic的原因，可以加上`expect`参数：
```rust
impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 {
            panic!("Guess value must be greater than or equal to 1, got {}.",
                   value);
        } else if value > 100 {
            panic!("Guess value must be less than or equal to 100, got {}.",
                   value);
        }

        Guess {
            value
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "Guess value must be less than or equal to 100")]
    fn greater_than_100() {
        Guess::new(200);
    }
}
```



#### `Result<T, E>`用于测试

除了用`assert`在失败时panic，我们也可以用`Result<T, E>`来进行测试：

```rust
#[cfg(test)]
mod tests {
    #[test]
    fn it_works() -> Result<(), String> {
        if 2 + 2 == 4 {
            Ok(())
        } else {
            Err(String::from("two plus two does not equal four"))
        }
    }
}
```









### 控制测试如何运行

你自然可以通过这些方式来确定参数：
```bash
cargo test --help 
# 或者更详细的
cargo help test
```





#### 并行 / 连续地运行测试

- 运行多个测试时，**Rust默认使用线程来并行运行**。

  也因此，你得**保证各个测试之间不能有依赖关系，以及依赖任何共享的状态**

- 如果**不希望并行 / 想要控制线程数**，可以：
  ```rust
  cargo test -- --test-threads=1
  // 单线程
  ```

#### 显示函数输出

- 默认测试时，只要**测试通过那么其打印到stdout的所有内容都会被截获**（比如`println!`），只有失败的会被打印
- 如果想要查看所有输出，就需要开启`--show-output`参数



#### 指定运行测试

- 运行单个测试，可以直接指定对应的名字

  ```bash
  cargo test <test_func_name>
  ```

- **过滤运行：**

  ```rust
  cargo test add
  ```

  那么所有包含`add`的名字的测试都会被运行

- **忽略测试：**

  如果我们不想要一部分测试运行，可以用`ignore`属性标注：
  ```rust
  #[test]
  fn it_works() {
      assert_eq!(2 + 2, 4);
  }
  
  #[test]
  #[ignore]					// 他不会被运行
  fn expensive_test() {
      // 需要运行一个小时的代码
  }
  ```



### 测试的组织结构

测试分为**单元测试(unit tests) / 集成测试(integration tests)**



#### 单元测试

- 在与其他测试隔离的环境中测试每个单元的代码。
- 单元测试与它们要测试的代码共同存放在`src/`下相同的文件里
- 规范是**在每个文件中创建包含测试函数的`tests`模块**
- 你需要用`#[cfg(test)]`的选项来说明这些代码不应该被包含在编译结果当中

```rust
#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
```



#### 集成测试

- 集成测试对于要测试的库来说完全是外部的，换句话说我们只能调用公有的API
- 为了创建集成测试，我们需要创建一个`test/`目录，与`src/`同级

> 看看`cargo test`的输出：
> ```bash
> running 1 test
> test tests::internal ... ok
> 
> test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
> 
>      Running unittests src/main.rs (target/debug/deps/adder-63975c027cf5c1ef)
> 
> running 0 tests
> 
> test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
> 
>      Running tests/integration_test.rs (target/debug/deps/integration_test-97c9b1c19f8a9817)
> 
> running 1 test
> test it_adds_two ... ok
> 
> test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
> 
>    Doc-tests adder
> 
> running 0 tests
> 
> test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
> ```
>
> 这里有3个部分的输出：
>
> - 单元测试
> - 集成测试
> - 文档测试



#### 集成测试中的子模块



#### 二进制crate的集成测试

**如果项目是binary crate，那么`src/main.rs`及其下面的模块都不会对外暴露接口，如果想要让其他crate使用，我们就必须有一个library crate也就是说`src/lib.rs`。**

> 不过实际上我们可以在Cargo.toml里面指定：
> ```toml
> [lib]
> path = "src/library.rs"
> [[bin]]
> name = "my_app"
> path = "src/app.rs"
> ```
>
> 



编写一个grep！







## 迭代器和闭包

### 闭包：捕获环境的匿名函数

- 闭包是可以保存入变量 / 作为参数传递给其他函数的匿名函数

- 不同于函数，闭包允许捕获调用者作用域的值



> 闭包需要被编译器lowering为一个普通的struct + 普通的函数
>
> 它是对一段可以被调用的计算过程的抽象（而不是一个结果），之所以叫闭包就是因为它把一个函数和它引用的外部环境闭合在一起了

#### 用闭包创建行为的抽象

我们来看一个闭包的示例：

我们想要保存一个计算过程，只有在需要的时候才去调用它。

```rust

fn main() {
use std::thread;
use std::time::Duration;

fn generate_workout(intensity: u32, random_number: u32) {
    let expensive_closure = |num| {
        println!("calculating slowly...");
        thread::sleep(Duration::from_secs(2));
        num
    };

    if intensity < 25 {
        println!(
            "Today, do {} pushups!",
            expensive_closure(intensity)
        );
        println!(
            "Next, do {} situps!",
            expensive_closure(intensity)
        );
    } else {
        if random_number == 3 {
            println!("Take a break today! Remember to stay hydrated!");
        } else {
            println!(
                "Today, run for {} minutes!",
                expensive_closure(intensity)
            );
        }
    }
}
}

```

注意：

- `let`意味着`expensive_closure`是一个匿名函数的**定义**，而不是调用匿名函数的返回值
- `||`指定参数，如果多个参数用`,`分隔
- 此时我们的计算只会在一个地方被调用而且只会在需要结果的时候执行



#### 闭包类型推断和标注

**闭包不要求像`fn`一样在参数和返回值上标注类型**。因为函数需要类型标注是因为需要暴露给用户作为显式接口，而闭包不需要暴露。

虽然你当然可以标注类型：
```rust
fn  add_one_v1   (x: u32) -> u32 { x + 1 }
let add_one_v2 = |x: u32| -> u32 { x + 1 };
let add_one_v3 = |x|             { x + 1 };
let add_one_v4 = |x|               x + 1  ;
```

而且同样**闭包也是会被编译器最终赋予具体的类型的**，所以你不能不使用泛型用不同的类型作为参数调用一个闭包：

> ```rust
> let example_closure = |x| x;
> let s = example_closure(String::from("hello"));
> let n = example_closure(5);
> ```
>
> ```bash
> error[E0308]: mismatched types
>  --> src/main.rs
>   |
>   | let n = example_closure(5);
>   |                         ^ expected struct `std::string::String`, found
>   integer
>   |
>   = note: expected type `std::string::String`
>              found type `{integer}`
> ```


#### 带有泛型和`fn trait`的闭包

我们完全可以用一个惰性求值的方法，也就是说只有需要时才进行求值，这可以通过一个Option<T>实现，但是这个例子其实不是很好：
```rust

fn main() {
struct Cacher<T>
    where T: Fn(u32) -> u32
{
    calculation: T,
    value: Option<u32>,
}

impl<T> Cacher<T>
    where T: Fn(u32) -> u32
{
    fn new(calculation: T) -> Cacher<T> {
        Cacher {
            calculation,
            value: None,
        }
    }

    fn value(&mut self, arg: u32) -> u32 {
        match self.value {
            Some(v) => v,
            None => {
                let v = (self.calculation)(arg);
                self.value = Some(v);
                v
            },
        }
    }
}
}

```

显然我们更合适的方法是用一个hashmap，这会更好地符合惰性求值的功能



#### 闭包捕获环境

闭包可以捕获环境并访问其被定义的作用域内的变量，比如这样：
```rust
fn main(){
    let x = 4;
    let equal_to_x = |z| z==x;
    let y = 4;
    assert!(equal_to_x(y));
}
```

有3中种捕获方式，：

- `FnOnce`：获取所有权，消费捕获到的变量（之后不能再用`println!`之类的了）
    具体来说，就是加上`move`关键字：
    ```rust
    let equal_to_x = move |z| z==x;
    ```
- `FnMut`：获取可变的引用，但是你知道的后面你就不能再试图引用它了
- `Fn`：获取不可变引用

### 用迭代器处理元素序列

- 迭代器负责遍历序列中每一项和决定序列合适结束的逻辑
- 迭代器是惰性的，你不去消费它它什么都不会做
- 所有迭代器都实现了一个叫作`Iterator`的trait：
    ```rust
    pub trait Iterator {
        type Item;
        fn next(&mut self) -> Option<Self::Item>;
    }
    ```
    这里的`next`方法就是实现者被要求定义的唯一方法，它一次返回迭代器的一项，封装在`Some`里面，结束时返回`None`，你当然可以直接调用它

#### 消费迭代器的方法：消费适配器

调用`next`方法的方法就被称为**消费适配器**(consuming adaptors)，就比如`sum`，由于调用它后会获取器迭代器的所有权，所以之后就不能再用了：
```rust
#[test]
fn iterator_sum() {
    let v1 = vec![1, 2, 3];

    let v1_iter = v1.iter();

    let total: i32 = v1_iter.sum();

    assert_eq!(total, 6);
}
```
#### 产生其他迭代器的方法：迭代器适配器

这是另一种的迭代器，它们的作用则是可以将当前的迭代器变成不同类型的迭代器，比如这样：
```rust
let v1: Vec<i32> = vec![1, 2, 3];
v1.iter().map(|x| x + 1);
```
这会产生警告：
```rust
warning: unused `std::iter::Map` which must be used: iterator adaptors are lazy
and do nothing unless consumed
 --> src/main.rs:4:5
  |
4 |     v1.iter().map(|x| x + 1);
  |     ^^^^^^^^^^^^^^^^^^^^^^^^^
  |
  = note: #[warn(unused_must_use)] on by default
```

这里的问题说了：迭代器是lazy的，如果你不消费它它什么都不会做，因此我们必须这样：
```rust
let v1: Vec<i32> = vec![1, 2, 3];
let v2: Vec<_> = v1.iter().map(|x| x + 1).collect();
assert_eq!(v2, vec![2, 3, 4]);
```

然后我们就可以自己创建迭代器了，只需要保证是Option<T>类型的返回：
```rust
struct Counter {
    count: i32,
}
impl Iterator for Counter {
    type Item = u32;
    fn next(&mut self) -> Option<Self::item> {
        self.count += 1;
        if self.count < 6 {
            Some(self.count)
        } else{
            None
        }
    }
}
```

而一旦我们保证了我们实现了`Iterator`trait的话，我们就可以用任何标准库定义的拥有默认实现的`Iterator`方法了


#### 性能

迭代器还是只用循环更快？事实上，用迭代器还可能更快，因为我们的编译器帮我们把事情搞定了，这就是**零成本抽象(zero-cost abstractions)**

```rust
let buffer: &mut [i32];
let coefficients: [i64; i32];
let qlp_shift: i16;

for i in 12..buffer.len() {
    let prediction = coefficients.iter()
                                .zip(&buffer[i - 12..i])
                                .map(|(&c, &s)| c * s as i64)
                                .sum::<i64>() >> qlp_shift;
    let delta = buffer[i];
    buffer[i] = prediction as i32 + delta;
}
```

显然，编译器这里会索性直接循环展开生成汇编




## Cargo & Crates.io





## 智能指针

rust的指针主要是引用

- 而智能指针，表现的类似指针，但是有额外的元数据和功能
- 和普通引用不同，智能指针拥有它指向的数据
    > 实际上，`String` / `Vec<T>`都是智能指针，因为他们拥有一些数据允许修改，也带有元数据和额外功能或保证
- 智能指针通常使用结构体，不过不同于普通结构体在于实现了`Deref` + `Drop`的trait，这允许了它们表现地像引用一样

### 使用Box<T>指向堆上的数据

box允许我们把一个值放在堆上而非栈上，而在栈上的是数据的指针

往往用于以下场景：

- 有一个在编译时未知大小的类型，而又想要在需要确切大小的context里面使用这个类型值时
- 有大量数据并且希望在确保数据不被拷贝的情况下转移所有权时
- 希望拥有一个值并且只关心它的类型是否实现了trait而不关注具体类型时

#### 创建递归类型

rust需要在编译时知道类型占用多少空间，而无法在编译时知道大小的类型是**递归类型(recursive type)**，它的值的一部分可以是相同类型的另一个值，也就是说我们没法清楚这个变量要给它赋予多少的内存，看看这个例子：（这太丑陋了！）
```rust
enum List {
    Cons(i32, List),
    Nil,
}
```
而如果只是这么做一定会报错的：
```rust
use crate::List::{Cons. Nil};
fn main(){
    let list = Cons(1, Cons(2, Cons(3, Nil)));
}
```
```bash
error[E0072]: recursive type `List` has infinite size
```

正因为如此，我们需要使用Box，因为我们放在堆上不就好了，动态内存分配器会帮我们搞定的
于是我们可以这样：
```rust
enum List {
    Cons(i32, Box<List>),
    Nil,
}
use crate::List::{Cons, Nil};
fn main(){
    let list = Cons(1,
        Box::new(Cons(2,
            Box::new(Cons(3,
                Box::new(Nil) ) ) ) ));
}
```

### Deref trait

实现了`Deref`trait允许我们重载解引用运算符`*`，通过这种方法实现`Deref`trait的智能指针就可以被当作常规引用

#### 通过解引用运算符最终指针的值

比如这样：
```rust
let x = 5;
let y = &x;
assert_eq!(5, *y);
```

#### 像引用一样使用`Box<T>`

这就是很简单地使用：
```rust
fn main(){
    let x = 5;
    let y = Box::new(x);

    assert_eq!(5, *y);
}
```
与前者唯一的不同就是`y`被设置为一个指向`x`值的实例，而非指向`x`值的引用

#### 具体来说？

正如我们前面所说的，关键在于`Deref`trait，我们当然也可以自己实现：
```rust
struct MyBox<T>(T);
impl<T> MyBox<T> {
    fn new(x: T) -> MyBox(T) {
        MyBox(x)
    }
}
```
但是编译器此时还无法确认如何解析这个指针，我们不能用`*y`，那么就得实现了：
```rust
use std::ops::Deref;
imply<T> Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &T {
        &self.0             // 访问里面的第0个字段
    }
}
```
也就是说当我们写`*y`时，我们在写的是：`*(y.deref())`，注意到我们不可能直接返回值，那样就会有所有权的问题了

#### 解引用强制转换

解引用强制转换(deref coersions)是Rust在函数/方法传参上的一种便利。
- 它仅适用于实现了Deref trait的类型上
- 将一种类型A隐式转换为另一种类型B，因为A实现了deref trait，并且其关联类型是B，那么就可以这么做：
```rust
#[stable(feature = "rust1", since = "1.0.0")]
impl ops::Deref for String {
    type Target = str;              // 关联类型是str
    #[inline]
    fn deref(&self) -> &str {
        unsafe {str::from_utf8_unchecked(&self.vec)}
    }
}
```
比如当我们写：
```rust
fn hello(name: &str){
    println!("Hello, {}", name);
}
let m = String::from("rsut");
hello(&m);
```
因为标准库实现了`String`的`Deref`实现，返回slice，所以没问题


#### 如何解引用强制转换？

rust会在发现类型和trait满足以下3种情况时进行解引用强制转换：

- `T: Deref<Target=U>`: 从`&T`到`&U`
- `T: DerefMut<Target=U>`: 从`&mut T`到`&mut U`
- `T: Deref<Target=U>`: 从`&mut T`到`&U`
我们注意到，显然是不可能从一个不可变引用转换为`&mut`的


### Drop trait

显然我们使用智能指针后由于在栈分配了空间，所以需要清理使用的内存或资源，当然了，我们可以直接用`Drop` trait，这样离开作用域时就会直接丢掉了

```rust
struct CustomSmartPointer {
    data: String,
}
impl Drop for CustomSmartPointer {
    fn drop(&mut self) {
        println!("Dropping CustomSmartPointer with data `{}`", self.data);
    }
}
fn main(){
    let c = CustomSmartPointer { data: String::from("mystuff")};
    let d = CustomSmartPointer { data: String::from("other stuff")};
}
```
我们看看输出：
```text
CustomSmartPointers created.
Dropping CustomSmartPointer with data `other stuff`!
Dropping CustomSmartPointer with data `my stuff`!
```
显然，这里的顺序正是因为我们需要先把靠里面的新的变量丢掉再丢更老的，这符合直觉

#### 手动提前std::mem:drop

`Drop`trait的存在意义在于它是自动清理的，不过很多时候我们会想手动提前清理掉某个值，但是`drop`本身是不可以直接调用的，比如：

```rust
let c = CustomSmartPointer { data: String::from("some data") };
println!("CustomSmartPointer created.");
c.drop();
println!("CustomSmartPointer dropped before the end of main.");
```
这里就会报错：
```text
error[E0040]: explicit use of destructor method
  --> src/main.rs:14:7
   |
14 |     c.drop();
   |       ^^^^ explicit destructor calls not allowed
```
原因在于`析构(destructor)`函数不允许显式调用

> 它的意思是清理实例的函数，与之相对的是创建实例的构造函数，比如我们常用的`new`

不过我们如果调用`drop(x)`，也就是`std::mem::drop`函数，那就没问题了：
```rust
drop(c);
```

### `Rc<T>`引用计数指针

很多时候问题在于多所有权，我们希望一个值有多个的所有者，也就是说直到没有东西拥有它时它都应该继续存在

而这就需要`Rc<T>`了，**引用计数(reference counting)**，意味着记录一个值的引用数量来确定它是否被使用

#### 使用`Rc<T>`共享数据

我们首先肯定知道，这样的代码是不可能正确的：
```rust

enum List {
    Cons(i32, Box<List>),
    Nil,

}

use crate::List::{Cons, Nil};

fn main() {
    let a = Cons(5,
        Box::new(Cons(10,
            Box::new(Nil))));
    let b = Cons(3, Box::new(a));
    let c = Cons(4, Box::new(a));
}
```
问题就在于它试图让`b` / `c`获取`a`的所有权。我们当然可以使用之前讲的生命周期参数来告知每一个列表的元素至少需要活得和列表本身一样长

而正确的做法是使用`Rc`：
```rust
enum List {
    Cons(i32. Rc<List>),
    Nil,
}
use crate::List::{Cons, Nil};
use std::rc:Rc;
fn main() {
    let a = Rc::new(Cons(5, Rc::new(Cons(10, Rc::new(Nil)))));
    let b = Cons(3, Rc::clone(&a));
    let c = Cons(4, Rc::Clone(&a));
}
```
- `Rc<T>`不在`prelude`当中，所以我们需要先引入作用域
- 当创建`b` / `c`时，我们调用`Rc::clone`传递了`a`的`Rc<List>`引用作为参数
- 我们当然可以调用`a.clone()`了，但是这里`Rc::clone()`的好处是它只会**增加引用计数**而不是深拷贝

#### 克隆`Rc<T>`会增加引用计数

我们可以看看它的引用次数：
```rust
    let a = Rc::new(Cons(5, Rc::new(Cons(10, Rc::new(Nil)))));
    println!("count after creating a = {}", Rc::strong_count(&a));
    let b = Cons(3, Rc::clone(&a));
    println!("count after creating b = {}", Rc::strong_count(&a));
    {
        let c = Cons(4, Rc::clone(&a));
        println!("count after creating c = {}", Rc::strong_count(&a));
    }
    println!("count after c goes out of scope = {}", Rc::strong_count(&a));
```
我们看看输出：
```text
count after creating a = 1
count after creating b = 2
count after creating c = 3
count after c goes out of scope = 2
```

### `RefCell<T>`和内部可变性模式

**内部可变性(Interior Mutability)**允许我们在有不可变引用时也可以修改数据，这需要`unsafe`来模糊规则。

#### 通过RefCell<T>在运行时检查借用规则

不同于`Rc<T>`，`RefCell`代表其数据唯一所有权，而和`Box<T>`不同之处在于，它的借用规则作用于运行时而非编译期！也就是如果违反了，那么程序就会`panic`退出

好处就在于我们允许出现特定内存安全的场景，因为静态分析是不可能面面俱到的，最著名的就是Turing的Halting Problem（你不可能写出一段程序判断一个程序会不会陷入Halting）。

也就是说，**它适用于：Rust不清楚有没有问题，但是你清楚的时候**

选取的理由：

- `Rc<T>`：允许相同数据有多个所有者
- `Box<T>`：允许在编译时执行借用规则的检查







## 并发编程

我们想在一个程序内部有多条逻辑控制流，那么自然就是要用线程了

> 但是需要注意...所谓的线程实际上是可以指代很多个东西的...硬件有自己的线程（就像riscv里面的`hart`），kernel也有线程，还有kernel-level 的线程，还有绿色线程...


而这显然会带来问题，因为程序可以同时进行多个任务，但是我们需要保证执行顺序不能出问题，也就是：

- 竞态
- 死锁
- 别的什么bug

编程语言实际上有很多方法实现线程，比如很多os就提供了创建新线程的api，这种调用系统api的称为1:1（一个OS线程对应一个语言的线程）。
而另一方面，很多语言自身会自己提供特殊的线程实现，也就是所谓green线程，一般来说绿色线程是M:N的，也就是说M个绿色线程对应N个OS线程然后调度
而rust不希望提供一个庞大的运行时，而M:N实际上需要runtime来调度，这对性能不怎么好，毕竟rust是偏底层的语言，因此std只提供了1:1的线程模型实现

- 使用`spawn`创建线程：
    ```rust
    use std::thread;
    use std::time::Duration;
    fn main(){
       thread::spawn(|| {
           for i in 1..10 {
                println!("{} from spawned thread");
                thread::sleep(Duration::from_millis(1));
           }
        }); 
       for i in 1..5 {
           println!("{} from main thread");
           thread::sleep(Duration::from_millis(1));
       }
    }
    ```
- 当主线程结束时，子线程也会结束
    不过就像我们进程可以用`waitpid`一样，这里可以用`join`来搞定：
    ```rust
    use std::thread;
    use std::time::Duration;
    fn main(){
       thread::spawn(|| {
           for i in 1..10 {
                println!("{} from spawned thread");
                thread::sleep(Duration::from_millis(1));
           }
        }); 
       for i in 1..5 {
           println!("{} from main thread");
           thread::sleep(Duration::from_millis(1));
       }
       handle.join().unwrap();
    }
    ```
    此时的主线程就会等待子线程执行完毕，通常调用的`join`会阻塞主线程直到所有子线程执行完毕

- 同样，线程也需要关注所有权，比如这个例子：
    ```rust
    use std::thread;
    fn main(){
        let v = vec![1, 2, 3];
        let handle = thread::spawn(|| {
            println!("Here's a vector: {:?}", v);
        });
        handle.join().unwrap();
    }
    ```
    我们实际上问题在于压根不清楚这个线程何时结束，也就是我们不知道这个引用的生命周期，所以会报错：
    ```bash
    error[E0373]: closure may outlive the current function, but it borrows `v`,
    ```
    而一种方法是我们直接给它所有权，也就是`move`，


### 使用消息传递在线程间传送数据

一个确保安全并发的方式是**消息传递(message passing)**

而Rust中实现消息传递的主要工具是**通道(channel)**，由两部分组成：**发送者(transmitter)** / **接收者(receiver)**，而当发送者/接收者任一方被drop时我们就认为这个通道**关闭**

- rust需要知道我们要发送什么类型：
    ```rust
    use std::sync::mpsc;
    fn main() {
        let (tx, rx) = mpsc::channel()
    }
    ```
    这里`mpsc::channel`就是在创建一个新的通道，它是multiple producer, single consumer的缩写。也就是说允许多个产生值的发送端，但是只能有一个消费这些值的接收端。
    它返回的是一个tuple，第一个元素是发送端，第二个元素是接收端，这样我们就可以用这两个结构体的trait去完成：
    ```rust
    use std::{thread, sync};
    fn main() {
        let (tx, rx) = mpsc::channel();
        thread::spawn(move || {
            let val = String::from("hi");
            tx.send(val).unwrap();
            });
    }
    let received = rx.recv().unwrap();
    println!("Got: {}", received);
    ```
    > 显然一个有趣的现象是我们的channel压根就无所谓有没有线程，因为线程之间不像进程那样存在地址空间的隔离，只是拥有自己的执行上下文罢了
    而这里接收端有2个方法，均通过`Result<T, E>`：
    - `recv`: 接收，阻塞主线程直到接收到一个值
    - `try_recv`: 接收，但是不阻塞，而是立刻返回一个`Result<T, E>`，这里的`Err`代表没有消息，这显然更有用，尤其是当你有别的事情要做时，你可以用一个轮询，只有需要时处理他


#### 通道和所有权转移

当我们通过`send`发送时，这个对象的所有权就被移交给了通道的接收方（当然依旧`Copy`），也就是说之后你不能用它了

#### 发送多个值并观察接收方的等待

```rust
use std::{thread, sync::mpsc, time::Duration};
fn main() {
    let (tx, rx) = mpsc::channel();
    thread::spawn(move || {
        let vals = vec![
            String::from("hi"),
            String::from("hihi"),
            String::from("hihihi"),
        ];
        for val in vals {
            tx.send(vals).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
        });
    for received in rx {
        println!("Got: {}", received);
    }
}
```
这里我们可以直接把`rx`当作一个迭代器，当通道关闭时它也就结束了

#### 克隆来创建多个producer

正如名字所说，我们可以有多个tx，只需要对它们复制一下即可：
```rust
let (tx, rx) = mpsc::channel();

let tx1 = tx.clone();
thread::spawn(move || {
    let vals = vec![
        String::from("hi"),
        String::from("from"),
        String::from("the"),
        String::from("thread"),
    ];

    for val in vals {
        tx1.send(val).unwrap();
        thread::sleep(Duration::from_secs(1));
    }
});

thread::spawn(move || {
    let vals = vec![
        String::from("more"),
        String::from("messages"),
        String::from("for"),
        String::from("you"),
    ];

    for val in vals {
        tx.send(val).unwrap();
        thread::sleep(Duration::from_secs(1));
    }
});

for received in rx {
    println!("Got: {}", received);
}
```

### 共享状态并发

虽然消息传递是很好的并发处理方式，但是显然不是唯一一个，因为通道传递后所有权还是唯一的，我们不允许多个线程同时使用这个变量。而共享内存则类似多所有权：多个线程可以同时访问相同的内存位置。
> 虽然智能指针可以让多所有权变得可能，但是这会额外引入复杂性...

#### mutex互斥

```rust
use std::sync::Mutex;
fn main(){
    let m = Mutex::new(5);
    {
        let mut num = m.lock().unwrap();
        *num = 6;
    }
    println!("m = {:?}", m);
}
```
- `lock`方法获取锁，它会一直阻塞当前线程，直到我们拥有锁为止
    - 失败：如果另一个线程有锁并且它panic了，那么`lock`调用就会失败,,,此时没人可以获取这把锁了，所以这里选择`unwrap`来立刻panic
    - 成功：而一旦获取了锁，就可以把返回值视为一个其内部数据的可变引用了

- 很显然的是，这里的`Mutex<T>`正是一个智能指针，而`lock`返回的是一个叫作`MutexGuard`的智能指针，它实现了`Deref`来指向其内部的数据，也提供了一个`Drop`来当`MutexGuard`立刻作用域时自动释放锁。这就方便得多了！这里正是离开了作用域，所以我们才可以打印这个内容
> 以及要补充一下，我们`println!`哪怕只读也是需要获取锁的！只是我们这里不需要显式声明，因为Debug帮我们做了

#### 线程间共享`Mutex<T>`

我们接下来就可以尝试一下共享了：
```rust
use std::{thread, sync::Mutex};
fn main(){
    let counter = Mutex::new(0);
    let mut handles = vec![];
    for _ in 0..10 {
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
            });
        handles.push(handle);
    }
    for handle in handles {
        handle.join().unwrap();
    }
    println!("Result: {}", *counter.lock().unwrap());
}
```
不出所料，它会报错的，因为我们这里闭包`move`捕获了`counter`，结果就是所有权出现问题了！

#### 试试看`Rc<T>`?

我们上一章用过`Rc<T>`来实现多个所有者，不过很显然我们能猜到它几乎一定是不适用于并发场景的，毕竟它不能保证操作是原子的，也就是说如果两个引用同时修改时几乎一定会出错，因为引用是指向一块内存的...data race自然就来了

不妨看看这个例子：
```rust
use std::{rc::Rc, sync::Mutex, thread};
fn main(){
    let counter = Rc::new(Mutex::new(0));
    let mut handles = vec![];
    for _ in 0..10 {
        let counter = Rc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock.unwrap();
            *num += 1;
            });
        handles.push(handle);
    }
    for handle in handles {
        handle.join().unwrap();
    }
    println!("Result: {}", *counter.lock().unwrap());
}
```
```text
error[E0277]: `Rc<std::sync::Mutex<i32>>` cannot be sent between threads safely
   --> src/main.rs:7:36
    |
  7 |           let handle = thread::spawn(move || {
    |                        ------------- ^------
    |                        |             |
    |  ______________________|_____________within this `{closure@src/main.rs:7:36: 7:43}`
    | |                      |
    | |                      required by a bound introduced by this call
  8 | |             let mut num = counter.lock().unwrap();
  9 | |             *num += 1;
 10 | |             });
    | |_____________^ `Rc<std::sync::Mutex<i32>>` cannot be sent between threads safely
    |
    = help: within `{closure@src/main.rs:7:36: 7:43}`, the trait `Send` is not implemented for
 `Rc<std::sync::Mutex<i32>>`
```
这个闭包有问题，编译器告诉我们问题在于我们没有实现`Send`trait，`Rc<T>`无法被安全地线程间共享

#### 原子引用计数`Arc<T>`

**原子引用计数(atomically reference counted)**，这样的话我们每一个进行的对count的操作都是原子的！

那么重新写一下：
```rust
use std::sync::{Mutex, Arc};
use std::thread;
fn main(){
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let num = counter.lock().unwrap();
            *num += 1;
            });
        handles.push(handle);
    }
    for handle in handles {
        handle.join().unwrap();
    }
    println!("Result: {}", *counter.lock.unwrap());
}
```
那么很自然输出就是`Result: 10`了

但是一个很显然的问题，`Mutex`本身会导致死锁的可能，也就是A拥有a的锁要求b，B拥有b的锁要求a
> 一个经典的死锁的代码：（原谅我糟糕的命名）
> ```rust
> use std::{sync::{Mutex, Arc}, thread, time::Duration};
> fn main(){
>     let mut a = Arc::new(Mutex::new(10));
>     let mut b = Arc::new(Mutex::new(0));
>     let a0 = Arc::clone(&mut a);
>     let b0 = Arc::clone(&mut b);
>     let h1 = thread::spawn(move || {
>         let mut A = a0.lock().unwrap();
>         *A -= 1;
>         thread::sleep(Duration::from_millis(100));
>         let mut B = b0.lock().unwrap();
>         *B += 1;
>         println!("1 finished");
>     });
>     let aa = Arc::clone(&mut a);
>     let bb = Arc::clone(&mut b);
>     let h2 = thread::spawn(move || {
>         let mut B = bb.lock().unwrap();
>         *B += 1;
>         thread::sleep(Duration::from_millis(100));
>         let mut A = aa.lock().unwrap();
>         *A += 1;
>         println!("2 finished");
>     });
>     h1.join().unwrap();
>     h2.join().unwrap();
>     println!("a:{},b:{}", a.lock().unwrap(), b.lock().unwrap());
> }
> ```

### 通过Sync 和Send Trait的可扩展并发
实际上，语言本身对并发知之甚少，而如果你`no_std`的情况下，前面哪些就都不好使了
但是`std::marker`里面的`Sync`和`Send`trait是属于语言本身的

#### Send

- 它表明类型的所有权可以在线程间传递
- 几乎所有Rust类型都是Send的
- 但是`Rc<T>`不是（因为计数会出问题），只能用于单线程

#### Sync

- 表明一个这样的类型可以安全地在多个线程中拥有它的值的引用，换句话说就是，如果∀T有：`&T`是`Send`的话，那么`T`就是`Sync`的，引用可以安全地交给另一线程
- 同样`Rc<T>`也不`Sync`，`RefCell<T>` / `Cell<T>`也是

#### Send / Sync手动实现是不安全的

你几乎不需要这么做，因为由这样的类型组成的类型本身就会满足`Send` / `Sync`，但是你还是需要小心



## Rust OOP

Rust本身就是各种各样编程范式的大杂烩。我想关于OOP本身应该无须赘述了：

- 对象：数据+方法。Rust这个层面上可以是
- 封装encapsulation：提供公有的API。`pub`就是，Rust也满足
- 继承：这个就不太一样了，继承本身的好处是我们可以复用代码，另一方面也是多态性。但是它的缺点还是有些明显的，子类不应该总是共享父类的所有特征，这会让程序不灵活而且有冗余的方法调用，甚至出现不适用的错误。Rust选择把数据和方法解耦，也就是所谓的trait

### trait

#### trait定义

我们定义的trait，实际上就是对相关方法的抽象

比如：
```rust
pub trait Draw {
    fn draw(&self);
}
```
#### trait object

- 但是关键是，我们怎么说明一个`“实现了xxtrait的对象”`？此时就需要一个trait object了，这里用了胖指针`dyn`，我们看看这个例子：
    ```rust
    pub struct Screen {
        pub components: Vec<Box<dyn Draw>>,
    }
    ```
    这里的`dyn Draw`含义就是一个不确定类型，但是保证实现了`Draw`trait的东西。
    而由于`dyn`本身是一个可变长度的（你也不知道给的是什么），所以我们必须装到`Box<T>`里面来保证它是定长的，数据就放到栈上了

#### trait object执行动态分发

回忆我们之前讲泛型的那部分，我们讲到，编译器会对泛型进行单态化，实际上我们也可以用<T: Draw>来达到类似的效果，而编译器进行的就是静态分发，在编译期就会实现单独的方法

而当我们用`dyn`的时候就不一样了，关键在于，总有类型可能会在运行时被决定，这就是`dyn`的作用，编译器也不知道会是什么类型，所以会

#### Trait object要求对象安全

只有object safe 的trait才可以组成一个trait object：

- 返回值不为`Self`
- 方法没有任何泛型类型 / 参数

像`Clone`就不是对象安全的，因为它返回的是`Self`类型

### 面向对象设计模式的实现

额...我觉得这部分讲得挺烂的


## 模式

### 有哪些？

事实上这些都是模式：

- `match`: 一个必须穷尽的匹配：
    ```rust
    match VAL {
        PATTERN => EXPRESSION,
        PATTERN => EXPRESSION, 
    }
    ```
    当然你可以用`_`来表示我接收一个别的值但是我不用它
- `if let`: 如果等于则执行对应的内容并返回，否则返回`()`
    ```rust
    if let PATTERN = VAL {
        EXPRESSION
    }
    ```
    - 它允许引入一个覆盖变量
    - 但是它不要求穷尽

    比如这个例子：
    ```rust
    let favorite_color: Option<&str> = None;
    let is_tuesday = false;
    let age: Result<u8, _> = "34".parse();
    
    if let Some(color) = favorite_color {
        println!("Using your favorite color, {}, as the background", color);
    } else if is_tuesday {
        println!("Tuesday is green day!");
    } else if let Ok(age) = age {
        if age > 30 {
            println!("Using purple as the background color");
        } else {
            println!("Using orange as the background color");
        }
    } else {
        println!("Using blue as the background color");
    }
    ```
- `while let`：条件循环
    ```rust
    let mut stack = Vec::new();
    stack.push(1);
    stack.push(2);
    stack.push(3);
    while let Some(top) = stack.pop() {
        println!("{}", top);
    }
    ```
- `for`: 也是如此！实际上我们就是`for PATTERN in VAL`，同样是模式匹配然后从里面拿出来
- `let`：它也是！实际上`let PATTERN = EXPRESSION`
    比如这个例子：
    ```rust
    let (x,y,z) = (1,2,3);
    ```
    这就是把x/y/z分别赋值给了对应的匹配，如果你改成这样就会报错：
    ```rust
    let (x,y) = (1,2,3);
    ```
- 函数参数：这也是！
    ```rust
    fn print_coordinate(&(x, y): &(i32, i32)) {
    ```

### Refutability(可反驳性)：模式是否会匹配失效

模式有2种：

- 可反驳：也就是对某些可能的值会匹配失败的模式，`if let Some(x) = val`这种
- 不可反驳：任何可能的值都可以匹配，比如`let x = 5;`，`x`可以匹配任何值所以不可能失败
- 显然函数参数 / `let` / `for`只能接收不可反驳的模式
- `if let` / `while let`只能接收可反驳的模式（因为他们本身就是处理可能的失败的）
- `match`必须前面使用可反驳模式，只有最后一个需要使用能匹配任何剩余值的不可反驳模式

一个典型的例子：
```rust
let Some(x) = in_val;
```
这不能编译，因为你没有cover掉`None`的可能

### 语法

#### 匹配命名变量

除了字面量，命名变量也可以作为匹配的：
```rust
fn main() {
    let x = Some(5);
    let y = 10;

    match x {
        Some(50) => println!("Got 50"),
        Some(y) => println!("Matched, y = {:?}", y),
        _ => println!("Default case, x = {:?}", x),
    }
}
```

#### 多个模式

你可以用`|`：
```rust
match x {
    1 | 2 => println!("one or two"),
    3 => println!("three"),
    _ => println!("anything"),
}
```

#### 通过`..=`匹配范围：

```rust
match x {
    1..=5 => println!("1-5");
    _ => println!("unmatched")
}
```

#### 解构并分解值：

##### 解构结构体

```rust
struct Point {
    x: i32,
    y: i32,
}
fn main() {
    let p = Point { x: 0, y: 7};
    let Point {x: a, y: b} = p;
    println!("a:{}, b:{}", a, b);
}
```
甚至你可以只看一部分：
```rust
    match p {
        Point { x, y: 0 } => println!("On the x axis at {}", x),
        Point { x: 0, y } => println!("On the y axis at {}", y),
        Point { x, y } => println!("On neither axis: ({}, {})", x, y),
    }
```

##### 解构enum

这个就更直接了，我们最常用的，之前写过的：
```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

fn main() {
    let msg = Message::ChangeColor(0, 160, 255);

    match msg {
        Message::Quit => {
            println!("The Quit variant has no data to destructure.")
        }
        Message::Move { x, y } => {
            println!(
                "Move in the x direction {} and in the y direction {}",
                x,
                y
            );
        }
        Message::Write(text) => println!("Text message: {}", text),
        Message::ChangeColor(r, g, b) => {
            println!(
                "Change the color to red {}, green {}, and blue {}",
                r,
                g,
                b
            )
        }
    }
}
```
你甚至可以相互嵌套地处理

##### 解构结构体 和元组：

```rust
let ((feet, inches), Point {x, y}) = ((3, 10), Point{ x: 3, y: -10});
```

#### 忽略模式的值

##### `_`忽略整个值
无需赘述
##### `_`忽略一部分

```rust
match (setting_value, new_setting_value) {
    (Some(_), Some(_)) => {
        println!("Can't overwrite an existing customized value");
    }
    _ => {
        setting_value = new_setting_value;
    }
}
```

##### 忽略未使用变量
前面加个下划线

##### 忽略剩余值

```rust
struct Point {
    x: i32,
    y: i32,
    z: i32,
}

let origin = Point { x: 0, y: 0, z: 0 };

match origin {
    Point { x, .. } => println!("x is {}", x),
}
```


#### Match guard

也就是`match`之后再加一个额外的条件判断：
```rust
    let x = Some(5);
    let y = 10;

    match x {
        Some(50) => println!("Got 50"),
        Some(n) if n == y => println!("Matched, n = {}", n),
        _ => println!("Default case, x = {:?}", x),
    }

```

#### `@`绑定

允许我们创建一个值的同时测试它是否匹配模式：
```rust
enum Message {
    Hello { id: i32 },
}

let msg = Message::Hello { id: 5 };

match msg {
    Message::Hello { id: id_variable @ 3..=7 } => {
        println!("Found an id in range: {}", id_variable)
    },
    Message::Hello { id: 10..=12 } => {
        println!("Found an id in another range")
    },
    Message::Hello { id } => {
        println!("Found some other id: {}", id)
    },
}
```



## 高级特征

### unsafe

我们`unsafe`就可以允许我们进行一些不安全的操作：

- 解引用裸指针
- 调用不安全的函数 / 方法
- 访问 / 修改可变静态变量
- 实现不安全trait
- 访问`union`的字段

#### 解引用裸指针

一个裸指针写作：`*const T`（不可变）/ `*mut T`（可变）

和智能指针的区别：

- 允许忽略借用规则，和C一样
- 不保证指向有效内存
- 可以为空指针
- 不能实现任何自动清理功能

它的创建是不需要`unsafe`的，但是解引用必须放在`unsafe`里面：
```rust
let mut num = 5;
let r1 = &num as *const i32;
let r2 = &mut num as *mut i32;
unsafe {
    println!("r1 = {}", *r1);
    println!("r2 = {}", *r2);
}
```
这里用`as`将引用强制转换为对应的裸指针类型

#### 调用不安全的函数或方法

不安全函数 / 方法：用`unsafe`开头的，调用它们也要在`unsafe`里面：
```rust
unsafe fn dangerous() {}
unsafe {
    dangerous();
}
```

##### 创建不安全代码的安全抽象

实际上哪怕是安全函数，内部也允许有不安全的代码，比如标准库的`split_at_mut`：
```rust
use std::slice;

fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();

    assert!(mid <= len);

    unsafe {
        (slice::from_raw_parts_mut(ptr, mid),
         slice::from_raw_parts_mut(ptr.add(mid), len - mid))
    }
}

```

##### 使用extern函数调用外部代码

```rust
extern "C" {
    fn abs(input: i32) -> i32;
}
fn main() {
    unsafe {
        println!("C:{}", abs(-3));
    }
}
```
这里就是使用了C定义的ABI，当然这自己肯定无法工作，我们需要链接对应C的目标文件，比如你自己告诉`rustc`有这个`.o`文件，不过更合适的方法是在`build.rs`里面声明，也就是先：
```toml
[package]
build = "build.rs"
```
然后详见[Build Scripts](https://doc.rust-lang.org/cargo/reference/build-scripts.html?utm_source=chatgpt.com)

##### 让其他语言调用Rust函数

依旧extern，不过还需要增加`#[no_mangle]`告诉rustc不要mangle次函数名称（也就是编译时给名字加入额外信息），我们这样声明：
```rust
#[no_mangle]
pub extern "C" fn call_from_c() {
    println!("Just called Rust function from C");
}
```

#### 访问 / 修改可变静态变量

也就是所谓全局变量，声明它本身不会有不安全的，只要是只读的：
```rust
static HELLO_WORLD: &str = "Hello, world!";

fn main() {
    println!("name is: {}", HELLO_WORLD);
}
```
但如果我们声明的是一个`mut`的全局变量，无论读写都是不安全的：
```rust
static mut COUNTER: u32 = 0;

fn add_to_count(inc: u32) {
    unsafe {
        COUNTER += inc;
    }
}

fn main() {
    add_to_count(3);

    unsafe {
        println!("COUNTER: {}", COUNTER);
    }
}
```

#### 实现不安全trait

如果trait中至少有一个方法中包含编译器无法验证的不变式时，trait就是不安全的，在它前面加上`unsafe`，并且实现时也需要加上：
```rust
unsafe trait Foo{
}
unsafe impl Foo for i32{

}
```

#### 访问联合体中的字段

没啥好说的



### 高级trait

#### 关联类型





## 一个简单的web服务器

我们看看发送的请求：
```text
Request: GET / HTTP/1.1
Host: localhost:7878
Connection: keep-alive
sec-ch-ua: "Chromium";v="154", "Google Chrome";v="154", "Not A(Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Linux"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.
0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng
,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br, zstd
Accept-Language: zh-CN,zh;q=0.9
```
嗯，格式是：
```text
Method / HTTP-Version CRLF(也就是回车/换行符)
headers CRLF
message-body
```
而一个响应的格式是：
```rust
HTTP-Version Status-Code Reason-Phrase(描述状态码) CRLF
headers CRLF
message-body
```

算了反正书上都有


## 9.28 rust并发编程

单核执行多线程，也就是需要不同控制流之间做上下文切换，而问题在于数据...很明显我们如果操作非原子 / 数据没有加锁，那么就会出现竞态：

> 考虑两个线程：
> ```rust
> // A						//B
> load cnt					load cnt
> add 1						add 1
> store cnt					store cnt
> ```
>
> 一旦A load后立刻恰好B也加载，两个都分别在自己的上下文状态里面读取了这个值，结果就是写回的时候只会+1...
>
> 这是UB未定义行为...

那一个很自然的想法就是我们想让这个操作作为一个整体不被打断，

**不变量**是程序约定要守住的正确性条件

多核则会带来**缓存一致性**的问题，最基础的缓存一致性思想有两种：

1. Write-invalidate：写入数据的时候，将其他 Cache 中这条 Cache Line 设为 Invalid
2. Write-update：写入数据的时候，把新的结果写入到有这条 Cache Line 的其他 Cache

要知道源码顺序可不能单独证明跨线程可见的顺序

那么我们第一种方法：原子变量：
```rust
use std::sync::atomic::{AtomicUsize, Ordering::Relaxed};
use std::thread;
fn main(){
    let x = AtomicUsize::new(0);
    let y = AtomicUsize::new(0);
    let (r0, r1) = 
}
```

这可能有4种情况：

- $(0,1)$
- $(1,0)$
- $(1,1)$
- $(0,0)$ ：这也是可能的...因为多核的情况下，可能还没来得及同步，两个线程之间看不到对方的操作
> 为什么有可能？按理来说，从缓存一致性的角度来说，似乎这不太可能，毕竟写入时另一个hart的cache line应该被标记无效？
> 因为处理器的`store`并不会立即执行...实际上并不是处理器执行完立刻就放入缓存，因为慢死了，而且现代处理器实际上都是ROB决定何时要retire的，而即使retire也只是说明这条指令产生的作用不可撤销了，实际上往往会先写入一个store buffer，

Rust用类型约束跨线程访问，再用同步机制协调运行时的修改：

| 约束 | 可以做什么                 | 例子            |
| ---- | -------------------------- | --------------- |
| Send | 把值安全的move给另一个线程给所有权 | String移交      |
| Sync | 把共享引用&T交给其他线程   | 共享AtomicUsize |

- `Mutex<T>`：用锁限制同一时刻的访问（但是问题在于这会变慢...）；

  `RwLock<T>`：读写锁，允许多个读者或一个写者（就像我们`mut`同时只能存在一个一样）

- `Arc<T>`：让多个线程共同拥有同一份T，但是不允许同时修改



原子操作：

- load / store：各自原子地读取 / 写入
- swap：写入新值返回旧值
- fetch_add：原子递增并返回旧值(+=读加写放到一起)
- CAS(Compare-and-Swap，比较并交换)：当前值符合预期才尝试更新

原子是处理器层面实现的（虽然超标量乱序的情况下的确会被拆分为uop，不过对外的观察顺序是按照）

内存序：

| Ordering | 保证 | 常见用途 |
| -------- | ---- | -------- |
| Relaxed  |      |          |
| Release  |      |          |
| Acquire  |      |          |
| AcqRel   |      |          |
| SeqCst   |      |          |

可以用`Release`和`Acquire`一对来实现消息传递


不过很显然，我们这里不需要太过关注硬件的方面


## 并发进阶

### 引入
首先我们需要认识到一个误区：**并发编程里面你认为成立的未必成立。**

比如关于编译器的优化，我们看这个例子:
```rust
use std::sync::{mpsc, Arc};
use std::time::Duration;

/// 一个普通的内存位置, 没有任何同步语义.
struct Flag(bool);

fn main() {
    let flag = Arc::new(Flag(true));
    let (tx, rx) = mpsc::channel();

    // 工作线程: 等标志被翻转
    let reader = Arc::clone(&flag);
    std::thread::spawn(move || {
        let mut reloads = 0u64;
        // 注意: 这是普通读
        while reader.0 {
            reloads += 1;
        }
        tx.send(reloads).unwrap();
    });

    // 主线程: 等一会, 然后翻转标志
        std::thread::sleep(Duration::from_millis(200));

    let p = Arc::as_ptr(&flag) as *mut Flag;
    // WARN: 故意制造数据竞争, 用来演示后果
    unsafe {
        (*p).0 = false;
    }

    match rx.recv_timeout(Duration::from_secs(2)) {
        Ok(n) => println!("reader 看到了标志变化, 重读了 {n} 次"),
        Err(_) => println!("等了 2 秒, reader 始终没有看到标志变化"),
    }
}
```
这里，当我们用release 和 debug模式分别运行时，会产生不同的现象：
```bash
> cargo run -q
reader 看到了标志变化, 重读了 130978961 次

> cargo run -q --release
等了 2 秒, reader 始终没有看到标志变化
```
为什么会这样？问题就在于这个`unsafe`：

- 首先，这里子线程里面的reloads是一个mut引用，那么从safe rust的角度有充足的理由认为这里生命周期结束前会被修改，那么编译器在release模式就会优化为:
```rust
let v = reader.0;
if (v) {
    loop {
        reloads += 1;
    }
}
```
- 而糟糕的事，我们偏偏在主线程里面`unsafe`解引用裸指针修改了这里的字段，实际上编译器认为的`loop`并不成立！

### Send / Sync

我们看看std::sync::mpsc 的`Sender`，关注这2个trait：

- Send: 把值安全地移交给另一个线程
- Sync: 把共享引用`&T`交给别的线程
- 如果一个类型的所有字段都是`Send`，那它就是`Send`的

而显然`Rc<T>`是不能`Send`/`Sync`的，但是它本身的字段显然只包含了一个指针和计数，所以我们std的源码里面就声明：
```rust
#[stable(feature = "rust1", since = "1.0.0")]
impl<T: ?Sized, A: Allocator> !Send for Rc<T, A> {}
impl<T: ?Sized, A: Allocator> !Sync for Rc<T, A> {}
```
当然你甚至也可以自己反过来承诺：
```rust
unsafe impl Send for MyType {}
```


### 内存序 Memory Ordering
> rust的内存序是和C++20的一致的

所谓内存序，就是规定一个线程的内存操作顺序应该在外界如何被观察

> 当然，所谓内存序自然是给编译器看的，处理器才不知道也不关心呢，具体来说就是让编译器清楚指令的顺序的约束，以及加上比如`fence`的指令来引入顺序的约束

我们知道，现代的处理器是乱序执行的，再加上多核，很可能出现需要另一个线程同时在观察这个线程的时候,而编译器也可能会打乱顺序（如果没有可观察副作用编译器就可以随便打乱顺序甚至整个优化），此时我们就需要对外保证这个内存的顺序

五种内存序从轻到重：

- `Relaxed`: 只需要原子性，没有同步语义，也就是保证这个操作是原子的
- `Release`: 发布之前的操作。这条之前的所有内存操作不会排到这个之后
- `Acquire`: 获取之前发布的信息。这条之后的所有内存操作不会排到这个之前
> 关于`Release`和`Acquire`: 具体来说，`Release`保证的是在这条之前的所有内存的操作对于另一个接收到这个的`Acquire`完全可见（也就是约束了内存操作的顺序），而建立关系的前提就是有相关的访存行为，具体来说，就是如果一个`Acquire`的`load`的是这个`Release`的`store`的值，那么它就接收到对方`Release`之前的所有操作
> 当然这种解释很容易混淆... 事实上我们不需要真的有一个匹配的读写，仅仅满足那两条就行了，而这两条都可以通过fence实现
- `AcqRel`: 同时具有`Acquire`/`Release`的语义，既发布前面的所有内存操作，也保证后续的所有操作都不可先于这条指令
> 主要适用于读改写？
- `SeqCst`: 我全都要！不仅仅是`Acquire`+`Release`，还要求所有`SeqCst`原子操作共同遵循顺序
> 这很显然，问题在于如果有多个`SeqCst`，会发生什么呢？我们看看这个例子：
> ```rust
> use std::sync::atomic::{AtomicBool, Ordering};
> static X: AtomicBool = AtomicBool::new(false);
> static Y: AtomicBool = AtomicBool::new(false);
> ```
> 
> 线程A:
> ```rust
> X.store(true, Ordering::SeqCst);
> let r1 = Y.load(Ordering::SeqCst);
> ```
> 线程B:
> ```rust
> Y.store(true, Ordering::SeqCst);
> let r2 = X.load(Ordering::SeqCst);
> ```
> 而这里有1种是不可能允许的结果，就是`r1=false && r2=false`，原因在于这个顺序会形成一个循环：
> X.store < Y.load < Y.store < X.load < X.store
> 这是不能允许的


### 跨变量




## no_std

### 引入：启动流程

实际上，rust的流程同样逃不开那一套，比如GNU/Linux里面我们写`main`，总是从`__libc_start_main`开始的，而rust虽然函数返回的是`()`，但是实际上返回类型的要求是必须实现`Termination`这个`#[lang]`项，包括`()` / `!` / `Exitcode` / `Result<T, E> where E: Debug`。之后`Termination::report()`把返回值折成`Exitcode`：`()` / `Exitcode::SUCCESS`返回0，`Exitcode::FAILURE` / `Err(_)`返回1（后者会打印`Error: {err:?}`，因此必须满足`Debug`trait才能输出），`panic!`返回101（这是std的运行时规范）
> 详见：[trait:Termination](https://doc.rust-lang.org/std/process/trait.Termination.html)

为什么要这样封装？

- `panic`的捕获：我们不可能让内核崩溃，需要把`main`的`panic`转换为退出码`101`
- 线程`guard`+溢出检测：std运行时在启动时会注册好信号的handler并记录线程栈预期的guard区间，这样溢出就可以被诊断而不是一个信号


### 标准库

包含关系：

- `core`：
    - 最底层的语言基础设施
    - 提供`Option`/`Result`/`str`/`slice`/`[T;N]`(用于初始化数组)之类的
- `alloc`: 
    - 依赖`core`
    - 不需要os支持但是需要一个heap来分配
    - 提供`vec`/`string`/`box`/`rc`/`arc`/`format!`/`vec!`等这些需要堆的类型
- `std`:
    - 依赖前两者
    - 需要os
    - 提供文件 / 网络 / 进程 / 线程 / 时间 / env / panic hook / 栈展开等


而如果你想找关于无须std的内容，那么就在`--std`里面的`core`部分，官方的介绍：

> The Rust Core Library is the dependency-free[1](#fn1) foundation of [The Rust Standard Library](../std/index.html). It is the portable glue between the language and its libraries, defining the intrinsic and primitive building blocks of all Rust code. It links to no upstream libraries, no system libraries, and no libc.

为什么需要`no_std`？标准库本身就是OS提供的抽象，我们写内核写的就是这部分东西
core永远都在extern prelude 里面，我们看看预处理的结果就知道了

对于`core`，这些仍然可用：
```rust
Option / Result / Iterator / FromIterator
panic! / assert! / debug_assert!
core::fmt（Display / Debug / write!）
slice / str / 数组 / 元组
core::mem / core::ptr / core::cell / core::sync::atomic
core::hint::spin_loop
```

#### 基本的队列
那首先，我们没有vec之类的了，所有这种都必须在编译期确定，那么我们只能把大小写进类型里面了：
```rust
use core::mem::MaybeUninit;      // 一个union表示这个内存现在可能还没有初始化
use core::ptr;

pub struct HistoryBuffer<T, const n: usize> {
    buf: [MaybeUninit<T>; n],
    head: usize,
    tail: usize,
    len: usize,
}
```
这样这部分就不需要放到堆上，可以作为全局或者放到栈里面

> 做个区分：`Option<T>`和`MaybeUninit<T>`
>
> 我们如果想分配一个数组，但是没法给出它的初始化内容，Rust不允许你创建一个未初始化的`[T; num]`因为它们必须是有效的`T`
>
> 
>
> |                             | `Option<T>`                   | `MaybeUninit<T>`               |
> | --------------------------- | ----------------------------- | ------------------------------ |
> | 表达的含义                  | 有值或没有值                  | 内存中可能尚未初始化           |
> | 能否安全地表示空槽位        | 可以                          | 可以，但需要自己维护状态       |
> | 是否自动管理内部 `T` 的析构 | 是                            | 否                             |
> | 是否有额外的判别状态        | 语义上有 `Some` / `None` 状态 | 没有内置的初始化标记           |
> | 常见用途                    | 普通业务逻辑、可选值          | 底层容器、数组初始化、内存管理 |
>
> 同时`Option<T>`的大小显然会比我们原始的数据大的，它需要包装，但是`MaybeUninit`不一样，它的对齐和大小和内部的`T`一致


同时，为了在编译期完成初始化，我们的初始化方法也必须被`const`修饰（**这代表这个函数可以在编译期执行，也就是说编译器会调用它并且把结果直接嵌入生成的代码里面**）
```rust
impl<T, const N: usize> HistoryBuffer<T, N> {
    pub const fn new() -> Self {
        Self {
            buf: [const {MaybeUninit::uninit()}; N],
            head: 0,
            tail: 0,
            len: 0,
        }
    }
    pub const fn capacity(&self) -> usize { N }
    pub const fn len(&self) -> usize { self.len }
    pub const fn is_empty(&self) -> bool { self.len == 0 }
    pub const fn is_full(&self) -> bool { self.len == N }
}
```
> 数组的重复初始化语法`[expr; N]`。这里用`const`把`MaybeUninit`包起来，原因在于它只有`T:Copy`时才会`Copy`，这样包起来就相当于每个元素都是独立求值的常量了

之后就可以加入读写方法了：（这里的元素访问必须unsafe使用裸指针，因为`MaybeUninit<T>`不能被直接当作`T`使用）

```rust
impl<T, const N: usize> HistoryBuffer<T, N> {
    /// 我们先给出访问的方法
    /// # Safety
    /// index < N
    #[inline]
    unsafe fn slot(&self, index: usize) -> *const T {
        debug_assert!(index < N);       // 只会在debug优化等级开启，一旦高级的优化就不会执行
        unsafe { self.buf.as_ptr().add(index).cast::<T>() }
    }
    /// #Safety
    unsafe fn slot(&self, index: usize) -> *mut T {
        debug_assert!(index < N);
        unsafe { self.buf.as_mut_ptr().add(index).cast::<T>() }
    }

    /// 接下来就是正式实现访问的方法了
    pub fn push(&mut self, value: T){
        if self.is_full() {         // 满了
            drop(self.pop());       // 把最老的元素丢掉
        }
        // SAFETY: head in [0, N)
        unsafe { ptr::write(self.slot_mut(self.head, value)) };
        self.head = (self.head + 1) % N;
        self.len += 1;
    }
    pub fn pop(&mut self) -> Option<T> {
        if self.is_empty() {
            return None;
        }
        // 为什么这里不需要drop? 因为我们返回了这个值，它的所有权被返回值管理，它自己无须关心了
        let value = unsafe {ptr::read(self.slot(self.tail)) };
        self.tail = (self.tail + 1) % N;
        self.len -= 1;
        Some(value)
    }
    pub fn peek(&self) -> Option<&T> {
        if self.is_empty() {
            return None;
        }
        Some(unsafe { &*self.slot(self.tail) })
    }
    pub fn iter(&self) -> impl Iterator<Item = &T> + '_ {
        (0..self.len).map(move |i| {
            let index = (self.tail + i) % N;
            unsafe { &*self.slot(index) }
        })
    }
}
```
以及别忘了！我们还有`Drop`trait没实现！
> MaybeUninit不会自动析构里面的`T`，rust编译器无法自动析构里面的元素的话自然也就无从管理，换句话说我们必须自己实现Drop之类的
```rust
impl<T, const N: usize> Drop for HistoryBuffer<T, N> {
    fn drop(&mut self) {
        while self.pop().is_some() {}
    }
}
```

然后再补上迭代器的实现：
```rust
impl<'a, T, const N: usize> IntoIterator for &'a HistoryBuffer<T, N> {
    type Item = &'a T;
    type IntoIterator = HistoryIter<'a, T, N>;
    fn into_iter(self) -> Self::IntoIter {
        HistoryIter { buf: self, index: 0 }
    }
}
pub struct HistoryIter<'a, T, const N: usize> {
    buf: &'a HistoryBuffer<T, N>,
    index: usize,
}
impl<'a, T, const N: usize> Iterator for HistoryIter<'a, T, N> {
    type Item = &'a T;
    fn next(&mut self) -> Option<Self::Item> {
        if self.index >= self
    }
}
```



但是这还不够，因为我们还没有准备堆，也就是说我们还需要一个全局分配器，可以见alloc，要实现的就是`GlobalAlloc`

```rust
pub unsafe trait GlobalAlloc {
    unsafe fn alloc
}
```
