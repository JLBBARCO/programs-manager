import subprocess
from time import sleep
from lib import log, web


def install(data, system):
    for item in data:
        try:
            web.wait_for_internet_connection()
            version = str(item.get('version', '')).strip()

            if system == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                command = ["winget", "install", "--id", item['id'], "-e", "--accept-source-agreements", "--accept-package-agreements"]
                if version:
                    command.extend(["--version", version])
                    log.info(f"Installing {item['name']} (version {version})...")
                else:
                    log.info(f"Installing {item['name']} (latest version)...")

                subprocess.run(command, shell=True, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            elif system == 'Linux':
                package_target = f"{item['id']}={version}" if version else item['id']
                if version:
                    log.info(f"Installing {item['name']} (version {version})...")
                else:
                    log.info(f"Installing {item['name']} (latest version)...")

                subprocess.run(["sudo", "apt", "install", "-y", package_target], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            log.info(f"Installed {item['name']} successfully.")
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to install {item['name']}: {e}")

        for _ in range(10):
            web.wait_for_internet_connection()
            sleep(0.1)

