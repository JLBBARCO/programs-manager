from lib import log


def update_package_manager(nameSO):
    import subprocess

    from lib import web

    name_so = nameSO

    try:
        web.wait_for_internet_connection()
        if name_so == "Windows":
            subprocess.run(["winget", "upgrade", "--id", 'Microsoft.AppInstaller'], check=True)
            log.info("Package manager updated successfully.")
        elif name_so == "Linux":
            subprocess.run(["sudo", "apt", "update"], check=True)
            log.info("Package manager updated successfully.")
        elif name_so == "MacOS":
            subprocess.run(["brew", "update"], check=True)
            log.info("Package manager updated successfully.")
        else:
            log.error(f"Unsupported operating system: {name_so}")
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to update package manager: {e}")
