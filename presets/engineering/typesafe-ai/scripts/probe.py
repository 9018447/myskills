#!/usr/bin/env python3
"""System One 探针：把 state + questions 发给网关，逐条打印类型化答案并留档负载。

问题措辞与阈值应该集中在被测项目的模块里；本脚本只负责发送、解读和留档，方便
"每次改动都用非调参用例检验"。用法示例：

    python3 probe.py --state state.json --questions questions.json \
        --case representative --case hard

失败以非零退出码上报，不会被当成一个答案。仅依赖标准库。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

MAGPIE_DEFAULT = "http://127.0.0.1:3425/v1/systemone"
# 实测：magpie 的 decision-models 只接受 noul / choice / score；box 返回 400。
GATEWAY_TYPES = {"noul", "choice", "score"}


def load_json(path: str):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def guard(endpoint: str, payload: dict, questions: dict, force: bool) -> None:
    """把 magpie 上的静默失效变成显式错误（见 references/gateway-magpie.md）。"""
    if force or "api.typesafe.ai" in endpoint:
        return
    problems = []
    bad = {qid: q.get("type") for qid, q in questions.items()
           if q.get("type") not in GATEWAY_TYPES}
    if bad:
        problems.append(f"网关不支持的问题类型 {bad}（只有 {sorted(GATEWAY_TYPES)}）")
    if payload.get("assets"):
        problems.append("请求带 assets：网关返回 200 但模型不读图，答案只由文本决定")
    if problems:
        sys.exit("探针拒绝发送：\n  - " + "\n  - ".join(problems)
                 + "\n确认要发就加 --force，或改用 https://api.typesafe.ai/v1/systemone"
                 " （图片与 box 需 TypeSafe-Danger-Zone-Images: true）。")


def post(endpoint: str, payload: dict, headers: dict, timeout: int) -> dict:
    req = urllib.request.Request(
        endpoint, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **headers})
    try:
        started = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as exc:
        sys.exit(f"调用失败（HTTP {exc.code}），按错误上报而不是按答案解读：\n"
                 + exc.read().decode()[:800])
    except urllib.error.URLError as exc:
        sys.exit(f"端点不可达：{exc.reason}")
    body = json.loads(raw)
    if "answers" not in body:
        sys.exit(f"响应缺少 answers 字段，按错误处理：{raw[:800]}")
    body["_elapsed_s"] = round(time.time() - started, 2)
    return body


def read_aloud(qid: str, ans: dict, yes_at: float, no_at: float) -> str:
    kind = ans.get("type")
    if kind == "noul":
        v = ans["noul"]
        verdict = "是" if v >= yes_at else "否" if v <= no_at else "未决"
        return f"{qid:28s} noul={v:.3f}  {verdict}"
    if kind == "choice":
        probs = {k: round(p, 3) for k, p in ans["probabilities"].items()}
        return (f"{qid:28s} choice={ans['choice']} conf={ans['confidence']:.3f} "
                f"probs={probs}")
    if kind == "score":
        probs = {k: round(p, 3) for k, p in ans["probabilities"].items()}
        return (f"{qid:28s} score={ans['score']:.3f} conf={ans['confidence']:.3f} "
                f"probs={probs}")
    if kind == "box":
        return f"{qid:28s} box={ans['box']} conf={ans['confidence']:.3f}"
    return f"{qid:28s} {json.dumps(ans, ensure_ascii=False)}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--endpoint", default=MAGPIE_DEFAULT)
    ap.add_argument("--model", default="decision-models")
    ap.add_argument("--state", required=True, help="JSON 文件：请求的 state")
    ap.add_argument("--questions", required=True, help="JSON 文件：问题定义")
    ap.add_argument("--assets", help="JSON 文件：图片 assets（官方 API 才生效）")
    ap.add_argument("--header", action="append", default=[], metavar="K:V")
    ap.add_argument("--case", action="append", default=[],
                    help="用例标签，写进留档文件名")
    ap.add_argument("--receipts", default=".probe-receipts")
    ap.add_argument("--yes-at", type=float, default=0.7)
    ap.add_argument("--no-at", type=float, default=0.3)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--force", action="store_true",
                    help="跳过网关能力护栏，按原样发送")
    args = ap.parse_args()

    state = load_json(args.state)
    questions = load_json(args.questions)
    headers = dict(h.split(":", 1) for h in args.header)
    payload = {"model": args.model, "state": state, "questions": questions}
    if args.assets:
        payload["assets"] = load_json(args.assets)
    guard(args.endpoint, payload, questions, args.force)

    out = pathlib.Path(args.receipts)
    out.mkdir(parents=True, exist_ok=True)
    tag = "-".join(args.case) or "probe"
    stamp = time.strftime("%Y%m%dT%H%M%S")
    receipt = out / f"{stamp}-{tag}.json"
    body = post(args.endpoint, payload, headers, args.timeout)
    receipt.write_text(json.dumps({"payload": payload, "response": body},
                                  ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"model={body['model']}  elapsed={body.get('_elapsed_s')}s  "
          f"usage={body.get('usage')}")
    print(f"留档：{receipt}")
    for qid, ans in body["answers"].items():
        print("  " + read_aloud(qid, ans, args.yes_at, args.no_at))
    missing = sorted(set(questions) - set(body["answers"]))
    if missing:
        sys.exit(f"响应缺少问题 {missing} 的答案——按错误处理，不要当作否")


if __name__ == "__main__":
    main()
