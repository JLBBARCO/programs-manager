import subprocess

from time import sleep

from lib import log, web


def uninstall(data, system):
    for item in data:
        try:
            web.wait_for_internet_connection()
            if system == 'Windows':
                subprocess.run(["winget", "uninstall", "--id", item['id']], shell=True, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elif system == 'Linux':
                subprocess.run(["sudo", "apt", "remove", "-y", item['id']], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elif system == 'MacOS':
                subprocess.run(["brew", "uninstall", item['id']], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log.info(f"Uninstalled {item['name']} successfully.")
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to uninstall {item['name']}: {e}")

        for _ in range(10):
            web.wait_for_internet_connection()
            sleep(0.1)

