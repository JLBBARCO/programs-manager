from pathlib import Path
import os


def windows_start_menu_directories() -> list[Path]:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return []
    return [Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"]


def windows_desktop_directories() -> list[Path]:
    userprofile = os.environ.get("USERPROFILE")
    if not userprofile:
        return []
    return [Path(userprofile) / "Desktop"]