#!/usr/bin/env python3
"""Rewrite generic residue names in topology/structure files.

All residue names are forced to exactly 3 characters. In directory mode,
if duplicate residue names are detected, the script automatically resolves
conflicts by incrementing the last character.
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from pathlib import Path

GENERIC_RESNAMES = {"MOL", "UNL"}
TEXT_SUFFIXES = {".pdb", ".itp", ".top", ".gro"}
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def sanitize_text(raw_content: bytes, file_path: str) -> str | None:
    try:
        content = raw_content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            content = raw_content.decode("latin-1")
        except Exception as exc:
            print(f"警告: 无法解码文件 {file_path}: {exc}")
            return None

    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", content)


def normalize_to_three_chars(resname: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", resname.strip())
    if not cleaned:
        raise ValueError("resname 不能为空")

    if not re.match(r"^[A-Za-z][A-Za-z0-9]*$", cleaned):
        raise ValueError(f"resname 必须字母开头且仅包含字母数字: {resname}")

    if len(cleaned) == 3:
        return cleaned

    if len(cleaned) < 3:
        padded = cleaned + "X" * (3 - len(cleaned))
        return padded

    return cleaned[:3]


def resolve_duplicates(file_pairs: list[tuple[str, str]]) -> dict[str, str]:
    name_to_indices: dict[str, list[int]] = defaultdict(list)
    for idx, (_, stem) in enumerate(file_pairs):
        name_to_indices[stem].append(idx)

    result: dict[int, str] = {}
    used: set[str] = set()

    for stem, indices in name_to_indices.items():
        if len(indices) == 1:
            result[indices[0]] = stem
            used.add(stem)
            continue

        for idx in indices:
            candidate = stem
            counter = 0

            while candidate in used:
                if counter >= len(ALPHABET):
                    raise ValueError(f"无法为 {stem} 生成唯一的残基名")
                candidate = stem[:2] + ALPHABET[counter]
                counter += 1

            result[idx] = candidate
            used.add(candidate)

    return {file_pairs[idx][0]: result[idx] for idx in result}


def get_resname_from_filename(filename: str) -> str | None:
    try:
        return normalize_to_three_chars(filename)
    except ValueError as exc:
        print(f"警告: 文件 {filename} 的文件名无法转换为合法 resname，跳过处理。原因: {exc}")
        return None


def replace_generic_tokens(content: str, new_resname: str) -> str:
    updated = content
    for generic in GENERIC_RESNAMES:
        updated = re.sub(rf"\b{re.escape(generic)}\b", new_resname, updated)
    return updated


def rewrite_gro_content(content: str, new_resname: str) -> str:
    lines = content.splitlines()
    if len(lines) < 3:
        return content

    rewritten: list[str] = []
    atom_line_stop = len(lines) - 1
    for index, line in enumerate(lines):
        if index < 2 or index >= atom_line_stop or len(line) < 10:
            rewritten.append(line)
            continue

        residue_number = line[:5]
        residue_name = line[5:10].strip()
        if residue_name in GENERIC_RESNAMES:
            rewritten.append(f"{residue_number}{new_resname:>5}{line[10:]}")
        else:
            rewritten.append(line)

    updated = "\n".join(rewritten)
    if content.endswith("\n"):
        updated += "\n"
    return updated


def update_resname_in_file(file_path: str, new_resname: str) -> None:
    path = Path(file_path)
    raw_content = path.read_bytes()
    content = sanitize_text(raw_content, file_path)
    if content is None:
        return

    updated_content = replace_generic_tokens(content, new_resname)
    if path.suffix.lower() == ".gro":
        updated_content = rewrite_gro_content(updated_content, new_resname)

    path.write_text(updated_content, encoding="utf-8")
    print(f"已更新文件: {file_path}，将通用残基名替换为 {new_resname}")


def iter_target_files(current_dir: str):
    for filename in os.listdir(current_dir):
        path = Path(current_dir, filename)
        if not path.is_file():
            continue
        if path.name == "box.pdb":
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def main() -> None:
    if len(sys.argv) == 3:
        file_path = sys.argv[1]
        requested_resname = normalize_to_three_chars(sys.argv[2])
        if not os.path.isfile(file_path):
            raise SystemExit(f"文件不存在: {file_path}")
        update_resname_in_file(file_path, requested_resname)
        print("处理完成！")
        return

    current_dir = os.getcwd()
    print(f"处理目录: {current_dir}")

    file_to_stem: list[tuple[str, str]] = []
    for path in iter_target_files(current_dir):
        stem_resname = get_resname_from_filename(path.stem)
        if stem_resname:
            file_to_stem.append((str(path), stem_resname))

    mapping = resolve_duplicates(file_to_stem)

    for file_path, stem_resname in file_to_stem:
        final_resname = mapping[file_path]
        if final_resname != stem_resname:
            print(f"注意: {Path(file_path).name} 的残基名从 {stem_resname} 调整为 {final_resname}（重复冲突解决）")
        update_resname_in_file(file_path, final_resname)


if __name__ == "__main__":
    main()
    print("处理完成！")
