@echo off
REM ═══════════════════════════════════════════════════════════════
REM  Sticky Notes — Windows one-time build script
REM  Produces a single executable: dist\sticky_notes.exe
REM  After building, just double-click dist\sticky_notes.exe
REM ═══════════════════════════════════════════════════════════════

echo.
echo ╔══════════════════════════════════════════╗
echo ║   Sticky Notes — Windows Builder         ║
echo ╚══════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM ── Step 1: Check Python is installed ────────────────────────────────────────
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
echo        Python found.

REM ── Step 2: Install Python dependencies ──────────────────────────────────────
echo.
echo [2/3] Installing Python packages...
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q
echo        Done.

REM ── Step 3: Build executable with PyInstaller ────────────────────────────────
echo.
echo [3/3] Building executable...
pyinstaller ^
    --onefile ^
    --name "sticky_notes" ^
    --noconsole ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --hidden-import PIL.ImageTk ^
    main.py

echo.
echo ============================================================
echo  Build complete!
echo  Executable: %~dp0dist\sticky_notes.exe
echo.
echo  Run it anytime by double-clicking:
echo    dist\sticky_notes.exe
echo ============================================================
echo.
pause
