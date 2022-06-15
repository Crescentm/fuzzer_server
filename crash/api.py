from flask import Blueprint, render_template
from flask_restx import Resource, Namespace, fields, errors
import logging
from database.mysql import get_cursor
from crash.error import *


crash_blueprint = Blueprint('crash', __name__, url_prefix='/crash', template_folder='./templates')
api = Namespace('crash', description='API for crashes')

crash_post_model = api.model("crashPostModel", {
    "job_id": fields.Integer(required=True, description="Job ID"),
    "type": fields.String(required=True, description="Crash type"),
    # overflow , potential overflow, truncation
    "backtrace": fields.String(required=True, description="Crash backtrace")
})

crash_get_model = api.model("crashGetModel", {
    "id": fields.Integer(required=True, description="Crash ID"),
    "job_id": fields.Integer(required=True, description="Job ID"),
    "type": fields.String(required=True, description="Crash type"),
    "backtrace": fields.String(required=True, description="Crash backtrace")
})


class CrashDAO(object):
    def __init__(self):
        pass

    def create(self, payload):
        crash_obj = {
            "job_id": payload['job_id'],
            "type": payload['type'],
            "backtrace": payload['backtrace']
        }
        cursor = get_cursor(dictionary=True)
        query = "INSERT INTO crashes(job_id, type, backtrace) " \
                "value (%(job_id)s, %(type)s, %(backtrace)s)"

        logging.debug(f"Create crash '{payload['job_id']}'")

        cursor.execute(query, crash_obj)
        query = "SELECT * FROM crashes where job_id=%s"
        cursor.execute(query, (payload['job_id'],))
        result = cursor.fetchall()
        if len(result) != 1:
            error_msg = "Failed to get crash '{}' after creation".format(payload['job_id'])
            logging.error(error_msg)
            raise CrashCreateError(error_msg)

        return result[0]

    def get(self, id):
        cursor = get_cursor(dictionary=True)
        query = "SELECT * FROM crashes where id like %s"
        crash_id = id if id else "%"
        cursor.execute(query, (crash_id,))
        result = cursor.fetchall()
        if id:
            # return one result
            if len(result) != 1:
                err_msg = "Crash {} not exist".format(crash_id)
                logging.error(err_msg)
                raise CrashGetError(err_msg)

            return result[0]
        else:
            # return result list
            return result


crash_dao = CrashDAO()


@api.route('/')
class CrashRouter(Resource):
    @api.doc('Upload new crash', response={201: "Uploaded", 400: "Bad request"})
    @api.expect(crash_post_model)
    @api.marshal_with(crash_get_model)
    def post(self):
        try:
            result = crash_dao.create(api.payload)
        except CrashCreateError as e:
            errors.abort(code=400, message=str(e))
        return result

    @api.doc('Get all crashes', response={200: "ok"})
    @api.marshal_list_with(crash_get_model)
    def get(self):
        try:
            result = crash_dao.get(id=None)
        except CrashGetError as e:
            # should never execute
            errors.abort(code=502, message=str(e))
        return result


# @api.route('/<int:id>/')
# class CrashObjRouter(Resource):
#     @api.doc()

@crash_blueprint.route('/')
@crash_blueprint.route('/index/')
def crash_index_view():
    return render_template('crashes.html')
