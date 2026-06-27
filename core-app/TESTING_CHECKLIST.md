# Testing Checklist - Programs Manager

## Prerequisites

- Python 3.12 or newer
- Project dependencies installed with `python -m pip install -r requirements.txt`
- A Windows or Linux machine for the matching build script

## Smoke tests

- Start the application with `python core-app/main.py`.
- Confirm the first screen opens with the detected operating system in the title.
- Select entries and confirm the second screen opens.
- Confirm the selected entries are separated into install, uninstall, and function groups.
- Run the flow and confirm the log server starts on a `99xx` port.
- Confirm the website opens with `?port=NNNN`.

## Execution order

- Uninstall actions run first.
- Function actions run second.
- Install actions run last.

## Build verification

- Windows: `build-compilers/build.bat`
- Linux: `build-compilers/build.sh`

Expected results:

- Windows produces `dist/Programs Manager/Programs Manager.exe`.
- Linux produces `dist/Programs Manager/Programs Manager`.

## Launcher verification

- Windows: `run.ps1`
- Linux: `run.sh`

Expected results:

- Local builds are used first when present.
- The scripts fall back to release downloads when no local build is found.
- The branch override selects prerelease assets when `AIP_BRANCH` or `SCRIPT_BRANCH` is set to `develop`.

## Documentation checks

- `README.md` matches the Python application flow.
- `QUICKSTART.md` does not mention npm or Vite.
- `ARCHITECTURE.md` describes the Python modules and runtime flow.

## Final sign-off

- The main flow handles cancelation without crashing.
- Build scripts do not block CI with interactive prompts.
- Launcher scripts start the correct binary on each platform.
