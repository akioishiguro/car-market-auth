from config import Config
from utils.response_helper import ResponseHelper

class UserGroupManager:
    def __init__(self, client):
        self.client = client
        self.user_pool_id = Config.get('userPoolId')
        self.response_helper = ResponseHelper.response_helper

    def add_user_to_group(self, username, group_name):
        try:
            response = self.client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id,
                Username=username,
                GroupName=group_name
            )
            return self.response_helper(response, 'User added to group successfully', 'Error adding user to group')
        except Exception as e:
            return self.response_helper(None, '', str(e))

    def remove_user_from_group(self, username, group_name):
        try:
            response = self.client.admin_remove_user_from_group(
                UserPoolId=self.user_pool_id,
                Username=username,
                GroupName=group_name
            )
            return self.response_helper(response, 'User removed from group successfully', 'Error removing user from group')
        except Exception as e:
            return self.response_helper(None, '', str(e))

    def list_users_in_group(self, group_name):
        try:
            response = self.client.list_users_in_group(
                UserPoolId=self.user_pool_id,
                GroupName=group_name
            )
            return self.response_helper(response, 'Users listed successfully', 'Error listing users in group')
        except Exception as e:
            return self.response_helper(None, '', str(e))