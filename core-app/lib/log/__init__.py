import datetime
import json
import threading

from lib.find_folders import get_ProgramsManager_folder


_log_file_path = get_ProgramsManager_folder() / 'log.log'
_log_file = open(_log_file_path, 'a+', encoding='utf-8')
_historic_file_path = get_ProgramsManager_folder() / 'historic.json'
_lock = threading.Lock()

# Only these levels are persisted to historic.json, matching the same
# typing already used in log.log (INFO, WARNING, ERROR). DEBUG messages
# stay in log.log only.
_HISTORIC_LEVELS = {'INFO', 'WARNING', 'ERROR'}


def _now():
    return datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def get_log_file_path():
    return _log_file_path


def get_historic_file_path():
    return _historic_file_path


def _load_historic_entries() -> list[dict[str, str]]:
    if not _historic_file_path.exists():
        return []

    try:
        with open(_historic_file_path, 'r', encoding='utf-8') as historic_file:
            content = historic_file.read().strip()
    except Exception:
        return []

    if not content:
        return []

    try:
        data = json.loads(content)
    except Exception:
        return []

    if isinstance(data, dict):
        data = data.get('data', [])

    return data if isinstance(data, list) else []


# Historic entries are cached in memory after the initial load to avoid
# re-reading the file from disk on every single log call.
_historic_entries: list[dict[str, str]] = _load_historic_entries()


def _write_historic_entries() -> None:
    try:
        with open(_historic_file_path, 'w', encoding='utf-8') as historic_file:
            json.dump(_historic_entries, historic_file, indent=2, ensure_ascii=False)
            historic_file.flush()
    except Exception:
        pass


def _append_historic_entry(message: str, level: str, now: str) -> None:
    if level not in _HISTORIC_LEVELS:
        return

    _historic_entries.append({
        'timestamp': now,
        'level': level,
        'message': message,
    })
    _write_historic_entries()


def log(message, level="INFO"):
    now = _now()
    level = str(level).strip().upper()

    with _lock:
        _log_file.write(f'[{now}] [{level}] {message}\n')
        _log_file.flush()
        _append_historic_entry(message, level, now)


def info(message):
    log(message, 'INFO')


def debug(message):
    log(message, 'DEBUG')


def warning(message):
    log(message, 'WARNING')


def error(message):
    log(message, 'ERROR')


# initial separator for new run
with _lock:
    _log_file.write('\n')
    _log_file.flush()
