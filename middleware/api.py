import datetime

from flask import Blueprint
from flask_restx import Resource, Namespace, fields, errors
import logging
import datetime
import middleware.ether
import time
import os
from middleware.error import DeployError, CallContractError
from database.mysql import get_cursor
from config.config_value import *
from pathlib import Path

# set blueprint and Namespace
middleware_blueprint = Blueprint('middleware', __name__, url_prefix='/middleware')
api = Namespace('middleware', description='API for interaction with private net')


# custom field
class AbiField(fields.Raw):
    def format(self, value):
        return value


# marshal model
tx_post_model = api.model("TransactionPostModel", {
    'address': fields.String(required=True, description="contract address"),
    'data': fields.String(required=True, description="packed input data for contract")
})

tx_response_model = api.model("TransactionResponseModel", {
    "transaction_hash": fields.String(required=True, description="Hash for the transaction"),
    "pc": fields.String(required=True, description="PC list separated by comma"),
    "cost": fields.String(required=True, description="cost list separated by comma"),
    "status": fields.String(required=True)
})


class TransactionDAO(object):
    def __init__(self):
        pass

    def get_transaction_by_hash(self, tx_hash):
        cursor = get_cursor(dictionary=True)
        query = "SELECT * FROM transactions WHERE transaction_hash=%s"
        cursor.execute(query, (tx_hash,))
        result = cursor.fetchall()
        return result

    def create(self, ret_obj):
        cursor = get_cursor(dictionary=True)
        query = "INSERT INTO transactions (transaction_hash, pc, cost, status) " \
                "value (%(transaction_hash)s, %(pc)s, %(cost)s, %(status)s)"
        cursor.execute(query, ret_obj)
        return


transaction_dao = TransactionDAO()


@api.route('/transactions')
class TransactionRouter(Resource):
    """
    GET input of one transaction
    POST send a new transaction with input from request body
    """
    @api.doc('Send a transaction with input from json',
             response={201: "Transaction created", 400: "Bad request", 500: "Internal server error"})
    @api.expect(tx_post_model)
    @api.marshal_with(tx_response_model)
    def post(self):
        try:
            tx_hash = ether.call_contract_with_wait(api.payload['address'], api.payload['data'])
        except CallContractError as e:
            errors.abort(code=400, message=str(e))

        max_attempts = 5
        delay_time = 1
        result = []
        for i in range(max_attempts):
            result = transaction_dao.get_transaction_by_hash(tx_hash=tx_hash)
            if len(result) != 0:
                break
            time.sleep(delay_time)
        if len(result) == 0:
            errors.abort(code=500, message="No response from Geth")

        return result

    def get(self):
        pass


@api.route('/transactions/return')
class TransactionReturnRouter(Resource):
    @api.doc('Post evm execution output')
    @api.expect(tx_response_model)
    def post(self):
        transaction_dao.create(api.payload)
        return None, 200
