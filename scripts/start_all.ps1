# scripts/start_all.ps1

Write-Host "=== Polygon Token Project Starter ==="

# Activate virtual environment
Write-Host "Активую віртуальне середовище..."
. ../venv/Scripts/Activate.ps1

# -------------------- Розгортання контракту --------------------

Write-Host "`n=== Розгортання контракту (online/offline) ==="
python ./scripts/deploy_polygon_token.py --offline

# -------------------- Купівля токенів --------------------

Write-Host "`n=== Купівля токенів ==="
python ./scripts/buy_tokens.py --offline

# -------------------- Управління whitelist --------------------

Write-Host "`n=== Управління whitelist ==="
python ./scripts/whitelist_manage.py --offline

# -------------------- Airdrop токенів --------------------

Write-Host "`n=== Airdrop токенів ==="
python ./scripts/airdrop.py --offline

# -------------------- Перевірка знижки --------------------

Write-Host "`n=== Перевірка знижки ==="
python ./scripts/check_discount.py --offline

Write-Host "`n=== Усі скрипти завершено ==="
pause
