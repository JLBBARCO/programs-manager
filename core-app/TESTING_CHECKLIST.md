# Testing Checklist - Programs Manager

## Prerequisites

- Python 3.12 or newer
- Project dependencies installed with `python -m pip install -r requirements.txt`
- A Windows or Linux machine

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

## Launcher verification

- Windows: `run.ps1`
- Linux: `run.sh`

Expected results:

- The scripts run `core-app/main.py` through Python.
- If Python 3.12 or newer is missing, the scripts install it through the platform package manager.
- The branch override selects source from that branch when `AIP_BRANCH` or `SCRIPT_BRANCH` is set.

## Documentation checks

- `README.md` matches the Python application flow.
- `QUICKSTART.md` does not mention npm or Vite.
- `ARCHITECTURE.md` describes the Python modules and runtime flow.

## Final sign-off

- The main flow handles cancelation without crashing.
- Build scripts do not block CI with interactive prompts.
- Launcher scripts start the correct binary on each platform.
