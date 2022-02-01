import base64
import json
import random
import web3
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

# TESTED WITH python 3.6

# Fill these from the compilation and from the deploy of the smart contract
USER = "e0eaz9d1s8"
PASS = "CSm6W_uxIXZqGtTkurw7S7wxer-Xsixur2U2LN89-VM"
RPC_ENDPOINT = "https://e0mnb9789l-e0ki64wmzb-rpc.de0-aws.kaleido.io"
apikey = 'ZTBlYXo5ZDFzODpDU202V191eElYWnFHdFRrdXJ3N1M3d3hlci1Yc2l4dXIyVTJMTjg5LVZN'
setBalances = True  
setTransactions = True

#set balance amt for a specified account (param = receiver)
def setBankBalance(w3, contract, receiver, sender, bankCustomer):
    #for PUT apis must add transact()
    tx_hash = contract.functions.setBankBalance(
        receiver,
        random.randint(100, 1000)*100,
        random.randint(100, 1000)*100,
        random.randint(100, 1000)*100,
        bankCustomer
        ).transact({'from':sender})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    balance = contract.functions.getBankBalance(receiver).call()
    print(f'bank balance: {balance}, account: {receiver}')

#transfer funds from sender to receipient 
def transfer(w3, contract, recipient, sender, amount):
    print(f'transfer {amount} from {sender} to {recipient}',end=None)
    tx_hash = contract.functions.transfer(recipient,amount, 0).transact({'from': sender})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Print all transactions for account
def printTransactions(contract, account):
  res = contract.functions.totalRecivedTransactions().call({'from': account})
  print(f'{account} received transactions[{res}]:')
  for i in range(res):
    transact = contract.functions.transactionReceived(i + 1).call({'from': account})
    print(f'{transact}')
  res = contract.functions.totalSentTransactions().call({'from': account})
  print(f'{account} sent transactions[{res}]:')
  for i in range(res):
    transact = contract.functions.transactionSent(i + 1).call({'from': account})
    print(f'{transact}')

def setup_web3():
    # Encode the username and password from the app creds into USER:PASS base64 encoded string
    auth = USER + ":" + PASS
    encodedAuth = base64.b64encode(auth.encode('ascii')).decode('ascii')
    
    # Build the header object with the Basic auth and the standard headers
    headers = {'headers': {'Authorization': 'Basic %s' % apikey,
                           'Content-Type': 'application/json',
                           'User-Agent': 'kaleido-web3py'}}
    
    # Construct a Web3 object by constructing and passing the HTTP Provider
    provider = HTTPProvider(endpoint_uri=RPC_ENDPOINT, request_kwargs=headers)
    w3 = Web3(provider)
    
    
    # Add the Geth POA middleware needed for ExtraData Header size discrepancies between consensus algorithms
    # See: http://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority
    # ONLY for GETH/POA; If you are using quorum, comment out the line below
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Get the latest block in the chain
    block = w3.eth.getBlock("latest")
    
    # Print the block out to the console
    print(block)
    print(f'\nconnected: {w3.isConnected()}')
    print(f'clientVersion: {w3.clientVersion}')
    
    # Get all accounts from the currnet node
    # First accountis my account
    accounts = w3.eth.accounts
    my_account = w3.eth.accounts[0]
    print(f'me: {my_account}')
    with open('C:/code/kaleido/build/contracts/BitErc20.json','r') as f:
      data = json.load(f)
      
    # get contract ABI (Application Binary Interface) 
    # used for function calls to the EVM (Ethereum Virtual Machine).
    abi=data['abi']
    
    # get contract id
    chain_id = list(data.get('networks', {}))[0]
    address = data['networks'][chain_id]['address']
    
    # get a instance for the smart contract to used to call functions 
    # call() used for GET info from the smart contract
    # transact () used for PUT to change something within the contract
    # both functions must use a parameter of type dict {'from': 'user_id'} 
    # where user_id is the account that call the function
    
    w3_contract = w3.eth.contract(address=address, abi=abi)
    print(f'Contract: {address}')
    return w3_contract, w3, my_account, accounts

if __name__ == '__main__':
  # !!! Done it, now get the balances for my account
  contract, w3, me, accounts = setup_web3()
  balance = contract.functions.getBankBalance(me).call()
  print(f'my bank balance: {balance}')
  print(f'token symbol: {contract.functions.symbol().call()}, toke name: {contract.functions.name().call()}')

  # Set some test data
  # Set random balances for 9 customers 
  if (setBalances):
    for account in accounts:
      setBankBalance(w3, contract, account, me, True)
    setBankBalance(w3, contract, accounts[9], me, False)   #Define account[9] as occasional customer !!Not a bank customer
  if (setTransactions):
    # Set random transactions
    for i in range(5):
      transfer(w3, contract, 
        accounts[random.randint(0, 8)],
        accounts[random.randint(0, 8)],
        random.randint(10, 250)
        )
      
    #Add test transactions sent to me
    transfer(w3, contract, 
          w3.eth.accounts[random.randint(0, 8)],
          w3.eth.accounts[8],
          i * 100 + random.randint(0, 100)
          )
  
    #Add test transactions from me
    for i in range(4):
      transfer(w3, contract, 
            w3.eth.accounts[random.randint(0, 8)],
            me,
            i * 100 + random.randint(0, 100)
            )
      #Add test transactions from me to random customers
      transfer(w3, contract, 
            me,
            w3.eth.accounts[random.randint(0, 8)],
            i * 100 + random.randint(0, 100)
            )
    #print test data for testing purposes
    #=========================================
    #for GET apis must add .call() after the funtion name
    res = contract.functions.sender().call({'from': me})
    print(f'sender = {res}')
    res = contract.functions.sender().call({'from': w3.eth.accounts[1]})
    print(f'sender = {res}')
    res = contract.functions.totalRecivedTransactions().call({'from': me})
    print(f'total received trasactions: {res} to my account')
    res = contract.functions.totalSentTransactions().call({'from': me})
    print(f'total sent transactions {res} from my account:')
    
    print('My received transactions')
    printTransactions(me)
    printTransactions(w3.eth.accounts[9])
    
    print('do some transfers')
    transfer(me,account, 1999)
    transfer(me,account, 222)
    transfer(account, me, 444)
    
    print('My received transactions')
    printTransactions(contract, me)
    printTransactions(contract, accounts[9])
    
    transact = contract.functions.transactionReceived(1).call({'from': me})
    print(f'my transaction {transact}')
    balance = contract.functions.getBankBalance(me).call()
    print(f'my bank balance before approved transaction: {balance}')  
    
    balance = contract.functions.getBankBalance(me).call()
    print(f'my bank balance after approved transaction: {balance}')
    transact1 = contract.functions.transactionReceived(1).call({'from': me})
    print(f'My transaction after approval {transact1}')
    
    print('My received transactions')
    printTransactions(contract, me)
    printTransactions(accounts[9])
      
      
