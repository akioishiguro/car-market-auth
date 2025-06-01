import json
from utils.datetime_converter import datetime_converter

class ResponseHelper:
    @staticmethod
    def response_helper(response, message_success: str, message_error: str):
        if response:
            if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
                return {
                    'status_success': True,
                    'message': message_success,
                    'response': json.loads(json.dumps(response, default=datetime_converter))
                }
            else:
                return {
                    'status_success': False,
                    'message': message_error,
                    'response': json.loads(json.dumps(response, default=datetime_converter))
                }
        else:
            return {
                'status_success': False,
                'message': message_error,
                'response': None
            }