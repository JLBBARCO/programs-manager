import importlib
import re
import subprocess
from pathlib import Path
from time import sleep

from lib import log, system
from . import bios_shortcut, clear_temp_files, correctly_internal_drive, dark_mode, essential_programs_initialization, notifications, video_drivers, vision_cursor_black, rainmeter
from .essential_programs_initialization import (
    disable_startup_programs,
    enable_startup_whitelist,
    essentials_programs_whitelist,
    save_startup_keys,
)

STARTUP_MODULE_FOR_FUNCTION = {
    'disable_startup_programs': 'essential_programs_initialization',
    'enable_startup_whitelist': 'essential_programs_initialization',
    'save_startup_keys': 'essential_programs_initialization',
    'essentials_programs_whitelist': 'essential_programs_initialization',
}


def _filter_install_output(output: str) -> str:
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    clean = ansi_escape.sub('', output)
    lines = clean.splitlines()
    kept_lines = []
    removed_count = 0
    progress_re = re.compile(r'\b\d{1,3}%\b')

    for line in lines:
        if progress_re.search(line) and len(line.strip()) < 120:
            removed_count += 1
            continue
        if len(line.strip()) > 0 and set(line.strip()) <= set('.-') and len(line.strip()) < 40:
            removed_count += 1
            continue
        kept_lines.append(line)

    if removed_count:
        kept_lines.append(f"[{removed_count} progress updates suppressed]")

    return "\n".join(kept_lines).strip()


def _restart_windows_explorer() -> None:
    if system.name() != 'Windows':
        return

    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"],
            capture_output=True,
            text=True,
            shell=False,
        )
    except Exception:
        pass

    try:
        subprocess.Popen(
            ["explorer.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
        log.info('Windows Explorer restarted to apply system changes.')
    except Exception as error:
        log.error(f'Failed to restart Windows Explorer: {error}')


def _resolve_function(func_name: str):
    module_name = STARTUP_MODULE_FOR_FUNCTION.get(func_name, func_name)

    try:
        module = globals().get(module_name)
        if module is None:
            module = importlib.import_module(f'.{module_name}', package=__package__)

        if hasattr(module, func_name):
            return getattr(module, func_name)

        if hasattr(module, 'run'):
            return getattr(module, 'run')

        return None
    except ImportError as error:
        log.warning(f"Não foi possível importar o módulo {module_name}: {error}")
        return None


def functions(functions_list):
    try:
        for item in functions_list:
            func_name = item.get('id') if isinstance(item, dict) else item
            if not func_name:
                continue

            display_name = item.get('name', func_name) if isinstance(item, dict) else func_name
            func = _resolve_function(func_name)

            if callable(func):
                log.info(f"Executando: {display_name}")
                func()
            else:
                log.warning(f"Function not found or not callable: {display_name} ({func_name})")

            sleep(1)

        _restart_windows_explorer()
    except Exception as error:
        log.error(f"Error executing functions: {error}")

