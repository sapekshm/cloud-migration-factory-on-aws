#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: Apache-2.0


import json
import boto3
import botocore
import os
import logging
import urllib.parse

logging.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s', level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if 'cors' in os.environ:
    cors = os.environ['cors']
else:
    cors = '*'

default_http_headers = {
    'Access-Control-Allow-Origin': cors,
    'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload',
    'Content-Security-Policy': "base-uri 'self'; upgrade-insecure-requests; default-src 'none'; object-src 'none'; connect-src none; img-src 'self' data:; script-src blob: 'self'; style-src 'self'; font-src 'self' data:; form-action 'self';"
}


def create_groups(body, client):
    errors = []
    for group in body['groups']:
        try:
            if 'group_name' in group:
                logger.info("Created group '%s'." % group['group_name'])
                client.create_group(
                    GroupName=group['group_name'],
                    UserPoolId=os.environ['userpool_id']
                )
                logger.info("Created group '%s'." % group)
            else:
                logger.info("group_name not provided for group object in POST '%s'." % group)
                errors.append("group_name not provided for group object in provided '%s'." % group)
        except client.exceptions.GroupExistsException:
            logger.error("A group already exists with the name '%s'." % group['group_name'])
            errors.append("A group already exists with the name '%s'." % group['group_name'])
        except client.exceptions.NotAuthorizedException:
            logger.error("Group update Lambda does not have permission to update groups "
                         "in pool %s. Cancelling update." % os.environ['userpool_id'])
            errors.append("Group update Lambda does not have permission to update groups "
                          "in pool %s. Cancelling update." % os.environ['userpool_id'])
            raise
        except botocore.exceptions.ClientError as boto_client_error:
            # Error not specific boto client error.
            logger.error(boto_client_error)
            errors.append("Internal error.")
        except Exception as unknown_error:
            logger.error(unknown_error)
            errors.append("Internal error.")
    return errors


def lambda_handler(event, _):
    client = boto3.client('cognito-idp')
    if 'body' in event and event['body']:
        body = json.loads(event['body'])
    else:
        body = None
    errors = []

    if event['httpMethod'] == 'DELETE' and 'pathParameters' in event and 'group_name' in event['pathParameters']:
        client.delete_group(
            GroupName=urllib.parse.unquote(event['pathParameters']['group_name']),
            UserPoolId=os.environ['userpool_id']
        )
        logger.info("Deleted group '%s'." % event['pathParameters']['group_name'])
    elif 'groups' in body and event['httpMethod'] == 'POST':
        errors = create_groups(body, client)

    if len(errors) > 0:
        return {'headers': {**default_http_headers},
                'statusCode': 400,
                'body': json.dumps(errors)
                }
    else:
        return {'headers': {**default_http_headers},
                'statusCode': 200
                }
