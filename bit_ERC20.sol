// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;
//
//pragma experimental 'ABIEncoderV2';
//import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
//ERC20 contains several functions that a compliant token must be able to implement.
//TotalSupply: provides information about the total token supply
//BalanceOf: provides account balance of the owner's account
//Transfer: executes transfers of a specified number of tokens to a specified address
//TransferFrom: executes transfers of a specified number of tokens from a specified address
//Approve: allow a spender to withdraw a set number of tokens from a specified account
//Allowance: returns a set number of tokens from a spender to the owner
//


contract BitErc20 {
 
    address payable creator;    
    mapping (address => uint256) private _balances;
    mapping (address => BankBalance) private _bankBalance;
    mapping (address => Transaction) private _senderTransaction;
    mapping (address => Transaction) private _recipientTransaction;
    mapping (address => Payment) private _payment;

    mapping (address => mapping (address => uint256)) internal _allowances;
    uint256 private _totalSupply;
    string private _name;
    string private _symbol;

	struct BankBalance {  //state of the contract 
		uint256 _currentAccount;
		uint256 _deposit;
		uint256 _credit;
		bool _bankUser;
		uint256 _lastTransaction; 
		uint256 _validityTime;
    }

	struct Transaction {
	  uint256 _lastTransaction;
	  address[] _account;   //holds sender or recipient depending of transaction
		uint256[] _amt;
	  uint256[] _transactionId;
	  transactionAccount[] _accountType; 
		transactionState[] _accepted;
		uint256[] _validityTime;		
	}
	
	struct Payment {
	  uint256 _lastPayment;
	  string[] _provider;
	  string[] _billNo;
		uint256[] _amt;
		string[] _emailTo;
	  transactionAccount[] _accountType; 
		transactionState[] _accepted;
		uint256[] _validityTime;		
	}

	enum transactionState {pending, accepted, rejected}
	enum transactionAccount {CurrentAccount, Deposit, Credit}

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Accept(address indexed account, address indexed sender, uint256 value);
    event Reject(address indexed account, address indexed sender, uint256 value);

    constructor (string memory name_, string memory symbol_) {
        _name = name_;
        _symbol = symbol_;
         creator = payable(msg.sender);
    }

    /**
    * @dev Self Destruct a contract for blockchain.
    * @dev To be used only by the owner and only on extreme situations
    */
    function kill() public {
        if (msg.sender == creator) {
            selfdestruct(creator);
        }
    }
    
    /**
    * @dev Store a payment
    */
    function setPayment(transactionAccount _account, string calldata _provider, string calldata _billNo, uint256 _amt, string calldata _emailTo) public {
				_payment[msg.sender]._provider.push(_provider);        
			  _payment[msg.sender]._billNo.push(_billNo);
				_payment[msg.sender]._amt.push(_amt);
				_payment[msg.sender]._emailTo.push(_emailTo);
			  _payment[msg.sender]._accountType.push(_account); 
				_payment[msg.sender]._accepted.push(transactionState.accepted);
				_payment[msg.sender]._validityTime.push(block.timestamp);		
	  		_payment[msg.sender]._lastPayment+=1;
    }
    
    /**
    * @dev Store a payment
    */
    function getPayment(uint256 paymentNo) public view virtual returns (string memory _provider, string memory _billNo, 
       uint256 _amt, string memory _emailTo, transactionAccount _accountType, transactionState _accepted, uint256 _validityTime) {
           
       string memory provider = _payment[msg.sender]._provider[paymentNo]; 
       string memory billNo =_payment[msg.sender]._billNo[paymentNo]; 
       uint256 amt = _payment[msg.sender]._amt[paymentNo]; 
       string memory emailTo = _payment[msg.sender]._emailTo[paymentNo];
       transactionAccount accountType = _payment[msg.sender]._accountType[paymentNo]; 
       transactionState accepted = _payment[msg.sender]._accepted[paymentNo]; 
       uint256 validityTime = _payment[msg.sender]._validityTime[paymentNo];
       
       return (
						provider,        
					  billNo,
						amt,
						emailTo,
					  accountType, 
						accepted,
						validityTime);
    }
    

    /**
    * @dev Get the token name. Could be useful for apps UI 
    */
    function name() public view virtual returns (string memory) {
        return _name;
    }

    /**
    * @dev Get the token symbol. Could be useful for apps UI 
    */
    function symbol() public view virtual returns (string memory) {
        return _symbol;
    }

    function decimals() public pure virtual returns (uint8) {
        return 0;
    }

    function totalSupply() public view virtual returns (uint256) {
        return _totalSupply;
    }

    /**
    * @dev Get the address of who is calling the function. Could be useful for debuging. 
    */
    function sender() public view virtual returns (address _sender) {
        return msg.sender;
    }

    /**
    * @dev Get the number of transactions that was sent by who is calling this function.
    * @dev Useful for looping between transactions. 
    */
		function totalSentTransactions() public view virtual returns (uint256) {
        return _senderTransaction[msg.sender]._lastTransaction;
        }

    /**
    * @dev Get the number of transactions that was received by who is calling this function.
    * @dev Useful for looping between transactions. 
    */
    function totalRecivedTransactions() public view virtual returns (uint256) {
        return _recipientTransaction[msg.sender]._lastTransaction;
    }

    /**
    * @dev Get bank balances. 
    * @param account The user account address.
    * @param CurrentAccount The current account balance.
    * @param Deposit The deposit balance.
    * @param Credit The loan balance.
    */
    function getBankBalance(address account) public view virtual returns (uint256 CurrentAccount, uint256 Deposit, uint256 Credit, bool bankUser, uint256 ValidityTime) {
        return (
            _bankBalance[account]._currentAccount, 
            _bankBalance[account]._deposit, 
            _bankBalance[account]._credit,
            _bankBalance[account]._bankUser,  
            _bankBalance[account]._validityTime
        );
    }

    /**
    * @dev Set bank balances. Useful for the bank to synchronize balances 
    * @dev between the bank and the blockchain network
    * @param account The user account address to be set.
    * @param CurrentAccount The current account balance.
    * @param Deposit The deposit balance.
    * @param Loan The loan balance.
    */
    function setBankBalance(address account, uint256 CurrentAccount, uint256 Deposit, uint256 Loan, bool BankUser) public virtual returns (bool, uint256) {
        _bankBalance[account]._currentAccount = CurrentAccount;
        _bankBalance[account]._deposit = Deposit;
        _bankBalance[account]._credit = Loan;
        _bankBalance[account]._bankUser = BankUser;
        _bankBalance[account]._validityTime = block.timestamp;
        _balances[account] = CurrentAccount;
        return (true, _balances[account]);
    }

    /**
    * @dev Get transaction metadata sent by the caller of the function. 
    * @param recipient The recipient account to be queried.
    * @param transactionId The transaction Id.
    * @param amt The transaction amount.
    * @param accepted The transaction approving state.
    */
    function transactionSent(uint256 transactionId) public view virtual returns (address recipient, uint256 amt, transactionState accepted, uint256 validityTime, uint256 lastTransaction) {
        require(transactionId > 0, "ERC20: Unknown transaction. Error 1001");
        require(_senderTransaction[msg.sender]._lastTransaction >= transactionId, "ERC20: Unknown transaction. Error 1002");
        uint256 _transactionId = _senderTransaction[msg.sender]._lastTransaction - transactionId;
        return (
            	_senderTransaction[msg.sender]._account[_transactionId], 
            	_senderTransaction[msg.sender]._amt[_transactionId], 
            	_senderTransaction[msg.sender]._accepted[_transactionId], 
            	_senderTransaction[msg.sender]._validityTime[_transactionId],
            	_senderTransaction[msg.sender]._transactionId[_transactionId]           	
        );
    }

    /**
    * @dev Get transaction metadata received by the caller of the function. 
    * @param recipient The recipient account to be queried.
    * @param transactionId The transaction Id.
    * @param amt The transaction amount.
    * @param accepted The transaction approving state.
    */
    function transactionReceived(uint256 transactionId) public view virtual returns (address recipient, uint256 amt, transactionState accepted, uint256 validityTime, uint256 lastTransaction) {
        require(transactionId > 0, "ERC20: Unknown transaction. Error 1001");
        require(_recipientTransaction[msg.sender]._lastTransaction >= transactionId, "ERC20: Unknown transaction. Error 1002");
        uint256 _transactionId = _recipientTransaction[msg.sender]._lastTransaction - transactionId;
        return (
            	_recipientTransaction[msg.sender]._account[_transactionId], 
            	_recipientTransaction[msg.sender]._amt[_transactionId], 
            	_recipientTransaction[msg.sender]._accepted[_transactionId], 
            	_recipientTransaction[msg.sender]._validityTime[_transactionId],
            	_recipientTransaction[msg.sender]._transactionId[_transactionId]           	
        );
    }



    /**
    * @dev Approve one transaction from sender to caller and add the amount to my current account balance. 
    * @param transactionId The ID of the transaction to be accepted. The transaction must be in pending state
    */
    function approveTransaction(uint256 transactionId, transactionAccount dest) public virtual {
				_approveTransaction(msg.sender, transactionId, transactionState.accepted, dest);
    }

    /**
    * @dev Deny one transaction from sender and add the amount to back to the sender current account balance. 
    * @param transactionId The ID of the transaction to be accepted. The transaction must be in pending state
    */
    function rejectTransaction(uint256 transactionId) public virtual{
				_approveTransaction(msg.sender, transactionId, transactionState.rejected, transactionAccount.CurrentAccount);					    		
    }

    /**
    * @dev Transfer token to a specified address. 
    * @dev Sender must have at least the amount requested to be transfered
    * @param recipient The address to transfer to.
    * @param amount The amount to be transferred.
    * @param currentAccountBalance Updated sender current account balance
    * @param addrsender Sender address
    * @param addrrecipient Recipient address
    */
    function transfer(address recipient, uint256 amount, transactionAccount fromAccount) public virtual returns (uint256 currentAccountBalance, address addrsender, address addrrecipient) {
        _transfer(msg.sender, recipient, amount, fromAccount);
        return (_balances[msg.sender], msg.sender, recipient);
    }

    /**
    * @dev Make a deposit. Updated balances will be returned
    * @dev The user must have enough funds in his current account
    * @param amount The amount to be deposit.
    * @param currentAccountBalance Updated current account balance
    * @param depositBalance Updated deposit balance
    */
    function deposit(uint256 amount) public virtual returns (uint256 currentAccountBalance, uint256 depositBalance) {
        _deposit(amount);
        return (_bankBalance[msg.sender]._currentAccount, _bankBalance[msg.sender]._deposit);
    }

    /**
    * @dev Withdraw from deposit. Updated balances will be returned
    * @dev The user must have enough funds in his deposit account
    * @param amount The amount to be withdraw.
    * @param currentAccountBalance Updated current account balance
    * @param depositBalance Updated deposit balance
    */
    function withdraw(uint256 amount) public virtual returns (uint256 currentAccountBalance, uint256 depositBalance) {
        _withdraw(amount);
        return (_bankBalance[msg.sender]._currentAccount, _bankBalance[msg.sender]._deposit);
    }

    /**
    * @dev Credit my account by amount. Updated balances will be returned
    * @dev The user must have enough funds in his credit account
    * @param amount The amount to be added to the current account..
    * @param currentAccountBalance Updated current account balance
    * @param loanBalance Updated credit balance
    */
    function credit(uint256 amount) public virtual returns (uint256 currentAccountBalance, uint256 loanBalance) {
        _credit(amount);
        return (_bankBalance[msg.sender]._currentAccount, _bankBalance[msg.sender]._deposit);
    }

    /**
    * @dev Debit my account by amount. Updated balances will be returned
    * @dev The user must have enough funds in his current account
    * @param amount The amount to be deducted from the current account..
    * @param currentAccountBalance Updated current account balance
    * @param loanBalance Updated credit balance
    */
    function debit(uint256 amount) public virtual returns (uint256 currentAccountBalance, uint256 loanBalance) {
        _debit(amount);
        return (_bankBalance[msg.sender]._currentAccount, _bankBalance[msg.sender]._deposit);
    }

    function allowance(address owner, address spender) public view virtual returns (uint256) {
        return _allowances[owner][spender];
    }

    function approve(address spender, uint256 amount) internal virtual returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }

    function increaseAllowance(address spender, uint256 addedValue) public virtual returns (bool) {
        uint256 currentAllowance = _allowances[msg.sender][spender];
        _approve(msg.sender, spender, currentAllowance + addedValue);
        return true;
    }

    function decreaseAllowance(address spender, uint256 subtractedValue) public virtual returns (bool) {
        uint256 currentAllowance = _allowances[msg.sender][spender];
        require(currentAllowance >= subtractedValue, "ERC20: decreased allowance below zero");
        _approve(msg.sender, spender, currentAllowance - subtractedValue);

        return true;
    }

    function _transfer(address _sender, address recipient, uint256 amount, transactionAccount fromAccount) internal virtual {
        require(_sender != address(0), "ERC20: transfer from the unknown address. Error 1001");
        require(recipient != address(0), "ERC20: transfer to the incorrect address. Error 1002");
        require(_bankBalance[_sender]._currentAccount >= amount, "ERC20: transfer incorrect amount. Error 1003");

        if (fromAccount == transactionAccount.CurrentAccount) {
		        _bankBalance[_sender]._currentAccount -= amount;
			    	_balances[_sender] -= amount;
        } else if (fromAccount == transactionAccount.Credit) {
			    	_bankBalance[msg.sender]._credit -= amount;
        } else if (fromAccount == transactionAccount.Deposit){
			    	_bankBalance[msg.sender]._deposit -= amount;
        }
        
				_senderTransaction[_sender]._accepted.push(transactionState.pending);
				_senderTransaction[_sender]._amt.push(amount);
				_senderTransaction[_sender]._account.push(recipient);
				_senderTransaction[_sender]._validityTime.push(block.timestamp);
				
				_recipientTransaction[recipient]._accepted.push(transactionState.pending);
				_recipientTransaction[recipient]._amt.push(amount);
				_recipientTransaction[recipient]._account.push(_sender);
				_recipientTransaction[recipient]._validityTime.push(block.timestamp);

				_senderTransaction[_sender]._transactionId.push(_recipientTransaction[recipient]._lastTransaction);
				_recipientTransaction[recipient]._transactionId.push(_senderTransaction[_sender]._lastTransaction);
				_senderTransaction[_sender]._lastTransaction += 1;
				_recipientTransaction[recipient]._lastTransaction += 1;

        emit Transfer(_sender, recipient, amount);
    }


    function _mint(address account, uint256 amount) internal virtual {
        require(account != address(0), "ERC20: mint to the zero address");
        _totalSupply += amount;
        _balances[account] += amount;
    }

    function _burn(address account, uint256 amount) internal virtual {
        require(account != address(0), "ERC20: burn from the zero address");

        uint256 accountBalance = _balances[account];
        require(accountBalance >= amount, "ERC20: burn amount exceeds balance");
        _balances[account] = accountBalance - amount;
        _totalSupply -= amount;

        //emit Transfer(account, address(0), amount);
    }

    function _deposit(uint256 amount) internal virtual {
        require(_bankBalance[msg.sender]._currentAccount >= amount, "ERC20: Not enough available fund to make the deposit");
        _bankBalance[msg.sender]._currentAccount -= amount;
        _bankBalance[msg.sender]._deposit += amount;
        //emit Approval(owner, spender, amount);
    }

    function _withdraw(uint256 amount) internal virtual {
        require(_bankBalance[msg.sender]._deposit >= amount, "ERC20: Not enough available fund to make the deposit");
        _bankBalance[msg.sender]._currentAccount += amount;
        _bankBalance[msg.sender]._deposit -= amount;
        //emit Approval(owner, spender, amount);
    }
    
    function _debit(uint256 amount) internal virtual {
        require(_bankBalance[msg.sender]._currentAccount >= amount, "ERC20: Not enough available fund to make the deposit");
        _bankBalance[msg.sender]._currentAccount -= amount;
        _bankBalance[msg.sender]._credit += amount;
        //emit Approval(owner, spender, amount);
    }

    function _credit(uint256 amount) internal virtual {
        require(_bankBalance[msg.sender]._credit >= amount, "ERC20: Not enough available fund to make the deposit");
        _bankBalance[msg.sender]._currentAccount += amount;
        _bankBalance[msg.sender]._credit -= amount;
        //emit Approval(owner, spender, amount);
    }
    
    function _approve(address owner, address spender, uint256 amount) internal virtual {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner][spender] = amount;
        //emit Approval(owner, spender, amount);
    }
    
    function _approveTransaction(address account, uint256 transactionId, transactionState state, transactionAccount dest) internal  {

        require(transactionId > 0, "ERC20: Unknown transaction. Error 1001");
        require(_recipientTransaction[account]._lastTransaction >= transactionId, "ERC20: Unknown transaction. Error 1002");
        uint256 _transactionId = _recipientTransaction[account]._lastTransaction - transactionId;
        require (_recipientTransaction[account]._accepted[_transactionId] == transactionState.pending,"ERC20: Unknown transaction. Error 1003");
				uint256 amount =  _recipientTransaction[account]._amt[_transactionId];
				
				//Approve my transaction
	    	_recipientTransaction[account]._accepted[_transactionId] = state;   	

				//Approve sender transaction
	    	address _sender = _recipientTransaction[account]._account[_transactionId];
	    	_transactionId = _recipientTransaction[account]._transactionId[_transactionId];			
 	    	_senderTransaction[_sender]._accepted[_transactionId] = state;

				//Add amount to my account
				if (state == transactionState.accepted) {
		        if (dest == transactionAccount.CurrentAccount) {
					    	_bankBalance[account]._currentAccount += amount;
					    	_balances[account] += amount;
		        } else if (dest == transactionAccount.Credit) {
					    	_bankBalance[account]._credit += _recipientTransaction[account]._amt[_transactionId];
		        } else if (dest == transactionAccount.Deposit){
					    	_bankBalance[account]._deposit += _recipientTransaction[account]._amt[_transactionId];
		        }
		    } else {
			    	_bankBalance[account]._currentAccount += amount;
			    	_balances[account] += amount;		        
		    }				
    }

    function balanceOf(address account) internal view virtual returns (uint256) {
        return _balances[account];
    }

    /**
     * @dev Hook that is called before any transfer of tokens. This includes
     * minting and burning.
     *
     * Calling conditions:
     *
     * - when `from` and `to` are both non-zero, `amount` of ``from``'s tokens
     * will be to transferred to `to`.
     * - when `from` is zero, `amount` tokens will be minted for `to`.
     * - when `to` is zero, `amount` of ``from``'s tokens will be burned.
     * - `from` and `to` are never both zero.
     *
     * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
     */

}