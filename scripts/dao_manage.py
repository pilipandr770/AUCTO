# scripts/dao_manage.py
import os
from dotenv import load_dotenv
from web3 import Web3
import json

load_dotenv()

RPC_URL = os.getenv("POLYGON_MAINNET_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
DAO_CONTRACT_ADDRESS = os.getenv("DAO_CONTRACT_ADDRESS")
ACCOUNT_ADDRESS = Web3.to_checksum_address(os.getenv("ACCOUNT_ADDRESS"))

w3 = Web3(Web3.HTTPProvider(RPC_URL))

with open("./contracts/TokenDAO_abi.json") as f:
    abi = json.load(f)

dao = w3.eth.contract(address=Web3.to_checksum_address(DAO_CONTRACT_ADDRESS), abi=abi)

def create_proposal():
    desc = input("Опис пропозиції: ")
    tx = dao.functions.createProposal(desc).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': w3.eth.get_transaction_count(ACCOUNT_ADDRESS),
        'gas': 200000,
        'gasPrice': w3.to_wei('10', 'gwei')
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print("Створено пропозицію. Тx:", w3.to_hex(tx_hash))

def vote():
    proposal_id = int(input("ID пропозиції: "))
    tx = dao.functions.vote(proposal_id).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': w3.eth.get_transaction_count(ACCOUNT_ADDRESS),
        'gas': 200000,
        'gasPrice': w3.to_wei('10', 'gwei')
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print("Голос враховано. Тx:", w3.to_hex(tx_hash))

def execute():
    proposal_id = int(input("ID пропозиції для виконання: "))
    tx = dao.functions.executeProposal(proposal_id).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': w3.eth.get_transaction_count(ACCOUNT_ADDRESS),
        'gas': 200000,
        'gasPrice': w3.to_wei('10', 'gwei')
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print("Виконано. Тx:", w3.to_hex(tx_hash))

def list_proposals():
    count = dao.functions.getProposalsCount().call()
    for i in range(count):
        p = dao.functions.proposals(i).call()
        print(f"[{i}] {p[0]} | Голоси: {p[1]} | До: {p[2]} | Виконано: {p[3]}")

if __name__ == "__main__":
    while True:
        print("\nDAO Менеджер")
        print("1. Список пропозицій")
        print("2. Створити пропозицію")
        print("3. Голосувати")
        print("4. Виконати пропозицію")
        print("5. Вийти")
        choice = input("Виберіть дію: ")

        if choice == "1":
            list_proposals()
        elif choice == "2":
            create_proposal()
        elif choice == "3":
            vote()
        elif choice == "4":
            execute()
        elif choice == "5":
            break
