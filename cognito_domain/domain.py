import logging

import boto3
from crhelper import CfnResource

logger = logging.getLogger(__name__)
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL')

client = boto3.client('cognito-idp')


@helper.create
def create(event, context):
    logger.info("Got Create")
    domain_name, user_pool_id = _get_properties(event)

    if not domain_name:
        raise Exception('Must provide a "Domain" value in properties.')

    response = client.create_user_pool_domain(
        Domain=domain_name,
        UserPoolId=user_pool_id
    )
    helper.Data.update({"DomainName": domain_name})

    return helper.PhysicalResourceId


@helper.update
def update(event, context):
    logger.info("Got Update")
    domain_name, user_pool_id = _get_properties(event)
    old_domain = event['OldResourceProperties']['DomainName']

    if old_domain != domain_name:
        response_delete = client.delete_user_pool_domain(
            Domain=old_domain,
            UserPoolId=user_pool_id
        )

        response_create = client.create_user_pool_domain(
            Domain=domain_name,
            UserPoolId=user_pool_id
        )
        helper.Data.update({"DomainName": domain_name})

    return helper.PhysicalResourceId


@helper.delete
def delete(event, context):
    logger.info("Got Delete")
    domain_name, user_pool_id = _get_properties(event)

    response = client.delete_user_pool_domain(
        Domain=domain_name,
        UserPoolId=user_pool_id
    )

    return helper.PhysicalResourceId


def handler(event, context):
    helper(event, context)


def _get_properties(event):
    properties = event.get('ResourceProperties', None)

    domain_name = properties.get('DomainName')
    user_pool_id = properties.get('UserPoolId')

    return domain_name, user_pool_id
