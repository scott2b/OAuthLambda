import os
import time
import oauthlib
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import MissingTokenError
from requests_oauthlib import OAuth2Session


AWS_ACCESS_KEY_ID=os.environ['OAUTHAPI_AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY=os.environ['OAUTHAPI_AWS_SECRET_ACCESS_KEY']
BASE_URL = os.environ['API_ROOT'] + '/'
TOKEN_URL = BASE_URL + 'token'
REFRESH_URL = BASE_URL + 'token-refresh'
HELLO_URL = BASE_URL + 'hello'
app_id = os.environ['OAUTHAPI_CLIENT_APP_ID']
app_secret = os.environ['OAUTHAPI_CLIENT_APP_SECRET']


TOKEN = None


def fetch_api_token():
    backend = BackendApplicationClient(client_id=app_id)
    oauth = OAuth2Session(client=backend)
    try:
        token = oauth.fetch_token(
            token_url=TOKEN_URL,
            client_id=app_id,
            client_secret=app_secret,
            include_client_id=True)
    except MissingTokenError:
        # oauthlib gives the same error regardless of the problem
        print('Something went wrong, please check your client credentials.')
        raise
    print(token)
    return token


def token_saver(token):
    global TOKEN
    print("You'll want to save the token somehow.")
    TOKEN = token


def main():
    global TOKEN
    print('Fetching token from endpoint:', TOKEN_URL)
    TOKEN = fetch_api_token()
    print('Received token:', TOKEN)
    print('Creating client for token.')
    client = OAuth2Session(app_id, token=TOKEN,
                auto_refresh_url=REFRESH_URL, auto_refresh_kwargs={},
                token_updater=token_saver)
    print('Access token times out after 5 minutes. Looping just to show that '
          'token refresh works. Ctl-C to quit.')
    while True:
        print(client.get(HELLO_URL).json())
        time.sleep(30)


if __name__=='__main__':
    main()
