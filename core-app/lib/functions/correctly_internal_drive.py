import os
import platform
import subprocess
import glob
from lib.log import info, warning, error


def correctly_internal_drive():
    """Detect whether the system/root drive is an internal (fixed) drive.

    Returns True when detected as internal/fixed, False otherwise.
    Uses Windows API on Windows, `/sys/block` heuristics on Linux.
    """
    try:
        system = platform.system()
        if system == "Windows":
            # Prefer SystemDrive env (e.g. 'C:')
            system_drive = os.environ.get("SystemDrive") or os.path.splitdrive(os.path.abspath(os.sep))[0]
            if not system_drive:
                warning("Could not determine system drive on Windows.")
                return False
            # Ensure root path like 'C:\\' for GetDriveTypeW
            root = system_drive.rstrip('\\/') + "\\\\"
            try:
                GetDriveTypeW = __import__('ctypes').windll.kernel32.GetDriveTypeW
                drive_type = GetDriveTypeW(root)
                DRIVE_FIXED = 3
                if drive_type == DRIVE_FIXED:
                    info("Internal drive is correctly detected (fixed drive).")
                    return True
                else:
                    warning(f"Internal drive is not correctly detected (drive type {drive_type}).")
                    return False
            except Exception as e:
                error(f"Windows drive-type detection failed: {e}")
                return False

        elif system == "Linux":
            # Heuristic: check /sys/block/*/removable == 0 for non-removable devices
            try:
                for block in glob.glob('/sys/block/*'):
                    try:
                        with open(os.path.join(block, 'removable'), 'r') as f:
                            val = f.read().strip()
                        if val == '0':
                            info("Internal drive is correctly detected (Linux, non-removable block found).")
                            return True
                    except Exception:
                        continue
                warning("Internal drive is not correctly detected (Linux heuristics).")
                return False
            except Exception as e:
                error(f"Linux drive detection failed: {e}")
                return False

        else:
            warning(f"Unsupported platform for internal drive detection: {system}")
            return False

    except Exception as e:
        error(f"An error occurred while detecting internal drive: {e}")
        return False

