import subprocess
import threading
import time


class ExecutionCancelled(Exception):
    pass


_cancel_event = threading.Event()
_active_process = None
_process_lock = threading.Lock()


def is_cancelled() -> bool:
    return _cancel_event.is_set()


def cancel_all() -> None:
    _cancel_event.set()
    with _process_lock:
        process = _active_process
    if process and process.poll() is None:
        try:
            process.terminate()
        except OSError:
            pass


def run(command, **kwargs):
    if is_cancelled():
        raise ExecutionCancelled()

    check = kwargs.pop('check', False)
    popen_kwargs = dict(kwargs)
    if popen_kwargs.pop('capture_output', False):
        popen_kwargs.setdefault('stdout', subprocess.PIPE)
        popen_kwargs.setdefault('stderr', subprocess.PIPE)

    process = subprocess.Popen(command, **popen_kwargs)
    global _active_process
    with _process_lock:
        _active_process = process

    try:
        while process.poll() is None:
            if is_cancelled():
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                raise ExecutionCancelled()
            time.sleep(0.1)

        stdout, stderr = process.communicate()
        if is_cancelled():
            raise ExecutionCancelled()
        result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        if check and process.returncode:
            raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)
        return result
    finally:
        with _process_lock:
            if _active_process is process:
                _active_process = None