# scripts/buy_tokens.py

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
    print("=== Інструмент купівлі токенів (OFFLINE РЕЖИМ) ===")
    mock_data = load_mock_data()

    buyer_account = mock_data["accounts"][1]
    token_price = mock_data["token_price"]
    token_symbol = mock_data["token_symbol"]

    print(f"Контракт токену: {mock_data['contract_address']}")
    print(f"Використовуємо акаунт: {buyer_account}")
    print("Баланс акаунту: 100 ETH (тестове значення)")

    current_balance = mock_data["balances"].get(buyer_account, 0)
    print(f"Поточний баланс токенів: {current_balance / 10**18} {token_symbol}")

    token_price_eth = Web3.from_wei(token_price, 'ether')
    print(f"Ціна токена: {token_price_eth} ETH за токен")

    eth_to_spend = float(input("Введіть суму ETH для витрати: "))
    wei_to_spend = Web3.to_wei(eth_to_spend, 'ether')
    tokens_to_buy = wei_to_spend / token_price

    print(f"\nВи збираєтесь придбати {tokens_to_buy} {token_symbol} за {eth_to_spend} ETH")
    confirm = input("Підтвердити покупку? (y/n): ").lower()

    if confirm == 'y':
        new_balance = current_balance + (tokens_to_buy * 10**18)
        mock_data["balances"][buyer_account] = int(new_balance)

        with open(MOCK_DATA_PATH, "w") as file:
            json.dump(mock_data, file, indent=2)

        print("Покупку успішно симульовано!")
        print(f"Новий баланс токенів: {new_balance / 10**18} {token_symbol}")
    else:
        print("Покупку скасовано.")

def online_mode():
    print("=== Інструмент купівлі токенів (ONLINE MODE Polygon) ===")
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
    print("Використовується акаунт:", account.address)

    abi = load_contract_abi()
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    try:
        token_name = contract.functions.name().call()
        token_symbol = contract.functions.symbol().call()
        token_price = contract.functions.tokenPrice().call()
        decimals = contract.functions.decimals().call()

        balance_eth = w3.eth.get_balance(account.address)
        balance_formatted = w3.from_wei(balance_eth, 'ether')

        token_balance = contract.functions.balanceOf(account.address).call()
        token_balance_formatted = token_balance / 10**decimals

        print(f"Токен: {token_name} ({token_symbol})")
        print(f"Баланс акаунту: {balance_formatted} MATIC")
        print(f"Баланс токенів: {token_balance_formatted} {token_symbol}")
        print(f"Ціна токена: {w3.from_wei(token_price, 'ether')} MATIC")

        is_whitelisted = contract.functions.whitelist(account.address).call()
        print("У білому списку" if is_whitelisted else "НЕ у білому списку")

        matic_to_spend = float(input("Введіть суму MATIC для витрати: "))
        wei_to_spend = w3.to_wei(matic_to_spend, 'ether')

        if wei_to_spend > balance_eth:
            print("Недостатньо MATIC для покупки!")
            sys.exit(1)

        discount = contract.functions.getDiscountRate(account.address).call()
        discount_percent = discount / 100

        tokens_to_buy = wei_to_spend / token_price
        bonus_tokens = tokens_to_buy * (discount_percent / 100)
        total_tokens = tokens_to_buy + bonus_tokens

        print(f"\nВи купуєте {total_tokens} {token_symbol}. Бонус: {bonus_tokens}")

        confirm = input("Підтвердити покупку? (y/n): ").lower()
        if confirm != "y":
            print("Покупку скасовано.")
            return

        nonce = w3.eth.get_transaction_count(account.address)

        tx = contract.functions.buyTokens().build_transaction({
            "from": account.address,
            "value": wei_to_spend,
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
            "nonce": nonce
        })

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print("Очікуємо підтвердження...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            print(f"Успіх! Транзакція: https://mumbai.polygonscan.com/tx/{tx_hash.hex()}")
        else:
            print("Помилка при покупці!")

    except Exception as e:
        print("ПОМИЛКА:", e)

if OFFLINE_MODE:
    offline_mode()
else:
    online_mode()
