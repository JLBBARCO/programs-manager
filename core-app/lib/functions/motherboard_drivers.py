import subprocess
import json
import logging

# Módulos do seu projeto
from lib.system import name as CURRENT_OS
from lib.install import install
from lib.execution import run

class MotherboardInstallerModule:
    """
    Módulo para identificar fabricante e modelo da placa-mãe
    e mapear os programas e drivers recomendados para Windows e Linux.
    """

    # --- MAPEAMENTO PARA WINDOWS (WINGET) ---
    WIN_VENDOR_MAP = {
        "ASUSTeK COMPUTER INC.": [
            {"id": "Asus.ArmouryCrate", "log_name": "ASUS Armoury Crate", "desc": "Utilitário e controle ASUS"}
        ],
        "Micro-Star International Co., Ltd.": [
            {"id": "MSI.MSICenter", "log_name": "MSI Center", "desc": "Gerenciador do sistema MSI"}
        ],
        "Gigabyte Technology Co., Ltd.": [
            {"id": "Gigabyte.GIGABYTEControlCenter", "log_name": "GIGABYTE Control Center", "desc": "Controle de hardware Gigabyte"}
        ],
        "Dell Inc.": [
            {"id": "Dell.CommandUpdate", "log_name": "Dell Command Update", "desc": "Atualizador de drivers/BIOS Dell"}
        ],
        "Lenovo": [
            {"id": "Lenovo.SystemUpdate", "log_name": "Lenovo System Update", "desc": "Atualizador de drivers Lenovo"}
        ],
        "HP": [
            {"id": "HP.SupportAssistant", "log_name": "HP Support Assistant", "desc": "Assistente de suporte e drivers HP"}
        ],
        "Acer": [
            {"id": "Acer.CareCenter", "log_name": "Acer Care Center", "desc": "Gerenciador do sistema Acer"}
        ]
    }

    # --- MAPEAMENTO PARA LINUX (APT, DNF, PACMAN, FLATPAK, SNAP) ---
    LINUX_VENDOR_MAP = {
        "ASUSTeK COMPUTER INC.": [
            {"id": "openrgb", "log_name": "OpenRGB", "desc": "Controle de iluminação RGB (Multi-marca)"},
            {"id": "asusctl", "log_name": "ASUS Control", "desc": "Utilitário de controle de energia e perfis ASUS"}
        ],
        "Dell Inc.": [
            {"id": "fwupd", "log_name": "FWUPD", "desc": "Gerenciador de atualizações de Firmware/BIOS no Linux"}
        ],
        "Lenovo": [
            {"id": "fwupd", "log_name": "FWUPD", "desc": "Gerenciador de atualizações de Firmware/BIOS no Linux"}
        ]
    }

    # Softwares de drivers e utilitários genéricos para Linux
    LINUX_GENERIC_APPS = [
        {"id": "fwupd", "log_name": "FWUPD", "desc": "Utilitário de atualização de Firmware e BIOS"},
        {"id": "lm-sensors", "log_name": "LM-Sensors", "desc": "Leitura de temperatura e sensores da placa-mãe"}
    ]

    @staticmethod
    def get_motherboard_info():
        """Detecta a placa-mãe de acordo com o Sistema Operacional retornado por lib.system.name."""
        os_type = CURRENT_OS

        if os_type == "Windows":
            try:
                cmd = 'Get-CimInstance -ClassName Win32_BaseBoard | Select-Object Manufacturer, Product | ConvertTo-Json'
                result = run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)
                data = json.loads(result.stdout)
                return {
                    "manufacturer": data.get("Manufacturer", "Desconhecido").strip(),
                    "model": data.get("Product", "Desconhecido").strip()
                }
            except Exception as e:
                logging.error(f"Erro ao obter placa-mãe no Windows: {e}")

        elif os_type == "Linux":
            try:
                # Método 1: Tenta ler direto dos arquivos sysfs (não requer root)
                try:
                    with open("/sys/class/dmi/id/board_vendor", "r") as f:
                        vendor = f.read().strip()
                    with open("/sys/class/dmi/id/board_name", "r") as f:
                        model = f.read().strip()
                    return {"manufacturer": vendor, "model": model}
                except FileNotFoundError:
                    pass

                # Método 2: Fallback usando o comando hostnamectl
                res = run(["hostnamectl"], capture_output=True, text=True)
                vendor, model = "Desconhecido", "Desconhecido"
                for line in res.stdout.splitlines():
                    if "Hardware Vendor:" in line:
                        vendor = line.split(":", 1)[1].strip()
                    elif "Hardware Model:" in line:
                        model = line.split(":", 1)[1].strip()
                return {"manufacturer": vendor, "model": model}

            except Exception as e:
                logging.error(f"Erro ao obter placa-mãe no Linux: {e}")

        return {"manufacturer": "Desconhecido", "model": "Desconhecido"}

    @classmethod
    def get_recommended_arrays(cls):
        """
        Gera os arrays formatados para a interface gráfica e para a execução.
        Formato do Array: [id_programa, nome_log, marcado_bool, tipo_operacao]
        """
        info = cls.get_motherboard_info()
        manufacturer = info["manufacturer"]
        detected_apps = []
        os_type = CURRENT_OS

        if os_type == "Windows":
            # Processa o mapeamento do Windows
            for vendor, apps in cls.WIN_VENDOR_MAP.items():
                if vendor.lower() in manufacturer.lower():
                    detected_apps.extend(apps)
                    break

            # Drivers/Assistentes genéricos no Windows
            combined_text = (manufacturer + " " + info["model"]).lower()
            if "amd" in combined_text or "ryzen" in combined_text:
                detected_apps.append({"id": "AMD.AutoDetectAndInstall", "log_name": "AMD Software & Driver Auto-Detect", "desc": "Instalador de drivers AMD"})
            else:
                detected_apps.append({"id": "Intel.DriverAndSupportAssistant", "log_name": "Intel Driver & Support Assistant", "desc": "Assistente de drivers Intel"})

        elif os_type == "Linux":
            # Processa o mapeamento de Linux
            for vendor, apps in cls.LINUX_VENDOR_MAP.items():
                if vendor.lower() in manufacturer.lower():
                    detected_apps.extend(apps)
                    break
            
            # Adiciona utilitários genéricos de hardware para Linux
            detected_apps.extend(cls.LINUX_GENERIC_APPS)

        # Monta os arrays no formato consumido pelo seu projeto
        formatted_arrays = []
        for item in detected_apps:
            program_array = [
                item["id"],        # ID para o comando de instalação
                item["log_name"],  # Nome para o arquivo de log
                True,              # Marcar por padrão no checkbox
                "install"          # Operação ("install", "uninstall", etc)
            ]
            formatted_arrays.append((program_array, item["desc"]))

        return info, formatted_arrays

    @classmethod
    def execute_installation(cls, task_array):
        """
        Lê um array individual e envia para a sua função importada `install(data, system)`.
        Estrutura do task_array: [program_id, log_name, is_checked, op_type]
        """
        program_id, log_name, is_checked, op_type = task_array

        if is_checked and op_type == "install":
            logging.info(f"Iniciando instalação de {log_name}...")
            # Executa a função do seu módulo lib.install
            install(data=program_id, system=CURRENT_OS)