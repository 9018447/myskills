---
name: wos-paper-workflow
description: |
  Complete Web of Science research pipeline: search papers, browse results, view paper details,
  access publisher full text, and download PDF. Use this skill whenever the user wants to find
  academic papers, look up paper details, read full text, or download PDFs from Web of Science.
  Also trigger when the user mentions any combination of: "search paper", "find paper",
  "download PDF", "view full text", "get paper", "WoS", "Web of Science", or wants to do
  literature research even if they don't explicitly ask for a "workflow".
argument-hint: "[search keywords or WoS ID or 'download {WoS ID}']"
user-invocable: true
disable-model-invocation: false
---

# WoS Paper Workflow

End-to-end pipeline for searching, viewing, and downloading papers from Web of Science.
## Environment Setup

This skill requires a browser connected to a Chrome instance with Web of Science login state.
Before starting any workflow, ensure the browser is launched with:

```bash
# 前台启动Chrome，用户可以看到浏览器界面
/usr/bin/google-chrome --remote-debugging-port=9222 --user-data-dir=/home/smh/chrome-profile-stable
```

**重要提示**：
1. 使用前台启动，不要使用 `nohup` 或 `&` 后台运行
2. 这样用户可以看到浏览器界面，便于手动干预
3. 当遇到反爬机制（如CAPTCHA验证）时，向用户求助，不要尝试自动绕过
4. 用户可以手动完成验证，然后继续自动化流程

然后通过CDP连接：

```javascript
// browser.open action
{
  "action": "open",
  "app": {
    "cdp_url": "http://127.0.0.1:9222"
  }
}
```

如果Chrome已经使用此配置文件运行，直接连接而不要重新启动。

## Workflow Overview

```
Search → Browse Results → Paper Details → Publisher Full Text → PDF Download
```

Each step uses the minimal tool calls and recovers gracefully from session loss.

## Step 1: Search Papers

Use `wos-search` skill. Key points:

- **API first**: Single `evaluate_script` with `fetch` to `/api/wosnx/core/runQuerySearch?SID={sid}`
- Extract SID from `performance.getEntriesByType('resource')`
- Chinese keywords → translate to English before searching
- Default: 10-15 results, sort by relevance
- Present results as table with `# | Title | Authors | Journal | Year | Cited | WoS ID`

If SID is lost (e.g., returning from publisher site), navigate to any WoS page first to re-establish session, then run API call.

## Step 2: Browse / Sort Results

User may ask to:
- See more results → `wos-navigate-pages` with `retrieve.first` offset
- Sort by citations → re-run search API with `sort: times-cited-descending`
- Sort by date → `sort: date-descending`

All pagination uses **1 tool call** via API with remembered query/editions/sort.

## Step 3: Paper Details

User picks a paper (by number from results, or by WoS ID). Use `wos-paper-detail`:

1. `navigate_page` to `/wos/woscc/full-record/{WOS_ID}`
2. `evaluate_script` to extract title, authors, abstract, DOI, keywords, citations, JIF, full text links
3. Present structured summary

Offer next actions:
- "View full text on publisher site" → proceed to Step 4
- "Download PDF directly" → proceed to Step 5

## Step 4: View Full Text on Publisher Site

User wants to read the full text (not just abstract). Use `wos-download` steps 1-3:

1. Navigate to full record page (if not already there)
2. Extract publisher links via `a[data-ta^="FRLinkTa"]` selectors
3. Navigate to chosen publisher link with `initScript` anti-detection
4. `evaluate_script` to extract article content from publisher HTML

**Important**: After navigating to publisher site, WoS SID is lost. Any further WoS searches must re-establish session first (navigate to WoS page before API call).

## Step 5: Download PDF

User wants to save the PDF file. Use `wos-download` steps 4-5:

1. Check if current page is direct PDF (`contentType === 'application/pdf'`)
2. If yes: trigger download via `a.download = '{FirstAuthor}_{Year}_{ShortTitle}.pdf'`
3. If on publisher HTML page: find PDF links (`/pdf/`, `.pdf`, "Download PDF" text)
4. If `pdf_links_found`: click the download link, wait for PDF to load, then trigger `a.download`
5. If `login_required` or `paywall`: inform user and provide direct PDF URL for manual download

**Filename convention**: `{FirstAuthor}_{Year}_{ShortTitle}.pdf` (e.g., `Gross_2002_PC-SAFT.pdf`)

## Session Recovery

After visiting external publisher sites, the browser loses WoS session (SID cleared from performance entries). To continue using WoS:

1. Navigate to `https://www.webofscience.com/wos/woscc/basic-search`
2. Then resume API-based operations

## Language

Reply in the same language the user uses.

## Example Flow

**User**: "搜索PC-SAFT相关论文"
→ `wos-search`: "PC-SAFT" → show results table

**User**: "按引用量排序"
→ `wos-search` with `sort: times-cited-descending` → show top-cited papers

**User**: "打开第一篇"
→ `wos-paper-detail WOS:000174114200023` → show abstract, DOI, links

**User**: "去出版商页面看全文"
→ `wos-download` view steps → navigate to ACS → extract article HTML

**User**: "下载PDF"
→ `wos-download` download steps → trigger `a.download` → save `Gross_2002_PC-SAFT.pdf`

**User**: "回到WoS看第二篇"
→ Navigate to WoS to recover SID → `wos-paper-detail WOS:000235512600027`

## Anti-Detection

Every `navigate_page` must include:
```javascript
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

Never use `wait_for`. Always use `evaluate_script` with internal `for` + `setTimeout` polling loops.

Never use `take_screenshot` for data extraction. Use `evaluate_script` returning structured JSON.

## 遇到反爬机制时的处理

当遇到反爬机制（如CAPTCHA验证、Cloudflare挑战等）时：

1. **不要尝试自动绕过** - 停止自动化尝试
2. **向用户求助** - 告知用户遇到了验证页面
3. **提供手动解决方案** - 让用户在浏览器中手动完成验证
4. **等待用户确认** - 用户完成验证后继续自动化流程

**示例响应**：
```
检测到反爬机制：爱思唯尔网站显示了CAPTCHA验证页面。
请在浏览器中手动完成验证，完成后告诉我，我将继续操作。
```

**重要**：
- 保持浏览器前台运行，用户可以看到界面
- 不要尝试使用技术手段绕过验证
- 尊重网站的反爬虫策略
- 用户的手动干预是最可靠的解决方案

## Tool Call Budget

| Step | Tool Calls |
|------|-----------|
| Search | 1 (API) or 2 (recover SID + API) |
| Sort / Paginate | 1 (API) |
| Paper Details | 2 (navigate + evaluate_script) |
| View Full Text | 2-3 (navigate record + evaluate links + navigate publisher) |
| Download PDF | 1-2 (evaluate PDF status + optional click download) |
| Session Recovery | 1 (navigate to WoS) |

Typical complete flow (search → details → view → download): **6-8 tool calls**.
