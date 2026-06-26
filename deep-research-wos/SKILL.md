---
name: deep-research-wos
description: |
  当用户需要对某个学术主题进行系统性、多方向的深度文献研究时调用此 skill。

  触发词与场景：
  - "帮我深度研究一下..."、"系统梳理...相关文献"、"做一个文献调研"
  - "XXX 领域的研究现状"、"XXX 有哪些关键文献"
  - 用户给出一个宽泛的研究主题，需要拆解成多个子方向分别搜索
  - 用户要求"逻辑闭环"的文献覆盖，即各方向的文献能互相支撑、覆盖主题全貌
  - 用户说"不要写报告，只要文献列表"或"只列文献信息和摘要"

  NOT:
  - 用户只需要单次搜索某关键词（用 search-wos 即可）
  - 用户要求撰写论文、综述或研究总结（本 skill 不生成报告正文）
  - 用户要求使用 Google Scholar、PubMed 等非 WoS 数据库
  - 用户已有明确的论文列表，只需整理格式

  IO:
  - 输入：研究主题（中英文均可）、可选的方向偏好、时间范围
  - 输出：按研究方向组织的文献清单（标题/作者/期刊/年份/DOI/摘要），附文献关联提纲
---

# deep-research-wos

系统性学术文献深度研究工具。将用户主题拆解为多方向研究计划，对每个方向执行 Web of Science 搜索，迭代至逻辑闭环，输出结构化文献清单。

## Chrome 启动规范（MANDATORY）

Before ANY WoS operation, launch Chrome via agent-browser with the user's personal data directory:

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

**CRITICAL RULES**:
1. **Use user's profile** — `--user-data-dir=/home/smh/chrome-profile-stable` (contains login cookies for institutional access)
2. **Foreground launch** — Do NOT use `--headless`. User must see the browser.
3. **No headless mode** — Never use `--headless`. Some publisher sites block headless browsers.
4. **If Chrome already running** with this profile on port 9222, connect directly via `agent-browser connect 9222`.
5. **Wait for CDP** — After opening, verify `http://127.0.0.1:9222/json/version` responds before connecting.

Then connect via agent-browser:
```bash
agent-browser connect 9222
```
   - **不要超过 5 个方向** — 过多的方向会导致搜索浅层化

### 方向命名规范

每个方向给出一个简洁的中文名称（8 字以内）和对应的英文搜索关键词集合：

```
方向1: 多孔液体合成
  - 核心关键词: "porous liquid*" synthesis preparation
  - 扩展关键词: "porous liquid*" AND ("synthetic method*" OR preparation)

方向2: CO2 吸附机理
  - 核心关键词: "porous liquid*" "CO2 capture" mechanism
  - 扩展关键词: "porous liquid*" AND "carbon dioxide" AND (adsorption OR absorption)
```

### 用户确认（可选但推荐）

拆解完成后，向用户展示研究计划：

```
我将围绕 "{主题}" 从以下 {N} 个方向进行深度文献搜索：

1. {方向1名称} — 关注...
2. {方向2名称} — 关注...
...

每个方向将搜索 10-15 篇核心文献，判断是否覆盖该方向的关键概念。
如确认，我将开始执行搜索。
```

如果用户有特定偏好（如更关注某方向、排除某方向），按用户要求调整。

## Phase 2: 搜索执行

### Chrome 启动规范（继承自 search-wos）

执行任何 WoS 操作前，必须启动 Chrome：

```bash
/usr/bin/google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/home/smh/chrome-profile-stable --no-first-run --no-default-browser-check
```

**规则**：
1. 使用用户 profile：`--user-data-dir=/home/smh/chrome-profile-stable`
2. 前台启动，不要用 `nohup` 或 `&`
3. 禁止 `--headless`
4. 已运行在 9222 端口则直接 `agent-browser connect 9222`
5. 验证 `http://127.0.0.1:9222/json/version` 响应后再连接

### SID 提取

```javascript
(function() {
  var entries = performance.getEntriesByType('resource');
  for (var i = 0; i < entries.length; i++) {
    var match = entries[i].name.match(/SID=([^&]+)/);
    if (match) return match[1];
  }
  return 'no_sid';
})()
```

### 搜索 API 调用（单方向单次搜索 = 1 个 tool call）

```javascript
(function() {
  var sid = 'EXTRACTED_SID';
  var body = JSON.stringify({
    product: 'WOSCC',
    searchMode: 'general',
    viewType: 'search',
    serviceMode: 'summary',
    search: {
      mode: 'general',
      database: 'WOSCC',
      query: [{rowField: 'TS', rowText: '"SEARCH_TERM"'}]
    },
    retrieve: {
      count: 15,
      history: true,
      jcr: true,
      sort: 'times-cited-descending',
      analyzes: [],
      locale: 'en'
    },
    eventMode: null
  });

  return fetch('/api/wosnx/core/runQuerySearch?SID=' + sid, {
    method: 'POST',
    headers: {'Content-Type': 'text/plain;charset=UTF-8', 'Accept': 'application/x-ndjson'},
    body: body
  }).then(function(r) { return r.text(); }).then(function(text) {
    var lines = text.trim().split('\n');
    var recordsData = null;
    var searchInfo = null;
    for (var i = 0; i < lines.length; i++) {
      try {
        var parsed = JSON.parse(lines[i]);
        if (parsed.key === 'records') recordsData = parsed.payload;
        if (parsed.key === 'searchInfo') searchInfo = parsed.payload;
      } catch(e) {}
    }
    if (!recordsData) return JSON.stringify({status: 'no_records', lines: lines.length});
    var keys = Object.keys(recordsData);
    var results = [];
    for (var j = 0; j < keys.length; j++) {
      var rec = recordsData[keys[j]];
      var title = '';
      try { title = rec.titles.item.en[0].title; } catch(e) {}
      var authors = '';
      try { authors = rec.names.author.en.filter(Boolean).map(function(a){return a.wos_standard;}).join('; '); } catch(e) {}
      var source = '';
      try { source = rec.titles.source.en[0].title; } catch(e) {}
      var abstract = '';
      try { abstract = rec.abstract.basic.en.abstract.replace(/<[^>]*>/g, '').substring(0, 500); } catch(e) {}
      var cites = 0;
      try { cites = rec.citation_related.counts.WOSCC; } catch(e) {}
      var citesAll = 0;
      try { citesAll = rec.citation_related.counts.ALLDB; } catch(e) {}
      results.push({
        idx: j+1,
        wosId: rec.colluid || '',
        title: title,
        authors: authors,
        source: source,
        year: rec.pub_info ? rec.pub_info.pubyear : '',
        doi: rec.doi || '',
        citations: cites,
        citationsAll: citesAll,
        abstract: abstract
      });
    }
    return JSON.stringify({
      status: 'ok',
      total: searchInfo ? searchInfo.RecordsFound : 0,
      count: results.length,
      records: results
    });
  });
})()
```

### 搜索排序策略

按方向性质选择排序：

| 方向类型 | 排序方式 | 原因 |
|----------|----------|------|
| 基础理论/机理 | `times-cited-descending` | 找奠基性高被引文献 |
| 最新方法/技术 | `date-descending` | 找最新进展 |
| 应用/案例 | `times-cited-descending` | 找代表性应用 |
| 补充搜索 | `relevance` | 找最相关的 |

## Phase 3: 逻辑闭环判断

### 闭环标准（必须同时满足）

对每个方向，搜索后判断是否"闭环"：

1. **有锚点文献**：至少 1 篇高被引（>50 次）综述或里程碑论文，能代表该方向的核心共识
2. **概念覆盖**：搜索结果中包含该方向的关键子概念（如合成方向应覆盖不同合成路线；机理方向应覆盖不同理论模型）
3. **时间跨度合理**：既有奠基性文献（5-10 年前），也有近 2-3 年的最新进展
4. **数量充足**：至少 8-10 篇有意义的文献（非重复、非完全无关）

### 未闭环时的处理

如果某方向未闭环，分析缺口并调整搜索：

```
方向X 搜索分析：
- 已覆盖: ...
- 缺口: 缺少关于 {具体子概念} 的文献
- 调整策略: 增加关键词 "{新增关键词}"，或改用 "{替代关键词}" 重新搜索
```

调整方式：
- **关键词细化**：将宽泛词替换为具体术语
- **关键词扩展**：添加同义词或相关术语（用 OR）
- **限定条件**：添加年份限定（如 `PY=2020-2025`）或期刊限定
- **反向搜索**：从已找到的高被引文献的参考文献/施引文献中找线索

**最多迭代 3 次** — 超过 3 次仍未闭环，记录缺口并在输出中标注"该方向文献覆盖不完全"。

## Phase 4: 整合输出

### 输出结构

```markdown
# 深度研究文献清单：{主题}

## 研究总纲

**主题**: {主题}
**搜索时间**: {日期}
**总文献数**: {N} 篇（来自 {M} 个研究方向）

### 方向概览
| # | 方向 | 文献数 | 闭环状态 |
|---|------|--------|----------|
| 1 | {方向1} | {N} | ✓ 已闭环 |
| 2 | {方向2} | {N} | ✓ 已闭环 |
| 3 | {方向3} | {N} | △ 部分覆盖（缺口：...）|

---

## 方向1: {方向名称}

**搜索关键词**: {使用的关键词}
**逻辑闭环依据**: {简述为什么认为该方向已覆盖}

### 锚点文献（高被引/综述）
1. **{标题}**
   - 作者: {authors}
   - 期刊: {source} | 年份: {year} | 引用: {citations}
   - DOI: https://doi.org/{doi}
   - 摘要: {abstract}

### 核心文献
2. **{标题}** ...
3. **{标题}** ...

### 最新进展
...

---

## 方向2: {方向名称}
...

---

## 文献关联提纲

```
{主题}
├── {方向1}
│   ├── 锚点: [{第一作者}, {年份}] — 提出...
│   └── 支撑: [{第一作者}, {年份}] — 验证...
├── {方向2}
│   ├── 锚点: [{第一作者}, {年份}] — 建立...
│   └── 与方向1关联: [{第一作者}, {年份}] 连接了...和...
└── {方向3}
    └── ...
```

### 跨方向关联
- **{方向A} ↔ {方向B}**: [{作者}, {年份}] 在...方面建立了联系
- **{方向B} → {方向C}**: ...

---

## DOI 链接汇总

### 方向1
1. https://doi.org/10.xxxx/xxxxx
2. ...

### 方向2
...
```

### 输出原则

1. **不写报告**：不生成综述段落、不总结研究进展、不提出结论
2. **只列事实**：仅呈现文献的客观信息（标题、作者、期刊、摘要等）
3. **结构化呈现**：按方向分层，每方向内部按重要性排序（锚点→核心→最新）
4. **关联提纲仅描述连接关系**：用一句话说明两篇文献在哪个概念上有关联，不展开论述

## Anti-Detection（继承自 search-wos）

1. **每次导航**包含：
   ```javascript
   Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
   ```
2. **不用 `wait_for`** — 用 `evaluate_script` 内部轮询
3. **不用 `take_screenshot` 提取数据** — 用 `evaluate_script` 返回 JSON
4. **遇到 CAPTCHA**：立即停止，告知用户手动验证，等待确认后继续

## Session 恢复

如果 SID 丢失（如跳转到出版商页面后）：
1. 导航到 `https://www.webofscience.com/wos/woscc/basic-search`
2. 重新提取 SID
3. 继续搜索

## 语言

- 用户用什么语言就用什么语言回复
- 中文关键词必须翻译为英文用于 WoS 搜索
- 文献标题保留英文原文
- 摘要保留英文原文（WoS 返回的摘要）

## 完整示例

### 用户输入
"帮我深度研究一下多孔液体在二氧化碳捕获中的应用"

### 方向拆解
1. 多孔液体合成方法
2. CO2 吸附机理与热力学
3. 多孔液体 CO2 捕获性能评估
4. 工业应用与放大研究

### 搜索执行
对每个方向分别执行 search-wos API 搜索，迭代至闭环。

### 输出片段
```markdown
# 深度研究文献清单：多孔液体在二氧化碳捕获中的应用

## 研究总纲
...

## 方向1: 多孔液体合成方法

**搜索关键词**: TS="porous liquid*" AND (synthesis OR preparation OR "synthetic route*")
**逻辑闭环依据**: 覆盖了有机多孔液体、无机多孔液体、混合型三种主要合成策略；有 1 篇引用>200 的综述作为锚点。

### 锚点文献
1. **Organic cage porous liquids**
   - 作者: Zhang, J; et al.
   - 期刊: Nature Communications | 年份: 2017 | 引用: 245
   - DOI: https://doi.org/10.1038/s41467-017-01184-5
   - 摘要: Porous liquids are a new class of liquid materials that contain...

### 核心文献
2. **Porous liquids for natural gas sweetening** ...
...
```
