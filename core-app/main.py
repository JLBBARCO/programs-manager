from pathlib import Path
import customtkinter as ctk
from lib.log import info
from lib.screens import options
import sys


if getattr(sys, "frozen", False):
    runtime_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
else:
    runtime_root = Path(__file__).resolve().parents[1]
if str(runtime_root) not in sys.path:
    sys.path.insert(0, str(runtime_root))

from src.lib.shortcuts import ensure_platform_shortcuts_best_effort


class App(ctk.CTk):
    info('Start system')
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.resizable(False, False)
        self.title("Programs Manager")

        ensure_platform_shortcuts_best_effort()

        icon_path = Path(__file__).resolve().parent / "assets" / "icons" / "icon.ico"
        if icon_path.is_file():
            self.iconbitmap(default=str(icon_path))

        self.options_screen = options.OptionsScreen(
            self
        )

        info("End system")

if __name__ == "__main__":
    app = App()
    app.mainloop()
