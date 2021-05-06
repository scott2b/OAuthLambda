import base64
import datetime
from dataclasses import dataclass
from . import identity
from . import oauth


### Utilities

@dataclass
class OAuth2TokenRequest():
    grant_type: str
    client_id: str
    client_secret: str


@dataclass
class OAuth2TokenRefreshRequest():
    grant_type: str
    refresh_token: str
    allow_redirects: str


def validate_oauth_request(event):
    """requests-oauthlib sends its POST data via forms. You may need to do
    something different if e.g. your client library sends JSON data.
    """
    assert event['isBase64Encoded'], 'Expected base64 encoded form body'
    body = event['body']
    payload = base64.b64decode(body).decode('utf-8')
    data = { kv.split('=')[0]: kv.split('=')[1] for kv in payload.split('&') }
    grant_type = data['grant_type']
    if grant_type == 'client_credentials':
        return OAuth2TokenRequest(**data)
    elif grant_type == 'refresh_token':
        return OAuth2TokenRefreshRequest(**data)
    else:
        raise Exception('Unexpected grant type')


### Endpoints


def token(event, context):
    req = validate_oauth_request(event)
    client_info = identity.get_client_info(req.client_id)
    if not req.client_id == client_info['ClientId'] and req.client_secret == client_info['ClientSecret']:
        return { 'statusCode': 401, 'body': '{"message": "Invalid client credentials"}' }
    token = oauth.create_token(req.client_id, req.grant_type, scope='api')
    return token


def refresh_token(event, context):
    req = validate_oauth_request(event)
    return oauth.refresh_token(req.refresh_token, req.grant_type)


def hello(event, context, require_auth=True):
    if require_auth:
        auth = event['headers']['authorization']
        bearer = auth.split()
        assert bearer[0] == 'Bearer'
        access_token = bearer[1]
        token_obj = oauth.get_token_object(access_token)        
        if token_obj['expires_at'] < datetime.datetime.utcnow().isoformat():
            return { 'statusCode': 401, 'message': 'Token expired' }
        return {
            'message': f'hello, your access token is {access_token}'
        }
    else:
        return { 'message': 'No auth' }

