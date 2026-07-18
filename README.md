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

## Code signing (Windows executables)

The Windows build steps in `build-core-app.yml` and `build-user-generator.yml`
can optionally sign the generated `.exe` with an Authenticode certificate.
Signing only runs if the `CODE_SIGN_PFX_BASE64` repository secret is set; if
it's empty the step is skipped and the build proceeds unsigned, as before.

To set it up with a self-signed certificate:

1. Run `.github/scripts/generate-self-signed-cert.ps1` once, locally, on
   Windows (see the comments at the top of the script for usage and output
   files).
2. Add the repository secrets `CODE_SIGN_PFX_BASE64` and
   `CODE_SIGN_PFX_PASSWORD` with the values it prints out.
3. Distribute the generated `.cer` (public certificate) file to anyone who
   needs to run the signed executables, so they can import it into their
   local "Trusted Root Certification Authorities" store, e.g.:
   ```powershell
   Import-Certificate -FilePath ".\code-signing-cert.cer" -CertStoreLocation Cert:\CurrentUser\Root
   ```

**Important:** a self-signed certificate has no chain to a publicly trusted
root CA, so Windows SmartScreen and any Application Control / WDAC policy
will still treat the executable as untrusted unless the certificate above is
explicitly imported and trusted on that machine (or an administrator adds an
allow rule for it). Signing removes the "unknown publisher" warning and lets
you verify the binary hasn't been tampered with, but it does not, by itself,
bypass an organization's Application Control policy. For that, a certificate
issued by a CA that's already trusted by the target machines (or an explicit
WDAC/AppLocker rule) is required.

## Deploy flow

- GitHub Actions builds `core-app` and `user-generator` on pushes to `main` and `develop`.
- The release workflow publishes the generated archives from those builds.
- The website is deployed through Vercel using the configuration in [website/vercel.json](website/vercel.json).

## Documentation

- [core-app/README.md](core-app/README.md)
- [user-generator/README.md](user-generator/README.md)
- [website/README.md](website/README.md)
