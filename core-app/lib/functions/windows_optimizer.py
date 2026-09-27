import shutil
import subprocess

from lib import log, system


WINDOWS_OPTIMIZER_SCRIPT = (
    'irm https://raw.githubusercontent.com/JLBBARCO/windows-optimizer/main/core-app/run.ps1 | iex'
)


def run() -> bool:
    """Run the Windows Optimizer launcher through PowerShell."""
    if system.name() != 'Windows':
        log.warning('Windows Optimizer can only be run on Windows.')
        return False

    powershell = shutil.which('powershell') or shutil.which('pwsh')
    if not powershell:
        log.error('PowerShell was not found. Windows Optimizer was not started.')
        return False

    log.info('Starting Windows Optimizer through PowerShell...')
    try:
        process = subprocess.run(
            [powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', WINDOWS_OPTIMIZER_SCRIPT],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=False,
            check=False,
        )
    except OSError as error:
        log.error(f'Could not start Windows Optimizer: {error}')
        return False

    output = '\n'.join(part.strip() for part in (process.stdout, process.stderr) if part and part.strip())
    if output:
        for line in output.splitlines():
            log.info(f'[Windows Optimizer] {line}')

    if process.returncode != 0:
        log.error(f'Windows Optimizer exited with code {process.returncode}.')
        return False

    log.info('Windows Optimizer finished successfully.')
    return True
