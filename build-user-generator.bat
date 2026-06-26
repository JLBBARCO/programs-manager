@echo off
echo Cleaning old builds...
rd /s /q dist build 2>nul
del /f /q "Programs Manager User Generator.spec" 2>nul

echo Installing required dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Iniciando o Build com PyInstaller...

echo Adding install directory to bundle...
python -m PyInstaller --noconfirm --onedir --windowed ^
    --name "Programs Manager User Generator" ^
    --icon "src/assets/icon/icon.ico" ^
    --add-data "user-generator/lib;lib" ^
    --collect-all customtkinter ^
    --collect-all psutil ^
    --noupx ^
    "main.py"

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the errors above.
    exit /b 1
)

echo.
echo Build completed successfully!
echo %%%%
echo.
echo O executavel esta em: dist/Programs Manager User Generator/
echo.
if not defined CI pause
