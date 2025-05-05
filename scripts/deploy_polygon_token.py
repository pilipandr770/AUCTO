# scripts/deploy_polygon_token.py

import os
import sys
import json
from dotenv import load_dotenv
from web3 import Web3
from solcx import compile_source, set_solc_version, install_solc

load_dotenv()

OFFLINE_MODE = "--offline" in sys.argv

# Встановлення потрібної версії компілятора
try:
    set_solc_version("0.8.20")
except:
    install_solc("0.8.20")
    set_solc_version("0.8.20")

CONTRACT_FILE = "./contracts/SimpleToken.sol"

if OFFLINE_MODE:
    print("=== Розгортання контракту (OFFLINE РЕЖИМ) ===")
else:
    print("=== Розгортання контракту на Polygon ===")

with open(CONTRACT_FILE, "r") as f:
    source_code = f.read()

compiled_sol = compile_source(source_code, output_values=["abi", "bin"])
contract_id, contract_interface = compiled_sol.popitem()
abi = contract_interface["abi"]
bytecode = contract_interface["bin"]

with open("./contracts/abi.json", "w") as f:
    json.dump(abi, f, indent=2)

if OFFLINE_MODE:
    mock_data = {
        "contract_address": "0x1234567890123456789012345678901234567890",
        "accounts": [
            "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
            "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
            "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        ],
        "balances": {},
        "whitelist": {},
        "token_price": 10000000000000000,
        "token_name": "SimpleToken",
        "token_symbol": "STK"
    }

    with open("./mock_data.json", "w") as f:
        json.dump(mock_data, f, indent=2)

    print("Контракт успішно 'розгорнуто' в OFFLINE режимі!")
    sys.exit(0)

RPC_URL = os.getenv("POLYGON_MUMBAI_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not RPC_URL or not PRIVATE_KEY:
    print("ERROR: Налаштуйте POLYGON_MUMBAI_RPC_URL та PRIVATE_KEY в .env")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("Помилка підключення до Polygon RPC")
    sys.exit(1)

account = w3.eth.account.from_key(PRIVATE_KEY)
print("Використовується акаунт:", account.address)

SimpleToken = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(account.address)

token_name = input("Назва токену (SimpleToken): ") or "SimpleToken"
token_symbol = input("Символ токену (STK): ") or "STK"
initial_supply = int(input("Початкова кількість токенів (1000000): ") or "1000000") * 10**18
token_price = Web3.to_wei(float(input("Ціна токену в MATIC (0.01): ") or "0.01"), 'ether')

transaction = SimpleToken.constructor(token_name, token_symbol, initial_supply, token_price).build_transaction({
    "from": account.address,
    "nonce": nonce,
    "gas": 3000000,
    "gasPrice": w3.eth.gas_price
})

signed_tx = account.sign_transaction(transaction)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

print("Очікуємо підтвердження...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

if tx_receipt.status == 1:
    contract_address = tx_receipt.contractAddress
    print("Контракт розгорнуто за адресою:", contract_address)

    with open("./.env", "a") as f:
        f.write(f"\nCONTRACT_ADDRESS={contract_address}")

    print("Адресу контракту записано в .env!")
else:
    print("Розгортання не вдалося!")
