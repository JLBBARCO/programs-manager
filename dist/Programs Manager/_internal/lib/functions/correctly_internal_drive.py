import subprocess
from lib import log


def correctly_internal_drive():
    try:
        # Run the command to check for internal drive
        result = subprocess.run(['cmd', '/c', 'sfc', '/scannow'], capture_output=True, text=True)
        
        # Check if the output contains "Fixed" which indicates an internal drive
        if "Fixed" in result.stdout:
            log.info("Internal drive is correctly detected.")
        else:
            log.warning("Internal drive is not correctly detected.")
    except Exception as e:
        log.error(f"An error occurred: {e}")