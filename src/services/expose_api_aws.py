import awsgi
from flask_restx import Api
from flask import Flask

from services.resources.user_api_resources import users_ns
from services.resources.group_api_resources import groups_ns
from services.resources.user_group_resources import user_groups_ns
from services.resources.auth_api_resources import auth_ns

app = Flask(__name__)

api = Api(app)

api.add_namespace(users_ns)
api.add_namespace(groups_ns)
api.add_namespace(user_groups_ns)
api.add_namespace(auth_ns)

def api_using_aws_lambda(event, context):
    return awsgi.response(app, event, context)
