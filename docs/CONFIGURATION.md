# Configuration and `.env`

This guide describes the repository-root `.env` file read by `core-app/lib/config.py`, as well as related process environment variables that are often confused with it.

## What the `.env` file controls

When running from the source checkout, the application looks for `.env` at the repository root. It reads the file directly; it does not use `python-dotenv` and does not load every entry into `os.environ`. Only these keys are used by `core-app/lib/config.py`:

| Key | Default | Meaning |
| --- | --- | --- |
| `DEVELOPER` | `false` | Enables developer mode when set to `1`, `true`, `yes`, or `on` (case-insensitive). |
| `BRANCH` | `main` | Catalog branch, used only when `DEVELOPER` is enabled. An empty value falls back to `main`. |

The application uses the selected branch when constructing raw GitHub URLs for platform catalogs. With developer mode disabled, `BRANCH` is ignored and catalogs are fetched from `main`. Developer mode also affects logging behavior in `core-app/lib/log`.

## Create or edit the file

Create a file named `.env` in the repository root, next to `README.md` and `requirements.txt`:

```dotenv
# Normal use: catalogs come from main
DEVELOPER=false
BRANCH=main
```

To load catalogs from a development branch, enable developer mode and set the branch name:

```dotenv
DEVELOPER=true
BRANCH=develop
```

The application reads this file when the relevant configuration functions are called. Restart the application after changing the file so the new configuration is used consistently.

The root `.env` is excluded by `.gitignore` because it is intended for local settings. Keep it local and do not put credentials or secrets in it. If you need to share non-sensitive settings with contributors, document them or add a separately tracked example file; never commit a personal `.env`.

The PyInstaller build scripts do not include the repository `.env` in release artifacts. Treat this file as a source/development configuration. Release selection is controlled separately by launcher variables such as `AIP_VERSION` and `AIP_BRANCH`.

## Parsing rules

The parser is intentionally small. Use one `KEY=value` assignment per line:

- Blank lines and lines whose first non-space character is `#` are ignored.
- Key names are case-insensitive (`developer` and `DEVELOPER` are equivalent).
- Whitespace around the key and value is trimmed.
- A single pair of surrounding single or double quotes is removed from the value.
- `DEVELOPER` accepts `1`, `true`, `yes`, or `on` as true; other values are false.
- `BRANCH` is treated as a literal branch name. It is not used unless `DEVELOPER` is true.
- Do not use `export KEY=value`, inline comments, or shell interpolation. They are not interpreted by this parser.

For example, this works:

```dotenv
DEVELOPER="true"
BRANCH='feature/catalog-update'
```

This does not enable the branch setting because `export` is not supported:

```dotenv
export DEVELOPER=true
```

## Settings that are not read from `.env`

Several related options are read from the process environment by other modules or launchers. Adding these names to the root `.env` alone has no effect.

### Release launcher variables

Set these in the shell before invoking `core-app/run.ps1` or `core-app/run.sh`:

| Variable | Effect |
| --- | --- |
| `AIP_VERSION` | Requests a release by version/tag, with or without a leading `v`. |
| `AIP_BRANCH` | Selects the launcher channel. `main` is the default. The launchers recognize `develop` as the prerelease channel; other values currently follow stable-release behavior. |
| `AIP_ARCHITECTURE` | Windows PowerShell launcher only: choose `x86` to download the x86 archive; other values use x64. |

PowerShell example:

```powershell
$env:AIP_BRANCH = 'develop'
$env:AIP_VERSION = '2026.07.18.200959'
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.ps1 | iex
```

Bash example (the variables are set on the `bash` process that runs the downloaded script):

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.sh \
  | AIP_BRANCH=develop AIP_VERSION=2026.07.18.200959 bash
```

`SCRIPT_BRANCH` is a secondary fallback understood by both launchers when `AIP_BRANCH` is not set. The website may show channel commands that do not exactly match the release workflow's current allowed branch names; check the repository workflows and GitHub Releases when selecting a channel.

### Companion website URLs

`core-app/lib/web` reads `PROGRAMS_MANAGER_SITE_URL` and `PROGRAMS_MANAGER_SITE_FALLBACK_URL` from the process environment when that module is imported. These select the primary and fallback website URLs opened by the application. They are not read from `.env` automatically.

PowerShell example for a source run:

```powershell
$env:PROGRAMS_MANAGER_SITE_URL = 'https://example.org'
python core-app/main.py
```

Bash example:

```bash
PROGRAMS_MANAGER_SITE_URL=https://example.org python core-app/main.py
```

Other environment variables such as `APPDATA`, `USERPROFILE`, and `TEMP` are supplied by the operating system and used for platform paths. They are not Programs Manager `.env` settings.

## Troubleshooting

- **Catalogs still come from `main`:** confirm `DEVELOPER` is set to an accepted true value and `BRANCH` names a branch that exists in the GitHub repository.
- **A setting in `.env` has no effect:** only `DEVELOPER` and `BRANCH` are read from this file. Set launcher and website options in the process environment instead.
- **The app cannot load catalogs:** check the network connection, branch name, and that the relevant JSON catalog exists at `core-app/system/<platform>/json/` on that branch.
- **The file seems to be ignored by Git:** this is expected for `.env`. It is a local configuration file and should not be committed.
