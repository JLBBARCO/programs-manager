param(
    [Parameter(Mandatory = $true)]
    [string]$Version,
    [string]$Publisher = "JLBBARCO",
    [string]$PackageIdentifier = "JLBBARCO.PasswordsManager",
  [string]$InstallerUrl = "",
  [string]$ReleaseTag = ""
)

$ErrorActionPreference = "Stop"

function Get-DefaultReleaseTag {
  param(
    [string]$InputVersion,
    [string]$InputTag
  )

  if ($InputTag) {
    return $InputTag
  }

  if ($InputVersion -match '^beta') {
    return $InputVersion
  }

  return "v$InputVersion"
}

function Download-InstallerWithRetry {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Url,
    [Parameter(Mandatory = $true)]
    [string]$OutputFile,
    [int]$MaxAttempts = 4
  )

  $headers = @{
    'User-Agent' = 'passwords-manager-winget-bootstrap'
    'Accept' = 'application/octet-stream'
  }

  for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
    try {
      Write-Host "Download attempt $attempt/$MaxAttempts" -ForegroundColor DarkCyan
      Invoke-WebRequest -Uri $Url -OutFile $OutputFile -Headers $headers -UseBasicParsing -TimeoutSec 120
      if ((Test-Path $OutputFile) -and ((Get-Item $OutputFile).Length -gt 0)) {
        return
      }
      throw "Downloaded file is empty"
    }
    catch {
      if ($attempt -eq $MaxAttempts) {
        throw
      }
      Start-Sleep -Seconds (2 * $attempt)
    }
  }
}

# Improve compatibility with older PowerShell defaults on Windows.
try {
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls11
}
catch {
  # Ignore when the host does not expose these values.
}

$resolvedReleaseTag = Get-DefaultReleaseTag -InputVersion $Version -InputTag $ReleaseTag
$fixedInstallLocation = 'C:\File Programs (x86)\Passwords Manager'

if (-not $InstallerUrl) {
  $InstallerUrl = "https://github.com/JLBBARCO/passwords-manager/releases/download/$resolvedReleaseTag/passwords-manager-windows-installer.exe"
}

Write-Host "Downloading installer to calculate SHA256..." -ForegroundColor Yellow
$tempRoot = if ($env:TEMP) { $env:TEMP } elseif ($env:RUNNER_TEMP) { $env:RUNNER_TEMP } else { [System.IO.Path]::GetTempPath() }
$tempFile = Join-Path $tempRoot ("passwords-manager-installer-" + $Version + ".exe")
try {
  Download-InstallerWithRetry -Url $InstallerUrl -OutputFile $tempFile
}
catch {
  Write-Error "Failed to download installer from '$InstallerUrl'. Verify that release/tag '$resolvedReleaseTag' exists and includes passwords-manager-windows-installer.exe."
  throw
}

$sha256 = (Get-FileHash -Path $tempFile -Algorithm SHA256).Hash
Remove-Item -Force $tempFile

$manifestRoot = Join-Path $PSScriptRoot "..\packaging\winget\$Version"
New-Item -ItemType Directory -Path $manifestRoot -Force | Out-Null

$versionManifest = @"
PackageIdentifier: $PackageIdentifier
PackageVersion: $Version
DefaultLocale: en-US
ManifestType: version
ManifestVersion: 1.6.0
"@

$installerManifest = @"
PackageIdentifier: $PackageIdentifier
PackageVersion: $Version
InstallerType: inno
Scope: machine
InstallModes:
  - interactive
  - silent
InstallerSwitches:
  Silent: /VERYSILENT /NORESTART /SUPPRESSMSGBOXES
  SilentWithProgress: /SILENT /NORESTART /SUPPRESSMSGBOXES
  Custom: /VERYSILENT /NORESTART /SUPPRESSMSGBOXES /DIR="$fixedInstallLocation"
InstallLocationRequired: true
AppsAndFeaturesEntries:
  - DisplayName: Passwords Manager
    Publisher: $Publisher
    InstallLocation: $fixedInstallLocation
Installers:
  - Architecture: x64
    InstallerUrl: $InstallerUrl
    InstallerSha256: $sha256
ManifestType: installer
ManifestVersion: 1.6.0
"@

$localeManifest = @"
PackageIdentifier: $PackageIdentifier
PackageVersion: $Version
PackageLocale: en-US
Publisher: $Publisher
PublisherUrl: https://github.com/JLBBARCO
PackageName: Passwords Manager
PackageUrl: https://github.com/JLBBARCO/passwords-manager
License: MIT
LicenseUrl: https://github.com/JLBBARCO/passwords-manager/blob/main/LICENSE
ShortDescription: Password manager with encrypted local storage.
Description: Manage and generate passwords with encrypted local storage under LocalAppData.
Moniker: passwords-manager
ReleaseNotesUrl: https://github.com/JLBBARCO/passwords-manager/releases/tag/$resolvedReleaseTag
ManifestType: defaultLocale
ManifestVersion: 1.6.0
"@

Set-Content -Path (Join-Path $manifestRoot "$PackageIdentifier.yaml") -Value $versionManifest -Encoding UTF8
Set-Content -Path (Join-Path $manifestRoot "$PackageIdentifier.installer.yaml") -Value $installerManifest -Encoding UTF8
Set-Content -Path (Join-Path $manifestRoot "$PackageIdentifier.locale.en-US.yaml") -Value $localeManifest -Encoding UTF8

Write-Host "Winget manifests generated at: $manifestRoot" -ForegroundColor Green
Write-Host "Next step: open a PR in microsoft/winget-pkgs with these 3 files." -ForegroundColor Cyan
