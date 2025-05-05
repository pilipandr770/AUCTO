@echo off
echo === Polygon Token Project Starter ===

:: Activate virtual environment
echo Активую віртуальне середовище...
call ..\venv\Scripts\activate.bat

:: -------------------- Розгортання контракту --------------------
echo.
echo === Розгортання контракту (online/offline) ===
python scripts/deploy_polygon_token.py --offline

:: -------------------- Купівля токенів --------------------
echo.
echo === Купівля токенів ===
python scripts/buy_tokens.py --offline

:: -------------------- Управління whitelist --------------------
echo.
echo === Управління whitelist ===
python scripts/whitelist_manage.py --offline

:: -------------------- Airdrop токенів --------------------
echo.
echo === Airdrop токенів ===
python scripts/airdrop.py --offline

:: -------------------- Перевірка знижки --------------------
echo.
echo === Перевірка знижки ===
python scripts/check_discount.py --offline

echo.
echo === Усі скрипти завершено ===
pause
