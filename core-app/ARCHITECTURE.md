# Architecture & Implementation Guide

## Overview

Programs Manager is a Python desktop application that lets the user select package-manager actions and custom functions, then runs those actions in the background.

## Runtime flow

- Start the internet monitor.
- Show the primary screen and collect the first selection.
- Show the secondary screen if the user selected entries.
- Start the shared log server on a free port in the `9900-9999` range.
- Open the configured website with `?port=NNNN`.
- Update the package manager.
- Run uninstall actions.
- Run function actions.
- Run install actions.
- Stop services and finalize notifications.

## Main modules

- `main.py` orchestrates startup and background execution.
- `lib/system` detects the operating system.
- `lib/web` manages the internet monitor, log server, and website launch.
- `lib/functions` resolves and runs custom functions.
- `lib/install` executes installs.
- `lib/uninstall` executes uninstalls.
- `lib/updates` updates the package manager.
- `lib/screen_primary` and `lib/screen_secondary` implement the UI screens.
- `system/<os>/json` stores runtime JSON files.

## Data and packaging

- JSON data is loaded at runtime from `system/<os>/json`.
- The build artifacts intentionally exclude `system/` because the JSON files are fetched from GitHub RAW when the app runs.
- The build scripts create platform-specific PyInstaller outputs.

## Notes

- The repository is not a React, Vite, or TypeScript web app.
- Documentation that mentions `npm`, `client/src`, or browser-based log rendering is outdated.
