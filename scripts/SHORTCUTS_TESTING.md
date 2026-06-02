# Shortcut Validation & Testing

This directory contains scripts to validate and test the automatic shortcut creation feature for Passwords Manager on first run.

## Files

### `validate_shortcuts.py`

Validates that shortcuts exist after app startup. Supports all platforms.

**Usage:**

```bash
python scripts/validate_shortcuts.py
```

**Output:**

- On Windows: Checks for `Passwords Manager.lnk` in Start Menu and Desktop
- On Linux: Checks for `passwords-manager.desktop` in `~/.local/share/applications`
- On macOS: Checks for `Passwords Manager.command` in `~/Applications`

**Exit codes:**

- `0`: All shortcuts validated successfully
- `1`: One or more shortcuts missing or invalid

### `test-shortcuts-integration.sh` (Linux/macOS)

Integration test that runs the app and validates shortcut creation.

**Usage:**

```bash
chmod +x scripts/test-shortcuts-integration.sh
scripts/test-shortcuts-integration.sh          # Run test
scripts/test-shortcuts-integration.sh --cleanup # Run test and cleanup shortcuts after
```

**What it does:**

1. Removes any existing shortcuts
2. Runs the app for 3 seconds (creates shortcuts on startup)
3. Validates shortcuts were created
4. Optionally cleans up

### `test-shortcuts-integration.ps1` (Windows)

Integration test for Windows (PowerShell).

**Usage:**

```powershell
# Run test
.\scripts\test-shortcuts-integration.ps1

# Run test and cleanup shortcuts after
.\scripts\test-shortcuts-integration.ps1 -Cleanup
```

**What it does:**

1. Runs the app for 3 seconds (creates shortcuts on startup)
2. Validates shortcuts in Start Menu and Desktop
3. Optionally cleans up

## CI/CD Integration

A dedicated GitHub Actions workflow already exists at [`.github/workflows/test-shortcuts.yml`](.github/workflows/test-shortcuts.yml) that:

- **Runs on every push/PR** to `main` and `develop` branches
- **Runs on all platforms**: Windows, Linux, macOS
- **Tests shortcut creation** on first app run
- **Validates** that shortcuts exist and are properly configured
- **Cleans up** test shortcuts after validation

The workflow is triggered when changes are made to:

- `src/lib/shortcuts/`
- `src/lib/app/`
- `main.py`
- Any shortcut test script or the workflow itself

### Manual Integration

To add shortcut validation to existing workflows:

```yaml
- name: Validate shortcuts (Linux/macOS)
  if: runner.os != 'Windows'
  run: chmod +x scripts/test-shortcuts-integration.sh && scripts/test-shortcuts-integration.sh

- name: Validate shortcuts (Windows)
  if: runner.os == 'Windows'
  run: .\scripts\test-shortcuts-integration.ps1
```

Or use just the validator:

```yaml
- name: Validate shortcuts creation
  run: python scripts/validate_shortcuts.py
```

## Behavior by Platform & Installation Type

### Windows

- **Winget**: App creates/updates Start Menu shortcut on startup
- **Portable**: App creates shortcuts on first run at startup
- **Pre-compiled**: Shortcuts created at first run

**Shortcut locations:**

- Start Menu: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\`
- Desktop: `%USERPROFILE%\Desktop\`

### Linux

- **Package (Homebrew)**: Package post_install hook creates `.desktop`
- **Portable**: App creates `.desktop` on first run at startup
- **Pre-compiled**: Shortcuts created at first run

**Shortcut location:**

- `~/.local/share/applications/passwords-manager.desktop`

### macOS

- **Package (Homebrew)**: Package post_install hook creates `.command` launcher
- **Portable**: App creates `.command` launcher on first run at startup
- **Pre-compiled**: Shortcuts created at first run

**Shortcut location:**

- `~/Applications/Passwords Manager.command`

## Troubleshooting

### Shortcuts not created

1. Verify app is running as compiled binary (`sys.frozen == True`)
2. Check permissions: Python process must have write access to target directories
3. Inspect `ensure_platform_shortcuts_best_effort()` in `src/lib/shortcuts/__init__.py`

### Permission errors on Linux/macOS

- Ensure `~/.local/share/applications` or `~/Applications` directories exist
- Check directory ownership and permissions
- Run `python scripts/validate_shortcuts.py` for detailed diagnostics

### Windows Start Menu permissions

- Usually requires UAC elevation to write system Start Menu
- Falls back to user Start Menu (`%APPDATA%\...`)
- Check environment variables `APPDATA` and `USERPROFILE` are set

## Architecture

The shortcut creation logic:

1. **Runtime detection**: `src/lib/shortcuts/__init__.py` checks if running as frozen binary
2. **Platform detection**: Uses `os.name`, `sys.platform` to determine OS
3. **Safe execution**: `ensure_platform_shortcuts_best_effort()` catches all exceptions
4. **Called at app startup**: In `main.py` before app GUI launches
5. **Winget startup path**: `_is_running_from_winget_package()` ensures Start Menu shortcut and opens app directly

## API Reference

```python
from src.lib.shortcuts import ensure_platform_shortcuts_best_effort

# This is called automatically at app startup
# Returns [] if running as script or on error
created_shortcuts = ensure_platform_shortcuts_best_effort()
```

For manual invocation or testing:

```python
from src.lib.shortcuts import ensure_platform_shortcuts
# Raises exception on error
shortcuts = ensure_platform_shortcuts()
```
