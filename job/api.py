from flask import Blueprint, render_template, send_from_directory
from flask_restx import Resource, Namespace, fields, errors
import datetime
import logging
import datetime
import time
import os
import json
import subprocess
from job.error import JobCreateError, JobNotExistError
from database.mysql import get_cursor
from config.config_value import *
from pathlib import Path

# set blueprint and Namespace
job_blueprint = Blueprint('job', __name__, url_prefix='/job', template_folder='./templates')
api = Namespace('job', description='API for job actions')


# custom field
class AbiField(fields.Raw):
    def format(self, value):
        return value


# marshal model
job_post_model = api.model("JobPostModel", {
    "name": fields.String(required=True, description="Job name"),
    "abi": AbiField(required=True, description="abi array"),
    # "abi": fields.String(required=True, description="abi string"),
    "bytecodes": fields.String(required=True, description="contract bytecodes in hex string"),
    "data": fields.String(required=True, description="packed input data for constructor")
})

job_response_model = api.model("JobResponseModel", {
    "id": fields.Integer(required=True, description="Job id"),
    "name": fields.String(required=True, description="Job name"),
    "abi": AbiField(required=True, description="contract abi array"),
    # "abi": fields.String(required=True, description="abi string"),
    "address": fields.String(required=False, description="Deployed contract address")
})

test_request_model = api.model("TestRequestModel", {
    "id": fields.Integer(required=True, description="job id"),
    "input": fields.String(required=True, description="Input for this test")
})

test_response_model = api.model("TestResponseModel", {
    "id": fields.Integer(required=True, description="job id"),
    "response": fields.String(required=True, description="test response in json format")
})


class JobDAO(object):
    def __init__(self):
        pass

    def create(self, payload):
        if RUN_LOCAL:
            now_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            job_name = "{}.{}".format(payload['name'], now_time)
            cursor = get_cursor(dictionary=True)
            query = "INSERT INTO jobs (name, abi_path, bin_path) " \
                    "value (%(name)s, %(abi_path)s, %(bin_path)s)"
            job_path = os.path.join(
                os.path.join(NFS_PATH, JOB_SUB_PATH),
                job_name
            )
            abi_path = os.path.join(job_path, ABI_PATH)
            bin_path = os.path.join(job_path, BIN_PATH)

            # create job folder
            Path(job_path).mkdir(parents=True, exist_ok=True)
            Path(abi_path).mkdir(parents=True, exist_ok=True)
            Path(bin_path).mkdir(parents=True, exist_ok=True)

            # TODO: change permission

            # save abi file and bin file
            abi_file_name = os.path.join(abi_path, f"{payload['name']}.abi")
            bin_file_name = os.path.join(bin_path, f"{payload['name']}.bin")
            with open(abi_file_name, 'w') as f:
                logging.debug(f"save abi file to f{abi_file_name}")
                # obj = json.load(payload['abi'])
                # f.write(json.dumps(obj))
                # f.write(json.load(payload['abi']))
                logging.debug("abi: {}".format(payload['abi']))
                f.write(json.dumps(payload['abi']))

            with open(bin_file_name, 'w') as f:
                logging.debug(f"save bin file to f{bin_file_name}")
                f.write(payload['bytecodes'])


            job_obj = {
                "name": job_name,
                "abi_path": abi_file_name,
                "bin_path": bin_file_name
            }

            cursor.execute(query, job_obj)
            logging.debug(f"Create job '{job_name}'")

            get_query = "SELECT * FROM jobs where name = %s"
            cursor.execute(get_query, (job_name,))
            result = cursor.fetchall()
            cursor.close()
            if len(result) != 1:
                error_msg = "Failed to get job '{}' after creation".format(job_name)
                logging.error(error_msg)
                raise JobCreateError(error_msg)

            return result[0]

    def get(self, id=None):
        query = "SELECT * FROM jobs where id like %s"
        job_id = id if id else "%"
        cursor = get_cursor(dictionary=True)
        cursor.execute(query, (job_id,))
        result = cursor.fetchall()
        cursor.close()
        return result

    def run(self, id, input):
        cursor = get_cursor(dictionary=True)
        query = "SELECT * FROM jobs where id = %s"
        cursor.execute(query, (id,))
        result = cursor.fetchall()
        cursor.close()
        if len(result) != 1:
            err_msg = f"Job with id {id} not exist"
            logging.error(err_msg)
            raise JobNotExistError(err_msg)
        abi_path = result[0]['abi_path']
        bin_path = result[0]['bin_path']
        command = f"./evm --codefile {bin_path} --input {input} run"
        result = subprocess.check_output(command, shell=True)

        json_obj = json.loads(result)
        logging.debug("evm output: json {}, raw {}".format(json_obj, result))
        res = {
            'id': id,
            'response': json.dumps(json_obj)
        }
        return res



job_dao = JobDAO()


@api.route('/')
class JobRouter(Resource):
    @api.doc('Create a fuzz job', response={201: "Contract deployed", 400: "Bad request"})
    @api.expect(job_post_model)
    @api.marshal_with(job_response_model)
    def post(self):
        # RUN_ONLINE
        # w3 = ether.get_web3_instance()
        # try:
        #     contract_address = ether.deploy_contract(
        #         deploy_account=w3.eth.default_account,
        #         contract_abi=api.payload['abi'],
        #         contract_bin=api.payload['bytecodes'],
        #         constructor_input=api.payload['data']
        #     )
        #     response = {
        #         "abi": api.payload['abi'],
        #         "address": contract_address
        #     }
        #     return response, 201
        # except DeployError as e:
        #     errors.abort(code=400, message=str(e))
        try:
            result = job_dao.create(api.payload)
        except JobCreateError as e:
            errors.abort(code=400, message=str(e))

        return result

    @api.doc('Get all fuzz jobs', response={200: "ok"})
    @api.marshal_list_with(job_response_model)
    def get(self):
        try:
            # TODO: add Error object
            result = job_dao.get()
        except:
            pass
        return result


@api.route('/test/')
class JobTest(Resource):
    @api.doc("Test one job", response={200: "ok", 404: "not found"})
    # @api.expect(test_request_model, validation=True)
    @api.expect(test_request_model)
    @api.marshal_with(test_response_model)
    def post(self):
        # job_dao.run(id=api.payload['id'], input=api.)
        try:
            result = job_dao.run(**api.payload)
        except JobNotExistError as e:
            errors.abort(code=404, message=f"Job with id {api.payload['id']} not found")
        return result

@job_blueprint.route('/')
@job_blueprint.route('/index/')
def job_index_view():
    return render_template('index.html')

# @job_blueprint.route('/<path:path>')
# def send_static(path):
#     return send_from_directory('templates', path)
