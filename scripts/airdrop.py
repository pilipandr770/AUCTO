# scripts/airdrop.py

import os
import sys
import json
import csv
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
    print("=== Token Airdrop Tool (OFFLINE MODE) ===")
    mock_data = load_mock_data()
    owner = mock_data["accounts"][0]
    whitelist = mock_data["whitelist"]

    total_tokens = mock_data["balances"][owner] / 10**18
    print(f"Owner account: {owner}")
    print(f"Available tokens for airdrop: {total_tokens}")
    print(f"Whitelisted addresses: {sum(1 for v in whitelist.values() if v)}")

    choice = input("Load from CSV file? (y/n): ").lower()
    targets = {}

    if choice == "y":
        filename = input("Enter CSV filename: ")
        try:
            with open(filename, "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) >= 2 and is_valid_address(row[0]):
                        targets[row[0]] = float(row[1])
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return
    else:
        for address in whitelist:
            if whitelist[address]:
                tokens = float(input(f"Enter tokens for {address}: "))
                targets[address] = tokens

    for address, tokens in targets.items():
        mock_data["balances"][address] = mock_data["balances"].get(address, 0) + int(tokens * 10**18)

    with open(MOCK_DATA_PATH, "w") as file:
        json.dump(mock_data, file, indent=2)

    print("Airdrop simulation complete!")

def online_mode():
    print("=== Token Airdrop Tool (ONLINE MODE) ===")

    RPC_URL = os.getenv("POLYGON_MUMBAI_RPC_URL")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")

    if not CONTRACT_ADDRESS or not RPC_URL:
        print("ERROR: CONTRACT_ADDRESS or POLYGON_MUMBAI_RPC_URL missing in .env")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not w3.is_connected():
        print("ERROR: Cannot connect to Polygon Network")
        sys.exit(1)

    abi = load_contract_abi()
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    owner = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"Owner address: {owner.address}")

    whitelisted = []
    print("Fetching whitelist...")

    for address in contract.functions.getAllWhitelisted().call():
        whitelisted.append(address)

    print(f"Whitelisted addresses: {len(whitelisted)}")

    targets = {}
    choice = input("Load from CSV file? (y/n): ").lower()

    if choice == "y":
        filename = input("Enter CSV filename: ")
        try:
            with open(filename, "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) >= 2 and is_valid_address(row[0]):
                        targets[row[0]] = float(row[1])
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return
    else:
        for address in whitelisted:
            tokens = float(input(f"Enter tokens for {address}: "))
            targets[address] = tokens

    for address, tokens in targets.items():
        nonce = w3.eth.get_transaction_count(owner.address)
        tx = contract.functions.airdropTokens(address, int(tokens * 10**18)).build_transaction({
            'from': owner.address,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })

        signed_tx = owner.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Airdrop sent to {address} | Tx: {tx_hash.hex()}")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print(f"Airdrop complete for {address} ✔")
        else:
            print(f"Airdrop FAILED for {address} ✖")

if OFFLINE_MODE:
    offline_mode()
else:
    online_mode()
