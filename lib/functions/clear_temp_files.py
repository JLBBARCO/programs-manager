import subprocess
from lib import log, system


def clear_temp_files():
    log.info('Clearing temporary files...')
    try:
        if system.name() == 'Windows':
            subprocess.run('del /q/f/s %TEMP%\\*', shell=True, check=True)
        elif system.name() in ['Linux', 'Darwin']:
            subprocess.run('rm -rf /tmp/*', shell=True, check=True)
        log.info('Temporary files cleared successfully.')
    except Exception as e:
        log.error(f"An error occurred while clearing temporary files: {e}")

