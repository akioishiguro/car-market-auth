from flask import Flask
from loguru import logger
from waitress import serve
from flask_restx import Api

from services.resources.user_api_resources import users_ns
from services.resources.group_api_resources import groups_ns
from services.resources.user_group_resources import user_groups_ns
from services.resources.auth_api_resources import auth_ns
from services.resources.admin_api_resources import admin_users_ns

app = Flask(__name__)


class ApiService(object):
    HOST = '0.0.0.0'
    PORT = 8080

    def __init__(self):
        self.api = Api(app,
                       version='1.0',
                       title='API',
                       description='Descricao da API',
                       doc='/swagger/')

    def run(self):
        self.api.add_namespace(users_ns)
        self.api.add_namespace(groups_ns)
        self.api.add_namespace(user_groups_ns)
        self.api.add_namespace(auth_ns)
        self.api.add_namespace(admin_users_ns)
        logger.info('Serving on http://localhost:{}/swagger/'.format( self.PORT))
        serve(app, host=self.HOST, port=self.PORT)
