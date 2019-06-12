import logging

import boto3
from crhelper import CfnResource

logger = logging.getLogger(__name__)
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL')
client = boto3.client('cognito-idp')


@helper.create
def create(event, context):
    logger.info("Got Create")

    user_pool_id, client_name, provider_name = _get_properties(event)
    client_id = ''

    if not client_name:
        raise Exception('Must provide a "ClientName" value in properties.')

    response_create_user_pool_client = client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=client_name,
        GenerateSecret=True
    )
    logger.info(response_create_user_pool_client)

    response_list_user_pool_clients = client.list_user_pool_clients(
        UserPoolId=user_pool_id
    )
    for i in response_list_user_pool_clients['UserPoolClients']:
        if i['ClientName'] == client_name:
            client_id = i['ClientId']

    response_update_user_pool_client = client.update_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id,
        SupportedIdentityProviders=[
            provider_name,
        ],
        CallbackURLs=[
            'https://application.url/login',
        ],
        LogoutURLs=[
            'https://application.url/logout'
        ],
        AllowedOAuthFlows=[
            'code'
        ],
        AllowedOAuthScopes=[
            'phone',
            'email',
            'openid'
        ],
        AllowedOAuthFlowsUserPoolClient=True
    )
    logger.info(response_update_user_pool_client)

    helper.Data.update({"ClientName": client_name})

    return helper.PhysicalResourceId


@helper.update
def update(event, context):
    logger.info("Got Update")

    user_pool_id, client_name, provider_name = _get_properties(event)
    client_id = ''
    old_client_name = event['OldResourceProperties']['ClientName']
    old_client_id = ''

    if not client_name:
        raise Exception('Must provide a "ClientName" value in properties.')

    response_create_user_pool_client = client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=client_name,
        GenerateSecret=True
    )
    logger.info(response_create_user_pool_client)

    response_list_user_pool_clients = client.list_user_pool_clients(
        UserPoolId=user_pool_id
    )
    for i in response_list_user_pool_clients['UserPoolClients']:
        if i['ClientName'] == client_name:
            client_id = i['ClientId']
        elif i['ClientName'] == old_client_name:
            old_client_id = i['ClientId']

    response_delete_user_pool_client = client.delete_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=old_client_id
    )
    logger.info(response_delete_user_pool_client)

    response_update_user_pool_client = client.update_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id,
        ClientName=client_name,
        SupportedIdentityProviders=[
            provider_name,
        ],
        CallbackURLs=[
            'https://application.url/login',
        ],
        LogoutURLs=[
            'https://application.url/logout'
        ],
        AllowedOAuthFlows=[
            'code'
        ],
        AllowedOAuthScopes=[
            'phone',
            'email',
            'openid'
        ],
        AllowedOAuthFlowsUserPoolClient=True
    )
    logger.info(response_update_user_pool_client)

    helper.Data.update({"ClientName": client_name})

    return helper.PhysicalResourceId


@helper.delete
def delete(event, context):
    logger.info("Got Delete")

    user_pool_id, client_name, provider_name = _get_properties(event)
    client_id = ''

    response_list_user_pool_clients = client.list_user_pool_clients(
        UserPoolId=user_pool_id
    )

    for i in response_list_user_pool_clients['UserPoolClients']:
        if i['ClientName'] == client_name:
            client_id = i['ClientId']

    response_delete_user_pool_client = client.delete_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id
    )
    logger.info(response_delete_user_pool_client)


def handler(event, context):
    helper(event, context)


def _get_properties(event):
    properties = event.get('ResourceProperties', None)

    user_pool_id = properties.get('UserPoolId')
    client_name = properties.get('ClientName')
    provider_name = properties.get('ProviderName')

    return user_pool_id, client_name, provider_name
