from flask import request
from flask_restx import Namespace, Resource, fields
from http import HTTPStatus

from services.user_auth import CognitoAuth

auth_ns = Namespace('auth', description='Authentication operations')

cognito = CognitoAuth()

auth_model = auth_ns.model('LoginModel', {
    'username': fields.String(required=True, description='The username of the user'),
    'password': fields.String(required=False, description='The password of the user')
})


@auth_ns.route('/login')
class LoginResource(Resource):
    @auth_ns.expect(auth_model)
    def post(self):
        data = request.json
        username = username = ''.join(filter(str.isalnum, data.get('username', '')))
        password = data.get('password')

        response = cognito.authenticate_user(username, password)
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.UNAUTHORIZED


@auth_ns.route('/validate_token')
class ValidateTokenResource(Resource):
    @auth_ns.param('token', 'The token to validate', _in='formData')
    def post(self):
        data = request.form
        token = data.get('token')
        response = cognito.validate_token(token)
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.UNAUTHORIZED

@auth_ns.route('/validate_token_by_group')
class ValidateTokenResourceByGroup(Resource):
    @auth_ns.param('group_name', 'Group Name for validate', _in='formData')
    def post(self):
        token = request.headers.get('Authorization')
        group_name = request.form.get('group_name')

        response = cognito.validate_token_permission(token, [group_name])
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.UNAUTHORIZED