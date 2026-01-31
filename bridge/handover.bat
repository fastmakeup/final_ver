@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

REM ============================================================
REM   HandOverAI - Management Console v3
REM ============================================================

set "COMMAND=%~1"

if "%COMMAND%"=="" goto :main_loop

REM --- CLI Mode ---
if /i "%COMMAND%"=="dev"       goto :op_dev
if /i "%COMMAND%"=="react"     goto :op_react_build
if /i "%COMMAND%"=="build"     goto :cli_build
if /i "%COMMAND%"=="full"      goto :op_full_build
if /i "%COMMAND%"=="test"      goto :op_test
if /i "%COMMAND%"=="installer" goto :op_installer
if /i "%COMMAND%"=="help"      goto :op_help

echo [ERROR] Unknown command: %COMMAND%
echo Usage: handover.bat [dev^|react^|build^|full^|test^|installer^|help]
exit /b 1

:cli_build
set "BUILD_REACT=0"
set "CLEAN_BUILD=0"
:cli_parse
shift
if "%~1"=="" goto :cli_do_build
if /i "%~1"=="--with-react" set "BUILD_REACT=1"
if /i "%~1"=="--clean" set "CLEAN_BUILD=1"
goto :cli_parse
:cli_do_build
call :sub_build
exit /b %ERRORLEVEL%

REM ============================================================
REM   Interactive Menu
REM ============================================================
:main_loop
cls
echo ============================================================
echo   HandOverAI - Management Console
echo ============================================================
echo.
echo   [1] Dev Run          (uv run python main.py)
echo   [2] React Build      (npm run build only)
echo   [3] EXE Build        (PyInstaller, reuse cache)
echo   [4] Full Build        (uv sync + React + EXE clean)
echo   [5] Dev Test          (dev_test.py)
echo   [6] Create Installer (Inno Setup)
echo.
echo   [H] Help    [Q] Quit
echo ============================================================
set "CHOICE="
set /p CHOICE="Select: "

if /i "!CHOICE!"=="1" ( call :op_dev & goto :main_loop )
if /i "!CHOICE!"=="2" ( call :op_react_build & goto :main_loop )
if /i "!CHOICE!"=="3" ( call :op_standard_build & goto :main_loop )
if /i "!CHOICE!"=="4" ( call :op_full_build & goto :main_loop )
if /i "!CHOICE!"=="5" ( call :op_test & goto :main_loop )
if /i "!CHOICE!"=="6" ( call :op_installer & goto :main_loop )
if /i "!CHOICE!"=="h" ( call :op_help & goto :main_loop )
if /i "!CHOICE!"=="q" exit /b 0

echo [ERROR] Invalid choice.
timeout /t 1 /nobreak >nul
goto :main_loop

REM ============================================================
REM   Operations
REM ============================================================

:op_dev
echo.
echo [Dev] Starting application...
call uv run python main.py
echo.
echo [Dev] Application closed.
pause
exit /b 0

:op_react_build
echo.
echo [React] Building frontend...
call :sub_react_build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] React build failed.
    pause
    exit /b 1
)
call :sub_copy_frontend
echo [React] Done.
pause
exit /b 0

:op_standard_build
echo.
echo [Build] EXE build (reuse cache)...
set "BUILD_REACT=0"
set "CLEAN_BUILD=0"
call :sub_build
pause
exit /b 0

:op_full_build
echo.
echo [Full] Starting full build...
set "BUILD_REACT=1"
set "CLEAN_BUILD=1"
call uv sync
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] uv sync failed.
    pause
    exit /b 1
)
call :sub_build
pause
exit /b 0

:op_test
echo.
echo [Test] Running dev_test.py...
call uv run python dev_test.py
pause
exit /b 0

:op_installer
echo.
echo [Installer] Creating installer...
if not exist "dist\HandOverAI\HandOverAI.exe" (
    echo [ERROR] Build first. EXE not found.
    pause
    exit /b 1
)
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo [ERROR] Inno Setup not found at %ISCC%
    pause
    exit /b 1
)
%ISCC% installer.iss
pause
exit /b 0

:op_help
echo.
echo Usage: handover.bat [command]
echo.
echo Commands:
echo   dev        Run dev server (uv run python main.py)
echo   react      Build React frontend only
echo   build      Build EXE (options: --with-react --clean)
echo   full       Full build (uv sync + React + clean EXE)
echo   test       Run dev_test.py
echo   installer  Create Inno Setup installer
echo   help       Show this help
echo.
pause
exit /b 0

REM ============================================================
REM   Subroutines
REM ============================================================

:sub_react_build
echo   [*] Building React...
pushd fe\Make_up
if not exist "node_modules" (
    echo   [*] Installing node_modules...
    call npm install
    if !ERRORLEVEL! NEQ 0 (
        popd
        exit /b 1
    )
)
call npm run build
set "RE=%ERRORLEVEL%"
popd
exit /b %RE%

:sub_copy_frontend
echo   [*] Copying frontend to bridge_build...
if exist "bridge_build" rmdir /s /q "bridge_build"
mkdir "bridge_build"
xcopy /E /I /Y /Q "fe\Make_up\dist" "bridge_build" >nul
exit /b 0

:sub_build
echo ============================================================
echo   Building EXE
echo ============================================================

REM Kill running instance
echo   [*] Checking for running instances...
taskkill /F /IM HandOverAI.exe /T >nul 2>&1

if "%CLEAN_BUILD%"=="1" (
    echo   [*] Cleaning build cache...
    if exist dist rmdir /s /q dist
    if exist build rmdir /s /q build
)

if "%BUILD_REACT%"=="1" (
    call :sub_react_build
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] React build failed.
        exit /b 1
    )
    call :sub_copy_frontend
)

echo   [*] Running PyInstaller...
if "%CLEAN_BUILD%"=="1" (
    call uv run pyinstaller build.spec --clean
) else (
    call uv run pyinstaller build.spec
)
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller failed.
    exit /b 1
)

REM DLL copy if needed
if exist ".venv\Scripts\python311.dll" (
    if not exist "dist\HandOverAI\python311.dll" (
        copy /Y ".venv\Scripts\python311.dll" "dist\HandOverAI\" >nul
    )
)

echo   [OK] Build successful: dist\HandOverAI\HandOverAI.exe
exit /b 0
