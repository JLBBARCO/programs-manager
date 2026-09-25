# Programs Manager

Programs Manager is a Python desktop application for selecting package-manager actions and custom functions, then running those actions in the background while sharing a live log stream with the website.

## What it does

- Shows a primary screen to pick categories.
- Shows a secondary screen to pick install, uninstall, and function entries.
- Starts a local shared log server on a free `99xx` port.
- Opens the Programs Manager website with the selected port in `?port=NNNN`.
- Runs actions in this order: uninstall, function, install.

## Repository layout

- [main.py](main.py) is the entry point.
- [lib/](lib) contains the runtime modules for screens, logging, package actions, updates, and functions.
- [system/](system) contains runtime JSON files per operating system.
- [run.ps1](run.ps1) and [run.sh](run.sh) run the app from Python source.

## Runtime JSON

The app reads JSON from `system/<os>/json/` at runtime. Those files are fetched from GitHub RAW and are not bundled into the build artifacts.

The expected path is:

`https://raw.githubusercontent.com/JLBBARCO/programs-manager/<branch>/system/<operating_system>/json/<file_name>.json`

## Run scripts

The run scripts find Python 3.12 or newer, install it through the available system package manager when missing, install the runtime dependencies, then launch `main.py` in the Python interpreter. When launched from the repository they use the local source; when piped from GitHub they download the selected branch source first.

Windows:

```powershell
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.ps1 | iex
```

Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.sh | bash
```

Branch override for testing:

```powershell
$env:AIP_BRANCH='develop'; irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.ps1 | iex
```

```bash
AIP_BRANCH=develop curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.sh | bash
```

## GitHub Actions

The screenshots workflow runs the application directly through Python. It does not package or compile the desktop app.
