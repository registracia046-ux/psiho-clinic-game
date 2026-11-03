#!/usr/bin/env bash
# Обёртка: ./versions/rollback.sh list | <тег> | save "описание"
cd "$(dirname "$0")/.." && python3 versions/rollback.py "$@"
