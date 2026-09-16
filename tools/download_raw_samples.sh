#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$project_dir/tools/sync_raw_corpus.py" "$@"
