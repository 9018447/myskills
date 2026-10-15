# Chapter 9: 神经网络在化工中的应用

## Core Idea
神经网络是"理论化的人脑神经网络的数学模型"，描述网络输入和输出之间的一种函数关系：网络结构与传递函数决定关系形式，权值和阀值（bias）就是待估计的未知参数，"调节权值和阀值"实际上也是利用最优化方法——与第7章常规参数估计同源，但神经网络"虽然缺乏内在的物理意义，但通用性很广"，可作黑箱模型模拟难以建立机理模型的复杂过程，且天然支持多响应建模。

## Frameworks Introduced
- **线性神经网络（Madaline 网络）**: "由一个或多个线性神经元组成"，传递函数 purelin()，"线性神经网络的输出可以取任意值，因此，线性神经网络常用作多层神经网络的最后一层"；采用 Widrow-Hoff 学习规则或 LMS 算法
  - When to use: 线性拟合、（自适应）信号预测
  - How: 若输入/目标向量已知可直接设计——`net = newlind(P,T)` 一步算出权值阀值，无需训练；或 `newlin(PR,S,ID,LR)` 创建（PR: R×2 最小最大矩阵；ID: 输入延迟向量默认[0]；LR: 学习速率默认0.01）后用 train()/adapt() 训练；学习率用 `maxlinlr(P)` 求最大合适值
- **BP 神经网络（反向传播前向网络）**: "第1层用sigmoid型传递函数，第2层用线性传递函数，经过训练后能够很好的逼近任意函数"
  - When to use: 函数逼近（非线性黑箱建模）；训练过程四步："（1）汇集数据；（2）创建网络对象；（3）训练网络；（4）仿真网络对新输入的响应"
  - How: `net = newff(PR,[S1...SNl],{TF1...TFNl},BTF,BLF,PF)`；TF 默认 'tansig'，BTF 默认 'trainlm'，BLF 默认 'learngdm'，PF 默认 'mse'；训练 `net = train(net, P, T)`，仿真 `y = sim(net, p)`
- **径向基神经网络（RBN）**: "可能比标准的前向网络需要更多的神经元，但其所需的训练时间只相当于FFBN的一小部分。当有许多训练向量时，RBN工作得很好"；径向基神经元输入为"输入向量 p 与权值向量 w 的距离乘以阀值 b"
  - When to use: 训练向量多、要求快速完成函数逼近
  - How: `net = newrb(P,T,goal,spread,MN,DF)`（goal: 残差平方均值指标默认0.0；spread: 分布常数默认1.0；MN: 最大神经元数默认Q；DF默认25）；`newrbe(P,T)` 设计零误差精确网络
- **GRNN（普遍化回归神经网络）**: RBN 的变种，结构类似仅第二层不同——nprod 框（normprod）输出"a¹ 的所有元素加和进行归一化"的点乘结果；"前者（GRNN）可用于函数逼近"，PNN（或然神经网络）用于分类
  - How: `net = newgrnn(P,T,spread)`；注意 spread 权衡——"a smaller spread would fit data better but be less smooth"
- **nntool GUI**: 网络/数据管理器，功能为"建立神经网络；将数据输入至 GUI 中；对网络进行初始化、训练和模拟；将训练结果从 GUI 输出至命令行工作环境中"
  - How: 命令行执行 `nntool`；[New Data]→[New Network]→[Train]→[Simulate]→[Export]；"nntool 求解思路，与命令行函数编程求解思路是完全一样的"

## Key Concepts
- **神经元模型**: 单输入单输出系统 $a=f(n)=f(wp+b)$；向量输入时 $a=f(\mathbf{Wp}+b)$；"阀很像一个权，只是其输入恒定为 1"
- **传递函数**: purelin: $f(n)=n$；logsig: $f(n)=1/(1+e^{-n})$；tansig: $f(n)=2/(1+e^{-2n})-1$；radbas: $f(n)=e^{-n^2}$（高斯）
- **网络训练**: 通过调节参数 w 和 b"以达到所希望的目标（如网络计算输出值与实验结果之间的残差平方和最小）"
- **输入权 vs 层权**: "与输入相连的权称为输入权（input weights），而把层与层之间的连接权称为层权（layer weights）"，记号 $\mathbf{IW}^{1,1}$、$\mathbf{LW}^{3,2}$（上标=目标,源）
- **输出层与隐含层**: "最后产生网络输出的那层称为输出层（以 y 表示），而所有其他层称为隐含层"
- **Widrow-Hoff 学习规则**: `e = t - a; [dw, db] = learnwh(p, e, lr)`；"当 lr 过大时，学习过程将变得不稳定，且误差将会加大"
- **自适应滤波（TDL）**: Tapped Delay Line 抽头延迟线 + `adapt()` 在线修正权值阀值，"对时变信号序列进行预测"
- **delays（输入延迟向量）**: 时序预测用过去值构造延迟输入，如 `delays = [1 2 3 4 5]`（用过去五个目标值预测下一个）
- **spread**: 径向基函数分布常数，控制基函数宽度
- **数学符号↔MATLAB 代码**: 上标→单元数组下标（$p^1\to p\{1\}$）；下标→圆括号下标（$p_2\to p(2)$，$p_2^1\to p\{1\}(2)$）；圆括号下标→第2个单元数组下标（$p^1(k-1)\to p(1,k-1)$）；如 $\mathbf{IW}^{1,1}\to$ `net.IW{1,1}`

## Mental Models
- **Use newlind when 问题本质是线性**: 输入/目标已知时一步直接设计出最优权值阀值（用 errsurf/plotes 画误差曲面可直观看到最低点），无需迭代训练。
- **Use adapt（而非 train）when 信号时变**: 时变序列在线预测——newlin 设置 delays 和 lr，adapt 逐样本在线修正权值，网络"对信号在过去和将来时刻的值的变化及时作出反应"（例9-3 中第 4 秒频率突然加倍仍能跟踪）。
- **Use 两层结构（tansig 隐层 + purelin 输出层）when 逼近任意非线性函数**: 这是 BP 网络的标准配置；trainlm 最快但耗内存。
- **Use RBN when 求快、数据多**: "所需的训练时间只相当于FFBN的一小部分"；GRNN 用 newgrnn 一行完成回归型逼近。
- **Use 神经网络 when 机理建模困难**: "由于神经网络具有并行性和高度非线性等特点，因此它常常作为一种黑箱模型，用来模拟难于用机理模型建立的复杂过程"。

## Anti-patterns
- **BP 输出层用 sigmoid**: "如果 BP 多层网络的最后一层是 sigmoid 型神经元，那么网络的输出将限制在一个很小的范围内"——要输出任意值，最后一层必须 purelin
- **学习率 lr 取得过大**: "学习过程将变得不稳定，且误差将会加大"——先用 maxlinlr() 求合适学习率
- **trainlm 报 out-of-memory 后放弃**: 作者给出三条出路：①设 `net.trainParam.mem_reduc = 2` 或更大（减慢速度换内存）；②改 trainbfg()（较慢但内存效率高）；③改 trainrp()（更慢、更省）
- **把神经网络当机理解释工具**: "常规数学模型具有明显的物理意义……而神经网络……缺乏内在的物理意义"；且常规模型化"通常必须为每一个响应分别建立一个独立模型"，神经网络才支持多响应
- **spread 盲目取值**: spread 小拟合好但欠光滑，需在拟合精度与平滑性间权衡（例9-6 注释明言）

## Code Examples

```matlab
function xNewff
clear all; clc
% 输入样本 p 和目标 t
p = -1:.1:1;
t = [-.9602 -.5770 -.0729 .3771 .6405 .6600 .4609 ...
.1336 -.2013 -.4344 -.5000 -.3930 -.1647 .0988 ...
.3072 .3960 .3449 .1816 -.0312 -.2189 -.3201];
net = newff([-1 1], [10 1], {'tansig' 'purelin'}, 'trainlm');
% 对前向网络进行仿真，并将网络输出值对目标值作图
y = sim(net, p)
plot(p, t, 'o', p, y, 'x'), title('训练向量 (训练 1 个 epoch)');
xlabel('输入向量 p'); ylabel('目标向量 t');
% Here the network is trained for 50 epochs. Again the network's output is plotted.
net.trainParam.epochs = 50; net = train(net, p, t); y = sim(net, p)
plot(p, t, 'o', p, y, '*-'), title('训练向量 (训练 50 个 epoch)');
xlabel('输入向量 p'); ylabel('目标向量 t');
```
- **What it demonstrates**: BP 函数逼近的最小完整模板——newff 创建两层网络（tansig 隐层10神经元+purelin 输出）、train 50 epochs 前后对比（程序 xNewff.m）。

```matlab
% 设置学习率为 0.1 及五个延时信号，然后用 newlin() 创建一个线性网络，
% 所得的网络将用过去五个目标值来预测下一个目标值
lr = 0.1;    delays = [1 2 3 4 5];
net = newlin(minmax(cat(2, p{:})), 1, delays, lr);
[net, y, e] = adapt(net, p, t);    % 自适应地滤波信号
```
- **What it demonstrates**: 时变信号自适应预测——delays=[1 2 3 4 5] 构造抽头延迟线输入，adapt() 在线修正权值（程序 xAdapLinPred.m）。

```matlab
function HPLC_RB
load HPLCdata
p = HPLCdata(:, 1:2)';    t = HPLCdata(:, 3)';
eg = 0.02;    % sum-squared error goal.残差平方和指标
sc = 1;    % spread constant radial basis functions.径向基函数的分布常数
net = newrb(p, t, eg, sc);
% Simulate the network response for inputs over the same range:
PF = sim(net, p),    N = 30;    C = linspace(10, 30, N);    pH = linspace(5.0, 6.0, N);
for i=1:N
    for j=1:N
    PF(i, j) = sim(net, [C(j); pH(i)])
    end
end
PFmax = max(max(PF)),    [i, j] = find(PF==PFmax),    Copt = C(j),    pHopt = pH(i)
PFopt = sim(net, [Copt; pHopt])
% And plot the results on the same graph:
surf(C,pH,PF),    xlabel('C, %');    ylabel('pH');    zlabel('PF'),    title('模拟结果');
```
- **What it demonstrates**: 化工应用完整闭环——正交实验数据→newrb 训练 RBF 网络→细网格 sim 扫描→max/find 定位最优流动相（程序 HPLC_RB.m）。

## Reference Tables

| 网络类型 | 设计/训练函数 | 传递函数 | 适用任务（作者原文表述） |
|---|---|---|---|
| 线性网络（Madaline） | newlind（直接设计）/ newlin+train | purelin | 线性拟合；"利用线性网络进行（自适应）线性预测" |
| 自适应线性网络 | newlin + adapt（delays+lr） | purelin | "对时变信号序列进行预测" |
| BP 网络 | newff + train（BTF 默认 trainlm） | 隐层 logsig/tansig，输出层 purelin | "两层 BP 网络来完成函数逼近的任务" |
| 径向基网络 RBN | newrb（goal,spread）/ newrbe（零误差） | radbas（隐层）+ 线性输出层 | "应用径向基网络来完成函数逼近任务" |
| GRNN | newgrnn(P,T,spread) | radbas + normprod | "用普遍化回归神经网络(GRNN)实现函数逼近" |
| PNN | （提及未展开） | — | "后者（PNN）可用于分类" |

| 传递函数 | 公式 | 调用 | 典型用途 |
|---|---|---|---|
| purelin | f(n)=n | `a=purelin(n)` | 线性近似；多层网络最后一层 |
| logsig | f(n)=1/(1+e⁻ⁿ) | `a=logsig(n)` | BP 隐层 |
| tansig | f(n)=2/(1+e⁻²ⁿ)−1 | `a=tansig(n)` | BP 隐层（newff 默认） |
| radbas | f(n)=e^(−n²) | `a=radbas(n)` | 径向基网络 |

## Worked Example
**例9-8（HPLC 柱流动相的神经网络模拟）**：建立酒样常规分析规程，目标是对流动相效率因子 PF 建模以寻找最合适流动相——"若它通过柱子太快，则分离效果差；若它太慢，则分析时间太长"。仅考虑流动相两个性质：乙醇浓度 Ce（经验范围 10%~30%）与酸度 pH（5.0~6.0）。
- **问题**: 两变量三水平正交实验测得 9 组（Ce, pH, PF）数据（PF 范围 2.10~7.31，存于 HPLCdata.mat）。
- **方法**: 径向基神经网络黑箱建模——`p = HPLCdata(:,1:2)'; t = HPLCdata(:,3)';`，`net = newrb(p, t, eg, sc)`，eg=0.02（残差平方和指标），sc=1（分布常数）。
- **MATLAB 要点**: Ce 在 10%~30%、pH 在 5.0~6.0 各分 N=30 等份构成 30×30 离散条件矩阵，双重循环 `PF(i,j)=sim(net,[C(j);pH(i)])`，`max(max(PF))` 配合 `find` 定位最优，surf 绘制响应曲面。
- **结果**: 最佳点 **Ce_opt = 10%，pH_opt = 5.7，最高效率因子 PFopt = 7.41**——用 9 个实验点的神经网络模型即完成流动相优化。

## Key Takeaways
1. 神经网络程序五要素（作者对例9-1/9-2 的总结）：①定义输入和目标向量；②绘制信号或用 errsurf/plotes 画误差曲面；③设计网络；④检验/测试网络性能并绘图；⑤用训练好的网络预测或模拟。
2. 线性网络能"直接设计"：newlind(P,T) 一步解出权值阀值，是与 newlin+train/adapt 迭代训练路线的本质区别。
3. 输出范围由最后一层传递函数决定：sigmoid 限幅，purelin 才能取任意值。
4. 网络选型按任务：线性→newlind/newlin；时变序列→newlin+adapt；函数逼近→newff 或 newrb/newgrnn；训练向量多求快→RBN；内存受限→trainlm 改 trainbfg/trainrp 或调 mem_reduc。
5. 化工黑箱建模闭环（例9-8）：正交实验取点→RBF 训练（eg=0.02, sc=1）→网格 sim 扫描→max/find 优化——与第8章实验设计天然衔接。
6. 读/写 MATLAB 神经网络代码的符号规则：$p^1\to p\{1\}$、$p_2\to p(2)$、$p^1(k-1)\to p(1,k-1)$、$\mathbf{IW}^{1,1}\to$ `net.IW{1,1}`。
7. 神经网络化工应用四类：①故障诊断和特征分类；②预测和优化；③时变系统的过程预测、模型化和控制；④混合使用神经网络和专家系统对复杂过程的预测与设计。

## Connects To
- **Ch 7**: 计算框架同构——神经网络训练与常规参数估计"都采用最优化方法来确定未知参数"，残差平方和最小为收敛准则；但神经网络是多响应、无物理意义的黑箱
- **Ch 8**: 例9-8 实验数据来自两变量三水平正交实验设计；nntool GUI 与 Ch5 的 PDE 工具箱 GUI 思路类比（作者明示"与 PDE 工具箱类似"）
- **Ch 3**: 神经网络函数逼近是"化工数据处理指南"（8.6 节）所列数据建模手段的最后一级，可与插值/最小二乘拟合相互印证
