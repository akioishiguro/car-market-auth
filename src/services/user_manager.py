from config import Config
from utils.response_helper import ResponseHelper
from utils.check_document import validate_document
from services.user_group_manager import UserGroupManager

MESSAGE_ACTION = 'SUPPRESS'

class UserManager:
    def __init__(self, client):
        self.client = client
        self.user_pool_id = Config.get('userPoolId')
        self.response_helper = ResponseHelper.response_helper

    def create_user(self, username, password, attributes: list[dict], group_name):
        try:
            check_document = validate_document(username)
            if check_document.get('status'):
                username = check_document.get('document')
                response = self.client.admin_create_user(
                    UserPoolId=self.user_pool_id,
                    Username=username,
                    UserAttributes=attributes,
                    TemporaryPassword=password,
                    MessageAction=MESSAGE_ACTION
                )

                self.client.admin_set_user_password(
                    UserPoolId=self.user_pool_id,
                    Username=username,
                    Password=password,
                    Permanent=True
                )

                user_group_manager = UserGroupManager(self.client)
                user_group_manager.add_user_to_group(username, group_name)

                return self.response_helper(response, 'User created successfully', 'Error creating user')
            else:
                return self.response_helper(None, '', 'The provided CPF is invalid')
        except self.client.exceptions.UsernameExistsException:
            return self.response_helper(None, '', 'User already exists')
        except self.client.exceptions.InvalidPasswordException:
            return self.response_helper(None, '', 'Password must have uppercase characters')
        except Exception as e:
            print(e)

    def get_user(self, username):
        try:
            response = self.client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            return self.response_helper(response, 'User found successfully', 'Error fetching user')
        except self.client.exceptions.UserNotFoundException:
            return self.response_helper(None, '', 'User not found')
        except Exception as e:
            print(e)

    def update_user(self, username, attributes: list[dict]):
        try:
            response = self.client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=attributes
            )
            return self.response_helper(response, 'User updated successfully', 'Error updating user')
        except self.client.exceptions.UserNotFoundException:
            return self.response_helper(None, '', 'User not found')
        except self.client.exceptions.InvalidParameterException:
            return self.response_helper(None, '', 'Invalid parameters')
        except Exception as e:
            print(e)
            return self.response_helper(None, '', 'Error updating user')

    def delete_user(self, username):
        try:
            response = self.client.admin_delete_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            return self.response_helper(response, 'User deleted successfully', 'Error deleting user')
        except self.client.exceptions.UserNotFoundException:
            return self.response_helper(None, '', 'User not found')
        except Exception as e:
            print(e)
            return self.response_helper(None, '', 'Error deleting user')

    def list_all_users(self):
        try:
            response = self.client.list_users(
                UserPoolId=self.user_pool_id
            )
            return self.response_helper(response, 'Users found successfully', 'Error loading users')
        except Exception as e:
            print(e)
            return self.response_helper(None, '', 'Error loading users')