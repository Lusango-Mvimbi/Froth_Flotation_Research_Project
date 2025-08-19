@echo off
echo Stopping all Python and Node.js processes...
echo ================================================

echo Stopping Python processes...
taskkill /f /im python.exe 2>nul
if %errorlevel% equ 0 (
    echo All Python processes stopped
) else (
    echo No Python processes were running
)

echo Stopping Node.js processes...
powershell -Command "Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force"
if %errorlevel% equ 0 (
    echo All Node.js processes stopped
) else (
    echo No Node.js processes were running
)

echo.
echo Waiting for processes to terminate...
timeout /t 3 /nobreak >nul

echo.
echo Checking remaining processes...
tasklist /fi "imagename eq python.exe" 2>nul | find "python.exe" >nul
if %errorlevel% equ 0 (
    echo Warning: Some Python processes may still be running
) else (
    echo All Python processes stopped
)

tasklist /fi "imagename eq node.exe" 2>nul | find "node.exe" >nul
if %errorlevel% equ 0 (
    echo Warning: Some Node.js processes may still be running
) else (
    echo All Node.js processes stopped
)

echo.
echo Cleanup complete!
pause
