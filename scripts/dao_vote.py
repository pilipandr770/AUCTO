# scripts/dao_vote.py

import os
from web3 import Web3
from dotenv import load_dotenv
import json

load_dotenv()

DAO_CONTRACT_ADDRESS = os.getenv("DAO_CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
POLYGON_RPC_URL = os.getenv("POLYGON_MAINNET_RPC_URL")

if not DAO_CONTRACT_ADDRESS or not PRIVATE_KEY or not POLYGON_RPC_URL:
    print("ERROR: Вкажіть DAO_CONTRACT_ADDRESS, PRIVATE_KEY та POLYGON_MAINNET_RPC_URL в .env")
    exit()

w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))

account = w3.eth.account.from_key(PRIVATE_KEY)
address = account.address

# Завантажуємо ABI DAO контракту
with open("./contracts/dao_abi.json", "r") as f:
    dao_abi = json.load(f)

dao = w3.eth.contract(address=DAO_CONTRACT_ADDRESS, abi=dao_abi)

def create_proposal():
    description = input("Введіть опис пропозиції: ")

    tx = dao.functions.createProposal(description).build_transaction({
        'from': address,
        'nonce': w3.eth.get_transaction_count(address),
        'gas': 300000,
        'gasPrice': w3.to_wei('50', 'gwei')
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print("Створено пропозицію! Tx Hash:", w3.to_hex(tx_hash))

def vote_proposal():
    proposal_id = int(input("ID пропозиції для голосування: "))
    vote = input("Ваш голос (y/n): ").lower()

    support = vote == 'y'

    tx = dao.functions.vote(proposal_id, support).build_transaction({
        'from': address,
        'nonce': w3.eth.get_transaction_count(address),
        'gas': 200000,
        'gasPrice': w3.to_wei('50', 'gwei')
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print("Голосування надіслано! Tx Hash:", w3.to_hex(tx_hash))

def check_result():
    proposal_id = int(input("ID пропозиції для перевірки результату: "))

    result = dao.functions.getProposalResult(proposal_id).call()

    print("Результат пропозиції:", "ПРИЙНЯТО" if result else "ВІДХИЛЕНО")

def main():
    print("=== DAO VOTE TOOL ===")
    print("1. Створити пропозицію")
    print("2. Голосувати")
    print("3. Перевірити результат")
    print("4. Вийти")

    choice = input("Ваш вибір (1-4): ")

    if choice == "1":
        create_proposal()
    elif choice == "2":
        vote_proposal()
    elif choice == "3":
        check_result()
    else:
        print("Вихід.")

if __name__ == "__main__":
    main()
