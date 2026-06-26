import argparse
import re
from pathlib import Path


_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def _iter_md_files(root: Path):
    for p in root.rglob("*.md"):
        if p.name.upper() == "LICENSE.MD":
            continue
        yield p


def _extract_links(md_text: str):
    for m in _LINK_RE.finditer(md_text):
        yield m.group(1)


def _is_relative_link(link: str) -> bool:
    if "://" in link:
        return False
    if link.startswith("#"):
        return False
    if link.startswith("mailto:"):
        return False
    return True


def check(root: Path, max_lines: int) -> dict:
    report = {
        "root": str(root),
        "missing_files": [],
        "broken_links": [],
        "too_long": [],
        "non_english": [],
    }

    skill_md = root / "SKILL.md"
    if not skill_md.exists():
        report["missing_files"].append(str(skill_md))
        return report

    md_files = list(_iter_md_files(root))

    for md in md_files:
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if _CJK_RE.search(text):
            report["non_english"].append(str(md))

        line_count = text.count("\n") + 1
        if md.name == "SKILL.md" and line_count > 500:
            report["too_long"].append({"file": str(md), "lines": line_count, "limit": 500})
        elif md.name != "SKILL.md" and line_count > max_lines:
            report["too_long"].append({"file": str(md), "lines": line_count, "limit": max_lines})

        for link in _extract_links(text):
            if not _is_relative_link(link):
                continue
            link_path = link.split("#", 1)[0]
            target = (md.parent / link_path).resolve()
            if not target.exists():
                report["broken_links"].append({"from": str(md), "link": link, "resolved": str(target)})

    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--max-lines", type=int, default=250)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rep = check(root, args.max_lines)

    ok = (not rep["missing_files"]) and (not rep["broken_links"]) and (not rep["too_long"])

    if rep["non_english"]:
        ok = False

    if rep["missing_files"]:
        print("missing_files:")
        for p in rep["missing_files"]:
            print(f"- {p}")

    if rep["broken_links"]:
        print("broken_links:")
        for item in rep["broken_links"]:
            print(f"- from: {item['from']}")
            print(f"  link: {item['link']}")
            print(f"  resolved: {item['resolved']}")

    if rep["too_long"]:
        print("too_long:")
        for item in rep["too_long"]:
            print(f"- {item['file']} lines={item['lines']} limit={item['limit']}")

    if rep["non_english"]:
        print("non_english:")
        for p in rep["non_english"]:
            print(f"- {p}")

    print(f"ok: {ok}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
