# Chapter 2: MATLAB 编程基础

## Core Idea
MATLAB 以矩阵为基本实体、以函数为一等公民：数组是 MATLAB 语言唯一能够处理的对象类型（标量即 1×1 矩阵）；编程效率来自"向量化 + 优先调用内建/工具箱函数"，通用算法则通过"函数句柄 @fun + feval"写成 function function。程序遵循"程序定义(function) → 主程序（数据输入→计算→输出）→ 内部函数"的固定框架。

## Frameworks Introduced
- **Script 与函数（过程 procedure）的分工**: 作者原话——"在 MATLAB 中，过程主要包括函数和 Script 命令……其中，函数有返回值，而 Script 则没有"；"Script 仅仅是一连串 MATLAB 命令，它具有全局性，即一旦调用 Script 命令，Script 中的所有变量将在整个工作环境中有效"。
  - When to use: 需重复执行一连串命令且数据存取要求全局有效时用 Script（如数据 M 文件 Data_x2Dplot.m）；需要输入参数、返回结果、像内部函数一样被调用时用函数
  - How: Script 直接排列命令；函数以 `function [y1,...,yn] = FuncName(x1,...,xn)` 声明，用 nargin/nargout 检索实参个数以提高通用性
- **程序的基本框架构成**（2.10.2 节）: 作者原话——"(1) 程序的定义——在程序首行用 function 定义……(2) 主程序……一般包括数据输入（已知参数）、计算过程和结果输出（数值和图形结果）……(3) 程序的内部函数——在程序中定义的函数，只供该程序调用……一般把定义这些内部函数的代码置于主程序之后"。
  - When to use: 编写任何完整的 MATLAB 程序
  - How: 首行 `function 程序名`（不带输入输出表），主程序居中，内部函数置后；若把函数存为独立 .m 文件供多程序调用，则为外部函数
- **函数句柄 + feval 的 function function 框架**: 作者原话——"MATLAB 及其工具箱提供大量函数，通用性很强，其第一个参数一般用于传递函数句柄，在 MATLAB 中称为'function function'。因此，调用此类函数时，通常第一个参数给定 @function_name"。
  - When to use: 编写通用算法函数（求解器），或调用 fzero()、roots()、ode45() 等内建求解器
  - How: 通用函数第一个参数为 fun，内部用 `feval(fun, x1,...,xn)` 计算函数值；调用时传 `@fun`。函数句柄四大好处：传递函数给另一函数、减少函数文件个数、改善重复操作性能、保证计算可靠性
- **代码优化四原则**（2.11 节）: ①"尽量避免使用循环，而使用向量或矩阵代替"；②"在循环语句之前预先对向量、矩阵或数组初始化（预分配）"，"动态地分配向量、矩阵或数组的维数，是很浪费时间的"，用 zeros()/ones() 预分配；③"尽量使用 MATLAB 的内在函数或工具箱函数"——它们"由 C 语言直接编写……代码由专家编写，执行速度通常比较快"；④混合编程——把慢的部分（如循环）用 VC/CVF 写成 EXE、DLL/MEX 或 ActiveX 部件。
  - When to use: 程序运行速度不满足要求时按序逐级采用
  - How: 用 tic/toc 测时对比；混合编程最简单的数据通讯是磁盘文件（save data x y → !c_loop → load data）

## Key Concepts
- **数组（array）**: MATLAB 语言唯一能够处理的对象类型，标量、向量、矩阵、字符串、单元数组、结构体和对象都以数组方式存储；标量是 1×1 矩阵，向量是 1×n（或 n×1）矩阵，矩阵即二维数组
- **按列存储**: 作者原话——"与 FORTRAN 一样，所有的 MATLAB 数据按列方式存储"
- **点运算**: 元素对元素的操作运算，在操作符前用"."——点乘(.*)、点除(./)、点乘方(.^)
- **数据类型**: 字符和字符串型（char/string，16 位 Unicode，不以 NULL 结尾）、数值型（int8/16/32、uint8/16/32、single、double、稀疏矩阵）、单元数组（cell）、结构（structure）、java 类、函数句柄
- **双精度要求**: 作者原话——"MATLAB 要求所有的数学运算必须是双精度浮点运算，因此，整型必须先转换为双精度后再进行数学运算"（单精度同理）
- **稀疏矩阵（sparse）**: 含大量零元素的矩阵，MATLAB 只对非零元素进行存储和计算，用 B = sparse(A) 由满矩阵转换生成，创建后自动调用稀疏矩阵算法
- **单元数组（cell array）**: "用于保存不同类型和/或不同大小的数据"，单元下标用"{}"取内容（c = a{1,2}），celldisp 显示完整内容
- **结构（structure）**: "由一组称为域(fields)的成员变量（向量）构成，每一个域可以为不同的 MATLAB 数据类型"，如 student.name、student.entrance_exam；也可用 struct() 创建
- **全局变量与局部变量**: 默认函数内变量为局部变量；全局变量用 global 关键字定义，对整个程序的所有过程都有效
- **nargin / nargout**: 在自定义函数内检索被调用时的输入/输出变量个数，配合条件语句使函数更通用——"MATLAB 大量的内部函数也正是使用这种方法"
- **feval**: 按函数句柄/函数名计算函数值的函数，格式 feval(f, x1,...,xn)，支持多响应系统 [y1,...,yn] = feval(f, x1,...,xn)
- **符号运算（Symbolic Toolbox）**: 1993 年从加拿大滑铁卢大学购买 Maple 使用权开发而成，保留与 Maple 的接口（maple 命令，MATLAB 内嵌 Maple 5.0）；核心函数 sym/syms、vpa、subs、diff、jacobian、solve（代数方程组）、dsolve（ODE，D/D2/D3 表示微分阶次）
- **三类错误**: ①语法错误（不符合 MATLAB 语法规则）；②运行时错误（执行不能执行的操作）；③逻辑错误（程序未按预期方式执行，只有通过测试和分析结果才能检验）

## Mental Models
- **Use 向量/矩阵运算 when 写循环只是逐元素套公式**: 作者原话——"强烈建议，尽量使用向量代替 for 循环，以大大提高运算速度"（例 2-5 中 t_cycle = 0.0500 s，t_vector = 0）
- **Use @fun + feval when 编写通用求解器**: 把"算法"与"具体方程"分离——eulerpro(fun, x0, xf, y0, h) 是算法，fun 是用户方程，换方程只换 @fun
- **Use zeros() 预分配 when 循环内要往数组里写结果**: 大型矩阵尤其需要，"这样可明显地加快执行速度"
- **Use help/lookfor when 不确定函数用法**: 先 `lookfor curv` 按关键词搜索，再 `help curvefit` 看用法；函数/文件开头连续注释行即 help 文本（>>help xScript）

## Anti-patterns
- **在 Script 文件中定义函数**: 作者原话——"需要注意的是，不能在 Script 文件中定义函数，否则运行出错"。含内部函数的程序首行必须用 function 声明程序（如 xFunction.m 的"function xFunction"），"若去掉第一行……程序变成 Script M 文件……运行将出错"
- **用自定义循环函数替代内建函数**: 例 2-7 求矩阵所有元素之和，自定义双层循环 MySum 耗时 t1 = 0.2700 s，直接 sum(sum(A)) 仅 t2 = 0.0100 s——"直接使用 MATLAB 内部函数的计算速度要比自定义函数的运行速度快得多"
- **在循环内动态增长数组**: "在循环语句内，动态地分配向量、矩阵或数组的维数，是很浪费时间的"
- **多个语句挤在同一行**: "会造成程序可读性差、维护不便，所以一般单个语句单独成行"
- **不清除旧变量就写入更短的同名向量**: 得到新向量前先用 clear 清除旧向量（clear all 清除所有变量、函数以及 MEX 链接）
- **整型/单精度数据直接参与数学运算**: 必须先 double() 转换，否则运算报错

## Code Examples
```matlab
function xFunction    % An Example of using Function
clear; clc
disp('Calculating the reaction rate of ammonia synthesis')
t = input('vector of temperatures (°C) ='),    T = t + 273.15;    dH = ReactionHeat(T)
% Ploting the results
plot(T,dH,'o-'),    xlabel('T(K)'),    ylabel('-ΔH_r'),    title('Reaction rate VS temperature')
% ----
function dH = ReactionHeat(T)
% T: Temperature, K;    dH: Reaction heat (-ΔHr), kJ/kmol
dH = (10000+0.219*T-2.845e-3*T.^2+0.9703e-6*T.^3)*4.184;
```
- **What it demonstrates**: 例 2-2——程序基本框架（function 程序定义 + 主程序 + 内部函数置于主程序后），合成氨变换反应热 -ΔHr = (10000 + 0.219T - 2.845e-3T² + 0.9703e-6T³)×4.184 kJ/kmol，温度输入 210:2:230℃

```matlab
function [x, y] = eulerpro(fun, x0, xf, y0, h)
% 功能：用改进的欧拉方法计算一阶常微分方程的初值问题
% fun: 微分方程的 f(x, y) 函数句柄或函数名，x0: 积分下限，xf: 积分上限，h: 积分步长
n = fix((xf - x0)/h);    x(1) = x0;    y(1) = y0;
for i = 1:(n-1)
    x(i+1) = x0 + i*h;    y1 = y(i) + h*feval(fun, x(i), y(i));
    y2 = y(i) + h*feval(fun, x(i+1), y1);    y(i+1) = (y1 + y2)/2;
end
```
- **What it demonstrates**: 例 2-4——通用算法函数的写法：第一个参数 fun 传递方程右端 f(x,y)，内部用 feval 调用；改进欧拉法 y1 = yn + h·f(xn,yn)，y2 = yn + h·f(xn+1,y1)，y(n+1) = (y1+y2)/2，区间按 h 等分（n = fix((xf-x0)/h)）；调用例程 xEulerpro.m 中 [x, y] = eulerpro(@fun, 0, 1, 1, 0.1) 求解 y' = -y + x + 1, y(0) = 1

```matlab
clear all; clc
% 循环方法
tic    % 开始计时
x = 0.01;
for k = 1:1001, y(k) = log10(x); x = x + .01; end
t_cycle = toc    % 结束计时，并把所耗的时间赋给变量 t_cycle
% 向量化方法
tic, x = .01:.01:10; y = log10(x); t_vector = toc
```
- **What it demonstrates**: 例 2-5——向量化与循环的速度对比（t_cycle = 0.0500，t_vector = 0），以及 tic/toc 计时法

## Reference Tables
表 2-1 绘图线型、点标和颜色的字符串（plot 的 s 参数）：

| 类别 | 取值 |
|---|---|
| 颜色 | b 蓝、c 青、g 绿、k 黑、m 洋红、r 红、y 黄 |
| 点标 | . 小圆点、o 小圆圈、x x形、+ 加号、* 星号、s 方形、d 菱形、v 下三角、^ 上三角、< 左三角、> 右三角、p 五角形、h 六角形 |
| 线型 | - 实线、: 点虚线、-. 点划线、-- 长虚线 |

本章小结的常用函数速查（按功能分组）：

| 功能组 | 函数 |
|---|---|
| 工作环境与内存 | who/whos、size、length、clear all、clc、format |
| 数据输入/输出 | load、fscanf、input；save、fprintf、disp |
| 函数机制 | function 声明、nargin()/nargout()、@function_name、feval() |
| 流程控制 | if...elseif...else...end；switch...case...otherwise...end；for...end；while...end；try...catch；continue/break/pause/return |
| 通用计算 | max、min、mean、sum、sqrt、exp、log、sort（sqrt/exp/log 支持数组运算） |
| 矩阵函数 | eye、ones、zeros、rand、linspace、logspace、sparse、det、eig、inv、rank、svd、find |
| 求解器（预告第 3 章） | fsolve 解代数方程组、fzero 解单变量代数方程、ode45 积分求解常微分方程组、polyfit 多项式最小二乘拟合 |
| 符号运算 | sym、syms、vpa、subs、diff、gradient、jacobian、solve、dsolve |
| 绘图 | plot、hold on/off、text、gtext、subplot、grid、xlabel/ylabel/zlabel、title、axis、shg、clf、figure、meshgrid、mesh、surf |

## Worked Example
**例 2-4 用改进欧拉法求解一阶 ODE 初值问题**：
- **问题**: 求解 y' = -y + x + 1，y(0) = 1（区间 [0, 1]，h = 0.1）
- **模型**: 一阶常微分方程初值问题 y' = f(x, y)
- **数值方法**: 改进欧拉公式（预估-校正）：y₁ = yₙ + h·f(xₙ, yₙ)；y₂ = yₙ + h·f(xₙ₊₁, y₁)；yₙ₊₁ = (y₁ + y₂)/2；积分区间 [x0, xf] 按 h 等分，n = fix((xf - x0)/h)
- **MATLAB 要点**: 先直接编程 IntegByEulerpro.m（迭代公式硬编码），但换方程就要改代码、"比较麻烦，且容易造成错误"；于是改写成通用函数 eulerpro(fun, x0, xf, y0, h)，内部用 feval(fun, x(i), y(i)) 计算 f 值；例程 xEulerpro.m 以 [x, y] = eulerpro(@fun, 0, 1, 1, 0.1) 调用，fun 为自定义内部函数 f = -y + x + 1，最后 plot(x, y) 绘解曲线
- **结果与注记**: 作者特别注明——MATLAB 已提供许多具有自动变步长自适应功能的 ODE 积分函数（见第 3 章），本例是定步长的改进欧拉积分算法，价值在于展示 function function 通用程序的构造模式

## Key Takeaways
1. 先想向量运算，再想 for 循环：同一段计算向量化后耗时从 0.0500 s 降到 0（例 2-5）。
2. 循环前用 zeros()/ones() 预分配数组内存，动态增长是最慢的写法。
3. 能用内建函数就不自己写：例 2-7 中 sum(sum(A)) 比双层循环快 27 倍（0.0100 s 对 0.2700 s）。
4. 通用求解器的标准形态：第一个参数是函数句柄 fun，内部用 feval 调用；使用时传 @fun——这正是 fzero、fsolve、ode45 等内建函数的通用模式。
5. 含内部函数的 M 文件首行必须用 function 声明程序；Script 内定义函数会运行出错。
6. 全部数学运算必须双精度：整型、单精度先经 double() 转换。
7. 程序组织三段式：function 程序定义 → 主程序（输入→计算→输出）→ 内部函数；供多程序复用的函数存为独立外部函数文件。
8. 优化仍不够快时混合编程：慢代码（循环）用 VC/CVF 编译为 EXE/DLL/MEX，通过磁盘文件（save/!exe/load）交换数据。

## Connects To
- **Ch 1**: 落实第 1 章"拿来就用"选型——本工具箱页给出让 MATLAB 高效的语言基础
- **Ch 3 (数值分析)**: 所有数值求解函数（fzero、fsolve、ode45、polyfit 等）都是 function function，第一个参数传 @fun 的用法在本章例 2-4 建立原型
- **Ch 4-5 (常微分/偏微分方程)**: eulerpro 的定步长通用函数将被变步长自适应求解器（ode45 等）取代
- **Ch 6-7 (最优化/参数估计)**: fsolve 解代数方程组、符号微分 jacobian 将在求解非线性方程组与参数估计中反复使用
