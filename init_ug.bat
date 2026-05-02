@echo off

REM ===============================
REM VARIABLES ENVIRONNEMENT
REM ===============================
set DB_HOST=dpg-d731ru6uk2gs73e8cag0-a.oregon-postgres.render.com
set DB_PORT=5432
set DB_NAME=syscadof
set DB_USER=syscadof_user
set DB_PASSWORD=zAg9wpsLt0JY4n1o7jMm7hrWkvnIMdvD

REM ===============================
REM EXECUTION SCRIPT
REM ===============================
echo Lancement de l'initialisation de la base...
python init_ug.py

echo.
echo Terminé.
pause