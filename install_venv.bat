@echo off
setlocal enabledelayedexpansion

REM ===============================
REM INSTALL_VENV.BAT - VERSION PRO SECURISEE
REM ===============================

cd /d C:\SYSCADOF_RENDER

echo ===============================
echo Verification Python 3.11...
echo ===============================

py -3.11 --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] Python 3.11 non detecte. Installation...
    winget install --id Python.Python.3.11 -e --source winget

    IF %ERRORLEVEL% NEQ 0 (
        echo [ERREUR] Echec installation Python
        pause
        exit /b 1
    )
) ELSE (
    echo [OK] Python 3.11 detecte.
)

echo ===============================
echo Creation environnement virtuel...
echo ===============================

py -3.11 -m venv venv
IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Creation venv echouee
    pause
    exit /b 1
)

echo ===============================
echo Activation environnement...
echo ===============================

call venv\Scripts\activate.bat
IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Activation venv echouee
    pause
    exit /b 1
)

echo ===============================
echo Mise a jour pip...
echo ===============================

python -m pip install --upgrade pip setuptools wheel
IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Mise a jour pip echouee
    pause
    exit /b 1
)

echo ===============================
echo Installation numpy (etape critique)...
echo ===============================

pip install numpy==1.26.4 --default-timeout=1000
IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Installation numpy echouee
    pause
    exit /b 1
)

echo ===============================
echo Installation dependances...
echo ===============================

pip install --only-binary=:all: -r requirements.txt --default-timeout=1000
IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Installation requirements echouee
    pause
    exit /b 1
)

echo ===============================
echo [SUCCESS] Installation terminee avec succes !
echo ===============================

pause
exit /b 0