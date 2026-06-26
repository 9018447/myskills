---
name: wos-latex-citation-manager
description: "从LaTeX文档的introduction部分提取关键要点，按语义分组后联合搜索Web of Science相关文献（按相关性排序），生成BibTeX引用并插入到LaTeX中。适用于需要为学术论文添加参考文献的场景。"
argument-hint: "<tex-file-path> [--points 10] [--refs-per-point 5] [--compile]"
user-invocable: true
disable-model-invocation: false
---

# LaTeX Citation Manager

从LaTeX文档的introduction部分提取关键要点，使用Web of Science搜索相关文献，整理高引用文献，生成BibTeX引用并插入到LaTeX中。

## 工作流程

### 1. 解析LaTeX文件
- 读取用户提供的.tex文件
- 定位并提取`\section{Introduction}`部分的内容
- 分析introduction的结构和内容

### 2. 提取关键要点
- 基于语义分析提取introduction中的关键要点
- 每个要点应该是一个完整的研究主题或概念
- 默认提取10个要点，可通过`--points`参数调整
- 要点应该覆盖introduction的不同部分，确保全面性

### 3. 搜索相关文献（使用Web of Science）
- **多要点联合搜索**：将语义相近的要点合并为一个查询（如2-3个要点组合），避免单个要点关键词过窄导致偏离原文
- 每个联合查询提取共同的名词短语和专业术语，构建布尔组合查询
- 使用Web of Science API搜索相关文献
- **按相关性排序**（而非引用次数），确保搜索结果与原文主题紧密匹配
- 每个联合查询默认选择8篇文献，可通过`--refs-per-point`参数调整
- **最少参考文献数**：最终生成的BibTeX文件必须包含至少50篇文献（`--min-refs`），不足时扩大搜索范围或降低相关性阈值补充

### 4. 整理文献信息
- 从搜索结果中提取完整的文献元数据
- 包括：标题、作者、期刊、年份、卷期页码、DOI、引用次数等
- 为每个要点生成结构化的文献列表

### 5. 生成BibTeX引用
- 将文献信息转换为BibTeX格式
- 为每篇文献生成唯一的引用键（key）
- 确保BibTeX格式符合LaTeX标准

### 6. 插入引用到LaTeX
- 在introduction的相应位置插入`\cite{}`命令
- 在文档末尾添加`\bibliography{}`和`\bibliographystyle{}`命令
- 创建或更新.bib文件
- 保持LaTeX文档的结构完整性

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<tex-file-path>` | LaTeX文件路径 | 必需 |
| `--points` | 提取的关键要点数量 | 10 |
| `--refs-per-point` | 每个联合查询的文献数量 | 8 |
| `--min-refs` | 最少参考文献总数 | 50 |
| `--database` | Web of Science数据库 | WOSCC |
| `--sort` | 文献排序方式 | relevance |

## 使用示例

```bash
# 基本用法
/wos-latex-citation-manager main_manuscript.tex

# 指定参数
/wos-latex-citation-manager main_manuscript.tex --points 8 --refs-per-point 8 --min-refs 50

# 使用特定数据库
/wos-latex-citation-manager main_manuscript.tex --database ALLDB
```

## 依赖工具

### Web of Science相关skills
- **wos-search**: 搜索Web of Science文献
- **wos-parse-results**: 解析搜索结果
- **wos-export**: 导出文献信息（可选用于Zotero集成）

### LaTeX工具（如需手动编译）
- **pdflatex**: LaTeX编译器
- **bibtex**: BibTeX处理工具
- **必要LaTeX包**: 
  - `natbib` 或 `biblatex`（用于引用管理）
  - `hyperref`（用于超链接）
  - `amsmath`（数学公式支持）

## 输出文件

1. **更新的.tex文件**: 包含引用的LaTeX文档（Introduction部分每个关键句子都应有引用）
2. **references.bib**: BibTeX引用文件（至少50篇文献）

## 数量保障机制

搜索完成后必须检查文献总数：
1. 统计`references.bib`中的条目数
2. 如果 < `--min-refs`（默认50），执行补充搜索：
   - 扩大关键词范围（去掉过于具体的限定词）
   - 切换排序方式为`times-cited-descending`获取经典文献
   - 增加数据库范围（如`ALLDB`）
3. 最终条目数必须 ≥ `--min-refs`

## 工作原理

### 要点提取算法
1. 将introduction按段落分割
2. 使用AI分析每个段落的核心主题
3. 合并相似主题，提取独立要点
4. 确保要点覆盖introduction的不同方面

### 文献搜索策略
1. **要点分组**：将10个要点按语义相似性分为3-5个搜索组（如：CO₂捕集相关、DES材料相关、热力学模型相关）
2. **关键词提取**：从每个搜索组中提取共同的名词短语和专业术语
3. **构建联合查询**：使用布尔运算符（AND/OR）组合同组关键词，避免单个要点的关键词过窄
4. **按相关性排序**：使用`sort: "relevance"`确保结果与原文主题匹配，而非仅按引用次数
5. **相关性验证**：检查搜索结果的标题和摘要是否与原文的对应段落主题一致
6. **数量保障**：搜索完成后统计总文献数，不足50篇时执行补充搜索（扩大关键词范围、降低检索条件、增加数据库）

### 引用插入逻辑
1. 分析introduction的上下文
2. 在相关句子后插入`\cite{}`命令
3. 确保引用位置合理，不破坏句子结构
4. 处理多个引用的情况（如`\cite{key1,key2}`）
5. **文献分配**：将搜索到的文献按主题分配到introduction的对应段落，每个段落至少2-3篇引用，确保全文覆盖均匀

## Web of Science API调用指南

### 环境准备
1. 确保浏览器已连接到Chrome实例
2. 浏览器需要在Web of Science页面上（已登录）
3. 使用`chrome_devtools_list_pages`检查可用标签页
4. 使用`chrome_devtools_select_page`选择目标标签页

### API调用流程
1. **提取SID**: 从浏览器的performance资源中提取会话ID
2. **构建请求**: 构建Web of Science API请求体
3. **执行请求**: 使用`chrome_devtools_evaluate`执行fetch请求
4. **解析结果**: 解析返回的NDJSON数据

### 示例API调用
```javascript
// 1. 提取SID — 使用裸表达式，不要用const声明
//    chrome_devtools_evaluate在持久化上下文中运行，
//    const/let会跨调用累积，导致"Identifier already declared"错误
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('SID='))
  .map(r => r.name.match(/SID=([^&]+)/)?.[1])
  .filter(Boolean)[0] || '';

// 2. 构建请求
const requestBody = {
  "product": "WOSCC",
  "searchMode": "general",
  "viewType": "search",
  "serviceMode": "summary",
  "search": {
    "mode": "general",
    "database": "WOSCC",
    "query": [{"rowField": "TS", "rowText": "YOUR_SEARCH_QUERY"}],
    "editions": ["WOS.SCI"]
  },
  "retrieve": {
    "count": 10,
    "history": true,
    "jcr": true,
    "sort": "relevance",
    "analyzes": [],
    "locale": "en"
  },
  "eventMode": null
};

// 3. 执行请求
const response = await fetch(`/api/wosnx/core/runQuerySearch?SID=${sid}`, {
  method: 'POST',
  headers: { 'Content-Type': 'text/plain;charset=UTF-8', 'Accept': 'application/x-ndjson' },
  body: JSON.stringify(requestBody)
});

// 4. 解析结果
const text = await response.text();
const lines = text.trim().split('\n').map(line => {
  try { return JSON.parse(line); } catch(e) { return null; }
}).filter(Boolean);

const recordsData = lines.find(l => l.key === 'records')?.payload;
```

### Chrome DevTools Evaluate 注意事项

> ⚠️ `chrome_devtools_evaluate` 在页面的持久化JavaScript上下文中执行。前一次调用中声明的 `const`/`let` 变量在后续调用中仍然存在。

❌ **错误做法** — 重复声明同名变量：
```javascript
// 第一次调用
const sid = 'abc123';
// 第二次调用（在同一页面上下文中）
const sid = 'xyz789'; // → SyntaxError: Identifier 'sid' has already been declared
```

✅ **正确做法** — 使用裸表达式直接返回值：
```javascript
// 提取SID — 直接写表达式，不要声明变量
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('SID='))
  .map(r => r.name.match(/SID=([^&]+)/)?.[1])
  .filter(Boolean)[0] || '';
```

❌ **错误做法** — 在evaluate中使用return：
```javascript
return performance.getEntriesByType('resource'); // → SyntaxError: Illegal return statement
```

✅ **正确做法** — 直接写表达式：
```javascript
performance.getEntriesByType('resource'); // 结果自动返回
```

❌ **错误做法** — 在单次evaluate中批量执行多个顺序网络请求：
```javascript
// 10个顺序fetch调用 → 可能超时（CDP默认超时约30秒）
for (const q of queries) { await fetch(...); }
```

✅ **正确做法** — 逐个调用，或使用Promise.all并行执行：
```javascript
// 方案1：逐个调用（推荐，更可靠）
// 每个搜索单独一次chrome_devtools_evaluate调用

// 方案2：并行执行（更快，但可能触发限流）
await Promise.all(queries.map(q => fetch(...)));
```

## 注意事项

1. **网络连接**: 需要稳定的网络连接以访问Web of Science API
2. **浏览器状态**: 浏览器需要在Web of Science页面上（已登录）
3. **文件权限**: 需要对.tex文件有读写权限
4. **备份建议**: 建议在运行前备份原始.tex文件
5. **PDF编译**: 如需编译PDF，请使用Overleaf或本地LaTeX环境手动编译

## 故障排除

### 常见问题
1. **无法找到introduction**: 检查LaTeX文件是否包含`\section{Introduction}`
2. **搜索无结果**: 尝试使用更通用的关键词或不同的数据库
3. **BibTeX格式错误**: 验证生成的.bib文件格式
4. **SID丢失**: 重新导航到Web of Science页面
5. **`Identifier already declared`**: Chrome DevTools evaluate在持久化上下文中运行，不要重复声明同名变量。使用裸表达式直接返回值。
6. **`Illegal return statement`**: 在evaluate中不要使用`return`，直接写表达式即可。
7. **CDP超时**: 不要在单次evaluate中批量执行多个顺序网络请求，应逐个调用。
8. **`grep`退出码1**: 当没有匹配时grep返回退出码1，使用`grep ... || true`处理。

### 调试模式
添加`--verbose`参数查看详细的工作流程信息。

## 扩展功能

### 未来可能的扩展
1. 支持其他章节（如Related Work、Background）
2. 自动推荐相关文献
3. 集成Zotero或Mendeley
4. 支持多种引用格式（APA、IEEE、MLA等）
5. 文献去重和优先级排序

## 最佳实践

1. **先备份**: 运行前备份原始LaTeX文件
2. **小范围测试**: 先在小文档上测试功能
3. **检查结果**: 人工检查生成的引用是否合适
4. **调整参数**: 根据需要调整要点数量和文献数量
5. **保持更新**: 定期更新Web of Science会话
6. **按相关性搜索**: 默认使用`sort: "relevance"`而非引用次数，确保文献与原文主题匹配
7. **多要点联合搜索**: 将语义相近的要点合并为一个查询，避免单个要点关键词过窄导致偏离
8. **分组策略**: 按主题将要点分为3-5个搜索组（如CO₂捕集、DES材料、热力学模型），每组构建一个联合查询

## 要点分组策略

当提取10个关键要点后，不要逐个搜索，而是按语义相似性分组：

| 搜索组 | 包含要点示例 | 查询构建策略 |
|--------|-------------|-------------|
| CO₂捕集与排放 | 碳捕集技术、水蒸气去除、传统干燥局限 | `TS=("CO2 capture" AND ("water removal" OR "dehydration" OR "drying"))` |
| 溶剂材料 | 离子液体、深共熔溶剂、胆碱基DES | `TS=("deep eutectic solvent" AND (choline OR ionic liquid))` |
| 热力学建模 | COSMO-RS、PDH理论、热力学模型 | `TS=("COSMO-RS" AND ("deep eutectic" OR electrolyte))` |

**分组原则**：
- 每组2-4个要点，共3-5组
- 组内要点共享核心术语
- 组间术语有明显区分
- 每个查询保持简洁，避免过长的布尔表达式