@echo off
echo Starting update of all installed applications...
winget update --all
echo Update process completed.
echo.

echo Starting installation applications...
echo.

call :install "Google Chrome" "Google.Chrome"
call :install "Mozilla FireFox" "9NZVDKPMR9RD"
call :install "VLC" "XPDM1ZW6815MQM"
call :install "WinRAR" "RARLab.WinRAR"
call :install "WhatsApp" "9NKSQGP7F2NH"
call :install "Telegram Desktop" "Telegram.TelegramDesktop"
call :install "HP Smart" "9WZDNCRFHWLH"
call :install "Spotify" "9NCBCSZSJRSB"
call :install "Microsoft PC Manager" "9PM860492SZD"
call :install "Proton VPN" "Proton.ProtonVPN"
call :install "Google Quick Share" "Google.QuickShare"
call :install "LinkedIn" "9WZDNCRFJ4Q7"
call :install "Google Drive" "Google.GoogleDrive"
call :install "Warp VPN" "Cloudflare.Warp"

goto :eof

:install
set NAME=%~1
set ID=%~2
echo Installing %NAME%...
winget install %ID% --accept-source-agreements --accept-package-agreements
set INSTALL_ERROR=%ERRORLEVEL%

if %INSTALL_ERROR% EQU 0 (
    echo [SUCCESS] %NAME% Installed or updated successfully!
) else if %INSTALL_ERROR% EQU -1978335189 (
    echo [INFO] %NAME% It's already installed and there are no updates available.
) else (
    echo [ERROR] Failed to install or update %NAME%. Code: %INSTALL_ERROR%
)
echo.
goto :eof