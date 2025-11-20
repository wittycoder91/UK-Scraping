@echo off
echo Starting Chrome with remote debugging enabled...
echo.

REM Try common Chrome installation paths
set CHROME_PATH=""

if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else (
    echo Chrome not found in default locations.
    echo Please edit this batch file and set CHROME_PATH to your Chrome installation.
    pause
    exit /b 1
)

REM Create temp directory if it doesn't exist
if not exist "C:\temp\chrome_debug" mkdir "C:\temp\chrome_debug"

REM Start Chrome with remote debugging
start "" %CHROME_PATH% --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_debug"

echo.
echo Chrome started with remote debugging on port 9222
echo You can now navigate to the DVSA website and run the Python script.
echo.
pause

