#!/usr/bin/env python3
"""explore-repo 可信驱动：preflight / explore / repair / verify / assert-passed / finalize。

裁决约定：verify 恒以 0 退出（引擎对非零 shell 退出直接判失败，不进修复分支），
裁决写入 verify.json，stdout 末行输出 VERDICT=<pass|repairable|fatal>；
assert-passed 读取 verify.json 强制终态，绕过裁决即失败。
"""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.getcwd()
CONTRACT_PATH = ".agent/luna/task.json"
MODEL = "gpt-6-luna"
REQUIRED_SECTIONS = ("## Findings", "## Evidence", "## Open Questions")
CITE_RE = re.compile(
    r"(?:[\w.-]+/)*[\w.-]+\.(?:py|js|tsx?|jsx|go|rs|java|kt|swift|c|cc|h|hpp|cpp|cs|rb|php|sh|md|json|ya?ml|toml|txt|sql)"
)


def fail(msg, code=2):
    print(f"[explore-repo] FATAL: {msg}", file=sys.stderr)
    sys.exit(code)


def contract():
    p = os.path.join(REPO, CONTRACT_PATH)
    if not os.path.isfile(p):
        fail(f"缺少任务契约 {CONTRACT_PATH}")
    try:
        with open(p, encoding="utf-8") as f:
            c = json.load(f)
    except Exception as e:
        fail(f"契约不是合法 JSON: {e}")
    for k in ("task_id", "objective"):
        if not str(c.get(k) or "").strip():
            fail(f"契约缺少必填字段 {k}")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", c["task_id"]):
        fail("task_id 只允许字母数字与 . _ -")
    c.setdefault("focus_paths", [])
    c.setdefault("exclude_paths", [])
    c.setdefault("allowed_write_paths", [])
    c.setdefault("constraints", [])
    c.setdefault("max_attempts", 2)
    c.setdefault("timeout_seconds", 1800)
    return c


def outdir_of(c):
    return os.path.join(REPO, ".agent/luna/explore", c["task_id"])


def safe_rel(rel):
    """校验契约内相对路径：拒绝绝对路径、..、符号链接逃逸。返回仓库内绝对路径。"""
    if os.path.isabs(rel) or ".." in rel.split(os.sep) or ".." in rel.split("/"):
        fail(f"契约路径非法（绝对路径或 ..）: {rel}")
    real = os.path.realpath(os.path.join(REPO, rel))
    if real != REPO and not real.startswith(REPO + os.sep):
        fail(f"契约路径符号链接逃逸: {rel}")
    return real


def porcelain_paths(repo):
    out = subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout
    paths = set()
    for line in out.splitlines():
        if not line.strip():
            continue
        p = line[3:]
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        paths.add(p.strip().strip('"'))
    return paths


def under(path, roots):
    return any(path == r or path.startswith(r.rstrip("/") + "/") for r in roots)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- preflight

def cmd_preflight():
    c = contract()
    if shutil.which("git") is None:
        fail("git 不可用")
    subprocess.run(["git", "rev-parse", "--git-dir"], cwd=REPO, capture_output=True, check=True)
    for tool in ("acpx", "codex", "python3"):
        if shutil.which(tool) is None:
            fail(f"执行器不可用: {tool}")
    for rel in c["focus_paths"] + c["exclude_paths"] + c["allowed_write_paths"]:
        safe_rel(rel)
    od = outdir_of(c)
    os.makedirs(od, exist_ok=True)
    # 允许写的路径 = 契约白名单 + 产物目录（固定收敛）
    baseline = sorted(porcelain_paths(REPO))
    write_json(os.path.join(od, "baseline.json"), {"preexisting": baseline})
    write_json(os.path.join(od, "contract.snapshot.json"), c)
    print(f"[explore-repo] preflight OK: task={c['task_id']} outdir={od}")


# ---------------------------------------------------------------- prompt

def build_prompt(c, repair_notes=None):
    od = outdir_of(c)
    rel_out = os.path.relpath(od, REPO)
    parts = [
        "You are performing a READ-ONLY exploration of the repository at the current working directory.",
        "",
        f"## Objective\n{c['objective']}",
        "",
        "## Scope",
        f"- Focus paths: {', '.join(c['focus_paths']) or '(entire repo)'}",
        f"- Exclude paths: {', '.join(c['exclude_paths']) or '(none)'}",
        f"- Constraints: {'; '.join(c['constraints'])}",
        "",
        "## Deliverables (write exactly these two files)",
        f"1. `{rel_out}/report.md` with ALL THREE required headings, in this order:",
        "   - `## Findings` — claims, each backed by citations in the form `path:line`",
        "   - `## Evidence` — one bullet per citation",
        "   - `## Open Questions` — what could not be determined",
        f"2. `{rel_out}/evidence.json` — a JSON array of objects `{{\"path\": \"repo/relative/file\", \"lines\": \"12-40\", \"note\": \"why it matters\"}}`",
        "",
        "## Rules",
        "- Every cited path must be repo-relative and must exist. Wrong paths fail verification.",
        "- Write ONLY inside " + rel_out + "/. Modifying anything else fails verification.",
        "- No network access. Read-only exploration otherwise.",
    ]
    if repair_notes:
        parts += [
            "",
            "## Previous attempt failed verification. Fix exactly these:",
            repair_notes,
        ]
    path = os.path.join(od, "prompt.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")
    return path


def run_explore(c, prompt_path):
    od = outdir_of(c)
    log_path = os.path.join(od, "explore.log")
    cmd = [
        "acpx", "--cwd", REPO, "--approve-all", "--model", MODEL,
        "codex", "exec", "-f", os.path.abspath(prompt_path),
    ]
    with open(log_path, "wb") as log:
        try:
            r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT,
                               timeout=c["timeout_seconds"])
        except subprocess.TimeoutExpired:
            fail(f"探索超时（>{c['timeout_seconds']}s），日志: {log_path}")
    if r.returncode != 0:
        fail(f"执行器退出码 {r.returncode}，日志: {log_path}")


def cmd_explore():
    c = contract()
    od = outdir_of(c)
    attempts = read_json(os.path.join(od, "attempts.json"))["attempts"] if os.path.exists(
        os.path.join(od, "attempts.json")) else 0
    if attempts >= max(1, int(c["max_attempts"])):
        fail(f"已达探索次数上限 {c['max_attempts']}", code=1)
    write_json(os.path.join(od, "attempts.json"), {"attempts": attempts + 1})
    run_explore(c, build_prompt(c))


def cmd_repair():
    c = contract()
    od = outdir_of(c)
    v = read_json(os.path.join(od, "verify.json"))
    notes = "\n".join("- " + f for f in v.get("failures", [])) or "(unspecified)"
    attempts = read_json(os.path.join(od, "attempts.json"))["attempts"]
    if attempts >= max(1, int(c["max_attempts"])):
        fail(f"已达探索次数上限 {c['max_attempts']}，不再修复", code=1)
    write_json(os.path.join(od, "attempts.json"), {"attempts": attempts + 1})
    run_explore(c, build_prompt(c, repair_notes=notes))


# ---------------------------------------------------------------- verify

def cmd_verify():
    c = contract()
    od = outdir_of(c)
    failures, warnings = [], []

    report = os.path.join(od, "report.md")
    if not os.path.isfile(report):
        failures.append(f"报告缺失: {report}")
    else:
        text = open(report, encoding="utf-8").read()
        if len(text.strip().encode("utf-8")) < 500:
            failures.append("报告不足 500 字节，疑似空跑")
        pos = -1
        for sec in REQUIRED_SECTIONS:
            idx = text.find(sec)
            if idx < 0:
                failures.append(f"报告缺少必需章节 {sec}")
            elif idx < pos:
                failures.append(f"章节顺序错误: {sec}")
            else:
                pos = idx

    evidence = os.path.join(od, "evidence.json")
    ev_paths = []
    if not os.path.isfile(evidence):
        failures.append(f"证据索引缺失: {evidence}")
    else:
        try:
            ev = read_json(evidence)
            if not isinstance(ev, list) or not ev:
                failures.append("evidence.json 须为非空数组")
            else:
                for i, e in enumerate(ev):
                    p = str(e.get("path", "")).strip()
                    if not p:
                        failures.append(f"evidence[{i}] 缺 path")
                    else:
                        ev_paths.append(p)
        except Exception as e:
            failures.append(f"evidence.json 不是合法 JSON: {e}")

    # grounding：报告正文与证据索引里引用的路径必须真实存在
    cited = set(ev_paths)
    if os.path.isfile(report):
        clean = re.sub(r"https?://\S+", "", open(report, encoding="utf-8").read())
        for m in CITE_RE.finditer(clean):
            if "/" in m.group(0):
                cited.add(m.group(0))
    for p in sorted(cited):
        p = p.split(":")[0].rstrip(".,;)")
        if p.startswith(".agent/luna/explore/"):
            continue  # 产物自身
        if os.path.isabs(p) or p.startswith("http"):
            failures.append(f"引用路径须为仓库相对路径: {p}")
        elif not os.path.exists(os.path.join(REPO, p)):
            failures.append(f"引用路径不存在: {p}")

    # write-path：与 baseline 差异比对，越界 = fatal
    baseline = set(read_json(os.path.join(od, "baseline.json"))["preexisting"])
    allowed = [os.path.relpath(safe_rel(r), REPO) for r in c["allowed_write_paths"]]
    allowed.append(os.path.relpath(od, REPO))
    for p in sorted(porcelain_paths(REPO) - baseline):
        if not under(p, allowed):
            failures.append(f"写入越界（致命）: {p}")

    fatal = any("致命" in f for f in failures)
    verdict = "fatal" if fatal else ("repairable" if failures else "pass")
    write_json(os.path.join(od, "verify.json"),
               {"verdict": verdict, "failures": failures, "warnings": warnings,
                "attempt": read_json(os.path.join(od, "attempts.json"))["attempts"]})
    print(f"[explore-repo] verify: {len(failures)} failure(s)")
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
    print("[explore-repo] assert-passed OK")


def cmd_finalize():
    c = contract()
    od = outdir_of(c)
    v = read_json(os.path.join(od, "verify.json"))
    if v.get("verdict") != "pass":
        fail("finalize 仅在验收通过后运行")
    write_json(os.path.join(od, "summary.json"), {
        "task_id": c["task_id"], "workflow_id": "explore-repo", "model": MODEL,
        "attempts": v.get("attempt"),
        "report": os.path.abspath(os.path.join(od, "report.md")),
        "finished_at": datetime.now(timezone.utc).isoformat(),
    })
    with open(os.path.join(od, "SUCCESS"), "w") as f:
        f.write(v["verdict"] + "\n")
    print(f"[explore-repo] finalize OK: {od}")


HANDLERS = {
    "preflight": cmd_preflight, "explore": cmd_explore, "repair": cmd_repair,
    "verify": cmd_verify, "assert-passed": cmd_assert_passed, "finalize": cmd_finalize,
}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in HANDLERS:
        fail(f"用法: driver.py <{'|'.join(HANDLERS)}>")
    HANDLERS[sys.argv[1]]()
