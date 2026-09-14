#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
root_dir="$(cd -- "$script_dir/.." && pwd)"
failure=0
schema_count=0

while IFS= read -r schema_path; do
    schema_count=$((schema_count + 1))
    if ! jq empty "$schema_path" >/dev/null; then
        relative_path="$(printf '%s\n' "$schema_path" | sed "s#^$root_dir/##")"
        printf 'contract-check: invalid JSON: %s\n' \
            "$relative_path" >&2
        failure=1
    fi
done < <(find "$root_dir/schemas" -maxdepth 1 -type f -name '*.json' -print | sort)

if (( schema_count != 3 )); then
    printf 'contract-check: expected three product schemas, found %d\n' \
        "$schema_count" >&2
    failure=1
fi

if (( failure != 0 )); then
    exit 1
fi

printf 'contract-check: %d product schemas are readable\n' "$schema_count"
