from pathlib import Path
from typing import Any
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = Path(__file__).resolve().parent
for import_path in (PROJECT_ROOT, APP_ROOT):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from src.lib.shortcuts import ensure_platform_shortcuts_best_effort
from lib import system, log, screen_primary, screen_secondary, updates, install, uninstall, web

from lib.functions import functions, notifications

theme = "system"
operational_system = system.name()
system_title = f'{operational_system} Programs Manager'


log.info('Start System')
log.info(f'Start Programs Manager')
log.info(f'Operating System: {operational_system}')
ensure_platform_shortcuts_best_effort()

try:
    web.start_internet_monitor()
    secondary_result: Any = None
    try:
        primary_screen = screen_primary.ScreenPrimary(operational_system, theme, system_title)
        primary_screen.mainloop()
        primary_array = primary_screen.return_array() or []
    except:
        log.warning('User interrupted the program.')
        primary_array = []

    if primary_array:
        try:
            secondary_screen = screen_secondary.ScreenSecondary(operational_system, theme, system_title, primary_array)
            secondary_screen.mainloop()
            secondary_result: Any = secondary_screen.ScreenSecondaryReturn()
        except KeyboardInterrupt:
            log.warning('User interrupted the program.')
            secondary_result = None

    if primary_array and secondary_result:
        install_list = []
        uninstall_list = []
        function_list = []

        if isinstance(secondary_result, dict):
            install_list.extend(item for item in secondary_result.get('install', []) if isinstance(item, dict))
            uninstall_list.extend(item for item in secondary_result.get('uninstall', []) if isinstance(item, dict))
            function_list.extend(item for item in secondary_result.get('function', []) if isinstance(item, dict))
        elif isinstance(secondary_result, list):
            try:
                for programs in secondary_result:
                    if not isinstance(programs, dict):
                        continue

                    entry_type = str(programs.get('type', '')).strip().lower()
                    if entry_type == 'install':
                        install_list.append(programs)
                    elif entry_type == 'uninstall':
                        uninstall_list.append(programs)
                    elif entry_type == 'function':
                        function_list.append(programs)
                log.info('Data Successfully separated into its reference array')
            except Exception as e:
                log.error(f'Error in separated data in yours reference array: {e}')


        web.start_shared_log_server()
        web.wait_for_internet_connection()
        web.open_programs_manager_site(web.get_shared_log_server_port())

        updates.update_package_manager(operational_system)
        if uninstall_list:
            try:
                web.wait_for_internet_connection()
                log.info('Uninstalling programs...')
                uninstall.uninstall(uninstall_list, operational_system)
            except Exception as e:
                log.error(f'Error to run Uninstall System: {e}')
        if install_list:
            try:
                web.wait_for_internet_connection()
                log.info('Installing programs...')
                install.install(install_list, operational_system)
            except Exception as e:
                log.error(f'Error to run Install System: {e}')
        if function_list:
            try:
                web.wait_for_internet_connection()
                log.info('Executing functions...')
                functions(function_list)
            except Exception as e:
                log.error(f'Error to run Functions System: {e}')


except Exception as e:
    log.error(f"An error occurred: {e}")

finally:
    log.info('End System')
    web.stop_internet_monitor()
    web.stop_shared_log_server()
    notifications.finalize_notification()

