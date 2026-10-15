#!/usr/bin/env python3
"""ticket-status-audit driver：preflight / scan / execute / verify / repair / assert-passed / finalize。

退出码语义：0=通过；1=可修复失败（走 repair-once）；2=越界/致命；3=契约非法；4=预算耗尽。
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import NoReturn

ROOT = Path.cwd().resolve()
WORKFLOW_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / ".agent-results" / "ticket-status-audit"
STATE_DIR = OUT_DIR / "state"
CONTRACT_PATH = ROOT / ".agent" / "workflow" / "task.json"
STATE_PATH = STATE_DIR / "state.json"
SCAN_PATH = STATE_DIR / "tickets-scan.json"
REPORT_PATH = OUT_DIR / "report.json"

STATUS_WORDS_CLOSED = {"resolved", "done", "completed", "merged"}
STATUS_WORDS_OPEN = {"pending", "ready-for-agent", "claimed", "open", "todo", "wip", "in-progress", "draft"}
STATUS_WORDS_SUPERSEDED = {"superseded"}
STATUS_WORDS_FROZEN = {"frozen", "paused", "on-hold"}

VALID_STATUSES = {"unfinished", "done_unmarked", "done", "obsolete"}
VALID_BASIS = {"confirmed", "insufficient_evidence"}


def deep_report_path(rnd):
    return OUT_DIR / f"deep-round{rnd}.json"


def die(code, msg) -> NoReturn:
    print(f"[driver] {msg}", file=sys.stderr)
    sys.exit(code)


def load_contract():
    if not CONTRACT_PATH.is_file():
        die(3, f"契约不存在: {CONTRACT_PATH}")
    try:
        c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        die(3, f"契约 JSON 非法: {e}")
    return c


def check_path_str(p, field):
    if not isinstance(p, str) or not p or p.startswith("/") or "\\" in p or p.startswith("~"):
        die(3, f"契约 {field} 非法路径: {p!r}")
    parts = Path(p).parts
    if ".." in parts or Path(p).is_absolute():
        die(3, f"契约 {field} 含越界段: {p!r}")


def validate_contract(c):
    for k in ("task_id", "objective", "inputs", "allowed_write_paths", "protected_paths", "acpx_args", "max_attempts"):
        if k not in c:
            die(3, f"契约缺字段: {k}")
    if not isinstance(c["max_attempts"], int) or c["max_attempts"] < 1:
        die(3, "max_attempts 须为正整数")
    for p in c["allowed_write_paths"] + c["protected_paths"]:
        check_path_str(p, "路径字段")
    if not isinstance(c["acpx_args"], list) or not c["acpx_args"] or not all(isinstance(a, str) and a for a in c["acpx_args"]):
        die(3, "acpx_args 须为非空字符串数组")
    for a in c["acpx_args"]:
        if re.search(r"[;|&`$><\n]", a):
            die(3, f"acpx_args 元素含 shell 元字符: {a!r}")
    inputs = c["inputs"]
    if "scan_root" not in inputs:
        die(3, "契约 inputs 缺 scan_root")
    check_path_str(inputs["scan_root"], "inputs.scan_root")


def read_state():
    if STATE_PATH.is_file():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {}


def write_state(s):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE_PATH)


def snapshot_git():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
    return {"head": head.stdout.strip(), "porcelain": st.stdout.splitlines()}


def extract_status(text, max_lines=80):
    lines = text.splitlines()[:max_lines]
    for line in lines:
        s = line.strip()
        if s.startswith("*"):
            s = s.strip("*").strip()
        if s.lower().startswith("status"):
            _, _, v = s.partition(":")
            return line.strip(), v.strip()
    # 节式：`## Status` 小节，取节内首个非空行作值
    for i, line in enumerate(lines):
        if line.strip().rstrip("#") == "## Status" or line.strip().lower() == "## status":
            for nxt in lines[i + 1:i + 6]:
                if nxt.strip():
                    return f"## Status → {nxt.strip()[:40]}", nxt.strip()
            break
    return None, ""


def norm_status(raw):
    w = re.split(r"[\s:：,，()（）\*]", raw.strip(), maxsplit=1)[0].lower() if raw.strip() else ""
    if w in STATUS_WORDS_CLOSED:
        return "closed"
    if w in STATUS_WORDS_OPEN:
        return "open"
    if w in STATUS_WORDS_SUPERSEDED:
        return "superseded"
    if w in STATUS_WORDS_FROZEN:
        return "frozen"
    return "none" if not w else "other"


def scan_tickets(contract):
    scan_root = (ROOT / contract["inputs"]["scan_root"]).resolve()
    if not scan_root.is_dir():
        die(3, f"scan_root 不存在: {scan_root}")
    root_resolved = scan_root.resolve()
    efforts = set(contract["inputs"].get("efforts") or [])
    out = []
    for p in sorted(root_resolved.rglob("*.md")):
        if p.is_symlink() or not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if efforts and p.relative_to(root_resolved).parts[0] not in efforts:
            continue
        try:
            if p.stat().st_size > 300_000:
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        status_raw, status_val = extract_status(text)
        title = ""
        for line in text.splitlines()[:15]:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        out.append({
            "file": rel.as_posix(),
            "slug_dir": rel.parent.as_posix(),
            "title": title,
            "has_status_field": status_raw is not None,
            "status_raw": status_raw or "",
            "status_norm": norm_status(status_val),
            "is_ticket": status_raw is not None or rel.parent.name == "issues",
        })
    return out


def dispatch_codex(prompt_path, log_path, contract, timeout):
    args = ["acpx", "--cwd", str(ROOT), "--approve-all"] + contract["acpx_args"] + ["exec", "-f", str(prompt_path)]
    with open(log_path, "w", encoding="utf-8") as logf:
        proc = subprocess.run(args, cwd=ROOT, stdout=logf, stderr=subprocess.STDOUT, timeout=timeout)
    return proc.returncode


# ---------------- phases ----------------

def phase_preflight():
    contract = load_contract()
    validate_contract(contract)
    for binname in ("zg", "acpx", "git"):
        if not subprocess.run(["which", binname], capture_output=True).returncode == 0:
            die(3, f"依赖命令不可用: {binname}")
    scan_root = ROOT / contract["inputs"]["scan_root"]
    if not scan_root.is_dir():
        die(3, f"scan_root 不存在: {scan_root}")
    if not (WORKFLOW_DIR / "scripts" / "prompt-template.md").is_file():
        die(3, "prompt-template.md 缺失")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    write_state({
        "task_id": contract["task_id"],
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "baseline_states": file_states(porcelain_map(snapshot_git()["porcelain"])),
        "attempt": 0,
        "verify_exit": None,
        "validator_errors": [],
        "dispatch": None,
    })
    print(f"[driver] preflight OK: {contract['task_id']}")


def phase_scan():
    contract = load_contract()
    tickets = scan_tickets(contract)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SCAN_PATH.write_text(json.dumps(tickets, ensure_ascii=False, indent=2), encoding="utf-8")
    audited = sum(1 for t in tickets if t["is_ticket"])
    print(f"[driver] scan: {len(tickets)} 个 md，其中 {audited} 张票（含 Status 行或位于 issues/ 目录）")


def run_zg_index():
    print("[driver] zg index（增量）…", flush=True)
    try:
        proc = subprocess.run(["zg", "index"], cwd=ROOT, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return "timeout"
    if proc.returncode != 0:
        print(f"[driver] zg index 失败: {proc.stderr[-2000:]}", file=sys.stderr)
        return f"rc={proc.returncode}"
    return "ok"


def build_prompt(attempt, errors_block):
    tickets = json.loads(SCAN_PATH.read_text(encoding="utf-8"))
    audited = [t for t in tickets if t["is_ticket"]]
    table = "\n".join(f"- {t['file']} ｜ Status≈{t['status_norm']} ｜ {t['title']}" for t in audited)
    tpl = (WORKFLOW_DIR / "scripts" / "prompt-template.md").read_text(encoding="utf-8")
    prompt = (tpl
              .replace("{{ATTEMPT}}", str(attempt))
              .replace("{{TOTAL}}", str(len(audited)))
              .replace("{{TICKET_TABLE}}", table)
              .replace("{{STATE}}", str(SCAN_PATH))
              .replace("{{OUT}}", str(OUT_DIR))
              .replace("{{ERRORS_BLOCK}}", errors_block))
    prompts_dir = OUT_DIR / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    path = prompts_dir / f"audit-attempt{attempt}.md"
    path.write_text(prompt, encoding="utf-8")
    return path


def do_dispatch(contract, attempt, errors_block):
    if attempt > contract["max_attempts"]:
        die(4, f"派发次数超出 max_attempts={contract['max_attempts']}")
    zg_result = run_zg_index()
    if zg_result != "ok":
        # 不派发，留待 verify 判 1 → repair 重试
        write_state({**read_state(), "dispatch": {"zg_index": zg_result, "attempt": attempt, "rc": None}})
        print(f"[driver] zg index 未成功（{zg_result}），本轮不派发")
        return
    prompt = build_prompt(attempt, errors_block)
    log = OUT_DIR / f"dispatch-attempt{attempt}.log"
    timeout = int(contract.get("timeout_seconds", 5400))
    try:
        rc = dispatch_codex(prompt, log, contract, timeout)
    except subprocess.TimeoutExpired:
        write_state({**read_state(), "dispatch": {"attempt": attempt, "rc": "timeout", "log": str(log)}})
        print(f"[driver] 派发超时（>{timeout}s），日志: {log}")
        return
    write_state({**read_state(), "dispatch": {"attempt": attempt, "rc": rc, "log": str(log)}})
    print(f"[driver] 派发 rc={rc}，日志: {log}")


def phase_execute():
    contract = load_contract()
    tickets = scan_tickets(contract)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SCAN_PATH.write_text(json.dumps(tickets, ensure_ascii=False, indent=2), encoding="utf-8")
    state = read_state()
    attempt = state.get("attempt", 0) + 1
    state["attempt"] = attempt
    write_state(state)
    do_dispatch(contract, attempt, "")


def phase_repair():
    contract = load_contract()
    state = read_state()
    attempt = state.get("attempt", 1) + 1
    if attempt > contract["max_attempts"]:
        die(4, f"repair 后仍超预算（attempt={attempt} > max_attempts）")
    state["attempt"] = attempt
    write_state(state)
    errs = "\n".join(f"- {e}" for e in state.get("validator_errors", []))
    errors_block = f"\n## 上一轮报告被验收器驳回，须修正以下问题后重新产出 report.json\n\n{errs}\n" if errs else ""
    do_dispatch(contract, attempt, errors_block)


def is_pending(entry):
    return (not entry.get("skip") and entry.get("status") == "unfinished"
            and entry.get("basis", "insufficient_evidence") == "insufficient_evidence")


def build_deep_prompt(rnd, pending, errors_block):
    lines = []
    for t in pending:
        ch = t.get("channels") or []
        traj = "；".join(f"{c.get('channel')}:{c.get('query')}→{str(c.get('result'))[:40]}" for c in ch[:6]) if ch else "（尚无检索轨迹）"
        lines.append(f"- {t['file']}\n    上轮轨迹: {traj}\n    上轮理由: {str(t.get('reason'))[:120]}")
    tpl = (WORKFLOW_DIR / "scripts" / "prompt-deep-template.md").read_text(encoding="utf-8")
    prompt = (tpl
              .replace("{{ROUND}}", str(rnd))
              .replace("{{N}}", str(len(pending)))
              .replace("{{PENDING_TABLE}}", "\n".join(lines))
              .replace("{{OUT}}", str(OUT_DIR))
              .replace("{{ERRORS_BLOCK}}", errors_block))
    prompts_dir = OUT_DIR / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    path = prompts_dir / f"deep-round{rnd}.md"
    path.write_text(prompt, encoding="utf-8")
    return path


def validate_deep(deep, pending_map, errors):
    if not isinstance(deep, dict) or not isinstance(deep.get("tickets"), list):
        errors.append("deep 报告顶层须为 {tickets:[]}")
        return
    seen = {}
    for ent in deep["tickets"]:
        if not isinstance(ent, dict) or not isinstance(ent.get("file"), str):
            errors.append("deep tickets[] 有非法条目")
            continue
        f = ent["file"]
        if f in seen:
            errors.append(f"deep 报告重复条目: {f}")
        seen[f] = ent
        if f not in pending_map:
            errors.append(f"deep 报告含待查清单之外的票: {f}")
            continue
        if ent.get("status") not in VALID_STATUSES:
            errors.append(f"{f}: status 非法: {ent.get('status')!r}")
            continue
        if ent.get("basis") not in VALID_BASIS:
            errors.append(f"{f}: basis 非法: {ent.get('basis')!r}")
        if ent.get("basis") == "confirmed":
            reason = str(ent.get("reason") or "")
            channels = ent.get("channels") or []
            if not isinstance(channels, list) or not channels:
                errors.append(f"{f}: basis=confirmed 须给 channels 检索轨迹")
            else:
                for c in channels:
                    if not isinstance(c, dict) or not (c.get("channel") or "").strip() or not (c.get("query") or "").strip():
                        errors.append(f"{f}: channels 条目须含 channel 与 query")
                        break
            if ent["status"] == "unfinished" and not any(k in reason for k in ("→", "无命中", "未命中", "查询", "frozen", "冻结")):
                errors.append(f"{f}: 终判 unfinished 的 reason 须引用具体查询词或冻结证据")
        ev = ent.get("evidence") or []
        if ent["status"] == "done_unmarked" and not ev:
            errors.append(f"{f}: done_unmarked 至少一条证据")
        for e in ev:
            if isinstance(e, dict):
                check_evidence(e, errors, f)
    missing = set(pending_map) - set(seen)
    if missing:
        errors.append(f"deep 报告漏 {len(missing)} 张: {sorted(missing)[:5]}")


def phase_deepdive():
    contract = load_contract()
    if not REPORT_PATH.is_file():
        die(3, "report.json 不存在——deepdive 在 verify 通过后运行")
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    max_rounds = int(contract.get("deep_max_rounds", 3))
    timeout = int(contract.get("timeout_seconds", 5400))
    prev_report_text = REPORT_PATH.read_text(encoding="utf-8")
    for rnd in range(1, max_rounds + 1):
        pending = [t for t in report["tickets"] if is_pending(t)]
        print(f"[deepdive] 第 {rnd} 轮：待深查 {len(pending)} 张", flush=True)
        if not pending:
            break
        state = read_state()
        errors_block = ""
        if state.get("validator_errors"):
            errors_block = "\n## 上一轮深查报告被驳回，须修正：\n\n" + "\n".join(f"- {e}" for e in state["validator_errors"][:40]) + "\n"
        prompt = build_deep_prompt(rnd, pending, errors_block)
        log = OUT_DIR / f"dispatch-deep-round{rnd}.log"
        try:
            rc = dispatch_codex(prompt, log, contract, timeout)
        except subprocess.TimeoutExpired:
            print(f"[deepdive] 第 {rnd} 轮派发超时（>{timeout}s），日志: {log}", flush=True)
            break
        print(f"[deepdive] 第 {rnd} 轮派发 rc={rc}", flush=True)
        dp = deep_report_path(rnd)
        if not dp.is_file():
            print(f"[deepdive] 第 {rnd} 轮未产出 {dp}，停止迭代", flush=True)
            break
        errors = []
        deep = None
        try:
            deep = json.loads(dp.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"deep 报告非法 JSON: {e}")
        if deep is None:
            write_state({**read_state(), "validator_errors": errors[:60]})
            continue
        validate_deep(deep, {t["file"] for t in pending}, errors)
        if errors:
            write_state({**read_state(), "validator_errors": errors[:60]})
            for e in errors[:15]:
                print(f"[deepdive][reject] {e}", file=sys.stderr)
            continue
        by_file = {t["file"]: t for t in report["tickets"]}
        changed = 0
        for ent in deep["tickets"]:
            old = by_file.get(ent["file"])
            if not old:
                continue
            merged = dict(old)
            merged.update({k: ent[k] for k in ("status", "basis", "reason", "evidence", "channels") if k in ent})
            if merged != old:
                changed += 1
            by_file[ent["file"]] = merged
        report["tickets"] = list(by_file.values())
        counts = {}
        for t in report["tickets"]:
            if not t.get("skip") and t.get("status") in VALID_STATUSES:
                counts[t["status"]] = counts.get(t["status"], 0) + 1
        report["summary"] = {s: counts.get(s, 0) for s in sorted(VALID_STATUSES)}
        REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        write_state({**read_state(), "validator_errors": []})
        print(f"[deepdive] 第 {rnd} 轮合并：{changed} 张改判/更新", flush=True)
        if changed == 0 and REPORT_PATH.read_text(encoding="utf-8") == prev_report_text:
            print("[deepdive] 本轮零变化 → 查无可查，停止", flush=True)
            break
        prev_report_text = REPORT_PATH.read_text(encoding="utf-8")
    left = sum(1 for t in report["tickets"] if is_pending(t))
    print(f"[deepdive] 结束：仍有 {left} 张证据不足未收敛（轮数上限 {max_rounds}）")


def safe_repo_path(p):
    if not isinstance(p, str) or not p or p.startswith("/"):
        return None
    parts = Path(p).parts
    if ".." in parts:
        return None
    resolved = (ROOT / p).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        return None
    return resolved


def check_evidence(ev, errors, ticket_file):
    kind = ev.get("kind")
    if kind in ("file", "zg"):
        rp = safe_repo_path(ev.get("path", ""))
        if rp is None or not rp.exists():
            errors.append(f"{ticket_file}: 证据 {kind} 路径不存在或越界: {ev.get('path')!r}")
    elif kind == "commit":
        h = ev.get("commit", "")
        if not re.fullmatch(r"[0-9a-f]{7,40}", str(h)):
            errors.append(f"{ticket_file}: commit 哈希非法: {h!r}")
        elif subprocess.run(["git", "rev-parse", "--verify", f"{h}^{{commit}}"], cwd=ROOT, capture_output=True).returncode != 0:
            errors.append(f"{ticket_file}: commit 不存在于仓库: {h!r}")
    else:
        errors.append(f"{ticket_file}: 证据 kind 非法: {kind!r}")


def porcelain_map(lines):
    out = {}
    for ln in lines:
        code = ln[:2]
        pth = ln[3:].strip().strip('"')
        if " -> " in pth:
            pth = pth.split(" -> ", 1)[1]
        out[pth] = code
    return out


def digest(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def file_states(lines_map):
    # porcelain 把未跟踪目录折叠为单条；展开到文件级并取内容哈希，
    # 使「同码不同内容」「未跟踪目录内部新增」都能被基线差分捕捉。
    states = {}
    for pth, code in lines_map.items():
        rp = safe_repo_path(pth)
        if rp is None:
            states[pth] = f"unresolvable:{code}"
        elif rp.is_dir():
            for f in sorted(rp.rglob("*")):
                if f.is_file() and not f.is_symlink():
                    try:
                        states[str(f.relative_to(ROOT))] = digest(f)
                    except OSError:
                        states[str(f.relative_to(ROOT))] = "unreadable"
        elif rp.is_file() and not rp.is_symlink():
            states[pth] = digest(rp)
        else:
            states[pth] = "deleted"
    return states


def phase_verify():
    contract = load_contract()
    state = read_state()
    errors = []
    fatal = False
    report = None

    if not REPORT_PATH.is_file():
        errors.append(f"report.json 不存在（派发记录: {state.get('dispatch')}）")
    else:
        try:
            report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            report = None
            errors.append(f"report.json 非法 JSON: {e}")
    if report is not None:
        if not isinstance(report, dict) or not isinstance(report.get("tickets"), list) or not isinstance(report.get("summary"), dict):
            errors.append("report.json 顶层须为 {tickets:[], summary:{}}")
        else:
            scan = json.loads(SCAN_PATH.read_text(encoding="utf-8")) if SCAN_PATH.is_file() else []
            must = {t["file"] for t in scan if t["is_ticket"]}
            seen = {}
            for ent in report["tickets"]:
                if not isinstance(ent, dict) or not isinstance(ent.get("file"), str):
                    errors.append("tickets[] 存在非法条目（缺 file）")
                    continue
                f = ent["file"]
                if f in seen:
                    errors.append(f"重复条目: {f}")
                seen[f] = ent
                st = ent.get("status")
                if ent.get("skip"):
                    if not (ent.get("reason") or "").strip():
                        errors.append(f"{f}: skip=true 须给 reason")
                    continue
                if st not in VALID_STATUSES:
                    errors.append(f"{f}: status 非法: {st!r}")
                    continue
                ev = ent.get("evidence", [])
                if not isinstance(ev, list):
                    errors.append(f"{f}: evidence 须为数组")
                    ev = []
                if st == "done_unmarked" and not ev:
                    errors.append(f"{f}: done_unmarked 至少要一条证据")
                for e in ev:
                    if isinstance(e, dict):
                        check_evidence(e, errors, f)
                if not (ent.get("reason") or "").strip():
                    errors.append(f"{f}: 须给 reason")
            missing = must - set(seen)
            extra = set(seen) - must
            if missing:
                errors.append(f"漏判 {len(missing)} 张票，如: {sorted(missing)[:5]}")
            if extra:
                errors.append(f"多判 {len(extra)} 张不在审计范围的票: {sorted(extra)[:5]}")
            counts = {}
            for f, ent in seen.items():
                if not ent.get("skip") and ent.get("status") in VALID_STATUSES:
                    counts[ent["status"]] = counts.get(ent["status"], 0) + 1
            for s in sorted(VALID_STATUSES):
                if report["summary"].get(s) != counts.get(s, 0):
                    errors.append(f"summary.{s}={report['summary'].get(s)} 与实际 {counts.get(s, 0)} 不符")

    base = state.get("baseline_states", {})
    cur = file_states(porcelain_map(snapshot_git()["porcelain"]))
    allowed = tuple(contract["allowed_write_paths"])
    for pth in sorted(set(base) | set(cur)):
        if base.get(pth) != cur.get(pth) and not pth.startswith(allowed):
            errors.append(f"越界写入/删除: {pth}（基线={str(base.get(pth))[:8]}，现状={str(cur.get(pth))[:8]}）")
            fatal = True

    state["verify_exit"] = 2 if fatal else (1 if errors else 0)
    state["validator_errors"] = errors[:80]
    write_state(state)
    for e in errors[:40]:
        print(f"[verify] {e}", file=sys.stderr)
    print(f"[driver] verify exit={state['verify_exit']}（{len(errors)} 个问题）")
    sys.exit(state["verify_exit"])


def phase_assert_passed():
    state = read_state()
    if state.get("verify_exit") != 0:
        die(1, f"最终验收未通过（verify_exit={state.get('verify_exit')}），工作流判失败")
    print("[driver] assert-passed OK")


def phase_finalize():
    state = read_state()
    summary = {}
    try:
        summary = json.loads(REPORT_PATH.read_text(encoding="utf-8")).get("summary", {})
    except Exception:
        pass
    success = {
        "task_id": state.get("task_id"),
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "attempts": state.get("attempt"),
        "summary": summary,
        "insufficient_remaining": sum(1 for t in json.loads(REPORT_PATH.read_text(encoding="utf-8"))["tickets"] if is_pending(t)) if REPORT_PATH.is_file() else None,
        "report": str(REPORT_PATH),
    }
    (OUT_DIR / "SUCCESS.json").write_text(json.dumps(success, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[driver] finalize OK → {OUT_DIR / 'SUCCESS.json'}")


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    {"preflight": phase_preflight,
     "scan": phase_scan,
     "execute": phase_execute,
     "verify": phase_verify,
     "repair": phase_repair,
     "deepdive": phase_deepdive,
     "assert-passed": phase_assert_passed,
     "finalize": phase_finalize}.get(phase, lambda: die(3, f"未知 phase: {phase}"))()


if __name__ == "__main__":
    main()
