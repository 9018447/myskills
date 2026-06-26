# LaTeX Citation Manager

从LaTeX文档的introduction部分提取关键要点，使用Web of Science搜索相关文献，整理高引用文献，生成BibTeX引用并插入到LaTeX中，最后编译PDF。

## 功能概述

1. **提取关键要点**：从LaTeX文档的introduction部分提取关键研究主题
2. **搜索文献**：使用Web of Science API搜索相关高引用文献
3. **生成BibTeX**：将文献信息转换为标准BibTeX格式
4. **插入引用**：在LaTeX文档的相应位置插入`\cite{}`命令
5. **编译PDF**：自动编译生成包含引用的PDF文件

## 使用方法

### 基本用法
```bash
/wos-latex-citation-manager main_manuscript.tex
```

### 指定参数
```bash
/wos-latex-citation-manager main_manuscript.tex --points 8 --refs-per-point 3 --compile
```

### 使用特定数据库
```bash
/wos-latex-citation-manager main_manuscript.tex --database ALLDB
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<tex-file-path>` | LaTeX文件路径 | 必需 |
| `--points` | 提取的关键要点数量 | 10 |
| `--refs-per-point` | 每个要点的文献数量 | 5 |
| `--compile` | 是否自动编译PDF | 否 |
| `--database` | Web of Science数据库 | WOSCC |
| `--sort` | 文献排序方式 | times-cited-descending |

## 依赖工具

### Web of Science相关skills
- **wos-search**: 搜索Web of Science文献
- **wos-parse-results**: 解析搜索结果
- **wos-export**: 导出文献信息（可选用于Zotero集成）

### LaTeX工具
- **pdflatex**: LaTeX编译器
- **bibtex**: BibTeX处理工具
- **必要LaTeX包**: 
  - `natbib` 或 `biblatex`（用于引用管理）
  - `hyperref`（用于超链接）
  - `amsmath`（数学公式支持）

## 输出文件

1. **更新的.tex文件**: 包含引用的LaTeX文档
2. **references.bib**: BibTeX引用文件
3. **编译后的PDF**: 如果指定`--compile`参数

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
- 为每个要点构建搜索查询
- 使用Web of Science API搜索相关文献
- 按引用次数排序，选择引用最高的文献
- 每个要点默认选择5篇文献，可通过`--refs-per-point`参数调整

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

### 7. 编译PDF（可选）
- 如果指定了`--compile`参数，自动编译PDF
- 运行pdflatex、bibtex、pdflatex、pdflatex的编译流程
- 处理可能的编译错误

## 测试结果

### 测试用例1：基本功能测试
- ✅ 成功提取introduction中的关键要点
- ✅ 每个要点都有对应的文献引用
- ✅ BibTeX文件格式正确
- ✅ LaTeX文档能够成功编译
- ✅ 引用位置合理，不破坏文档结构

### 测试用例2：边界情况测试
- ✅ 能够处理简单的LaTeX文件
- ✅ 即使introduction很短也能提取要点
- ✅ 生成的引用适合简短文档

### 测试用例3：错误处理测试
- ✅ 返回清晰的错误信息
- ✅ 不会因文件不存在而崩溃
- ✅ 建议用户检查文件路径

## 注意事项

1. **网络连接**: 需要稳定的网络连接以访问Web of Science API
2. **浏览器状态**: 浏览器需要在Web of Science页面上（已登录）
3. **LaTeX编译**: 需要安装完整的LaTeX发行版（如TeX Live或MiKTeX）
4. **文件权限**: 需要对.tex文件有读写权限
5. **备份建议**: 建议在运行前备份原始.tex文件

## 故障排除

### 常见问题
1. **无法找到introduction**: 检查LaTeX文件是否包含`\section{Introduction}`
2. **搜索无结果**: 尝试使用更通用的关键词或不同的数据库
3. **编译错误**: 检查LaTeX语法，确保引用键唯一
4. **BibTeX格式错误**: 验证生成的.bib文件格式
5. **SID丢失**: 重新导航到Web of Science页面

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