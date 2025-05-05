# scripts/whitelist_manage.py

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
    print("=== Управління білим списком (OFFLINE РЕЖИМ) ===")
    mock_data = load_mock_data()

    owner_account = mock_data["accounts"][0]

    print(f"Контракт токену: {mock_data['contract_address']}")
    print(f"Ви увійшли як власник: {owner_account}")

    print("\nПоточний стан білого списку:")
    for address, status in mock_data["whitelist"].items():
        print(f"  {address}: {'✓' if status else '✗'}")

    print("\nОберіть дію:")
    print("1. Додати адресу до білого списку")
    print("2. Видалити адресу з білого списку")
    print("3. Вийти")
    
    choice = input("Ваш вибір (1-3): ")

    if choice == "1":
        address = input("\nВведіть адресу для додавання до білого списку: ")

        if not is_valid_address(address):
            print("Неправильна адреса Ethereum.")
            return

        mock_data["whitelist"][address] = True

        with open(MOCK_DATA_PATH, "w") as file:
            json.dump(mock_data, file, indent=2)

        print(f"Адресу {address} успішно додано.")
        
    elif choice == "2":
        address = input("\nВведіть адресу для видалення з білого списку: ")

        if not is_valid_address(address):
            print("Неправильна адреса Ethereum.")
            return

        if address in mock_data["whitelist"]:
            mock_data["whitelist"][address] = False

            with open(MOCK_DATA_PATH, "w") as file:
                json.dump(mock_data, file, indent=2)

            print(f"Адресу {address} успішно видалено.")
        else:
            print("Адресу не знайдено у білому списку.")

    else:
        print("Вихід.")

def online_mode():
    print("=== Управління білим списком (ONLINE MODE Polygon) ===")

    RPC_URL = os.getenv("POLYGON_MUMBAI_RPC_URL")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")

    if not CONTRACT_ADDRESS or not RPC_URL or not PRIVATE_KEY:
        print("ERROR: Налаштуйте CONTRACT_ADDRESS, POLYGON_MUMBAI_RPC_URL та PRIVATE_KEY в .env")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not w3.is_connected():
        print("ERROR: Не вдалося підключитися до RPC")
        sys.exit(1)

    account = w3.eth.account.from_key(PRIVATE_KEY)
    abi = load_contract_abi()
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    owner = contract.functions.owner().call()

    if owner.lower() != account.address.lower():
        print("Ви не власник контракту. Доступ заборонено.")
        sys.exit(1)

    print(f"Власник контракту: {owner}")

    print("\nОберіть дію:")
    print("1. Додати адресу до білого списку")
    print("2. Видалити адресу з білого списку")
    print("3. Перевірити статус адреси")
    print("4. Вийти")

    choice = input("Ваш вибір (1-4): ")

    if choice == "1":
        address = input("\nВведіть адресу для додавання до білого списку: ")

        if not is_valid_address(address):
            print("Неправильна адреса Ethereum.")
            return

        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.addToWhitelist(address).build_transaction({
            "from": account.address,
            "gas": 100000,
            "gasPrice": w3.eth.gas_price,
            "nonce": nonce
        })

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print("Очікуємо підтвердження...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            print(f"Адресу {address} додано до білого списку!")
            print(f"Транзакція: https://mumbai.polygonscan.com/tx/{tx_hash.hex()}")
        else:
            print("Не вдалося додати адресу!")

    elif choice == "2":
        address = input("\nВведіть адресу для видалення з білого списку: ")

        if not is_valid_address(address):
            print("Неправильна адреса Ethereum.")
            return

        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.removeFromWhitelist(address).build_transaction({
            "from": account.address,
            "gas": 100000,
            "gasPrice": w3.eth.gas_price,
            "nonce": nonce
        })

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print("Очікуємо підтвердження...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            print(f"Адресу {address} видалено з білого списку!")
            print(f"Транзакція: https://mumbai.polygonscan.com/tx/{tx_hash.hex()}")
        else:
            print("Не вдалося видалити адресу!")

    elif choice == "3":
        address = input("\nВведіть адресу для перевірки: ")

        if not is_valid_address(address):
            print("Неправильна адреса Ethereum.")
            return

        status = contract.functions.whitelist(address).call()
        print("У білому списку!" if status else "НЕ у білому списку.")

    else:
        print("Вихід.")

if OFFLINE_MODE:
    offline_mode()
else:
    online_mode()
