#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
bash -n "$ROOT/install.sh"
python3 -m py_compile "$ROOT/tools/steam-discord-bridge.py"
test -x "$ROOT/install.sh"
test -x "$ROOT/tools/steam-discord-bridge.py"
grep -q 'credentials' "$ROOT/README.md"
grep -q 'nvidia-capture' "$ROOT/install.sh"
grep -q 'Exec=%h/.local/bin/steam-discord-bridge' "$ROOT/autostart/steam-discord-bridge.desktop"
printf 'Static checks passed.\n'
