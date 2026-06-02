#!/usr/bin/env python3
"""
Validator script to check if shortcuts were created correctly on first run.
Supports Windows (Start Menu + Desktop), Linux (.desktop files), and macOS (.command files).
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def validate_windows_shortcuts():
    """Validate Windows Start Menu and Desktop shortcuts."""
    from src.lib.windows_shortcuts import (
        windows_start_menu_directories,
        windows_desktop_directories,
    )

    errors = []
    found_shortcuts = []

    try:
        start_menu_dirs = windows_start_menu_directories()
    except Exception as error:
        errors.append(f"Failed to get Start Menu directories: {error}")
        return found_shortcuts, errors

    for start_menu_dir in start_menu_dirs:
        start_menu_shortcut = start_menu_dir / "Passwords Manager.lnk"
        if start_menu_shortcut.exists():
            found_shortcuts.append(str(start_menu_shortcut))
        else:
            errors.append(f"Start Menu shortcut not found: {start_menu_shortcut}")

    for desktop_dir in windows_desktop_directories():
        desktop_shortcut = desktop_dir / "Passwords Manager.lnk"
        if desktop_shortcut.exists():
            found_shortcuts.append(str(desktop_shortcut))
        else:
            errors.append(f"Desktop shortcut not found: {desktop_shortcut}")

    return found_shortcuts, errors


def validate_linux_shortcuts():
    """Validate Linux .desktop files."""
    app_dir = Path.home() / ".local" / "share" / "applications"
    app_entry = app_dir / "passwords-manager.desktop"

    errors = []
    found_shortcuts = []

    if not app_dir.exists():
        errors.append(f"Applications directory not found: {app_dir}")
        return found_shortcuts, errors

    if app_entry.exists():
        found_shortcuts.append(str(app_entry))

        try:
            content = app_entry.read_text(encoding="utf-8")
            if "passwords-manager" in content:
                found_shortcuts.append(f"{app_entry} (verified: contains executable reference)")
            else:
                errors.append(f"Desktop entry missing executable reference: {app_entry}")
        except Exception as error:
            errors.append(f"Failed to read desktop entry: {app_entry}: {error}")
    else:
        errors.append(f"Desktop entry not found: {app_entry}")

    return found_shortcuts, errors


def validate_macos_shortcuts():
    """Validate macOS .command launcher files."""
    app_dir = Path.home() / "Applications"
    app_launcher = app_dir / "Passwords Manager.command"

    errors = []
    found_shortcuts = []

    if not app_dir.exists():
        errors.append(f"Applications directory not found: {app_dir}")
        return found_shortcuts, errors

    if app_launcher.exists():
        found_shortcuts.append(str(app_launcher))

        try:
            content = app_launcher.read_text(encoding="utf-8")
            if "passwords-manager" in content:
                found_shortcuts.append(f"{app_launcher} (verified: contains executable reference)")
            else:
                errors.append(f"Launcher missing executable reference: {app_launcher}")

            if os.access(app_launcher, os.X_OK):
                found_shortcuts.append(f"{app_launcher} (verified: executable permission set)")
            else:
                errors.append(f"Launcher missing executable permission: {app_launcher}")
        except Exception as error:
            errors.append(f"Failed to read launcher: {app_launcher}: {error}")
    else:
        errors.append(f"Launcher not found: {app_launcher}")

    return found_shortcuts, errors


def main():
    """Main validation routine."""
    print("=" * 70)
    print("Passwords Manager - Shortcut Validation")
    print("=" * 70)
    print()

    all_found = []
    all_errors = []

    if os.name == "nt":
        print("Validating Windows shortcuts...")
        found, errors = validate_windows_shortcuts()
        all_found.extend(found)
        all_errors.extend(errors)
    elif sys.platform.startswith("linux"):
        print("Validating Linux shortcuts...")
        found, errors = validate_linux_shortcuts()
        all_found.extend(found)
        all_errors.extend(errors)
    elif sys.platform == "darwin":
        print("Validating macOS shortcuts...")
        found, errors = validate_macos_shortcuts()
        all_found.extend(found)
        all_errors.extend(errors)
    else:
        print(f"Unsupported platform: {sys.platform}")
        return 1

    print()
    if all_found:
        print("[OK] Shortcuts found:")
        for shortcut in all_found:
            print(f"  - {shortcut}")
    else:
        print("[FAIL] No shortcuts found")

    print()
    if all_errors:
        print("[FAIL] Issues detected:")
        for error in all_errors:
            print(f"  - {error}")
        print()
        return 1
    else:
        print("[OK] All shortcuts validated successfully!")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
