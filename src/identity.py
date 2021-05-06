import os
import boto3


# You may be able to give permisssions to these resources directly to the
# lambda execution role and so remove the explicit keys, but I've had
# better luck keeping these things separate.

AWS_ACCESS_KEY_ID = os.environ['OAUTHAPI_AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['OAUTHAPI_AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ['OAUTHAPI_AWS_REGION']

idp_client = boto3.client('cognito-idp',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
COGNITO_USER_POOL = os.environ['OAUTHAPI_COGNITO_USER_POOL']


def get_client_info(client_id):
    response = idp_client.describe_user_pool_client(
        UserPoolId=COGNITO_USER_POOL,
        ClientId=client_id
    )
    return response['UserPoolClient']
