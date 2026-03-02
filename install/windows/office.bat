@echo off

echo Installing and configure Microsoft Office...
pushd "%~dp0Office"
setup.exe /configure settings.xml
set INSTALL_ERRORLEVEL=%ERRORLEVEL%
popd

IF %INSTALL_ERRORLEVEL% NEQ 0 (
    echo Failed to install Microsoft Office. Please check the error message above.
) ELSE (
    echo Microsoft Office installed successfully.
)