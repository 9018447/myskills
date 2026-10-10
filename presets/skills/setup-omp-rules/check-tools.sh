#!/usr/bin/env bash
# Check whether the tools the search-routing and coding-labor rules depend on are on PATH.
# Always exits 0: missing tools do not block the install — report only, the user decides whether to install first.

for t in jg rg zg ast-grep gitnexus omp; do
  if command -v "$t" >/dev/null 2>&1; then
    echo "ok      $t -> $(command -v "$t")"
  else
    echo "MISSING $t"
  fi
done

# jg needs OpenRouter credentials; the binary alone is not enough
if command -v jg >/dev/null 2>&1; then
  jg doctor >/dev/null 2>&1 && echo "ok      jg auth (Jev reachable)" || echo "WARN    jg auth not configured/unreachable, run jg auth once"
fi

# LSP is not a CLI tool; it is built into omp, so we can only note it
echo "note    LSP is built into omp; the script cannot check it"
