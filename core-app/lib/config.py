from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / '.env'
DEFAULT_BRANCH = 'main'
_TRUE_VALUES = {'1', 'true', 'yes', 'on'}


def _read_env() -> dict[str, str]:
    if not ENV_FILE.is_file():
        return {}

    values = {}
    try:
        lines = ENV_FILE.read_text(encoding='utf-8').splitlines()
    except OSError:
        return {}

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip().lower()] = value.strip().strip('"\'')
    return values


def is_developer_mode() -> bool:
    return _read_env().get('developer', '').lower() in _TRUE_VALUES


def get_github_branch() -> str:
    if not is_developer_mode():
        return DEFAULT_BRANCH

    branch = _read_env().get('branch', '').strip()
    return branch or DEFAULT_BRANCH
