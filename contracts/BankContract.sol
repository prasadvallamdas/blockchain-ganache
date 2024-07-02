// SPDX-License-Identifier: MIT
pragma solidity >= 0.4.0 <= 0.9.0;

contract BankContract {
    string public users;
    string public bankaccount;
    string public history;

    function addhistory(string memory ra) public{
        history = ra;
    }

    function gethistory() public view returns (string memory){
        return history;
    }

    function addUsers(string memory u) public {
        users = u;	
    }

    function getUsers() public view returns (string memory) {
        return users;
    }

    function bankAccount(string memory ba) public {
        bankaccount = ba;	
    }

    function getBankAccount() public view returns (string memory) {
        return bankaccount;
    }

  


    constructor() public {
        users = "empty";
	bankaccount = "empty";
    history = "empty";
    }
}
