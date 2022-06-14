import logging

import web3.exceptions
from web3 import Web3
from web3.middleware import geth_poa_middleware
from middleware.error import DeployError, CallContractError
from config.config_value import *

# web3_instance = None
# test_contract_address = ""


def connect(geth_http_url):
    w3 = Web3(Web3.HTTPProvider(geth_http_url))
    if w3.isConnected():
        logging.log("Connected to {}".format(geth_http_url))
        logging.log("Client version: {}".format(w3.clientVersion))
    else:
        logging.error("Failed to connect {}".format(geth_http_url))
        return None
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.eth.default_account = w3.eth.accounts[0]
    return w3


def get_web3_instance():
    # global web3_instance
    web3_instance = connect(GETH_HTTP_URL)
    if web3_instance is None:
        exit(1)
    return web3_instance


# def get_test_contract_address():
#     global test_contract_address
#     if test_contract_address == "":


def deploy_contract(deploy_account, contract_abi, contract_bin, constructor_input) -> str:
    """
    deploy a contract on private net
    :param string deploy_account:
    :param list contract_abi:
    :param string contract_bin: contract bin in hex string format
    :param string constructor_input: constructor input in hex string format, example: "0xdeadbeef"
    :return: contract address
    """
    w3 = get_web3_instance()
    contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bin)
    try:
        tx_hash = contract.constructor().transact({
            'from': deploy_account,
            'data': Web3.toBytes(hexstr=constructor_input)
        })
    except ValueError as e:
        err_msg = "Failed to deploy contract: {}".format(str(e))
        logging.error(err_msg)
        raise DeployError(err_msg)

    try:
        # TODO: add timeout option
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        logging.log("Deploy contract succeed to address: {}".format(tx_receipt.contractAddress))
        return tx_receipt.contractAddress

    except web3.exceptions.TimeExhausted:
        err_msg = "Time limit exceeded on deploying contract, transaction hash: {}".format(tx_hash)
        logging.error(err_msg)
        raise DeployError(err_msg)

    return ""


def call_contract(contract_address, data):
    """
    :param string contract_address: target contract address
    :param string data: packed data field for transaction
    :return: transaction hash
    """
    w3 = get_web3_instance()
    # test account settings
    test_account_address = w3.eth.default_account
    try:
        tx_hash = w3.eth.send_transaction({
            'from': test_account_address,
            'to': contract_address,
            'data': data
        })
        return tx_hash
    except ValueError as e:
        err_msg = "Call contract failed: {}".format(str(e))
        logging.error(err_msg)
        raise CallContractError(err_msg)

    return ""


def call_contract_with_wait(contract_address, data):
    w3 = get_web3_instance()
    # test account settings
    test_account_address = w3.eth.default_account
    try:
        tx_hash = w3.eth.send_transaction({
            'from': test_account_address,
            'to': contract_address,
            'data': data
        })
    except ValueError as e:
        err_msg = "Call contract failed: {}".format(str(e))
        logging.error(err_msg)
        raise CallContractError(err_msg)

    try:
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash
    except web3.exceptions.TimeExhausted as e:
        err_msg = "Call contract failed: time limit exceeded {}: {}".format(tx_hash, str(e))
        logging.error(err_msg)
        raise CallContractError(err_msg)

    return ""
