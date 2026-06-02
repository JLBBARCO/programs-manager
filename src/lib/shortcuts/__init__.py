from __future__ import annotations

from pathlib import Path
import os
import shlex
import stat
import subprocess
import sys

from src.lib.windows_shortcuts import (
    windows_desktop_directories,
    windows_start_menu_directories,
)


APP_NAME = "Passwords Manager"
APP_SLUG = "passwords-manager"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _launcher_command() -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable]
    return [sys.executable, str(_project_root() / "main.py")]


def _launcher_text() -> str:
    return " ".join(shlex.quote(part) for part in _launcher_command())


def _windows_powershell_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _create_windows_shortcut(shortcut_path: Path) -> None:
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)
    command = _launcher_command()
    target = command[0]
    arguments = " ".join(command[1:])
    icon_path = _project_root() / "src" / "assets" / "icon" / "icon.ico"
    icon = str(icon_path) if icon_path.exists() else target

    ps_script = (
        "$shell = New-Object -ComObject WScript.Shell; "
        f"$shortcut = $shell.CreateShortcut({_windows_powershell_literal(str(shortcut_path))}); "
        f"$shortcut.TargetPath = {_windows_powershell_literal(target)}; "
        f"$shortcut.Arguments = {_windows_powershell_literal(arguments)}; "
        f"$shortcut.WorkingDirectory = {_windows_powershell_literal(str(_project_root()))}; "
        f"$shortcut.IconLocation = {_windows_powershell_literal(icon)}; "
        "$shortcut.Save();"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        check=True,
        capture_output=True,
        text=True,
    )


def _ensure_windows_shortcuts() -> list[Path]:
    created: list[Path] = []
    for directory in [*windows_start_menu_directories(), *windows_desktop_directories()]:
        shortcut_path = directory / f"{APP_NAME}.lnk"
        _create_windows_shortcut(shortcut_path)
        created.append(shortcut_path)
    return created


def _ensure_linux_shortcut() -> list[Path]:
    app_dir = Path.home() / ".local" / "share" / "applications"
    app_dir.mkdir(parents=True, exist_ok=True)
    shortcut_path = app_dir / f"{APP_SLUG}.desktop"
    content = f"""[Desktop Entry]
Type=Application
Version=1.0
Name={APP_NAME}
Exec={_launcher_text()}
Terminal=false
Categories=Utility;Security;
StartupWMClass={APP_SLUG}
"""
    shortcut_path.write_text(content, encoding="utf-8")
    shortcut_path.chmod(shortcut_path.stat().st_mode | stat.S_IXUSR)
    return [shortcut_path]


def _ensure_macos_shortcut() -> list[Path]:
    app_dir = Path.home() / "Applications"
    app_dir.mkdir(parents=True, exist_ok=True)
    shortcut_path = app_dir / f"{APP_NAME}.command"
    content = f"""#!/bin/bash
# {APP_SLUG}
cd {shlex.quote(str(_project_root()))}
exec {_launcher_text()}
"""
    shortcut_path.write_text(content, encoding="utf-8")
    shortcut_path.chmod(shortcut_path.stat().st_mode | stat.S_IXUSR)
    return [shortcut_path]


def ensure_platform_shortcuts() -> list[Path]:
    if os.name == "nt":
        return _ensure_windows_shortcuts()
    if sys.platform.startswith("linux"):
        return _ensure_linux_shortcut()
    if sys.platform == "darwin":
        return _ensure_macos_shortcut()
    return []


def ensure_platform_shortcuts_best_effort() -> list[Path]:
    try:
        return ensure_platform_shortcuts()
    except Exception:
        return []
