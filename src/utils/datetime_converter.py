from datetime import datetime

def datetime_converter(payload):
    if isinstance(payload, datetime):
        return payload.isoformat()
    raise TypeError(f'Object of type {payload.__class__.__name__} is not JSON serializable')
