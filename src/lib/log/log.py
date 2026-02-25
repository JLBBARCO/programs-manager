from datetime import datetime
import threading
import os
import inspect

_log_file = open('log.log', 'a+', encoding="utf-8")
_lock = threading.Lock()


def _now():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def log(message, level="INFO"):
    """Write a timestamped log entry with level, PID, thread name and caller.

    Usage: log('message', level='ERROR')
    """
    try:
        caller = inspect.stack()[1].function
    except Exception:
        caller = "<unknown>"

    now = _now()
    pid = os.getpid()
    thread_name = threading.current_thread().name

    with _lock:
        _log_file.write(f'[{now}] [{level}] [pid:{pid}] [thread:{thread_name}] [caller:{caller}] {message}\n')
        _log_file.flush()


# initial separator for new run
with _lock:
    _log_file.write('\n')
    _log_file.flush()