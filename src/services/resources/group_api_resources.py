import boto3
from flask import request
from loguru import logger
from flask_restx import Namespace, Resource, fields
from http import HTTPStatus

from config import Config
from services.bearer_token_validation import auth
from services.group_manager import GroupManager

groups_ns = Namespace(name='groups', description='Gerenciamento de Grupos')

client = boto3.client(Config.get('awsClientCognito'), region_name=Config.get('awsRegion'))
group_manager = GroupManager(client)

create_group_model = groups_ns.model('Group', {
    'group_name': fields.String(required=True, description='Group name'),
    'description': fields.String(required=False, description='Group description')
})

response_model = groups_ns.model('Response', {
    'status_success': fields.Boolean,
    'response': fields.Raw,
    'message': fields.String
})


@groups_ns.route('/create_group')
class CreateGroupResource(Resource):
    @auth.login_required
    @groups_ns.expect(create_group_model)
    @groups_ns.marshal_with(response_model)
    def post(self):
        logger.info(f'endpoint create_group was called with data {groups_ns.payload}')

        data = groups_ns.payload
        response = group_manager.create_group(data['group_name'], data.get('description', ''))
        if response['status_success']:
            return response, HTTPStatus.CREATED
        else:
            return response, HTTPStatus.BAD_REQUEST


@groups_ns.route('/get_group')
class GetGroupResource(Resource):
    @auth.login_required
    @groups_ns.marshal_with(response_model)
    @groups_ns.param('group_name', 'The name of the group', _in='query')
    def get(self):
        group_name = request.args.get('group_name')
        logger.info(f'endpoint get_group was called with group_name {group_name}')

        response = group_manager.get_group(group_name)
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.NOT_FOUND


@groups_ns.route('/update_group')
class UpdateGroupResource(Resource):
    @auth.login_required
    @groups_ns.expect(create_group_model)
    @groups_ns.marshal_with(response_model)
    def put(self):
        logger.info(f'endpoint update_group was called with data {groups_ns.payload}')

        data = groups_ns.payload
        response = group_manager.update_group(data['group_name'], data.get('description', ''))
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.BAD_REQUEST


@groups_ns.route('/delete_group')
class DeleteGroupResource(Resource):
    @auth.login_required
    @groups_ns.marshal_with(response_model)
    @groups_ns.param('group_name', 'The name of the group', _in='query')
    def delete(self):
        group_name = request.args.get('group_name')
        logger.info(f'endpoint delete_group was called with group_name {group_name}')

        response = group_manager.delete_group(group_name)
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.NOT_FOUND


@groups_ns.route('/list_all_groups')
class ListAllGroupsResource(Resource):
    @auth.login_required
    @groups_ns.marshal_with(response_model)
    def get(self):
        logger.info('endpoint list_all_groups was called')

        response = group_manager.list_all_groups()
        if response['status_success']:
            return response, HTTPStatus.OK
        else:
            return response, HTTPStatus.INTERNAL_SERVER_ERROR