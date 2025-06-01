from flask_httpauth import HTTPTokenAuth

from config import Config
from services.user_auth import CognitoAuth

auth = HTTPTokenAuth(scheme='Bearer')

cognito_auth = CognitoAuth()

GROUP_NAME = Config.get_list('groupsWithAccessPermissions')


@auth.verify_token
def verify_token(token):
    if token:
        response = cognito_auth.validate_token_permission(token, GROUP_NAME)
        if response['status_success']:
            return response['message']
