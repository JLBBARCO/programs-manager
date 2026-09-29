import subprocess

from lib.log import info, warning, error as log_error
from lib.system import name as system_name
from lib.execution import run


def _run_command(command: str) -> str:
	process = run(command, capture_output=True, text=True, shell=True)
	raw_output = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")
	return raw_output.strip()


def dark_mode():
	if system_name() == 'Windows':
		try:
			_run_command(
				'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
				'/v AppsUseLightTheme /t REG_DWORD /d 0 /f >nul 2>&1'
			)
			_run_command(
				'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
				'/v SystemUsesLightTheme /t REG_DWORD /d 0 /f >nul 2>&1'
			)
			info('Dark mode applied successfully.')
		except Exception as error:
			log_error(f'Failed to apply dark mode: {error}')
