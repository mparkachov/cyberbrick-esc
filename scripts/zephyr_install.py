#!/usr/bin/env python3
"""Install the local Zephyr workspace used by the just recipes."""

from __future__ import annotations

import glob
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
STABLE_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def run(args: list[str], *, cwd: Path = PROJECT_ROOT, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(args))
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        check=True,
        stdout=subprocess.PIPE if capture else None,
    )


def require_commands(commands: list[str]) -> None:
    missing = [command for command in commands if shutil.which(command) is None]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"Missing required command(s): {joined}")


def latest_stable_tag() -> str:
    result = run(
        ["git", "ls-remote", "--tags", "--refs", ZEPHYR_REPO, "v*"],
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

    run(["uv", "pip", "install", "--python", str(VENV_PYTHON), "west"])


def ensure_workspace(tag: str) -> None:
    if not (ZEPHYR_WORKSPACE / ".west").exists():
        ZEPHYR_WORKSPACE.mkdir(exist_ok=True)
        run([str(WEST), "init", "-m", ZEPHYR_REPO, "--mr", tag, str(ZEPHYR_WORKSPACE)])
    else:
        run(["git", "fetch", "--tags", "origin"], cwd=ZEPHYR_BASE)
        run(["git", "checkout", "--detach", tag], cwd=ZEPHYR_BASE)

    run([str(WEST), "update"], cwd=ZEPHYR_WORKSPACE)


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
    accepted_compilers = [
        "riscv64-zephyr-elf-gcc",
        "riscv32-zephyr-elf-gcc",
        "riscv32-esp-elf-gcc",
    ]
    if any(shutil.which(compiler) for compiler in accepted_compilers):
        return

    sdk_env = os.environ.get("ZEPHYR_SDK_INSTALL_DIR")
    if sdk_env and Path(sdk_env).exists():
        return

    sdk_candidates: list[Path] = []
    for pattern in [
        str(Path.home() / "zephyr-sdk-*"),
        "/opt/zephyr-sdk-*",
        "/Applications/zephyr-sdk-*",
    ]:
        sdk_candidates.extend(Path(path) for path in glob.glob(pattern))

    if any(candidate.exists() for candidate in sdk_candidates):
        return

    raise SystemExit(
        "ESP32-C3 RISC-V toolchain was not found. Install the Zephyr SDK, "
        "set ZEPHYR_SDK_INSTALL_DIR, or provide an ESP32-C3-compatible "
        "RISC-V compiler on PATH."
    )


def main() -> int:
    os.environ.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")
    os.environ.setdefault("UV_CACHE_DIR", str(PROJECT_ROOT / ".cache" / "uv"))

    require_commands(["python3", "uv", "git", "cmake", "ninja", "dtc", "screen"])
    ensure_venv()

    tag = latest_stable_tag()
    print(f"Using Zephyr {tag}")
    ensure_workspace(tag)
    install_python_requirements()
    verify_esp32c3_toolchain()

    print("Zephyr workspace is ready.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
