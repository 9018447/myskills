#!/usr/bin/env python3
"""deep-research 可信驱动：preflight / broad-search / deep-dive / synthesize / repair / verify / assert-passed / finalize / selftest。

编排者给出计划的网络深入研究：契约 .agent/luna/task.json，产物 .agent/luna/research/<task_id>/。
流程：计划→广域搜索→逐子方向深潜→综合闭环；AI（codex）只提查询、读结果、写产出，不接触网络。

裁决约定：verify 恒以 0 退出（引擎对非零 shell 退出直接判失败，不进修复分支），
裁决写入 verify.json（结构为 {verdict, failures, attempt}），stdout 末行输出 VERDICT=<pass|repairable|fatal>；
assert-passed 读取 verify.json 强制终态，绕过裁决即失败。

安全边界：搜索/抓取全部由本脚本用 python 标准库确定性调用 metaso HTTP API
（Bearer $METASO_API_KEY，密钥只从环境读取、绝不落盘）；AI 产出只经文件传递
（prompts/、logs/、queries/、fetch-requests/、notes/、findings/、report.md），
本脚本从不把 AI 输出拼进 shell 命令。可测函数与 subprocess/codex 调用解耦，selftest 离线自测。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

REPO = os.getcwd()
CONTRACT_PATH = ".agent/luna/task.json"
MODEL = "gpt-6-luna"
WORKFLOW_ID = "deep-research"
OUT_ROOT = ".agent/luna/research"
SEARCH_URL = "https://metaso.cn/api/v1/search"
READER_URL = "https://metaso.cn/api/v1/reader"
SCOPES_ALLOWED = {"webpage", "news", "wechat", "arxiv", "github"}
CITE_RE = re.compile(r"\[S(\d+)\]")


def fail(msg, code=2):
    print(f"[deep-research] FATAL: {msg}", file=sys.stderr)
    sys.exit(code)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def is_http_url(u):
    return isinstance(u, str) and (u.startswith("http://") or u.startswith("https://"))


def normalize_url(url):
    """URL 归一化：去 fragment、去尾斜杠；用于来源去重。"""
    u = (url or "").strip()
    if "#" in u:
        u = u.split("#", 1)[0]
    while u.endswith("/"):
        u = u[:-1]
    return u


# ---------------------------------------------------------------- 路径与越界

def rel_errors(rel, repo):
    """契约内相对路径的纯校验（不退出）：拒绝绝对路径、..、符号链接逃逸。"""
    errs = []
    if not isinstance(rel, str) or not rel.strip():
        return ["契约路径须为非空字符串"]
    if os.path.isabs(rel) or ".." in rel.split(os.sep) or ".." in rel.split("/"):
        errs.append(f"契约路径非法（绝对路径或 ..）: {rel}")
    else:
        real = os.path.realpath(os.path.join(repo, rel))
        if real != repo and not real.startswith(repo + os.sep):
            errs.append(f"契约路径符号链接逃逸: {rel}")
    return errs


def safe_rel(rel):
    """校验契约内相对路径并返回仓库内绝对路径；非法即退出。"""
    errs = rel_errors(rel, REPO)
    if errs:
        fail("; ".join(errs))
    return os.path.realpath(os.path.join(REPO, rel))


def porcelain_paths(repo):
    out = subprocess.run(
        ["git", "status", "--porcelain", "-z"], cwd=repo, capture_output=True, check=True
    ).stdout
    records = [os.fsdecode(r) for r in out.split(b"\0")]
    paths = set()
    i = 0
    while i < len(records):
        rec = records[i]
        i += 1
        if not rec:
            continue
        paths.add(rec[3:])
        if "R" in rec[:2] or "C" in rec[:2]:
            # -z 模式重命名/复制条目为两条记录：带 XY 前缀的是新路径，下一条裸记录是旧路径，跳过
            i += 1
    return paths


def violates(path, roots):
    """越界判定：path 不在任一白名单根之下、也不是白名单根的祖先目录才算越界。

    porcelain 会把全新未跟踪子树折叠到最上层未跟踪目录（如产物目录的父级），
    该祖先条目可能在 preflight 之后才首次出现，不代表产物目录之外的写入。
    """
    p = path.rstrip("/") + "/"
    for r in roots:
        rp = r.rstrip("/") + "/"
        if p.startswith(rp) or rp.startswith(p):
            return False
    return True


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- 契约校验

def check_contract(raw, repo=REPO):
    """契约纯校验：返回 (errors, normalized)。errors 为空即合法；不退出、不做 I/O。"""
    errs = []
    if not isinstance(raw, dict):
        return ["契约必须是 JSON 对象"], {}
    c = dict(raw)

    tid = c.get("task_id")
    if not isinstance(tid, str) or not tid.strip():
        errs.append("契约缺少必填字段 task_id")
    elif not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", tid):
        errs.append("task_id 只允许字母数字与 . _ -")
    for k in ("topic", "objective"):
        if not isinstance(c.get(k), str) or not c.get(k).strip():
            errs.append(f"契约缺少必填字段 {k}")

    dirs = c.get("directions")
    if not isinstance(dirs, list) or not (1 <= len(dirs) <= 12):
        errs.append("directions 须为 1..12 个")
        dirs = []
    seen = set()
    for i, d in enumerate(dirs):
        if not isinstance(d, dict):
            errs.append(f"directions[{i}] 须为对象")
            continue
        did = d.get("id")
        if not isinstance(did, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,15}", did):
            errs.append(f"directions[{i}] id 非法: {did!r}")
        else:
            if did in seen:
                errs.append(f"方向 id 重复: {did}")
            seen.add(did)
        if not isinstance(d.get("title"), str) or not d.get("title").strip():
            errs.append(f"方向 {did or i} 缺 title")
        qs = d.get("questions")
        if not isinstance(qs, list) or not (1 <= len(qs) <= 8):
            errs.append(f"方向 {did or i} questions 须为 1..8 条")
        elif any(not isinstance(q, str) or not q.strip() for q in qs):
            errs.append(f"方向 {did or i} questions 含空条目")

    scopes = c.get("scopes")
    if scopes is None:
        scopes = ["webpage"]
    if not isinstance(scopes, list) or not scopes or not set(scopes) <= SCOPES_ALLOWED:
        errs.append(f"scopes 须为非空子集于 {sorted(SCOPES_ALLOWED)}")
    else:
        c["scopes"] = scopes

    def num(key, lo, hi, default):
        v = c.get(key, default)
        if not isinstance(v, int) or isinstance(v, bool):
            errs.append(f"契约字段 {key} 须为整数")
            return default
        if not (lo <= v <= hi):
            errs.append(f"契约字段 {key}={v} 超出范围 [{lo},{hi}]")
            return default
        return v

    c["broad_queries"] = num("broad_queries", 1, 6, 4)
    c["queries_per_direction"] = num("queries_per_direction", 1, 6, 3)
    c["size_per_query"] = num("size_per_query", 1, 10, 10)
    c["max_searches"] = num("max_searches", 1, 1000000, 24)
    c["max_fetches"] = num("max_fetches", 0, 30, 8)
    c["fulltext_max_chars"] = num("fulltext_max_chars", 1, 10000000, 40000)
    c["max_attempts"] = num("max_attempts", 1, 50, 2)
    c["step_timeout_seconds"] = num("step_timeout_seconds", 60, 86400, 1200)
    c["timeout_seconds"] = num("timeout_seconds", 60, 86400, 5400)
    plan_budget = c["broad_queries"] + len(dirs) * c["queries_per_direction"]
    if c["max_searches"] < plan_budget:
        errs.append(f"max_searches={c['max_searches']} 小于计划搜索预算 {plan_budget}"
                    "（broad_queries + 方向数×queries_per_direction），请修改计划")

    pf = c.get("plan_file")
    if pf is not None:
        if not isinstance(pf, str) or not pf.strip():
            errs.append("plan_file 须为非空字符串或 null")
        else:
            errs.extend(rel_errors(pf, repo))
    else:
        c["plan_file"] = None

    awp = c.get("allowed_write_paths", [])
    if not isinstance(awp, list):
        errs.append("allowed_write_paths 须为数组")
    else:
        for rel in awp:
            errs.extend(rel_errors(rel, repo))
        c["allowed_write_paths"] = awp
    c.setdefault("constraints", [])
    return errs, c


def contract():
    p = os.path.join(REPO, CONTRACT_PATH)
    if not os.path.isfile(p):
        fail(f"缺少任务契约 {CONTRACT_PATH}")
    try:
        raw = read_json(p)
    except Exception as e:
        fail(f"契约不是合法 JSON: {e}")
    errs, c = check_contract(raw)
    if errs:
        fail("契约校验失败: " + "; ".join(errs))
    pf = c.get("plan_file")
    if pf and not os.path.isfile(safe_rel(pf)):
        fail(f"plan_file 不存在: {pf}")
    return c


def outdir_of(c):
    return os.path.join(REPO, OUT_ROOT, c["task_id"])


def plan_abs(c):
    pf = c.get("plan_file")
    return safe_rel(pf) if pf else None


def attempts(od):
    p = os.path.join(od, "attempts.json")
    if os.path.isfile(p):
        return int(read_json(p)["attempts"])
    return 0


# ---------------------------------------------------------------- sources.json

def sources_path(od):
    return os.path.join(od, "sources.json")


def load_sources(od):
    p = sources_path(od)
    if os.path.isfile(p):
        return read_json(p)
    return {"sources": [], "searches": [], "search_failures": [],
            "search_dropped": [], "fetches": [], "fetch_failures": [],
            "fetch_dropped": [], "budget": {"used": 0, "max": 0}}


def write_sources(od, src):
    write_json(sources_path(od), src)


def ensure_sources(od, c):
    p = sources_path(od)
    if not os.path.isfile(p):
        write_sources(od, {"sources": [], "searches": [], "search_failures": [],
                           "search_dropped": [], "fetches": [], "fetch_failures": [],
                           "fetch_dropped": [], "budget": {"used": 0, "max": c["max_searches"]}})
    else:
        src = read_json(p)
        src.setdefault("budget", {"used": 0, "max": c["max_searches"]})
        write_sources(od, src)


def qid_number(qid):
    m = re.fullmatch(r"q(\d+)", str(qid or ""))
    return int(m.group(1)) if m else 0


def next_qid(src):
    used = 0
    for key in ("searches", "search_failures", "search_dropped"):
        for rec in src.get(key, []) or []:
            used = max(used, qid_number(rec.get("qid")))
    return "q" + str(used + 1)


def qid_seq(start, count):
    n = qid_number(start)
    return ["q" + str(n + i) for i in range(count)]


def register_search_results(src, webpages, scope, qid, direction):
    """按归一化 URL 去重登记来源，sid 全局递增 S1..Sk；返回新增条数。"""
    added = 0
    for w in webpages:
        url = str(w.get("link") or "").strip()
        if not is_http_url(url):
            continue
        nurl = normalize_url(url)
        entry = next((s for s in src["sources"] if s["url"] == nurl), None)
        if entry is None:
            src["sources"].append({
                "sid": "S" + str(len(src["sources"]) + 1),
                "url": nurl,
                "title": str(w.get("title") or ""),
                "snippet": str(w.get("snippet") or ""),
                "summary": str(w.get("summary") or ""),
                "date": str(w.get("date") or ""),
                "scope": scope,
                "query_ids": [qid],
                "direction": direction,
            })
            added += 1
        else:
            if qid not in entry["query_ids"]:
                entry["query_ids"].append(qid)
    return added


def record_search_success(src, qid, q, scope, direction, count, at, max_searches):
    src.setdefault("searches", []).append({
        "qid": qid, "q": q, "scope": scope, "direction": direction,
        "count": count, "ok": True, "at": at})
    src.setdefault("budget", {})
    src["budget"]["used"] = len(src["searches"])
    src["budget"]["max"] = max_searches
    return src


def record_search_failure(src, qid, q, scope, direction, error, at):
    src.setdefault("search_failures", []).append({
        "qid": qid, "q": q, "scope": scope, "direction": direction,
        "count": 0, "ok": False, "at": at, "error": error})
    return src


def record_search_dropped(src, item, direction, reason):
    src.setdefault("search_dropped", []).append({
        "qid": item["qid"], "q": item["q"], "scope": item["scope"],
        "direction": direction, "reason": reason, "at": utc_now()})
    return src


def budget_ok(src, c):
    return src["budget"].get("used", 0) < int(c["max_searches"])


def record_fetch_ok(src, sid, url, at):
    src.setdefault("fetches", []).append({"sid": sid, "url": url, "ok": True, "at": at})
    return src


def record_fetch_fail(src, sid, url, error, at):
    src.setdefault("fetch_failures", []).append(
        {"sid": sid, "url": url, "ok": False, "at": at, "error": error})
    return src


def record_fetch_dropped(src, sid, reason):
    src.setdefault("fetch_dropped", []).append(
        {"sid": sid, "reason": reason, "at": utc_now()})
    return src


# ---------------------------------------------------------------- 提案校验

def validate_queries_proposal(obj, limit, allowed_scopes):
    """查询提案 schema 校验：{queries: [{q, scope?}]}，1..limit 条。"""
    errs = []
    if not isinstance(obj, dict) or not isinstance(obj.get("queries"), list):
        return False, ["queries 须为数组"]
    qs = obj["queries"]
    if not qs:
        return False, ["queries 不能为空"]
    if len(qs) > limit:
        return False, [f"查询数 {len(qs)} 超过上限 {limit}"]
    for i, it in enumerate(qs):
        if not isinstance(it, dict):
            errs.append(f"queries[{i}] 须为对象")
            continue
        q = it.get("q")
        if not isinstance(q, str) or not q.strip():
            errs.append(f"queries[{i}] 缺非空 q")
        scope = it.get("scope", "webpage")
        if scope not in allowed_scopes:
            errs.append(f"queries[{i}] scope 非法: {scope!r}（允许 {sorted(allowed_scopes)}）")
    return (not errs), errs


def canonicalize_queries(obj, direction_id, start_qid):
    """改写为 canonical：分配全局唯一 qid、补齐默认 scope。"""
    qids = qid_seq(start_qid, len(obj["queries"]))
    out = []
    for qid, it in zip(qids, obj["queries"]):
        out.append({"qid": qid, "q": str(it.get("q") or "").strip(),
                    "scope": it.get("scope") or "webpage"})
    return {"direction": direction_id, "queries": out}


def validate_fetch_proposal(obj):
    """fetch 提案 schema 校验：{sids: ["S1", ...]}（sid 存在性在过滤阶段处理）。"""
    errs = []
    if not isinstance(obj, dict) or not isinstance(obj.get("sids"), list):
        return False, ["sids 须为数组"]
    for i, s in enumerate(obj["sids"]):
        if not isinstance(s, str) or not re.fullmatch(r"S\d+", s):
            errs.append(f"sids[{i}] 非法: {s!r}（须为 S<数字>）")
    return (not errs), errs


def filter_fetch_sids(sids, known, already, remaining):
    """纯过滤：已知且未抓取者按顺序进入 pending，超出剩余预算者 dropped，未知者跳过。"""
    pending, skipped = [], []
    for sid in sids:
        if sid not in known:
            skipped.append(sid)
            continue
        if sid in already:
            continue
        pending.append(sid)
    dropped = pending[remaining:] if remaining < len(pending) else []
    pending = pending[:remaining] if remaining < len(pending) else pending
    return pending, dropped, skipped


# ---------------------------------------------------------------- metaso 调用（可信脚本，不经 AI）

def http_post(url, body, headers, timeout=30):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def metaso_headers():
    key = os.environ.get("METASO_API_KEY", "")
    return {"Authorization": "Bearer " + key, "Content-Type": "application/json"}


def run_search(c, od, qid, q, scope, direction):
    """执行一次搜索：失败重试 1 次，仍失败记 raw/<qid>.json={"ok":false} 且不计预算。"""
    src = load_sources(od)
    raw_dir = os.path.join(od, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    body = {"q": q, "scope": scope, "includeSummary": True,
            "size": str(c["size_per_query"]), "includeRawContent": False,
            "conciseSnippet": True}
    resp, err = None, None
    for _ in range(2):
        try:
            status, data = http_post(SEARCH_URL, body, metaso_headers(), 30)
            if status == 200:
                resp = json.loads(data.decode("utf-8"))
                break
            err = f"HTTP {status}"
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
    at = utc_now()
    if resp is not None and isinstance(resp, dict) and isinstance(resp.get("webpages"), list):
        write_json(os.path.join(raw_dir, qid + ".json"), resp)
        added = register_search_results(src, resp["webpages"], scope, qid, direction)
        record_search_success(src, qid, q, scope, direction, len(resp["webpages"]), at,
                              c["max_searches"])
        write_sources(od, src)
        print(f"[deep-research] 搜索 {qid}: scope={scope} count={len(resp['webpages'])} 新增来源={added}")
        return True
    if resp is not None:
        write_json(os.path.join(raw_dir, qid + ".json"), resp)
    else:
        write_json(os.path.join(raw_dir, qid + ".json"), {"ok": False, "qid": qid, "error": err})
    record_search_failure(src, qid, q, scope, direction, err or "响应无 webpages 列表", at)
    write_sources(od, src)
    print(f"[deep-research] 搜索失败 {qid}: {err}", file=sys.stderr)
    return False


def fetch_fulltext(c, od, sid):
    src = load_sources(od)
    entry = next((s for s in src["sources"] if s["sid"] == sid), None)
    if entry is None:
        return False
    headers = metaso_headers()
    headers["Accept"] = "text/plain"
    body = {"url": entry["url"]}
    err = None
    try:
        status, data = http_post(READER_URL, body, headers, 30)
        if status == 200:
            text = data.decode("utf-8", errors="replace")[: c["fulltext_max_chars"]]
            os.makedirs(os.path.join(od, "fulltext"), exist_ok=True)
            with open(os.path.join(od, "fulltext", sid + ".txt"), "w", encoding="utf-8") as f:
                f.write(text)
            record_fetch_ok(src, sid, entry["url"], utc_now())
            write_sources(od, src)
            print(f"[deep-research] 抓取 {sid}: {len(text)} 字符")
            return True
        err = f"HTTP {status}"
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
    record_fetch_fail(src, sid, entry["url"], err, utc_now())
    write_sources(od, src)
    print(f"[deep-research] 抓取失败 {sid}: {err}", file=sys.stderr)
    return False


def process_fetch_proposal(c, od, stage, proposal_path, t0=None):
    """读取 codex 的 fetch 提案并执行抓取；schema 非法重提 1 次，仍失败 fatal。"""
    if not os.path.isfile(proposal_path):
        print(f"[deep-research] {stage}: 无 fetch 提案，跳过")
        return
    obj = read_json(proposal_path)
    ok, errs = validate_fetch_proposal(obj)
    if not ok:
        prompt = build_fetch_fix_prompt(c, od, stage, proposal_path, errs)
        call_id = f"{stage}-fetch-fix"
        run_one(c, od, call_id, prompt, t0)
        obj = read_json(proposal_path)
        ok, errs = validate_fetch_proposal(obj)
        if not ok:
            fail(f"{stage} fetch 提案两次校验失败: {errs}")
    src = load_sources(od)
    known = {s["sid"] for s in src["sources"]}
    already = {s["sid"] for s in src.get("fetches", [])}
    remaining = max(0, c["max_fetches"] - len(src.get("fetches", [])))
    pending, dropped, skipped = filter_fetch_sids(obj["sids"], known, already, remaining)
    for sid in skipped:
        print(f"[deep-research] {stage}: 跳过未知 sid {sid}", file=sys.stderr)
    for sid in dropped:
        src = load_sources(od)
        record_fetch_dropped(src, sid, "budget")
        write_sources(od, src)
        print(f"[deep-research] {stage}: 抓取超预算，丢弃 {sid}", file=sys.stderr)
    for sid in pending:
        fetch_fulltext(c, od, sid)


# ---------------------------------------------------------------- codex 调用

def check_stage_timeout(c, t0):
    if t0 is not None and time.monotonic() - t0 > c["timeout_seconds"]:
        fail(f"研究阶段超时（>{c['timeout_seconds']}s）")


def write_prompt(od, call_id, text):
    d = os.path.join(od, "prompts")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, call_id + ".md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def run_codex(c, od, call_id, prompt_path):
    """acpx 固定调用 codex；stdout/stderr 落 logs/<call-id>.log；超时或非 0 退出 fatal。"""
    log_dir = os.path.join(od, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, call_id + ".log")
    cmd = ["acpx", "--cwd", REPO, "--approve-all", "--model", MODEL,
           "codex", "exec", "-f", os.path.abspath(prompt_path)]
    with open(log_path, "wb") as log:
        try:
            r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT,
                               timeout=c["step_timeout_seconds"])
        except subprocess.TimeoutExpired:
            fail(f"执行器超时（>{c['step_timeout_seconds']}s），日志: {log_path}")
    if r.returncode != 0:
        fail(f"执行器退出码 {r.returncode}，日志: {log_path}")


def run_one(c, od, call_id, prompt_text, t0=None):
    check_stage_timeout(c, t0)
    p = write_prompt(od, call_id, prompt_text)
    run_codex(c, od, call_id, p)
    return p


def propose_json(c, od, base_call_id, first_prompt, out_file, validator, t0=None):
    """codex 产出 JSON 提案；校验失败附错误说明重提 1 次；仍失败 fatal（不算 repair attempt）。"""
    obj, retry_notes = None, None
    for i in range(2):
        call_id = base_call_id if i == 0 else f"{base_call_id}-retry"
        prompt = first_prompt if retry_notes is None else first_prompt + retry_notes
        run_one(c, od, call_id, prompt, t0)
        if not os.path.isfile(out_file):
            if i == 1:
                fail(f"{base_call_id}: 未产出 {out_file}")
            retry_notes = f"\n\n## 上次输出缺失\n未找到输出文件 {out_file}，请把结果写入该文件。"
            continue
        try:
            obj = read_json(out_file)
        except Exception as e:
            if i == 1:
                fail(f"{base_call_id}: {out_file} 不是合法 JSON: {e}")
            retry_notes = f"\n\n## 上次输出非法\n{out_file} 不是合法 JSON: {e}。请重写该文件。"
            continue
        ok, errs = validator(obj)
        if ok:
            return obj
        retry_notes = (f"\n\n## 上次输出校验失败\n- " + "\n- ".join(errs)
                       + f"\n请重写 {out_file}，仅修改该文件。")
    fail(f"{base_call_id}: JSON 提案两次校验失败: {errs}")


# ---------------------------------------------------------------- prompt 模板（全中文）

def _preamble(c):
    return [
        "你是网络深度研究流水线中的执行者。当前工作目录（cwd）是一个 git 仓库，研究产物都在其中。",
        "## 硬性规则",
        "- 只读本 prompt 列出的文件；绝不访问网络、绝不发起任何搜索或全文抓取。",
        "- 只写本 prompt 指定的产物文件；不得创建、修改、删除任何其他文件。",
        "- 引用一律用 [S<数字>] 形式，数字必须对应 sources.json 里真实存在的 sid。",
    ]


def _plan_line(plan_abs):
    if plan_abs:
        return f"- {plan_abs}（编排者研究计划，只读）"
    return "- （本任务未提供 plan_file）"


def build_source_digest(sources, cap=60):
    lines = ["## 来源清单（S<sid> | url | title）"]
    if len(sources) > cap:
        sources = sources[:cap]
        lines.append("（列表过长，仅显示前 %d 条）" % cap)
    for s in sources:
        summ = (s.get("summary") or "").replace("\n", " ")[:300]
        snip = (s.get("snippet") or "").replace("\n", " ")[:200]
        lines.append(f"- {s['sid']} | {s.get('url')} | {s.get('title') or ''}")
        if summ:
            lines.append(f"  摘要: {summ}")
        if snip:
            lines.append(f"  片段: {snip}")
    return "\n".join(lines)


def build_fulltext_index(od, src):
    lines = ["## 全文索引（已抓取正文的 sid）"]
    for s in src["sources"]:
        if os.path.isfile(os.path.join(od, "fulltext", s["sid"] + ".txt")):
            lines.append(f"- {s['sid']} | {s.get('url')}（正文已抓取，只读 fulltext/{s['sid']}.txt）")
    return "\n".join(lines)


def remaining_fetch(c, src):
    return max(0, c["max_fetches"] - len(src.get("fetches", [])))


def build_broad_queries_prompt(c, od, plan_abs):
    parts = _preamble(c) + [
        "",
        "## 阶段",
        "广域搜索：为整个研究主题提出覆盖多个角度的独立搜索查询。",
        "## 只读",
        f"- {os.path.join(REPO, CONTRACT_PATH)}（任务契约：topic、objective、scopes、broad_queries）",
        _plan_line(plan_abs),
        "## 任务",
        f"提出恰好 {c['broad_queries']} 条互不重叠、角度互补的查询（中文），覆盖主题的不同侧面。",
        "## 只写（绝对路径）",
        f"- {os.path.join(od, 'queries', 'broad.json')}",
        '结构：{"queries": [{"q": "查询", "scope": "webpage"}, ...]}',
        f"- q 为非空中文提问；scope ∈ {sorted(c['scopes'])}，省略默认 webpage。",
        f"- 恰好 {c['broad_queries']} 条。",
    ]
    return "\n".join(parts) + "\n"


def build_broad_notes_prompt(c, od, plan_abs):
    src = load_sources(od)
    parts = _preamble(c) + [
        "",
        "## 阶段",
        "广域搜索综述：阅读广域搜索命中结果，写综述笔记与全文抓取提案。",
        "## 只读",
        f"- {os.path.join(REPO, CONTRACT_PATH)}（任务契约）",
        _plan_line(plan_abs),
        f"- {os.path.join(od, 'queries', 'broad.json')}（canonical，含 qid）",
        f"- {os.path.join(od, 'sources.json')}（来源登记表，sid 是唯一事实源）",
        f"- 原始响应（需要时可读，只读）：{os.path.join(od, 'raw', '<qid>.json')}",
    ]
    parts += ["", build_source_digest(src["sources"])]
    parts += ["", build_fulltext_index(od, src)]
    parts += ["",
              "## 任务",
              f"1. 写 {os.path.join(od, 'notes', 'broad.md')}（≥500 字节）：综述广域发现与主题概貌，"
              "指出值得深挖的信号与矛盾；文中用 [S<数字>] 引用来源。",
              f"2. 写 {os.path.join(od, 'fetch-requests', 'broad.json')}："
              '{"sids": ["S1", ...]}，选择值得抓全文的来源 sid'
              f"（剩余全文预算 {remaining_fetch(c, src)} 条，含本次）。",
              "## 只写",
              f"- {os.path.join(od, 'notes', 'broad.md')}",
              f"- {os.path.join(od, 'fetch-requests', 'broad.json')}",
              ]
    return "\n".join(parts) + "\n"


def build_deep_queries_prompt(c, od, d):
    src = load_sources(od)
    parts = _preamble(c) + [
        "",
        "## 阶段",
        f"子方向 {d['id']}（{d['title']}）深潜：为回答该方向的问题提出聚焦查询。",
        "## 只读",
        f"- {os.path.join(REPO, CONTRACT_PATH)}（任务契约，本方向 questions 见下）",
        f"- {os.path.join(od, 'notes', 'broad.md')}（广域综述）",
        f"- {os.path.join(od, 'sources.json')}（已有来源登记表）",
    ]
    parts += ["", "## 已有来源摘要", build_source_digest(src["sources"])]
    parts += ["", "## 该方向要回答的问题",
              *[f"- {q}" for q in d["questions"]],
              "## 任务",
              f"提出恰好 {c['queries_per_direction']} 条聚焦查询（中文），"
              "补足广域阶段未覆盖的角度，避免与已有查询重复。",
              "## 只写",
              f"- {os.path.join(od, 'queries', d['id'] + '.json')}（结构同 broad）",
              ]
    return "\n".join(parts) + "\n"


def build_deep_findings_prompt(c, od, d):
    src = load_sources(od)
    new = [s for s in src["sources"] if s.get("direction") == d["id"]]
    parts = _preamble(c) + [
        "",
        "## 阶段",
        f"子方向 {d['id']}（{d['title']}）深潜：阅读新命中结果，写发现笔记。",
        "## 只读",
        f"- {os.path.join(REPO, CONTRACT_PATH)}（任务契约，本方向 questions 见下）",
        f"- {os.path.join(od, 'queries', d['id'] + '.json')}（canonical，含 qid）",
        f"- {os.path.join(od, 'notes', 'broad.md')}（广域综述）",
        f"- {os.path.join(od, 'sources.json')}（来源登记表，sid 是唯一事实源）",
    ]
    parts += ["", build_source_digest(new)]
    parts += ["", build_fulltext_index(od, src)]
    parts += ["", "## 该方向要回答的问题",
              *[f"- {q}" for q in d["questions"]],
              "## 任务",
              f"1. 写 {os.path.join(od, 'findings', d['id'] + '.md')}（≥300 字节）：逐条回答上述问题，"
              "每条回答至少 1 个 [S<数字>] 引用；标注证据不足或相互矛盾之处。",
              f"2. 写 {os.path.join(od, 'fetch-requests', d['id'] + '.json')}："
              '{"sids": ["S1", ...]}'
              f"（剩余全文预算 {remaining_fetch(c, src)} 条，含本次）。",
              "## 只写",
              f"- {os.path.join(od, 'findings', d['id'] + '.md')}",
              f"- {os.path.join(od, 'fetch-requests', d['id'] + '.json')}",
              ]
    return "\n".join(parts) + "\n"


def build_synthesize_prompt(c, od, plan_abs):
    parts = _preamble(c) + [
        "",
        "## 阶段",
        "综合：整合广域综述与全部子方向发现，写最终报告。",
        "## 只读",
        f"- {os.path.join(REPO, CONTRACT_PATH)}（任务契约：topic、objective、directions 顺序）",
        _plan_line(plan_abs),
        f"- {os.path.join(od, 'notes', 'broad.md')}",
        f"- {os.path.join(od, 'findings')}/*.md（全部子方向）",
        f"- {os.path.join(od, 'sources.json')}（来源登记表，sid 是唯一事实源）",
        f"- 全文正文（需要细读时，只读）：{os.path.join(od, 'fulltext')}/",
    ]
    parts += ["",
              "## 任务",
              f"写 {os.path.join(od, 'report.md')}（≥1000 字节）。章节固定，仅以下标题与顺序"
              "（方向节标题为方向 id 原文，按契约顺序）：",
              "# <自由标题>",
              "## 执行摘要",
              *[f"## {d['id']}" for d in c["directions"]],
              "## 交叉对比与矛盾",
              "## 证据缺口",
              "## 结论",
              f"正文引用一律 [S<数字>]；报告引用的不同来源数 ≥ {len(c['directions'])}；"
              "不得引用 sources.json 之外的 sid。",
              "## 只写",
              f"- {os.path.join(od, 'report.md')}",
              ]
    return "\n".join(parts) + "\n"


def build_repair_prompt(c, od, failures):
    parts = _preamble(c) + [
        "",
        "## 阶段",
        "修复：上一轮验收未通过，按失败明细修正产物文本。",
        "## 只读",
        f"- {os.path.join(od, 'verify.json')}（失败明细）",
        f"- {os.path.join(od, 'sources.json')}（只读事实源，禁止修改）",
        "## 失败明细",
        *[f"- {f}" for f in failures],
        "## 只写（仅以下文件，可新建或重写）",
        f"- {os.path.join(od, 'report.md')}",
        f"- {os.path.join(od, 'notes', 'broad.md')}",
        *[f"- {os.path.join(od, 'findings', d['id'] + '.md')}" for d in c["directions"]],
        "## 硬性规则",
        "- 本阶段没有任何搜索或抓取能力：禁止访问网络、禁止发起搜索。",
        "- 不得修改 sources.json、queries/、raw/、fulltext/、fetch-requests/ 或任何其他文件。",
        "- report.md 章节固定为：# <标题> → ## 执行摘要 → 每个 ## <方向id>（契约顺序）"
        "→ ## 交叉对比与矛盾 → ## 证据缺口 → ## 结论。",
        "- 所有 [S<数字>] 引用必须能解析到 sources.json 的 sid。",
    ]
    return "\n".join(parts) + "\n"


def build_fetch_fix_prompt(c, od, stage, proposal_path, errs):
    parts = _preamble(c) + [
        "",
        "## 阶段",
        f"修正 {stage} 阶段的全文抓取提案。",
        "## 只读",
        f"- {os.path.join(od, 'sources.json')}（来源登记表）",
        "## 校验失败明细",
        f"- 文件 {proposal_path} 不合法：",
        *[f"  - {e}" for e in errs],
        "## 任务",
        f"重写 {proposal_path}，结构：{{\"sids\": [\"S1\", ...]}}，"
        "sids 必须是 sources.json 中存在的 sid。",
        "## 只写",
        f"- {proposal_path}",
    ]
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- preflight

def cmd_preflight():
    c = contract()
    if shutil.which("git") is None:
        fail("git 不可用")
    subprocess.run(["git", "rev-parse", "--git-dir"], cwd=REPO,
                   capture_output=True, check=True)
    for tool in ("acpx", "codex", "python3"):
        if shutil.which(tool) is None:
            fail(f"执行器不可用: {tool}")
    if not os.environ.get("METASO_API_KEY", "").strip():
        fail("环境变量 METASO_API_KEY 未设置（必填；仅检查存在性，密钥不落盘）")
    od = outdir_of(c)
    for sub in ("prompts", "logs", "queries", "raw", "fulltext",
                "fetch-requests", "notes", "findings"):
        os.makedirs(os.path.join(od, sub), exist_ok=True)
    baseline = sorted(porcelain_paths(REPO))
    write_json(os.path.join(od, "baseline.json"), {"preexisting": baseline})
    write_json(os.path.join(od, "contract.snapshot.json"), c)
    if not os.path.isfile(os.path.join(od, "attempts.json")):
        write_json(os.path.join(od, "attempts.json"), {"attempts": 0})
    print(f"[deep-research] preflight OK: task={c['task_id']} outdir={od}")


# ---------------------------------------------------------------- 阶段流程

def cmd_broad_search():
    c = contract()
    od = outdir_of(c)
    t0 = time.monotonic()
    ensure_sources(od, c)
    pf = plan_abs(c)
    # (a) codex 写查询提案 → 校验 → canonical
    qf = os.path.join(od, "queries", "broad.json")
    obj = propose_json(c, od, "broad-queries", build_broad_queries_prompt(c, od, pf), qf,
                       lambda o: validate_queries_proposal(o, c["broad_queries"], c["scopes"]), t0)
    canon = canonicalize_queries(obj, None, next_qid(load_sources(od)))
    write_json(qf, canon)
    # (b) 可信脚本执行搜索（预算超限丢弃并记录，不报错）
    for item in canon["queries"]:
        check_stage_timeout(c, t0)
        src = load_sources(od)
        if not budget_ok(src, c):
            src = record_search_dropped(src, item, None, "budget")
            write_sources(od, src)
            print(f"[deep-research] 搜索超预算，丢弃 {item['qid']}", file=sys.stderr)
            continue
        run_search(c, od, item["qid"], item["q"], item["scope"], None)
    src = load_sources(od)
    if not src["searches"]:
        fail("广域搜索无任何成功查询（成功搜索为 0 条）")
    if not src["sources"]:
        fail("广域搜索未获得任何来源")
    # (c) codex 写综述笔记 + fetch 提案
    run_one(c, od, "broad-notes", build_broad_notes_prompt(c, od, pf), t0)
    # (d) 可信脚本抓全文
    process_fetch_proposal(c, od, "broad", os.path.join(od, "fetch-requests", "broad.json"), t0)
    src = load_sources(od)
    print(f"[deep-research] broad-search OK: 搜索 {len(src['searches'])} 次, "
          f"来源 {len(src['sources'])} 条, 抓取 {len(src.get('fetches', []))} 条")


def cmd_deep_dive():
    c = contract()
    od = outdir_of(c)
    t0 = time.monotonic()
    ensure_sources(od, c)
    for d in c["directions"]:
        did = d["id"]
        # (a) codex 写该方向查询提案 → 校验 → canonical
        qf = os.path.join(od, "queries", did + ".json")
        obj = propose_json(c, od, f"deep-dive-{did}-queries",
                           build_deep_queries_prompt(c, od, d), qf,
                           lambda o: validate_queries_proposal(o, c["queries_per_direction"], c["scopes"]), t0)
        canon = canonicalize_queries(obj, did, next_qid(load_sources(od)))
        write_json(qf, canon)
        # (b) 可信脚本执行搜索（direction 记为 did）
        for item in canon["queries"]:
            check_stage_timeout(c, t0)
            src = load_sources(od)
            if not budget_ok(src, c):
                src = record_search_dropped(src, item, did, "budget")
                write_sources(od, src)
                print(f"[deep-research] 搜索超预算，丢弃 {item['qid']}", file=sys.stderr)
                continue
            run_search(c, od, item["qid"], item["q"], item["scope"], did)
        # (c) codex 写该方向发现笔记 + fetch 提案
        run_one(c, od, f"deep-dive-{did}-findings", build_deep_findings_prompt(c, od, d), t0)
        # (d) 可信脚本抓全文
        process_fetch_proposal(c, od, did, os.path.join(od, "fetch-requests", did + ".json"), t0)
    src = load_sources(od)
    print(f"[deep-research] deep-dive OK: {len(c['directions'])} 个方向, "
          f"搜索累计 {len(src['searches'])} 次, 来源累计 {len(src['sources'])} 条")


def cmd_synthesize():
    c = contract()
    od = outdir_of(c)
    t0 = time.monotonic()
    run_one(c, od, "synthesize", build_synthesize_prompt(c, od, plan_abs(c)), t0)
    print("[deep-research] synthesize OK")


def cmd_repair():
    c = contract()
    od = outdir_of(c)
    vpath = os.path.join(od, "verify.json")
    if not os.path.isfile(vpath):
        fail("verify.json 不存在，修复分支被绕过")
    v = read_json(vpath)
    if v.get("verdict") != "repairable":
        fail(f"当前裁决为 {v.get('verdict')}，无修复分支")
    n = attempts(od)
    if n >= max(1, int(c["max_attempts"])):
        fail(f"已达修复次数上限 {c['max_attempts']}，不再修复", code=1)
    write_json(os.path.join(od, "attempts.json"), {"attempts": n + 1})
    run_one(c, od, f"repair-{n + 1}", build_repair_prompt(c, od, v.get("failures", [])))
    print(f"[deep-research] repair OK（第 {n + 1} 次）")


# ---------------------------------------------------------------- verify

def check_report_sections(text, direction_ids):
    """report 固定章节逐字检查：H1 标题 + 期望的 H2 序列（顺序与内容完全一致）。"""
    errs = []
    lines = text.splitlines()
    first = next((ln for ln in lines if ln.strip()), "")
    if not first.strip().startswith("# "):
        errs.append("report 首行须为 '# ' 标题")
    h2 = [ln.strip()[3:].strip() for ln in lines if ln.strip().startswith("## ")]
    expected = ["执行摘要"] + list(direction_ids) + ["交叉对比与矛盾", "证据缺口", "结论"]
    if h2 != expected:
        errs.append(f"章节标题或顺序不符：期望 {expected}，实际 {h2}")
    return errs


def extract_citations(text):
    return sorted({int(m) for m in CITE_RE.findall(text)})


def extract_citation_sids(text):
    return sorted("S%d" % n for n in extract_citations(text))


def check_sources_integrity(src, max_searches, max_fetches):
    """sources.json 完整性检查；任何违反均为结构性失败（fatal）。返回消息列表。"""
    errs = []
    sources = src.get("sources")
    if not isinstance(sources, list):
        return ["sources 缺失或非数组"]
    sids = [str(s.get("sid") or "") for s in sources]
    if any(not re.fullmatch(r"S\d+", s) for s in sids):
        errs.append("sid 格式非法（须为 S<数字>）")
    if len(set(sids)) != len(sids):
        errs.append("sid 重复")
    for i, s in enumerate(sids, 1):
        if s != "S%d" % i:
            errs.append(f"sid 不连续: 期望 S{i} 实际 {s}")
            break
    for s in sources:
        if not is_http_url(s.get("url")):
            errs.append(f"{s.get('sid')} url 非 http(s): {s.get('url')!r}")
    searches = src.get("searches")
    if not isinstance(searches, list):
        return errs + ["searches 缺失或非数组"]
    qids = [str(s.get("qid") or "") for s in searches]
    if len(set(qids)) != len(qids):
        errs.append("searches[].qid 重复")
    qset = set(qids)
    for s in sources:
        qids_ = s.get("query_ids")
        if not isinstance(qids_, list):
            errs.append(f"{s.get('sid')} query_ids 缺失或非数组")
            continue
        for q in qids_:
            if q not in qset:
                errs.append(f"{s.get('sid')} query_ids 含未知 qid {q}")
    budget = src.get("budget") or {}
    if budget.get("used") != len(searches):
        errs.append(f"budget.used={budget.get('used')} 与 searches 条数 {len(searches)} 不一致")
    if budget.get("used", 0) > max_searches:
        errs.append(f"搜索使用 {budget.get('used')} 超过 max_searches {max_searches}")
    fetches = src.get("fetches")
    if not isinstance(fetches, list):
        errs.append("fetches 缺失或非数组")
    elif len(fetches) > max_fetches:
        errs.append(f"抓取 {len(fetches)} 超过 max_fetches {max_fetches}")
    return errs


def _read_or(od, rel):
    p = os.path.join(od, rel)
    return open(p, encoding="utf-8").read() if os.path.isfile(p) else ""


def cmd_verify():
    c = contract()
    od = outdir_of(c)
    failures = []

    # --- 文件齐全（缺 report/notes/findings 可修复；缺 sources.json 结构性致命）
    src = None
    if not os.path.isfile(sources_path(od)):
        failures.append("sources.json 缺失（结构性致命）")
    else:
        try:
            src = read_json(sources_path(od))
        except Exception as e:
            failures.append(f"sources.json 不是合法 JSON（结构性致命）: {e}")
    for rel in ("report.md", "notes/broad.md"):
        if not os.path.isfile(os.path.join(od, rel)):
            failures.append(f"产物缺失: {rel}")
    for d in c["directions"]:
        if not os.path.isfile(os.path.join(od, "findings", d["id"] + ".md")):
            failures.append(f"发现缺失: findings/{d['id']}.md")

    # --- 字节数
    report_text = _read_or(od, "report.md")
    notes_text = _read_or(od, "notes/broad.md")
    findings_text = {}
    if report_text and len(report_text.strip().encode("utf-8")) < 1000:
        failures.append("report.md 不足 1000 字节，疑似空跑")
    if notes_text and len(notes_text.strip().encode("utf-8")) < 500:
        failures.append("notes/broad.md 不足 500 字节")
    for d in c["directions"]:
        ft = _read_or(od, "findings/" + d["id"] + ".md")
        findings_text[d["id"]] = ft
        if ft and len(ft.strip().encode("utf-8")) < 300:
            failures.append(f"findings/{d['id']}.md 不足 300 字节")

    # --- report 固定章节（逐字检查标题与顺序）
    if report_text:
        failures += check_report_sections(report_text, [d["id"] for d in c["directions"]])

    # --- 闭环引用：[S#] 可解析；report 覆盖方向数；findings 至少 1 引用
    sid_set = {s["sid"] for s in (src or {}).get("sources", [])} if src else set()
    labels = {"report.md": report_text, "notes/broad.md": notes_text}
    labels.update({f"findings/{k}.md": v for k, v in findings_text.items()})
    for label, text in labels.items():
        if not text:
            continue
        cited = extract_citation_sids(text)
        dangling = set(cited) - sid_set
        if dangling:
            failures.append(f"悬空引用（可修复）: {label} 引用了不存在的 {sorted(dangling)}")
    if report_text:
        report_sids = set(extract_citation_sids(report_text))
        if len(report_sids) < len(c["directions"]):
            failures.append(f"report.md 引用的不同来源数 {len(report_sids)} "
                            f"少于方向数 {len(c['directions'])}")
    for did, ft in findings_text.items():
        if ft and not extract_citation_sids(ft):
            failures.append(f"findings/{did}.md 无任何 [S#] 引用")

    # --- sources.json 完整性（任何违反 = 结构性致命）
    if src is not None:
        failures += ["%s（结构性致命）" % m
                     for m in check_sources_integrity(src, c["max_searches"], c["max_fetches"])]

    # --- 写入边界：porcelain 差异必须落在白名单内（产物目录 + .specify/ + 契约 allowed_write_paths）
    baseline = set(read_json(os.path.join(od, "baseline.json"))["preexisting"])
    allowed = [os.path.relpath(od, REPO), ".specify"]
    allowed += [os.path.relpath(safe_rel(r), REPO) for r in c["allowed_write_paths"]]
    for p in sorted(porcelain_paths(REPO) - baseline):
        if violates(p, allowed):
            failures.append(f"写入越界（致命）: {p}")

    fatal = any("致命" in f for f in failures)
    verdict = "fatal" if fatal else ("repairable" if failures else "pass")
    write_json(os.path.join(od, "verify.json"),
               {"verdict": verdict, "failures": failures, "attempt": attempts(od)})
    print(f"[deep-research] verify: {len(failures)} failure(s)")
    print(f"VERDICT={verdict}")


# ---------------------------------------------------------------- assert / finalize

def cmd_assert_passed():
    od = outdir_of(contract())
    vpath = os.path.join(od, "verify.json")
    if not os.path.isfile(vpath):
        fail("verify.json 不存在，验收被绕过")
    v = read_json(vpath)
    if v.get("verdict") != "pass":
        fail(f"最终裁决为 {v.get('verdict')}，失败明细: {v.get('failures')}", code=1)
    print("[deep-research] assert-passed OK")


def cmd_finalize():
    c = contract()
    od = outdir_of(c)
    v = read_json(os.path.join(od, "verify.json"))
    if v.get("verdict") != "pass":
        fail("finalize 仅在验收通过后运行")
    src = load_sources(od)
    write_json(os.path.join(od, "summary.json"), {
        "task_id": c["task_id"], "workflow_id": WORKFLOW_ID, "model": MODEL,
        "attempts": v.get("attempt"),
        "report": os.path.abspath(os.path.join(od, "report.md")),
        "source_count": len(src.get("sources", [])),
        "searches_used": src.get("budget", {}).get("used", 0),
        "finished_at": datetime.now(timezone.utc).isoformat(),
    })
    with open(os.path.join(od, "SUCCESS"), "w") as f:
        f.write(v["verdict"] + "\n")
    print(f"[deep-research] finalize OK: {od}")


# ---------------------------------------------------------------- selftest（离线，无网络、无 codex）

VALID_CONTRACT = {
    "task_id": "research-test-001",
    "topic": "测试主题",
    "objective": "测试目标",
    "directions": [{"id": "D1", "title": "方向一", "questions": ["问题A", "问题B"]}],
}


def _rejects(**mut):
    base = dict(VALID_CONTRACT)
    base.update(mut)
    errs, _ = check_contract(base, "/tmp/dr-nonexistent-repo")
    return errs


def test_contract_defaults():
    errs, c = check_contract(VALID_CONTRACT, "/tmp/dr-nonexistent-repo")
    assert not errs, errs
    assert c["scopes"] == ["webpage"]
    assert c["broad_queries"] == 4
    assert c["queries_per_direction"] == 3
    assert c["size_per_query"] == 10
    assert c["max_searches"] == 24
    assert c["max_fetches"] == 8
    assert c["fulltext_max_chars"] == 40000
    assert c["max_attempts"] == 2
    assert c["step_timeout_seconds"] == 1200
    assert c["timeout_seconds"] == 5400
    assert c["allowed_write_paths"] == []
    assert c["plan_file"] is None


def test_contract_rejections():
    assert _rejects(task_id="bad id!")
    assert _rejects(task_id="")
    assert _rejects(task_id=123)
    assert _rejects(topic="")
    assert _rejects(objective="")
    assert _rejects(directions=[])
    assert _rejects(directions="x")
    assert _rejects(directions=[{"id": f"D{i}", "title": "t", "questions": ["q"]} for i in range(12)] + [{"id": "D12", "title": "t", "questions": ["q"]}])
    assert _rejects(directions=[{"id": "D.1", "title": "t", "questions": ["q"]}])
    assert _rejects(directions=[{"id": "D1", "title": "", "questions": ["q"]}])
    assert _rejects(directions=[{"id": "D1", "title": "t", "questions": []}])
    assert _rejects(directions=[{"id": "D1", "title": "t", "questions": ["q"] * 9}])
    assert _rejects(directions=[{"id": "D1", "title": "t", "questions": ["", "q"]}])
    assert _rejects(directions=[{"id": "D1", "title": "t", "questions": ["q"]}, {"id": "D1", "title": "t2", "questions": ["q2"]}])
    assert _rejects(scopes=["podcast"])
    assert _rejects(scopes=[])
    assert _rejects(scopes="webpage")
    assert _rejects(broad_queries=0)
    assert _rejects(broad_queries=7)
    assert _rejects(queries_per_direction=0)
    assert _rejects(queries_per_direction=7)
    assert _rejects(size_per_query=0)
    assert _rejects(size_per_query=11)
    assert _rejects(max_fetches=-1)
    assert _rejects(max_fetches=31)
    assert _rejects(max_attempts=0)
    assert _rejects(broad_queries="4")
    assert _rejects(max_searches=2)  # 低于计划预算 4 + 1*3 = 7
    assert _rejects(plan_file=123)
    assert _rejects(plan_file="")
    assert _rejects(plan_file="/etc/passwd")
    assert _rejects(plan_file="../outside.md")
    # 合法边界
    errs, _ = check_contract({**VALID_CONTRACT, "directions": [
        {"id": f"D{i}", "title": "t", "questions": ["q"]} for i in range(12)],
        "max_searches": 40},
        "/tmp/dr-nonexistent-repo")
    assert not errs
    errs, _ = check_contract({**VALID_CONTRACT, "max_searches": 7}, "/tmp/dr-nonexistent-repo")
    assert not errs
    errs, _ = check_contract({**VALID_CONTRACT, "scopes": ["arxiv", "webpage"],
                              "broad_queries": 6, "queries_per_direction": 6, "max_searches": 18},
                             "/tmp/dr-nonexistent-repo")
    assert not errs


def test_queries_proposal():
    def v(o, limit=4):
        return validate_queries_proposal(o, limit, {"webpage", "news"})
    assert v({"queries": [{"q": "x", "scope": "webpage"}, {"q": "y"}]})[0]
    assert not v({})[0]
    assert not v({"queries": []})[0]
    assert not v({"queries": [{"q": "x"}] * 5})[0]
    assert not v({"queries": [{"q": ""}]})[0]
    assert not v({"queries": [{"scope": "webpage"}]})[0]
    assert not v({"queries": [{"q": "x", "scope": "arxiv"}]})[0]
    assert not v({"queries": "x"})[0]
    canon = canonicalize_queries({"queries": [{"q": "x"}, {"q": "y", "scope": "news"}]}, "D1", "q5")
    assert canon["direction"] == "D1"
    assert [x["qid"] for x in canon["queries"]] == ["q5", "q6"]
    assert canon["queries"][0]["scope"] == "webpage"
    assert next_qid({"searches": [{"qid": "q5"}, {"qid": "q7"}]}) == "q8"
    assert next_qid({"search_failures": [{"qid": "q2"}]}) == "q3"
    assert next_qid({"search_dropped": [{"qid": "q1"}]}) == "q2"
    assert next_qid({}) == "q1"


def test_urls_and_sids():
    assert normalize_url("https://a.com/x/#frag") == "https://a.com/x"
    assert normalize_url("https://a.com/x/") == "https://a.com/x"
    assert normalize_url("http://a.com") == "http://a.com"
    assert normalize_url(" https://a.com/y/?a=1#f ") == "https://a.com/y/?a=1"
    src = {"sources": []}
    added = register_search_results(src, [
        {"link": "https://a.com/x/#f", "title": "A", "snippet": "s", "summary": "m", "date": "2025"},
        {"link": "https://a.com/x/", "title": "A2", "snippet": "", "summary": "", "date": ""},
        {"link": "http://b.com", "title": "B", "snippet": "", "summary": "", "date": ""},
        {"link": "not-a-url", "title": "C", "snippet": "", "summary": "", "date": ""},
    ], "webpage", "q1", None)
    assert added == 2
    assert len(src["sources"]) == 2
    assert src["sources"][0]["sid"] == "S1"
    assert src["sources"][1]["sid"] == "S2"
    assert src["sources"][0]["url"] == "https://a.com/x"
    assert src["sources"][0]["query_ids"] == ["q1"]
    register_search_results(src, [{"link": "https://a.com/x", "title": "", "snippet": "", "summary": "", "date": ""}],
                            "webpage", "q2", "D1")
    assert len(src["sources"]) == 2  # 去重合并
    assert src["sources"][0]["query_ids"] == ["q1", "q2"]
    assert src["sources"][0]["direction"] is None  # 首次出现者定方向


def test_citations():
    text = "见 [S1] 与 [S12]，以及 [S3]。"
    assert extract_citations(text) == [1, 3, 12]
    assert extract_citation_sids(text) == ["S1", "S12", "S3"]
    cited = set(extract_citation_sids(text))
    assert cited - {"S1", "S3"} == {"S12"}  # S12 悬空
    assert extract_citation_sids("无引用") == []


def test_report_sections():
    dirs = ["D1", "D2"]
    good = "# 标题\n## 执行摘要\n## D1\n## D2\n## 交叉对比与矛盾\n## 证据缺口\n## 结论\n"
    assert check_report_sections(good, dirs) == []
    ok5 = "# 标题\n## 执行摘要\n### 小节\n## D1\n## D2\n## 交叉对比与矛盾\n## 证据缺口\n## 结论\n"
    assert check_report_sections(ok5, dirs) == []  # ### 子节不干扰
    bad1 = "# 标题\n## 执行摘要\n## D2\n## D1\n## 交叉对比与矛盾\n## 证据缺口\n## 结论\n"
    assert check_report_sections(bad1, dirs)
    bad2 = "# 标题\n## 执行摘要\n## D1\n## D2\n## 交叉对比与矛盾\n## 结论\n## 证据缺口\n"
    assert check_report_sections(bad2, dirs)
    bad3 = "## 执行摘要\n## D1\n## D2\n## 交叉对比与矛盾\n## 证据缺口\n## 结论\n"
    assert check_report_sections(bad3, dirs)
    bad4 = "# 标题\n## 执行摘要\n## D1\n## D2\n## 交叉对比与矛盾\n## 证据缺口\n## 结论\n## 额外章节\n"
    assert check_report_sections(bad4, dirs)
    bad5 = "# 标题\n## 执行摘要\n## D1\n## 交叉对比与矛盾\n## 证据缺口\n## 结论\n"
    assert check_report_sections(bad5, dirs)  # 缺 D2


def test_budget_accounting():
    src = {"sources": [], "searches": [], "budget": {"used": 0, "max": 3}}
    record_search_success(src, "q1", "a", "webpage", None, 2, "t", 3)
    record_search_success(src, "q2", "b", "webpage", "D1", 5, "t", 3)
    assert src["budget"]["used"] == 2
    assert len(src["searches"]) == 2
    assert budget_ok(src, {"max_searches": 3})
    record_search_success(src, "q3", "c", "webpage", None, 1, "t", 3)
    assert not budget_ok(src, {"max_searches": 3})  # used==3 达上限
    record_search_failure(src, "q4", "d", "webpage", None, "boom", "t")
    assert src["budget"]["used"] == 3  # 失败不计预算
    assert len(src["search_failures"]) == 1
    assert len(src["searches"]) == 3
    assert src["budget"]["used"] == len(src["searches"])


def test_fetch_filter():
    known = {"S1", "S2", "S3"}
    pending, dropped, unk = filter_fetch_sids(["S1", "S2", "S3", "S9"], known, set(), 2)
    assert pending == ["S1", "S2"]
    assert dropped == ["S3"]
    assert unk == ["S9"]
    pending, dropped, unk = filter_fetch_sids(["S1", "S2"], known, {"S1"}, 5)
    assert pending == ["S2"] and not dropped and not unk
    pending, dropped, unk = filter_fetch_sids(["S1"], known, set(), 0)
    assert pending == [] and dropped == ["S1"] and not unk


def test_fetch_proposal_schema():
    ok, errs = validate_fetch_proposal({"sids": ["S1", "S3"]})
    assert ok and not errs
    assert validate_fetch_proposal({"sids": []})[0]  # 空提案合法（不抓取）
    assert not validate_fetch_proposal({"sids": ["S1", "X2"]})[0]
    assert not validate_fetch_proposal({"sids": "S1"})[0]
    assert not validate_fetch_proposal({})[0]
    assert not validate_fetch_proposal({"sids": [1, 2]})[0]


def test_sources_integrity():
    def mk(**mut):
        src = {"sources": [{"sid": "S1", "url": "https://a.com", "query_ids": ["q1"]}],
               "searches": [{"qid": "q1"}],
               "budget": {"used": 1, "max": 3},
               "fetches": []}
        src.update(mut)
        return src
    assert check_sources_integrity(mk(), 3, 8) == []
    assert check_sources_integrity(mk(budget={"used": 2, "max": 3}), 3, 8)
    assert check_sources_integrity(mk(sources=[{"sid": "S2", "url": "ftp://x", "query_ids": ["q1"]}]), 3, 8)
    assert check_sources_integrity(mk(sources=[{"sid": "S1", "url": "https://a.com", "query_ids": ["q9"]}]), 3, 8)
    assert check_sources_integrity(mk(fetches=[{"sid": "S1"}] * 9), 3, 8)
    assert check_sources_integrity(mk(sources=[{"sid": "S1", "url": "https://a.com", "query_ids": ["q1"]},
                                               {"sid": "S3", "url": "https://b.com", "query_ids": ["q1"]}]), 3, 8)
    assert check_sources_integrity(mk(searches=[{"qid": "q1"}, {"qid": "q1"}]), 3, 8)
    assert check_sources_integrity({"sources": "x"}, 3, 8)


def test_violates():
    allowed = [".agent/luna/research/t1", ".specify"]
    assert violates("outside.txt", allowed)
    assert violates("src/evil.py", allowed)
    assert not violates(".agent/luna/research/t1", allowed)
    assert not violates(".agent/luna/research/t1/x.txt", allowed)
    assert not violates(".agent/luna", allowed)          # 祖先折叠
    assert not violates(".agent", allowed)               # 更上层祖先
    assert not violates(".specify/workflows/runs/ab/state.json", allowed)
    assert not violates(".specify", allowed)
    assert violates(".git/config", allowed)


SELFTESTS = [
    ("契约默认值", test_contract_defaults),
    ("契约拒绝路径", test_contract_rejections),
    ("查询提案校验与 canonical", test_queries_proposal),
    ("URL 归一化/去重/sid 分配", test_urls_and_sids),
    ("[S#] 引用抽取与悬空检测", test_citations),
    ("报告章节顺序检查", test_report_sections),
    ("预算记账", test_budget_accounting),
    ("抓取过滤", test_fetch_filter),
    ("fetch 提案 schema", test_fetch_proposal_schema),
    ("sources.json 完整性", test_sources_integrity),
    ("violates 越界判定", test_violates),
]


def cmd_selftest():
    failures = []
    for name, fn in SELFTESTS:
        try:
            fn()
            print(f"  ok: {name}")
        except Exception as e:
            failures.append(f"{name}: {type(e).__name__}: {e}")
            print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    if failures:
        print(f"[deep-research] selftest: {len(failures)} 项失败")
        sys.exit(1)
    print(f"[deep-research] selftest: {len(SELFTESTS)} 项全部通过")


HANDLERS = {
    "preflight": cmd_preflight,
    "broad-search": cmd_broad_search,
    "deep-dive": cmd_deep_dive,
    "synthesize": cmd_synthesize,
    "repair": cmd_repair,
    "verify": cmd_verify,
    "assert-passed": cmd_assert_passed,
    "finalize": cmd_finalize,
    "selftest": cmd_selftest,
}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in HANDLERS:
        fail(f"用法: driver.py <{'|'.join(HANDLERS)}>")
    HANDLERS[sys.argv[1]]()
