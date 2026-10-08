---
name: latex-introduction-bibliography
description: Generate and manage a rigorous, real-citation bibliography for the Introduction section of a LaTeX academic manuscript by connecting to a user-provided Chrome instance that is already logged into Web of Science. Use this skill whenever the user has a .tex manuscript (especially in chemistry, chemical engineering, materials science, or molecular thermodynamics) and asks to add references, expand the literature review, insert citations, build a .bib file, or guarantee a minimum number of references in the Introduction. Trigger when you see phrases like "帮我加引用", "扩充参考文献", "至少 N 篇", "latex 参考文献", "introduction 文献", or when a user pastes a manuscript introduction and wants it supported by peer-reviewed literature.
argument-hint: "[path/to/manuscript.tex] [--bib path/to/output.bib] [--min-ref 50]"
user-invocable: true
disable-model-invocation: false
---

# LaTeX Introduction Bibliography Manager

This skill reads the Introduction of a LaTeX manuscript, extracts 5–10 thematic keywords, connects to a Chrome instance that the user has already launched and logged into Web of Science, extracts the active Web of Science session ID (SID), searches the Web of Science internal API for real peer-reviewed papers, and produces a BibTeX (`.bib`) file with `\cite{}` commands inserted at appropriate places in the Introduction.

**Key assumption:** The user is responsible for launching Chrome with remote debugging enabled and logging into Web of Science. This skill does **not** perform VPN connection, institutional portal navigation, or account login.

## When to use

- The user wants to expand the Introduction references of a LaTeX manuscript.
- The user specifies a minimum number of references (e.g., ≥50).
- The user asks to generate or update a `.bib` file from manuscript themes.
- The user needs citations inserted at contextually appropriate positions, not just appended.

## Dependencies

- The `wos-search` skill must be installed and available.
- A browser automation tool must be available through **either**:
  - pi-coding-agent's native Chrome extension tools (`chrome_navigate`, `chrome_evaluate`, `chrome_list_network_requests`, etc.), **or**
  - the `chrome-devtools` MCP server configured in `.mcp.json` / `@.mcp.json`.
- A Chrome browser must be running with the DevTools Protocol (CDP) exposed, typically at `http://127.0.0.1:9222`.
- The active Chrome tab must be on a logged-in Web of Science Core Collection page with a valid SID.
- The manuscript must use a BibTeX-compatible bibliography style (`.bst`) or accept a `\bibliography{...}` command.

## Prerequisites — hard gates

**Do not proceed to Step 1 until all of the following checks pass.** If any check fails, stop immediately, tell the user exactly what is missing, and ask them to fix it before continuing.

### Check 1: Browser automation capability

Verify that a browser automation stack is available. Acceptable in two forms:

#### Option A: pi-coding-agent native Chrome extension

If the current agent is **pi-coding-agent** and exposes native Chrome tools such as `chrome_navigate`, `chrome_evaluate`, `chrome_list_network_requests`, etc., this check passes. Run a lightweight probe (e.g., `chrome_list_network_requests` or `chrome_navigate` to `about:blank`). If the probe fails, ask the user to run `/chrome authorize` first.

#### Option B: Claude Code style MCP config with chrome-devtools

If Option A is not available, require a project-level MCP configuration:

1. Look for the project MCP configuration file. Check, in order:
   - `{project-root}/.mcp.json`
   - `{project-root}/@.mcp.json`
2. If neither file exists, **STOP**. Tell the user:
   > 当前不是 pi-coding-agent，也未找到 `.mcp.json`（或 `@.mcp.json`）。请配置 `chrome-devtools` MCP server，或切换到支持原生 Chrome 扩展的 pi-coding-agent。
3. Read the file. It must contain a top-level `mcpServers` object with a `chrome-devtools` entry, for example:
   ```json
   {
     "mcpServers": {
       "chrome-devtools": {
         "command": "npx",
         "args": [
           "-y",
           "chrome-devtools-mcp@latest",
           "--userDataDir=/path/to/your/chrome-profile"
         ]
       }
     }
   }
   ```
4. Verify that the MCP server is registered and reachable. Use `ListMcpResourcesTool` or a non-invasive ping. **Do not** call `mcp__chrome-devtools__list_pages` or `mcp__chrome-devtools__take_snapshot` as probes — these may conflict with an already-running Chrome instance launched by the MCP server itself.

If neither Option A nor Option B is available, **STOP**.

### Check 2: Chrome CDP connection and logged-in Web of Science session

1. Confirm the user has Chrome running with the DevTools Protocol exposed. The default CDP endpoint is:
   ```
   http://127.0.0.1:9222
   ```
   If the user is using a different CDP URL, ask them to provide it.
2. **Directly connect to the running Chrome instance using CDP. Do not launch, navigate, or snapshot.** Use the browser automation tool that is available:
   - pi-coding-agent: use `chrome_evaluate` on the current tab.
   - MCP `chrome-devtools`: use `mcp__chrome-devtools__evaluate_script` on the current page.
   - If your environment provides a `browser` tool with CDP mode, connect with:
     ```
     browser(app: { cdp_url: "http://127.0.0.1:9222" })
     ```
3. Verify the active tab is on `webofscience.com` and shows a logged-in Core Collection interface. The safest way is to evaluate a script that returns:
   - `window.location.href`
   - Whether the page contains a visible user name / profile menu and not a "Sign In" button.
   - Whether the page contains "Web of Science Free View", "Sign In", or "Register".
   If the page is not on `webofscience.com` or shows login indicators, **STOP**. Tell the user:
   > 当前 Chrome 中的 Web of Science 页面未登录或不在 webofscience.com。请手动在浏览器中完成登录（建议使用机构入口登录个人账号），然后让我继续。本 skill 不处理登录过程。
4. Extract the Web of Science session ID (SID). Evaluate a script on the page to obtain it, for example:
   - Parse `window.location.href` for the `SID` query parameter.
   - Inspect network request logs (`chrome_list_network_requests` or `mcp__chrome-devtools__list_network_requests`) for URLs containing `SID=`.
   - Read page globals / `localStorage` if SID is stored there.
   If no SID can be extracted, **STOP** and ask the user to refresh the Web of Science page or confirm they are on a search/results page.

> ⚠️ **Why this matters:** The `wos-search` skill calls the Web of Science internal API (`/api/wosnx/core/runQuerySearch?SID=<sid>`). Without a valid, personally authenticated SID, the API returns empty results or login redirects. This skill does **not** perform login, VPN, or page navigation.

## Workflow

### Step 0: Pre-flight checks (MUST pass before continuing)

Run **Check 1** (browser automation available) and **Check 2** (Chrome running with CDP + logged-in WoS page + SID extracted). If either fails, stop and report the failure. Do not attempt to search Web of Science or modify the manuscript until both checks pass.

### Step 1: Read the manuscript Introduction

1. Locate the manuscript file. Default to the `.tex` file the user provides, or the main `.tex` in the current directory.
2. Read only the content between `\section{Introduction}` and the next `\section{...}`. If the heading uses a variant such as `\section*{Introduction}`, `\section{引言}`, or `\section{绪论}`, use regex `\\section\\*?\\{[^}]*[Ii]ntroduction[^}]*\\}` or fall back to Chinese variants.
3. Extract the scientific narrative and identify 5–10 distinct thematic keywords or phrases. Aim for the concepts that actually need literature support:
   - broad context (e.g., carbon capture, CCS)
   - specific technologies (e.g., ionic liquids, deep eutectic solvents)
   - subclass of materials (e.g., choline-based DES)
   - theoretical/methodological concepts (e.g., COSMO-RS, Pitzer-Debye-Hückel, molecular dynamics)
   - application or problem (e.g., gas dehydration, CO₂ drying)
4. List the keywords to the user and ask for confirmation before searching, unless the user has already provided explicit keywords or told you to proceed automatically.

### Step 2: Search Web of Science for each keyword

**Before the first `wos-search` call**, re-verify the active Chrome tab is still on a logged-in Web of Science page and the SID is still valid. If the session appears expired (login prompt, "Free View", or 401/redirect responses), **STOP** and ask the user to refresh the page and re-login.

For each confirmed keyword, call the `wos-search` skill via the Skill tool. Pass the extracted SID so the skill can call the WoS internal API:

```
Skill: wos-search
Args: <English search query> --sid <SID> [--edition SCI/SSCI] [--sort citations|date|relevance] [--db woscc]
```

Guidelines for building queries:
- Translate Chinese keywords to English before searching.
- Prefer focused queries tied to the manuscript domain. For example:
  - `CO2 capture and storage CCS energy penalty`
  - `ionic liquids gas drying dehydration`
  - `deep eutectic solvents CO2 capture`
  - `choline chloride deep eutectic solvents`
  - `COSMO-RS deep eutectic solvents`
  - `Pitzer Debye Huckel electrolyte solution model`
- Use `--sort citations` for landmark/overview papers and `--sort date` for recent work.
- Request enough results so that you can select the most relevant 5+ papers per keyword. A good default is to retrieve 10–15 records.

If `wos-search` returns an authentication error, empty results with a login redirect, or any response indicating the session is no longer valid, **STOP** immediately. Do not retry with broader queries. Tell the user:
> Web of Science 会话已失效（SID 无效或已过期）。请在 Chrome 中刷新页面并重新登录，然后再继续。

If `wos-search` returns 0 useful results, refine the query (broader terms, alternate synonyms) and try once more. Do not invent papers.

### Step 3: Select and verify papers

For each keyword, select at least 5 relevant papers from the search results. Selection criteria:
1. **Topical fit**: title/abstract clearly supports the sentence or claim in the Introduction.
2. **Recency and authority**: mix highly cited foundational work with recent reviews or applications (last 5–10 years where possible).
3. **Verifiability**: each paper must have a WoS ID, DOI, or at minimum a journal, year, volume, and pages. If a result lacks these, skip it.
4. **No duplication**: the same paper may support multiple keywords, but it should appear only once in the final `.bib` file. Use a single BibTeX key and cite it in multiple places if appropriate.

Keep a selection log mapping each chosen paper to the keyword and the claim it supports.

### Step 4: Build BibTeX entries

Generate a `.bib` file using a single consistent key style, for example:

```bibtex
@article{AuthorYearKeyword,
  author  = {A. Author and B. Author},
  title   = {Title of the Paper},
  journal = {Journal Name},
  year    = {2024},
  volume  = {10},
  number  = {2},
  pages   = {100--110},
  doi     = {10.xxxx/xxxxx},
}
```

- Use `article` for journal papers and `book`/`inbook` only if the source is genuinely a book.
- Preserve special characters using LaTeX escapes (e.g., `\\"{u}`, `\\&`).
- If the manuscript uses a numbered citation style (AMA, Vancouver, etc.), the keys are arbitrary, but keep them short and stable.
- If a DOI is available, include it.

### Step 5: Insert `\cite{}` commands in the Introduction

Re-read the Introduction and insert `\cite{key1,key2,...}` at the exact locations where each paper provides support:

- Use multiple keys inside one `\cite{}` when several sources support the same claim: `\cite{key1,key2,key3}`.
- Place citations at the end of the relevant sentence, before the period.
- Do not insert citations randomly; each citation must clearly support the preceding clause or sentence.
- If a paragraph makes several distinct claims, distribute citations accordingly rather than stacking them all at the end.
- Ensure the total number of unique references in the generated `.bib` meets or exceeds the requested minimum (default 50). If the keywords yield fewer than 50, add one or two additional related keywords and repeat Step 2.

### Step 6: Write outputs and validate

1. Write the `.bib` file to the path requested by the user, or default to `<manuscript-name>-references.bib` in the same directory as the manuscript.
2. If the user wants the citations embedded in the `.tex` file, write an updated `.tex` file (or a patch) with the `\cite{}` commands inserted. Otherwise, present the insertion plan so the user can apply it manually.
3. Run a quick consistency check:
   - Count unique BibTeX keys.
   - Count `\cite{}` commands.
   - Confirm every key cited appears in the `.bib` file.
   - Confirm the requested minimum reference count is met.
4. Report a short summary to the user: number of keywords, number of papers found, number of unique references, and the output file paths.

## Output format

Report using this template:

```markdown
## Bibliography generation summary
- Manuscript: `{path}`
- Keywords searched: {N}
- Total unique references generated: {N} (requested minimum: {N})
- `.bib` file: `{path}`
- Updated `.tex` (if written): `{path}`

### Keyword coverage
| Keyword | Papers selected | Example key |
|---|---|---|
| ... | ... | ... |

### Next steps
- Compile the manuscript with LaTeX/BibTeX to generate the formatted reference list.
- Review citations in context; move or remove any that feel misplaced.
```

## 🛟 Failure modes & fallback tree

## 🔴 Gate failures (Pre-flight)

| Trigger condition | First-line fix | Still fails → escalation |
|---|---|---|
| Browser automation unavailable | Detect pi-coding-agent native Chrome tools. If yes, ask user to run `/chrome authorize`. If no, ask user: "需要我帮你创建 `.mcp.json` 模板吗？（含 `chrome-devtools` MCP server 配置）" | **STOP** — 告知用户手动创建 `.mcp.json` 或切换到 pi-coding-agent 后再试 |
| `.mcp.json` lacks valid chrome-devtools config (Option B only) | Ask user for Chrome profile path or correct MCP config | **STOP** — guide user to fix MCP config |
| Chrome is not running with CDP at `127.0.0.1:9222` | Ask user to launch Chrome with `--remote-debugging-port=9222` and provide the correct CDP URL if different | **STOP** — skill cannot launch Chrome for the user |
| Probe tools (`list_pages`, `take_snapshot`) error with "browser already running" | This is expected when MCP server already owns Chrome. Switch to direct CDP evaluate — do **not** retry those probes | Use `evaluate_script` / `chrome_evaluate` directly on the current tab |
| Active Chrome tab is not on `webofscience.com` | Ask user to navigate to Web of Science and log in | **STOP** — skill does not perform navigation/login |
| Web of Science page is not logged in (Sign In / Free View shown) | Ask user to complete personal login in Chrome | **STOP** — skill does not perform login |
| SID cannot be extracted | Ask user to refresh the WoS page or perform a search so `SID=` appears in the URL/network requests | **STOP** — API calls require SID |
| `wos-search` returns auth error / empty results due to expired SID | Re-check Chrome tab; ask user to refresh and re-login | **STOP** — do not retry searches until session is restored |

## 🔴 Search failures (Step 2)

| Trigger condition | First-line fix | Still fails → escalation |
|---|---|---|
| `wos-search` returns 0 results | Broaden query: drop the narrowest term, use synonyms, or remove year/field filters | If still 0 after 2 refinements → **STOP** for that keyword, note to user: "`{keyword}` 未搜到相关文献，跳过该关键词" |
| `wos-search` returns <5 relevant results per keyword | Lower relevance threshold; include partially relevant papers; switch from `--sort citations` to `--sort relevance` | If still <5 → merge this keyword into an adjacent one and redistribute papers |
| `wos-search` returns results missing DOI / volume / pages | Use `wos-paper-detail` with the WoS ID to fetch full metadata | If `wos-paper-detail` also incomplete → still include the entry with available fields; mark with `⚠️ incomplete metadata` in the selection log |
| All results from a keyword already selected (duplicate) | Reuse existing BibTeX key; count paper for that keyword without adding a new entry | N/A — this is the correct behavior |

## 🔴 Execution failures (Steps 3–6)

| Trigger condition | First-line fix | Still fails → escalation |
|---|---|---|
| `\section{Introduction}` not found in .tex | Try `\section*{Introduction}` or Chinese headings "引言" / "绪论" via regex | **Ask user** to point out where the Introduction section begins |
| Manuscript already has a `.bib` file with existing `\bibliography{...}` | Read existing `.bib`, build a set of existing keys — avoid duplicates with `-suffix` (e.g. `Author2023b`) | Conflict on >10 keys → output a merge report and ask user to pick |
| Total unique refs < user minimum after all keywords | If user has NOT forbidden adding keywords: suggest 1–2 supplementary derived from broader context. If user HAS constrained keywords: do NOT add. | If permission denied or keywords exhausted → report: "仅搜到 {N} 篇唯一引用（目标 {M} 篇），建议接受或补充更多关键词" |
| User has no .tex manuscript (BibTeX-only request) | Flag to user: "未提供 .tex 文件，只能输出纯 bib 条目而无法插入 `\cite{}`。仍继续?"; ask for output path for `.bib` file | If user insists on citations → ask them to paste the Introduction text manually |

## 🚫 Anti-patterns blacklist — do NOT do these

| # | 🚫 Anti-pattern | Why it fails | ✅ Correct alternative |
|---|---|---|---|
| 1 | Fabricate references or papers | Undermines manuscript credibility; reviewers will catch it | Every paper must come from `wos-search` or another verifiable source |
| 2 | Stack unrelated citations at paragraph end | Reader can't tell which paper supports which claim | Distribute citations per claim; use multiple `\cite{}` across the paragraph |
| 3 | Search Chinese keywords directly in WoS | WoS index is English; returns 0 or irrelevant results | Translate all keywords to English before searching |
| 4 | Overwrite existing `.bib` without checking | Destroys user's existing reference collection | Read existing `.bib` first, append new entries, use `-suffix` for duplicate keys |
| 5 | Silently add extra keywords when user forbids it | Violates user intent | Respect constraint; report shortfall and ask permission before expanding |
| 6 | Attempt to log in to Web of Science for the user | This skill is not authorized to handle credentials, MFA, or institutional portals | Ask the user to log in manually in Chrome before starting |
| 7 | Skip the SID extraction and call `wos-search` blindly | API will return empty or login-redirect responses | Always extract SID from the logged-in WoS page in Step 0 |
| 8 | Write `.bib` with incomplete entries (missing DOI/vol/pages) | BibTeX compilation fails or produces warnings | Try `wos-paper-detail` to fill missing fields; warn user if still incomplete |
| 9 | Insert citations without re-reading the Introduction | Citations placed randomly, supporting nothing | Re-read text; insert each `\cite{}` at the exact clause it supports |
| 10 | Use `list_pages` / `take_snapshot` as connectivity probes | These tools may conflict with an already-running Chrome instance launched by the MCP server and can reset or error out | Use non-invasive probes (`ListMcpResourcesTool`) or direct CDP `evaluate_script` / `chrome_evaluate` |

## Important rules

- **This skill does not log in to Web of Science.** The user must manually launch Chrome, navigate to Web of Science, and complete personal login before invoking this skill.
- **Always run the pre-flight checks first.** No browser automation or no valid logged-in WoS session/SID means the skill must not continue.
- **Never fabricate references.** Every paper must come from `wos-search` or another verifiable source.
- **Translate Chinese queries to English** before calling `wos-search`.
- **Do not stack unrelated citations** just to hit a number. Each citation must support the text.
- **Respect the manuscript's existing references.** If a `.bib` file already exists, append new entries rather than overwriting, and avoid duplicate keys.
