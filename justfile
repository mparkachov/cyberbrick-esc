set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

device := env_var_or_default("DEVICE", "auto")
mpremote := ".venv/bin/mpremote"
prepare_repl := "scripts/mp_prepare_repl.py"
serial_fs := "scripts/mp_serial_fs.py"
backup_root := "device-backups"
mpremote_connect_delay_s := "1.5"
clear_safe_repl := "import os\nfor p in ('cyberbrick_boot_pending.txt','cyberbrick_safe_repl.txt','main.poc.py'):\n    try:\n        os.remove(p)\n    except OSError:\n        pass"

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

mp-tree: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    "$PWD/.venv/bin/python" "{{serial_fs}}" --device "{{device}}" tree

mp-cat-boot: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    "$PWD/.venv/bin/python" "{{serial_fs}}" --device "{{device}}" cat :boot.py

mp-cat-main: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    "$PWD/.venv/bin/python" "{{serial_fs}}" --device "{{device}}" cat :main.py

mp-cat-boot-marker: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    "$PWD/.venv/bin/python" "{{serial_fs}}" --device "{{device}}" cat :poc_boot_seen.txt

mp-repl: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    port="$("$PWD/.venv/bin/python" "{{prepare_repl}}" "{{device}}")"
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume repl

mp-backup: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    root="$PWD"
    port="$("$root/.venv/bin/python" "$root/{{prepare_repl}}" "{{device}}")"
    stamp="$(date +%Y%m%d-%H%M%S)"
    dest="$root/{{backup_root}}/$stamp"
    mkdir -p "$dest/files"
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs tree : > "$dest/tree.txt" || true
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs cp -r : "$dest/files"
    printf 'Backed up MicroPython filesystem to %s\n' "$dest"

deploy-blink: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    root="$PWD"
    just mp-backup
    port="$("$root/.venv/bin/python" "$root/{{prepare_repl}}" "{{device}}")"
    mkdir -p "$root/.cache"
    tmp="$(mktemp -d "$root/.cache/mpremote.XXXXXX")"
    trap 'rm -rf "$tmp"' EXIT
    if "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs cp -f :boot.stock.py "$tmp/boot.stock.py" >/dev/null 2>&1; then
        printf 'Remote boot.stock.py already exists; leaving it unchanged.\n'
    else
        "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs cp -f :boot.py "$tmp/boot.py"
        "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs cp -f "$tmp/boot.py" :boot.stock.py
    fi
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs cp -f micropython/examples/blink_boot.py :boot.py + fs cp -f micropython/examples/blink_main.py :main.py + exec "{{clear_safe_repl}}" + reset

run-blink: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    port="$("$PWD/.venv/bin/python" "{{prepare_repl}}" "{{device}}")"
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume run micropython/examples/blink_main.py

run-led-probe: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    port="$("$PWD/.venv/bin/python" "{{prepare_repl}}" "{{device}}")"
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume run micropython/examples/led_probe.py

deploy: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    root="$PWD"
    just mp-backup
    port="$("$root/.venv/bin/python" "$root/{{prepare_repl}}" "{{device}}")"
    mkdir -p "$root/.cache"
    tmp="$(mktemp -d "$root/.cache/mpremote.XXXXXX")"
    trap 'rm -rf "$tmp"' EXIT
    if "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs cp -f :boot.stock.py "$tmp/boot.stock.py" >/dev/null 2>&1; then
        printf 'Remote boot.stock.py already exists; leaving it unchanged.\n'
    else
        "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs cp -f :boot.py "$tmp/boot.py"
        "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs cp -f "$tmp/boot.py" :boot.stock.py
    fi
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs mkdir :lib >/dev/null 2>&1 || true
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs mkdir :lib/cyberbrick_esc >/dev/null 2>&1 || true
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs cp -f micropython/boot.py :boot.py + fs cp -f micropython/main.py :main.py + fs cp -f micropython/lib/cyberbrick_esc/*.py :lib/cyberbrick_esc/ + exec "{{clear_safe_repl}}" + reset

mp-stop: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    "$PWD/.venv/bin/python" "{{serial_fs}}" --device "{{device}}" stop

mp-restore: _ensure-tools
    #!/usr/bin/env bash
    set -euo pipefail
    root="$PWD"
    port="$("$root/.venv/bin/python" "$root/{{prepare_repl}}" "{{device}}")"
    latest="$(find "$root/{{backup_root}}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tail -n 1)"
    test -n "$latest" || { echo "No backup found under {{backup_root}}."; exit 1; }
    files="$latest/files"
    test -d "$files" || { echo "Backup has no files directory: $latest"; exit 1; }
    for remote_path in :main.py :main.poc.py :boot.stock.py :cyberbrick_boot_pending.txt :cyberbrick_safe_repl.txt :lib/cyberbrick_esc/app.py :lib/cyberbrick_esc/config.py :lib/cyberbrick_esc/led.py :lib/cyberbrick_esc/pwm_input.py :lib/cyberbrick_esc/safety.py :lib/cyberbrick_esc/__init__.py; do
        "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs rm "$remote_path" >/dev/null 2>&1 || true
    done
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs rmdir :lib/cyberbrick_esc >/dev/null 2>&1 || true
    "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs rmdir :lib >/dev/null 2>&1 || true
    shopt -s nullglob dotglob
    items=("$files"/*)
    if [ "${#items[@]}" -gt 0 ]; then
        "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume fs cp -r "${items[@]}" : + reset
    else
        "{{mpremote}}" connect "$port" sleep {{mpremote_connect_delay_s}} resume reset
    fi
    printf 'Restored MicroPython filesystem from %s\n' "$latest"

test:
    #!/usr/bin/env bash
    set -euo pipefail
    root="$PWD"
    python="${PYTHON:-python3}"
    PYTHONPATH="$root/micropython/lib" "$python" -m unittest discover -s tests
    "$python" -m py_compile scripts/*.py micropython/boot.py micropython/main.py micropython/examples/*.py micropython/lib/cyberbrick_esc/*.py tests/*.py
