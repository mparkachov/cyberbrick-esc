# This file intentionally replaces stock boot.py only after `just mp-backup`.
# `just mp-stop` restores the original boot.py from remote boot.stock.py.

import gc
import os
from time import sleep_ms


BOOT_PENDING_FILE = "cyberbrick_boot_pending.txt"
SAFE_REPL_FILE = "cyberbrick_safe_repl.txt"
APP_MAIN_FILE = "main.py"
SAFE_MAIN_FILE = "main.poc.py"
RECOVERY_WINDOW_MS = 5000


def file_exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def remove_file(path):
    try:
        os.remove(path)
    except OSError:
        pass


def write_file(path, text):
    with open(path, "w") as handle:
        handle.write(text)


def move_app_main_to_safe_name():
    if not file_exists(APP_MAIN_FILE):
        return

    remove_file(SAFE_MAIN_FILE)
    try:
        os.rename(APP_MAIN_FILE, SAFE_MAIN_FILE)
    except OSError:
        remove_file(APP_MAIN_FILE)


gc.collect()

if file_exists(SAFE_REPL_FILE) or file_exists(BOOT_PENDING_FILE):
    remove_file(BOOT_PENDING_FILE)
    write_file(SAFE_REPL_FILE, "CyberBrick ESC safe REPL mode\n")
    move_app_main_to_safe_name()
    print("CyberBrick ESC safe REPL mode; run just deploy or just mp-stop.")
else:
    write_file(BOOT_PENDING_FILE, "Reset again before app start to enter safe REPL.\n")
    try:
        sleep_ms(RECOVERY_WINDOW_MS)
        remove_file(BOOT_PENDING_FILE)
        exec(open(APP_MAIN_FILE).read(), globals())
    except KeyboardInterrupt:
        remove_file(BOOT_PENDING_FILE)
        write_file(SAFE_REPL_FILE, "CyberBrick ESC safe REPL mode\n")
        move_app_main_to_safe_name()
        print("CyberBrick ESC boot interrupted; safe REPL mode active.")
