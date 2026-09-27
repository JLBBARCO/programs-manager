# Programs Manager

Programs Manager is a Python desktop application for installing and removing software and running system maintenance tasks. Its graphical interface is built with CustomTkinter. Program and function catalogs are JSON files stored in this repository and fetched from GitHub when the application starts.

## Contents

- [Platforms and requirements](#platforms-and-requirements)
- [Run a published release](#run-a-published-release)
- [Run from source](#run-from-source)
- [Build the application](#build-the-application)
- [Use the application](#use-the-application)
- [Repository layout](#repository-layout)
- [Application architecture](#application-architecture)
- [Catalog format and maintenance](#catalog-format-and-maintenance)
- [Configuration and `.env`](docs/CONFIGURATION.md)
- [Workflows](#workflows)
- [Local files and logs](#local-files-and-logs)

## Platforms and requirements

| Platform | Requirements | Package operations |
| --- | --- | --- |
| Windows | Python 3.12 to run from source; Tk support; `winget` for package operations | `winget install`, `winget uninstall`, and `winget upgrade` |
| Linux | Python 3.12, Tkinter, and `apt`; `sudo` for package operations | `apt install` and `apt remove` |

The interface fetches catalogs from GitHub, and the launchers use the GitHub Releases API to find builds. An internet connection is needed for catalog loading, release downloads, and update checks. Some maintenance functions also download packages or drivers.

The core application detects Windows and Linux. Shortcut helper code includes macOS support, but the interface does not recognize macOS as a supported platform and the application does not provide complete macOS support.

## Run a published release

The launchers install or update the app in `%USERPROFILE%\.programs-manager` on Windows or `~/.programs-manager` on Linux, then start the executable. They also try to create a desktop or application-menu shortcut.

**Windows PowerShell:**

```powershell
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.ps1 | iex
```

**Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.sh | bash
```

The launchers support two optional environment variables:

- `AIP_VERSION`: download a specific release version, with or without the leading `v`.
- `AIP_BRANCH`: select a release channel. The launchers use `main` by default; the PowerShell launcher selects the latest prerelease when the value is `develop`.

For example, on PowerShell:

```powershell
$env:AIP_VERSION = '2026.07.18.200959'
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.ps1 | iex
```

The `AIP_*` variables configure the launcher process; they are separate from the repository `.env` file documented in [Configuration and `.env`](docs/CONFIGURATION.md). Check the GitHub Releases page for available versions and channels. The website also contains beta launcher commands, while current build and release workflow branch settings are not fully aligned.

## Run from source

Run these commands from the repository root:

```bash
python -m venv .venv
```

Activate the environment, then install dependencies and launch:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python core-app/main.py
```

On Linux, install your distribution's Tkinter package if needed (for example, `python3-tk` on Ubuntu). Package installation and removal use `apt`, even though the installed-program listing can detect `dpkg`, `pacman`, or `rpm` systems. Windows package installation/removal requires `winget`.

When running from source, the working directory matters: logs are written to `log.log` in the current directory. The application reads the repository-root `.env` file for its developer/catalog branch settings. See [Configuration and `.env`](docs/CONFIGURATION.md).

## Build the application

Run the relevant script from the repository root:

```powershell
core-app\build.bat
```

```bash
core-app/build.sh
```

Both scripts install dependencies from `requirements.txt` and use PyInstaller in one-directory (`onedir`) mode. The output is placed in `dist/Programs Manager/`. The Linux build requires Tk support; the GitHub Actions workflow installs `python3-tk` on its Ubuntu runner.

The `Build Multi-Platform Core App` workflow builds Windows x64, Windows x86, and Linux x64 artifacts and generates SHA-256 checksum files. Release publication is handled by `release.yml`.

## Use the application

The main window provides three modes:

1. **Install** loads platform-specific software categories and lets you select packages to install.
2. **Uninstall** lists installed packages detected by the system and lets you select packages to remove.
3. **Functions** displays maintenance tasks provided by the platform's `functions.json` catalog.

Select one or more checkboxes and press **Run**. The progress screen processes selected entries sequentially. An error for one entry is displayed and logged; the pipeline continues with the next entry.

Package operations need an internet connection. Linux install and removal commands invoke `sudo`, so authorization may be requested. Some functions modify system settings, startup entries, drivers, or temporary files. Review a function's implementation before running it, especially on systems with important data or customized settings.

## Repository layout

```text
core-app/
  main.py                         GUI application entry point
  lib/
    screens/                      Options and progress screens
    install/ uninstall/            Package installation and removal
    functions/                     System utility implementations
    json/                          JSON read/write helpers
    web/                           Connectivity and local history server
    config.py                      Repository .env configuration
  system/
    windows/json/                  Windows package and function catalogs
    linux/json/                    Linux package and function catalogs
  run.ps1, run.sh                  Release download, update, and launch scripts
  build.bat, build.sh              Local PyInstaller build scripts
src/lib/                           Shortcut creation helpers
website/client/                    Static launcher instructions
.github/workflows/                 Build, release, and launcher workflows
requirements.txt                   Pinned Python dependencies
```

## Application architecture

### Startup and interface

`core-app/main.py` initializes the CustomTkinter window, sets the system appearance, tries to create platform shortcuts, and displays `OptionsScreen`. Shortcut creation is best-effort: failures do not prevent the interface from starting.

`core-app/lib/screens/options` loads the program and function catalogs from the raw GitHub URL for the current platform and branch. It also queries the local package manager to populate the uninstall list. `core-app/lib/screens/progress` runs the selected operations in a worker thread and updates the interface with progress and status messages.

### Package operations

`core-app/lib/install` and `core-app/lib/uninstall` handle the selected catalog entries. Windows uses WinGet IDs; Linux install and removal use apt package names. The uninstall screen's package discovery supports `winget` on Windows and can read package listings from `dpkg-query`, `pacman`, or `rpm` on Linux; this discovery support does not change the apt-based removal command.

The app's package manager update function uses `winget upgrade` on Windows and `apt update` on Linux. Other maintenance routines can have different platform behavior and requirements.

### Maintenance functions

Function identifiers in the platform `functions.json` catalog are resolved by `core-app/lib/functions`. Available source modules include tasks for BIOS shortcuts, temporary-file cleanup, drive identification, dark mode, startup initialization, notifications, video and motherboard drivers, program updates, and Rainmeter. Exact availability and behavior depend on the catalog and operating system. Inspect both the platform JSON entry and its implementation before adding or invoking a task.

### Web and local history features

`core-app/lib/web` monitors connectivity and can run a local HTTP server that exposes history JSON to the companion website. The server binds to `127.0.0.1` by default and searches ports in the 9900 range. `PROGRAMS_MANAGER_SITE_URL` and `PROGRAMS_MANAGER_SITE_FALLBACK_URL` are read from the process environment to choose the website URLs; they are not read from `.env` automatically. See [Configuration and `.env`](docs/CONFIGURATION.md) for the distinction.

## Catalog format and maintenance

Program catalogs are JSON arrays. Each entry needs a display name, a package identifier, an operation type, and a checkbox state. The optional `version` field pins the requested package version when supported by the package manager.

```json
[
  {
    "name": "Example App",
    "id": "Publisher.Package",
    "type": "install",
    "checkbox": false,
    "version": "1.2.3"
  }
]
```

Use an identifier accepted by the target system: a WinGet package ID in the Windows catalog or an apt package name in the Linux catalog. Keep the equivalent catalogs under `core-app/system/windows/json/` and `core-app/system/linux/json/` consistent where the software is available on both platforms. The UI requests the catalog file whose basename matches the category configured in `core-app/lib/screens/options`.

Function catalogs use the same list/check-box pattern, with `type` set to `function` and `id` set to the implementation identifier. To add a function, implement it in `core-app/lib/functions/`, add an entry to the appropriate platform `functions.json`, and ensure the function resolver can locate it. Do not place shell commands or executable code in catalog JSON; JSON entries are inputs consumed by application code.

Validate JSON syntax before committing catalog changes. The current app fetches catalog files from the selected GitHub branch at runtime, so source changes must be pushed to that branch before a published application sees them.

## Configuration and `.env`

See the dedicated [Configuration and `.env` guide](docs/CONFIGURATION.md) for the supported keys, parsing rules, examples, launcher variables, and troubleshooting.

## Workflows

- `.github/workflows/build-core-app.yml` builds platform artifacts when relevant files change on configured branches, for pull requests, or when manually dispatched.
- `.github/workflows/release.yml` packages successful workflow artifacts into GitHub Releases. Its allowed branch names should be checked against the build workflow when changing release channels.
- `.github/workflows/run-raw.yml` downloads and executes launchers on Windows and Linux runners on demand.

## Local files and logs

The application creates its data directory at `Documents/Programs Manager` (using the Windows Documents registry location when available). Its JSON helper can write user data there. The web module reads or creates `historic.json` in that directory for history sharing. The logger writes `log.log` relative to the application's current working directory.

The root `.env` is ignored by Git. Do not commit credentials or other secrets in it. The configuration guide contains safe templates for the supported repository settings.

## License

See [LICENSE](LICENSE).
