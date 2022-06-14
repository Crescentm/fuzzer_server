import datetime
import logging
from flask import Flask, Blueprint
from flask_restx import Api

from middleware.api import middleware_blueprint, api as middleware_api
from job.api import job_blueprint, api as job_api

app = Flask(__name__)

api_blueprint = Blueprint("api", __name__, url_prefix='/api')
api = Api(api_blueprint, version="1.0", title="Fuzzer api")
api.add_namespace(middleware_api)
api.add_namespace(job_api)

app.register_blueprint(job_blueprint)
app.register_blueprint(api_blueprint)
# set logging
time = datetime.datetime.now().strftime('%Y-%m-%d')
filename = '{}.{}'.format('log', time)
logging.basicConfig(filename=filename, format='%(levelname)s:%(asctime)s:%(message)s', level=logging.DEBUG)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
