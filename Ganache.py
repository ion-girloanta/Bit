# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 14:17:46 2022

@author: ion_g

Test local ethereum server and set some balances

"""
from web3 import Web3
import json, random

setBalances = True  
setTransactions = True

def setBankBalance(receiver,sender, bankCustomer):
  # for GET must use call()
  # for PUT must use transact()
  contract.functions.setBankBalance(
    receiver,
    random.randint(100, 1000)*100,
    random.randint(100, 1000)*100,
    random.randint(100, 1000)*100,
    bankCustomer
    ).transact({'from':sender})
  balance = contract.functions.getBankBalance(receiver).call({'from':sender})
  print(f'bank balance: {balance}, account: {receiver}')

#Connect to blockchain on my local computer
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
print(f'connected: {w3.isConnected()}')
print(f'clientVersion: {w3.clientVersion}')

#First accountis my account
me = w3.eth.accounts[0]
print(f'me: {me}')


#Load smart contract definitions file
with open('C:/code/bit2201/build/contracts/BitErc20.json','r') as f:
  data = json.load(f)
abi=data['abi']
address = data['networks']['5777']['address']
contract = w3.eth.contract(address=address, abi=abi)
print(f'Contract: {address}')

#need to add .call() at the end to call the smart contract
#set my bank account balances
balance = contract.functions.getBankBalance(me).call()
print(f'my bank balance: {balance}')
print(f'token: {contract.functions.symbol().call()}, name: {contract.functions.name().call()}')

#print customers accounts
print(w3.eth.accounts)

#Set random balances for 9 customers 
if (setBalances):
  for account in w3.eth.accounts:
    setBankBalance(account, me, True)
  setBankBalance(w3.eth.accounts[9], me, False)
  receiver = Web3.toChecksumAddress('0xd9a7d949ef1708147e827f03d0fe761b1a51e46d')
  balance = contract.functions.getBankBalance(receiver).call()
  print(f'bank balance: {balance}, account: {receiver}')

def printTransactions(account):
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

#add test data
def transfer(recipient, sender, amount):
  print(f'transfer {amount} from {sender} to {recipient}',end=None)
  contract.functions.transfer(recipient,amount, 0).transact({'from': sender})

#==================
#add random 20 transactions between 8 accounts
if (setTransactions):
  for i in range(5):
    transfer(
      w3.eth.accounts[random.randint(0, 8)],
      w3.eth.accounts[random.randint(0, 8)],
      random.randint(10, 250)
      )
    
#Add test transactions sent to me
  transfer(
        w3.eth.accounts[random.randint(0, 8)],
        w3.eth.accounts[8],
        i * 100 + random.randint(0, 100)
        )

for i in range(4):
  #Add test transactions sent to me
  transfer(
        w3.eth.accounts[random.randint(0, 8)],
        me,
        i * 100 + random.randint(0, 100)
        )
  #Add test transactions from me to random customers
  transfer(
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
printTransactions(me)
printTransactions(w3.eth.accounts[9])

transact = contract.functions.transactionReceived(1).call({'from': me})
print(f'my transaction {transact}')
balance = contract.functions.getBankBalance(me).call()
print(f'my bank balance before approved transaction: {balance}')


balance = contract.functions.getBankBalance(me).call()
print(f'my bank balance after approved transaction: {balance}')
transact1 = contract.functions.transactionReceived(1).call({'from': me})
print(f'My transaction after approval {transact1}')

print('My received transactions')
printTransactions(me)
printTransactions(w3.eth.accounts[9])

