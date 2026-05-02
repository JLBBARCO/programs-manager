#!/usr/bin/env python3
"""Capture a full-screen screenshot or the active app window and save as WEBP.

Usage: python scripts/ci_screenshot.py output.webp
"""
import os
import subprocess
import sys
import time
import argparse
import shutil

try:
    from mss import MSS
    from PIL import Image
    have_mss = True
except Exception:
    have_mss = False
    print("mss not available; will try PIL.ImageGrab fallback on supported OSes.")
    try:
        from PIL import Image, ImageGrab
    except Exception:
        print("Missing dependencies: please install mss and pillow (PIL.ImageGrab fallback failed).")
        raise


def capture(output_path: str) -> int:
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    if have_mss:
        with MSS() as sct:
            monitor = sct.monitors[0]
            sct_img = sct.grab(monitor)
            img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
            img.save(output_path, 'WEBP', quality=85)
    else:
        try:
            img = ImageGrab.grab()
            img = img.convert('RGB')
            img.save(output_path, 'WEBP', quality=85)
        except Exception as e:
            print(f"ImageGrab fallback failed: {e}")
            raise
    return 0


def _grab_region(output_path: str, bbox: tuple[int, int, int, int]) -> int:
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    if have_mss:
        with MSS() as sct:
            monitor = {
                "left": bbox[0],
                "top": bbox[1],
                "width": max(1, bbox[2] - bbox[0]),
                "height": max(1, bbox[3] - bbox[1]),
            }
            sct_img = sct.grab(monitor)
            img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
            img.save(output_path, 'WEBP', quality=85)
            return 0

    img = ImageGrab.grab(bbox=bbox)
    img = img.convert('RGB')
    img.save(output_path, 'WEBP', quality=85)
    return 0


def _get_foreground_window_bbox_windows():
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return None

    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None

    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None

    return rect.left, rect.top, rect.right, rect.bottom


def _get_window_bbox_windows_by_pid(pid: int, timeout_seconds: float = 12.0):
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return None

    user32 = ctypes.windll.user32
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        window_handles = []

        def enum_windows_callback(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True

            window_pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
            if window_pid.value != pid:
                return True

            rect = wintypes.RECT()
            if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return True

            if rect.right <= rect.left or rect.bottom <= rect.top:
                return True

            title_length = user32.GetWindowTextLengthW(hwnd)
            title = ''
            if title_length > 0:
                buffer = ctypes.create_unicode_buffer(title_length + 1)
                user32.GetWindowTextW(hwnd, buffer, title_length + 1)
                title = buffer.value.strip()

            window_handles.append((rect.left, rect.top, rect.right, rect.bottom, title))
            return True

        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        enum_windows_proc = callback_type(enum_windows_callback)
        if not user32.EnumWindows(enum_windows_proc, 0):
            time.sleep(0.25)
            continue

        preferred_windows = []
        terminal_windows = []
        for left, top, right, bottom, title in window_handles:
            title_lower = title.lower()
            is_terminal_window = any(
                keyword in title_lower
                for keyword in ('powershell', 'cmd', 'terminal', 'windows terminal', 'git bash')
            )
            if is_terminal_window:
                terminal_windows.append((left, top, right, bottom, title))
            else:
                preferred_windows.append((left, top, right, bottom, title))

        chosen_windows = preferred_windows or terminal_windows
        if chosen_windows:
            left, top, right, bottom, _title = chosen_windows[-1]
            if left >= 0 and top >= 0 and right > left and bottom > top:
                return left, top, right, bottom

        time.sleep(0.25)

    return None


def _get_foreground_window_bbox_linux():
    if shutil.which('xdotool') is None or shutil.which('xwininfo') is None:
        return None

    try:
        window_id = subprocess.check_output(['xdotool', 'getwindowfocus'], text=True).strip()
    except Exception:
        return None

    if not window_id:
        return None

    try:
        output = subprocess.check_output(['xwininfo', '-id', window_id], text=True)
    except Exception:
        return None

    left = top = None
    width = height = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('Absolute upper-left X:'):
            left = int(line.split(':', 1)[1].strip())
        elif line.startswith('Absolute upper-left Y:'):
            top = int(line.split(':', 1)[1].strip())
        elif line.startswith('Width:'):
            width = int(line.split(':', 1)[1].strip())
        elif line.startswith('Height:'):
            height = int(line.split(':', 1)[1].strip())

    if None in (left, top, width, height):
        return None

    return left, top, left + width, top + height


def _get_window_bbox_linux_by_pid(pid: int, timeout_seconds: float = 12.0):
    if shutil.which('xdotool') is None or shutil.which('xwininfo') is None:
        return None

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            window_ids = subprocess.check_output(['xdotool', 'search', '--pid', str(pid)], text=True).splitlines()
        except Exception:
            window_ids = []

        for window_id in reversed([window_id.strip() for window_id in window_ids if window_id.strip()]):
            try:
                output = subprocess.check_output(['xwininfo', '-id', window_id], text=True)
            except Exception:
                continue

            left = top = None
            width = height = None
            for line in output.splitlines():
                line = line.strip()
                if line.startswith('Absolute upper-left X:'):
                    left = int(line.split(':', 1)[1].strip())
                elif line.startswith('Absolute upper-left Y:'):
                    top = int(line.split(':', 1)[1].strip())
                elif line.startswith('Width:'):
                    width = int(line.split(':', 1)[1].strip())
                elif line.startswith('Height:'):
                    height = int(line.split(':', 1)[1].strip())

            if None not in (left, top, width, height):
                return left, top, left + width, top + height

        time.sleep(0.25)

    return None


def _get_window_bbox_macos_by_pid(pid: int, timeout_seconds: float = 12.0):
    """Get window bounds for a process on macOS using lsof and osascript."""
    if shutil.which('lsof') is None:
        return None

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            # Get the application name from process ID
            result = subprocess.check_output(['ps', '-p', str(pid), '-o', 'comm='], text=True).strip()
            if not result:
                time.sleep(0.25)
                continue
            
            app_name = result.split('/')[-1]  # Get just the executable name
            
            # Try to get window bounds using osascript
            applescript = f'''
tell application "System Events"
    set procs to (every application process whose name contains "{app_name}")
    if (count of procs) is 0 then return ""
    set frontProc to item 1 of procs
    if (count of windows of frontProc) is 0 then return ""
    set win to front window of frontProc
    set {{x, y}} to position of win
    set {{w, h}} to size of win
    return (x as text) & "," & (y as text) & "," & ((x + w) as text) & "," & ((y + h) as text)
end tell
'''
            output = subprocess.check_output(['osascript', '-e', applescript], text=True).strip()
            
            if output and output != '':
                try:
                    left, top, right, bottom = (int(value) for value in output.split(','))
                    if left >= 0 and top >= 0 and right > left and bottom > top:
                        return left, top, right, bottom
                except Exception:
                    pass
        
        except Exception:
            pass
        
        time.sleep(0.25)

    return None


def _get_foreground_window_bbox_macos():
    applescript = r'''
tell application "System Events"
    set frontProc to first application process whose frontmost is true
    if (count of windows of frontProc) is 0 then return ""
    set win to front window of frontProc
    set {x, y} to position of win
    set {w, h} to size of win
    return (x as text) & "," & (y as text) & "," & ((x + w) as text) & "," & ((y + h) as text)
end tell
'''
    try:
        result = subprocess.check_output(['osascript', '-e', applescript], text=True).strip()
    except Exception:
        return None

    if not result:
        return None

    try:
        left, top, right, bottom = (int(value) for value in result.split(','))
    except Exception:
        return None

    return left, top, right, bottom


def capture_active_window(output_path: str) -> int:
    if sys.platform.startswith('win'):
        bbox = _get_foreground_window_bbox_windows()
    elif sys.platform == 'darwin':
        bbox = _get_foreground_window_bbox_macos()
    else:
        bbox = _get_foreground_window_bbox_linux()

    if bbox is None:
        print("Warning: Unable to determine the active window bounds; falling back to full-screen capture")
        return capture(output_path)

    return _grab_region(output_path, bbox)


def launch_and_capture(output_path: str, launch_command: list[str], wait_seconds: float) -> int:
    process = subprocess.Popen(launch_command)
    try:
        if sys.platform.startswith('win'):
            bbox = _get_window_bbox_windows_by_pid(process.pid, timeout_seconds=max(wait_seconds, 1.0) + 6.0)
            if bbox is None:
                time.sleep(wait_seconds)
                bbox = _get_foreground_window_bbox_windows()
            if bbox is None:
                print("Warning: Unable to locate app window by PID on Windows; falling back to full-screen capture")
                return capture(output_path)
            return _grab_region(output_path, bbox)

        elif sys.platform == 'darwin':
            # macOS: try PID-based capture first, then active window, then full-screen fallback
            bbox = _get_window_bbox_macos_by_pid(process.pid, timeout_seconds=max(wait_seconds, 1.0) + 6.0)
            if bbox is None:
                # If PID-based fails, try active window
                time.sleep(wait_seconds)
                return capture_active_window(output_path)
            return _grab_region(output_path, bbox)

        else:  # Linux
            bbox = _get_window_bbox_linux_by_pid(process.pid, timeout_seconds=max(wait_seconds, 1.0) + 6.0)
            if bbox is None:
                time.sleep(wait_seconds)
                bbox = _get_foreground_window_bbox_linux()
            if bbox is None:
                print("Warning: Unable to locate app window by PID on Linux; falling back to full-screen capture")
                return capture(output_path)
            return _grab_region(output_path, bbox)
    finally:
        try:
            process.terminate()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("output")
    parser.add_argument("--wait-seconds", type=float, default=6.0)
    parser.add_argument("--launch", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    launch_command = args.launch or None
    if launch_command == ["--"]:
        launch_command = []

    if launch_command is not None and not launch_command:
        print("--launch requires at least one command argument")
        return 2

    try:
        if launch_command is None:
            return capture(args.output)
        return launch_and_capture(args.output, launch_command, args.wait_seconds)
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
