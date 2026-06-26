#!/bin/bash

extract_atomtypes_from_file() {
    local file="$1"
    awk '
    /^\[ atomtypes \]$/ { flag=1; next }
    /^\[ .* \]$/ { flag=0 }
    flag && !/^;/ && NF>0 { print }
    ' "$file" | tr -d '\000'
}

remove_atomtypes_from_file() {
    local file="$1"
    awk '
    /^\[ atomtypes \]$/ { flag=1; next }
    /^\[ .* \]$/ { flag=0 }
    !flag { print }
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
}

extract_defaults_from_file() {
    local file="$1"
    awk '
    /^\[ defaults \]$/ { flag=1; next }
    /^\[ .* \]$/ { flag=0 }
    flag && !/^;/ && NF>0 { print }
    ' "$file" | tr -d '\000'
}

remove_defaults_from_file() {
    local file="$1"
    awk '
    /^\[ defaults \]$/ { flag=1; next }
    /^\[ .* \]$/ { flag=0 }
    !flag { print }
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
}

dedup_atomtypes() {
    local input_file="$1"
    local output_file="$2"
    local conflicts_file="${3:-}"

    if [ -n "$conflicts_file" ]; then
        # Full deduplication with conflict detection
        python3 - <<PY
from pathlib import Path
src = Path(r"$input_file")
lines = []
seen = set()
conflicts = []
by_atom = {}
for raw in src.read_text(encoding="utf-8", errors="ignore").splitlines():
    line = raw.strip()
    if not line or line.startswith(";") or line.startswith("#") or (line.startswith("[") and line.endswith("]")):
        continue
    atom = line.split()[0]
    existing = by_atom.get(atom)
    if existing is not None and existing != line:
        conflicts.append(f"{atom}\t{existing}\t{line}")
    else:
        by_atom[atom] = line
    if atom in seen:
        continue
    seen.add(atom)
    lines.append(line)
Path(r"$output_file").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
Path(r"$conflicts_file").write_text("\n".join(conflicts) + ("\n" if conflicts else ""), encoding="utf-8")
PY
    else
        # Simple deduplication
        sort -k1,1 -u "$input_file" > "$output_file"
    fi
}

merge_topology() {
    local output_file="${1:-topol.top}"
    shift
    local system_name="${1:-}"
    if [ -n "$system_name" ]; then shift; fi
    local source_files=("$@")
    local temp_atomtypes="/tmp/atomtypes.tmp.$$"
    local temp_defaults="/tmp/defaults.tmp.$$"

    > "$temp_atomtypes"
    > "$temp_defaults"

    for source_file in "${source_files[@]}"; do
        if [ -f "$source_file" ]; then
            extracted=$(extract_atomtypes_from_file "$source_file")
            if [ -n "$extracted" ]; then
                echo "$extracted" >> "$temp_atomtypes"
                remove_atomtypes_from_file "$source_file"
            fi
            local defaults_data
            defaults_data=$(extract_defaults_from_file "$source_file")
            if [ -n "$defaults_data" ]; then
                echo "$defaults_data" >> "$temp_defaults"
                remove_defaults_from_file "$source_file"
            fi
        fi
    done

    if [ -f "原子类型.txt" ]; then
        awk '!/^#include / && !/^\[/' "原子类型.txt" >> "$temp_atomtypes"
    fi

    local deduped_atomtypes="/tmp/atomtypes.dedup.$$"
    dedup_atomtypes "$temp_atomtypes" "$deduped_atomtypes"

    # Use the first [ defaults ] found (all molecules should share the same values)
    local defaults_line
    defaults_line=$(head -n 1 "$temp_defaults" 2>/dev/null)
    if [ -z "$defaults_line" ]; then
        defaults_line="     1              2              yes            0.5       0.8333"
    fi

    {
        head -n 5 "$output_file" 2>/dev/null || echo "; Topology file"
        echo ""
        echo "[ defaults ]"
        echo "; nbfunc        comb-rule       gen-pairs       fudgeLJ    fudgeQQ"
        echo "$defaults_line"
        echo ""
        echo "[ atomtypes ]"
        echo "; name   at.num      mass       charge   ptype     sigma (nm)    epsilon (kJ/mol)"
        cat "$deduped_atomtypes"
        echo ""

        for source_file in "${source_files[@]}"; do
            if [ -f "$source_file" ]; then
                echo "#include \"${source_file}\""
            fi
        done

        echo ""
        echo "[ system ]"
        echo "${system_name:-System}"
        echo ""
        echo "[ molecules ]"
        echo "; Compound        #mols"

        # Write molecule counts from box.inp if available
        if [ -f "box.inp" ]; then
            awk '/structure/ && !/end structure/ {
                mol=$2
                getline
                if (/number/) {
                    num=$2
                    gsub(/\.pdb$/, "", mol)
                    print mol "\t" num
                }
            }' box.inp
        fi
    } > "$output_file"

    cp "$deduped_atomtypes" "原子类型.txt" 2>/dev/null || true
    rm -f "$temp_atomtypes" "$deduped_atomtypes" "$temp_defaults"
}

merge_vle_topology() {
    local base_topology="$1"
    local gas_molecules_str="$2"
    local inserted_gas_molecules_str="$3"
    local output_file="$4"

    local tmp_dir
    tmp_dir=$(mktemp -d)
    trap 'rm -rf "$tmp_dir"' EXIT

    local preamble_file="$tmp_dir/preamble.txt"
    local base_includes_file="$tmp_dir/base_includes.txt"
    local system_block_file="$tmp_dir/system_block.txt"
    local base_molecules_file="$tmp_dir/base_molecules.txt"
    local temp_atomtypes="$tmp_dir/all_atomtypes.txt"
    local deduped_atomtypes="$tmp_dir/deduped_atomtypes.txt"
    local atomtype_conflicts="$tmp_dir/atomtype_conflicts.txt"

    # Extract [ defaults ] from base topology
    local defaults_line
    defaults_line=$(extract_defaults_from_file "$base_topology" | head -n 1)
    if [ -z "$defaults_line" ]; then
        defaults_line="     1              2              yes            0.5       0.8333"
    fi

    local atomtypes_line
    atomtypes_line=$(grep -n '^\[ atomtypes \]$' "$base_topology" | head -n 1 | cut -d: -f1 || true)
    if [ -n "$atomtypes_line" ]; then
        awk -v stop="$atomtypes_line" 'NR < stop && $1 != "#include" {print}' "$base_topology" > "$preamble_file"
    else
        : > "$preamble_file"
    fi
    awk '/^#include / {print}' "$base_topology" > "$base_includes_file"
    awk 'BEGIN {capture=0} /^\[ system \]$/ {capture=1} /^\[ molecules \]$/ {capture=0} capture {print}' "$base_topology" > "$system_block_file"
    awk 'BEGIN {capture=0} /^\[ molecules \]$/ {capture=1; next} capture && !/^;/ && NF>0 {print $1, $2}' "$base_topology" > "$base_molecules_file"

    > "$temp_atomtypes"

    if [ -f "原子类型.txt" ]; then
        awk '!/^#include / && !/^\[/' "原子类型.txt" >> "$temp_atomtypes"
    fi

    awk '
    /^\[ atomtypes \]$/ {flag=1; next}
    /^#include / && flag {flag=0}
    /^\[ .* \]$/ && flag {flag=0}
    flag && !/^;/ && NF>0 {print}
    ' "$base_topology" >> "$temp_atomtypes"

    for mol_pair in $gas_molecules_str; do
        mol_name="${mol_pair%%:*}"
        if [ -f "${mol_name}.itp" ]; then
            local extracted
            extracted=$(extract_atomtypes_from_file "${mol_name}.itp")

            if [ -n "$extracted" ]; then
                echo "$extracted" >> "$temp_atomtypes"
                remove_atomtypes_from_file "${mol_name}.itp"
            fi
        fi
    done

    while IFS= read -r include_line; do
        local base_itp
        base_itp=$(echo "$include_line" | sed -n 's/#include "\([^"]*\)"/\1/p')
        if [ -n "$base_itp" ] && [ -f "$base_itp" ]; then
            local base_extracted
            base_extracted=$(extract_atomtypes_from_file "$base_itp")

            if [ -n "$base_extracted" ]; then
                echo "$base_extracted" >> "$temp_atomtypes"
                remove_atomtypes_from_file "$base_itp"
            fi
        fi
    done < "$base_includes_file"

    dedup_atomtypes "$temp_atomtypes" "$deduped_atomtypes" "$atomtype_conflicts"

    cp "$deduped_atomtypes" "原子类型.txt"

    {
        cat "$preamble_file"
        echo
        echo "[ defaults ]"
        echo "; nbfunc        comb-rule       gen-pairs       fudgeLJ    fudgeQQ"
        echo "$defaults_line"
        echo
        echo "[ atomtypes ]"
        echo "; name   at.num      mass       charge   ptype     sigma (nm)    epsilon (kJ/mol)"
        cat "$deduped_atomtypes"
        echo
        cat "$base_includes_file"
        for mol_pair in $inserted_gas_molecules_str; do
            mol_name="${mol_pair%%:*}"
            include_line="#include \"${mol_name}.itp\""
            if ! grep -Fxq "$include_line" "$base_includes_file"; then
                echo "$include_line"
            fi
        done
        echo
        cat "$system_block_file"
        echo
        echo "[ molecules ]"
        echo "; Compound        #mols"
    } > "$output_file"

    python3 - <<PY
from collections import OrderedDict
from pathlib import Path
counts = OrderedDict()
base_file = Path(r"$base_molecules_file")
for raw in base_file.read_text(encoding="utf-8", errors="ignore").splitlines():
    parts = raw.split()
    if len(parts) < 2:
        continue
    counts[parts[0]] = counts.get(parts[0], 0) + int(parts[1])
for raw in r"""$inserted_gas_molecules_str""".split():
    name, count = raw.split(":", 1)
    counts[name] = counts.get(name, 0) + int(count)
with Path(r"$output_file").open("a", encoding="utf-8") as fh:
    for name, count in counts.items():
        fh.write(f"{name:<15s}  {count:6d}\n")
PY
}
