from flask import Blueprint, render_template
from flask_restx import Resource, Namespace, fields, errors
import logging
from database.mysql import get_cursor
from corpus.error import *


corpus_blueprint = Blueprint('corpus', __name__, url_prefix='/corpus', template_folder='./templates')
api = Namespace('corpus', description='API for corpus')

corpus_post_model = api.model("corpusPostModel", {
    "job_id": fields.Integer(required=True, description="Job ID"),
    "file": fields.String(required=True, description="Base64 encoded corpus zip file")
})

corpus_get_model = api.model("corpusGetModel", {
    "id": fields.Integer(required=True, description="Corpus ID"),
    "name": fields.String(required=True, description="Corpus name"),
    "job_id": fields.Integer(required=True, description="Job ID"),
    "size": fields.String(required=True, description="corpus file size"),
    "update_time": fields.DateTime(required=True, description="corpus update time")
})


class CorpusDAO(object):
    def __init__(self):
        pass

    def create(self, payload):
        # TODO: save file to target path
        # TODO: get file size
        pass

    def get(self, cid=None):
        cursor = get_cursor(dictionary=True)
        query = "SELECT * FROM corpuses where id like %s"
        corpus_id = cid if cid else '%'
        cursor.execute(query, (corpus_id,))
        result = cursor.fetchall()
        cursor.close()
        if cid:
            # return one result
            if len(result) != 1:
                err_msg = "Failed to get corpus with id {}".format(corpus_id)
                logging.error(err_msg)
                raise CorpusGetError(err_msg)

            return result[0]
        else:
            # return result list
            return result


corpus_dao = CorpusDAO()


@api.route('/')
class CorpusRouter(Resource):
    @api.doc('get all corpus', response={200:"ok"})
    @api.marshal_list_with(corpus_get_model)
    def get(self):
        try:
            result = corpus_dao.get()
        except CorpusGetError as e:
            # should never execute
            errors.abort(code=400, message=str(e))
        return result

    @api.doc('Create new corpus', response={201: "Created", 400: "Bad request"})
    @api.expect(corpus_post_model)
    @api.marshal_with(corpus_get_model)
    def post(self):
        try:
            result = corpus_dao.create(api.payload)
        except CorpusCreateError as e:
            errors.abort(code=400, message=str(e))
        return result


@corpus_blueprint.route('/')
def corpus_index_view():
    return render_template('corpuses.html')
