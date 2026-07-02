# Programs Manager Monorepo

This repository combines three related projects:

- [core-app](core-app) is the desktop application launcher and packaged runtime.
- [website](website) is the Vercel-deployed log viewer.
- [user-generator](user-generator) builds the user list generator utility.

## Entry points

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.ps1 | iex
```

Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/core-app/run.sh | bash
```

User generator:

```powershell
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/user-generator/run.ps1 | iex
```

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/user-generator/run.sh | bash
```

## Deploy flow

- GitHub Actions builds `core-app` and `user-generator` on pushes to `main` and `develop`.
- The release workflow publishes the generated archives from those builds.
- The website is deployed through Vercel using the configuration in [website/vercel.json](website/vercel.json).

## Documentation

- [core-app/README.md](core-app/README.md)
- [user-generator/README.md](user-generator/README.md)
- [website/README.md](website/README.md)
