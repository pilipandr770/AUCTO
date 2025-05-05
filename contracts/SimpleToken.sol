// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SimpleToken {
    string public name;
    string public symbol;
    uint8 public decimals = 18;
    uint public totalSupply;
    uint public tokenPrice;

    address public owner;

    mapping(address => uint) public balanceOf;
    mapping(address => bool) public whitelist;

    event Transfer(address indexed from, address indexed to, uint value);
    event WhitelistUpdated(address indexed user, bool status);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(string memory _name, string memory _symbol, uint _initialSupply, uint _tokenPrice) {
        name = _name;
        symbol = _symbol;
        totalSupply = _initialSupply;
        tokenPrice = _tokenPrice;
        owner = msg.sender;
        balanceOf[owner] = _initialSupply;
    }

    function transfer(address _to, uint _value) external returns (bool) {
        require(balanceOf[msg.sender] >= _value, "Not enough tokens");
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    function buyTokens() external payable {
        uint amount = msg.value / tokenPrice;
        require(balanceOf[owner] >= amount, "Not enough tokens in reserve");

        if (whitelist[msg.sender]) {
            amount += amount * 10 / 100; // +10% бонус для whitelist
        }

        balanceOf[owner] -= amount;
        balanceOf[msg.sender] += amount;

        emit Transfer(owner, msg.sender, amount);
    }

    function addToWhitelist(address _user) external onlyOwner {
        whitelist[_user] = true;
        emit WhitelistUpdated(_user, true);
    }

    function removeFromWhitelist(address _user) external onlyOwner {
        whitelist[_user] = false;
        emit WhitelistUpdated(_user, false);
    }

    function getDiscountRate(address _user) external view returns (uint) {
        if (whitelist[_user]) {
            return 1000; // 10%
        }
        return 0;
    }

    function withdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}
