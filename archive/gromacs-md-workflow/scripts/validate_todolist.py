#!/usr/bin/env python3
"""
validate_todolist.py - 严格校验并格式化 todolist.json

校验规则（不能少 / 不能多 / 不能不换行）：
1. 必须是合法 JSON，不含尾随逗号。
2. 顶层只允许 task1、task2、task3、task4。
3. task3 必须存在；其 molecules[] 每项只能包含 name、count、phase。
4. task4（VLE 用）每项只能包含 name、count、phase，及可选 fchk、source_file、aliases。
5. name 必须是非空字符串，只能以字母开头且仅含字母数字，不能为 MOL 或 UNL。
6. count 必须是正整数。
7. phase 只能是 "l" 或 "g"。
8. 通过校验后，自动用标准 2 空格缩进格式化写回文件。
"""

import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED_TOP_KEYS = {"task1", "task2", "task3", "task4"}
ALLOWED_TASK3_MOL_KEYS = {"name", "count", "phase"}
ALLOWED_TASK4_MOL_KEYS = {"name", "count", "phase", "fchk", "source_file", "aliases"}
ALLOWED_PHASES = {"l", "g"}
FORBIDDEN_NAMES = {"MOL", "UNL"}


def validate_name(name, path):
    errors = []
    if not isinstance(name, str) or not name:
        errors.append(f"{path}.name 必须是非空字符串")
        return errors
    if not re.match(r"^[A-Za-z][A-Za-z0-9]*$", name):
        errors.append(f"{path}.name 只能包含字母数字且必须以字母开头: {name}")
    if name.upper() in FORBIDDEN_NAMES:
        errors.append(f"{path}.name 不能使用通用默认残基名: {name}")
    if len(name) > 3:
        print(f"警告: {path}.name 长度超过 3 个字符，将被截断为 3 字符残基名: {name}", file=sys.stderr)
    return errors


def validate_molecule(obj, path, allowed_keys):
    errors = []
    if not isinstance(obj, dict):
        errors.append(f"{path} 必须是对象")
        return errors

    extra = set(obj.keys()) - allowed_keys
    if extra:
        errors.append(f"{path} 包含多余字段: {', '.join(sorted(extra))}")

    required = allowed_keys - {"fchk", "source_file", "aliases"}
    missing = required - set(obj.keys())
    if missing:
        errors.append(f"{path} 缺少字段: {', '.join(sorted(missing))}")

    if "name" in obj:
        errors.extend(validate_name(obj["name"], path))

    if "count" in obj:
        count = obj["count"]
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            errors.append(f"{path}.count 必须是正整数")

    if "phase" in obj:
        phase = obj["phase"]
        if phase not in ALLOWED_PHASES:
            errors.append(f'{path}.phase 必须是 "l" 或 "g"')

    if "aliases" in obj:
        aliases = obj["aliases"]
        if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
            errors.append(f"{path}.aliases 必须是字符串数组")

    for k in ("fchk", "source_file"):
        if k in obj and not isinstance(obj[k], str):
            errors.append(f"{path}.{k} 必须是字符串")

    return errors


def validate(data, mode):
    errors = []

    top_keys = set(data.keys())
    extra = top_keys - ALLOWED_TOP_KEYS
    if extra:
        errors.append(f"不允许的顶层键: {', '.join(sorted(extra))}")

    # task3 required for all modes
    if "task3" not in data:
        errors.append("缺少必需的 task3")
    else:
        task3 = data["task3"]
        if not isinstance(task3, dict):
            errors.append("task3 必须是对象")
        else:
            if "molecules" not in task3:
                errors.append("task3 缺少 molecules")
            elif not isinstance(task3["molecules"], list):
                errors.append("task3.molecules 必须是数组")
            else:
                for i, mol in enumerate(task3["molecules"]):
                    errors.extend(validate_molecule(mol, f"task3.molecules[{i}]", ALLOWED_TASK3_MOL_KEYS))

    # task4 required for vle mode
    if mode in ("vle", "all"):
        if "task4" not in data:
            if mode == "vle":
                errors.append("VLE 模式缺少必需的 task4")
        else:
            task4 = data["task4"]
            if not isinstance(task4, dict):
                errors.append("task4 必须是对象")
            else:
                if "molecules" not in task4:
                    errors.append("task4 缺少 molecules")
                elif not isinstance(task4["molecules"], list):
                    errors.append("task4.molecules 必须是数组")
                else:
                    for i, mol in enumerate(task4["molecules"]):
                        errors.extend(validate_molecule(mol, f"task4.molecules[{i}]", ALLOWED_TASK4_MOL_KEYS))

    # task1 optional but strict if present
    if "task1" in data:
        task1 = data["task1"]
        if isinstance(task1, dict) and isinstance(task1.get("molecules"), list):
            for i, mol in enumerate(task1["molecules"]):
                if not isinstance(mol, dict):
                    errors.append(f"task1.molecules[{i}] 必须是对象")
                    continue
                extra = set(mol.keys()) - {"name", "smiles", "charge"}
                if extra:
                    errors.append(f"task1.molecules[{i}] 包含多余字段: {', '.join(sorted(extra))}")
                if "name" not in mol or not isinstance(mol["name"], str) or not mol["name"]:
                    errors.append(f"task1.molecules[{i}].name 必须是非空字符串")
                if "charge" in mol and (not isinstance(mol["charge"], (int, float)) or isinstance(mol["charge"], bool)):
                    errors.append(f"task1.molecules[{i}].charge 必须是数值")

    return errors


def format_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def main():
    parser = argparse.ArgumentParser(description="校验并格式化 todolist.json")
    parser.add_argument("file", nargs="?", default="todolist.json")
    parser.add_argument("--mode", choices=["homogeneous", "vle", "all"], default="all")
    parser.add_argument("--check-only", action="store_true", help="仅检查，不自动格式化")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"错误: {path} 不存在", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate(data, args.mode)
    if errors:
        print(f"todolist.json 校验失败 ({len(errors)} 个错误):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    formatted = format_json(data)
    if not args.check_only and formatted != raw:
        with open(path, "w", encoding="utf-8") as f:
            f.write(formatted)
        print("todolist.json 校验通过，已自动格式化为标准 2 空格缩进")
    else:
        print("todolist.json 校验通过")

    sys.exit(0)


if __name__ == "__main__":
    main()
