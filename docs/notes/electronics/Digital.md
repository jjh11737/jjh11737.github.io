# 数字电路与系统

## 逻辑代数基础

这是学校课程的笔记

基本：

|              |             |
| ------------ | ----------- |
| $A \oplus B$ | $A'B + B'A$ |
| $A\odot B$   | $AB+A'B'$   |

常用的公式：

| num  |                                    |
| ---- | ---------------------------------- |
| 21   | $A+AB=A$                           |
| 22   | $A+A'B=A+B$                        |
| 23   | $AB+AB'=A(B+B')=A$                 |
| 24   | $A(A+B)=A$                         |
| 25   | $AB+A'C+BC=AB+A'C+(A+A')BC=AB+A'C$ |
| 26   |                                    |
|      |                                    |
|      |                                    |
|      |                                    |

代入定理：

对任何一个对$A$成立的逻辑等式，将任意一个逻辑式代入$A$的所有位置，等式仍成立

反演定理：

对一个逻辑式$Y$，如果：

- $\cdot \leftrightarrow$+
- $0 \leftrightarrow 1$
- $A \leftrightarrow A'$（注意我们只对变量取反，表达式的取反我们不干涉）

则原式等于$Y'$

> $Y=((AB'+C)'+D)'+C$，求$Y'$：
>
> 
>
> 



对偶定理：

如果两个逻辑式相等，那么它们的对偶式也相等，即：

- $\cdot \leftrightarrow$+
- $0 \leftrightarrow 1$

则得到的结果是$Y^D$

>如：
>
>$$





从真值表写出表达式：

你可以根据真值表把所有能使输出为1的表达式或到一起，就是我们想要的了

#### 2.5.3 逻辑函数的标准形式

##### 最小项：

所有变量取不取反的乘积，可以编码得到对应的序号记为$m_0-m_{2^N-1}$

性质：

- 每个最小项与变量对应，$A'BC\leftrightarrow 011$
- 任意两个最小项相乘为0（因为至少有一位是不同的）
- 全体最小项和为1
- 相邻性：如果两个最小项只有一个因子不同，那么相加就会消去这个因子

这其实就类似我们投影到一组完备正交基上（定义与为内积的话）

##### 最大项：

包含所有变量取不取反的和，编码得到

性质：

- 对应让这个最大项取0的值：$A'+B+C'\leftrightarrow 101$
- 任意两个最大项和为1
- 所有最大项积为0

关系：$M_i = \bar{m_i}$

##### 最小项之和：

把逻辑表达式用最小项的和来表示，真值表中所有令结果为1的最小项的和

> 比如$Y=ABC'+BC=ABC'+A'BC+ABC=\Sigma m(3,6,7)$

##### 最大项之和：

同上，最大项的积，等于

而且注意，同u一个逻辑式，用最小项和最大项的表示刚好是取反的：
$y=\sum m_i = $

与非与非形式就是最小项和取反2次

或非-或非形式可以先求出取反的最小项之和，然后自然就是对应的形式了





## 门电路

### mos

二极管问题显然很大，因为存在输出电平的偏移

因此我们才引入mos管，这玩意耦合没那么讨厌。

而我们的最基础的应用就是cmos非门了：
![image-20260922101758065](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260922101758065.png)

而对应的电压电流传输特性：
![image-20260922102054735](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260922102054735.png)![image-20260922102110730](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260922102110730.png)

#### 静态特性

##### 输入噪声容限：

换句话说就是我们上级到下一级允许的噪声最大范围：
![image-20260922102224882](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260922102224882.png)
显然这里$VDD$越高我们噪声容限越大：
![image-20260922102556595](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260922102556595.png)

##### 静态输入特性：

处理门电路间以及对外连接的依据，也就是从输入端看进去的特性。

而为了保护电路，我们往往会在输入端加入输入保护电路，如下：
![image-20260922103329631](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260922103329631.png)![image-20260922103340862](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260922103340862.png)
这些都是为了防止静电放电损坏栅极衬底间的绝缘层

静态输出特性：

VDD太高结果就是：

- 低电平：$VDD$越大我们的$V_{OL}$会不断变大，而且越大抬升越慢

  > 这对应我们输出特性曲线的可变电阻区

  ![image-20260922105108208](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260922105108208.png)

- 高电平：
  ![image-20260922105213885](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260922105213885.png)![image-20260922105222272](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260922105222272.png)



##### CMOS的静态I/O特性总结：

- CMOS的栅源极间为绝缘层，输入阻抗高，对微弱信号捕捉能力强

- **输入端不允许悬空**

  > 悬空时很容易被外界噪声干扰，输入电平不定，而且最重要的是很容易因为静电造成栅极感应经典而击穿

- 与门 / 与非门的多于输入端接入高电平

  或门 / 或非门多于输入接低电平

  当然更简单的方法是与使用端并联

#### 动态特性

##### 传输延迟事件(propagation delay time)

电平翻转需要时间，所以会存在一定的延迟：

- $C_I/ C_L$充放电，因为$R_{ON}$较大所以$C_l$充放电影响也较大
- 

> 也正因为如此芯片的主频取决于关键路径，所以我们要引入流水线来缩短一个时钟周期走的最长的关键路径

##### 交流噪声容限



##### 动态功耗

静态功耗是输出状态不变时的功耗，主要来源是输入保护二极管和寄生二极管

动态功耗则来源于输出状态切换时的功耗：

- 负载电容充放电功耗：
  $$
  P_C=C_LfV_{DD}^2
  $$

- 瞬时导通功耗：
  $$
  P_T=C_{PD}fV_{DD}^2
  $$



##### 扇出数(Fan-out)

扇出数：一个电路的输出端驱动同类型负载电路输入端的数目

- 直流工作状态下扇出数非常大（负载电阻是所有负载门输入电阻的并联）

- 动态工作状态下的扇出数与工作频率有关

  > 随工作频率升高而降低。
  
  负载电容是所有负载门输入电容之和





##### 无缓冲级的CMOS门电路的缺陷

- 输入电阻受输入端影响
- 输出高 / 低电平手输入端数目的影响
- 输入端工作状态的不同对电压传输特性有影响

而一个完整的cmos GATE是需要逻辑功能+保护电路+缓冲级的

##### 带缓冲级

我们的解决方法很简单，对输入端和输出端都加入非门。

因此带缓冲级的与非就是或非在输入输出都加上反相器，带缓冲级的或非就是与非在输入输出都加上反相器：
![image-20260923100743870](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260923100743870.png)

##### 漏极开路输出门--OD门

- 用于输出电平的变换（这里$V_{DD1}$可以不等于$V_{DD2}$）

![image-20260923101429481](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260923101429481.png)

- 而且关键是可以吸收大负载电流（我们不需要考虑互补了)
- $R_{OFF}>>R_L>>R_{ON}$

##### OD门的线与接法

所谓线与就是我们不需要逻辑门就能实现与的功能（这很简单，因为我们的$R_{OFF}$远大于其他状态的输出电阻，只要有一个导通那就是决定性的，只有全部置高才输出1。而两个普通的cmos，一旦有两个同时导通，由于导通内阻几乎没有，会烧毁！）
![image-20260923101905417](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260923101905417.png)

##### OD门上拉电阻$R_L$的计算

而关于上拉电阻的计算，实际上我们只需要考虑电流总和：

- 最大值：$V_{DD}-R_L(nI_{OH}+mI_{IH})\geq V_{OH}$，此时对应最大的电阻：$R_L\leq \frac{V_{DD}-V_{OH}}{nI_{OH}+mI_{IH}}$（我们让所有od门输出高电平而输出的高电平不能低于规定的值）

- 最小值：输出低电平时，并联OD门中只有一个输出MOS管导通，负载电流不超过输出管允许最大电流，$R_L$不能太小：
  $$
  \frac {V_{DD}-V_{OL}}{R_L}+m'I_{IL}\leq I_{OL(max)} \\
  R_L \geq \frac {V_{DD}-V_{OL}}{I_{OL(max)-m'I_{IL}}}=R_{L(min)}
  $$
  



##### 传输门

目的：我们通过一个位来控制输出是否受输入影响
![image-20260923103536696](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260923103536696.png)

不过我们还是要关注一下截止的问题...

- $C$接低电平0，$v_1\in(0,V_{DD})$，$T_1 T_2$均截止，输出高阻态，相当于断开开关
- $C$接高电平$V_{DD}$，



有了传输门，我们就可以用它来更简单地时序爱你异或门了（应该用了更少的静态管，而且关键路径也变短了）

当然它也可以作为模拟开关



##### 三态门TS

![image-20260923105315153](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260923105315153.png)

用途：

- output buffer

- 总线





### ttl
