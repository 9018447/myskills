# 深度研究助手（deep-research-wos）

当用户需要对某个学术主题进行系统性、多方向的深度文献研究时，使用 `deep-research-wos` skill。

## 触发条件

以下任一情况激活本规范：
- 用户说 "深度研究"、"系统梳理"、"文献调研"、"研究现状"
- 用户要求对某个主题进行 "多方向"、"全方位" 的文献搜索
- 用户提到 "逻辑闭环" 或要求文献覆盖主题的所有关键维度
- 用户明确说 "不要写报告，只要文献" 或 "只列文献信息和摘要"

## NOT（不要触发）
- 用户只需要单次搜索某个关键词（交给 `search-wos`）
- 用户要求撰写论文、综述、研究总结（这是写作任务）
- 用户要求使用 Google Scholar、PubMed 等非 WoS 数据库
- 用户已有明确论文列表，只需整理格式

## 核心工作流

```
主题输入 → 方向拆解 → 逐方向搜索 → 闭环判断 → 调整/补搜 → 整合输出
```

### Phase 1: 方向拆解

1. 分析主题的核心概念、时间范围、学科领域
2. 从以下维度拆解为 2-5 个研究方向：
   - 机理/理论维度
   - 方法/技术维度
   - 应用/场景维度
   - 材料/体系维度
   - 关联/交叉维度
3. 为每个方向命名（中文，8字以内）并给出英文搜索关键词
4. **向用户展示拆解计划并确认**（推荐但非强制）

### Phase 2: 搜索执行

对每个方向：
1. 使用 `search-wos` skill 的 API 搜索模式执行搜索
2. 根据方向性质选择排序：
   - 基础理论 → `times-cited-descending`（找奠基文献）
   - 最新方法 → `date-descending`（找最新进展）
   - 应用案例 → `times-cited-descending`（找代表性应用）
3. 提取 10-15 篇核心文献的信息

### Phase 3: 逻辑闭环判断

检查每个方向是否满足：
1. **锚点文献**：≥1 篇高被引（>50次）综述或里程碑论文
2. **概念覆盖**：包含该方向的关键子概念
3. **时间跨度**：既有奠基文献（5-10年前），也有近2-3年进展
4. **数量充足**：≥8-10 篇有意义的文献

未闭环时：分析缺口 → 调整关键词（细化/扩展/限定）→ 重新搜索
**最多迭代 3 次**，超过后标注"部分覆盖"。

### Phase 4: 整合输出

按以下结构输出：

```markdown
# 深度研究文献清单：{主题}

## 研究总纲
（方向概览表 + 闭环状态）

## 方向N: {方向名称}
## Chrome 启动规范

执行任何 WoS 操作前，通过 agent-browser 启动 Chrome（使用用户数据文件夹以保持 WoS 登录状态）：

```json
{
  "action": "open",
  "app": {
    "path": "/usr/bin/google-chrome-stable",
    "args": [
      "--remote-debugging-port=9222",
      "--user-data-dir=/home/smh/chrome-profile-stable",
      "--no-first-run",
      "--no-default-browser-check"
    ]
  }
}
```

规则：
1. 必须使用 `/home/smh/chrome-profile-stable`
2. 前台启动，禁止 `--headless`
3. 已运行在 9222 则直接连接 `agent-browser connect 9222`
- 关联提纲仅描述连接关系，不展开论述

## Chrome 启动规范

执行任何 WoS 操作前，按 `search-wos` 规范启动 Chrome：

```bash
/usr/bin/google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/home/smh/chrome-profile-stable --no-first-run --no-default-browser-check
```

规则：
1. 必须使用 `/home/smh/chrome-profile-stable`
2. 前台启动，禁止 `nohup` / `&` / `--headless`
3. 已运行在 9222 则直接连接

## Anti-Detection

- 每次导航包含 initScript: `Object.defineProperty(navigator, 'webdriver', {get: () => undefined})`
- 不用 `wait_for`，用 `evaluate_script` 内部轮询
- 不用 `take_screenshot` 提取数据
- 遇到 CAPTCHA 立即停止，告知用户手动验证

## 语言

- 用户用什么语言就用什么语言回复
- 中文关键词翻译为英文用于 WoS 搜索
- 文献标题和摘要保留英文原文
