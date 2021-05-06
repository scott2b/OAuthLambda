import datetime
import os
import secrets
import boto3

OAUTH2_ACCESS_TOKEN_BYTES = 32
OAUTH2_REFRESH_TOKEN_BYTES = 64

AWS_ACCESS_KEY_ID = os.environ['OAUTHAPI_AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['OAUTHAPI_AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ['OAUTHAPI_AWS_REGION']

dynamodb = boto3.resource('dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
OAUTH_TOKENS_TABLE = dynamodb.Table(os.environ['OAUTH_TOKENS_TABLE'])


def timestamp(string=False):
    ts = datetime.datetime.utcnow()
    if string:
        ts = ts.isoformat()
    return ts


def create_random_key(nbytes):
    """Create a URL safe secret token."""
    return secrets.token_urlsafe(nbytes)


def get_token_object(token):
    response = OAUTH_TOKENS_TABLE.get_item(
        Key={'token': token},
        ProjectionExpression='#token, #client_id, #expires_at, #scope, #type, #access_token',
        ExpressionAttributeNames={
            "#token": "token",
            "#client_id": "client_id",
            "#expires_at": "expires_at",
            "#scope": "scope",
            "#type": "type",
            "#access_token": "access_token"
        }
    )
    return response.get('Item')


def create_token(client_id, grant_type, scope='api'):
    assert grant_type == 'client_credentials', f'Unexpected grant type: {grant_type}'
    _access_token = create_random_key(OAUTH2_ACCESS_TOKEN_BYTES)
    _refresh_token = create_random_key(OAUTH2_REFRESH_TOKEN_BYTES)
    created_at = datetime.datetime.utcnow()
    refreshed_at = created_at
    # TODO: get these deltas from the config in cognito
    access_token_expires_at = created_at + datetime.timedelta(minutes=5)
    refresh_token_expires_at = created_at + datetime.timedelta(minutes=60)
    access_token = {
        'token': _access_token,
        'type': 'access',
        'client_id': client_id,
        'scope': 'scope',
        'expires_at': access_token_expires_at.isoformat()
    }
    OAUTH_TOKENS_TABLE.put_item(Item=access_token)
    refresh_token = {
        'token': _refresh_token,
        'type': 'refresh',
        'access_token': _access_token,
        'client_id': client_id,
        'scope': 'scope',
        'expires_at': refresh_token_expires_at.isoformat()
    }
    OAUTH_TOKENS_TABLE.put_item(Item=refresh_token)
    return {
        'access_token': _access_token,
        'token_type': 'bearer',
        'refresh_token': _refresh_token,
        'expires_in': 300
    }


def refresh_token(token, grant_type):
    assert grant_type == 'refresh_token', f'Unexpected grant type: {grant_type}'
    token_obj = get_token_object(token)
    if token_obj['expires_at'] < datetime.datetime.utcnow().isoformat():
        return { 'statusCode': 401, 'message': 'Token expired' }
    response = OAUTH_TOKENS_TABLE.delete_item(
        Key={ 'token': token_obj['access_token'] }
    )
    _access_token = create_random_key(OAUTH2_ACCESS_TOKEN_BYTES)
    now = datetime.datetime.utcnow()
    access_token_expires_at = now + datetime.timedelta(minutes=5)
    refresh_token_expires_at = now + datetime.timedelta(minutes=60)
    access_token = {
        'token': _access_token,
        'type': 'access',
        'client_id': token_obj['client_id'],
        'scope': token_obj['scope'],
        'expires_at': access_token_expires_at.isoformat()
    }
    OAUTH_TOKENS_TABLE.put_item(Item=access_token)
    r = OAUTH_TOKENS_TABLE.update_item(
        Key = { 'token': token },
        UpdateExpression = 'SET #expires_at=:expires_at, #access_token=:access_token',
        ExpressionAttributeNames={
            '#expires_at': 'expires_at',
            '#access_token': 'access_token'
        },
        ExpressionAttributeValues={
            ':expires_at': refresh_token_expires_at.isoformat(),
            ':access_token':  _access_token
        }
    )
    return {
        'access_token': _access_token,
        'token_type': 'bearer',
        'refresh_token': token,
        'expires_in': 300
    }
