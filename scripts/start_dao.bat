@echo off
chcp 65001 >nul

REM Перейти у папку app
cd /d "%~dp0..\..\app"

REM === DAO Tools Starter ===
echo === DAO Tools Starter ===

REM Активуємо віртуальне середовище
echo Активуємо venv...
call venv\Scripts\activate.bat

:menu
echo.
echo ==== Дії ====
echo 1. Розгорнути DAO контракт
echo 2. Голосування (dao_vote.py)
echo 3. Вийти
set /p choice=Введіть номер опції (1-3): 

if "%choice%"=="1" (
    python scripts\deploy_dao.py
    goto menu
) else if "%choice%"=="2" (
    python scripts\dao_vote.py
    goto menu
) else if "%choice%"=="3" (
    echo Вихід...
    exit /b
) else (
    echo Невірний вибір!
    goto menu
)
