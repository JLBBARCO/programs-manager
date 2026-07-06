import json

from lib import log, find_folders


def _has_valid_id(entry) -> bool:
    """A program is only eligible for installation through the package
    manager if it carries a non-empty `id`. This filter is applied at
    write time as a safety net, even though the program list already
    filters out invalid ids upstream."""
    if not isinstance(entry, dict):
        return False
    return bool(str(entry.get('id', '')).strip())


def write_json(data=None):
    default_description = "User data generated after execution of write system"
    if isinstance(data, dict) and 'data' in data:
        raw_entries = data.get('data', [])
        payload = {
            "name": str(data.get('name', 'User')).strip() or 'User',
            "description": str(data.get('description', default_description)).strip() or default_description,
            "data": raw_entries,
        }
    else:
        payload = {
            "name": "User",
            "description": default_description,
            "data": [] if data is None else data,
        }

    raw_entries = payload.get('data', [])
    if isinstance(raw_entries, list):
        filtered_entries = [entry for entry in raw_entries if _has_valid_id(entry)]
        skipped = len(raw_entries) - len(filtered_entries)
        if skipped:
            log.warning(f'Skipped {skipped} program(s) without a valid package manager id.')
        payload['data'] = filtered_entries

    folder = find_folders.get_ProgramsManager_folder()
    with open(f'{folder}/user.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    log.info(f"User data written to {folder}/user.json")

