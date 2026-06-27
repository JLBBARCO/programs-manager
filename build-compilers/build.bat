@echo off
pushd "%~dp0\.."
echo Cleaning old builds...
rd /s /q dist build 2>nul
del /f /q "Programs Manager.spec" 2>nul

echo Installing required dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Iniciando o Build com PyInstaller...

echo Adding install directory to bundle...
python -m PyInstaller --noconfirm --onedir --windowed ^
    --name "Programs Manager" ^
    --icon "src/assets/icon/icon.ico" ^
    --paths "core-app" ^
    --add-data "core-app/lib;lib" ^
    --add-data "core-app/system;system" ^
    --add-data "src;src" ^
    --collect-all customtkinter ^
    --collect-all psutil ^
    --noupx ^
    "core-app/main.py"

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the errors above.
    popd
    exit /b 1
)

echo.
echo Build completed successfully!
echo %%%%
echo.
echo O executavel esta em: dist/Programs Manager/
echo.
if not defined CI pause
popd
