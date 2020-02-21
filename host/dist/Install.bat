
@echo off
call :isAdmin

if %errorlevel% == 0 (
    goto :run
) else (
    echo Error: Run as administrator.
)
pause
exit /b

:isAdmin
fsutil dirty query %systemdrive% >nul
exit /b

:run
REG ADD "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "BarsPyServer" /d "%~dp0BarsPyServer.exe" /f

pause