# 电磁场学习笔记
（期中前的暂略）

## 第五章 静磁场的位函数

毕奥沙伐定律：
$$
d\vec H = \frac 1 {4\pi} \frac {I d\vec{s_Q} \times \hat i_{rQP}}{r_{QP}^2}
$$
而由此，闭合曲线产生的磁场就是：
$$
\vec H =  \frac 1 {4\pi}\oint_{S_Q} \frac {I d\vec{s_Q} \times \hat i_{rQP}}{r_{QP}^2}
$$
分布电流则是：
$$
\vec H = \frac 1 {4\pi} \int_{V_Q}\frac{\vec J(\vec{r_Q})\times\hat i_{r_{QP}}}{r_{QP}^2}dV_Q
$$
#### 磁矢位

虽然B-S定律是由实验推测得到的，但是实际上它的形式可以从泊松方程里面推导出来，而这就可以借助磁矢位的概念
$$
\nabla\times\vec H=\vec J
$$

$$
\nabla \cdot \mu_0\vec H = 0
$$

显然我们知道$\mu_0\vec H$是无散的，那么它就可以作为某一矢量场的旋度:$\mu_0 \vec H = \nabla\times \vec A$，同时由Helmholtz定理我们知道还需要散度确定它，因此我们就认为它的散度为0。

那么由于$\nabla \times \nabla \times \vec A = \nabla(\nabla \cdot \vec A) - \nabla^2 \vec A = -\nabla^2 \vec A = \mu_0 \vec J$，也就是说$\nabla^2 \vec A = -\mu_0 \vec J$，它显然是满足泊松方程的，$\vec A (\vec {r_P}) = \frac{\mu_0}{4\pi}\int_{V_Q}\frac{\vec  J(\vec r_Q)}{r_{QP}}dV_Q$，可见电流源产生的磁矢位与其自身方向一致

而以此推导得到毕奥沙伐方程就很容易了，由于$\mu_0 \vec H = \nabla_P \times \vec A = \frac {\mu_0}{4\pi} \nabla_P \times \int_{V_Q}\frac{\vec  J(\vec r_Q)}{r_{QP}}dV_Q$，注意到这里求旋度的是在P而非Q，因此可以换序再展开：$\vec H = \frac {\mu_0}{4\pi}  \int_{V_Q} \nabla_P \times\frac{\vec  J(\vec r_Q)}{r_{QP}}dV_Q$，然后显然由于和$r_Q$无关，再由Stokes定理，就可以得到结果了

#### 边界条件

和之前的一样，以及要注意理想导体里面我们默认$\vec H = 0$（其实可以有恒定的磁场，但是时变场趋肤深度是0，无法改变内部，而初始磁场不可能不为零，否则不符合常理，所以无论如何我们都这么认为）
$$
\hat i_n \times(\vec H_1-\vec H_2) = \vec K \\
\hat i_n \cdot (\mu_0 H_1 - \mu_0 H_2) = 0 \\
\hat i_n \cdot (\mu_0 J_1 - \mu_0 J_2) + \nabla_{\Sigma} \cdot \vec K = 0
$$
例1 有限长载流直导线在XOY平面的磁场强度：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260527210752688.png" alt="image-20260527210752688" style="zoom:67%;" />

由对称性，我们知道这里磁场强度仅仅与$r_c$有关，且只有$\hat i_\phi$分量，所以只要知道XOY平面上的磁矢位分布，就可以得知整体的分布，计算即可

例2 圆形电流环在远离环的空间的磁场

#### 静磁场的标量位

如果求解域内$\vec J = 0$，那么磁场是无旋的，满足Laplace方程（其实就跟我们静电场一样的），引入磁标位$\Phi_m$，然后像标量电位一样处理即可，有
$$
\vec H = -\nabla \times \Phi_m
$$
（注意，如果想要保证$\Phi_m$的单值性，必须是**单连通域**，而复连通每绕电流一圈就可以增加一次电流值，不再唯一。而静电场的标量位对这个就无所谓，这是不同之处）

## 物质极化

外加电场会对带电粒子产生作用，因此会产生新的分布形式的场源，那么反过来我们只需要把物质等效为对应的场源即可正常求解（宏观的电荷和电流）

### 三种极化：

- 原子极化（中性原子）：我们认为电子云没动，中心+q的电荷被外场移动了$\vec d$（尺度$\ll$原子半径），相当于一个电偶极子$\vec p$
- 取向极化（非中性原子）：定向排序
- 离子极化：正负离子被拉开，和第一种可以用相同的方法分析

为了宏观描述极化，引入：

### 极化强度

（单位体积内电偶极矩密度）：
$$
\vec P = \lim_{\Delta V\to 0}\frac {\sum_{i=1}^{n}\vec p_i}{\Delta V}
$$
具体来说，当$\Delta V$很小时，我们可以认为这个体元内部电偶极子是相等的，因此若某点正束缚电荷密度$\rho_o$，则极化强度$\vec P  = \rho_0 \vec d$
而实际上它和外加场有关，$\vec P = \chi_e \varepsilon_0 \vec E$，这里的$\chi_e$是一个张量（一般常见的也就是二阶了）

而由于我们想要把物质等效为场源，那就是等效为：

### 极化电荷

求解方法：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260527213041679.png" alt="image-20260527213041679" style="zoom:50%;" />

1. 我们约定只有正的束缚电荷是移动一个位移$\vec d$
2. 在媒质里面取一个封闭曲面S，极化时正束缚电荷被移出曲面S，内部留下等量束缚电荷，那么我们只需要求出移出来多少电荷
3. 对面元，我们和$\vec d$构成一个体元$dV$，那么这里面的电荷取负就是产生的极化负电荷：$dQ_P = -\rho_p \vec d \cdot d\vec a = \vec P \cdot d \vec a$，因此平均极化电荷密度：$\rho_P = -\frac {\oint_S \vec P \cdot d \vec a}{V}$，那么极化电荷密度就是$\rho _p = -\nabla \cdot \vec P$

### 宏观模型下的电场高斯定律：

$\nabla \cdot \varepsilon_0 \vec E = \rho = \rho_f + \rho_p$，取$\vec D = \varepsilon_0 \vec E + \vec P$即电位移矢量，则$\nabla \cdot\vec D = \rho_f$，只取决于自由电荷。

边界条件变为：
$$
\hat i_n \cdot (\vec P_2 - \vec P_1) = \eta_p \\
\hat i_n \cdot( \vec D_1 - \vec D_2) = \eta_f
$$
因此修正的安培环路定理此时变为：
$$
\nabla \times \vec H = \vec J + \frac \partial {\partial t} \vec D
$$

### 物质的极化问题

#### 1 永久极化物体：

即没有外加场但是呈现宏观的极化性，因此此时的极化强度与$\vec E$无关，不再满足$\vec P = \chi_e \varepsilon_0 \vec E$

此时只能依靠$\vec D = \varepsilon_0 \vec E + \vec P$

求解步骤：

1. 已知极化强度求等效源分布：$\vec P \to \rho_p$
2. 由等效源分布求解$\vec E$，因为它同时取决于自由电荷$\rho_f$与极化电荷$\rho_p$。





#### 2 非永久极化

我们这里同样还是仅考虑线性各向同行的简单媒质。由于非时变，介电常数必须是实数，但可以是位置的函数。而我们不能预先求出等效电荷系统，只能以来$\vec D = \varepsilon \vec E$用宏观场定律求解！
