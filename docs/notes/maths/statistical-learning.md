### resampling

#### jackknife

我们核心思想就是估计我们这些估计量的偏差。

具体来说，对于未知分布的总体，从中抽取样本容量为n的样本，以此统计$\theta_n$来估计总体参数$\theta$一定会产生偏差，尤其是小样本，因此我们可以从原样本切去第$i$个个体后计算的\得到的统计量为$\theta_{-i}$，一般来说，估计值和实际值会存在一个常数偏差和幂级数展开的无穷小量：
$$
E(\theta_n)=\theta + \frac a n + \frac \epsilon {n^2} ...
$$

$$
E(\theta_{-i})=\theta + \frac a {n-1} + \frac \epsilon {(n-1)^2} ...
$$

定义二者的差为切除i后的虚拟值$\theta_{-i}'$：
$$
\theta_{-i}'=n \theta_n - (n-1)\theta_{-i}
$$

$$
E(\theta_{-i}') = nE(\theta) - (n-1)E(\theta_{-i})=\theta+\frac \epsilon n + \frac \epsilon {n-1}
$$

这样，我们就巧妙地保留了$\theta$本身，剩下的则是无穷小量。
因此可以用虚拟值作为总体参数的一个无偏估计：
$$
\bar \theta'= \frac 1 n \sum_{i=1}^n \theta_{-i}' = n\theta_n - \frac{n-1}n\sum_{i=1}^n\theta_{-i}
$$
$\theta_{-i}'$的方差就是：
$$
s^2 = \frac 1 {n(n-1)} \sum_{i=1}^n(\theta_{-i}' - \bar \theta')^2 = \frac {n-1}n \sum_{i=1}^n(\theta_{-i}- \bar\theta)^2
$$
实际上在这个过程当中，我们把原先的误差降阶了，比如原来最高阶是$\frac 1 n$现在就是$\frac 1 {n^2}$

当然我们可以进一步分析它，这就需要考虑偏差和标准误

**偏差**
以总体方差$\theta=\sigma^2$，我们构造统计量$\hat \theta = \hat \sigma ^2 = \frac 1 n \sum_{i=1}^n(x_i-\hat x)^2$，我们想知道这个统计量是否无偏，就可以考虑它的偏差$bias(\hat \theta)$：
$$
bias(\hat \theta)=E(\hat\theta)-\theta
$$
如果它是0就代表无偏，但是这显然是未知数，我们只能借助$\hat {bias}(\hat \theta)$来估计，方法：

- 用$\hat E (\hat \theta)$估计$E(\hat \theta)$，即用样本均值估计期望
- 用$\hat \theta$估计$\theta$

而麻烦的就是我们只能有一个样本$X={x_1,......x_n}$，只能计算一个$\hat \theta$的值，无法得到样本均值，正因为如此，我们才需要用jackknife进行多次抽样得到多个$\hat \theta_{-i}$。
$$
\hat {bias}(\hat \theta)=\hat E(\hat \theta)-\hat \theta = \frac 1 n \sum_1^n\hat \theta_{-i} - \hat \theta = \hat \theta_{(.)} - \hat \theta
$$
虽然我们本意是看看估计量$\theta$的好坏，因此引入了bias来衡量，但是bias本身又是未知的，结果就是我们又得构造统计量来估计它即$\hat bias$，但是它也可能不好，所以又得计算它的期望：
$$
E(\hat{bias}(\hat \theta))=E(\hat \theta_{(.)} - \hat \theta) \\=E(\hat \theta_{(.)}-\theta) - E(\theta - \hat \theta) \\ = bias(\hat \theta_{(.)})-bias(\hat \theta) \\ = -\frac{\sigma^2} {n-1} - (- \frac {\sigma^2} n) \\ = - \frac 1 {n(n-1)}\sigma^2
$$
这里存在可能有些跳跃，因此需要专门证明：
$$
bias(\hat \theta) = E(\hat \sigma ^2 - \sigma^2) \\
				= E(\frac 1 n \sum_{i=1}^{n}(x_i - \bar x)^2) - \sigma^2 \\
				= - \frac 1 n \sigma^2
$$
但是它有不适用的场景，比如若统计函数不是平滑函数时，数据小的变化会带来统计量的大变化，比如极值和中值。具体来看，数据集 的中位数是 46。然而，使用 Jackknife 估计得到中位数集 (依次去掉其中一个样本，求剩下样本的中位数) 为 。因此，只有在满足原始样本平滑的条件下，Jackknife 结果才会接近 Bootstrap，否则估计结果将是有偏的。

##### jackknife与交叉验证

一般来说数据会被划分为训练集和测试集，后者用于评估。而显然我们不希望过拟合发生，所以训练集内部会进行划分，留一部分作为验证集。
交叉验证法就是把数据样本切分为更小的样本，每个子集分别作为一次验证集，其它作为训练集，其目的就是定义一个验证集在训练阶段测试模型，得出未知数据集应用于该模型的结果

###### 留一法

只使用原样本的一个作为验证集，本质和jackknife无二，当然了你也可以留更多。。

###### K折交叉验证(K-Fold)

划分为K个子集，每次选一个当作验证集

###### 蒙特卡洛交叉验证

即重复随机子抽样验证，数据集被随机划分为训练和验证两部分。缺点是试验结果因为随机性不可复制

#### Bootstrap自助法

它的基本思想：如果观测样本是从母体随机抽取的，那么它将会包含母体的全部信息，我们就可以把观测样本视为“总体”。那么既然样本是抽出来的，我们完全可以从样本中再次抽样。和前者不同：

1. 是有放回的抽样
2. 不会遇到非光滑数据时失效
3. 若统计量是线性的，这二者结果会很接近（Jackknife可以被视为是Bootstrap的线性近似），换言之它的准确程度取决于统计量与其线性展开的接近程度



#### 基于bootstrap的置信区间估计-t置信区间

我们的方法是构造出一个$t = \frac{\hat \theta - \theta}{\hat {SE}_B (\hat \theta)}$，它的几何含义就是一个信噪比，上方是估计向量和原始向量的差









### Spatial Econometrics

| 符号    | 含义                  |
| ------- | --------------------- |
| **Y**   | 想解释的东西，因变量  |
| **X**   | 影响Y的因素，解释变量 |
| $\beta$ | 因素的影响强度        |
| u       | 没观测到的误差        |
| **W**   | 反应反馈的矩阵        |

空间计量学，相比传统计量我们默认样本之间是独立的，但是这里我们则需要考虑它们之间的影响。
普通回归默认$Y_i = X_i \beta + u_i$，默认ui和样本都是独立的

因此引入权重矩阵W，它就像邻接矩阵，表示i和j有多相关。有很多种构造方式

然后就是模型，Spatial Linear Regression Models，实际上就是在$Y_i = X_i \beta + u_i$的基础上我们引入：

- spatial lag (SL，直接影响，Y之间会相互影响)：$\lambda_1 W_{1n} Y_n$
  这就意味着会有互相的反馈，有$(I-\lambda W)^-1$这个矩阵进行传播，一点变化会被广播出去
- spatial error (SE，遗漏的一些空间相关的变量)：$u_n = \lambda_2 W_{2n} u_n + v_n$
- spatial Durbin (SD，邻居的X也会对你影响)：$W_{3n}X_n^*\lambda_3$

这里：

- $X_n^*$：$X_n$排除这行本身内容
- SL更偏向global effect（因为会扩散影响）
- SD更偏向local effect

而Spatial Panel Data Models则引入了时变的因素，即：
$$
Y_{nt} = X_{nt}\beta + Z_n\gamma+\mu_n+\alpha_t 1_n+u_{nt}
$$

- $X_{nt}$：n * p 矩阵of时变的regressors
- $Z_n$：n *q 矩阵of非时变regressors
- $\mu_n$是一个n*1的向量

Spatial Dynamic Panel Data Models进一步考虑了递归的可能
$$
Y_{nt}=\rho Y_{n,t-1}+X_{nt}\beta+Z_n\gamma+\mu_n+\alpha_t1_n+u_{nt}
$$
但是他会导致初值问题和incidential parameter problem

而关于这个权重矩阵$W_n=\{w_{ij}\}$是一个n^2的矩阵衡量的是空间单元的连通性，最终$w_{ii}=0$且$W_N$是行标准化的

![image-20260526111041837](/images/image-20260526111041837.png)

MLE
