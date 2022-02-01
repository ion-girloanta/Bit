# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 19:32:05 2022

@author: ion_g
"""

# Example script to create a single-account consortium, with an environment
# and a set of members. Each member is given one node, and the script
# waits until the nodes are initialized.

import urllib.request, json, os, re, argparse, time

host  = 'https://e0mnb9789l-e0ki64wmzb-connect.de0-aws.kaleido.io'
gateway = 'gateways/e0kpq33lpc'
apikey = 'ZTBlYXo5ZDFzODpDU202V191eElYWnFHdFRrdXJ3N1M3d3hlci1Yc2l4dXIyVTJMTjg5LVZN'
headers =  {
  'accept': 'application/json',
  'Content-Type': 'application/json', 
  'Authorization': 'Basic {0}'.format(apikey),
#  'x-kaleido-from': '0x6beb35a64c1e444d4bef96b8f7f420368c885cf0',
#  'account':  '0x6beb35a64c1e444d4bef96b8f7f420368c885cf0'
  }


##############################################################
function = [
  'getBankBalance',  
  'setBankBalance',
  'transfer',
  'withdraw',
  'deposit',
  'credit',
  'debit',
  'transactionOf']
##############################################################
user = [
  '0xd66854e8c91CA08504902073f9cf63b5EbbBac50',
  '0x4823e50fba88ad35f0d9b202e380345e7063e714',
  '0xbee532C53a5ceef1fF657A6124b607D50cD99c92',
  '0xc26494f46dc4e7fa8702c8d21a46500318a16240',
  '0x22da0a16c0330d6720de4ca4eea8950f98f51db2',
  '0x444d5e1267d3abc938868b3a13257898c942086a',
  '0xc41752facbfa53383b4e4a09baeb60cc61b4b4f8'
  ]
##############################################################
contracts = [
  '0xcbd2ddbd51e67f313c2e945b4138abf497fc2fea',
  '0x6e9994c98765a7a051d59c3611ee65831baa87ed',
  'instances/ss123',
  'instances/0x80db4c4c0383f3cb2379d6ec603544a6b3f8f970',
  'instances/0xd4729cad04f44990bc3df19ac70cc8b617cc0ca9',
  'instances/0x96a2ef61611e4e002c06a55d030291e50db11123',
  'instances/0x03f2992b3c954e475d42c7a1367587615e6f6a8f',
  'instances/0xdfed78e8f458f05e44a9f87be12ba4607461e323'
  ]
##############################################################

method = 'GET'
print_output = True
waitok = False

def call_api(host, gateway, contracts, function, params, method, json_data):
  url = f'{host}/{gateway}/{contracts}/{function}?{params}'
  if print_output: print('--> ', method, url)
  data_str = ''
  if (json_data != None):
    json_data['accept'] = 'application/json',
    json_data['Content-Type'] = 'application/json', 
    json_data['Authorization'] = 'Basic {0}'.format(apikey)
    data_str = json.dumps(json_data, indent=2).encode()
    if print_output: print(data_str.decode())
  else:
    data_str = None
  #print('headers: ', headers)
  req = urllib.request.Request(url, data=data_str, headers=headers, method=method) #data=data_str.encode()
  if (waitok):
    input('OK?')
  with urllib.request.urlopen(req) as res:
    json_res = json.load(res)
    if print_output:
      print('<-- {0}'.format(res.getcode()))
      print(json.dumps(json_res, indent=2))
    return json_res

#Initialize accounts
data={"account": user[0],"CurrentAccount": "21500","Deposit": "15000", "Loan": "10000", "BankUser": True}
call_api(host,gateway, contracts[0],function[1],f'kld-from={user[0]}&kld-sync=true','POST', data)  

data={"account": user[1], "CurrentAccount": "17000","Deposit": "5000",  "Loan": "13000", "BankUser": True}
call_api(host,gateway, contracts[0],function[1],f'kld-from={user[0]}&kld-sync=true','POST', data)  

data={"account": user[2], "CurrentAccount": "15500","Deposit": "6000",  "Loan": "52000", "BankUser": True}
call_api(host,gateway, contracts[0],function[1],f'kld-from={user[0]}&kld-sync=true','POST', data)  

data={"account": user[3], "CurrentAccount": "17000","Deposit": "5000",  "Loan": "13000", "BankUser": True}
call_api(host,gateway, contracts[0],function[1],f'kld-from={user[0]}&kld-sync=true','POST', data)  

#Check balances
call_api(host,gateway, contracts[0],function[0],f'account={user[0]}','GET', None)  
call_api(host,gateway, contracts[0],function[0],f'account={user[1]}','GET', None)  
call_api(host,gateway, contracts[0],function[0],f'account={user[2]}','GET', None)  
call_api(host,gateway, contracts[0],function[0],f'account={user[3]}','GET', None)  

#Do some transfers
data={"amount": "180", "recipient": user[1]}
call_api(host,gateway, contracts[0],function[2],f'kld-from={user[0]}&kld-sync=true','POST', data)  

data={"amount": "140", "recipient": user[2]}
call_api(host,gateway, contracts[0],function[2],f'kld-from={user[0]}&kld-sync=true','POST', data)  

data={"amount": "550", "recipient": user[2]}
call_api(host,gateway, contracts[0],function[2],f'kld-from={user[1]}&kld-sync=true','POST', data)  

#Check balances
call_api(host,gateway, contracts[0],function[0],f'account={user[0]}','GET', None)  
call_api(host,gateway, contracts[0],function[0],f'account={user[1]}','GET', None)  
call_api(host,gateway, contracts[0],function[0],f'account={user[2]}','GET', None)  
call_api(host,gateway, contracts[0],function[0],f'account={user[3]}','GET', None)  

#Do some withdraws
data={"amount": "550"}
call_api(host,gateway, contracts[0],function[3],f'kld-from={user[0]}&kld-sync=true','POST', data)  

data={"amount": "900"}
call_api(host,gateway, contracts[0],function[3],f'kld-from={user[1]}&kld-sync=true','POST', data)  

data={"amount": "2000"}
call_api(host,gateway, contracts[0],function[3],f'kld-from={user[2]}&kld-sync=true','POST', data)  

data={"amount": "100"}
call_api(host,gateway, contracts[0],function[3],f'kld-from={user[3]}&kld-sync=true','POST', data)  

#Do some deposits
data={"amount": "1550"}
call_api(host,gateway, contracts[0],function[3],f'kld-from={user[0]}&kld-sync=true','POST', data)  

data={"amount": "1700"}
call_api(host,gateway, contracts[0],function[3],f'kld-from={user[1]}&kld-sync=true','POST', data)  

data={"amount": "2000"}
call_api(host,gateway, contracts[0],function[3],f'kld-from={user[2]}&kld-sync=true','POST', data)  

data={"amount": "1012"}
call_api(host,gateway, contracts[0],function[3],f'kld-from={user[2]}&kld-sync=true','POST', data)  

#Get some transactions
data={'transactionId':'2'}
call_api(host,gateway, contracts[0],function[7],f'kld-from={user[0]}&kld-sync=true','POST', data)  

data={'transactionId':'4'}
call_api(host,gateway, contracts[0],function[7],f'kld-from={user[1]}&kld-sync=true','POST', data)  

data={'transactionId':'6'}
call_api(host,gateway, contracts[0],function[7],f'kld-from={user[0]}&kld-sync=true','POST', data)  

#Aprove some transactions
#Deny some transactions
#Get account balances
call_api(host,gateway, contracts[0],function[0],f'account={user[0]}','GET', None)  
call_api(host,gateway, contracts[0],function[0],f'account={user[1]}','GET', None)  
call_api(host,gateway, contracts[0],function[0],f'account={user[2]}','GET', None)  
call_api(host,gateway, contracts[0],function[0],f'account={user[3]}','GET', None)  
