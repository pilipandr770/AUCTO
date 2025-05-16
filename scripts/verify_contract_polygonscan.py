# scripts/verify_contract_polygonscan.py
"""
Сценарій для автоматичної верифікації контракту на PolygonScan через API Polygonscan
"""
import os
import time
import argparse
import requests
from dotenv import load_dotenv

# Завантажуємо змінні з .env
load_dotenv()
API_KEY = os.getenv('POLYGONSCAN_API_KEY')
if not API_KEY:
    print('❌ Помилка: у файлі .env не знайдено POLYGONSCAN_API_KEY')
    exit(1)

# Парсимо аргументи
parser = argparse.ArgumentParser(description='Верифікація контракту на PolygonScan')
parser.add_argument('-a', '--address', required=True, help='Адреса деплойнутого контракту')
parser.add_argument('-s', '--source', required=True, help='Шлях до файлу з вихідним кодом (.sol)')
parser.add_argument('-n', '--name', required=True, help='Ім'я контракту (заголовок у файлі .sol, наприклад, SimpleToken)')
parser.add_argument('-c', '--compiler', required=True, help='Версія компілятора (наприклад, v0.8.0+commit.c7dfd78e)')
parser.add_argument('-o', '--opt', type=int, choices=[0,1], default=1, help='Чи увімкнено оптимізацію (1 або 0)')
parser.add_argument('-r', '--runs', type=int, default=200, help='Кількість запусків оптимізатора (runs)')
parser.add_argument('-g', '--constructor-args', default='', help='Аргументи конструктора у hex (без 0x)')
args = parser.parse_args()

# Читаємо вихідний код
try:
    with open(args.source, 'r', encoding='utf-8') as f:
        source_code = f.read()
except FileNotFoundError:
    print(f'❌ Файл не знайдено: {args.source}')
    exit(1)

# Формуємо дані для запиту
payload = {
    'apikey': API_KEY,
    'module': 'contract',
    'action': 'verifysourcecode',
    'contractaddress': args.address,
    'sourceCode': source_code,
    'codeformat': 'solidity-single-file',
    'contractname': args.name,
    'compilerversion': args.compiler,
    'optimizationUsed': str(args.opt),
    'runs': str(args.runs),
    'constructorArguements': args.constructor_args
}

# Надсилаємо запит на верифікацію
print('🔄 Надсилання запиту на верифікацію...')
response = requests.post('https://api.polygonscan.com/api', data=payload)
data = response.json()
if data.get('status') != '1':
    print('❌ Помилка під час початкової верифікації:')
    print(data.get('result'))
    exit(1)

# GUID для перевірки статусу
guid = data.get('result')
print(f'✅ GUID запиту: {guid}')

# Опитуємо API до отримання результату
print('🔄 Опитування статусу верифікації...')
while True:
    time.sleep(5)
    status_resp = requests.get('https://api.polygonscan.com/api', params={
        'apikey': API_KEY,
        'module': 'contract',
        'action': 'checkverifystatus',
        'guid': guid
    })
    status_json = status_resp.json()
    if status_json.get('status') == '1':
        print('🎉 Контракт успішно верифіковано:')
        print(status_json.get('result'))
        exit(0)
    elif status_json.get('status') == '0':
        # Статус 0 може означати як "очікування", так і помилку після перевірки
        res = status_json.get('result')
        if 'Pass - Verified' in res:
            print('🎉 Контракт успішно верифіковано:')
            exit(0)
        elif 'Fail - Unable to verify' in res:
            print('❌ Не вдалося верифікувати контракт:')
            print(res)
            exit(1)
        else:
            print('⏳ Очікування...')
    else:
        print('❌ Невідомий статус верифікації:')
        print(status_json)
        exit(1)
