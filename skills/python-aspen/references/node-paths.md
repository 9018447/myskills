# Aspen 常用节点路径速查表

## 流股 (Streams)

### 输入参数设置
```python
# 总流量
\Data\Streams\<name>\Input\TOTFLOW\MIXED

# 温度
\Data\Streams\<name>\Input\TEMP\MIXED

# 压力
\Data\Streams\<name>\Input\PRES\MIXED

# 组分摩尔分数（求和应为 1）
\Data\Streams\<name>\Input\FRAC\MIXED\<Component>
# 示例：\Data\Streams\FEED\Input\FRAC\MIXED\WATER

# 组分质量流量
\Data\Streams\<name>\Input\MASSFLOW\MIXED\<Component>

# 组分摩尔流量
\Data\Streams\<name>\Input\MOLEFLOW\MIXED\<Component>
```

### 输出结果读取
```python
# 总质量流量
\Data\Streams\<name>\Output\MASSFLMX\MIXED

# 总摩尔流量
\Data\Streams\<name>\Output\MOLEFLOW\MIXED

# 总体积流量
\Data\Streams\<name>\Output\VOLFLMX\MIXED

# 温度
\Data\Streams\<name>\Output\TEMP\MIXED

# 压力
\Data\Streams\<name>\Output\PRES\MIXED

# 气相分率
\Data\Streams\<name>\Output\VFRAC\MIXED

# 组分摩尔流量
\Data\Streams\<name>\Output\MOLEFLOW\MIXED\<Component>
# 示例：\Data\Streams\PRODUCT\Output\MOLEFLOW\MIXED\DMS
```

## 模块 (Blocks)

### 通用模块输入
```python
# 模块参数的一般路径格式
\Data\Blocks\<name>\Input\<Parameter>

# 常见参数名（因模块类型而异）：
# PRES, TEMP, REAC_PRES, REAC_TEMP, PRESSURE, TEMPERATURE
# LENGTH, DIAM
# NSTAGES（理论板数）
# FEED_STAGE（进料板位置）
# REFLUX_RATIO（回流比）
# REBOIL_RATIO（再沸比）
# DISTILLATE_DUTY（馏出物流量）
```

### 反应器 (RPlug, RCSTR, RYield)
```python
# 平推流反应器 (RPlug)
\Data\Blocks\<name>\Input\REAC_TEMP      # 反应温度
\Data\Blocks\<name>\Input\REAC_PRES      # 反应压力
\Data\Blocks\<name>\Input\LENGTH         # 反应器长度
\Data\Blocks\<name>\Input\DIAM           # 反应器直径

# 全混流反应器 (RCSTR)
\Data\Blocks\<name>\Input\REAC_TEMP
\Data\Blocks\<name>\Input\REAC_PRES
\Data\Blocks\<name>\Input\VOLUME         # 反应器体积

# 产率反应器 (RYield)
\Data\Blocks\<name>\Input\REAC_TEMP
\Data\Blocks\<name>\Input\REAC_PRES
```

### 精馏塔 (Radfrac)
```python
\Data\Blocks\<name>\Input\NSTAGES        # 理论板数
\Data\Blocks\<name>\Input\FEED_STAGE     # 进料板位置
\Data\Blocks\<name>\Input\REFLUX_RATIO   # 回流比
\Data\Blocks\<name>\Input\REBOIL_RATIO   # 再沸比
\Data\Blocks\<name>\Input\DISTILLATE_DUTY # 馏出物流量

# 塔板温度输出（板号从 1 开始）
\Data\Blocks\<name>\Output\B_TEMP\<stage>  # 第 stage 块板温度

# 冷凝器和再沸器
\Data\Blocks\<name>\Output\COND_DUTY     # 冷凝器热负荷
\Data\Blocks\<name>\Output\REB_DUTY      # 再沸器热负荷
```

### 换热器 (Heater, HeaterX)
```python
\Data\Blocks\<name>\Input\TEMP           # 出口温度
\Data\Blocks\<name>\Input\PRES           # 出口压力
\Data\Blocks\<name>\Input\DUTY           # 热负荷（正=加热，负=冷却）
```

### 闪蒸罐 (Flash2)
```python
\Data\Blocks\<name>\Input\TEMP           # 闪蒸温度
\Data\Blocks\<name>\Input\PRES           # 闪蒸压力
\Data\Blocks\<name>\Input\VFRAC          # 气相分率（与 T/P 二选一）
```

## 全局设置

### 单位集
```python
\Data\Setup\Global\Input\INSET
# 常见值：MET (公制), SI (国际单位制), ENG (英制)
```

### 物性方法
```python
\Data\Properties\Specifications\Input\GBASEOPSET
# 常见值：RK-SOAVE, UNIQUAC, NRTL-RK, PENG-ROB
```

### 组分定义
```python
# 组分类型标识符
\Data\Components\Specifications\Input\TYPE
# 通过 .Elements 访问表格

# 组分名称
\Data\Components\Specifications\Input\NAME

# 组分 CAS 号
\Data\Components\Specifications\Input\CASN
```

## 模块创建类型标识

```python
# 添加模块时的类型标识符
# 格式：<BlockName>!<Type>

# 反应器
"R1!RPlug"    # 平推流
"R1!RCSTR"    # 全混流
"R1!RYield"   # 产率反应器
"R1!RStoic"   # 化学计量反应器

# 分离设备
"F1!Flash2"   # 闪蒸罐
"T1!Radfrac"  # 精馏塔（严格）
"T1!DSTWU"    # 精馏塔（简捷）
"D1!Decanter" # 分相器

# 传热设备
"H1!Heater"   # 加热器/冷却器
"H1!HeaterX"  # 两股流换热器

# 其他
"M1!Mixer"    # 混合器
"S1!Splitter" # 分割器
"P1!Pump"     # 泵
"C1!Compr"    # 压缩机
```

## 流股创建类型标识

```python
# 格式：<StreamName>!<Type>

"S1!MATERIAL"  # 物料流（最常用）
"Q1!HEAT"      # 热流
"W1!WORK"      # 功流/电功流
```

## 端口连接

```python
# 模块端口常见名称
"IN" or "1"      # 输入端口
"OUT" or "2"     # 输出端口

# 精馏塔专用
"FEED"          # 进料端口
"DIST"          # 塔顶产物
"BOTTOMS"       # 塔底产物

# 示例：连接流股到端口
\Data\Blocks\<name>\Ports\<port_name>\Elements.Add(<stream_name>)
```

## 路径编写注意事项

1. **使用原始字符串**：`r"\Data\Streams\S1"` 避免转义问题
2. **反斜杠方向**：Windows 路径用 `\`，也可用 `/`（但推荐 `\`）
3. **名称大小写**：Aspen 路径**不区分大小写**
4. **空格处理**：如果名称中有空格，直接使用，无需转义
5. **特殊字符**：避免在流股/模块名称中使用特殊字符

## 调试路径问题的步骤

```python
# 1. 确认路径格式正确
path = r"\Data\Streams\S1\Input\TEMP\MIXED"

# 2. 尝试逐层访问
data = aspen.Tree.Elements("Data")
streams = data.Elements("Streams")
s1 = streams.Elements("S1")
input_node = s1.Elements("Input")
# ... 继续向下，找出哪一层出错

# 3. 在 Aspen 变量浏览器中右键 → Copy Path
# 确保路径与 Aspen 中完全一致

# 4. 使用 FindNode 的异常处理
try:
    node = aspen.Tree.FindNode(path)
    print(f"找到节点，值 = {node.Value}")
except Exception as e:
    print(f"节点不存在: {e}")
```
