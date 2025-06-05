import boto3
from botocore.exceptions import ClientError
import hmac
import hashlib
import base64

from config import Config
from utils.response_helper import ResponseHelper

AUTHFLOW = 'USER_PASSWORD_AUTH'

client = boto3.client(Config.get('awsClientCognito'), region_name=Config.get('awsRegion'))


class CognitoAuth:
    def __init__(self):
        self.client = client
        self.client_id = Config.get('clientId')
        self.client_secret = Config.get('clientSecret')
        self.user_pool_id = Config.get('userPoolId')
        self.response_helper = ResponseHelper.response_helper

    @staticmethod
    def __get_secret_hash(username, client_id, client_secret):
        message = username + client_id
        dig = hmac.new(
            str(client_secret).encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()

    def authenticate_user(self, username: str, password: str):
        try:
            response = self.client.initiate_auth(
                AuthFlow=AUTHFLOW,
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password,
                    'SECRET_HASH': self.__get_secret_hash(username, self.client_id, self.client_secret)
                },
                ClientId=self.client_id
            )
            return self.response_helper(response, 'User authenticated successfully', 'Authentication failed')
        except self.client.exceptions.NotAuthorizedException as e:
            print(f'Error during authentication: {e}')
            return self.response_helper(None, '', 'Invalid username or password')
        except Exception as e:
            return self.response_helper(None, '', str(e))

    def validate_token(self, token: str) -> dict:
        if not token.startswith('Bearer '):
            return self.response_helper(None, '', 'Token must start with "Bearer "')

        token = token[len('Bearer '):]

        try:
            response = self.client.get_user(
                AccessToken=token
            )
            return self.response_helper(response, 'Token is valid', 'Token validation failed')
        except ClientError as e:
            return self.response_helper(None, '', f'Error: {e}')
        except Exception as e:
            return self.response_helper(None, '', str(e))

    def validate_token_permission(self, token: str, group_names: list) -> dict:
        try:
            if token.startswith('Bearer '):
                token = token[len('Bearer '):]

            response = self.client.get_user(
                AccessToken=token
            )
            username = response['Username']

            groups_response = self.client.admin_list_groups_for_user(
                Username=username,
                UserPoolId=self.user_pool_id
            )
            groups = [group['GroupName'] for group in groups_response['Groups']]

            for group_name in group_names:
                if group_name in groups:
                    return self.response_helper(response, f'User {username} has required permissions',
                                                'Permission validation failed')
                else:
                    raise ValueError(f'User {username} does not have required permissions')
            return self.response_helper(response, '', f'User {username} does not have required permissions')

        except ClientError as e:
            return self.response_helper('', '', f'Error: {e}')
        except Exception as e:
            return self.response_helper('', '', str(e))
