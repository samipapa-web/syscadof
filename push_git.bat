@echo off
setlocal enabledelayedexpansion

REM ======================================================
REM push_git.bat - VERSION PROFESSIONNELLE ROBUSTE
REM ======================================================

REM ---------- CONFIGURATION ----------
SET USERNAME=samipapa-web
SET REPO=syscadof
SET BRANCH=main

echo ==========================================
echo        SYSCADOF - PUSH AUTOMATIQUE
echo ==========================================

REM ---------- VERIFIER DEPOT GIT ----------
git rev-parse --is-inside-work-tree >nul 2>&1
IF "%ERRORLEVEL%" NEQ "0" (
    echo [INFO] Aucun repository Git detecte. Initialisation...
    git init
) ELSE (
    echo [OK] Repository Git detecte.
)

REM ---------- AJOUT DES FICHIERS ----------
echo [INFO] Ajout des fichiers...
git add .

REM ---------- COMMIT SI NECESSAIRE ----------
git diff-index --quiet HEAD >nul 2>&1
IF "%ERRORLEVEL%" NEQ "0" (
    echo [INFO] Commit en cours...
    git commit -m "Commit automatique SYSCADOF_RENDER"
    IF "%ERRORLEVEL%" NEQ "0" (
        echo [ERREUR] Echec du commit.
        goto :error
    )
) ELSE (
    echo [OK] Aucun changement a commit.
)

REM ---------- CONFIG REMOTE ----------
git remote get-url origin >nul 2>&1
IF "%ERRORLEVEL%" NEQ "0" (
    echo [INFO] Configuration du remote origin...
    git remote add origin https://github.com/%USERNAME%/%REPO%.git
) ELSE (
    echo [OK] Remote deja configure.
)

REM ---------- BRANCHE ----------
echo [INFO] Configuration de la branche %BRANCH%...
git branch -M %BRANCH%

REM ---------- OPTIMISATION GROS DEPOTS ----------
echo [INFO] Optimisation Git pour gros fichiers...
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

REM ---------- PUSH AVEC RETRY ----------
set RETRY_COUNT=0
set MAX_RETRY=3

:push_retry
echo [INFO] Push vers GitHub (tentative !RETRY_COUNT!/%MAX_RETRY%)...
git push origin %BRANCH% --progress

IF "!ERRORLEVEL!" NEQ "0" (
    set /a RETRY_COUNT+=1
    echo [WARNING] Echec du push.

    IF !RETRY_COUNT! LSS %MAX_RETRY% (
        echo [INFO] Nouvelle tentative dans 5 secondes...
        timeout /t 5 >nul
        goto push_retry
    ) ELSE (
        echo [ERREUR] Push echoue apres plusieurs tentatives.
        goto :error
    )
) ELSE (
    echo [SUCCES] Push termine avec succes !
    goto :end
)

:error
echo ==========================================
echo        ECHEC DU PROCESSUS
echo ==========================================
pause
exit /b 1

:end
echo ==========================================
echo        OPERATION TERMINEE
echo ==========================================
pause
exit /b 0