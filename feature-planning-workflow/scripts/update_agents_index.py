#!/usr/bin/env python3
"""Update AGENTS.md with an auto-generated index of ADRs, PRDs, and issues.

Usage:
    python scripts/update_agents_index.py [path/to/AGENTS.md]

If no path is given, the script looks for AGENTS.md in the repository root
(by walking up from this script's location).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Iterable

START_MARKER = "<!-- feature-planning-workflow:index:start -->"
END_MARKER = "<!-- feature-planning-workflow:index:end -->"


def find_repo_root(script_dir: Path) -> Path:
    """Return the repository root by looking for AGENTS.md or .git/.jj."""
    current = script_dir.resolve()
    for parent in [current, *current.parents]:
        if (parent / "AGENTS.md").exists():
            return parent
        if (parent / ".git").exists() or (parent / ".jj").exists():
            return parent
    return script_dir.resolve().parents[-1]


def read_status(path: Path) -> str | None:
    """Read the Status: line near the top of a markdown file, if present."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"^Status:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def read_title(path: Path) -> str:
    """Return the first H1 title from a markdown file, or the filename."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return path.name
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else path.stem


def collect_adrs(repo_root: Path) -> list[tuple[str, str]]:
    """Return (relative_path, title) for each ADR."""
    adr_dir = repo_root / "docs" / "adr"
    if not adr_dir.exists():
        return []
    paths = sorted(p for p in adr_dir.iterdir() if p.suffix == ".md" and p.is_file())
    return [(str(p.relative_to(repo_root)), read_title(p)) for p in paths]


def collect_prds(repo_root: Path) -> list[tuple[str, str, str | None]]:
    """Return (relative_path, title, status) for each PRD."""
    scratch = repo_root / ".scratch"
    if not scratch.exists():
        return []
    paths = sorted(p for p in scratch.rglob("PRD.md") if p.is_file())
    return [(str(p.relative_to(repo_root)), read_title(p), read_status(p)) for p in paths]


def collect_issues(repo_root: Path) -> list[tuple[str, str, str | None]]:
    """Return (relative_path, title, status) for each issue."""
    scratch = repo_root / ".scratch"
    if not scratch.exists():
        return []
    paths = sorted(p for p in (scratch).rglob("issues/*.md") if p.is_file())
    return [(str(p.relative_to(repo_root)), read_title(p), read_status(p)) for p in paths]


def format_index(adrs: Iterable[tuple[str, str]],
                 prds: Iterable[tuple[str, str, str | None]],
                 issues: Iterable[tuple[str, str, str | None]]) -> str:
    lines: list[str] = [
        START_MARKER,
        "",
        "## 文档索引",
        "",
        "本索引由 `/feature-planning-workflow` 自动维护，涵盖当前仓库的 ADR、PRD 与 Issue。",
        "",
        "### 架构决策记录 (ADR)",
        "",
    ]
    if adrs:
        for rel_path, title in adrs:
            lines.append(f"- [`{rel_path}`]({rel_path}) — {title}")
    else:
        lines.append("_暂无 ADR_")

    lines.extend(["", "### 产品需求文档 (PRD)", ""])
    if prds:
        for rel_path, title, status in prds:
            status_tag = f" `[{status}]`" if status else ""
            lines.append(f"- [`{rel_path}`]({rel_path}) — {title}{status_tag}")
    else:
        lines.append("_暂无 PRD_")

    lines.extend(["", "### 实现 Issue", ""])
    if issues:
        for rel_path, title, status in issues:
            status_tag = f" `[{status}]`" if status else ""
            lines.append(f"- [`{rel_path}`]({rel_path}) — {title}{status_tag}")
    else:
        lines.append("_暂无 Issue_")

    lines.extend(["", END_MARKER, ""])
    return "\n".join(lines)


def update_agents_md(path: Path, index_block: str) -> bool:
    """Insert or replace the index block in AGENTS.md. Return True if changed."""
    original = path.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(START_MARKER) + ".*?" + re.escape(END_MARKER) + r"\n?",
        re.DOTALL,
    )

    if pattern.search(original):
        new_text = pattern.sub(index_block.rstrip() + "\n\n", original)
    else:
        new_text = original.rstrip() + "\n\n" + index_block

    if new_text == original:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main(argv: list[str]) -> int:
    if argv:
        agents_path = Path(argv[0])
    else:
        repo_root = find_repo_root(Path(__file__).parent)
        agents_path = repo_root / "AGENTS.md"

    if not agents_path.exists():
        print(f"ERROR: AGENTS.md not found at {agents_path}", file=sys.stderr)
        return 1

    repo_root = agents_path.resolve().parent
    index_block = format_index(
        collect_adrs(repo_root),
        collect_prds(repo_root),
        collect_issues(repo_root),
    )

    changed = update_agents_md(agents_path, index_block)
    if changed:
        print(f"Updated {agents_path}")
    else:
        print(f"No changes needed for {agents_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
