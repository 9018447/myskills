#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

DEFAULT_ENDPOINT = "http://127.0.0.1:3425/v1/systemone"
DEFAULT_MODEL = "decision-models"
CALLOUT_THRESHOLD = 0.7
QUOTE_THRESHOLD = 0.3
CALLOUT_KINDS = ("note", "tip", "warning")

KIND_CRITERIA = {
    "note": "补充说明、限制条件或读者需要知道的事实",
    "tip": "帮助读者完成任务的建议、快捷方法或推荐做法",
    "warning": "可能造成错误、损失或风险，需要读者特别谨慎的信息",
}


class SemanticError(RuntimeError):
    pass


def build_payload(candidates: list[dict[str, Any]], model: str) -> dict[str, Any]:
    quotes = {
        candidate["id"]: {
            "text": candidate["text"],
            "section": candidate["section"],
        }
        for candidate in candidates
    }
    questions = {}
    for candidate in candidates:
        qid = candidate["id"]
        path = f"quotes.{qid}.text"
        questions[f"is_callout_{qid}"] = {
            "type": "noul",
            "instructions": f"`{path}` 是否承担注意、提示或警告作用？",
            "criteria": {
                "true": "这段文字提醒读者注意某个事实、建议或风险",
                "false": "这段文字是引用、普通摘录，或没有提醒作用",
            },
        }
        questions[f"kind_{qid}"] = {
            "type": "choice",
            "instructions": f"如果 `{path}` 是提示块，它属于哪一类？",
            "criteria": KIND_CRITERIA,
        }
    return {
        "model": model,
        "state": {"quotes": quotes},
        "questions": questions,
    }


def apply_truth_table(candidate: dict[str, Any], answers: dict[str, Any]) -> dict[str, Any]:
    qid = candidate["id"]
    callout_answer = answers[f"is_callout_{qid}"]
    kind_answer = answers[f"kind_{qid}"]
    probability = callout_answer["noul"]
    if probability >= CALLOUT_THRESHOLD:
        return {
            "index": candidate["index"],
            "action": "callout",
            "kind": kind_answer["choice"],
            "callout_probability": probability,
        }
    if probability <= QUOTE_THRESHOLD:
        return {
            "index": candidate["index"],
            "action": "quote",
            "callout_probability": probability,
        }
    return {
        "index": candidate["index"],
        "action": "unresolved",
        "callout_probability": probability,
    }


def post(endpoint: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if len(body) > 32 * 1024 * 1024:
        raise SemanticError("TypeSafe 请求超过 32 MiB，请分批处理文档")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1200]
        raise SemanticError(f"TypeSafe 调用失败，HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SemanticError(f"TypeSafe 端点不可达: {exc.reason}") from exc
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SemanticError("TypeSafe 返回的不是有效 JSON") from exc
    if not isinstance(result.get("answers"), dict) or not result.get("model"):
        raise SemanticError("TypeSafe 响应缺少 answers 或 model 字段")
    return result


def validate_answers(
    candidates: list[dict[str, Any]], answers: dict[str, Any]
) -> None:
    expected = {
        f"{prefix}_{candidate['id']}"
        for candidate in candidates
        for prefix in ("is_callout", "kind")
    }
    missing = sorted(expected - answers.keys())
    if missing:
        raise SemanticError(f"TypeSafe 响应缺少答案: {', '.join(missing)}")
    for candidate in candidates:
        qid = candidate["id"]
        callout = answers[f"is_callout_{qid}"]
        kind = answers[f"kind_{qid}"]
        probability = callout.get("noul")
        if not isinstance(probability, (int, float)) or not 0 <= probability <= 1:
            raise SemanticError(f"is_callout_{qid} 没有有效的 noul 概率")
        if kind.get("choice") not in CALLOUT_KINDS:
            raise SemanticError(f"kind_{qid} 返回了未知类型: {kind.get('choice')!r}")


def classify_quotes(
    candidates: list[dict[str, Any]],
    *,
    source: str,
    endpoint: str = DEFAULT_ENDPOINT,
    model: str = DEFAULT_MODEL,
    timeout: int = 180,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "endpoint": endpoint,
        "requested_model": model,
        "thresholds": {
            "callout_at_or_above": CALLOUT_THRESHOLD,
            "quote_at_or_below": QUOTE_THRESHOLD,
        },
        "candidates": candidates,
        "payload": None,
        "response": None,
        "decisions": [],
    }
    if not candidates:
        return [], receipt

    payload = build_payload(candidates, model)
    receipt["payload"] = payload
    response = post(endpoint, payload, timeout)
    receipt["response"] = response
    answers = response["answers"]
    validate_answers(candidates, answers)
    decisions = [apply_truth_table(candidate, answers) for candidate in candidates]
    receipt["decisions"] = decisions
    return decisions, receipt
