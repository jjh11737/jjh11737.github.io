# 电磁场学习笔记
（期中前的暂略）

## 第五章 静磁场的位函数

**毕奥沙伐定律**：
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

虽然B-S定律是由实验推测得到的，但是实际上它的形式可以从泊松方程里面推导出来，而这就可以借助磁矢位的概念：
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

常见例题：









## 物质磁化









最终磁荷模型的B-D形式场定律为：
$$
\nabla \times H = \vec J_f + \frac {\partial}{\partial t}\vec D \\
\nabla \times \vec E = -\frac \partial {\partial t} \vec B \\
\nabla \cdot \vec D = \rho_f \\
\nabla \cdot \vec B = 0 \\
\nabla \cdot \vec J = -\frac \partial {\partial t} \rho
$$




## 电磁场能量和功率

坡印亭定理：
$$
-\nabla \cdot \vec S = p + \frac d {dt} \omega
$$



## 10章 平面电磁波

### UPW波动方程的导出

首先我们针对电磁波，这里完全可以忽略场源，仅考虑耦合，即：
$$
\nabla \times \vec E = -\frac \partial {\partial t}\mu_0 \vec H ~~(1)\\
\nabla \times \vec H = \frac {\partial}{\partial t}\varepsilon_0\vec E ~~(2)\\
\nabla \cdot \varepsilon_0\vec E = 0 \\
\nabla \cdot \mu_0 \vec H  = 0
$$
考虑一均匀平面波upw，让它的等相面是z=常数，那么由对称性，电场与x,y无关，即$\frac \partial {\partial x}=\frac \partial {\partial y}=0$，对于电场我们直接带入电场高斯，有$\varepsilon_0\vec E =  \varepsilon_0(\frac \partial {\partial z}E_z)= 0$，则z分量与z无关，再由修正安培环路$\nabla \times \vec H = \frac {\partial}{\partial t}\varepsilon_0\vec E$，可知z分类与t也无关。换句话说z分量就是一个常量，因为我们讨论的是时变场，我们认为它就是0。而磁场也是同理，即有$H_z = 0, E_z = 0$。

再由式（2）得到：
$$
\left|
\begin{array}{cccc}
    \hat i_x &  \hat i_y & \hat i_z \\
    0 & 0 & \frac \partial {\partial z} \\
    H_x & H_y & H_z
\end{array}
\right|=\hat i_x \frac {\partial \varepsilon_0 E_x}{\partial t} + \hat i_y \frac {\partial \varepsilon_0 E_y}{\partial t}
$$
同理由（2）也可以得到相同的结果
$$
\left|
\begin{array}{cccc}
    \hat i_x &  \hat i_y & \hat i_z \\
    0 & 0 & \frac \partial {\partial z} \\
    E_x & E_y & E_z
\end{array}
\right|=\hat i_x \frac {\partial \mu_0 E_x}{\partial t} + \hat i_y \frac {\partial \mu_0 E_y}{\partial t}
$$
，因此可知：
$$
\frac {\partial H_y}{\partial z}=-\varepsilon_0\frac {\partial  E_x}{\partial t} ~~(3)\\
\frac {\partial H_x}{\partial z}= \varepsilon_0\frac {\partial  E_y}{\partial t} ~~(4)\\
\frac {\partial E_x}{\partial z}= -\mu_0 \frac {\partial  H_y}{\partial t} ~~(5)\\
\frac {\partial E_y}{\partial z}= \mu_0 \frac {\partial  H_x}{\partial t}~~(6)
$$
![image-20260603160332644](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260603160332644.png)

显然它们在xy方向上是耦合的，那么我们不妨先单独讨论电场，它两边对z求导再换序，然后带入(3)：
$$
\frac {\partial^2 E_x}{\partial z^2}= -\mu_0 \frac {\partial  H_y}{\partial t \partial z} = \mu_0\varepsilon_0 \frac {\partial^2 E_x}{\partial t^2} = \frac 1 {c^2} \frac {\partial^2 E_x}{\partial t^2}
$$
同理有：
$$
\frac {\partial^2 H_y}{\partial z^2}=\frac 1 {c^2} \frac {\partial^2 H_y}{\partial t^2}
$$
它们都符合波动方程$\frac {\partial^2 u}{\partial z^2}=\frac 1 {c^2} \frac {\partial^2 u}{\partial t^2}$，它的解是一维波动方程的达朗贝尔公式：$u = f(z \pm ct)$，`-`对应+z方向的传播，`+`对应-z方向的传播。

那么我们想要推导出它们两个的关系，根据上面的式子我们可以设$E_x(z,t)=f_1(z-ct) + f_2(z-ct)$，$\zeta=z+ct,\xi = z-ct$，那么我们由(3) (5)可知，首先$\frac \partial {\partial z}E_x = f_1'(\xi) + f_2'(\zeta)$，而$\frac \partial {\partial t}E_x = -cf_1'(\xi) + cf_2'(\zeta)$
另一边对磁场，$\frac \partial {\partial z} H_y = \frac \partial {\partial \xi}H_y + \frac \partial {\partial \zeta}H_y$，$\frac \partial {\partial t} H_y = -c\frac \partial {\partial \xi}H_y + c\frac \partial {\partial \xi}H_y$。
再由(5)有：$\frac {\partial E_x}{\partial z}= -\mu_0 \frac {\partial  H_y}{\partial t} = -\mu_0(-c\frac \partial {\partial \xi}H_y + c\frac \partial {\partial \xi}H_y)$
由（3）有：$\frac {\partial H_y}{\partial z} = -\varepsilon_0 (-c f_1'(\xi) + cf_2'(\zeta)) = \frac \partial {\partial \xi}H_y + \frac \partial {\partial \zeta}H_y$ ，联立这两式即可解得：
$$
H_y = \frac 1 {\eta_0} f_1(\xi) + C(\zeta) \\
H_y = -\frac 1 {\eta_0} f_2(\zeta) + D(\xi)
$$
那么很显然就有$H_y = \frac 1 {\eta_0} (f_1(z-ct) - f_2(z+ct))$

事实上是有4组独立解：$(E_x^+ H_y^+),(E_x^- H_y^-),(E_y^+ H_x^+),(E_y^- H_x^-)$

如果$(E^+ H^+) (E^- H^-)$同时存在且大小相等，那么就是一个**纯驻波**，比如电场就是$E_me^{ja_1}e^{-\beta z}+E_me^{ja_2}e^{\beta z}=E_me^{j(a_1+a_2)/2}cos(\beta z+\frac {a_1 -a_2} 2)$它的特性是"3个90度"：

- 时间相位上：电场-磁场=90度
- 空间相位上：电场-磁场=90度
- 空间指向上：电场-磁场=90度

而**自由空间波阻抗**：$\eta_0 = \frac {|\vec E|} {|\vec H|} = \frac {\mu_0}{\eta_0} = 120\pi$

**波速**$c = \frac 1 {\sqrt{\varepsilon_0 \mu_0}}$。

波数 $\beta =\frac \omega v = \omega \sqrt{\varepsilon \mu}$

### 时谐电磁波

我们引入复振幅的概念。那么有：$\vec E = Re[\widetilde E e^{j\omega t}] = \frac 1 2(\widetilde E e^{j\omega t} + \widetilde E^* e^{-j\omega t})$

而此时自由空间场定律变成：
$$
\nabla \times \widetilde E = -j \omega \widetilde B \\ 
\nabla \times \widetilde H = \widetilde J_f-j \omega \widetilde D \\ 
\nabla \cdot \widetilde D = \dot \rho_f \\
\nabla \cdot \widetilde B = 0 \\
\nabla \cdot \widetilde J_f = -j \omega \dot \rho_f
$$
而$\beta = \omega \sqrt{\mu \varepsilon} = \frac \omega v = \frac {2\pi} \lambda$。则有：
$$
\nabla \times \nabla \times \widetilde E = -j\omega \mu \nabla \times \widetilde H = -\omega ^2 \mu \varepsilon \widetilde E = -\beta^2 \widetilde E
$$
 那么解方程就得到解为：$\widetilde E = \dot E_{m1} e^{-j\beta z} + \dot E_{m2} e^{j\beta z}$。分别是+z和-z方向传播的两列波。
而$\widetilde H = -\frac 1 {j\omega \mu}\nabla \times \widetilde E$即可求出磁场。

### 复数形式的坡印亭定理

首先关于乘积：
$$
\vec S = \vec E \times \vec H = Re(\frac 1 2 (\widetilde E e^{j\omega t}+\widetilde E^* e^{-j\omega t})) \times Re(\frac 1 2 (\widetilde H e^{j\omega t}+\widetilde H^* e^{-j\omega t})) \\
= Re[\frac 1 4 (\widetilde E\times\widetilde H^* + \widetilde E\times\widetilde H + \widetilde E\times\widetilde He^{j2\omega t}+\widetilde E^*\times\widetilde H^*e^{-j2\omega t})] \\ 
=\frac 1 2 (Re[\widetilde E \times\widetilde H^*]+Re[\widetilde E \times\widetilde H e^{j2\omega t}] )
$$
而时间的平均值就是
$$
<\vec S> = \frac 1 2 Re[\widetilde E \times \widetilde H^*]
$$
因此我们定义：
$$
\widetilde S = \frac 1 2  \widetilde E \times \widetilde H^*
$$
那么便有
$$
\nabla \cdot \widetilde S  = \frac 1 2[\widetilde H ^* \cdot \nabla \times \widetilde E - \widetilde E  \cdot \nabla \times \widetilde H^*] \\
=\frac 1 2[\widetilde H ^* \cdot (-j\omega \mu \widetilde H) - \widetilde E  \cdot (\widetilde J_f^* - j\omega \varepsilon \widetilde E^*)] \\
 = -\frac 1 2[\widetilde E \cdot \widetilde J_f^*] - j2\omega[\frac \mu 4 |\widetilde H|^2 - \frac \varepsilon 4 |\widetilde E|^2]
$$
再由$J_f = J_d + J_s$，因此有：
$$
- \nabla \cdot \widetilde S -\frac 1 2[\widetilde E \cdot \widetilde J_s^*] = \frac 1 2[\widetilde E \cdot \widetilde J_d^*] + j2\omega[\frac \mu 4 |\widetilde H|^2 - \frac \varepsilon 4 |\widetilde E|^2]
$$

$$
- \nabla \cdot \widetilde S + <p_s>+jq_s = <p_d> + j2\omega[<\omega_m> - <\omega_e>]
$$

我们把实部和虚部分开看：

- 实部：
  $$
  - \nabla \cdot \widetilde S + <p_s> = <p_d> 
  $$
  **物理意义**：**<u>电磁场向某点提供的电磁功率密度的时间平均值 + 电源向该点提供的电磁功率密度平均值  = 该点焦耳热损耗功率密度的时间平均值</u>**(即全部损耗)

- 虚部：
  $$
  jq_s = j2\omega[<\omega_m> - <\omega_e>]
  $$
  **物理意义**：电磁场向该点提供的无功功率密度 = $2\omega$（该点的磁能功率密度的时间平均值 - 电能功率密度的时间平均值）

### 平面波在有耗媒质中的传播z

**有耗媒质中，电导率$\sigma$不为0**，因此就会有**传导电流$\widetilde J_d = \sigma \widetilde E$，**代入场定律，只会改变这两条：
$$
\nabla \times \widetilde H = \sigma\widetilde E-j \omega\varepsilon \widetilde E \\ 
\nabla \cdot \varepsilon\widetilde E = \dot \rho_f = -\frac {\nabla \cdot\widetilde J}{j\omega} = -\frac {\nabla \cdot \sigma\widetilde E}{j\omega}
\to \nabla\cdot(\varepsilon + \frac \sigma {j\omega})\widetilde E
$$
那么我们就定义新的介电常数$\dot \varepsilon_r = \varepsilon + \frac \sigma {j\omega}$，此时场定律再次变为：
$$
\nabla \times \widetilde E = -j \omega \widetilde \mu H \\ 
\nabla \times \widetilde H = j \omega\dot\varepsilon \widetilde E \\ 
\nabla \cdot \dot\varepsilon\widetilde  E= 0 \\
\nabla \cdot \widetilde B = 0 \\
\nabla \cdot \widetilde J = -j \omega \dot \rho
$$
对于波数来说，由于第2个方程改变，变为了$k^2 = \omega^2\dot\varepsilon\mu\to k = \beta +j\alpha$，波阻抗也变为了$\dot \eta = \sqrt{\frac \mu {\dot\varepsilon}}$。

当然解的形式还是不变的。

而又因为$k^2 = \omega^2(\varepsilon + \frac {\sigma}{j\omega})\mu= \beta^2 +2j\alpha\beta -\alpha^2$，那么我们就可以解得：



![image-20260605130107265](https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260605130107265.png)

#### $\alpha$的分布

而我们更关心的是这个波会如何衰减，也就是$\alpha$
而我们知道：$(\sqrt{1+x^2} - 1)^{\frac 1 2} = \frac x {\sqrt{1+ \sqrt{1+x^2}}}$
那么此时就有

1. x的分布：
   - $x\to 0$，有$f \to x / \sqrt 2$
   - $x\to \infty$，有$f \to \sqrt x$
2. $\omega$的分布：我们根据上面的推导令$x=\frac \sigma {\omega \varepsilon_0 \varepsilon_r}$}
   - $\omega \to 0$，有$x \to \infty, \alpha \to \sqrt{\omega^2 \mu_0 \varepsilon_0} \sqrt{\frac {\mu_r \varepsilon_r}{2}}\sqrt{\frac \sigma {\omega \varepsilon_0 \varepsilon_r}}=\sqrt{\frac {\omega \sigma \mu} 2} \to 0$
   - $\omega \to \infty$，有$x \to 0,  \alpha \to \sqrt{\omega^2 \mu_0 \varepsilon_0} \sqrt{\frac {\mu_r \varepsilon_r}{2}}\frac \sigma {\omega \varepsilon_0 \varepsilon_r} / \sqrt 2=\frac {\eta_0} 2 \sigma \sqrt{\frac {\mu_r}{\varepsilon_r}} = 60\pi\sigma \sqrt{\frac {\mu_r}{\varepsilon_r}}$

#### 良导体

对于良导体，$\sigma >> \omega \varepsilon$，传导电流远大于位移电流，$x \to \infty$，则此时$\alpha = \beta = \sqrt{\frac {\omega \sigma \mu}{2}}$，此时的解就是$\widetilde E = \hat i_x \dot E_0 e^{-\alpha z} e^{-j\beta z }$

显然由于此时$\alpha$非常大，所有进入良导体的电磁波将会很快地衰减，我们定义衰减为原来幅度的1/e时为**趋肤深度**:$\delta = \sqrt{\frac 2 {\omega \sigma \mu}}$

同时此时的波阻抗：$\dot \eta = \sqrt {\frac \mu {\dot \varepsilon}} = \sqrt {\frac \mu {\varepsilon + \frac \sigma {j\omega}}}  \approx \sqrt{\frac {\mu \omega}{\sigma}}\sqrt{j} = \sqrt{\frac \mu \sigma}\frac {\sqrt 2}{\delta \sqrt{\sigma \mu}}e^{j\frac \pi 4} = \frac 1 {\sigma \delta}(1+j) = R_s (1+j)$，$R_s=\sqrt{\frac {\omega \mu}{2\sigma}}$是良导体的**表面电阻**，而且显然$R_s = \sqrt {\frac {2 \mu}{\delta^2\sigma\mu}} << \sqrt {\frac \mu \varepsilon} = \eta$，**<u>电场的传导电流削弱了原电场，因此良导体中磁场的作用远大于电场</u>**

### 相速度 群速度

**相速度**：相位，$v_p = \frac {\omega}{\beta}$
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260605131554027.png" alt="image-20260605131554027" style="zoom:50%;" />

**群速度**：波包的传播速度
$v_g = \frac {d\omega}{d\beta}$

关系：真空中$v_g v_p = c^2$.



### 电磁波的极化

不同于物质的极化，它代表：<u>**电场矢量末端随时间变化在空间描述的轨迹**</u>

性质：

- 任何一个椭圆极化波都可以被分解为2个正交的线极化波
- 一个圆极化波无法被分解为一对左旋和右旋极化波（他们正交）

#### 判定方法：

具体来说就是把复振幅拆分为实部和虚部，然后四指从虚部向量指向实部向量，同时大拇指匹配传播方向，符合左手就是左旋，右手就是右旋

- 线极化波：$E_I=0 / E_R =0 / \vec E_I = \alpha \vec E_R(linear)$
- 圆极化波：$|E_I| = |E_R|$ 且相互垂直
- 椭圆极化：其他情况 

### 沿任意方向传播的UPW

其实没有本质区别，就是我们要改变一下：$e^{j\beta z} \to e^{j \vec k \cdot \vec r}$，此时仍然有$\widetilde H = \frac 1 \eta\vec i_k \times \widetilde E$。（其他部分没区别）

以及实际上更普遍性的可能还是$\vec H = \frac {-1}{j\omega \mu} \nabla \times \vec E$

## 11章 平面波的反射和折射

这里我们可以定义第三种极化，即**垂直极化**（线极化波的电场方向与入射面垂直）和**水平极化**（线极化波的电场方向与入射面平行），而任意波都可以被这样正交分解

**Snell 定律**：

- 入射面和折射线都在入射面内
- 反射角=入射角
- $\frac {sin \theta_\tau}{sin \theta_i} = \frac {n_i}{n_\tau} ，n=\sqrt{\mu_r\varepsilon_r}$

推导：



### 1. 自由空间与理想导体分界面的反射与折射

#### 垂直入射

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260605124114051.png" alt="image-20260605124114051" style="zoom:67%;" />

则显然有：$\vec \beta_i = \hat i_z \beta_0，\vec \beta_r = -\hat i_z \beta_0$，即反射场和入射反向，那么为了方便起见我们先假设这里反射波为$\dot E_{r0}$，那么自然我们就知道入射和反射场的形式：
$$
\widetilde E_i = \hat i_x \dot E_{i0}e^{-j\beta_0z} \\
  \widetilde H_i = \hat i_y \frac {\dot E_{i0}}{\eta_0}e^{-j\beta_0z} \\
  \widetilde E_r = \hat i_x \dot E_{r0}e^{j\beta_0z} \\
   \widetilde H_e = -\hat i_y \frac {\dot E_{r0}}{\eta_0}e^{j\beta_0z}
$$
之后我们就可以由边界条件：
$$
\hat i_n \times(\widetilde E_1 - \widetilde E_2)|_{\Sigma} = 0 \\
\to \widetilde E_1 = \widetilde E_i + \widetilde E_r \\
\to \widetilde E_2 = \widetilde E_\tau = 0 \\
\hat i_n = -\hat i_z
$$

$$
\to \widetilde E_i = -\widetilde E_r \\
\to \dot E_{i0} = -\dot E_{r0}
$$

那么很显然，这里形成的就是一个**纯驻波**：
$$
\widetilde E = \widetilde E_i + \widetilde E_r = \hat i_x (\dot E_{i0}e^{-j\beta_0z} - \dot E_{i0}e^{j\beta_0z}) = -\hat i_x j2 \dot E_{i0}sin\beta_0 z \\
\widetilde H = \widetilde H_i + \widetilde H_r = \frac 1 {\eta_0}\hat i_y (\dot E_{i0}e^{-j\beta_0z} + \dot E_{i0}e^{j\beta_0z})  = \hat i_y 2 \frac {\dot E_{i0}}{\eta_0}cos \beta_0 z
$$
同时此时在理想导体表面z=0，应该由面电流$\widetilde K = \hat i_n \times (\widetilde H_1 - \widetilde H_2)|_{z=0} =-\hat i_z \times (\widetilde H_i - \widetilde H_r) = \hat i_z \frac {2\dot E_{i0}} {\eta_0}$

再考虑它的电磁功率传输，即坡印亭矢量为：
$$
\widetilde S = \widetilde E \times \widetilde H^* = \hat i_z \frac 1 2(\dot E_{i0}e^{-j\beta_0z} - \dot E_{i0}e^{j\beta_0z})\frac 1 {\eta_0}(\dot E_{i0}^*e^{j\beta_0z} + \dot E_{i0}^*e^{-j\beta_0z}) = -j\hat i_z \frac 1 {\eta_0} |\dot E_{i0}|^2sin(2\beta_0 z)
$$

显然它在空间上的平均值为0，换句话说纯驻波并没有传递能量，只有能量的交换

#### 斜入射

分析起来其实并不复杂，我们只需要分开考虑切向和法向分量即可

##### 垂直极化

即电场方向垂直于我们的入射面，此时性质完全不一样，法向形成驻波，而切向则是行波，相当于电磁波仅仅在沿着导体方向前进。

分析：
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260609111943060.png" alt="image-20260609111943060" style="zoom:50%;" />

首先我们明确一下模型，我们现在条件有：
$$
\widetilde E_1 = \widetilde E_i + \widetilde E_r \\ 
\widetilde E_2 = 0 = \widetilde E_\tau \\
\vec i_n = -\vec i_z \\
\widetilde E_i = \hat i_y \dot E_{i0} e^{-j\beta_0 (xsin\theta_i+zcos\theta_i)} \\
\widetilde E_r = \hat i_y \dot E_{r0} e^{-j\beta_0 (xsin\theta_i-zcos\theta_i)}
$$
我们有边界条件：切向：$\hat i_n \times (\vec E_1 - \vec E_2) |_{z=0}= 0 \to \vec E_1  =0$，那么就可以推导有：$E_{i0} = -E_{r0}$

合成波就是：$\widetilde E = -2j\hat i_y \dot E_{i0}e^{-j\beta_0 xsin\theta}sin(\beta_0 z cos\theta)$，$\widetilde H = -\frac {2\dot E_0}{\eta_0}e^{-j\beta_x x}(\hat i_x cos\theta cos \beta_z z + j\hat i_y sin\theta sin \beta_z z)$

- 在z=常数的平面上是等幅度的，按照$e^{-j\beta_0xsin\theta}$分布，是非均匀平面波
- 在x=常数的平面上是等相位的，是纯驻波
- 是一个导行波，在x方向上传播，在z方向上为驻波，相当于贴着边界表面在传播
- 而传播方向的相速度：$\omega t - \beta_x x\to v_p = \frac \omega { \beta_0 sin\theta} > c$，相速度仅仅是视在速度，它不传递信息和能量
  <img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260609120040448.png" alt="image-20260609120040448" style="zoom:50%;" />
  具体来说，波本身的速度是从$A\to C$，而我们的相速度$v_p = \frac c {sin\theta}$是从$B\to C$，群速度$v_g=c sin\theta$是从$B\to C$，因此我们得到$v_g v_p = c^2$
- 虚拟电壁：我们正是利用导行波在理想导体表面的性质，由于垂直方向上是驻波，我们在波节的地方刚好就是电场强度恒为0（而具体实现的时候我们实际上就是要在中间制造一个确定的波节）
- 能流密度：$\widetilde S = \widetilde E \times \widetilde H^* = \frac {|E_{i0}|^2}{\eta_0}(-j\hat i_z cos\theta sin2\beta_z z +\hat i_x 2sin\theta sin^2\beta_z z)$ 
  它在z方向均值为0，没有能量，但是在x方向上是有能量传输的

##### 平行极化

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260609134813076.png" alt="image-20260609134813076" style="zoom:50%;" />

同样我们首先明确：
$$
\widetilde E_i = \dot E_{i0}(\hat i_xcos\theta -\hat i_y sin\theta )e^{-j(\beta_x x+\beta_z z)} \\
\widetilde H_i = \hat i_y \frac {E_{i0}}{\eta_0}e^{-j(\beta_x x +\beta_z z)} \\
\widetilde E_r = \dot E_{r0}(-\hat i_xcos\theta -\hat i_y sin\theta )e^{-j(\beta_x x-\beta_z z)}  \\
\widetilde H_r = \hat i_y \frac {E_{r0}}{\eta_0}e^{-j(\beta_x x -\beta_z z)} 
$$
那么首先由切向边界条件：$\dot E_{i0} = \dot E_{r0}$，那么就都求出来了



### 2. 理想介质分界面的折射

首先显然影响的只有我们的波数，$\beta = \beta_0 \sqrt{\mu_r \varepsilon_r}$

#### 垂直入射

<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260609141913329.png" alt="image-20260609141913329" style="zoom:50%;" />

我们要考虑的只有3列波，入射/反射/透射：
$$
E_i = \hat i_x\dot E_{i0}e^{-j\beta_1 z} \\
H_i = \hat i_y \frac {\dot E_{i0}}{\eta_0}e^{-j\beta_1 z} \\
E_r = \hat i_x \dot E_{r0}e^{j\beta_1 z} \\
H_r = -\hat i_y \frac {\dot E_{r0}}{\eta_0}e^{-j\beta_1 z} \\
E_\tau = \hat i_x \dot E_{\tau 0}e^{-j\beta_2 z} \\
H_\tau = \hat i_y \frac {\dot E_{\tau0}}{\eta_0}e^{-j\beta_2 z} \\
$$
还是边界条件：由两个切向边界条件得到：$E_{i0} + E_{r0}=E_{\tau0}$，$H_{i0}+H_{r0}=H_{\tau0} \to \frac {E_{i0}} {\eta_1} - \frac {E_{r0}} {\eta_1}=\frac {E_{\tau0}} {\eta_2}$，因此显然有$E_{\tau0} = \frac {2\eta_2}{\eta_2 +\eta_1}E_{i0} = T E_{i0}$，$E_{r0} = \frac {\eta_2 -\eta_1}{\eta_2 + \eta_1}E_{i0}$，分别是透射$T=\frac {2\eta_2}{\eta_2+\eta_1}$和反射系数$\Gamma=\frac {\eta_2 - \eta_1}{\eta_2+\eta_1}$。它们满足菲涅耳方程（$\theta=0$）:$\Gamma+1=T$

很显然，透射波是纯行波$E_\tau = \hat i_x T\dot E_{i 0}e^{-j\beta_2 z}$，而在入射区域，形成的则是行驻波：
$$
E_{i0}e^{-j\beta_1z} + \Gamma E_{i0} e^{j\beta_1 z} = E_{i0}[(1+\Gamma)e^{-j\beta_1z} + \Gamma(e^{j\beta_1z}-e^{-j\beta_1z})]=E_{i0}[(1+\Gamma)e^{-j\beta_1z} + 2j\Gamma sin(\beta_1 z)]
$$


#### 透波/吸波现象

而实际应用的时候，我们则需要研究透波/吸波现象

##### 透波

显然我们前面已经知道，对于反射系数除非两种介质完全相同，否则一定会有部分波作为反射被损失而无法完全透波，因此我们考虑在中间加入一种介质，想办法将反射波抵消
<img src="https://raw.githubusercontent.com/jjh11737/jjh-blog-images/master/imgs/image-20260609150057728.png" alt="image-20260609150057728" style="zoom:50%;" />
形式：在1 2区域内显然都是即有正向也有反向的波（虽然我们目的是1区域内部不存在反向的波），而3区域则是纯行波，我们的目的是算出这整个系统对1区域总的反射系数，希望它是0

我们利用切向边界条件（实际上也只有切向能用）：
1 2交界处：$E_{10}^+ + E_{10}^- = E_{20}^+ +E_{20}^-$，$E_{10}^+ - E_{10}^- = \frac {\eta_1}{\eta_2} (E_{20}^+ - E_{20}^-))$
2 3交界处：$E_{2d}^+ + E_{2d}^- = E_{3d}^+$， $E_{2d}^+ - E_{2d}^- = \frac {\eta_2}{\eta_3}E_{3d}^+$

最终得到：$cos\beta_2d+j\frac {\eta_2}{\eta_3}sin\beta_2 d = j \frac {\eta_1}{\eta_2}sin\beta_2 d+\frac{\eta_1}{\eta_3}cos\beta_2d$

显然只有两种情况：

- $cos\beta_2d=0, \eta_2 = \sqrt{\eta_1 \eta_3}$，即$d = (\frac 1 4 + \frac n 2)\lambda$，天线的阻抗匹配
- $sin\beta_2d = 0,\eta_1 =\eta_3$，即$d = \frac n 2 \lambda$，两侧介质相同则这个厚度的介质等于没有，就是天线罩

#### 斜入射（不考）

这一部分我们主要是推导菲涅耳定律，





**驻波系数：**
$$
S = \frac {E_{max}}{E_{min}} = \frac {1+|\Gamma|}{1-|\Gamma|}
$$

- $|\Gamma|=1$，即完全反射时，此时$S\to \infty$，就是纯驻波
- $|\Gamma|=0$，不反射，此时$S = 1$，纯行波
- $\eta_1 >\eta_2 \implies \Gamma <0$，由于我们知道这里形成的驻波它的幅度为$1+\Gamma$，若$\Gamma =-1$此时交界恰好为波节点
- $\eta_1 < \eta_2 \implies \Gamma >0$，若$\Gamma = 1$此时交界为波腹点

**全反射：**

