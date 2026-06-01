# Quick Start Guide

## Local setup

- Install Python 3.12 or newer.
- Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

- Run the app from source:

```bash
python main.py
```

## Build

- Windows: `build.bat`
- Linux: `build.sh`
- macOS: `build-mac.sh`

## Run

- Windows: `run.ps1`
- Linux and macOS: `run.sh`

## What to verify

- `main.py` opens the two UI screens and then runs the selected actions.
- The log server uses a free port in the `9900-9999` range.
- The website is opened with `?port=NNNN`.
- `uninstall`, `function`, and `install` entries run in that order.

## Related files

- `README.md`
- `ARCHITECTURE.md`
- `TESTING_CHECKLIST.md`
