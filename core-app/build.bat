@echo off
setlocal
pushd "%~dp0\.."

echo Cleaning old builds...
rd /s /q dist build 2>nul
del /f /q "Programs Manager.spec" 2>nul

echo Installing required dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Starting build with PyInstaller...
python -m PyInstaller --noconfirm --clean --onedir --windowed ^
    --name "Programs Manager" ^
    --icon "core-app\assets\icons\icon.ico" ^
    --paths "core-app" ^
    --paths "." ^
    --add-data "core-app\lib;lib" ^
    --add-data "core-app\assets;assets" ^
    --add-data "core-app\system;system" ^
    --collect-all customtkinter ^
    --collect-all psutil ^
    --noupx ^
    "core-app\main.py"

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    popd
    exit /b 1
)

echo Build completed successfully!
echo Executable is at: dist\Programs Manager\
if not defined CI pause
popd
endlocal