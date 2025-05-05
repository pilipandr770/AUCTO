// contracts/TokenDAO.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ISimpleToken {
    function balanceOf(address account) external view returns (uint256);
}

contract TokenDAO {
    struct Proposal {
        string description;
        uint voteCount;
        uint endTime;
        bool executed;
    }

    ISimpleToken public token;
    address public owner;
    uint public votingDuration = 3 days;

    Proposal[] public proposals;
    mapping(uint => mapping(address => bool)) public voted;

    event ProposalCreated(uint proposalId, string description);
    event Voted(uint proposalId, address voter, uint votes);
    event ProposalExecuted(uint proposalId);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    constructor(address tokenAddress) {
        token = ISimpleToken(tokenAddress);
        owner = msg.sender;
    }

    function createProposal(string memory description) external onlyOwner {
        proposals.push(Proposal({
            description: description,
            voteCount: 0,
            endTime: block.timestamp + votingDuration,
            executed: false
        }));
        emit ProposalCreated(proposals.length - 1, description);
    }

    function vote(uint proposalId) external {
        require(proposalId < proposals.length, "Invalid proposal");
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp < proposal.endTime, "Voting ended");
        require(!voted[proposalId][msg.sender], "Already voted");

        uint votes = token.balanceOf(msg.sender);
        require(votes > 0, "No tokens");

        proposal.voteCount += votes;
        voted[proposalId][msg.sender] = true;

        emit Voted(proposalId, msg.sender, votes);
    }

    function executeProposal(uint proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp >= proposal.endTime, "Voting not ended");
        require(!proposal.executed, "Already executed");

        proposal.executed = true;

        emit ProposalExecuted(proposalId);
        // Here you can add additional logic for decision execution
    }

    function getProposalsCount() external view returns (uint) {
        return proposals.length;
    }
}
