import subprocess

from time import sleep
from lib.web import wait_for_internet_connection
from lib.log import info, error
from lib.system import name as system
from lib.execution import run, ExecutionCancelled, is_cancelled


def uninstall(data):
    for item in data:
        if is_cancelled():
            return
        try:
            wait_for_internet_connection()
            if system() == 'Windows':
                startupInfo = subprocess.STARTUPINFO()
                startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupInfo.wShowWindow = subprocess.SW_HIDE
                run(["winget", "uninstall", "--id", item['id'], "-e", "--accept-source-agreements", "--accept-package-agreements",], shell=True, startupinfo=startupInfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elif system() == 'Linux':
                run(["sudo", "apt", "remove", "-y", item['id']], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            info(f"Uninstalled {item['name']} successfully.")
        except ExecutionCancelled:
            return
        except subprocess.CalledProcessError as e:
            error(f"Failed to install {item['name']}: {e}")

        for _ in range(10):
            wait_for_internet_connection()
            sleep(0.1)

