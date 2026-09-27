import os
import subprocess
from pathlib import Path

from lib.log import error, info


def bios_shortcut():
	from lib.find_folders import get_StartMenu_Programs_folder

	try:
		shortcut_directories = [get_StartMenu_Programs_folder()]
		user_profile = os.environ.get('USERPROFILE')
		if user_profile:
			shortcut_directories.append(Path(user_profile) / 'Desktop')

		for directory in shortcut_directories:
			directory.mkdir(parents=True, exist_ok=True)
			shortcut_path = directory / 'BIOS Shortcut.lnk'
			ps_script = (
				"$shell = New-Object -ComObject WScript.Shell; "
				f"$shortcut = $shell.CreateShortcut('{shortcut_path}'); "
				"$shortcut.TargetPath = \"$env:SystemRoot\\System32\\shutdown.exe\"; "
				"$shortcut.Arguments = '/r /fw /t 1'; "
				"$shortcut.WorkingDirectory = \"$env:SystemRoot\\System32\"; "
				"$shortcut.IconLocation = \"$env:SystemRoot\\System32\\shell32.dll,27\"; "
				"$shortcut.Save();"
			)
			process = subprocess.run(
				["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
				capture_output=True,
				text=True,
				encoding="utf-8",
				errors="ignore",
				shell=False,
			)
			if process.returncode != 0:
				stderr = (process.stderr or '').strip()
				error(f'Failed to create BIOS shortcut at {shortcut_path}: {stderr or "unknown error"}')
			else:
				info(f'BIOS shortcut created: {shortcut_path}')
	except Exception as exception:
		error(f'Failed to create BIOS shortcut: {exception}')

