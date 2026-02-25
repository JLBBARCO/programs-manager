import winreg
from src.lib import log


def generate_startup_list(output_file="list.txt"):
    # Common startup paths in Registry
    paths = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
    ]

    found_programs = []

    for hkey, path in paths:
        try:
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_READ) as key:
                # Discover how many values exist in the key
                count = winreg.QueryInfoKey(key)[1]
                for i in range(count):
                    name, value, type = winreg.EnumValue(key, i)
                    found_programs.append(name)
        except Exception as e:
            log.log(f"Could not read key {path}: {e}", level="ERROR")

    # Remove duplicates and save to file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for app in sorted(set(found_programs)):
                f.write(f"{app}\n")
        log.log(f"Success! List generated in: {output_file}", level="INFO")
    except Exception as e:
        log.log(f"Failed to write startup list to {output_file}: {e}", level="ERROR")


# Execute the function when run as script
if __name__ == "__main__":
    generate_startup_list()