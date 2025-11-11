@echo off
echo ========================================
echo Building Historical Fiction Generator
echo ========================================
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building with PyInstaller...
py -3.11 -m PyInstaller build_exe.spec --clean

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Copying .env file...
copy .env dist\.env >nul

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo EXE location: dist\HistoricalFictionGenerator.exe
echo.
echo To test: cd dist ^& HistoricalFictionGenerator.exe
echo.
pause
