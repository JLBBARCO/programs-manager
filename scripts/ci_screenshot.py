#!/usr/bin/env python3
"""Capture a full-screen screenshot and save as WEBP.

Usage: python scripts/ci_screenshot.py output.webp
"""
import os
import sys

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


def main():
    if len(sys.argv) < 2:
        print("Usage: ci_screenshot.py OUTPUT_PATH")
        return 2
    output = sys.argv[1]
    try:
        return capture(output)
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
