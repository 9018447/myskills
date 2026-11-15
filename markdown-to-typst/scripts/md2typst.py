#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import unquote, urlsplit

from semantic import DEFAULT_ENDPOINT, DEFAULT_MODEL, SemanticError, classify_quotes

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "assets" / "template.typ"
CALLOUTS_FILTER = SKILL_DIR / "assets" / "callouts.lua"
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".webp"}
ALERT_RE = re.compile(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]$", re.IGNORECASE)
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


class BuildError(RuntimeError):
    pass


def run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise BuildError(f"找不到命令: {command[0]}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise BuildError(f"命令失败 ({' '.join(command)}):\n{detail}")
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result


def stringify(value: Any) -> str:
    if isinstance(value, list):
        return "".join(stringify(item) for item in value)
    if not isinstance(value, dict):
        return ""
    kind = value.get("t")
    content = value.get("c")
    if kind == "Str":
        return content
    if kind in {"Space", "SoftBreak", "LineBreak"}:
        return " " if kind != "LineBreak" else "\n"
    if kind == "Code":
        return content[1]
    if kind == "Math":
        return content[1]
    if kind == "Image":
        return stringify(content[1])
    if kind in {"RawInline", "RawBlock"}:
        return ""
    return stringify(content)


def walk_blocks(value: Any, section: list[str], quotes: list[dict[str, Any]]) -> None:
    if isinstance(value, list):
        for item in value:
            walk_blocks(item, section, quotes)
        return
    if not isinstance(value, dict):
        return
    kind = value.get("t")
    content = value.get("c")
    if kind == "Header":
        section[0] = stringify(content[2]).strip()
    if kind == "BlockQuote":
        index = len(quotes)
        text = stringify(content).strip()
        first = content[0] if content else None
        marker = None
        if first and first.get("t") in {"Para", "Plain"} and first.get("c"):
            first_inline = first["c"][0]
            if first_inline.get("t") == "Str":
                match = ALERT_RE.match(first_inline.get("c", ""))
                marker = match.group(1).upper() if match else None
        nested = any(
            item.get("t") == "BlockQuote"
            for block in content
            for item in iter_nodes(block)
            if item is not value
        )
        if nested:
            raise BuildError("暂不支持嵌套引用块，请先展开后再转换")
        quotes.append(
            {
                "index": index,
                "id": f"Q{index:03d}",
                "text": text,
                "section": section[0],
                "explicit_alert": marker,
            }
        )
        return
    walk_blocks(content, section, quotes)


def iter_nodes(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        yield from iter_nodes(value.get("c"))
    elif isinstance(value, list):
        for item in value:
            yield from iter_nodes(item)


def within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def image_map(
    ast: dict[str, Any], input_path: Path, output_path: Path, root: Path
) -> dict[str, str]:
    images = {}
    for node in iter_nodes(ast["blocks"]):
        if node.get("t") in {"RawBlock", "RawInline"}:
            raw_format, raw_content = node["c"]
            is_comment = raw_format == "html" and re.fullmatch(
                r"<!--.*-->", raw_content, re.DOTALL
            )
            if raw_format != "typst" and not is_comment:
                raise BuildError(f"不支持 {raw_format} 原始内容，请先转为 Markdown")
        if node.get("t") != "Image":
            continue
        target = node["c"][2][0]
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            raise BuildError(f"不支持远程或内嵌图片: {target}")
        raw_path = unquote(parsed.path)
        if not raw_path:
            raise BuildError(f"图片路径为空: {target}")
        candidate = Path(raw_path)
        absolute = (
            candidate.resolve()
            if candidate.is_absolute()
            else (input_path.parent / candidate).resolve()
        )
        if not within_root(absolute, root):
            raise BuildError(f"图片超出项目根目录: {target}")
        if not absolute.is_file():
            raise BuildError(f"图片不存在: {absolute}")
        if absolute.suffix.lower() not in SUPPORTED_IMAGES:
            raise BuildError(f"Typst 不支持该图片格式: {absolute}")
        relative = os.path.relpath(absolute, output_path.parent)
        images[target] = Path(relative).as_posix()
    return images


def available_fonts() -> list[str]:
    return run(["typst", "fonts"]).stdout.splitlines()


def choose_font(requested: str | None, source: str) -> str:
    fonts = available_fonts()
    if requested:
        if requested not in fonts:
            raise BuildError(f"Typst 未找到字体: {requested}")
        return requested
    candidates = (
        ("Noto Serif CJK SC", "Noto Sans CJK SC", "WenQuanYi Zen Hei")
        if HAN_RE.search(source)
        else ("Libertinus Serif", "DejaVu Serif")
    )
    for candidate in candidates:
        if candidate in fonts:
            return candidate
    raise BuildError("没有找到合适的已安装字体，请用 --font 指定字体")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将 Markdown 转为 Typst 并编译为 PDF")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, help="PDF 输出路径")
    parser.add_argument("--typst", dest="typst_path", type=Path, help="Typst 输出路径")
    parser.add_argument("--root", type=Path, help="Typst 项目根目录")
    parser.add_argument("--toc", action="store_true", help="生成目录")
    parser.add_argument("--font", help="Typst 字体家族全名")
    parser.add_argument("--semantic", action="store_true", help="用 TypeSafe 分类普通引用块")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--force", action="store_true", help="覆盖已有输出")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input.expanduser().resolve()
    if not input_path.is_file():
        raise BuildError(f"Markdown 文件不存在: {input_path}")
    root = (args.root.expanduser().resolve() if args.root else input_path.parent)
    if not root.is_dir() or not within_root(input_path, root):
        raise BuildError("项目根目录必须存在，并包含输入 Markdown")
    output_path = (args.output.expanduser().resolve() if args.output else input_path.with_suffix(".pdf"))
    typst_path = (
        args.typst_path.expanduser().resolve()
        if args.typst_path
        else output_path.with_suffix(".typ")
    )
    for path in (output_path, typst_path):
        if not within_root(path, root):
            raise BuildError(f"输出必须位于项目根目录内: {path}")
        if path.exists() and not args.force:
            raise BuildError(f"输出已存在，使用 --force 才能覆盖: {path}")
    if output_path.suffix.lower() != ".pdf" or typst_path.suffix.lower() != ".typ":
        raise BuildError("输出扩展名必须分别为 .pdf 和 .typ")
    receipt_path = output_path.with_name(f"{output_path.stem}.semantic-receipt.json")
    if args.semantic and receipt_path.exists() and not args.force:
        raise BuildError(f"语义回执已存在，使用 --force 才能覆盖: {receipt_path}")

    pandoc_version = run(["pandoc", "--version"]).stdout.splitlines()[0]
    typst_version = run(["typst", "--version"]).stdout.strip()
    version_match = re.search(r"typst (\d+)\.(\d+)\.", typst_version)
    if not version_match or version_match.groups() != ("0", "15"):
        raise BuildError(f"此技能已验证 Typst 0.15.x，当前版本为: {typst_version}")
    if "typst" not in run(["pandoc", "--list-output-formats"]).stdout.splitlines():
        raise BuildError("当前 Pandoc 没有 Typst writer")

    source = input_path.read_text(encoding="utf-8")
    ast = json.loads(
        run(
            ["pandoc", "-f", "markdown+tex_math_dollars+autolink_bare_uris+emoji", "-t", "json", str(input_path)]
        ).stdout
    )
    quotes: list[dict[str, Any]] = []
    walk_blocks(ast["blocks"], [""], quotes)
    images = image_map(ast, input_path, typst_path, root)
    font = choose_font(args.font, source)

    decisions: list[dict[str, Any]] = []
    if args.semantic:
        candidates = [
            quote.copy()
            for quote in quotes
            if not quote["explicit_alert"] and quote["text"]
        ]
        for candidate in candidates:
            candidate.pop("explicit_alert")
        decisions, receipt = classify_quotes(
            candidates,
            source=source,
            endpoint=args.endpoint,
            model=args.model,
            timeout=args.timeout,
        )
        atomic_write(
            receipt_path,
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        )

    decision_map = {
        str(decision["index"]): decision
        for decision in decisions
        if decision["action"] == "callout"
    }
    descriptor, runtime_name = tempfile.mkstemp(prefix="md2typst-runtime-", suffix=".json")
    temporary_pdf: Path | None = None
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump({"quotes": decision_map, "images": images}, handle)
        command = [
            "pandoc",
            "-f",
            "markdown+tex_math_dollars+autolink_bare_uris+emoji",
            "-t",
            "typst",
            "--standalone",
            "--wrap=none",
            f"--template={TEMPLATE}",
            f"--lua-filter={CALLOUTS_FILTER}",
            f"--metadata=mainfont={font}",
            str(input_path),
        ]
        if "lang" not in ast.get("meta", {}):
            command.append(f"--metadata=lang={'zh-CN' if HAN_RE.search(source) else 'en'}")
        if args.toc:
            command.append("--toc")
        environment = os.environ.copy()
        environment["MD2TYPST_RUNTIME"] = runtime_name
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        if result.returncode != 0:
            raise BuildError(f"Pandoc 生成 Typst 失败:\n{result.stderr.strip()}")
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        atomic_write(typst_path, result.stdout)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, pdf_name = tempfile.mkstemp(
            dir=output_path.parent, prefix=f".{output_path.stem}.", suffix=".pdf"
        )
        os.close(descriptor)
        temporary_pdf = Path(pdf_name)
        run(
            [
                "typst",
                "compile",
                "--root",
                str(root),
                "--jobs",
                "1",
                "--diagnostic-format",
                "short",
                str(typst_path),
                str(temporary_pdf),
            ]
        )
        os.replace(temporary_pdf, output_path)
        temporary_pdf = None
    finally:
        Path(runtime_name).unlink(missing_ok=True)
        if temporary_pdf is not None:
            temporary_pdf.unlink(missing_ok=True)

    print(f"Typst: {typst_path}")
    print(f"PDF: {output_path}")
    if args.semantic:
        print(f"语义回执: {receipt_path}")
        print(
            "语义决策: "
            + ", ".join(
                f"{action}={sum(item['action'] == action for item in decisions)}"
                for action in ("callout", "quote", "unresolved")
            )
        )
    print(f"{pandoc_version}; {typst_version}; font={font}")


if __name__ == "__main__":
    try:
        main()
    except (BuildError, SemanticError, json.JSONDecodeError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        sys.exit(1)
