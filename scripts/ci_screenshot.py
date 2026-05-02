#!/usr/bin/env python3
"""Capture a full-screen screenshot and save as WEBP.

Usage: python scripts/ci_screenshot.py output.webp
"""
import os
import subprocess
import sys
import time
import argparse

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


def launch_and_capture(output_path: str, launch_command: list[str], wait_seconds: float) -> int:
    process = subprocess.Popen(launch_command)
    try:
        time.sleep(wait_seconds)
        return capture(output_path)
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
