import shutil
import subprocess
import re
from lib import system


def _run_command(args: list[str]) -> str:
        process = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            shell=False,
        )
        return (process.stdout or '') + ('\n' + process.stderr if process.stderr else '')


def _clean_terminal_text(value: str) -> str:
        value = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', value)
        value = value.replace('\r', '').strip()
        return ''.join(character for character in value if character.isprintable() or character == '\t').strip()


def _is_noise_line(line: str) -> bool:
        stripped = _clean_terminal_text(line)
        if not stripped:
            return True

        lowered = stripped.lower()
        if lowered.startswith(('warning:', 'error:', 'erro:', 'advertencia:', 'failed:', '==>')):
            return True
        if lowered.startswith(('the source', 'this source', 'do you agree', 'terms', 'msstore source')):
            return True
        if lowered.startswith(('no installed package', 'nenhum pacote', 'no packages')):
            return True
        if lowered.startswith(('installed packages', 'available packages')):
            return True
        if lowered in {'name', 'nome', 'id', 'fonte', 'source', 'package'}:
            return True
        if _is_progress_line(stripped):
            return True

        return False


def _is_valid_package_id(item_id: str, package_manager: str) -> bool:
        token = _clean_terminal_text(item_id)
        if not token:
            return False
        if token != item_id.strip():
            return False
        if re.search(r'\s', token):
            return False
        if re.search(r'[<>"\'`|&;,$(){}[\]\\]', token):
            return False
        if re.search(r'\b\d{1,3}%\b', token):
            return False

        lowered = token.lower()
        if lowered in {'name', 'nome', 'id', 'package', 'source', 'fonte', 'installed', 'available', 'latest', 'unknown'}:
            return False
        if lowered.startswith(('http:', 'https:', 'file:')):
            return False

        if package_manager == 'winget':
            return _looks_like_winget_id(token)
        if package_manager in {'apt', 'dpkg'}:
            return bool(re.fullmatch(r'[a-z0-9][a-z0-9+.-]*', token))
        if package_manager == 'brew':
            return bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9@+._-]*', token))
        if package_manager in {'rpm', 'dnf'}:
            return bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9+._-]*', token))
        if package_manager == 'pacman':
            return bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9@+._-]*', token))

        return bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9@+._-]*', token))


def _is_valid_version(value: str) -> bool:
        """Returns True when `value` looks like a real, installable version
        string (e.g. '1.2.3', '10.0.19041.1-1') rather than a placeholder
        such as 'unknown', 'latest' or an empty value."""
        token = _clean_terminal_text(value)
        if not token:
            return False

        lowered = token.lower()
        if lowered in {'unknown', 'installed', 'available', 'latest', 'none', 'n/a', '-'}:
            return False
        if re.search(r'\s', token):
            return False

        return bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9:._+~-]*', token))


def _format_package(package: dict[str, str]) -> dict[str, str | bool]:
        name = str(package.get('name', '')).strip()
        item_id = str(package.get('id', name)).strip() or name
        version = _clean_terminal_text(str(package.get('version', '')))

        formatted: dict[str, str | bool] = {'name': name, 'type': 'install', 'id': item_id, 'checkbox': True}
        if _is_valid_version(version):
            formatted['version'] = version

        return formatted


def _format_packages(packages: list[dict[str, str]], package_manager: str) -> list[dict[str, str | bool]]:
        formatted_packages: list[dict[str, str | bool]] = []
        for package in packages:
            if not isinstance(package, dict):
                continue

            name = _clean_terminal_text(str(package.get('name', '')))
            item_id = _clean_terminal_text(str(package.get('id', name)) or name)
            version = _clean_terminal_text(str(package.get('version', '')))
            if not name or _is_noise_line(name) or not _is_valid_package_id(item_id, package_manager):
                continue

            formatted_packages.append(_format_package({'name': name, 'id': item_id, 'version': version}))

        return formatted_packages


def _append_package(
        results: list[dict[str, str]],
        seen_ids: set[str],
        name: str,
        item_id: str,
        package_manager: str,
        version: str = '',
) -> None:
        name = _clean_terminal_text(name)
        item_id = _clean_terminal_text(item_id)
        version = _clean_terminal_text(version)
        if not name or _is_noise_line(name) or not _is_valid_package_id(item_id, package_manager):
            return

        key = item_id.lower()
        if key in seen_ids:
            return

        seen_ids.add(key)
        results.append({'name': name, 'id': item_id, 'version': version})


def _is_progress_line(line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False

        if re.search(r'\b\d{1,3}%\b', stripped) and len(stripped) < 120:
            return True

        if len(stripped) < 120 and set(stripped) <= {'.', '-', '=', ' '}:
            return True

        if len(stripped) < 120 and re.fullmatch(r'[\W_]+', stripped):
            return True

        return False


def _is_winget_source(value: str) -> bool:
        return value.strip().lower() in {'winget', 'msstore'}


def _looks_like_winget_version(value: str) -> bool:
        token = value.strip().lower()
        if not token:
            return False
        if token in {'unknown', 'installed', 'available', 'latest'}:
            return True
        return bool(re.fullmatch(r'[0-9]+(?:\.[0-9a-z]+)*', token))


def _looks_like_winget_id(value: str) -> bool:
        token = value.strip()
        if not token or _is_winget_source(token):
            return False
        if _looks_like_winget_version(token):
            return False
        return bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', token))


def _extract_winget_name_and_id(label: str) -> tuple[str, str, str]:
        tokens = [token for token in label.split() if token.strip()]
        if len(tokens) < 2:
            return label.strip(), '', ''

        for index, token in enumerate(tokens):
            if not _looks_like_winget_id(token):
                continue

            next_token = tokens[index + 1] if index + 1 < len(tokens) else ''
            if index + 1 >= len(tokens) or _looks_like_winget_version(next_token) or _is_winget_source(next_token):
                extracted_name = ' '.join(tokens[:index]).strip()
                version = next_token if _looks_like_winget_version(next_token) else ''
                if extracted_name:
                    return extracted_name, token.strip(), version

        if len(tokens) >= 2 and _looks_like_winget_version(tokens[-1]):
            candidate_id = tokens[-2].strip()
            extracted_name = ' '.join(tokens[:-2]).strip()
            if extracted_name and _looks_like_winget_id(candidate_id):
                return extracted_name, candidate_id, tokens[-1].strip()

        return label.strip(), '', ''


def _parse_winget_rows(output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_ids: set[str] = set()

        for line in output.splitlines():
            raw = _clean_terminal_text(line)
            if _is_noise_line(raw):
                continue

            lowered = raw.lower()
            if lowered.startswith('name') or lowered.startswith('nome'):
                if 'id' in lowered or 'fonte' in lowered or 'source' in lowered:
                    continue
            if lowered in {'name', 'nome', 'id', 'fonte', 'source'}:
                continue
            if set(raw) <= {'-', ' '}:
                continue
            if re.search(r'\b\d{1,3}%\b', raw):
                continue

            parts = re.split(r'\s{2,}', raw)
            version = ''
            if len(parts) < 2:
                extracted_name, item_id, version = _extract_winget_name_and_id(raw)
                name = extracted_name
            else:
                name = str(parts[0]).strip()
                item_id = str(parts[1]).strip()
                if len(parts) >= 3 and _looks_like_winget_version(parts[2]):
                    version = str(parts[2]).strip()

            if not name or not item_id:
                extracted_name, extracted_id, extracted_version = _extract_winget_name_and_id(raw)
                name = name or extracted_name
                item_id = item_id or extracted_id
                version = version or extracted_version

            if not name or not item_id:
                continue
            if name.lower() in {'name', 'nome'}:
                continue
            if _is_winget_source(item_id) or item_id.lower() in {'id', 'id.'}:
                extracted_name, extracted_id, extracted_version = _extract_winget_name_and_id(raw)
                if extracted_name and extracted_id:
                    name = extracted_name
                    item_id = extracted_id
                    version = version or extracted_version
                else:
                    continue

            _append_package(results, seen_ids, name, item_id, 'winget', version)

        return sorted(results, key=lambda item: item['name'].lower())


def _run_and_parse_packages(args: list[str]) -> list[dict[str, str]]:
        output = _run_command(args)
        return _parse_winget_rows(output)


def _parse_simple_package_output(output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_ids: set[str] = set()

        for line in output.splitlines():
            raw = _clean_terminal_text(line)
            if _is_noise_line(raw):
                continue

            name = raw.split()[0].strip()
            _append_package(results, seen_ids, name, name, 'brew')

        return sorted(results, key=lambda item: item['name'].lower())


def _parse_name_version_pairs(output: str, package_manager: str) -> list[dict[str, str]]:
        """Parses lines shaped like `<name> <version> [...]`, as produced by
        commands such as `brew list --versions` or `pacman -Q`."""
        results: list[dict[str, str]] = []
        seen_ids: set[str] = set()

        for line in output.splitlines():
            raw = _clean_terminal_text(line)
            if _is_noise_line(raw):
                continue

            tokens = raw.split()
            if not tokens:
                continue

            name = tokens[0].strip()
            version = tokens[1].strip() if len(tokens) > 1 else ''
            _append_package(results, seen_ids, name, name, package_manager, version)

        return sorted(results, key=lambda item: item['name'].lower())


def _deduplicate_packages(packages: list[dict[str, str]]) -> list[dict[str, str | bool]]:
        unique_packages: dict[str, dict[str, str | bool]] = {}
        for package in packages:
            if not isinstance(package, dict):
                continue
            name = _clean_terminal_text(str(package.get('name', '')))
            item_id = _clean_terminal_text(str(package.get('id', name)) or name)
            version = _clean_terminal_text(str(package.get('version', '')))
            if not name or _is_noise_line(name) or not _is_valid_package_id(item_id, 'brew'):
                continue
            unique_packages[item_id.lower()] = _format_package({'name': name, 'id': item_id, 'version': version})

        return sorted(unique_packages.values(), key=lambda item: item['name'].lower())


def _parse_dpkg_list_output(output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_ids: set[str] = set()

        for line in output.splitlines():
            raw = _clean_terminal_text(line)
            if _is_noise_line(raw):
                continue

            columns = raw.split('\t')
            package_name = columns[0].strip()
            if ':' in package_name:
                package_name = package_name.split(':', 1)[0].strip()
            version = columns[1].strip() if len(columns) > 1 else ''
            _append_package(results, seen_ids, package_name, package_name, 'apt', version)

        return sorted(results, key=lambda item: item['name'].lower())


def _parse_rpm_list_output(output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_ids: set[str] = set()

        for line in output.splitlines():
            raw = _clean_terminal_text(line)
            if _is_noise_line(raw):
                continue

            columns = raw.split('\t')
            package_name = columns[0].strip()
            version = columns[1].strip() if len(columns) > 1 else ''
            _append_package(results, seen_ids, package_name, package_name, 'rpm', version)

        return sorted(results, key=lambda item: item['name'].lower())


def _parse_dnf_list_output(output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_ids: set[str] = set()

        for line in output.splitlines():
            raw = _clean_terminal_text(line)
            if _is_noise_line(raw):
                continue

            tokens = raw.split()
            if not tokens:
                continue

            token = tokens[0].strip()
            if '.' in token:
                token = token.split('.', 1)[0]

            version = tokens[1].strip() if len(tokens) > 1 else ''
            _append_package(results, seen_ids, token, token, 'dnf', version)

        return sorted(results, key=lambda item: item['name'].lower())


def run():
        system_name = system.name()

        if system_name == 'Windows':
            return _format_packages(_run_and_parse_packages(['winget', 'list', '--accept-source-agreements']), 'winget')

        if system_name == 'MacOS' and shutil.which('brew'):
            installed_items = _parse_name_version_pairs(_run_command(['brew', 'list', '--versions', '--formula']), 'brew')
            installed_items.extend(_parse_name_version_pairs(_run_command(['brew', 'list', '--versions', '--cask']), 'brew'))
            return _deduplicate_packages(installed_items)

        if system_name == 'Linux':
            if shutil.which('dpkg-query'):
                return _format_packages(_parse_dpkg_list_output(_run_command(['dpkg-query', '-W', '-f=${binary:Package}\t${Version}\n'])), 'apt')
            if shutil.which('pacman'):
                return _format_packages(_parse_name_version_pairs(_run_command(['pacman', '-Q']), 'pacman'), 'pacman')
            if shutil.which('rpm'):
                return _format_packages(_parse_rpm_list_output(_run_command(['rpm', '-qa', '--qf', '%{NAME}\t%{VERSION}\n'])), 'rpm')
            if shutil.which('dnf'):
                return _format_packages(_parse_dnf_list_output(_run_command(['dnf', 'list', 'installed'])), 'dnf')

        return []
