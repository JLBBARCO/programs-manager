# core-app — Programs Manager (desktop app)

Python desktop application (CustomTkinter UI) that lets a user pick package-manager
actions and custom functions, then runs them in the background while streaming a live
log to the companion website.

## Runtime flow

1. Start the internet monitor.
2. Show the primary screen (`lib/screen_primary`) — pick categories; detected OS shown
   in the title.
3. Show the secondary screen (`lib/screen_secondary`) if entries were selected — split
   into install / uninstall / function groups.
4. Start a shared log server on a free port in the `9900–9999` range.
5. Open the configured website with `?port=NNNN`.
6. Update the package manager (`lib/updates`).
7. Run actions **in this order: uninstall → function → install**.
8. Stop services and finalize notifications.

## Main modules (`lib/`)

| Module                                | Responsibility                                          |
| ------------------------------------- | ------------------------------------------------------- |
| `system`                              | Detects the operating system (Windows/Linux).           |
| `web`                                 | Internet monitor, shared log server, opens the website. |
| `functions`                           | Resolves and runs custom functions (see below).         |
| `install`                             | Executes install actions.                               |
| `uninstall`                           | Executes uninstall actions.                             |
| `updates`                             | Updates the underlying package manager.                 |
| `screen_primary` / `screen_secondary` | The two UI screens.                                     |
| `screen_other`                        | Additional/auxiliary screen logic.                      |
| `find_folders`                        | Locates relevant folders on disk.                       |
| `json`                                | Loads runtime JSON.                                     |
| `log`                                 | Logging utilities feeding the shared log server.        |

`main.py` orchestrates all of the above at startup.

### Custom functions (`lib/functions/`)

Discrete, independently invokable actions beyond simple install/uninstall, e.g.:
`bios_shortcut.py`, `clear_temp_files.py`, `correctly_internal_drive.py`,
`dark_mode.py`, `essential_programs_initialization.py`, `notifications.py`,
`rainmeter.py`, `update_programs.py`, `video_drivers.py`.

## Data and packaging

- Runtime JSON lives under `system/<os>/json/` (e.g. `essentials.json`, `games.json`,
  `developer.json`, `bloatware.json`, `customization.json`, `screen.json`,
  `initialization_whitelist.json`, `ti_tools.json` for Windows; a similar but smaller
  set for Linux, plus `server.json`).
- These JSON files are **fetched from GitHub RAW at runtime**, not bundled into the
  build:
  `https://raw.githubusercontent.com/JLBBARCO/programs-manager/<branch>/system/<os>/json/<file>.json`
- This lets the catalog of installable/removable programs be updated without a new
  release.
- Windows also has `system/windows/custom/`: a startup-programs whitelist tool
  (`list_startup_programs.py`, `white_list.txt`, `listar-startup.bat`) — see
  `WHITELIST_README.md`.

## Build & run

- Build: `core-app/build.bat` (Windows) / `core-app/build.sh` (Linux) — produce a
  PyInstaller bundle at `dist/Programs Manager/Programs Manager[.exe]`. The Windows
  script skips its final interactive pause automatically in CI.
- Run/install (auto-updating launcher, piped from GitHub raw):
  - Windows: `irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.ps1 | iex`
  - Linux: `curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.sh | bash`
  - Override branch (to pull prerelease builds): set `AIP_BRANCH=develop` (or
    `SCRIPT_BRANCH=develop`) before invoking.
- `core-app/scripts/` also contains: `generate-winget-manifest.ps1`,
  `install-unix.sh` / `uninstall-unix.sh`, screenshot generation
  (`generate_screenshots.py`, `assemble_thumbnails.py`, `ci_screenshot.py`), and shortcut
  validation/testing (`validate_shortcuts.py`,
  `test-shortcuts-integration.{ps1,sh}`, see `scripts/SHORTCUTS_TESTING.md`).

## Notes

- This project is **not** a React/Vite/TypeScript app — that's `website/`. Any
  documentation implying otherwise is outdated (see `core-app/ARCHITECTURE.md`).
- CI: `.github/workflows/build-core-app.yml` builds this project for `main` and
  `develop`; see the root spec for shared CI/CD, versioning, and code-signing details.
- Further reading already in the repo: `core-app/README.md`, `core-app/ARCHITECTURE.md`,
  `core-app/QUICKSTART.md`, `core-app/TESTING_CHECKLIST.md`.
