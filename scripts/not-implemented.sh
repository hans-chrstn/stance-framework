#!/usr/bin/env bash
set -euo pipefail

if (( $# == 0 )); then
    target=command
else
    target="$1"
fi

printf 'NOT IMPLEMENTED: %s\n' "$target" >&2
printf 'This repository stage is not implemented yet.\n' >&2
exit 2
