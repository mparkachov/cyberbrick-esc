#!/usr/bin/env python3
"""Install the local Zephyr workspace used by the just recipes."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = PROJECT_ROOT / ".venv"
VENV_PYTHON = VENV_DIR / "bin" / "python"
WEST = VENV_DIR / "bin" / "west"
ZEPHYR_WORKSPACE = PROJECT_ROOT / ".zephyr"
ZEPHYR_BASE = ZEPHYR_WORKSPACE / "zephyr"
ZEPHYR_REPO = "https://github.com/zephyrproject-rtos/zephyr.git"
ESP_IDF_DIR = PROJECT_ROOT / ".esp-idf"
ESPRESSIF_TOOLS_DIR = PROJECT_ROOT / ".espressif"
ESP_IDF_REPO = "https://github.com/espressif/esp-idf.git"
STABLE_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def run(
    args: list[str],
    *,
    cwd: Path = PROJECT_ROOT,
    capture: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(args))
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        check=True,
        stdout=subprocess.PIPE if capture else None,
        env=env,
    )


def require_commands(commands: list[str]) -> None:
    missing = [command for command in commands if shutil.which(command) is None]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"Missing required command(s): {joined}")


def latest_stable_tag(repo_url: str) -> str:
    result = run(
        ["git", "ls-remote", "--tags", "--refs", repo_url, "v*"],
        capture=True,
    )

    tags: list[tuple[tuple[int, int, int], str]] = []
    for line in result.stdout.splitlines():
        if "refs/tags/" not in line:
            continue
        tag = line.rsplit("refs/tags/", 1)[1].strip()
        match = STABLE_TAG_RE.match(tag)
        if match:
            tags.append(((int(match.group(1)), int(match.group(2)), int(match.group(3))), tag))

    if not tags:
        raise SystemExit("Could not resolve a stable Zephyr tag from upstream.")

    return max(tags, key=lambda item: item[0])[1]


def ensure_venv() -> None:
    if not VENV_PYTHON.exists():
        run(["uv", "venv", "--python", "python3", str(VENV_DIR)])

    run(["uv", "pip", "install", "--python", str(VENV_PYTHON), "west", "esptool>=5.0.2"])


def ensure_workspace(tag: str) -> None:
    if not (ZEPHYR_WORKSPACE / ".west").exists():
        ZEPHYR_WORKSPACE.mkdir(exist_ok=True)
        run([str(WEST), "init", "-m", ZEPHYR_REPO, "--mr", tag, str(ZEPHYR_WORKSPACE)])
    else:
        run(["git", "fetch", "--tags", "origin"], cwd=ZEPHYR_BASE)
        run(["git", "checkout", "--detach", tag], cwd=ZEPHYR_BASE)

    run([str(WEST), "update"], cwd=ZEPHYR_WORKSPACE)


def ensure_esp_idf(tag: str) -> None:
    if not (ESP_IDF_DIR / ".git").exists():
        run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                tag,
                ESP_IDF_REPO,
                str(ESP_IDF_DIR),
            ]
        )
    else:
        run(
            [
                "git",
                "-c",
                "fetch.recurseSubmodules=false",
                "fetch",
                "--no-tags",
                "--depth",
                "1",
                "origin",
                f"+refs/tags/{tag}:refs/tags/{tag}",
            ],
            cwd=ESP_IDF_DIR,
        )
        run(["git", "checkout", "--detach", tag], cwd=ESP_IDF_DIR)


def install_esp_idf_python_requirements() -> None:
    requirement_files = [
        ESP_IDF_DIR / "tools" / "requirements" / "requirements.core.txt",
    ]
    for requirement_file in requirement_files:
        if requirement_file.exists():
            run(
                [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    str(VENV_PYTHON),
                    "-r",
                    str(requirement_file),
                ]
            )


def esp_idf_env() -> dict[str, str]:
    env = os.environ.copy()
    env["IDF_PATH"] = str(ESP_IDF_DIR)
    env["IDF_TOOLS_PATH"] = str(ESPRESSIF_TOOLS_DIR)
    env["PATH"] = f"{VENV_DIR / 'bin'}{os.pathsep}{env.get('PATH', '')}"
    return env


def install_esp_idf_tools() -> None:
    run(
        [
            str(VENV_PYTHON),
            str(ESP_IDF_DIR / "tools" / "idf_tools.py"),
            "install",
            "--targets",
            "esp32c3",
        ],
        cwd=ESP_IDF_DIR,
        env=esp_idf_env(),
    )
    run(
        [
            str(VENV_PYTHON),
            str(ESP_IDF_DIR / "tools" / "idf_tools.py"),
            "install",
            "--targets",
            "esp32c3",
            "cmake",
            "ninja",
        ],
        cwd=ESP_IDF_DIR,
        env=esp_idf_env(),
    )


def find_local_esp_toolchain_prefix() -> Path | None:
    candidates = sorted(
        ESPRESSIF_TOOLS_DIR.glob(
            "tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-gcc"
        )
    )
    if not candidates:
        return None

    compiler = candidates[-1]
    return compiler.with_name("riscv32-esp-elf-")


def install_python_requirements() -> None:
    requirement_files = [
        ZEPHYR_BASE / "scripts" / "requirements.txt",
        ZEPHYR_BASE / "scripts" / "requirements-build-test.txt",
    ]
    for requirement_file in requirement_files:
        if requirement_file.exists():
            run(
                [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    str(VENV_PYTHON),
                    "-r",
                    str(requirement_file),
                ]
            )


def verify_esp32c3_toolchain() -> None:
    if find_local_esp_toolchain_prefix() is not None:
        return

    raise SystemExit(
        "ESP32-C3 RISC-V toolchain was not installed under .espressif. "
        "Run 'just install' again and check the ESP-IDF tool installation output."
    )


def main() -> int:
    os.environ.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")
    os.environ.setdefault("UV_CACHE_DIR", str(PROJECT_ROOT / ".cache" / "uv"))

    require_commands(["python3", "uv", "git", "dtc", "screen"])
    ensure_venv()

    zephyr_tag = latest_stable_tag(ZEPHYR_REPO)
    print(f"Using Zephyr {zephyr_tag}")
    ensure_workspace(zephyr_tag)
    install_python_requirements()

    esp_idf_tag = latest_stable_tag(ESP_IDF_REPO)
    print(f"Using ESP-IDF {esp_idf_tag}")
    ensure_esp_idf(esp_idf_tag)
    install_esp_idf_python_requirements()
    install_esp_idf_tools()
    verify_esp32c3_toolchain()

    print("Zephyr and ESP-IDF workspaces are ready.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
