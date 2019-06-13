import logging

import boto3
from crhelper import CfnResource

logger = logging.getLogger(__name__)
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL')
client = boto3.client('cognito-idp')


@helper.create
def create(event, context):
    logger.info("Got Create")

    user_pool_id, provider_name, provider_type, provider_details, attribute_mapping = _get_resource_properties(event)

    return _create(user_pool_id, provider_name, provider_type, provider_details, attribute_mapping)


@helper.update
def update(event, context):
    logger.info("Got Update")

    user_pool_id, provider_name, provider_type, provider_details, attribute_mapping = _get_resource_properties(event)
    old_provider_name = event['OldResourceProperties']['ProviderName']

    _delete(user_pool_id, old_provider_name)

    return _create(user_pool_id, provider_name, provider_type, provider_details, attribute_mapping)


@helper.delete
def delete(event, context):
    logger.info("Got Delete")

    user_pool_id, provider_name, provider_type, provider_details, attribute_mapping = _get_resource_properties(event)

    _delete(user_pool_id, provider_name)


def handler(event, context):
    helper(event, context)


def _get_resource_properties(event):
    properties = event.get('ResourceProperties', None)

    user_pool_id = properties.get('UserPoolId')
    provider_name = properties.get('ProviderName')
    provider_type = properties.get('ProviderType')
    provider_details = properties.get('ProviderDetails')
    attribute_mapping = properties.get('AttributeMapping')

    return user_pool_id, provider_name, provider_type, provider_details, attribute_mapping


def _create(user_pool_id, provider_name, provider_type, provider_details, attribute_mapping):
    if not provider_details:
        raise Exception('Must provide a "MetadataURL" value in properties.')

    response = client.create_identity_provider(
        UserPoolId=user_pool_id,
        ProviderName=provider_name,
        ProviderType=provider_type,
        ProviderDetails={
            'MetadataURL': provider_details
        },
        AttributeMapping={
            'email': attribute_mapping
        }
    )
    helper.Data.update({"MetadataURL": provider_details})


def _delete(user_pool_id, provider_name):
    response_delete_identity_provider = client.delete_identity_provider(
        UserPoolId=user_pool_id,
        ProviderName=provider_name
    )
    logger.info(response_delete_identity_provider)
