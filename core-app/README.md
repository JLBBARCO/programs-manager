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
- [build.bat](build.bat) and [build.sh](build.sh) build the packaged app.
- [run.ps1](run.ps1) and [run.sh](run.sh) download or reuse a packaged build.

## Runtime JSON

The app reads JSON from `system/<os>/json/` at runtime. Those files are fetched from GitHub RAW and are not bundled into the build artifacts.

The expected path is:

`https://raw.githubusercontent.com/JLBBARCO/programs-manager/<branch>/system/<operating_system>/json/<file_name>.json`

## Build scripts

- Windows: run [build.bat](build.bat).
- Linux: run [build.sh](build.sh).

The Windows script skips the final pause automatically in CI.

## Run scripts

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

- [.github/workflows/build-core-app.yml](../.github/workflows/build-core-app.yml) builds for `main` and `develop`.
