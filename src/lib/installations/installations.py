import subprocess
import os
import re
from src.lib import log

def install_program(program):
    # Build path to the .bat in a cross-platform way and run it with shell=True
    bat_path = os.path.join('install', f"{program}.bat")
    log.log(f'Running installer: {bat_path}', level="INFO")
    process = subprocess.run(bat_path, capture_output=True, text=True, shell=True)
    # Combine stdout and stderr
    raw_output = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")

    # Filter out progress-like lines (e.g., repeated percent updates, ANSI escapes)
    def _filter_install_output(output: str) -> str:
        # remove ANSI escape sequences
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        clean = ansi_escape.sub('', output)
        lines = clean.splitlines()
        kept_lines = []
        removed_count = 0
        progress_re = re.compile(r'\b\d{1,3}%\b')

        for line in lines:
            # skip lines that are simple progress indicators like '12%' or '12% downloaded'
            if progress_re.search(line) and len(line.strip()) < 120:
                removed_count += 1
                continue
            # skip very short lines with only dots or dashes that are likely progress markers
            if len(line.strip()) > 0 and set(line.strip()) <= set('.-') and len(line.strip()) < 40:
                removed_count += 1
                continue
            kept_lines.append(line)

        if removed_count:
            kept_lines.append(f"[{removed_count} progress updates suppressed]")

        return "\n".join(kept_lines).strip()

    filtered_output = _filter_install_output(raw_output)

    if process.returncode != 0:
        log.log(f'Installer {bat_path} returned code {process.returncode}', level="ERROR")
        log.log(filtered_output or f"(raw output suppressed; {len(raw_output)} bytes)", level="ERROR")
    else:
        log.log(f'Installer {bat_path} completed successfully', level="INFO")
        log.log(filtered_output or "(no meaningful output)", level="INFO")

    return filtered_output

def essentials():
    return install_program("essentials")

def office():
    import shutil
    destinationPath = r"C:\office"
    files = ['install/office/setup.exe', 'install/office/settings.xml']

    os.makedirs(destinationPath, exist_ok=True)
    messages = []
    for file in files:
        try:
            shutil.copy(file, destinationPath)
            messages.append(f"Successfully copied {file} to {destinationPath}")
        except Exception as error:
            messages.append(f"Failed to copy {file} to {destinationPath}. Error: {error}")
    
    result = install_program("office")
    messages.append(result)
    return "\n".join(messages)

def development():
    return install_program("development")

def games():
    return install_program("games")

def customization():
    import src.lib.customizations as custom
    log.log('Starting customization flow', level="INFO")

    # 1) Run customization installers
    installProgramsMessage = install_program("customization")
    log.log('Customization installers output captured', level="INFO")

    # 2) Disable all startup programs
    disableStartupMessage = custom.disable_startup_programs()
    log.log(f'Disable startup: {disableStartupMessage}', level="INFO")

    # 3) Save current startup keys to programs.log (overwrite)
    saveKeysMessage = custom.save_startup_keys('programs.log')
    log.log(saveKeysMessage, level="INFO")

    # 4) Reactivate entries that are in the whitelist
    # prefer 'install/white_list.txt' if present, otherwise try 'white_list.txt'
    whitelist_path = 'install/white_list.txt' if os.path.exists(os.path.join('install','white_list.txt')) else 'white_list.txt'
    enableStartupMessage = custom.enable_startup_whitelist(whitelist_path)
    log.log(enableStartupMessage, level="INFO")

    # 5) Apply dark mode and restart explorer to apply visual changes
    darkModeMessage = custom.dark_mode()
    log.log(darkModeMessage, level="INFO")
    os.system("taskkill /f /im explorer.exe")
    os.system("start explorer.exe")

    log.log('Customization flow completed', level="INFO")
    return f"{installProgramsMessage}\n{disableStartupMessage}\n{saveKeysMessage}\n{enableStartupMessage}\n{darkModeMessage}"