# Auto Installation Programs

Auto installation programs for windows

## Interface

![UI](src/assets/img/thumbnail.webp)

## Packaging

The project is built with PyInstaller using `build.bat`. All files under
`install/` and the `src` package are bundled into the executable. When the
application is run from the compiled directory the code uses a helper named
`_resource_path` to locate data files inside the bundle (`sys._MEIPASS`).

Logs (`log.log` and `programs.log`) are written next to the executable rather
than the current working directory, avoiding mysterious “path not found”
errors which were previously seen during installations.

## Installations

Installations in different SOs

### Windows

#### Drivers

The system analyzes the video card and installs the necessary drivers.

- AMD
- Intel
- NVIDIA

#### Essentials Programs

- Adobe Acrobat
- Cloudflare Warp
- Google Chrome
- Google Drive
- Mozilla FireFox
- Spotify
- Telegram Desktop
- VLC
- WinRAR
- WhatsApp

#### Microsoft Office

#### Screen

- AnyDesk
- SpaceDesk Client
- SpaceDesk Server

#### Customization

- Lively Wallpaper
- Rainmeter
- TranslucentTB

#### Developer Tools

- Arduino IDE
- Blender
- Docker Desktop
- Figma
- GIMP 3
- Git
- Github Desktop
- Java Runtime Environment
- Microsoft Teams
- MySQL Workbench
- Node.js
- Python 3.12
- Rufus
- Ventoy
- VirtualBox
- Visual Studio Code
- XAMPP

#### Games

- CourseForge
- Discord
- Epic Games Launcher
- Google Play Games
- Radmin VPN
- Steam
- Xbox App

### Linux

#### Linux Drivers

The system analyzes the video card and installs the necessary drivers.

- AMD
- Intel
- NVIDIA

#### Essencial Programs

- Curl
- Git
- Google Chrome
- Mozilla FireFox
- Spotify
- Telegram
- VLC
- WhatsApp

#### Screen

- AnyDesk
- Git
- VNC Server

#### Developer Tools

- Arduino IDE
- Blander
- Docker
- Gimp
- Git
- Node.js
- Python 3
- VirtualBox
- Visual Studio Code

#### Server Tools

- Curl & Wget
- Git
- HTOP
- Net-Tools
- SSH Server
- Vim

### MacOS

#### Essential programs

- Adobe Acrobat
- Cloudflare Warp
- Google Chrome
- Google Drive
- Mozilla FireFox
- Spotify
- Telegram
- The Unarchiver
- VLC
- WhatsApp

#### Screen

- AnyDesk

#### Developer Tools

- Arduino IDE
- Blender
- Docker
- Figma
- GIMP
- Github
- Microsoft Teams
- MySQL Workbench
- VirtualBox
- Visual Studio Code
- XAMPP
