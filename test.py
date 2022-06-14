from web3 import Web3
from web3.middleware import geth_poa_middleware
import pickle
import os


def deploy_contract(web3_instance, abi, bytecode):
    """

    :param Web3 web3_instance:
    :param abi:
    :param bytecode:
    :return:
    """
    contract = web3_instance.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = contract.constructor().transact()
    tx_receipt = web3_instance.eth.wait_for_transaction_receipt(tx_hash)
    contract_instance = web3_instance.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi
    )
    return contract_instance



w3 = Web3(Web3.HTTPProvider('http://192.168.229.143:8001'))
print("Connection:", w3.isConnected())
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
print(w3.clientVersion)
w3.eth.default_account = w3.eth.accounts[0]


# coinbase_account = "0xE29A1AE4447c341Eb45eD303d0aC30C77587E668"
coinbase_account = w3.eth.accounts[0]
# test_account = w3.eth.accounts[1]

if os.path.exists("test_account"):
    with open('test_account', 'rb') as f:
        test_account = pickle.load(f)
else:
    test_account = w3.eth.account.create()
    print(w3.eth.accounts)
    with open('test_account', 'wb') as f:
        pickle.dump(test_account, f)

print("test account address:", test_account.address)
print("all accounts:", w3.eth.accounts)
test_account_address = test_account.address
coinbase_balance = w3.eth.get_balance(coinbase_account)
test_account_balance = w3.eth.get_balance(test_account_address)
print(w3.fromWei(coinbase_balance, 'ether'), w3.fromWei(test_account_balance, 'gwei'))

if test_account_balance < w3.toWei(4, 'gwei'):
    transaction_hash = w3.eth.send_transaction({
        'from': w3.eth.coinbase,
        'to': test_account_address,
        'value': w3.toWei(2000, 'wei'),
        'gas': 21000,
        # 'maxPriorityFeePerGas': w3.toWei(2, 'gwei')
    })
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    print("receipt:", transaction_receipt)
    print("receipt return value:", transaction_receipt.returnValue)
    print("test account balance:", w3.fromWei(w3.eth.get_balance(test_account_address), 'wei'))

# abi = [{"inputs":[],"name":"retrieve","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"int256","name":"num","type":"int256"}],"name":"store","outputs":[],"stateMutability":"nonpayable","type":"function"}]
# bytecode = "0x608060405234801561001057600080fd5b50610150806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c80632e64cec11461003b578063d80deced14610059575b600080fd5b610043610075565b60405161005091906100a1565b60405180910390f35b610073600480360381019061006e91906100ed565b61007e565b005b60008054905090565b8060008190555050565b6000819050919050565b61009b81610088565b82525050565b60006020820190506100b66000830184610092565b92915050565b600080fd5b6100ca81610088565b81146100d557600080fd5b50565b6000813590506100e7816100c1565b92915050565b600060208284031215610103576101026100bc565b5b6000610111848285016100d8565b9150509291505056fea2646970667358221220be19c6b9d3577f692e2e4198f65334fa2855b46e7e6dab3fdf63e7b50e86e47464736f6c634300080d0033"
#
# contract_address = "0x0b7b69657218f5243eeE1C1F4E26bE4592654163"
# if contract_address == "":
#     contract = deploy_contract(w3, abi, bytecode)
#     print("contract address:", contract.address)
# else:
#     contract = w3.eth.contract(address=contract_address, abi=abi)
#
#
# output = contract.functions.retrieve().call()
# print("before set:", output)
# # tx_hash = contract_instance.functions.store(223).transact()
# # tx_receipt = web3_instance.eth.wait_for_transaction_receipt(tx_hash)
# # output = contract_instance.functions.retrieve().call()
# # print("after set:", output)
# with open('output', 'rb') as f:
#     input_data = f.read()
#
# tx_hash = w3.eth.send_transaction({
#     # 'from': test_account_address,
#     'to': contract.address,
#     'data': input_data
# })
#
# print(tx_hash.hex())
#
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
#
# print("receipt:", tx_receipt)
# print("receipt return value:", tx_receipt.returnValue)
#
# output = contract.functions.retrieve().call()
# print('after set:', output)
#
# curl -v -X POST -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"eth_getTransactionReceipt","params":["0xe2bcf058e6c8102f5ee893cca243f2e4c9309819e23ecb0201f03ff316876f74"],"id":1}' http://192.168.229.143:8001