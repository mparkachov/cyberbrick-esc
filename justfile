set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

board := env_var_or_default("BOARD", "esp32c3_devkitm")
device := env_var_or_default("DEVICE", "/dev/tty.usbmodem1101")
west := ".venv/bin/west"
esp_idf_path := ".zephyr/modules/hal/espressif"

install:
    python3 scripts/zephyr_install.py

build:
    test -x "{{west}}" || { echo "Run 'just install' first."; exit 1; }
    cd .zephyr && ../"{{west}}" -z zephyr build -b "{{board}}" -d ../build ..

flash:
    test -x "{{west}}" || { echo "Run 'just install' first."; exit 1; }
    test -d build || { echo "Run 'just build' before flashing."; exit 1; }
    cd .zephyr && ../"{{west}}" -z zephyr flash -d ../build --runner esp32 --skip-rebuild --esp-device "{{device}}" --esp-idf-path "../{{esp_idf_path}}"

log:
    screen "{{device}}" 115200
