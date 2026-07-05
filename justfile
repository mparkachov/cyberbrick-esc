set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

board := env_var_or_default("BOARD", "esp32c3_devkitm")
device := env_var_or_default("DEVICE", "/dev/tty.usbmodem1101")
west := ".venv/bin/west"
esp_idf_path := ".esp-idf"
esp_tools_path := ".espressif"

install:
    python3 scripts/zephyr_install.py

clean:
    rm -rf build .cache/ccache

build:
    #!/usr/bin/env bash
    set -euo pipefail
    root="$PWD"
    test -x "$root/{{west}}" || { echo "Run 'just install' first."; exit 1; }
    prefix="$(python3 "$root/scripts/esp_toolchain_prefix.py")"
    export IDF_PATH="$root/{{esp_idf_path}}"
    export IDF_TOOLS_PATH="$root/{{esp_tools_path}}"
    export PATH="$root/.venv/bin:$PATH"
    export CCACHE_DIR="$root/.cache/ccache"
    mkdir -p "$CCACHE_DIR"
    eval "$("$root/.venv/bin/python" "$IDF_PATH/tools/idf_tools.py" export)"
    if [ -d "$root/build" ] && [ ! -f "$root/build/build.ninja" ]; then
        rm -rf "$root/build"
    fi
    cd "$root/.zephyr"
    ZEPHYR_TOOLCHAIN_VARIANT=cross-compile CROSS_COMPILE="$prefix" "$root/{{west}}" -z zephyr build -p auto -b "{{board}}" -d "$root/build" "$root"

flash:
    #!/usr/bin/env bash
    set -euo pipefail
    root="$PWD"
    test -x "$root/{{west}}" || { echo "Run 'just install' first."; exit 1; }
    test -d "$root/build" || { echo "Run 'just build' before flashing."; exit 1; }
    export IDF_PATH="$root/{{esp_idf_path}}"
    export IDF_TOOLS_PATH="$root/{{esp_tools_path}}"
    export PATH="$root/.venv/bin:$PATH"
    eval "$("$root/.venv/bin/python" "$IDF_PATH/tools/idf_tools.py" export)"
    cd "$root/.zephyr"
    "$root/{{west}}" -z zephyr flash -d "$root/build" --runner esp32 --no-rebuild --esp-device "{{device}}" --esp-idf-path "$IDF_PATH"

log:
    screen "{{device}}" 115200
