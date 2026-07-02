from lib import log


def update_package_manager(nameSO):
    import subprocess
    import os  # Importado para verificar o ambiente com segurança

    from lib import web

    name_so = nameSO

    try:
        web.wait_for_internet_connection()
        if name_so == "Windows":
            # Criando o objeto para ocultar a janela também na atualização do winget
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            # Agora com o 'startupinfo' configurado localmente
            subprocess.run(["winget", "upgrade", "--id", 'Microsoft.AppInstaller', "-e", "--accept-source-agreements", "--accept-package-agreements",], shell=True, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log.info("Package manager updated successfully.")
        elif name_so == "Linux":
            subprocess.run(["sudo", "apt", "update"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log.info("Package manager updated successfully.")
        else:
            log.error(f"Unsupported operating system: {name_so}")
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to update package manager: {e}")

