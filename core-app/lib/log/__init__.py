import datetime
import threading

from lib.config import is_developer_mode

_log_file = open("log.log", 'a+', encoding='utf-8')
_lock = threading.Lock()

# Only these levels are persisted to historic.json, matching the same
# typing already used in log.log (INFO, WARNING, ERROR). DEBUG messages
# stay in log.log only.
_HISTORIC_LEVELS = {'INFO', 'WARNING', 'ERROR'}


def _now():
    return datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def log(message, level="INFO"):
    if not is_developer_mode():
        return
    now = _now()
    level = str(level).strip().upper()

    with _lock:
        _log_file.write(f'[{now}] [{level}] {message}\n')
        _log_file.flush()


def log_print(message, level="INFO"):
    now = _now()
    level = str(level).strip().upper()

    with _lock:
        if is_developer_mode():
            print(f'[{now}] [{level}] {message}')

        _log_file.write(f'[{now}] [{level}] {message}\n')
        _log_file.flush()


def info(message):
    log(message, 'INFO')
    log_print(message, 'INFO')


def debug(message):
    log(message, 'DEBUG')
    log_print(message, 'DEBUG')


def warning(message):
    log(message, 'WARNING')
    log_print(message, 'WARNING')


def error(message):
    log(message, 'ERROR')
    log_print(message, 'ERROR')


# initial separator for new run
with _lock:
    _log_file.write('\n')
    _log_file.flush()
