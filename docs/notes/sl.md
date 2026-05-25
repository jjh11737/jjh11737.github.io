## resampling

#### jackknife

我们核心思想就是降低估计的偏差。

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


#### 基于bootstrap的置信区间估计-t置信区间
我们的方法是构造出一个$t = \frac{\hat \theta - \theta}{\hat {SE}_B (\hat \theta)}$，它的几何含义就是一个信噪比，上方是估计向量和原始向量的差
