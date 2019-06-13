import logging

import boto3
from crhelper import CfnResource

logger = logging.getLogger(__name__)
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL')
client = boto3.client('cognito-idp')


@helper.create
def create(event, context):
    logger.info("Got Create")

    user_pool_id, client_name, provider_name, callback_urls, logout_urls = _get_resource_properties(event)

    return _create(user_pool_id, client_name, provider_name, callback_urls, logout_urls)


@helper.update
def update(event, context):
    logger.info("Got Update")

    user_pool_id, client_name, provider_name, callback_urls, logout_urls = _get_resource_properties(event)
    old_client_name = event['OldResourceProperties']['ClientName']

    _delete(user_pool_id, old_client_name)

    return _create(user_pool_id, client_name, provider_name, callback_urls, logout_urls)


@helper.delete
def delete(event, context):
    logger.info("Got Delete")

    user_pool_id, client_name, provider_name, callback_urls, logout_urls = _get_resource_properties(event)

    _delete(user_pool_id, client_name)


def handler(event, context):
    helper(event, context)


def _get_resource_properties(event):
    properties = event.get('ResourceProperties', None)
    user_pool_id = properties.get('UserPoolId')
    client_name = properties.get('ClientName')
    provider_name = properties.get('ProviderName')
    callback_urls = properties.get('CallbackURLs')
    logout_urls = properties.get('LogoutURLs')

    return user_pool_id, client_name, provider_name, callback_urls, logout_urls


def _create(user_pool_id, client_name, provider_name, callback_urls, logout_urls):
    response_create_user_pool_client = client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=client_name,
        GenerateSecret=True
    )
    logger.info(response_create_user_pool_client)

    response_list_user_pool_clients = client.list_user_pool_clients(
        UserPoolId=user_pool_id
    )

    client_id = next(
        x['ClientId'] for x in response_list_user_pool_clients['UserPoolClients'] if x['ClientName'] == client_name)

    response_update_user_pool_client = client.update_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id,
        SupportedIdentityProviders=[
            provider_name
        ],
        CallbackURLs=callback_urls,
        LogoutURLs=logout_urls,
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


def _delete(user_pool_id, client_name):
    response_list_user_pool_clients = client.list_user_pool_clients(
        UserPoolId=user_pool_id
    )

    client_id = next(
        x['ClientId'] for x in response_list_user_pool_clients['UserPoolClients'] if x['ClientName'] == client_name)

    response_delete_user_pool_client = client.delete_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id
    )
    logger.info(response_delete_user_pool_client)
