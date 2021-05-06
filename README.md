# OAuthLambda

Basic AWS Lambda project demonstrating use of OAuth2 for API auth


## Note on resources

I have not yet built out configs for all resources. Some things are still
manual and thus have to be manually destroyed. If you follow all the
instructions here, you will have:

 * 3 Lambdas
 * 1 Cognito user pool
 * 1 dynamodb table


Some of these things may incur AWS charges. You will also need to setup an IAM
Lambda execution role (see the serverless docs) and an IAM user who has:

 * Writable access to dynamodb
 * AmazonESCognitoAccess


## Getting started

Create the appropriate .env file (e.g. .env or .env.{stage}). Unless you
already have a user pool created, you will not have that ID yet to set in the
env file.

Create a dynamodb table in your AWS account that matches the env config in
serverless.yml. E.g.: dev-OAuthTokens.

```
 $ npm install
 $ sls deploy --stage dev
```

Get the user pool ID from the Cognito User Pools console and set it as the
`OAUTHAPI_COGNITO_USER_POOL` environment varialble. Re-deploy:

```
 $ sls deploy --stage dev
```


You will see output much like the following, but unique to your deployment:

```
Serverless: Stack create finished...
Service Information
service: oauthapi
stage: dev
region: us-east-1
stack: oauthapi-dev
resources: 21
api keys:
  None
endpoints:
  GET - https://pjdh9f2pv8.execute-api.us-east-1.amazonaws.com/hello
  POST - https://pjdh9f2pv8.execute-api.us-east-1.amazonaws.com/token
  POST - https://pjdh9f2pv8.execute-api.us-east-1.amazonaws.com/token-refresh
functions:
  hello: oauthapi-dev-hello
  test: oauthapi-dev-token
  refresh_token: oauthapi-dev-refresh_token
```

Copy the base path of the endpoints and paste it into your env file (or
however you export things to your environment) as `API_ROOT` to be used by
client.py. E.g. from above:

**.env:**

```
API_ROOT=https://pjdh9f2pv8.execute-api.us-east-1.amazonaws.com
```


