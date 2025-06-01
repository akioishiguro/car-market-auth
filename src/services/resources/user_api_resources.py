import boto3
from flask import request
from loguru import logger
from http import HTTPStatus
from flask_restx import Namespace, Resource, fields

from config import Config

from services.bearer_token_validation import auth
from services.user_manager import UserManager

PASSWORD_DEFAULT = Config.get('passwordDefault')
GROUP_NAME_DEFAULT = Config.get('groupNameDefault')

users_ns = Namespace(name='users', description='Gerenciamento de Usuários')

client = boto3.client(Config.get('awsClientCognito'), region_name=Config.get('awsRegion'))

user_manager = UserManager(client)

update_user_model = users_ns.model('User', {
    'username': fields.String(required=True, description='Username'),
    'attributes': fields.List(fields.Nested(users_ns.model('Attribute', {
        'Name': fields.String(required=True, description='Attribute name'),
        'Value': fields.String(required=True, description='Attribute value')
    })), required=True, description='List of attributes')
})

create_user_model = users_ns.model('User', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=False, description='Username'),
    'group_name': fields.String(required=False, description='Username'),
    'attributes': fields.List(fields.Nested(users_ns.model('Attribute', {
        'Name': fields.String(required=True, description='Attribute name'),
        'Value': fields.String(required=True, description='Attribute value')
    })), required=True, description='List of attributes')
})

response_model = users_ns.model('Response', {
    'status_success': fields.Boolean,
    'response': fields.Raw,
    'message': fields.String
})


@users_ns.route('/create_user')
class CreateUserResource(Resource):
    @auth.login_required
    @users_ns.expect(create_user_model)
    @users_ns.marshal_with(response_model)
    def post(self, password=PASSWORD_DEFAULT, group_name=GROUP_NAME_DEFAULT):
        logger.info(f'endpoint get_user was called with data {users_ns.payload} - by {auth.current_user()}')
        data = users_ns.payload
        if data.get('password'):
            password = data.get('password')
        if data.get('group_name'):
            group_name = data.get('group_name')
        response = user_manager.create_user(data['username'], password, data['attributes'], group_name)
        if response['status_success']:
            return response, HTTPStatus.CREATED
        else:
            return response, HTTPStatus.BAD_REQUEST

@users_ns.route('/get_user')
class GetUserResource(Resource):
    @auth.login_required
    @users_ns.marshal_with(response_model)
    @users_ns.param('username', 'The username of the user', _in='query')
    def get(self):
        username = request.args.get('username')
        logger.info(f'endpoint get_user was called with username {username}')

        response = user_manager.get_user(username)
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.NOT_FOUND

@users_ns.route('/update_user')
class UpdateUserResource(Resource):
    @auth.login_required
    @users_ns.expect(update_user_model)
    @users_ns.marshal_with(response_model)
    def put(self):
        logger.info(f'endpoint update_user was called with data {users_ns.payload}')

        data = users_ns.payload
        response = user_manager.update_user(data['username'], data['attributes'])
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.BAD_REQUEST

@users_ns.route('/delete_user')
class DeleteUserResource(Resource):
    @auth.login_required
    @users_ns.marshal_with(response_model)
    @users_ns.param('username', 'The username of the user', _in='query')
    def delete(self):
        username = request.args.get('username')
        logger.info(f'endpoint delete_user was called with username {username}')

        response = user_manager.delete_user(username)
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.NOT_FOUND

@users_ns.route('/list_all_users')
class ListAllUsersResource(Resource):
    @auth.login_required
    @users_ns.marshal_with(response_model)
    def get(self):
        logger.info('endpoint list_all_users was called')

        response = user_manager.list_all_users()
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.INTERNAL_SERVER_ERROR