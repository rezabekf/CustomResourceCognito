import logging

import boto3
from crhelper import CfnResource

logger = logging.getLogger(__name__)
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

client = boto3.client('cognito-idp')


@helper.create
def create(event, context):
    logger.info("Got Create")
    user_pool_id, provider_name, provider_type, provider_details, attribute_mapping = _get_properties(event)

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
            'email': 'email'
        }
    )
    helper.Data.update({"MetadataURL": provider_details})

    return helper.PhysicalResourceId


@helper.update
def update(event, context):
    logger.info("Got Update")
    user_pool_id, provider_name, provider_type, provider_details, attribute_mapping = _get_properties(event)

    response = client.delete_identity_provider(
        UserPoolId=user_pool_id,
        ProviderName=provider_name
    )

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
            'email': 'email'
        }
    )
    helper.Data.update({"MetadataURL": provider_details})

    return helper.PhysicalResourceId


@helper.delete
def delete(event, context):
    logger.info("Got Delete")
    user_pool_id, provider_name, provider_type, provider_details, attribute_mapping = _get_properties(event)

    response = client.delete_identity_provider(
        UserPoolId=user_pool_id,
        ProviderName=provider_name
    )

    return helper.PhysicalResourceId


def handler(event, context):
    helper(event, context)


def _get_properties(event):
    properties = event.get('ResourceProperties', None)

    user_pool_id = properties.get('UserPoolId')
    provider_name = properties.get('ProviderName')
    provider_type = properties.get('ProviderType')
    provider_details = properties.get('ProviderDetails')
    attribute_mapping = properties.get('AttributeMapping')

    return user_pool_id, provider_name, provider_type, provider_details, attribute_mapping
