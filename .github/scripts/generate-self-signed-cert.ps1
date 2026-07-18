# Generates a self-signed Authenticode code-signing certificate and exports
# it as a base64-encoded .pfx, ready to be stored as GitHub Actions secrets.
#
# Run this ONCE locally (on Windows, with PowerShell) and keep the output safe.
# Re-running it creates a NEW certificate with a different thumbprint, which
# means machines that already trust the old certificate would need to trust
# the new one again. Re-use the same secrets across builds instead of
# regenerating this on every run.
#
# Usage:
#   .\generate-self-signed-cert.ps1 -SubjectName "CN=Programs Manager" -Password "choose-a-strong-password"
#
# After running, add these as GitHub repository secrets
# (Settings > Secrets and variables > Actions):
#   CODE_SIGN_PFX_BASE64   -> contents of the generated .txt file
#   CODE_SIGN_PFX_PASSWORD -> the password you chose above
#
# You should also distribute the generated .cer file (public certificate) to
# anyone who needs to run the signed executables, so they can import it into
# their local "Trusted Root Certification Authorities" (or "Trusted
# Publishers") store. Without that step, Windows will still treat the
# executable as untrusted, since a self-signed certificate has no chain to a
# publicly trusted root CA.

param(
    [string]$SubjectName = "CN=Programs Manager",
    [Parameter(Mandatory = $true)]
    [string]$Password,
    [string]$OutputDir = "."
)

$ErrorActionPreference = "Stop"

$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject $SubjectName `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -KeyUsage DigitalSignature `
    -NotAfter (Get-Date).AddYears(5) `
    -CertStoreLocation "Cert:\CurrentUser\My"

$securePassword = ConvertTo-SecureString -String $Password -Force -AsPlainText
$pfxPath = Join-Path $OutputDir "code-signing-cert.pfx"
$cerPath = Join-Path $OutputDir "code-signing-cert.cer"
$base64Path = Join-Path $OutputDir "code-signing-cert.pfx.base64.txt"

Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $securePassword | Out-Null
Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null

$bytes = [System.IO.File]::ReadAllBytes($pfxPath)
[System.Convert]::ToBase64String($bytes) | Set-Content -Path $base64Path -NoNewline

Write-Host "Certificate thumbprint: $($cert.Thumbprint)"
Write-Host ""
Write-Host "Generated files in $OutputDir :"
Write-Host "  $pfxPath          (keep private, do not commit)"
Write-Host "  $cerPath          (public certificate, share with users)"
Write-Host "  $base64Path       (paste this into the CODE_SIGN_PFX_BASE64 secret)"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Add repository secrets CODE_SIGN_PFX_BASE64 and CODE_SIGN_PFX_PASSWORD."
Write-Host "  2. Distribute $cerPath to users; they should import it into"
Write-Host "     'Trusted Root Certification Authorities' (Local Machine or Current User)"
Write-Host "     via certmgr.msc, or run:"
Write-Host "     Import-Certificate -FilePath '$cerPath' -CertStoreLocation Cert:\CurrentUser\Root"
Write-Host "  3. Delete $pfxPath and $base64Path from disk once the secrets are saved."
