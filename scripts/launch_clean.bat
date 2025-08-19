@echo off
echo FROTH FLOTATION DIGITAL TWIN - CLEAN LAUNCH
echo ================================================

echo.
echo Step 1: Stopping all existing processes...
echo -----------------------------------------
call stop_all.bat

echo.
echo Step 2: Launching the system...
echo ------------------------------
python launch_froth_flotation_system.py

echo.
echo System launch complete!
pause
