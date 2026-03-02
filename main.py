from src.lib import externalLibs as libs
from src.lib import installations
from src.lib import log

# * Main Variables
systemName = "Windows Installations"
widthWindow = 400
heightWindow = 450

class App(libs.ctk.CTk):  # type: ignore
    def __init__(self):
        super().__init__()

        log.log('Program started', level="INFO")
        libs.ctk.set_appearance_mode("system")

        self.title(systemName)
        self.geometry(f'{widthWindow}x{heightWindow}')

        self.container = libs.ctk.CTkFrame(self)
        self.container.grid(pady=20, padx=50, row=0, column=0)

        self.labelTitle = libs.ctk.CTkLabel(self.container, text="Welcome to the Windows Installations", font=libs.ctk.CTkFont(size=16, weight="bold"))
        self.labelTitle.grid(pady=10, padx=10, columnspan=2, row=0)

        self.labelCheck = libs.ctk.CTkLabel(self.container, text="Select the programs you want to install:")
        self.labelCheck.grid(pady=10, padx=10, columnspan=2, row=1)

        self.options_frame = libs.ctk.CTkFrame(self.container)
        self.options_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        self.checkedButtonEssentials = libs.ctk.BooleanVar()
        self.checkButtonEssentials = libs.ctk.CTkCheckBox(self.options_frame, text="Essential Programs", onvalue=True, offvalue=False, variable=self.checkedButtonEssentials)
        self.checkButtonEssentials.select()
        self.checkButtonEssentials.grid(padx=20, pady=5, row=0, column=0, sticky="w")

        self.checkedButtonOffice = libs.ctk.BooleanVar()
        self.checkButtonOffice = libs.ctk.CTkCheckBox(self.options_frame, text="Microsoft Office", onvalue=True, offvalue=False, variable=self.checkedButtonOffice)
        self.checkButtonOffice.select()
        self.checkButtonOffice.grid(padx=20, pady=5, row=1, column=0, sticky="w")

        self.checkedButtonScreen = libs.ctk.BooleanVar()
        self.checkButtonScreen = libs.ctk.CTkCheckBox(self.options_frame, text="Screen", onvalue=True, offvalue=False, variable=self.checkedButtonScreen)
        self.checkButtonScreen.select()
        self.checkButtonScreen.grid(padx=20, pady=5, row=2, column=0, sticky="w")

        self.checkedButtonCustomization = libs.ctk.BooleanVar()
        self.checkButtonCustomization = libs.ctk.CTkCheckBox(self.options_frame, text="Customization", onvalue=True, offvalue=False, variable=self.checkedButtonCustomization)
        self.checkButtonCustomization.select()
        self.checkButtonCustomization.grid(padx=20, pady=5, row=3, column=0, sticky="w")

        self.checkedButtonDevelopment = libs.ctk.BooleanVar()
        self.checkButtonDevelopment = libs.ctk.CTkCheckBox(self.options_frame, text="Developer Tools", onvalue=True, offvalue=False, variable=self.checkedButtonDevelopment)
        self.checkButtonDevelopment.select()
        self.checkButtonDevelopment.grid(padx=20, pady=5, row=4, column=0, sticky="w")

        self.checkedButtonGames = libs.ctk.BooleanVar()
        self.checkButtonGames = libs.ctk.CTkCheckBox(self.options_frame, text="Games", onvalue=True, offvalue=False, variable=self.checkedButtonGames)
        self.checkButtonGames.select()
        self.checkButtonGames.grid(padx=20, pady=5, row=5, column=0, sticky="w")

        self.submitButton = libs.ctk.CTkButton(self.container, text="Install", command=self.install)
        self.submitButton.grid(pady=20, column=0, row=3)

        self.cancelButton = libs.ctk.CTkButton(self.container, text="Cancel", command=self.cancel)
        self.cancelButton.grid(pady=20, column=1, row=3)

    def install(self):
        self.destroy()  # Close the GUI before starting installations
        
        if self.checkedButtonEssentials.get():
            log.log(f'Install Essential Programs: {self.checkedButtonEssentials.get()}')
            log.log(installations.essentials())

        if self.checkedButtonOffice.get():
            log.log(f'Install Office: {self.checkedButtonOffice.get()}')
            log.log(installations.office())

        if self.checkedButtonDevelopment.get():
            log.log(f'Install Development Programs: {self.checkedButtonDevelopment.get()}')
            log.log(installations.development())

        if self.checkedButtonGames.get():
            log.log(f'Install Games: {self.checkedButtonGames.get()}')
            log.log(installations.games())

        if self.checkedButtonScreen.get():
            log.log(f'Install Screen: {self.checkedButtonScreen.get()}')
            log.log(installations.screen())

        if self.checkedButtonCustomization.get():
            log.log(f'Install Customization: {self.checkedButtonCustomization.get()}')
            log.log(installations.customization())

    def cancel(self):
        log.log('Installation cancelled by the user')
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
