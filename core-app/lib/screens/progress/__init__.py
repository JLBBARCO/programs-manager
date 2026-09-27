from threading import Thread
from typing import Any

import customtkinter as ctk
from lib.log import info

class ProgressScreen(ctk.CTkFrame):
    def __init__(self, master: Any, options_array):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=10, pady=10, fill='both')

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400, height=20)
        self.progress_bar.pack(padx=10, pady=10, side='top')

        self.progress_label = ctk.CTkLabel(self.main_frame, text="Progress: 0%")
        self.progress_label.pack(padx=10, pady=10, side='top')

        self.progress_info_label = ctk.CTkLabel(self.main_frame, text="Info: Waiting for progress...")
        self.progress_info_label.pack(padx=10, pady=10, side='top')

        self.progress_bar.set(0)
        self.after(0, lambda: self.pipeline_executions(options_array))


    def pipeline_executions(self, options_array):
        if not options_array:
            self._update_progress(1, 'No options selected.')
            return

        Thread(target=self._run_pipeline, args=(list(options_array),), daemon=True).start()

    def _run_pipeline(self, options_array):
        total = len(options_array)
        for index, option in enumerate(options_array, start=1):
            option_type = option.get('type', '')
            option_name = option.get('name', option.get('id', 'Unknown option'))
            self._update_progress((index - 1) / total, f'Executing: {option_name}')

            try:
                if option_type == 'uninstall':
                    from lib.uninstall import uninstall
                    uninstall([option])
                elif option_type == 'install':
                    from lib.install import install
                    install([option])
                elif option_type == 'function':
                    from lib.functions import functions
                    functions(option)
                else:
                    raise ValueError(f'Unsupported option type: {option_type}')
            except Exception as exception:
                self._update_progress((index - 1) / total, f'Error: {option_name} - {exception}')
                continue

            self._update_progress(index / total, f'Completed: {option_name}')

        self._update_progress(1, 'Pipeline completed.')

    def _update_progress(self, value, message):
        self.after(0, self._apply_progress, value, message)

    def _apply_progress(self, value, message):
        percentage = int(value * 100)
        self.progress_bar.set(value)
        self.progress_label.configure(text=f'Progress: {percentage}%')
        self.progress_info_label.configure(text=f'Info: {message}')