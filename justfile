set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

device := env_var_or_default("DEVICE", "auto")
mpremote := ".venv/bin/mpremote"
prepare_repl := "scripts/mp_prepare_repl.py"
backup_root := "device-backups"

default:
    just --list

install:
    python3 -m venv .venv
    .venv/bin/python -m pip --version >/dev/null 2>&1 || .venv/bin/python -m ensurepip --upgrade
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt

_ensure-tools:
    test -x "{{mpremote}}" || { echo "Run 'just install' first."; exit 1; }

mp-list: _ensure-tools
    "{{mpremote}}" connect list

mp-repl: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    port="$("$PWD/.venv/bin/python" "{{prepare_repl}}" "{{device}}")"
    "{{mpremote}}" connect "$port" resume repl

mp-backup: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    root="$PWD"
    port="$("$root/.venv/bin/python" "$root/{{prepare_repl}}" "{{device}}")"
    stamp="$(date +%Y%m%d-%H%M%S)"
    dest="$root/{{backup_root}}/$stamp"
    mkdir -p "$dest/files"
    "{{mpremote}}" connect "$port" resume fs tree : > "$dest/tree.txt" || true
    "{{mpremote}}" connect "$port" resume fs cp -r : "$dest/files"
    printf 'Backed up MicroPython filesystem to %s\n' "$dest"

deploy-blink: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    just mp-backup
    port="$("$PWD/.venv/bin/python" "{{prepare_repl}}" "{{device}}")"
    "{{mpremote}}" connect "$port" resume fs cp -f micropython/examples/blink_main.py :main.py + reset

deploy: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    just mp-backup
    port="$("$PWD/.venv/bin/python" "{{prepare_repl}}" "{{device}}")"
    "{{mpremote}}" connect "$port" resume exec "import os\nfor d in ('lib', 'lib/cyberbrick_esc'):\n    try:\n        os.mkdir(d)\n    except OSError:\n        pass" fs cp -f micropython/main.py :main.py + fs cp -f micropython/lib/cyberbrick_esc/*.py :lib/cyberbrick_esc/ + reset

mp-stop: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    port="$("$PWD/.venv/bin/python" "{{prepare_repl}}" "{{device}}")"
    "{{mpremote}}" connect "$port" resume exec "import os\ntry:\n    os.remove('main.py')\nexcept OSError:\n    pass" reset

mp-restore: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    root="$PWD"
    port="$("$root/.venv/bin/python" "$root/{{prepare_repl}}" "{{device}}")"
    latest="$(find "$root/{{backup_root}}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tail -n 1)"
    test -n "$latest" || { echo "No backup found under {{backup_root}}."; exit 1; }
    files="$latest/files"
    test -d "$files" || { echo "Backup has no files directory: $latest"; exit 1; }
    "{{mpremote}}" connect "$port" resume exec "import os\nfor p in ('main.py', 'lib/cyberbrick_esc/app.py', 'lib/cyberbrick_esc/config.py', 'lib/cyberbrick_esc/led.py', 'lib/cyberbrick_esc/pwm_input.py', 'lib/cyberbrick_esc/safety.py', 'lib/cyberbrick_esc/__init__.py'):\n    try:\n        os.remove(p)\n    except OSError:\n        pass\nfor d in ('lib/cyberbrick_esc', 'lib'):\n    try:\n        os.rmdir(d)\n    except OSError:\n        pass"
    shopt -s nullglob dotglob
    items=("$files"/*)
    if [ "${#items[@]}" -gt 0 ]; then
        "{{mpremote}}" connect "$port" resume fs cp -r "${items[@]}" : + reset
    else
        "{{mpremote}}" connect "$port" resume reset
    fi
    printf 'Restored MicroPython filesystem from %s\n' "$latest"

test:
    #!/usr/bin/env bash
    set -euo pipefail
    root="$PWD"
    python="${PYTHON:-python3}"
    PYTHONPATH="$root/micropython/lib" "$python" -m unittest discover -s tests
    "$python" -m py_compile scripts/*.py micropython/main.py micropython/examples/blink_main.py micropython/lib/cyberbrick_esc/*.py tests/*.py
