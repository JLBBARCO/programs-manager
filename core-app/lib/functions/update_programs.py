from lib import system
import subprocess

system_name = system.name()


if system_name == "Windows":
    subprocess.run(["powershell", "-Command", "winget upgrade --all -e --accept-source-agreements --accept-package-agreements --include-unknown"], shell=True)
elif system_name == "Linux":
    subprocess.run(["sudo", "apt", "update"], shell=True)
    subprocess.run(["sudo", "apt", "upgrade", "-y"], shell=True)
