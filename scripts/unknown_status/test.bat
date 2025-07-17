@echo off
echo [TEST] Starting test batch file...
echo [TEST] Current directory: %CD%
echo [TEST] Script location: %~dp0
echo [TEST] Parent directory: %~dp0..

REM Change to the project root (parent of this script)
cd /d %~dp0..

echo [TEST] After cd, current directory: %CD%
echo [TEST] Testing if we can call functions...

REM Test function call
call :test_function
echo [TEST] Function call completed

echo [TEST] Test completed successfully!
pause
exit /b 0

:test_function
echo [TEST] Function executed successfully!
goto :eof 