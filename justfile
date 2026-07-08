set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

device := env_var_or_default("DEVICE", "auto")
backup_root := "device-backups"

default:
    just --list

install:
    uv sync

mp-list:
    uv run mpremote connect list

mp-repl:
    uv run mpremote connect "{{device}}" resume repl

miniterm:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ "{{device}}" = "auto" ]; then
        echo "Set DEVICE to the serial port, for example: DEVICE=/dev/cu.usbmodem1101 just miniterm"
        exit 1
    fi
    uv run python -m serial.tools.miniterm --raw --dtr 0 --rts 0 "{{device}}" 115200

mp-backup:
    #!/usr/bin/env bash
    set -euo pipefail
    stamp="$(date +%Y%m%d-%H%M%S)"
    dest="{{backup_root}}/$stamp"
    mkdir -p "$dest/files"
    uv run mpremote connect "{{device}}" resume fs tree : > "$dest/tree.txt" || true
    uv run mpremote connect "{{device}}" resume fs --recursive cp : "$dest/files"
    printf 'Backed up MicroPython filesystem to %s\n' "$dest"

run-blink:
    uv run mpremote connect "{{device}}" resume run micropython/examples/blink_main.py

deploy-blink:
    #!/usr/bin/env bash
    set -euo pipefail
    just mp-backup
    mkdir -p .cache
    tmp="$(mktemp -d ".cache/stock-boot.XXXXXX")"
    trap 'rm -rf "$tmp"' EXIT
    if uv run mpremote connect "{{device}}" resume fs --force cp :boot.stock.py "$tmp/boot.stock.py" >/dev/null 2>&1; then
        printf 'Remote boot.stock.py already exists; leaving it unchanged.\n'
    else
        uv run mpremote connect "{{device}}" resume fs --force cp :boot.py "$tmp/boot.py"
        uv run mpremote connect "{{device}}" resume fs --force cp "$tmp/boot.py" :boot.stock.py
    fi
    uv run mpremote connect "{{device}}" resume fs --force cp micropython/examples/blink_boot.py :boot.py
    uv run mpremote connect "{{device}}" resume reset

deploy:
    #!/usr/bin/env bash
    set -euo pipefail
    just mp-backup
    mkdir -p .cache
    tmp="$(mktemp -d ".cache/stock-boot.XXXXXX")"
    trap 'rm -rf "$tmp"' EXIT
    if uv run mpremote connect "{{device}}" resume fs --force cp :boot.stock.py "$tmp/boot.stock.py" >/dev/null 2>&1; then
        printf 'Remote boot.stock.py already exists; leaving it unchanged.\n'
    else
        uv run mpremote connect "{{device}}" resume fs --force cp :boot.py "$tmp/boot.py"
        uv run mpremote connect "{{device}}" resume fs --force cp "$tmp/boot.py" :boot.stock.py
    fi
    uv run mpremote connect "{{device}}" resume fs mkdir :lib >/dev/null 2>&1 || true
    uv run mpremote connect "{{device}}" resume fs mkdir :lib/cyberbrick_esc >/dev/null 2>&1 || true
    uv run mpremote connect "{{device}}" resume fs --force cp micropython/examples/esc_boot.py :boot.py
    uv run mpremote connect "{{device}}" resume fs --force cp micropython/main.py :main.py
    uv run mpremote connect "{{device}}" resume fs --force cp micropython/lib/cyberbrick_esc/*.py :lib/cyberbrick_esc/
    uv run mpremote connect "{{device}}" resume reset

restore-stock:
    #!/usr/bin/env bash
    set -euo pipefail
    uv run mpremote connect "{{device}}" resume fs --force cp :boot.stock.py :boot.py
    uv run mpremote connect "{{device}}" resume fs rm :main.py >/dev/null 2>&1 || true
    uv run mpremote connect "{{device}}" resume fs rm :main.poc.py >/dev/null 2>&1 || true
    uv run mpremote connect "{{device}}" resume fs rm :poc_boot_seen.txt >/dev/null 2>&1 || true
    uv run mpremote connect "{{device}}" resume fs --recursive rm :lib/cyberbrick_esc >/dev/null 2>&1 || true
    uv run mpremote connect "{{device}}" resume fs rmdir :lib >/dev/null 2>&1 || true
    uv run mpremote connect "{{device}}" resume reset

test:
    uv run python -m unittest discover -s tests
    uv run python -m py_compile host/*.py micropython/main.py micropython/examples/*.py micropython/lib/cyberbrick_esc/*.py tests/*.py
