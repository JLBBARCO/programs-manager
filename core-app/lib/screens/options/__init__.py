import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Any
import customtkinter as ctk
from lib.system import name
from lib.log import info, warning, error
from lib.json import read_external_json
from lib.screens import progress


install_json_files = (
    {'file': 'ai', 'system': ['Windows'], 'name': 'AI Tools', 'area': 'ai_area'},
    {'file': 'browsers', 'system': ['Windows', 'Linux'], 'name': 'Browsers', 'area': 'browser_area'},
    {'file': 'developer', 'system': ['Windows', 'Linux'], 'name': 'Developer Tools', 'area': 'developer_area'},
    {'file': 'documents', 'system': ['Windows'], 'name': 'Documents', 'area': 'documents_area'},
    {'file': 'file-sharing', 'system': ['Windows'], 'name': 'File Sharing', 'area': 'file_sharing_area'},
    {'file': 'games', 'system': ['Windows', 'Linux'], 'name': 'Gamer Tools', 'area': 'games_area'},
    {'file': 'imaging', 'system': ['Windows', 'Linux'], 'name': 'Imaging', 'area': 'imaging_area'},
    {'file': 'media', 'system': ['Windows', 'Linux'], 'name': 'Media', 'area': 'media_area'},
    {'file': 'online-storages', 'system': ['Windows'], 'name': 'Online Storages', 'area': 'online_storages_area'},
    {'file': 'other', 'system': ['Windows'], 'name': 'Other', 'area': 'other_area'},
    {'file': 'security', 'system': ['Windows'], 'name': 'Security', 'area': 'security_area'},
    {'file': 'social', 'system': ['Windows', 'Linux'], 'name': 'Social', 'area': 'social_medias_area'},
    {'file': 'utilities', 'system': ['Windows', 'Linux'], 'name': 'Utilities', 'area': 'utilities_area'}
    )
functions_json_files = (
    {'file': 'functions', 'system': ['Windows', 'Linux'], 'name': 'Functions'},
)


class OptionsScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=10, pady=10, fill='both')

        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.pack(padx=10, pady=10, side='top')

        self.install_option = ctk.CTkButton(self.options_frame, text='Install', command=self.show_install_options)
        self.install_option.pack(padx=10, pady=10, side='left')

        self.uninstall_option = ctk.CTkButton(self.options_frame, text='Uninstall', command=self.show_uninstall_options)
        self.uninstall_option.pack(padx=10, pady=10, side='left')

        self.function_options = ctk.CTkButton(self.options_frame, text='Functions', command=self.show_function_options)
        self.function_options.pack(padx=10, pady=10, side='left')

        self.data_frame = ctk.CTkScrollableFrame(self.main_frame, width=800, height=400)
        self.data_frame.pack(padx=10, pady=10, fill='both', expand=True)
        self.data_frame.grid_rowconfigure(0, weight=1)
        self.data_frame.grid_columnconfigure(0, weight=1)
        self.data_frame.grid_columnconfigure(1, weight=1)
        self.data_frame.grid_columnconfigure(2, weight=1)
        self.data_frame.grid_columnconfigure(3, weight=1)
        self.data_frame.grid_columnconfigure(4, weight=1)
        self.data_frame.grid_columnconfigure(5, weight=1)

        self.ai_area = ctk.CTkFrame(self.data_frame)

        self.ai_area_title = ctk.CTkLabel(self.ai_area, text='AI Tools')
        self.ai_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.browser_area = ctk.CTkFrame(self.data_frame)

        self.browser_area_title = ctk.CTkLabel(self.browser_area, text='Browsers')
        self.browser_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.developer_area = ctk.CTkFrame(self.data_frame)

        self.developer_area_title = ctk.CTkLabel(self.developer_area, text='Developer Tools')
        self.developer_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.documents_area = ctk.CTkFrame(self.data_frame)

        self.documents_area_title = ctk.CTkLabel(self.documents_area, text='Documents')
        self.documents_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.file_sharing_area = ctk.CTkFrame(self.data_frame)

        self.file_sharing_area_title = ctk.CTkLabel(self.file_sharing_area, text='File Sharing')
        self.file_sharing_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.games_area = ctk.CTkFrame(self.data_frame)

        self.games_area_title = ctk.CTkLabel(self.games_area, text='Games')
        self.games_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.imaging_area = ctk.CTkFrame(self.data_frame)

        self.imaging_area_title = ctk.CTkLabel(self.imaging_area, text='Imaging')

        self.media_area = ctk.CTkFrame(self.data_frame)

        self.media_area_title = ctk.CTkLabel(self.media_area, text='Media')
        self.media_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.online_storages_area = ctk.CTkFrame(self.data_frame)

        self.online_storages_area_title = ctk.CTkLabel(self.online_storages_area, text='Online Storages')
        self.online_storages_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.other_area = ctk.CTkFrame(self.data_frame)

        self.other_area_title = ctk.CTkLabel(self.other_area, text='Other')
        self.other_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.security_area = ctk.CTkFrame(self.data_frame)

        self.security_area_title = ctk.CTkLabel(self.security_area, text='Security')
        self.security_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.social_medias_area = ctk.CTkFrame(self.data_frame)

        self.social_medias_area_title = ctk.CTkLabel(self.social_medias_area, text='Social Medias')
        self.social_medias_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.utilities_area = ctk.CTkFrame(self.data_frame)

        self.utilities_area_title = ctk.CTkLabel(self.utilities_area, text='Utilities')
        self.utilities_area_title.pack(padx=10, pady=10, anchor='center', side='top')

        self.message_label = ctk.CTkLabel(self, text='Message Area')
        self.message_label.pack(padx=10, pady=10, anchor='sw', side='left')

        self.button_run = ctk.CTkButton(self, text='Run', command=self.run)
        self.button_run.pack(padx=10, pady=10, anchor='se', side='right')

        self.update()

        self.json_data = {}
        self.installed_programs = []
        self._display_mode = 'install'
        self._package_executor = ThreadPoolExecutor(max_workers=1)

        self.after(100, self.load_json_install_files)  # Load JSON files after a short delay to ensure the GUI is initialized
        self.after(100, self.load_json_function_files)  # Load JSON files after a short delay to ensure the GUI is initialized
        self.after(100, self.load_installed_programs)


    def load_json_install_files(self):
        self.json_numb_read = 0
        self.json_data_read = {}

        for json_file in install_json_files:
            if name() in json_file['system']:
                try:
                    self.message_label.configure(text=f"Loading {json_file['name']} JSON file...")
                    self.update()
                    data = read_external_json(json_file['file'])
                    if data is None:
                        raise ValueError('Remote JSON data is unavailable')
                    self.json_data_read[json_file['name']] = data

                    info(f"Loaded {json_file['name']} JSON file successfully.")

                except Exception as e:
                    error(f"Failed to load {json_file['name']} JSON file: {e}")
                    continue

                try:
                    area_frame = getattr(self, json_file['area'])
                    row = self.json_numb_read // 3
                    col = self.json_numb_read % 3
                    area_frame.grid(row=row, column=col, padx=10, pady=10, sticky='news')
                    self.json_numb_read += 1
                except AttributeError as e:
                    error(f"Failed to access area frame for {json_file['name']}: {e}")
                    continue

                # Store data in main json_data dictionary
                self.json_data[json_file['name']] = data
                self.generate_checkboxes(data, area_frame, json_file['name'])


        self.message_label.configure(text=f"Loaded {self.json_numb_read} JSON files successfully.")


    def generate_checkboxes(self, data: Any, area_frame: ctk.CTkFrame, category_name: str):
        """Generate checkboxes from data and add real-time update callback"""
        if isinstance(data, list):
            for idx, item in enumerate(data):
                if isinstance(item, dict) and 'name' in item:
                    def create_callback(cat_name, item_idx, checkbox):
                        def on_checkbox_change():
                            if cat_name in self.json_data and isinstance(self.json_data[cat_name], list):
                                if item_idx < len(self.json_data[cat_name]):
                                    self.json_data[cat_name][item_idx]['checkbox'] = bool(checkbox.get())
                        return on_checkbox_change

                    checkbox = ctk.CTkCheckBox(
                        area_frame,
                        text=item['name'],
                        command=lambda: None
                    )
                    checkbox.configure(command=create_callback(category_name, idx, checkbox))
                    if item.get('checkbox', False):
                        checkbox.select()
                    checkbox.pack(padx=10, pady=5, anchor='w')


    def load_json_function_files(self):
        """Load JSON function files and generate UI elements"""
        self.json_numb_read = 0

        for json_file in functions_json_files:
            if name() in json_file['system']:
                try:
                    self.message_label.configure(text=f"Loading {json_file['name']} JSON file...")
                    print(f"Loading {json_file['name']} JSON file...")
                    self.update()
                    data = read_external_json(json_file['file'])
                    if data is None:
                        raise ValueError('Remote JSON data is unavailable')
                    
                    info(f"Loaded {json_file['name']} JSON file successfully.")
                    # Store in main json_data dictionary
                    self.json_data[json_file['name']] = data
                    
                except Exception as e:
                    error(f"Failed to load {json_file['name']} JSON file: {e}")
                    continue

    def load_installed_programs(self):
        self.message_label.configure(text=f"Loading installed programs for {name()}...")
        future = self._package_executor.submit(self._list_installed_programs)
        future.add_done_callback(
            lambda result: self.after(0, self._finish_installed_programs_load, result)
        )

    def _finish_installed_programs_load(self, future):
        try:
            self.installed_programs = future.result()
            self.message_label.configure(text=f"Loaded {len(self.installed_programs)} installed programs.")
            if self._display_mode == 'uninstall':
                self.show_uninstall_options()
        except Exception as exception:
            error(f"Failed to load installed programs: {exception}")
            self.message_label.configure(text='Could not load installed programs.')

    def _list_installed_programs(self):
        if name() == 'Windows' and shutil.which('winget'):
            return self._parse_winget_output(self._run_package_command(['winget', 'list', '--accept-source-agreements']))

        if name() == 'Linux':
            if shutil.which('dpkg-query'):
                return self._parse_simple_output(self._run_package_command(['dpkg-query', '-W', '-f=${binary:Package}\t${Version}\n']), '\t')
            if shutil.which('pacman'):
                return self._parse_simple_output(self._run_package_command(['pacman', '-Qq']))
            if shutil.which('rpm'):
                return self._parse_simple_output(self._run_package_command(['rpm', '-qa', '--qf', '%{NAME}\t%{VERSION}\n']), '\t')
        return []

    @staticmethod
    def _run_package_command(command):
        process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return process.stdout or ''

    @staticmethod
    def _parse_simple_output(output, separator=None):
        packages = []
        seen = set()
        for line in output.splitlines():
            fields = line.split(separator, 1) if separator else line.split()
            value = fields[0].strip() if fields else ''
            if value and value.lower() not in seen:
                seen.add(value.lower())
                packages.append({'name': value, 'id': value, 'checkbox': False})
        return sorted(packages, key=lambda item: item['name'].lower())

    @staticmethod
    def _parse_winget_output(output):
        packages = []
        seen = set()
        for line in output.splitlines():
            if not line.strip() or set(line.strip()) <= {'-', ' '}:
                continue
            columns = re.split(r'\s{2,}', line.strip())
            if len(columns) < 2 or columns[0].lower() in {'name', 'nome'}:
                continue
            package_id = columns[1].strip()
            if package_id.lower() in {'id', 'id.', 'source', 'fonte'} or package_id.lower() in seen:
                continue
            seen.add(package_id.lower())
            packages.append({'name': columns[0].strip(), 'id': package_id, 'checkbox': False})
        return sorted(packages, key=lambda item: item['name'].lower())

    def _clear_data_frame(self):
        for widget in self.data_frame.winfo_children():
            grid_forget = getattr(widget, 'grid_forget', None)
            if callable(grid_forget):
                grid_forget()
        if hasattr(self, '_temporary_frame') and self._temporary_frame is not None:
            self._temporary_frame.destroy()
            self._temporary_frame = None

    def _show_checkbox_list(self, title, data, category_name):
        self._clear_data_frame()
        frame = ctk.CTkFrame(self.data_frame)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky='news')
        self._temporary_frame = frame
        ctk.CTkLabel(frame, text=title).pack(padx=10, pady=10, anchor='center')
        self.json_data[category_name] = data
        self.generate_checkboxes(data, frame, category_name)

    def _show_install_areas(self):
        self._clear_data_frame()
        visible_index = 0
        for json_file in install_json_files:
            if name() not in json_file['system'] or json_file['name'] not in self.json_data:
                continue
            area_frame = getattr(self, json_file['area'], None)
            if area_frame is None:
                continue
            area_frame.grid(row=visible_index // 3, column=visible_index % 3, padx=10, pady=10, sticky='news')
            visible_index += 1
        self.message_label.configure(text=f"Loaded {visible_index} install categories.")

    def show_install_options(self):
        self._display_mode = 'install'
        self._show_install_areas()


    def show_uninstall_options(self):
        self._display_mode = 'uninstall'
        if not self.installed_programs:
            self.message_label.configure(text='Installed programs are still loading.')
            return
        self._show_checkbox_list('Installed Programs', self.installed_programs, 'Uninstall Programs')


    def show_function_options(self):
        self._display_mode = 'function'
        self._show_checkbox_list('Functions', self.json_data.get('Functions', []), 'Functions')


    def run(self):
        self.activate_checkboxes = self.get_selected_options()
        master = self.master
        self.destroy()
        progress.ProgressScreen(master, self.activate_checkboxes)

    def get_selected_options(self):
        return [
            item
            for options in self.json_data.values()
            if isinstance(options, list)
            for item in options
            if isinstance(item, dict) and item.get('checkbox') is True
        ]