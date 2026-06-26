import re
import subprocess
import winreg
from time import sleep
import urllib.request
import json as std_json

from lib import json, log, system


REG_PATHS = {
    "HKEY_CURRENT_USER": (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    "HKEY_LOCAL_MACHINE (32-bit)": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    "HKEY_LOCAL_MACHINE (64-bit/WOW64)": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
}
APPROVED_PATHS = {
    "HKEY_CURRENT_USER": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKEY_LOCAL_MACHINE (32-bit)": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKEY_LOCAL_MACHINE (64-bit/WOW64)": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32",
}
LEGACY_WHITELIST_TERMS = {
    'microsoftonedrive': {'onedrive'},
    'microsoftedgeautolaunch': {'msedge'},
    'microsoftpcmanager': {'microsoftpcmanager'},
    'nvidiageforceexperience': {'nvidia'},
    'nvcontainer': {'nvidia'},
    'nvbackend': {'nvidia'},
    'nvinitialize': {'nvidia'},
    'igfxtray': {'intelgraphics'},
    'igfxpers': {'intelgraphics'},
    'igfxhk': {'intelgraphics'},
    'hotkeyscmds': {'intelgraphics'},
    'persistence': {'intelgraphics'},
    'radeonsoftware': {'radeon'},
    'livelywpf': {'lively'},
    'camostudio': {'camo'},
}


def _normalize_startup_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _load_whitelist_terms(whitelist_content=None):
    """Parse whitelist content and return a set of normalized terms."""
    # If no whitelist content provided, attempt to fetch from the canonical GitHub raw URL
    remote_url = (
        "https://raw.githubusercontent.com/JLBBARCO/programs-manager/refs/heads/main/system/windows/json/initialization_whitelist.json"
    )
    if whitelist_content is None:
        try:
            with urllib.request.urlopen(remote_url, timeout=5) as resp:
                if getattr(resp, 'status', 200) == 200:
                    body = resp.read().decode('utf-8')
                    try:
                        whitelist_content = std_json.loads(body)
                        log.info("Loaded initialization whitelist from remote URL.")
                    except Exception:
                        whitelist_content = None
        except Exception:
            whitelist_content = None

    if whitelist_content is None:
        whitelist_content = json.read_external_json('initialization_whitelist')

    if not whitelist_content:
        return set()

    if isinstance(whitelist_content, dict):
        entries = (
            whitelist_content.get('data')
            or whitelist_content.get('whitelist')
            or whitelist_content.get('items')
            or []
        )
    elif isinstance(whitelist_content, (list, tuple, set)):
        entries = whitelist_content
    else:
        entries = str(whitelist_content).splitlines()

    whitelist = set()
    for raw_line in entries:
        line = str(raw_line).strip()
        if not line or line.startswith('#'):
            continue

        normalized = _normalize_startup_name(line)
        if not normalized:
            continue

        whitelist.add(normalized)
        whitelist.update(LEGACY_WHITELIST_TERMS.get(normalized, set()))

    return whitelist


def _is_whitelisted(entry_name: str, whitelist_terms) -> bool:
    return _normalize_startup_name(entry_name) in whitelist_terms


def disable_startup_programs():
    """Disable startup entries that are not present in the GitHub whitelist."""
    try:
        whitelist_terms = _load_whitelist_terms()
    except Exception as error:
        return f"Startup disable aborted. Failed to load initialization whitelist: {error}"

    if not whitelist_terms:
        return "Startup disable aborted. Whitelist is empty."

    disabled_count = 0
    preserved_count = 0
    disabled_value = b'\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    for label, (root, path) in REG_PATHS.items():
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as run_key:
                entry_names = []
                index = 0
                while True:
                    try:
                        name, _, _ = winreg.EnumValue(run_key, index)
                        entry_names.append(name)
                        index += 1
                    except OSError:
                        break

                app_root = winreg.HKEY_CURRENT_USER if "HKCU" in label else winreg.HKEY_LOCAL_MACHINE
                app_path = APPROVED_PATHS[label]

                with winreg.CreateKey(app_root, app_path) as approved_key:
                    for name in entry_names:
                        if _is_whitelisted(name, whitelist_terms):
                            preserved_count += 1
                            log.info(f'Preserved startup entry [{label}]: {name}')
                            continue

                        winreg.SetValueEx(approved_key, name, 0, winreg.REG_BINARY, disabled_value)
                        log.info(f'Disabled startup entry [{label}]: {name}')
                        disabled_count += 1
        except Exception as error:
            log.error(f"Skipping {label}, key not found or inaccessible: {error}")

    return (
        f"Scan complete. {disabled_count} startup entries were disabled and "
        f"{preserved_count} whitelist entries were preserved."
    )


def save_startup_keys():
    """Save the current startup registry state for audit/debugging."""
    from lib import find_folders
    output_path = find_folders.get_ProgramsManager_folder() / 'programs.log'

    try:
        lines = []
        for label, (root, path) in REG_PATHS.items():
            try:
                with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
                    count = winreg.QueryInfoKey(key)[1]
                    for index in range(count):
                        name, value, _ = winreg.EnumValue(key, index)
                        lines.append(f"{label}::{name}::{value}")
            except Exception:
                lines.append(f"{label}::(inaccessible)")

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write("\n".join(lines))
        log.info(f"Startup keys saved to {output_path}.")
    except Exception as error:
        log.error(f"Error saving keys: {error}")


def enable_startup_whitelist():
    """Re-enable whitelisted startup entries from GitHub."""
    try:
        whitelist_terms = _load_whitelist_terms()
    except Exception as error:
        log.error(f"Whitelist re-enable failed. Error: {error}")

    if not whitelist_terms:
        return "Whitelist is empty; nothing to re-enable."

    activated_count = 0
    enabled_value = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    for label, (root, path) in REG_PATHS.items():
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as run_key:
                app_root = winreg.HKEY_CURRENT_USER if "HKCU" in label else winreg.HKEY_LOCAL_MACHINE
                app_path = APPROVED_PATHS[label]

                with winreg.CreateKey(app_root, app_path) as approved_key:
                    index = 0
                    while True:
                        try:
                            name, _, _ = winreg.EnumValue(run_key, index)
                            if _is_whitelisted(name, whitelist_terms):
                                winreg.SetValueEx(approved_key, name, 0, winreg.REG_BINARY, enabled_value)
                                log.info(f'Re-enabled from whitelist: {name}')
                                activated_count += 1
                            index += 1
                        except OSError:
                            break
        except Exception:
            continue

    return f"Success: {activated_count} startup entries re-enabled from whitelist."


def essentials_programs_whitelist():
    pass


def essentials_programs_initialization(functions_list):
    try:
        for item in functions_list:
            func_name = item.get('id') if isinstance(item, dict) else item
            if not func_name:
                continue

            display_name = item.get('name', func_name) if isinstance(item, dict) else func_name

            if func_name == 'disable_startup_programs':
                log.info(f"Executing: {display_name}")
                disable_startup_programs()
            elif func_name == 'enable_startup_whitelist':
                log.info(f"Executing: {display_name}")
                enable_startup_whitelist()
            elif func_name == 'save_startup_keys':
                log.info(f"Executing: {display_name}")
                save_startup_keys()
            elif func_name == 'essentials_programs_whitelist':
                log.info(f"Executing: {display_name}")
                essentials_programs_whitelist()
            else:
                log.warning(f"Function not found or not callable: {display_name} ({func_name})")

            sleep(1)

    except Exception as error:
        log.error(f"Error executing functions: {error}")

