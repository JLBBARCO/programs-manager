import json
from lib.log import info, warning, error
from lib.system import name
from lib.config import get_github_branch
from lib.find_folders import get_ProgramsManager_folder


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().strip()
        dictionary = json.loads(data) if data else {}
        return dictionary


def read_internal_json(file):
    folder = get_ProgramsManager_folder()
    file_path = folder / f'{file}.json'
    if not file_path.exists():
        warning(f'File {file}.json not found, creating default file.')
        write_json()
    return read_json(file_path)


def read_external_json(file):
    branch = get_github_branch()
    url_path = f'https://raw.githubusercontent.com/JLBBARCO/programs-manager/{branch}/core-app/system/{name().lower()}/json/{file}.json'
    try:
        import requests
        response = requests.get(url_path, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as fallback_error:
        error(f"Failed to fetch external JSON: {fallback_error}")
    return None


def write_json(data=None):
    default_description = "User data generated after execution of write system"
    if isinstance(data, dict) and 'data' in data:
        payload = {
            "name": str(data.get('name', 'User')).strip() or 'User',
            "description": str(data.get('description', default_description)).strip() or default_description,
            "data": data.get('data', []),
        }
    else:
        payload = {
            "name": "User",
            "description": default_description,
            "data": [] if data is None else data,
        }


    folder = get_ProgramsManager_folder()
    with open(f'{folder}/user.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

