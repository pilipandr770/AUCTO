# scripts/sign_message.py
"""
Скрипт для підпису повідомлення і отримання hex-підпису (signature hash) для підтвердження права власності на Polygonscan.
Використовує web3.py та eth-account.
"""
import os
import sys
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct

# Завантажуємо змінні з .env
load_dotenv()
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
MESSAGE_TEXT = os.getenv('MESSAGE_TEXT')

if not PRIVATE_KEY:
    print('❌ Помилка: не знайдено PRIVATE_KEY у .env')
    sys.exit(1)
if not MESSAGE_TEXT:
    print('❌ Помилка: не знайдено MESSAGE_TEXT у .env. Скопіюйте туди текст з поля "Сообщение" на Polygonscan')
    sys.exit(1)

# Формуємо повідомлення для підпису
message = encode_defunct(text=MESSAGE_TEXT)
# Отримуємо підпис
signed = Account.sign_message(message, private_key=PRIVATE_KEY)
# Виводимо hex-підпис
print('Signature (hex):', signed.signature.hex())
