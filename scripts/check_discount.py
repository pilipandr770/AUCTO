# scripts/check_discount.py

import os
import sys
import json
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

OFFLINE_MODE = "--offline" in sys.argv
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
MOCK_DATA_PATH = "./mock_data.json"
CONTRACT_ABI_PATH = "./contracts/abi.json"

def load_contract_abi():
    with open(CONTRACT_ABI_PATH, "r") as file:
        return json.load(file)

def load_mock_data():
    with open(MOCK_DATA_PATH, "r") as file:
        return json.load(file)

def is_valid_address(address):
    return Web3.is_address(address)

def offline_mode():
    print("=== Перевірка знижок (OFFLINE РЕЖИМ) ===")

    mock_data = load_mock_data()

    print("Поточний whitelist:")
    for address, status in mock_data["whitelist"].items():
        discount = "50%" if status else "0%"
        print(f"{address} -> {discount}")

    address = input("\nВведіть адресу для перевірки: ")

    if not is_valid_address(address):
        print("Невірна адреса Ethereum.")
        return

    status = mock_data["whitelist"].get(address, False)

    if status:
        print(f"Адреса {address} має знижку 50% (у білому списку).")
    else:
        print(f"Адреса {address} не у білому списку. Знижка 0%.")

def online_mode():
    print("=== Перевірка знижок (ONLINE Polygon) ===")

    RPC_URL = os.getenv("POLYGON_MUMBAI_RPC_URL")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")

    if not CONTRACT_ADDRESS or not RPC_URL:
        print("ERROR: CONTRACT_ADDRESS або POLYGON_MUMBAI_RPC_URL не встановлені в .env")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not w3.is_connected():
        print("ERROR: Не вдалося підключитися до мережі.")
        sys.exit(1)

    abi = load_contract_abi()
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    address = input("Введіть адресу для перевірки знижки: ")

    if not is_valid_address(address):
        print("Невірна адреса Ethereum.")
        return

    try:
        discount_rate = contract.functions.getDiscountRate(address).call()
        if discount_rate > 0:
            print(f"Адреса {address} має знижку {discount_rate / 100}%")
        else:
            print(f"Адреса {address} не має знижки.")
    except Exception as e:
        print(f"Помилка при отриманні знижки: {e}")

if OFFLINE_MODE:
    offline_mode()
else:
    online_mode()
