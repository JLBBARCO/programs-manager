import json

from lib import log, find_folders


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


    folder = find_folders.get_ProgramsManager_folder()
    with open(f'{folder}/user.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    log.info(f"User data written to {folder}/user.json")

