# scripts/deploy_dao.py

import os
from web3 import Web3
from solcx import compile_source, set_solc_version
from dotenv import load_dotenv
import json

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
POLYGON_RPC_URL = os.getenv("POLYGON_MAINNET_RPC_URL")

if not PRIVATE_KEY or not POLYGON_RPC_URL:
    print("ERROR: Вкажіть PRIVATE_KEY та POLYGON_MAINNET_RPC_URL в .env")
    exit()

w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))

account = w3.eth.account.from_key(PRIVATE_KEY)
address = account.address

print("=== Розгортання DAO контракту ===")
print("Використовується акаунт:", address)

# Solidity код DAO контракту
dao_source_code = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DAO {

    struct Proposal {
        string description;
        uint256 votesFor;
        uint256 votesAgainst;
        bool executed;
    }

    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCount;

    mapping(address => mapping(uint256 => bool)) public hasVoted;

    function createProposal(string memory description) public {
        proposals[proposalCount] = Proposal(description, 0, 0, false);
        proposalCount++;
    }

    function vote(uint256 proposalId, bool support) public {
        require(!hasVoted[msg.sender][proposalId], "Already voted");


        hasVoted[msg.sender][proposalId] = true;

        if (support) {
            proposals[proposalId].votesFor++;
        } else {
            proposals[proposalId].votesAgainst++;
        }
    }

    function getProposalResult(uint256 proposalId) public view returns (bool) {
        Proposal memory p = proposals[proposalId];
        return p.votesFor > p.votesAgainst;
    }
}
'''

# Встановлюємо версію компілятора
set_solc_version("0.8.20")

compiled_sol = compile_source(
    dao_source_code,
    output_values=["abi", "bin"]
)

contract_id, contract_interface = compiled_sol.popitem()
abi = contract_interface["abi"]
bytecode = contract_interface["bin"]

# Створюємо контракт об'єкт
DAO = w3.eth.contract(abi=abi, bytecode=bytecode)

# Будуємо транзакцію
construct_txn = DAO.constructor().build_transaction({
    'from': address,
    'nonce': w3.eth.get_transaction_count(address),
    'gas': 2000000,
    'gasPrice': w3.to_wei('50', 'gwei')
})

# Підписуємо та надсилаємо
signed = w3.eth.account.sign_transaction(construct_txn, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

print("Очікуємо підтвердження...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress
print("DAO контракт розгорнуто за адресою:", contract_address)

# Зберігаємо ABI
os.makedirs("./contracts", exist_ok=True)

with open("./contracts/dao_abi.json", "w") as f:
    json.dump(abi, f)

print("ABI контракту збережено в ./contracts/dao_abi.json")

# Додаємо до .env
env_path = ".env"

with open(env_path, "a") as env_file:
    env_file.write(f"\nDAO_CONTRACT_ADDRESS={contract_address}\n")

print(".env оновлено (DAO_CONTRACT_ADDRESS)")
print("Готово!")
