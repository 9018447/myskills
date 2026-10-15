# Chapter 4: Basic Equations of Fluid Flow

## Core Idea
流体力学四大衡算——连续性（质量）、线性动量、角动量、机械能——从微分形式（Navier–Stokes）与宏观壳衡算两条路线展开，最终收敛于工程师的万能工作方程：带摩擦与泵功修正的伯努利方程。

## Frameworks Introduced
- **Continuity equation（连续性方程）**：$\partial\rho/\partial t=-(\nabla\cdot\rho\mathbf V)$；不可压缩时 $\nabla\cdot\mathbf V=0$；宏观稳态形式 $\dot m=\rho_a\bar V_a S_a=\rho_b\bar V_b S_b$。Use when任何流量/流速/管径换算的第一步。
- **Navier–Stokes equations（纳维-斯托克斯方程）**：常密度常黏度的运动方程 $\rho\,D\mathbf V/Dt=-\nabla p+\mu\nabla^2\mathbf V+\rho\mathbf g$；无黏极限即 **Euler equation**。Use when需要速度分布而非平均量的精确流场（层流解析解、CFD 前提）。
- **Macroscopic momentum balance（宏观动量衡算）**：$\sum F=\dot m(\beta_b\bar V_b-\beta_a\bar V_a)$，配动量校正因子 $\beta$。Use when求流体对管件/弯头/喷嘴的作用力——伯努利解不了的问题。
- **Angular-momentum equation（角动量方程）**：$T=\dot m(r_2u_{\theta2}-r_1u_{\theta1})$。Use when泵、风机、涡轮、搅拌器的转矩与功率分析。
- **Bernoulli equation（伯努利方程）家族**：无摩擦点式 $p/\rho+gZ+u^2/2=\text{const}$（沿流线）；工程工作式 $p_a/\rho+gZ_a+\alpha_a\bar V_a^2/2+\eta W_p=p_b/\rho+gZ_b+\alpha_b\bar V_b^2/2+h_f$。Use when不可压缩流动的压降、泵功、功率计算。
- **Nusselt 液膜流（层流降膜）**：$\delta=\left(3\mu\Gamma/(\rho^2 g\cos\phi)\right)^{1/3}$。Use when壁面降膜/冷凝膜厚与液膜负荷计算。

## Key Concepts
- **Streamline / stream tube（流线/流管）**：处处与净速度矢量相切的想象线/由流线围成的无渗漏"管"；沿流线流动天然是一维的。
- **Average velocity $\bar V$（平均流速）**：$\bar V\equiv\dot m/(\rho S)=q/S$——体积通量，跨截面积分的等效均匀速度。
- **Mass velocity $G$（质量流速）**：$G\equiv\dot m/S=\rho\bar V$，kg/m²·s；稳态等截面下不随温度压力变化——可压缩流计算的首选变量。
- **Substantial derivative $D\rho/Dt$（随体导数）**：随流体微团运动的观察者看到的变量变化率，区别于定点观察的 $\partial\rho/\partial t$。
- **Momentum correction factor $\beta$（动量校正因子）**：$\beta=\frac{1}{S}\int_S(u/\bar V)^2dS$，修正截面上速度不均匀对总动量流的影响；$\beta\ge1$。
- **Kinetic energy correction factor $\alpha$（动能校正因子）**：$\alpha=\frac{1}{S}\int_S(u/\bar V)^3dS$；层流 $\alpha=2.0$、高湍流约 1.05——速度分布越平坦越接近 1。
- **Liquid loading $\Gamma$（液膜负荷）**：单位板宽的液体质量流量 $\Gamma\equiv\dot m/b$，kg/s·m。
- **Skin friction / form friction（表面摩擦/形体摩擦）**：未分离边界层内的黏性耗散 vs 分离尾流内的耗散（取决于物体位置与形状）；$h_f$ 是两者之和。
- **Pump efficiency $\eta$（泵效率）**：$\eta=(W_p-h_{fp})/W_p<1$，流体实际得到的机械能是 $\eta W_p$。
- **Fluid friction（流体摩擦）的定义**：流动中一切机械能→热的转化；沿流向 $p/\rho+u^2/2+gZ$ 恒减。
- **Couette flow（库埃特流）**：两平行板间、由动板拖动的线性速度梯度流动，$\mu=F_sB/(Av_0)$，是黏度测量的原理基础。

## Key Equations
- 连续性（圆管两截面）：$\dfrac{\rho_a\bar V_a}{\rho_b\bar V_b}=\left(\dfrac{D_b}{D_a}\right)^2$ —— $D$=管径；不可压缩时简化为 $\bar V\propto 1/D^2$。
- 微分质量衡算：$\dfrac{\partial\rho}{\partial t}=-\left[\dfrac{\partial(\rho u)}{\partial x}+\dfrac{\partial(\rho v)}{\partial y}+\dfrac{\partial(\rho w)}{\partial z}\right]=-(\nabla\cdot\rho\mathbf V)$。
- Navier–Stokes（x 分量，常 ρ、μ）：$\rho\left(\dfrac{\partial u}{\partial t}+u\dfrac{\partial u}{\partial x}+v\dfrac{\partial u}{\partial y}+w\dfrac{\partial u}{\partial z}\right)=\mu\nabla^2u-\dfrac{\partial p}{\partial x}+\rho g_x$ —— $u,v,w$=速度分量，$p$=压力，$\mu$=黏度。
- 宏观动量衡算（含壁面力与重力分量）：$\sum F=p_aS_a-p_bS_b+F_w-F_g=\dot m(\beta_b\bar V_b-\beta_a\bar V_a)$ —— $F_w$=壁面对流体的净力，压力用标量 p 乘投影面积。
- 降膜速度分布与膜厚：$u=\dfrac{\rho g\cos\phi}{2\mu}(\delta^2-r^2)$（抛物线）；$\delta=\left(\dfrac{3\mu\Gamma}{\rho^2g\cos\phi}\right)^{1/3}$ —— $\phi$=板与竖直方向夹角，$r$=离自由面的距离，$\delta$=膜厚；液膜 Re $=4\Gamma/\mu$。
- 伯努利（无摩擦，沿流线）：$\dfrac{p_a}{\rho}+gZ_a+\dfrac{u_a^2}{2}=\dfrac{p_b}{\rho}+gZ_b+\dfrac{u_b^2}{2}$ —— 各项均为"单位质量能量"；$p/\rho$ 是外力推流体进出做的功。
- 工程工作式（含 α、泵、摩擦）：$\dfrac{p_a}{\rho}+gZ_a+\dfrac{\alpha_a\bar V_a^2}{2}+\eta W_p=\dfrac{p_b}{\rho}+gZ_b+\dfrac{\alpha_b\bar V_b^2}{2}+h_f$ —— $h_f$ 恒正、只存在于 a–b 之间、与机械能项不可互逆转换；$W_p$=泵对单位质量流体的功，$\eta$=泵总效率。
- 泵功率：$P=\dot m W_p$（对泵轴）；实际传给流体 $P=\dot m\,\eta W_p$。
- 角动量：$T=\dot m(r_2u_{\theta2}-r_1u_{\theta1})$ —— $T$=转矩，$u_\theta$=切向速度分量，$r$=到转轴半径（推导假设 β₁=β₂=1）。

## Reference Tables
| 项目 | 层流 | 高湍流 | 备注 |
|---|---|---|---|
| 动能校正因子 α | 2.0 | ≈1.05 | 速度分布越平越接近 1；湍流常直接取 1 |
| 动量校正因子 β | 1.33（圆管层流） | ≈1.02–1.05 | 湍流动量衡算常取 1 |
| 降膜 Re 判据 | 层流 Re≲1200 | >1200 出现转捩 | 比管流的 2100 低；波纹使膜厚 ∝ Re^0.45 |
| 理想化取值惯例 | 大槽表面 V̄ₐ≈0、α≈1（湍流）、等高程 Za=Zb 可消项 | | 例 4.4/4.6 的简化套路 |

| 摩擦类型 | 来源 | 主导场景 |
|---|---|---|
| Skin friction | 未分离边界层内剪切做功→黏性耗散 | 平行平板流、直管充分发展段 |
| Form friction | 边界层分离、尾流涡旋耗散 | 突扩、突缩、钝体、急弯、大折角管件 |

## Worked Example
**Example 4.6（泵选型的标准三段法）**：泵从储槽（液面为 a 点）经 3 in 吸入管、60% 效率、经 2 in 管排至上方 50 ft（b 点），全系统摩擦 10 ft·lb_f/lb，ρ=1.84×62.37 lb/ft³，吸入管流速 3 ft/s。①列工作式（a 取槽面：p 相等、V̄ₐ≈0；b 取排出口：湍流 α≈1）：$\eta W_p=\frac{g}{g_c}Z_b+\frac{\bar V_b^2}{2g_c}+h_f$；②由连续性 $\bar V_b=3\times(0.0513/0.0233)=6.61$ ft/s，代入得 $W_p=60.68/0.60=101.1$ ft·lb_f/lb；③泵两端单独写式 (4.65)（Za=Zb）得泵压 $p_b-p_a=4.79\times10^4$ Pa≈47.9 psi；功率 $P=\dot m W_p/550=3.25$ hp（轴），传给流体 1.95 hp。要义：选两点消掉最多的未知项；泵本身两端单独衡算求压差；轴功率与流体功率差一个 η。

## Anti-patterns
- **用平均流速直接算动能/动量而不做校正**：$\dot E_k/\dot m=\int u^3dS/(2\bar VS)\ne\bar V^2/2$；层流差一倍（α=2），粗算湍流可取 1 但层流必须带 α。
- **伯努利方程到处乱套**：a、b 必须取在同一流线上（或截面速度较均匀处），且无泵、无摩擦项时要确认假设成立；带摩擦的完整式只能由能量（非动量）导出。
- **动量衡算漏力项**：∑F 必须收齐流向压力（p×投影面积——压力是标量！）、壁面力、重力分量；弯管受力问题先画受力图再代式 (4.42)。
- **h_f 当成"损失后可回收"**：摩擦生热不可逆，机械能与热不互转——h_f 永远是扣减项、恒正。
- **降膜用管流判据**：液膜转捩 Re≈1200（非 2100），且波纹使 Nusselt 膜厚式在 Re>1000 偏薄/偏厚偏离；膜厚随流量约 1/3 次方（层流）而实测约 0.45 次方。
- **质量流速与平均流速混用**：可压缩流中 V̄ 与 ρ 都随 T、p 变，唯独 G=ṁ/S 稳态等截面下不变；写能量/动量衡算时分子量纲要配对检查。

## Key Takeaways
- 四大衡算共享同一骨架：输入−输出=积累；微分式解分布、壳衡算解两端——先问自己要"场"还是"端值"。
- 连续性先行：任何流动问题第一步用 $\dot m=\rho\bar VS$ 把未知流速/管径互相消元，圆管 $\bar V\propto1/D^2$。
- G=ρV̄ 是可压缩流的"不变量"语言——Ch. 6 气体管流的推导全程用 G。
- 伯努利是"机械能记账"：p/ρ、gZ、V̄²/2 三种户头互转，h_f 是单行道的手续费，ηW_p 是泵注入的新资金。
- 动量衡算管"力"，能量衡算管"功"：管件受力用动量（含 β），泵功/压降用能量（含 α），两套校正因子不要互换。
- 降膜厚度 Nusselt 式是冷凝传热（Ch. 13）的基石；Re=4Γ/μ 的定义与管流不同，别混用。

## Connects To
- **Ch. 3**：α、β 由本章正式定义，其数值来自 Ch. 3 的速度分布；湍流总剪应力 (μ+E_v)du/dy 进入微分动量衡算。
- **Ch. 5**：h_f 在直管中展开为 Fanning 摩擦因数 × 动能头；α=2（层流）与 Poiseuille 解在此对接。
- **Ch. 8/9**：角动量方程 T=ṁ(r₂u_θ2−r₁u_θ1) 是离心泵与搅拌器叶轮理论的核心。
- **Ch. 6**：质量流速 G 的不变性使可压缩管流方程组可解。
- **Ch. 13**：Nusselt 降膜理论直接用于竖壁膜状冷凝传热系数。
