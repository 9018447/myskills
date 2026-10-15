# Patterns — 决策规则与工作模式

> 来源：原书九章的作者方法论。格式：**When X → do Y, because Z**。

## 一、问题路由（拿到化工计算问题的第一决策）

1. **When 问题含时间演化或沿管长变化** → 建成 ODE 初值问题用 ode45（本书20+例均如此），because 化工IVP绝大多数非刚性。
2. **When 条件一部分在起点、一部分在终点（扩散-反应、速度分布）** → bvp4c+bvpinit+deval，because 作者明确放弃打靶法直接用 bvp4c。
3. **When 一维动态PDE（组）** → 优先 pdepe()（作者小结原文）；要控制格式细节才自写 Crank-Nicolson+TDMA。
4. **When 二维PDE** → 标准问题用 pdetool；≥3个方程用命令行 assempde/parabolic/pdenonlin，because pdetool 界面限2个方程。
5. **When 无时间维度的稳态系统** → 导数置零化为代数方程组用 fsolve（动态+稳态一体化：同一模型两用）。
6. **When 数据只有离散点** → 先判断插值还是拟合：数据可信→插值（spline/interp1）；数据有噪声→拟合（polyfit/spap2），because 噪声数据插值得负浓度等无意义值（例3-7）。

## 二、刚性诊断与求解器切换

7. **When ode45 长时间无输出/步长趋零/解曲线异常** → 改 ode23s，because 这是刚性方程组的典型征兆（例3-30、4-18"很久不能算出结果"、4-23）。
8. **When 强放热反应耦合传热（CSTR开车、化学热泵）** → 直接上刚性求解器，because 温度-速率指数耦合天然刚性。
9. **When 积分含奇异点的区间** → quad/quadl 而非 trapz，because trapz 对奇异积分返回 Inf。

## 三、求根与初值策略

10. **When 多项式求全部根** → roots() 而非 fzero()，because fzero 只得靠近初值的单个根。
11. **When 系统可能多稳态（带夹套CSTR）** → 循环扫初值调 fsolve，结果 sort+diff+find 去重（例3-27 得3个稳态解）。
12. **When 闪蒸/平衡计算** → 目标函数用 Σ(yᵢ−xᵢ) 单方程而非 Σx=1、Σy=1 双目标；初值须满足 Σxe<1 且落在两相区，because 初值不当会"不闪蒸"。
13. **When bvp4c 结果出现负浓度** → 改 bvpinit 初猜曲线，because 猜测值不当导致非物理解（例4-16）。
14. **When r=0 出现 (1/r)∂T/∂r 项** → 用罗必塔法则化为 ∂²T/∂r²，或对称延拓取平均过渡，because 直接计算除零（ch4/ch5）。

## 四、优化建模

15. **When 出现任何非线性约束** → fmincon 并把 c(x)/ceq(x) 打包进 @nonlcon，because SQP 是光滑NLP最有效算法；禁用 fminsearch/fminunc（例6-13 明确）。
16. **When 无约束低维问题** → fminsearch（Nelder-Mead，免导数）；单变量闭区间 → fminbnd。
17. **When 目标是平方和形式（拟合）** → lsqnonlin/lsqcurvefit，because G-N/L-M 对此类问题二次收敛。
18. **When 优化迭代发散** → 给决策变量加实际上下界/单调性约束，because 例6-16 中借此对初值不再苛刻且必收敛。
19. **When 连续系统最优控制（最优温度分布/时变政策）** → 庞特里阿金极大值原理（H、伴随方程、∂H/∂u=0）做理论分析，数值实现三解法：纯ode45 / ode45+fmincon / bvp4c+fmincon（例6-16 A/B/C）。
20. **When 建优化模型** → 先做自由度判定：决策变量数=变量总数−状态方程数，because 决策变量数为0则无优化空间（ch6）。

## 五、参数估计与模型辨识

21. **When 追求最窄参数置信区间** → 积分法（lsqnonlin 内嵌 ode45）而非微分法，because 例7-1 实测积分法区间最窄，"积分法较佳"。
22. **When 拟合非线性模型** → 线性化/regress 出初值 → lsqnonlin 精修 → nlparci 出区间，because 线性化只能当初值发生器，其统计不严格（三种线性化结果互异）。
23. **When 多响应且各响应误差不同** → 目标函数内拼 [√w₁f₁; √w₂f₂]，权重 w∝1/σ² 来自重复实验（式7-11/7-12，青霉素发酵例7-9）。
24. **When lsqnonlin 结果不理想** → 先 fmincon 求最优值再作 lsqnonlin 初值，because 前者收敛更低目标值，后者补统计区间（例7-5 串联策略）。
25. **When 速率常数跨数量级（Arrhenius）** → Kittrell变换：用平均温度重参数化，because 直接估计指数项强相关难收敛。
26. **When 筛选竞争模型** → 不能只比残差平方和：用 ρ²>0.9、F>10F_α、参数置信区间、后验概率 πᵢ 四统计量，because 例7-13 中残差最小的模型其置信区间比参数值还大且下限为负。
27. **When 判断模型适定性** → 对参数做两两灵敏度比较（例7-12），参数无法分辨则用 D-最优设计补实验（cordexch+nlinfit，例8-8）。
28. **When ode45 拟合时序数据** → 先 sort 时间点并对重复时刻插值，because ode45 不接受乱序/重复时间。
29. **When 数据点疑似异常** → 残差>3~4σ 判 outlier（概率~0.1%），检查原因后再决定去留（ch7）。

## 六、实验设计

30. **When 多因素实验** → 正交表代替简单比较法/尝试法，because 简单比较法代表性差且无法考察交互作用；例8-8 中13次实验"除非运气特别好"找不到最优，D-最优每次都能找到。
31. **When 选正交表** → 按 r=水平数、m≥因素数、n尽量小，先做自由度预算 f表≥Σf因（三水平交互占2列）（ch8）。
32. **When 交互作用平方和<空白列平方和** → 并入误差项增加误差自由度，because 该交互不显著（例8-4：Se=0.064+0.046+0.046）。
33. **When 为非线性模型精估参数选实验点** → cordexch 生成 D-最优 settings（试验次数≥参数个数）再 nlinfit，because det(X'X) 极大=置信椭球最小。

## 七、神经网络

34. **When 函数逼近非线性关系** → 两层结构：隐层 tansig + 输出层 purelin（newff），because 输出层用sigmoid会限制输出范围（ch9反模式）。
35. **When 训练样本多、求快** → newrb(goal=0.02, spread=1) 代替BP，because RBN训练时间只是FFBN的一小部分。
36. **When 小样本回归** → newgrnn（GRNN）。
37. **When 信号时变需在线预测** → newlin(delays=[1..5],lr)+adapt，because train 是离线批量训练，无法响应频率突变。
38. **When trainlm 爆内存** → mem_reduc≥2 或改 trainbfg/trainrp，不要放弃网络方案（ch9）。
39. **When 用神经网络得预测结果** → 只当黑箱预测器，不要作机理解释，because 网络权值无内在物理意义（ch9）。

## 八、MATLAB编程效率

40. **When 循环只是逐元素套公式** → 改写为向量运算（例2-5：0.05s vs 0s）。
41. **When 循环不可避免** → 循环前预分配数组，because 动态增长数组是MATLAB第一大性能杀手（例2-6）。
42. **When 自写循环函数可被内建函数替代** → 用内建函数，because 例2-7 中自定义求和0.27s vs 内建0.01s（27倍）。
43. **When 写通用数值算法** → 第一参数用 @fun 函数句柄、内部 feval 调用，because 一份算法适配任意模型方程（例2-4 eulerpro）。
44. **When MATLAB循环成瓶颈且必须提速** → CVF/VC 混合编程：MATLAB 存盘→!exe→load 读回，because Fortran/C 循环快一个量级（ch1/ch2）。
45. **When Script文件里定义函数** → 改成独立 function 文件，because Script 内定义函数运行出错（ch2反模式）。

## 通用工作流模式

**动态+稳态一体化**：同一套模型方程，动态模拟用 ode45，稳态解把导数置零交给 fsolve——避免重复建模（ch4）。
**控制器入模**：闭环控制模拟把控制律写成附加ODE（如 dEI/dt=E 积分分离），与对象方程联立求解（例4-24）。
**无因次化注意**：非标准系数（如 X=x/B 引入 (B/W)²）会破坏 pdetool/pdepe 的标准形，变换后须重新推导系数（例5-11注）。
**柱坐标伪装**：FEM工具箱解轴对称问题→变换为 −∇·x∇u=−xf(u) 标准形，c、f 用字符串表达式（ch5）。
