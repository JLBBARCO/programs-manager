import locale
import os
import sys
from pathlib import Path

from notifypy import Notify


def _resolve_notification_icon_path() -> Path | None:
	candidate_paths = []

	try:
		source_root = Path(__file__).resolve().parents[3]
		candidate_paths.extend([
			source_root / 'src' / 'assets' / 'icon' / 'icon.ico',
			source_root / 'program' / 'src' / 'assets' / 'icon' / 'icon.ico',
		])
	except Exception:
		pass

	executable_path = Path(sys.executable).resolve()
	candidate_paths.extend([
		executable_path.with_name('icon.ico'),
		executable_path.parent / 'icon.ico',
		Path.cwd() / 'icon.ico',
		Path.cwd() / 'src' / 'assets' / 'icon' / 'icon.ico',
	])

	bundled_root_value = getattr(sys, '_MEIPASS', None)
	if bundled_root_value:
		bundled_root = Path(bundled_root_value)
		candidate_paths.extend([
			bundled_root / 'icon.ico',
			bundled_root / 'src' / 'assets' / 'icon' / 'icon.ico',
		])

	for candidate in candidate_paths:
		if candidate.exists():
			return candidate

	return None


def _get_device_language() -> str:
	for value in (
		locale.getlocale()[0],
		os.environ.get('LC_ALL'),
		os.environ.get('LANG'),
		os.environ.get('LANGUAGE'),
	):
		if value:
			return value.split('_', 1)[0].split('-', 1)[0].lower()

	return 'en'


def _get_completion_message() -> tuple[str, str]:
	messages = {
		'en': (
			'Programs Manager',
			'All installations, uninstallations, updates, and functions have finished.',
		),
		'pt': (
			'Programs Manager',
			'Todas as instalações, desinstalações, atualizações e funções foram finalizadas.',
		),
		'es': (
			'Programs Manager',
			'Todas las instalaciones, desinstalaciones, actualizaciones y funciones han finalizado.',
		),
		'fr': (
			'Programs Manager',
			'Toutes les installations, désinstallations, mises à jour et fonctions sont terminées.',
		),
		'de': (
			'Programs Manager',
			'Alle Installationen, Deinstallationen, Aktualisierungen und Funktionen sind abgeschlossen.',
		),
	}

	return messages.get(_get_device_language(), messages['en'])


def finalize_notification():
	try:
		title, message = _get_completion_message()
		notification = Notify()
		notification.title = title
		notification.message = message
		icon_path = _resolve_notification_icon_path()
		if icon_path is not None:
			notification.icon = str(icon_path)
		notification.send()
		return True
	except Exception:
		return False
