import argparse
import json
import re
from pathlib import Path


def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except OSError:
        return False


_IDENT_RE = re.compile(r"^[A-Za-z_][\w.]*$")


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _extract_block(text: str, keyword: str) -> str:
    idx = text.find(keyword)
    if idx < 0:
        return ""
    brace_start = text.find("{", idx)
    if brace_start < 0:
        return ""
    depth = 0
    for i in range(brace_start, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[brace_start + 1 : i]
    return ""


def _parse_patch_names_from_boundary_file(boundary_text: str) -> list[str]:
    lines = boundary_text.splitlines()
    patches: list[str] = []

    in_list = False
    for i, line in enumerate(lines):
        s = line.strip()
        if not in_list:
            if s == "(":
                in_list = True
            continue
        if s == ")":
            break

        if not s or s.startswith("//"):
            continue

        m_inline = re.match(r"^([A-Za-z_][\w.]*)\s*\{\s*$", s)
        if m_inline:
            patches.append(m_inline.group(1))
            continue

        if _IDENT_RE.match(s):
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("{"):
                patches.append(s)

    return patches


def _parse_top_level_patch_names_from_boundary_field(boundary_field_block: str) -> list[str]:
    names: list[str] = []
    depth = 0

    for line in boundary_field_block.splitlines():
        s = line.strip()
        if not s:
            continue

        if depth == 0:
            m = re.match(r"^([A-Za-z_][\w.]*)\s*\{", s)
            if m:
                names.append(m.group(1))

        depth += s.count("{") - s.count("}")

    return names


def audit_case(case_dir: Path) -> dict:
    required_dirs = [case_dir / "0", case_dir / "constant", case_dir / "system"]
    required_files = [
        case_dir / "system" / "controlDict",
        case_dir / "system" / "fvSchemes",
        case_dir / "system" / "fvSolution",
    ]

    optional_props = [
        case_dir / "constant" / "transportProperties",
        case_dir / "constant" / "thermophysicalProperties",
    ]

    report = {
        "case_dir": str(case_dir),
        "missing": [],
        "warnings": [],
        "patch_mismatches": [],
        "ok": True,
    }

    for d in required_dirs:
        if not _exists(d) or not d.is_dir():
            report["missing"].append(str(d))

    for f in required_files:
        if not _exists(f) or not f.is_file():
            report["missing"].append(str(f))

    if not any(_exists(p) and p.is_file() for p in optional_props):
        report["warnings"].append(
            "Missing both constant/transportProperties and constant/thermophysicalProperties"
        )

    poly_boundary = case_dir / "constant" / "polyMesh" / "boundary"
    if _exists(poly_boundary):
        boundary_text = _read_text(poly_boundary)
        mesh_patches = _parse_patch_names_from_boundary_file(boundary_text)

        if not mesh_patches:
            report["warnings"].append(
                "Unable to extract patch names from constant/polyMesh/boundary"
            )
        else:
            zero_dir = case_dir / "0"
            if _exists(zero_dir) and zero_dir.is_dir():
                for field_file in sorted(zero_dir.iterdir()):
                    if not field_file.is_file():
                        continue
                    if field_file.name.startswith("."):
                        continue

                    field_text = _read_text(field_file)
                    block = _extract_block(field_text, "boundaryField")
                    if not block:
                        continue

                    field_patches = _parse_top_level_patch_names_from_boundary_field(block)
                    if not field_patches:
                        continue

                    missing_in_field = sorted(set(mesh_patches) - set(field_patches))
                    extra_in_field = sorted(set(field_patches) - set(mesh_patches))

                    if missing_in_field or extra_in_field:
                        report["patch_mismatches"].append(
                            {
                                "field": str(field_file),
                                "missing_in_field": missing_in_field,
                                "extra_in_field": extra_in_field,
                            }
                        )

            if report["patch_mismatches"]:
                report["warnings"].append(
                    "Patch mismatch detected between constant/polyMesh/boundary and one or more 0/* files"
                )

    report["ok"] = (len(report["missing"]) == 0) and (len(report["patch_mismatches"]) == 0)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    case_dir = Path(args.case_dir).resolve()
    rep = audit_case(case_dir)

    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print(f"case_dir: {rep['case_dir']}")
        if rep["missing"]:
            print("missing:")
            for m in rep["missing"]:
                print(f"- {m}")
        if rep["warnings"]:
            print("warnings:")
            for w in rep["warnings"]:
                print(f"- {w}")
        print(f"ok: {rep['ok']}")

    return 0 if rep["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
