import subprocess
from time import sleep
from lib.log import info as log_info, warning as log_warning, error as log_error
from lib.web import wait_for_internet_connection
from lib.system import name as system
from lib.execution import run, ExecutionCancelled, is_cancelled


def install(data):
    for item in data:
        if is_cancelled():
            return
        try:
            wait_for_internet_connection()
            version = str(item.get('version', '')).strip()

            if system() == 'Windows':
                startupInfo = subprocess.STARTUPINFO()
                startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupInfo.wShowWindow = subprocess.SW_HIDE

                command = ["winget", "install", "--id", item['id'], "-e", "--accept-source-agreements", "--accept-package-agreements"]
                if version:
                    command.extend(["--version", version])
                    log_info(f"Installing {item['name']} (version {version})...")
                else:
                    log_info(f"Installing {item['name']} (latest version)...")

                run(command, shell=True, startupinfo=startupInfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            elif system() == 'Linux':
                package_target = f"{item['id']}={version}" if version else item['id']
                if version:
                    log_info(f"Installing {item['name']} (version {version})...")
                else:
                    log_info(f"Installing {item['name']} (latest version)...")

                run(["sudo", "apt", "install", "-y", package_target], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            log_info(f"Installed {item['name']} successfully.")
        except ExecutionCancelled:
            return
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to install {item['name']}: {e}")

        for _ in range(10):
            wait_for_internet_connection()
            sleep(0.1)

