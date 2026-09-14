#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
root_dir="$(cd -- "$script_dir/.." && pwd)"
missing=0

for command_name in bash jq; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        printf 'doctor: missing command: %s\n' "$command_name" >&2
        missing=1
    fi
done

for required_path in \
    justfile \
    schemas/stance-package.schema.json \
    schemas/conflict-report.schema.json \
    schemas/oar-output-manifest.schema.json \
    templates/stance-package.example.json \
    framework \
    tools
do
    if [[ ! -e "$root_dir/$required_path" ]]; then
        printf 'doctor: missing repository path: %s\n' "$required_path" >&2
        missing=1
    fi
done

if (( missing != 0 )); then
    exit 1
fi

printf 'doctor: product repository prerequisites are present\n'
