---
title: "概率论与随机过程"
date: 2026-11-05T14:00:00+08:00
draft: true
noteTags: ["数学", "概率论"]
---


分为概率统计+随机过程

## 概率统计

### 一 随机事件与概率

#### 1.1 随机事件与样本空间

先看一个例子：

> 两个孩子，男女都是0.5的概率，相互独立，出生在1~7平均分布，已知至少有一个是星期二出生的男孩，则两个都是男孩的概率？
>
> 事件A：至少有一个是星期二出生的男孩
> B：两个都是男孩
>
> 显然用贝叶斯公式：
> $$
> P(B|A) = \frac {P(A\and B)}{P(A)}
> $$
> 那么先计算$P(A)$
> 一个孩子”不是星期二出生“的概率：$1-1/(2\cdot 7)=13/14$ ，所以2个都不是就是：
> $(13/14)^2$ ，那么至少一个是就是$1-169/196=27/196$
>
> 而再计算$P(A\and B)$
> 至少一个是星期二出生：$1-(6/7)^2=13/49$，



**随机试验(E)**：对现象进行一次观察 / 试验，统称一次**试验**。而随机试验需要满足：

- **可重复性**
- **结果明确**
- **不确定性**

**随机事件($(A,B...)$)：**随机试验中所有可能出现的结果

**样本空间($\Omega 或 S$)：**随机试验中所有可能事件的集合。

而关于事件：

- **必然事件($\Omega$)：**随机试验中必然会发生的事件
- **不可能事件($\Phi$)：**一定条件下必然不会发生的事件
- **基本事件($e,w$)：**随机事件的一个可能结果，一个样本点
- **复合事件：**多个样本点

|            |                                |
| ---------- | ------------------------------ |
| 交换律     | $A+B=B+A,AB=BA$                |
| 结合律     | $(A+B)+c=A+(B+C),(AB)C=A(BC)$  |
| 分配律     | $(A+B)C=AC+BC,AB+C=(A+C)(B+C)$ |
| 德摩根公式 | $\bar{\sum A_i}=$              |

#### 1.2 概率的定义

**概率**：用来描述随机事件发生的可能性大小的数量指标

##### 古典概型

- 样本空间包含**有限**个基本事件$S= { e_1,...e_n}$
- 每个事件的发生是**等可能**的

因此古典概率被定义为概率$P(A)=\frac k n$，它的性质：

- $0\leq P(A)\leq 1$
- $P(S)=1$
- 对不相容的事件$A_i$，有$P(\sum_1^mA_i)=\sum_1^mP(A_i)$
- $P(A)=1-P(\bar A)$

局限性：基本事件总数有限，各个基本事件的发生等可能，一旦基本事件总数无限就用不了

##### 几何概型与概率的几何定义

- 样本空间是**测度有限空间**
- **样本点在区域内等概率**

因此几何概率的定义为$P(A)=\frac {L(A)}{L(S)}$（我们记这个度量为$L(A)$）

> 注意这里其实就引入了测度的概念，概率本身就可以被定义为一种特殊的测度

> 例：约会问题：两人会在10:00~10:30中任意时刻碰面，甲到达等待20min，乙到达后等待15min，相遇的概率？（这不高中题吗）
>
> 自然很简单，我们令到达时间甲x乙y，那么约束条件是$y\leq x+20,x\leq y+15\to x-15 \leq y \leq x+20$ ，画图就可以了：
> ![image-20260910123435586](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260910123435586.png)

流程：先建立几何模型明确样本空间$\Omega$，然后确定满足条件的区域$A$，

>  贝特朗悖论：
>
> 样本空间取的不一样，因此对概率本身的定义就是不一致的
>
> ![image-20260910105807179](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260910105807179.png)

关键在于我们该如何度量事件的概率。。。因此我们就引入了统计概率

##### 统计概率

1. 频率：

   某试验重复了$n$次，$A$发生了$m$次，则称$A$发生的频率$f(A)=\frac m n$

2. 统计概率：

   $p(A)=lim_{n\to \infty}f(A)$

##### 概率的公理化

1. 定义：
   - 非负性：$0\leq P(A)\leq 1$
   - 规范性：$P(\Omega)=1,P(\emptyset)=0$
   - 可列可加性：$A_i \in \Omega,A_iA_j=\emptyset且i\neq j,则有P(\sum_1^mA_i)=\sum_1^mP(A_i)$





##### 一些概率问题

> 这部分老师不知道为什么讲得特别快还不清晰... 所以大部分是我自己补充的

###### 容斥原理

我们想描述多个事件的并集，如何描述？
$$
\begin{aligned}
\left|\bigcup_{i=1}^{n} A_i\right|
=&
\sum_i |A_i|
-\sum_{i<j}|A_i\cap A_j|
+\sum_{i<j<k}|A_i\cap A_j\cap A_k|
\\
&-\cdots
+(-1)^{n+1}
|A_1\cap A_2\cap\cdots\cap A_n|
\end{aligned} \\
其中：\sum|A_{i_1}\cap...\cap A_{i_k}|=\binom nk (n-k)!
$$

###### 错排问题：

一个对刚刚这个结论的应用：

> 一共有n封信送到n个人手里，随机派送，全部送错的概率是多少？

我们定义事件$A_i={第i个人取到了第i个信封}$，而我们想计算的是$D_n=|\bar{A_1}\cap \bar{A_2}\cap...\cap\bar{A_n}|=\overline{|{A_1}\cap {A_2}\cap...\cap{A_n}|}=n!-\left|\bigcup_{i=1}^{n} A_i\right| \\ \begin{aligned} D_n =& n! -\binom n1(n-1)! +\binom n2(n-2)!-\binom n3(n-3)! +\cdots +(-1)^n\binom nn0! \end{aligned} \\
又因为\binom nk(n-k)!=\frac {n!}{k!(n-k)!}(n-k)!=\frac {n!}{k!} \\
D_n=n!\sum_{k=0}^n \frac {(-1)^k}{k!}$

所以最终概率就是$\sum_{k=0}^n \frac {(-1)^k}{k!}$

###### 贝特朗投票问题

这个问题就更有趣了，我们针对这样一个问题：

> 选举结束甲p乙q，p>q，那么投票过程中甲一直大于乙的概率？

先讲一种最简单的方法，那就是网格折线：

我们定义事件：
$A:第一张选票属于甲\\B:第一张选票属于乙\\C:第一张选票属于甲且后续和对角线有交点$

> 我们想一下什么情况下是非法的，我们知道首先第一步我们必须让甲拿到选票，也就向右走，而如果的确是第一张属于甲，那么后续我们就得保证和$(q,q)$构成的对角线没有交点。

而有趣的是如果我们仔细想一下，会发现无论如何对满足$B$的所有事件都保证了它后续一定会和对角线$l$产生交点，而这对满足事件$C$的来说，实际上我们只需要把$C$到第一个交点之前的按照对角线反射到对角线的另一端，就会发现它们其实完全等价！

> 为什么？因为一个很简单的理由：和对角线相交一定发生在$(q,q)$与原点构成的四方形以内，而在这个结构里面只要和对角线相交就是完全对称的!
>
> 不过这个说法太笼统也不够严谨... 首先我们容易证明任何$C$经过反射都一定有$B$中反射对应的路径（因为$(1,0)$对应后第一步一定是$(0,1)$加上经过对角线的）；反过来我们同样也可以证明任何$B$本身也有$C$的对应，因为它一定要穿过对角线，否则不可能到达$(p,q)$...

而我们想求的概率就是$1-(P(B)+P(C))=1-2P(B)$

显然就是有p+q步，我们要想办法选出来其中p步，那么样本空间就是$\binom {p+q}p$。

而选择$B$的事件数量是：$\binom {p+q-1}{q-1}=\binom {p+q-1}p$ ，结果就是$\frac {p-q}{p+q}$

#### 1.3 条件概率

在$P(A|B)=\frac {P(AB)}{P(B)}$，代表B条件下A的概率

性质：

- 有界：$0\leq P(A|B) \leq 1$

  边界：$P(S|B)=\frac {P(SB)}{P(B)}=1;P(\empty | B)=0$

- 若$A_1,A_2...A_n$互不相容，那么有：
  $$
  P(\sum_{i=1}^nA_i|B)=\sum_{i=1}^nP(A_i|B)
  $$
  
- $P(\bar A|B)+P(A|B)=1$

**加了条件概率的变化可以是任意的**.

乘法公式：$P(AB)=P(B)P(A|B)$，
推广：$P(A_1..A_n)$

>  $P(A)=0.6,P(B)=0.5,P(\bar A|B)=0.35,P(\bar  B-A)?$
>
> $P(\bar B-A)=P(\bar B \bar A) \\=1-P(A+B)=1-(P(A)+P(B)-P(AB))$
>
> $P(A|\bar B)=\frac {P(A-AB)}{P(\bar B)}$，





> 黑白球不放回取出2球，两次都是白的概率$\frac 1 3$
>
> - 球最小的个数？
> - 黑球为偶数最少的球数？
>
> > 白a黑b，那么第一次抽到白色$\frac {a}{a+b}$，第二次抽到白色



几个重要的性质：

- $若B \subset A, P(A-B)=P(A)-P(B)$
- $P(A+B)=P(A)+P(B)-P(AB)$，$P(A+B)\leq P(A)+P(B)$
- 

#### 1.4 全概率公式 贝叶斯公式

##### 全概率公式

> 由原因推结果

###### 定义

对事件组$B_1,...B_n$，如果：

- $\sum B_i= S$
- $B_1,...B_n$互不相容
- $P(B_i)>0,i=1,..n$

则对任意事件必有$P(A)=\sum P(B_i)P(A|B_i)$

> 甲m乙n，现在进行赌博，每局1元，甲输光的概率？
>
> 显然$P(A)=P(B)P(A|B)+P(\bar B)P(A|\bar B)$
>
> 显然唯一的区别就是甲还剩多少，我们关注$P_m$
>
> 那么显然有：$P_m=\frac 12(P_{m+1}+P_{m-1})$，同时有边界条件：$P_0=1,P_{m+n}=0$
>
> 结果便是$P_m=\frac n{m+n}$



##### 贝叶斯公式

> 反过来，当我们已经知道一个结果了，那么它产生于何种原因的概率如何？
>
> 已知结果推原因

定义：如果：

1. $\sum_1^nB_i=S$

2. $B_1,..B_n$互不相容
3. $P(B_i)>0$

那么对任意事件A：
$$
P(B_i|A)=\frac{P(AB_i)}{P(A)}=\frac {P(B_i)P(A|B_i)}{ \sum_{i=1}^n P(B_j)P(A|B_j)}
$$
![image-20260914104426576](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260914104426576.png)





#### 1.5 事件独立性：

定义：对任意两个事件A与B，若$P(AB)=P(A)P(B)$，那么称两事件相互独立

定理：

1. 对任意事件A与B，且$P(B)>0$，则二者独立的充要条件：$P(A|B)=P(A)$
2. 若事件A与B独立，则：$\bar A$与$B$ / $A$与$\bar B$ / $\bar A$与$\bar B$均相互独立







基于贝叶斯思想的分类算法：

后验概率求解：

如果我们假定特征条件相互独立，就有：

$P(A|W_1, W_2,...W_n)=\frac {P(A)P(W_1,...W_n| A)}{P(W_1,W_2,..W_n)} \\ =\frac {P(W_1|A)P(W_2|A)...P(W_n|A)P(A)}{P(W_1,...,W_n|A)P(A)+P(W_1,...W_n|H)P(H)}$









### 二 随机变量及其分布

#### 2.1 随机变量及其分布函数

##### 随机变量

定义1 随机变量

设E为随机试验，若每次实验结果可用一个数$X$表示，且对任意实数$x$，$X\leq x$有确定的概率$P(X\leq x)$，则称$X$为一维随机变量

分类：

- 连续型随机变量
- 离散型随机变量

##### 概率分布函数

**定义2 概率分布函数**

设$X$一随机变量，对任意$x\in R$，令$F(x)=P(X\leq x),x\in (-\infty,+\infty)$，就是概率分布函数，记为$X$~$F(x)$

**特征：**

- 取值范围：[0,1]
- 单调增
- $x\to -\infty, F\to 0 \\ x\to +\infty, F\to 1$
- 极值点：$F(+\infty)=\lim_{x\to+\infty}F(x)=1,F(-\infty)=\lim_{x\to-\infty}F(x)=0$
- 右连续：对一切实数$x_0$，$F(x_0^+)=\lim_{x\to x_0^+}=F(x_0)$
- 对任意实数$a<b$，则$P\{a<x\leq b\}=F(b)-F(a)$



一维分布

- 分布函数$F_X(x)=P(X\leq x)$
- 离散型：$F_X(x)=\sum P(X=x)=\sum p_k$
- 连续型：$F_X(x)=\int_{-\infty}^{x} f(t)dt$



对离散型随机变量：

离散型随机变量的分布律用分布列来表述，有$P(X=x_k)=F(x_k)-F(x_k^-)$



##### 常用的离散型随机变量

1. **两点分布**

   > 伯努利概型 

2. **二项分布**

   > n重伯努利binomial：$P(X=k)=\binom nk p^n q^{n-k}$

3. **几何分布**

   > 连续地抛掷一枚硬币直到正面出现所需要抛掷的次数

   $P(X=k)=p^k(1-p)^k$

4. **超几何分布**

   > 不放回的抽样模型.

   比如：M件正品，N件次品，从中任取n件，取到的次品个数$X$，它的分布便是：
   $$
   P\{X=k\}=\frac {\binom Nk \binom M{n-k}}{\binom {M+N}n},k=0,1..,l 
   \\ l=min(n,N)
   $$
   

###### **泊松分布**

   $P(X=k)=e^{-\lambda}\frac {\lambda ^k}{k!},k=0,1,2,...$，记作$X$~$\prod(\lambda)$

   > 主要用于计数的问题中

   如果我们能的得到：$\sum_0^{\infty}P(X=k)=e^{-\lambda}\sum \frac{\lambda^k}{k!}=1$,就可以用泊松分布

**泊松近似定理：**

设随机变量序列$\{X_n\},X_n~B(n,p_n)$，则：
$$
\lim_{n\to \infty}\binom nk p_n^k (1-p_n)^{n-k}=e^{-\lambda}\frac {\lambda ^k}{k!}
$$
其中$\lambda = np_n>0$（一般是1），k为固定的非负整数

**需要n很大p很小！**

> 证明：
>
> 当$k\geq1$时，
> $$
> P_n(k)=\binom nkp^k(1-p)^{n-k} \\
> = \frac {n(n-1)...(n-k+1)}{k!}(\frac \lambda n)^k(1-\frac \lambda n)^{n-k}	\\
> = \frac {\lambda^k}{k!}[1(1-\frac 1n)(1-\frac 2n)..(1-\frac{k-1}n)] (1-\frac \lambda n)^n (1-\frac \lambda n)^{-k} \\
> = \frac {\lambda^k}{k!}e^{-\lambda}
> $$
> 

---

   > 比如：保险，每位交50元，出险时获得2万元赔付，已知一年中出险率位$0.15\%$，6000人，获利不少于6万元的概率？
   >
   > 已知：$X$~$B(6000,0.0015)$，而此时服从$\lambda=np=9$的泊松分布
   >
   > 收入为30万元，为了获利6万只能小于12个人出险，那么计算对应的概率：
   > $$
   > \sum_{0}^{12}\frac {9^k}{k!}e^{-9}=0.876
   > $$



#### 2.2 连续型随机变量

**定义1 ：**

设随机变量$X$的分布函数F(x)，那么存在一个定义在$(-\infty, +\infty)$上的非负可积函数使得对任意实数恒有
$$
F(x)=\int_{-\infty}^{x}f(t)dt
$$
**定理1:**

- $F(x)= \int_{-\infty}^{x}f(t)dt$是连续函数
- 对一切$x\in (-\infty,+\infty),P\{X=x\}=F(x)-F(x^-)=0$
- 对任意$a<b$，有$P\{a<X\leq b\}=F(b)-F(a)=\int_a^b f(x)dx$
- 若$f(x)$在$x_0$连续，则$F(x)$在点$x_0$处可导，且$F'(x_0)=f(x_0)$

各种连续分布：

##### 均匀分布

没啥好说的，就是均分：
$$
f(x) = \left \{
\begin{array}{} 
\frac 1{b-a}, a\leq x\leq b \\
0,其他
\end{array}
\right.
$$

----

##### 指数分布：

$$
f(x)=\left \{
\begin{array}{} 
\lambda e^{-\lambda x}, a\leq x\leq b \\
0,其他
\end{array}
\right.
$$

**无记忆性**：$P(X>s+t|X>s)=p(X>t)$

---

##### 韦布尔分布：

$$
f(x)=\frac \beta \eta (\frac {x-x_0}{\eta})^{\beta-1} e^{-(\frac{x-x_0}{\eta})^\beta}, x>x_0
$$

 

- $\beta=1\to 指数分布 \\ \beta=2\to 瑞丽分布$

---

##### $\Tau$分布（伽马分布）：

$f(x)=\frac{\beta^\alpha}{\Tau(\alpha)}x^{\alpha-1}e^{-\beta x}, x>0$

- 当$\alpha=\frac n 2,\beta=\frac 1 2$时，此时就是$\chi^2(n)$分布
- 

---

##### 正态分布：

若随机变量$X$的概率密度函数：
$$
f(x)=\frac1{\sqrt{2\pi}\sigma}e^{[-\frac{(x-\mu)^2}{2\sigma^2}]}
$$

> 证明一下它的积分为1？
>
> 很显然我们知道高斯积分的计算结果为$\sqrt\pi$，那么变换一下先做一个归一化，令$y=\frac {x-\mu}{\sqrt2\sigma}$，那么很显然最后在实轴上的积分就是1了

**标准正态分布：**

$x\sim N(0,1), \phi(x)=\frac1{\sqrt{2\pi}}\int_{-\infty}^xe^{-\frac {t^2}2}dt$

> 而任意随机变量满足正态分布，我们变量代换一下就是标准正态分布了

**性质：**

- $\Phi(x)+\Phi(-x)=1$
- $\Phi(0)=\frac 12$
- 
- 

- 

**标准正态分布的$\alpha$分位点：**
满足$P\{X\leq  z_\alpha\}=\alpha \in (0,1)$，那么就有：

- $z_\alpha=-z_{1-\alpha}$
- $P\{X>z_{1-\alpha}\}=\alpha$
- $P\{|X|>Z_{1-\frac\alpha2}\}=\alpha$





#### 2.3 二维随机变量及其分布

##### 二维随机变量

**定义1**  n维随机变量

设$E$为随机试验，样本空间为$S=\{e\}$，概率空间为$\{S,F,P\}$，而$X_1(e),X_2(e),...,X_n(e)$为定义在样本空间上的$n$个随机变量，称由这$n$个随机变量组成的向量$(X_1(e),X_2(e),...,X_n(e))$为n维随机变量(向量)

**定义2** 设$(X,Y)$为二维随机变量，对∀$x,y$，二元函数：
$$
F(x,y)=P\{X\leq x,Y\leq y\}=P\{e \in S | X(e)\leq x, Y(e)\leq y\}
$$
称为二维随机变量$(X,Y)$的分布函数，或称随机变量$X$与$Y$的联合分布函数

**4个性质：**

- 取值范围$(0,1)$
- 单调增
- 右连续：$F(x^+,y)=\lim_{\Delta x\to 0^+}F(x+\Delta x, y)=F(x,y)$
- $F(x,-\infty)=0,F(-\infty,y)=0 \\F(+\infty,+\infty)=1$（只要有一个趋于负无穷那就是0）
- $$
  0\leq P\{x_1<X\leq x_2,y_1\leq Y\leq y_2\}=F(x_2,y_2)+F(x_1,y_1)-F(x_1,y_2)-F(x_2,y_1)
  $$



> 蒲丰投针问题：
>
> 平面上有间隔为$d$的平行线，向平面投一长$l <d$的针，求相交的概率？
>
> 我们不妨通过两个参数来描述这个问题：中点和最近一条平行线的距离$x$，针与平行线的夹角$\phi$，那么我们需要描述的问题就是：$x\leq \frac l2 sin\phi$，看看它的面积如何？
>
> ![image-20261018190054024](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261018190054024.png)
>
> 很显然，答案是：
> $$
> P(A)=\frac {\int_0^\pi \frac l2 sin\phi d\phi}{\frac \pi 2 d}=\frac {2l}{\pi d}
> $$
> 

##### 二维随机变量分类

二维连续型随机变量：
$$
F(x,y)=\int_{-\infty}^y \int_{-\infty}^x f(x,y)dxdy 
$$

##### 二维连续型随机变量的性质

1. $$
   f(x,y) \geq 0
   $$

2. $$
   \int_{-\infty}^{+\infty}f(x,y)dxdy=F(-\infty,+\infty)=1
   $$

3. 若概率密度$f(x,y)$在点$(x_0,y_0)$的某个邻域内连续：
   $$
   \frac {\partial^2 F(x,y)}{\partial x \partial y}|_{x=x_0\\y=y_0}=f(x_0,y_0)
   $$

4. 利用概率密度可以计算概率：
   定理：
   设



##### 边缘分布函数

定义：设二维随机变量$(X,Y)$分布函数位$F(x,y)$，而分量$X$的分布函数记为$F_X(x)$，称$F_X(x)$为$(X,Y)$关于$X$的边缘分布函数：
$$
F_X(x)=\lim_{y\to +\infty}F(x,y)=F(x,+\infty)\\
F_Y(y)=\lim_{x\to +\infty}F(x,y)=F(+\infty,y)
$$
而显然这两个是对原本的$F(x,y)$的降维，所以往往我们无法从边缘分布函数得到原分布函数

##### 边缘分布律

设离散随机变量$(X,Y)$的分布律：
$$
P\{X=x_i, Y=y_i\}=p_{ij}
$$
那么$(X,Y)$关于$X$或$Y$的边缘分布律：
$$
P\{X=x_i\}=\sum_j P\{X=x_i,Y=y_j\}=\sum_j p_{ij} \\
P\{Y=y_i\}=\sum_i P\{X=x_i,Y=y_j\}=\sum_i p_{ij}
$$
![image-20260928100506073](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260928100506073.png)

##### 条件分布律

已知二维离散型随机变量$(X,Y)$的分布律：
$$
P\{X=x_i, Y=y_i\}=p_{ij}
$$
那么当$P\{X=x_i\}>0$时称这个为在$X=x_i$条件下$Y$的分布律：
$$
P\{X=x_i|Y=y_i\}=\frac {P\{X=x_i, Y=y_i\}}{P\{X=x_i\}}
$$

> 例：
>
> ![image-20260928101357733](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260928101357733.png)

##### 边缘概率密度

我们已知边缘分布函数：
$$
F(x,y)=\int_{-\infty}^{x}\int_{-\infty}^{y}f(u,v)dvdu\\
\to F_X(x)=F(x,+\infty)=\int_{-\infty}^{x}[\int_{-\infty}^{+\infty}f(u,v)dv]du \\
\to f_X(x)=\int_{-\infty}^{+\infty}f(x,y)dy1
$$


##### 条件分布函数

对于二维连续性随机变量$(X,Y)$，若存在极限
$$
\lim_{\varepsilon\to 0^+}P\{X\leq x | y-\varepsilon<Y<y+\varepsilon\}
$$
就称此极限为在条件$Y=y$下$X$的**条件分布函数**，记为$F_{X|Y}(x|y)$或$P\{X\leq x|Y=y\}$

##### 条件概率密度

对于二维连续型随机变量$(X,Y)$，已知二维概率密度函数$f(x,y)$和边缘概率密度函数$f_Y(y)$，若对于固定的y，$f_Y(y)>0$，则定义在$Y=y$条件下$X$的条件概率密度为：
$$
f_{X|Y}(x|y)=\frac {f(x,y)}{f_Y(y)}
$$
而关系就是：
$$
F_{X|Y}(x|y)=\int_{-\infty}^x f_{X|Y}(u|y)du=\int_{-\infty}^x\frac{f(u,y)}{f_Y(y)}du
$$


##### 独立性：

**定义：**

设两个随机变量$X,Y$，若对任意x,y，有：
$$
P\{X\leq x,Y \leq y\}=P\{X\leq x\}P\{Y\leq y\}
$$
则称**相互独立**

**定理：** **如果$f(x,y)=f_X(x)\cdot f_Y(y)$，那么就等价于独立的**

> 只有独立的时候才能从边缘分布反推联合分布

---

> 例6：设$(X,Y)$的概率密度函数为：
> $$
> f(x,y)=xe^{-(x+y)}~x>0,y>0
> $$
> 是否相互独立？
> $$
> f_X(x)=\int_{-\infty}^{+\infty}f(x,y)dy=\int_0^{+\infty}xe^{-(x+y)}dy=xe^{-x}, x>0 \\
> f_Y(y)=\int_{-\infty}^{+\infty}f(x,y)dx=e^{-y},y>0
> $$
> 显然满足$f(x,y)=f_X(x)f_Y(y)$





而正态分布显然是独立的：

> 推导：二维正态分布显然可以写为独立的边缘分布，反过来我们已知





### 随机变量函数的分布

#### 离散型随机变量的函数的分布

##### 离散型随机变量的函数的分布律

已知$P\{X=x_i\}=p_i$
若对$X$的不同取值$x_i$，$Y=g(X)$的取值$g(x_i)=y_i$也不同，则随机变量$Y=g(X)$的分布律为：
$$
P\{Y=g(x_i)=y_i\}=p_i
$$
而如果对$X$有限个 / 可列无穷多个不同取值$x_{i_1},...,x_{i_n}$，有
$$
g(x_{i_1})=...=g(x_{i_k})=y^*
$$
那么$P\{Y=y^*\}=\sum_k P\{X=x_{i_k}\}$

##### 二维离散随机变量的函数的分布律

> 这个同上，无需赘述

> 例题：
>
> 已知$X$~$\prod(\lambda_1)$，$Y$~$\prod(\lambda_2)$，且$X$和$Y$相互独立，证明：$Z=X+Y$~$\prod(\lambda_1+\lambda_2)$
> $$
> P\{X=i\}=\frac{e^{-\lambda_1}\lambda_1^i}{i!} \\
> P\{Y=j\}=\frac{e^{-\lambda_2}\lambda_2^j}{j!} \\
> P\{Z=k\}=\sum_{i=0}^{k}P\{X=i,Y=k-i\}\\
> =\sum_{i=0}^{k}\frac{e^{-\lambda_1}\lambda_1^i}{i!}\frac {e^{-\lambda_2}\lambda_2^{k-i}}{(k-i)!} \\
> =\frac {e^{-k}}{k!}\sum_{i=0}^{k}\binom ki\lambda_1^i\lambda_2^{k-i}
> $$
> 



#### 连续型随机变量的函数的分布



如果已知$X$概率密度为$f(x)$，$y = g(x)$在区间$(a,b)$上严格单调，其反函数$x=h(y)$有连续导数，则$Y=g(X)$是一个连续型随机变量，其概率密度为：
$$
f_Y(y)=f(h(y))\cdot |h'(y)|,~y\in(c,d)
$$

> 原因：我们的宽度变了，因为我们知道概率密度的定义取决于宽度

> 证明：
>
> 我们首先看X，从X的分布出发，由于严格单调，我们知道：
> $$
> P(c<Y<d)=P(c<g(x)<d)=P(h(c)<x<h(d))=\int_{h(a)}^{h(b)}f_X(x)dx
> $$
> 那么把变量更换一下就好了，$dx=h'(y)dy$，那么自然就等于$\int_a^bf_X(h(y))|h'(y)|dy$，而左侧分布本身就等于$\int_a^bf_Y(y)dy$，那就证明了...

如果要求目标函数的概率密度，如果已知概率密度，那么完全可以按照这条函数路径积分，它等价于从负无穷到正无穷的对原概率密度函数的积分，但是要加上这个函数作为约束

以及如果不是一一对应的变换，那么最保险通用的方法实际上还是直接求分布函数然后求导

#### 二维连续型随机变量的函数的分布

问题是针对于已知的概率密度，求一二维函数$z=g(X,Y)$的概率密度

##### Z=X+Y

这个我们直接代换就好了，$y=z-x$代入积分


##### Z=max{X,Y}

两种方法：

1. $$
   F_{max}(z)=F(z,z)
   $$

2. $$
   F_{max}(z)=\int_{-\infty}^z\int_{-\infty}^zf(x,y)dxdy
   $$

3. 如果相互独立，那就是：
   $$
   F_{max}(z)=\prod_1^nF_i(z)
   $$



##### Z=min{X,Y}

等价于$1-P\{Y\geq Z,X\geq Z\}$，同样两种方法：

1. $$
   F_{min}(z)=1-P\{min\{X,Y\}>Z\}=1-P\{X>z,Y>z\}=1-\iint_{x>z\\y>z}f(x,y)dxdy
   $$

2. $$
   F_{min}(z)=P\{min\{X,Y\}\leq z\}\\
   =P\{X\leq z\}+P\{Y\leq Z\}-P\{X\leq z,Y\leq z\} \\
   =F_X(z)+F_Y(z)-F(z,z)
   $$

3. 而如果相互独立，那就是：
   $$
   F_{min}(z)=1-\prod_1^n[1-F_i(z)]
   $$



总之其实都很简单，我们要做的就是最终把它转化为分布函数或者概率密度函数的积分的形式






### 随机变量的数学特征

#### 均值/方差

##### 数学期望

离散：已知随机变量分布律$p_k$，若级数$\sum_{1}^{+\infty} x_kp_k$绝对收敛，那么就称它为$X$的数学期望，记为E(X)

连续：$E(X)=\int_{-\infty}^{+\infty} xf(x)dx$，同样前提为绝对收敛，也即$\int_{-\infty}^{+\infty} |x|f(x)dx$收敛

离散随机向量：比如我们已知$Z=g(X,Y)$，那么就是$E(Z)=\sum\sum g(x_i,y_j)p_{ij}$，

连续随机向量：$EZ=Eg(X,Y)=\int_{-\infty}^{+\infty}\int_{-\infty}^{+\infty}g(x,y)f(x,y)dxdy$，同样要求绝对收敛

###### 性质

- $E(X+Y)=E(X)+E(Y)$
- $E(CX)=CE(X)$
- 也就是说它是线性的（这很显然，因为我们做的不管是求和还是积分都是线性算子）
- 如果$X,Y$独立且$E(X),E(Y),E(XY)$存在，那么有$E(XY)=E(X)E(Y)$

##### 方差

$D(X)=E(X-EX)^2=E(X^2)-E^2(X)$定义，也可写作$var(X)$

而$\sqrt{DX}$称为标准差/均方差

连续由概率密度函数：$DX=E(X-EX)^2=\int_{-\infty}^{+\infty} (x-EX)^2f(x)dx$

###### 性质

- 如果$X,Y$为相互独立的随机变量，则有：
  - $D(X+Y)=D(X)+D(Y) \\ D(X-Y)=D(X)+D(Y)$
  - $D(aX+bY+C)=a^2DX+b^2DYd$
  - $D(XY)=D(XY)^2-[D(XY)]^2=EX^2EY^2-(EX)^2(EY)^2$



##### 条件期望









##### 常见随机变量的数学期望和方差

##### 0-1分布

$$
EX=1p+0(1-p)=p \\
EX^2=p \\
DX=p(1-p)
$$

##### 二项分布

$X$~$B(n,p)$，$P\{X=k\}=\binom nkp^k(1-p)^{n-k}$

显然直接计算是愚蠢的，实际上由于是独立同分布，均服从0-1分布
$$
EX=E(\sum X_i)=\sum EX_i=np \\
DX=D(\sum X_i)=\sum DX_i=\sum p(1-p)=np(1-p)
$$


##### 泊松分布

$X$~$\prod (\lambda )$，也即：
$$
P\{X=k\}=\frac {e^{-\lambda} \lambda^k}{k!}
$$
根据离散型随机变量数学期望的定义：

\[ \begin{aligned} E(X) &=\sum_{k=0}^{\infty}kP\{X=k\}\\ &=\sum_{k=0}^{\infty} k\frac{e^{-\lambda}\lambda^k}{k!} \\ &=e^{-\lambda}\sum_{k=1}^{\infty} \frac{k\lambda^k}{k!}\\ &=e^{-\lambda}\sum_{k=1}^{\infty} \frac{\lambda^k}{(k-1)!} \\ &=\lambda e^{-\lambda}\sum_{j=0}^{\infty}\frac {\lambda^j} {j!} \\ &= \lambda \end{aligned}\]

而方差先求\[EX^2\]：

\[ \begin{aligned} E(X^2) &=\sum_{k=0}^{\infty}k^2P\{X=k\}\\ &=e^{-\lambda}\sum_{k=1}^{\infty} \frac{k^2\lambda^k}{k!} \end{aligned} \]

这里不能直接把 \(k^2\) 约掉，应该将其拆成：\[ k^2=k(k-1)+k\]，就有：

\[ \begin{aligned} E(X^2) &=e^{-\lambda}\sum_{k=0}^{\infty} \frac{[k(k-1)+k]\lambda^k}{k!}\\ &=e^{-\lambda}\left[ \sum_{k=2}^{\infty} \frac{k(k-1)\lambda^k}{k!} +\sum_{k=1}^{\infty} \frac{k\lambda^k}{k!} \right]\\ & look~familiar? \\ &= \lambda^2 + \lambda \end{aligned} \]

那么就有：

\[ \begin{aligned} D(X) &=E(X^2)-[E(X)]^2\\ &=(\lambda^2+\lambda)-\lambda^2\\ &=\boxed{\lambda} \end{aligned} \]

也就是说：\[ \boxed{E(X)=D(X)=\lambda} \]





##### 指数分布

懒得写了



##### 正态分布

求期望很简单，我们利用\[x-\mu\]期望为0即可。方差也差不多。





##### 均匀分布









### 常见分布的表

#### 离散：

| 分布                          | 概率质量函数                                            | \(E(X)\)       | \(D(X)\)                                    |
| ----------------------------- | ------------------------------------------------------- | -------------- | ------------------------------------------- |
| 0-1 分布 \(X\sim B(1,p)\)     | \(P(X=k)=p^k(1-p)^{1-k},\ k=0,1\)                       | \(p\)          | \(p(1-p)\)                                  |
| 二项分布 \(X\sim B(n,p)\)     | \(P(X=k)=\binom nk p^k(1-p)^{n-k}\)                     | \(np\)         | \(np(1-p)\)                                 |
| 泊松分布 \(X\sim P(\lambda)\) | \(P(X=k)=\dfrac{e^{-\lambda}\lambda^k}{k!}\)            | \(\lambda\)    | \(\lambda\)                                 |
| 几何分布 \(X\sim G(p)\)       | \(P(X=k)=(1-p)^{k-1}p,\ k\ge1\)                         | \(\dfrac1p\)   | \(\dfrac{1-p}{p^2}\)                        |
| 超几何分布 \(X\sim H(N,M,n)\) | \(P(X=k)=\dfrac{\binom Mk\binom{N-M}{n-k}}{\binom Nn}\) | \(n\dfrac MN\) | \(n\dfrac MN(1-\dfrac MN)\dfrac{N-n}{N-1}\) |

#### 连续：

| 分布                                | 概率密度函数 \(f(x)\)                                        | \(E(X)\)                    | \(D(X)\)                      |
| ----------------------------------- | ------------------------------------------------------------ | --------------------------- | ----------------------------- |
| 均匀分布 \(U(a,b)\)                 | \(\dfrac1{b-a},\ a<x<b\)                                     | \(\dfrac{a+b}{2}\)          | \(\dfrac{(b-a)^2}{12}\)       |
| 指数分布 \(E(\lambda)\)             | \(\lambda e^{-\lambda x},\ x>0\)                             | \(\dfrac1\lambda\)          | \(\dfrac1{\lambda^2}\)        |
| 正态分布 \(N(\mu,\sigma^2)\)        | \(\dfrac1{\sqrt{2\pi}\sigma}e^{-\frac{(x-\mu)^2}{2\sigma^2}}\) | \(\mu\)                     | \(\sigma^2\)                  |
| 标准正态分布 \(N(0,1)\)             | \(\dfrac1{\sqrt{2\pi}}e^{-x^2/2}\)                           | \(0\)                       | \(1\)                         |
| 伽马分布 \(\Gamma(\alpha,\lambda)\) | \(\dfrac{\lambda^\alpha}{\Gamma(\alpha)}x^{\alpha-1}e^{-\lambda x},\ x>0\) | \(\dfrac{\alpha}{\lambda}\) | \(\dfrac{\alpha}{\lambda^2}\) |

#### 其他的：

| 分布                   | 概率密度函数                                                 | \(E(X)\)                                   | \(D(X)\)                                               |
| ---------------------- | ------------------------------------------------------------ | ------------------------------------------ | ------------------------------------------------------ |
| 卡方分布 \(\chi^2(n)\) | \(\dfrac{x^{n/2-1}e^{-x/2}}{2^{n/2}\Gamma(n/2)},\ x>0\)      | \(n\)                                      | \(2n\)                                                 |
| \(t\) 分布 \(t(n)\)    | \(\dfrac{\Gamma(\frac{n+1}{2})}{\sqrt{n\pi}\Gamma(\frac n2)}(1+\frac{x^2}{n})^{-\frac{n+1}{2}}\) | \(n>1\) 时为 \(0\)；\(n\le1\) 时期望不存在 | \(n>2\) 时为 \(\dfrac n{n-2}\)；\(n\le2\) 时方差不存在 |





#### 协方差和相关系数

##### 定义：

$Cov(X,Y)=E[(X-EX)(Y-EY)]=E[XY-X\cdot EY-Y\cdot EX+EX\cdot EY]=E(XY)-EX\cdot EY$



##### 性质：

| 性质           | 公式                                                         |
| -------------- | ------------------------------------------------------------ |
| 自身协方差     | \(\operatorname{Cov}(X,X)=D(X)\)                             |
| 对称性         | \(\operatorname{Cov}(X,Y)=\operatorname{Cov}(Y,X)\)          |
| 与常数的协方差 | \(\operatorname{Cov}(X,c)=0\)                                |
| 加常数不变     | \(\operatorname{Cov}(X+a,Y+b)=\operatorname{Cov}(X,Y)\)      |
| 常数倍提取     | \(\operatorname{Cov}(aX,bY)=ab\operatorname{Cov}(X,Y)\)      |
| 对加法的线性性 | \(\operatorname{Cov}(X+Y,Z)=\operatorname{Cov}(X,Z)+\operatorname{Cov}(Y,Z)\) |
| 两个线性组合   | \(\operatorname{Cov}(aX+bY,cZ+dW)=ac\operatorname{Cov}(X,Z)+ad\operatorname{Cov}(X,W)+bc\operatorname{Cov}(Y,Z)+bd\operatorname{Cov}(Y,W)\) |

- 方差$D(X)=Cov(X,X)$

- 利用协方差的线性性质，能够推出：

  \[ \boxed{D(X+Y)=D(X)+D(Y)+2\operatorname{Cov}(X,Y)} \]

  同理，

  \[ \boxed{D(X-Y)=D(X)+D(Y)-2\operatorname{Cov}(X,Y)} \]

  更一般地，

  \[ \boxed{D(aX+bY)=a^2D(X)+b^2D(Y)+2ab\operatorname{Cov}(X,Y)} \]



##### 定理

###### 1. 独立性定理

若 \(X,Y\) 相互独立，则\[ E(XY)=E(X)E(Y) \]，因此有：

\[ \boxed{X,Y\text{ 独立}\implies \operatorname{Cov}(X,Y)=0} \]

**注意：逆命题不成立！**

即使 \(\operatorname{Cov}(X,Y)=0\)，也不能一般地推出 \(X,Y\) 独立。

> 例如，设 \(X\sim U(-1,1)\)，且 \(Y=X^2\)。显然 \(Y\) 完全由 \(X\) 决定，因此二者不独立。但由于
>
> \[ \begin{aligned} \operatorname{Cov}(X,Y) &=E(X^3)-E(X)E(X^2)\\ &=0-0\cdot E(X^2)\\ &=0 \end{aligned} \]
>
> 所以它们不相关，却不独立。

###### 2. 柯西–施瓦茨不等式

设任意随机变量的二阶矩$EX^2,EY^2$存在，那么下列不等式成立：
$$
|E(XY)|\leq \sqrt{EX^2} \cdot \sqrt{EY^2}
$$

> 证明

\[ \boxed{|\operatorname{Cov}(X,Y)| \leq \sqrt{D(X)D(Y)}} \] or\[ \boxed{\operatorname{Cov}^2(X,Y) \leq D(X)D(Y)} \]

###### 3. 相关系数定理

当 \(D(X)>0,D(Y)>0\) 时，定义相关系数

\[ \boxed{\rho_{XY}= \frac{\operatorname{Cov}(X,Y)} {\sqrt{D(X)}\sqrt{D(Y)}}} \]

由柯西–施瓦茨不等式，

\[ \boxed{-1\leq \rho_{XY}\leq 1} \]

并且：

- \(\rho_{XY}>0\)：正相关。
- \(\rho_{XY}<0\)：负相关。
- \(\rho_{XY}=0\)：不相关。
- \(|\rho_{XY}|=1\)：存在常数 \(a,b\)，使得 \(Y=aX+b\) 几乎处处成立，其中 \(a\neq0\)。越接近1越近似于线性关系

相关系数与协方差的区别是：协方差受变量的量纲和尺度影响，而相关系数没有量纲，且始终处于 \([-1,1]\) 内。

###### 4. 联合正态分布定理

若 \(X,Y\) 服从**联合正态分布**，也即\[(X,Y)\]~\[N(\mu_1,\sigma_1^2;\mu_2,\sigma_2^2;\rho)\]则：

\[ \boxed{\operatorname{Cov}(X,Y)=0 \iff X,Y\text{ 独立}} \]

这里必须强调“联合正态”，仅仅知道 \(X,Y\) 各自服从正态分布，并不足以保证这个结论成立。

这也是协方差为零时，一个非常重要的特殊情形。





#### 矩

矩就是一些数字特征的泛称/总称。

我们定义：

- \[E(X^k)\]存在，称为$X$的k阶原点矩
- \[E(X-EX)^k\]存在，称为$X$的k阶中心矩



#### 协方差矩阵

我们定义：
$$
C_{ij}=Cov(X_i,X_j)=E[(X_i-EX_i)(X_j-EX_j)]
$$
则矩阵
$$
C=(C_{ij})_{n\times n}
$$
就称为n维随机向量\[X_1,...,X_n\]的协方差矩阵

> 实际上，协方差矩阵本质就是向量的外积：
> \[ \boxed{ \operatorname{Cov}(\boldsymbol X) = E[ (\boldsymbol X-\boldsymbol\mu) (\boldsymbol X-\boldsymbol\mu)^T ] } \]
>
> 它的结构是：
>
> \[ \begin{pmatrix} D(X_1)&\operatorname{Cov}(X_1,X_2)&\cdots\\ \operatorname{Cov}(X_2,X_1)&D(X_2)&\cdots\\ \vdots&\vdots&\ddots \end{pmatrix} \]
>
> 









### 四 大数定律和中心极限定理

#### 4.1 马尔可夫不等式和切比雪夫不等式

---

**定理1：（马尔可夫不等式）**

设随机变量$X$若$E|X|^k$存在(k>0),则对任意正数$\varepsilon$有：
$$
P\{|X|>\varepsilon\} \leq \frac {E|X|^k}{\varepsilon^k}
$$

> 证明其实很简单，因为：
> $$
> P\{X\geq \varepsilon\}=\sum_{|x_i|\geq \varepsilon}P\{X=x_i\}\leq\sum_{|x_i|\leq \varepsilon}\frac {|x_i|^k}{\varepsilon^k}P\{X=x_i\}\leq\frac 1{\varepsilon^k}\sum_i {|x_i|^k}P\{X=x_i\}=\frac {E|X|^k}{\varepsilon^k}
> $$
> 连续同理

---

**定理2：（切比雪夫不等式）**

> 马尔可夫不等式的特殊情况

设随机变量 \(X\) 的数学期望为 \(E[X]=\mu\)，方差为 \(D(X)=\sigma^2\)，且方差存在。

对于任意 \(\varepsilon>0\)，有：

\[ \boxed{ P(|X-\mu|\geq\varepsilon) \leq \frac{\sigma^2}{\varepsilon^2} } \]

也可以写成：

\[ \boxed{ P(|X-E[X]|\geq\varepsilon) \leq \frac{D(X)}{\varepsilon^2} } \]

等价的另一种形式：

\[ P(|X-\mu|\geq k\sigma)\leq \frac{1}{k^2} \]，其中 \(k>0\)。

----





#### 4.2 大数定律

---

**定理1：（切比雪夫大数定律）**

设$X_1,...X_n$为相互独立的随机变量序列，每一个$X_i$都有有限的方差，公共上界即\[DX_i\leq C\]。
对\[Y_n=\frac 1n \sum_1^n X_i\]，则有：

- \[\lim_{n\to \infty}DY_n=0\]

  > 我们已经知道上界了

- 对任意$\varepsilon >0$，\[\lim_{n\to\infty}P\{|Y_n-EY_n|<\varepsilon\}=1\]成立

  > 这个由切比雪夫不等式即得

---

**定义1：**

依次序列出的随机变量$X_1,...X_n$简记为$\{X_n\}$，称为随机变量序列$\{X_n\}$

**定义2：**

对于随机变量序列$\{X_n\}$和随机变量$X$，若对任意$\varepsilon >0$有：
$$
\lim_{n\to+\infty}P\{|X_n-X|<\varepsilon \}=1
$$
则称随机变量序列$\{X_n\}$依概率收敛于$X$，简记为$X_n\xrightarrow{P} X$

---

**推论：（辛钦大数定律）**

若随机变量$X_1,...X_n$ 为独立同分布，且期望相同，那么对任意$\varepsilon >0$，有：
$$
\lim_{n\to+\infty}P\{|\bar X - \mu|<\varepsilon\}=1 \\
(\bar X=\frac1n \sum_1^nX_i)
$$

> 切比雪夫大数定律在独立 + 有限方差条件下的推论

---

**定理2：（伯努利大数定律）**

设$n_A$是n次独立重复试验中事件A发生的次数，p是事件A在每次试验中发生的概率，对任意$\varepsilon>0$，有
$$
\lim_{n\to +\infty}P\{|\frac{n_A}n-p|<\varepsilon\}=1
$$

> 证明：
>
> （它本质就是辛钦大数定律的一种特殊情况罢了）

---

**定义3：**

设有随机变量序列$\{X_n\}$，令$Y_n=\frac1n\sum_1^nX_i$，如有$(Y_n-EY_n)\xrightarrow{P}0(n\to\infty)$，则称该随机变量序列$\{X_n\}$服从大数定律

---

**定理3：**

设随机变量序列$X_1,...,X_n$服从独立同分布，且存在有限的数学期望/方差，即：
$$
EX_i=\mu,DX_i=\sigma^2,i=1,2,...
$$
那么记$\bar X=\frac1n\sum_i^nX_i,A_2=\frac1n\sum_1^nX_i^2,S_n^2=\frac1n\sum_1^n(X_i-\bar X)^2$，则$n\to+\infty$有

1. \[\bar X\xrightarrow{P}\mu\]

   > 辛钦大数定律

2. \[A_2\xrightarrow{P}\sigma^2+\mu^2\]

   > 这个不就是方差公式吗

3. \[\bar X^2\xrightarrow{P} \mu^2\]

   > 由柯西施瓦兹不等式：
   > \[E|\bar X^2-\mu^2|\leq (E|\bar X+\mu|^2)^{\frac12}\cdot (E|\bar X-\mu|^2)^{\frac12}\]，那么很显然前者有界，后者为\[D\bar X=\frac {\sigma^2} n\]，也就趋于零

4. \[S_n^2\xrightarrow{P}\sigma^2\]

   > 没啥好说的

---



> 1. ![image-20261109101251924](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20261109101251924.png)
>
> 直接由概率收敛的定义即可：
> $$
> P\{|X_n|\geq \varepsilon\}=\int_{|x|\geq \varepsilon}f_n(x)dx=2\int_{\varepsilon}^{+\infty}\frac 1\pi \frac n{1+n^2x^2}dx=0(n\to +\infty)
> $$
> 



---



#### 4.3 中心极限定理

**定理1：（同分布的中心极限定理）**

设随机变量\[X_1,...,X_n\]独立同分布，且**存在有限的数学期望和方差**，即：
$$
EX_i=\mu,DX_i=\sigma^2\neq0
$$
记\[Y_n=\sum_i^nX_i\]，则\[EY_n=n\mu,DY_n=n\sigma^2\]

那么对\[Y_n\]进行标准化，得到\[Y_n^*=\frac{Y_n-EY_n}{\sqrt{DY_n}}=\frac{Y_n-n\mu}{\sqrt n \sigma} \]，则对任意实数x有：
$$
\lim_{n\to+\infty}F_{Y_n^*}(x)=\Phi(x)=\int_{-\infty}^x\frac 1 {\sqrt{2\pi}}e^{-\frac {t^2}2}dt
$$
并且有\[\{F_{Y_n^*}(x)\}\]在实轴上一致收敛于\[\Phi(x)\]

> 也就是说，当n充分大时，随机变量\[\frac {\sum_1^nX_i-n\mu}{\sqrt n \sigma}\]近似服从标准正态分布$N(0,1)$，那么自然有\[Y_n=\sum_1^nX_i\]~\[N(n\mu, n\sigma^2)\]近似服从正态分布

---

应用：

1. **正态随机数的生成：**

   > 根据前面的中心极限定理，只要我们能生成尽可能多的独立同分布的一组随机变量，满足有限的期望和方差，我们就有办法求和归一化生成一个服从正态分布的变量

   一个经典的方法就是用均匀分布\[U(0,1)\]，我们知道它的期望和方差分别为1/2和1/12

   那么就可以应用中心极限定理了：

   - 取n个服从此均匀分布的随机数，记为\[x_1,...,x_n\]
   - 计算\[y_n=\frac {\sum_1^nx_i-\frac n2}{\sqrt{\frac n {12}}}\]，那么它就近似服从\[N(0,1)\]
   - 再令\[z=\mu + \sigma y_n\]，那么它就服从\[N(\mu, \sigma_2)\]了！

2. **误差分析：**

---

**定理2：（棣莫佛-拉普拉斯定理）**

对\[X\]~\[B(n,p)\]，而$\mu_n$是n次独立重复试验中事件A发生的次数，则对任意区间$[a,b]$，有
$$
\lim_{n\to +\infty}P\{a<\frac{\mu_n-np}{\sqrt{np(1-p)}}\leq b\}=\Phi(b)-\Phi(a)
$$

> 利用定理1







### 五 统计总体与样本

#### 5.1 总体和样本

总体是随机随机变量$X$取值的集合

每一个$x_i$都可以视为随机变量$X_i$所取的观察值。将$X_i$称为总体X的**样本**，样本中个体的数目$n$为**样本容量**，\[x_1,...,x_n\]就是样本\[X_1,...,X_n\]的一组观察值，称为**样本值**

由于每次抽取都是独立重复的（我们认为如此），所以\[X_1,...,X_n\]是相互独立的随机变量

---

**简单随机抽样**，需要满足：

1. 独立性：\[X_1,...,X_n\]是相互独立的随机变量
2. 代表性：样本与总体$X$有相同的分布



已知分布函数：\[F_{X_i}(x_i)=P\{X_i<x_i\}=P\{X<x_i\}=F(x_i)\]，故联合分布函数即为：
$$
F(x_1,...,x_n)=\prod_{i=1}^{n}F(x_i)
$$

#### 5.2 样本矩和统计量

**只要总体的k阶矩存在，样本k阶矩依概率收敛于总体的k阶矩，样本矩是总体矩的无偏估计**

以及定义依旧是：

\[ \boxed{A_k=\frac1n\sum_{i=1}^nX_i^k} \]	\[ \boxed{B_k=\frac1n\sum_{i=1}^n(X_i-\overline X)^k} \]



样本均值的性质：
$$
\sum_{i=1}^n(X_i-c)^2=\sum_{i=1}^n(X_i-\bar X)^2 + \sum_{i=1}^n(\bar X-c)^2+2(\bar X-c)\sum_{i=1}^n(X_i-\bar X)\\\geq\sum_{i=0}^n(X_i-\bar X)^2
$$
从几何上来说，实际上求均值就是向向量$1$的投影，而另一方面也很显然，它到超平面\[c_1=...=c_n\]的最短距离恰好在\[\bar X\]取到，是最小二乘意义下的最优拟合值











**估计**量的数学期望等于被**估计**参数的真实值，则称此此**估计**量为被**估计**参数的**无偏估计**

为什么无偏估计的方差是\[n-1\]？

因为一个很显然的事实：我们在估计这个$\bar X$的时候，实际上已经消耗了这批样本的一个自由度！因为我们必然能满足：\[\sum_1^nX_i-\bar X=0\]，

我想用线性代数的角度来解释是更加形象的，我们作方差其实是这样一个过程：

1. 原始样本处于n维空间，我们减去$\bar X$实际上是让向量投影到与向量$1$正交的子空间
2. 它的维数是$n-1$！
3. 我们试图计算的实际上是它的2-norm，然后做一个归一化，将总的平方偏差转化为每个自由度对应的平均平方偏差上，而这必须要用n-1，因为我们已经有了一个线性约束：$1^Td=0$

当然了，我们需要更加严谨的表述，首先需要证明为什么\[S_n^2=\frac1n\sum_1^n(X_i-\bar X)^2\]是有偏的



















## 随机过程



### 随机过程概述

#### 基本定义

**随机过程的定义：**

设 \((\Omega,\mathcal F,P)\) 是一个概率空间，\(T\) 是指标集合，\(S\) 是状态空间。随机过程是一个映射：
$$
X:T\times\Omega\rightarrow S
$$
满足适当的可测性条件。

也可以写成：\[ \{X(t),t\in T\} \]。其中，对于每一个固定的 \(t\in T\)，都有一个随机变量：\[ X(t):\Omega\rightarrow S \]，那么我们就可称之为随机过程

**样本函数：**

若对∀\[e\in \Omega\]，与之对应的$X(e,t)$是$t$的确定函数，称之为样本函数\[x(t)\]，样本函数全体称为样本函数空间

若时间离散称为随机序列，连续为随机过程

若状态离散称为离散型...

#### 概率分布

1. 一维分布

   同样，设随机过程\[X(t)\]，事件\[X(t)\leq x\]的概率：\[P[X(t)\leq x]=F_X(x)\]，称之为\[X(t)\]的一维分布函数，若其偏导存在就是一维概率密度函数\[f_X(x,t)=\frac {\partial F_X(x,t)}{\partial x}\]





#### 数字特征

1. 期望：

   设\[X(t)\]为随机过程，\[F_X(x,t)\]为其分布函数，保证：
   $$
   \int |x(t)|dF(x,t)<\infty \\
   则可定义：E[X(t)]=\int x(t)dF_X(x,t)=m_X(t)
   $$

2. 方差：
   $$
   D[X(t)]=E\{[X(t)-E[X(t)]]^2\}
   $$

3. 自相关函数：

   设\[t_1,t_2\in T\]，则定义：
   $$
   R_X(t_1,t_2)=E[X(t_1)X(t_2)]
   $$

4. 自协方差函数：
   $$
   C_X(t_1,t_2)=E\{[X(t_1)-m_x(t_1)][X(t_2)-m_X(t_2)]\}\\=R_X(t_1,t_2)-m_X(t_1)m_x(t_2)
   $$

#### 分类

##### 按统计特性区分

那就是平稳和非平稳

##### 按记忆特性

1. 纯粹随机过程

   最简单的随机过程是没有记忆的随机过程，也就是所有变量之间是相互独立的。

   \[ \boxed{ F_{X(t_1),\ldots,X(t_n)} (x_1,\ldots,x_n) = \prod_{i=1}^{n}F_X(x_i;t_i) } \]

   它的统计信息可以完全由一阶概率分布给出

   > 也就是只要知道单独的分布即可

2. 马尔可夫过程

   稍微复杂一点，它的统计信息完全包含在它的二阶概率分布函数中

### 平稳随机过程及其判定

对于两个随机过程，我们定义：

- 相互独立
  $$
  F(x,y;t_1,t_2)=F_X(x,t_1)F_Y(y,t_2) \\ F(x_1,x_2;t_1,t_2)=F_X(x_1,t_1)F_X(x_2,t_2) 
  $$

- 正交
  $$
  E[X(t_1)Y(t_2)]=0 \\ E[X(t_1)X(t_2)]=0
  $$

- 互不相关
  $$
  C_{XY}(t_1,t_2)=Cov[X(t_1),Y(t_2)]=R_{XY}(t_1,t_2)-m_X(t_1)m_Y(t_2)=0
  $$



而既然我们的随机过程是与时间相关的，那么就像在信号与系统里面一样应当想办法先研究一个简单的时不变的对象。

#### 狭义平稳随机过程的定义

设随机过程为 \(X(t)\)，如果对于任意正整数 \(n\)、任意时刻 \(t_1,t_2,\ldots,t_n\) 和任意时间平移量 \(\tau\)，随机变量组\[ (X(t_1),X(t_2),\ldots,X(t_n)) \]和\[ (X(t_1+\tau),X(t_2+\tau),\ldots,X(t_n+\tau)) \]

具有完全相同的联合概率分布，也即：

\[ \boxed{ F_{X(t_1),\ldots,X(t_n)}(x_1,\ldots,x_n) = F_{X(t_1+\tau),\ldots,X(t_n+\tau)} (x_1,\ldots,x_n) } \]

其中，对所有 \(n,t_1,\ldots,t_n,\tau\) 均成立。则称该随机过程为狭义平稳随机过程。

那么具体到相应的概率密度函数上：

- 一维：
  $$
  f_X(x,t)=f_X(x)
  $$

- 二维：
  $$
  f_X(x_1,x_2;t_1,t_2)=f_X(x_1,x_2;\tau)
  $$

而对数学特征，如果存在的话，应当满足：

- 均值
  $$
  m_X(t)=E[X(t)]=m_X
  $$
  
- 自相关函数
  $$
  R_X(t_1,t_2)=E[X(t_1)X(t_2)]=\int_{-\infty}
  $$

- 



#### 广义平稳随机过程

定义

设\[\{X(t),t\in T\}\]是一个随机过程，\[E[X^2(t)]<\infty\]，且：

- \[E[X(t)]=m_X\]为常数
- \[R(t_1,t_2)=E[X(t)X(t-\tau)]=R(\tau), \tau=t_1-t_2\]



那么既然如此，如何判定？

- 对于广义平稳，很简单，直接从定义出发判定两个条件就行了

- 对于狭义平稳，如果可以求出分布函数，那么也按定义

  如果分布函数也不知道... 那一般是让你判定它不是广义平稳的，直接一阶一阶检查过去即可





#### 平稳随机过程的自相关函数性质

- 奇偶性：
  $$
  R(\tau)=E[x(t+\tau)x(t)]=E[x(t)x(t+\tau)]=E(-\tau)
  $$

- 最大值：
  $$
  [x(t+\tau)-x(t)]^2>0\\
  \rightarrow E[x^2(t+\tau)]+E[x^2(t)]\geq 2E[x(t+\tau) x(t)]\\
  \rightarrow R_x(0) \geq R_x(\tau)
  $$
  
- 特殊值：
  $$
  \lim_{\tau\to\infty}R(\tau)=\lim_{\tau\to\infty}E[X(t)X(t-\tau)]=E[X(t)]E[X(t-\tau)]=m^2\\
  R(0)=E[X^2(t)]=m^2+\sigma^2
  $$

- 连续性：
  $$
  e
  $$

- 非负定性
- 周期性

#### 联合平稳

若随机过程$X(t),Y(t)$均平稳，相关函数满足
$$
R_{XY}(t_1,t_2)=E[X(t_1)Y(t_2)]=R_{XY}(\tau),\tau=t_1-t_2
$$
就称$X(t)$与$Y(t)$联合平稳

#### 互相关函数的性质

- 对称性
  $$
  R_{XY}(-\tau)=R_{YX}(\tau) \\
  C_{XY}(-\tau)=C_{YX}(\tau)
  $$

- 最大值（施瓦兹不等式）
  $$
  |R_{XY}(\tau)|^2\leq R_X(0)R_Y(0)\\
  |C_{XY}(-\tau)|^2\leq \sigma_X^2\sigma_Y^2
  $$

  > 证明：我们知道$E[XY]^2\leq E[X^2]E[Y^2]$，分别套一下就是了

- **如果过程$X(t),Y(t)$联合平稳，则$Z(t)=X(t)+Y(t)$为平稳随机过程**

  > 当然了我们只是证明广义平稳，首先一阶为：
  > $$
  > m_Z=EX+EY=m_X+m_Y \to 常数
  > $$
  > 而二阶的满足：
  > $$
  > R_Z(\tau)=E[Z(t)Z(t-\tau)]\\=E\{[X(t)+Y(t)][X(t-\tau)+Y(t-\tau)]\}\\=R_X(\tau)+R_Y(\tau)+R_{XY}(\tau)+R_{YX}(\tau)
  > $$
  > 显然也满足，故为平稳随机过程

#### 相关系数和相关时间

- 相关系数
  $$
  r_X(\tau)=\frac{C_X(\tau)}{C_X(0)}=\frac{R_X(\tau)-m_X^2}{\sigma_X^2}
  $$

- 相关时间
  反映信号变化的速度，或者说影响能持续的时间
  $$
  \tau_0=\int_0^\infty r_X(\tau)d\tau
  $$

> 实际上比如我们已知$r_X(\tau)=e^{-\frac{|x|}T}$，那么此时$\tau_0=T$，实际上就是那个时间常数

----

#### 例题

设随机过程X(t)=tY，式中Y是随机变量，试讨论X(t)的平稳性

> 首先显然不满足狭义平稳，$X(t)$是时变的
>
> 而宽平稳，显然$E[X(t)]=tE[Y]$，为了是常数，只能$E[Y]=0$，进而由于$D[X(t)]=t^2D[Y]$也需要为常数与t无关，推导出$D[Y]=0$。而关于自相关函数，$R_X(t_1,t_2)=t_1t_2E[Y^2]$也依赖时间。
>
> 因此，基本上可以说这个随机过程是不具有宽平稳性的

设两个平稳随机过程X(t)= cos(t+Φ)和Y(t)= sin(t+Φ) ，其中Φ 是在[0, 2π]上均匀分布的随机变量。试问这两个过程是否联合平稳？它们是否正交，不相关，统计独立？

> 首先是平稳，显然成立，因为我们作$\tau$的位移，则$\phi'=(\phi+\tau)mod2\pi$仍服从相同的均匀分布，所以$(X(t+\tau),Y(t+\tau)) \overset{d}{=} (X(t),Y(t))$满足联合严平稳
>
> 那么是否正交？$R_{XY}(t_1,t_2)=\frac12E[sin(t_1+t_2+2\phi)+sin(t_2-t_1)]=\frac12 sin(t_2-t_1)$，不正交
>
> 那是否不相关？
> $C_{XY}(t_1,t_2)=E[X(t_1)Y(t_2)]-E[X(t_1)]E[Y(t_2)]=R_{XY}(t_1,t_2)=0$，那么实际上同样不成立
>
> 是否统计独立？
>
> 显然不是，$X^2+Y^2=1$

### 时间平均和各态历经性

统计平均是做多次实验取平均，而时间平均则只是一次实验但是按时间取平均。

而显然，统计平均是很麻烦的，毕竟要多次实验，所以**各态历经性描述的就是何时统计平均和时间平均可以等价**，被定义为：
$$
\lim_{T\to +\infty}\frac 1T \int_0^TX(t)dt=E[X(t)]
$$
首先我们已经知道，平稳随机过程的任何一个样本函数的特性都能代表它的全部特性

----

##### 时间平均的均值：

$\begin{aligned} E[\overline X_T] &=E\left[\frac1T\int_0^T X(t)\,dt\right]\\ &=\frac1T\int_0^T E[X(t)]\,dt=m_X \end{aligned}$

时间平均是统计均值的一个无偏估计

##### 时间平均的方差：

根据方差定义：

\[ D[\overline X_T] =E[(\overline X_T-E[\overline X_T])^2] \]

代入积分表达式：

\[ D[\overline X_T] = \frac{1}{T^2} E\left[ \left( \int_0^T (X(t)-m_X)\,dt \right)^2 \right] \]

展开平方：

\[ D[\overline X_T] = \frac{1}{T^2} E\left[ \int_0^T\int_0^T (X(t)-m_X)(X(s)-m_X)\,dt\,ds \right] \]

交换积分与期望：

\[ D[\overline X_T] = \frac{1}{T^2} \int_0^T\int_0^T C_X(t,s)\,dt\,ds \]

其中 \(C_X(t,s)\) 是协方差函数。

对于宽平稳过程：

\[ C_X(t,s)=C_X(t-s) \]

因此：

\[ D[\overline X_T] = \frac{1}{T^2} \int_0^T\int_0^T C_X(t-s)\,dt\,ds \]

利用对称性和变量替换，得到：

\[ \boxed{ D[\overline X_T] = \frac{2}{T^2} \int_0^T(T-\tau)C_X(\tau)\,d\tau } \]

这就是平稳随机过程时间平均方差的常用公式。

如果用自相关函数表示，因为：

\[ C_X(\tau)=R_X(\tau)-m_X^2 \]

所以：

\[ \boxed{ D[\overline X_T] = \frac{2}{T^2} \int_0^T(T-\tau) [R_X(\tau)-m_X^2]\,d\tau } \]







### 平稳随机过程的功率谱密度
