import json
import os
import boto3
import decimal
import jwt

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)
        
def decode_auth_token(token):
    try:
        payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Login please'
    except jwt.InvalidTokenError:
        return 'Invalid token. Login please'

def get_token(event):
    if 'Authorization' not in event['headers']:
        return None
    auth_header = event['headers']['Authorization']
    if auth_header:
        token = auth_header.split(" ")[1]
        return token
    return None

def decode_token(token):
    decoded = decode_auth_token(token)
    if isinstance(decoded, str):
        return decoded, False
    else:
        return decoded['sub'], True

def fetch(event, context):
    result = {}
    table = boto3.resource('dynamodb').Table(os.environ['ORDERS_TABLE'])
    token = get_token(event)
    if token:
        decoded, status = decode_token(token)
        if status:
            userid = decoded
            output = table.get_item(Key={'userid': userid})
            result['message'] = "success"
            result['output'] = output['Item']
        else:
            result['message'] = 'Authorization string empty'
    else:
        result['message'] = 'Server error'

    
    return {
        'statusCode': 200,
        'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
        'body': json.dumps(result, cls=DecimalEncoder)
    }