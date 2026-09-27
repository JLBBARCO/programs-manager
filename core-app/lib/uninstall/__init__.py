import subprocess

from time import sleep
from lib.web import wait_for_internet_connection
from lib.log import info, error
from lib.system import name as system


def uninstall(data):
    for item in data:
        try:
            wait_for_internet_connection()
            if system() == 'Windows':
                startupInfo = subprocess.STARTUPINFO()
                startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupInfo.wShowWindow = subprocess.SW_HIDE
                subprocess.run(["winget", "uninstall", "--id", item['id'], "-e", "--accept-source-agreements", "--accept-package-agreements",], shell=True, startupinfo=startupInfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elif system() == 'Linux':
                subprocess.run(["sudo", "apt", "remove", "-y", item['id']], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            info(f"Uninstalled {item['name']} successfully.")
        except subprocess.CalledProcessError as e:
            error(f"Failed to install {item['name']}: {e}")

        for _ in range(10):
            wait_for_internet_connection()
            sleep(0.1)

