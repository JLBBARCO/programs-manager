# Programs Manager

A Python desktop application for installing and removing programs and performing system maintenance tasks. The interface uses CustomTkinter, and program catalogs are JSON files organized by operating system.

## Platforms and requirements

- Windows: Python 3.12 to run from source; `winget` to install or remove programs.
- Linux: Python 3.12, Tkinter, and `apt`; installation and removal use `sudo`.
- The interface fetches catalogs published on GitHub and needs an internet connection to load them and check for updates. The launcher downloads published releases.

The application recognizes Windows and Linux as supported platforms. The Bash launcher also includes macOS shortcut logic, but the application does not provide a catalog or full functional support for macOS.

## Running the application

### Use a published release

On Windows, in PowerShell:

```powershell
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.ps1 | iex
```

On Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.sh | bash
```

The launcher installs or updates the application in `~/.programs-manager` (Linux) or `%USERPROFILE%\.programs-manager` (Windows), then starts the executable. To select a version, set `AIP_VERSION` before running the launcher, with or without the leading `v`. To fetch prereleases, use the `develop` branch through `AIP_BRANCH=develop` (Linux) or `$env:AIP_BRANCH = 'develop'` (PowerShell). The website also lists commands for the `beta` channel, while the current build and release workflows use `main` and `beta` differently; make sure a release exists for the selected channel.

### Run from source

From the repository root:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python core-app/main.py
```

On Linux, also install your distribution's Tkinter package (for example, `python3-tk` on Ubuntu). On Windows, make sure `winget` is available to install or remove programs.

### Build the application

Run the build scripts from the repository root:

```powershell
core-app\build.bat
```

```bash
core-app/build.sh
```

The output is written to `dist/Programs Manager/`. The scripts install the dependencies from `requirements.txt` and use PyInstaller in one-directory (`onedir`) mode. The `Build Multi-Platform Core App` workflow packages Windows x64/x86 and Linux x64 builds and generates SHA-256 checksums.

## Using the interface

1. Choose **Install**, **Uninstall**, or **Functions**.
2. Select the desired options and press **Run**.
3. The progress screen processes the selections in order. Errors for one option are logged and do not prevent later options from running.

On Windows, program installation and removal call `winget`. On Linux, they use `sudo apt install/remove`; administrative access may be requested in the terminal. Utility functions may change system settings, so review the code for a function before running it.

## Repository structure

```text
core-app/
  main.py                      Application entry point
  lib/                         Interface, catalogs, package operations, functions, and utilities
  system/{windows,linux}/json/ Platform-specific program and function catalogs
  run.ps1, run.sh              Download, update, and launch the application
  build.bat, build.sh          Local PyInstaller builds
src/lib/                       Application shortcut helpers
website/client/                Static page with launcher instructions
.github/workflows/             Build, release, and launcher workflows
requirements.txt               Pinned Python dependencies
```

### How it works

- `core-app/main.py` creates the window, configures CustomTkinter, and attempts to create shortcuts.
- `core-app/lib/screens/options` fetches JSON files from `core-app/system/<platform>/json/` and displays their options.
- `core-app/lib/screens/progress` processes the selection; `lib/install` and `lib/uninstall` invoke the platform's package manager.
- `core-app/lib/functions` resolves and calls local routines listed in the `functions.json` catalog.
- `core-app/lib/web` contains connectivity checks and history sharing/viewing features.
- `core-app/lib/config.py` optionally reads `.env`: `DEVELOPER=true` enables `BRANCH` to select the branch used to fetch catalogs; otherwise, it uses `main`.

### JSON catalogs

Each program catalog is a list of objects with `name`, `id`, `type`, and `checkbox`; `version` is optional. For example:

```json
[
  {
    "name": "Example",
    "id": "Publisher.Package",
    "type": "install",
    "checkbox": false
  }
]
```

The `id` must match an identifier accepted by the package manager (a WinGet ID on Windows or an apt package on Linux). The platform catalogs are in `core-app/system/windows/json/` and `core-app/system/linux/json/`. To add a function, implement it under `core-app/lib/functions/` and add its `id` to the platform's function JSON catalog.

## Workflows

- `build-core-app.yml`: builds multi-platform packages on monitored pushes and pull requests, and when run manually.
- `release.yml`: publishes successful build artifacts as GitHub releases.
- `run-raw.yml`: runs the launchers on Windows and Linux runners on demand.

## Local data and logs

The application stores runtime data in the user's Documents folder under `Programs Manager`, as configured in `core-app/lib/find_folders`. The logger also writes `log.log` to the current working directory. `.env` is ignored by Git; do not put secrets in it. The documented settings (`DEVELOPER` and `BRANCH`) are read by `core-app/lib/config.py`.

## License

See [LICENSE](LICENSE).
