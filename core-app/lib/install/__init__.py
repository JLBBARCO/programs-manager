import subprocess
from time import sleep
from lib import log, web


def install(data, system):
    for item in data:
        try:
            web.wait_for_internet_connection()
            if system == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                subprocess.run(["winget", "install", "--id", item['id'], "-e", "--accept-source-agreements", "--accept-package-agreements",], shell=True, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elif system == 'Linux':
                subprocess.run(["sudo", "apt", "install", "-y", item['id']], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elif system == 'MacOS':
                subprocess.run(["brew", "install", item['id']], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log.info(f"Installed {item['name']} successfully.")
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to install {item['name']}: {e}")

        for _ in range(10):
            web.wait_for_internet_connection()
            sleep(0.1)

