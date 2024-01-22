#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: Apache-2.0


import os
import simplejson as json
import boto3
import datetime
from boto3.dynamodb.conditions import Key, Attr
from policy import MFAuth

if 'cors' in os.environ:
    cors = os.environ['cors']
else:
    cors = '*'

default_http_headers = {
    'Access-Control-Allow-Origin': cors,
    'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload',
    'Content-Security-Policy': "base-uri 'self'; upgrade-insecure-requests; default-src 'none'; object-src 'none'; connect-src none; img-src 'self' data:; script-src blob: 'self'; style-src 'self'; font-src 'self' data:; form-action 'self';"
}
application = os.environ['application']
environment = os.environ['environment']

schema_table_name = '{}-{}-schema'.format(application, environment)
schema_table = boto3.resource('dynamodb').Table(schema_table_name)


def process_item(items, schema, schema_notifications, default_date, last_change_date, date_format):
    if 'lastModifiedTimestamp' in items['Item']:
        dt_object = datetime.datetime.strptime(items['Item']['lastModifiedTimestamp'], date_format)
        if dt_object > last_change_date:
            last_change_date = dt_object
        schema_notifications['versions'].append(
            {
                'schema': schema,
                'lastModifiedTimestamp': items['Item']['lastModifiedTimestamp']
            })
    else:
        schema_notifications['versions'].append(
            {
                'schema': schema,
                'lastModifiedTimestamp': default_date.isoformat()
            })
    return last_change_date


def lambda_handler(event, _):
    if event['httpMethod'] == 'GET':
        resp_server = schema_table.get_item(Key={'schema_name': 'server'})
        resp_app = schema_table.get_item(Key={'schema_name': 'app'})
        resp_wave = schema_table.get_item(Key={'schema_name': 'wave'})
        default_date = datetime.datetime(2020, 1, 1)
        last_change_date = datetime.datetime(2020, 1, 1)
        notifications = {
            'lastChangeDate': '',
            'notifications': []
        }
        schema_notifications = {
            'type': 'schema',
            'versions': []}
        date_format = "%Y-%m-%dT%H:%M:%S.%f"
        if 'Item' in resp_server:
            last_change_date = process_item(resp_server, 'server', schema_notifications, default_date, last_change_date, date_format)

        if 'Item' in resp_app:
            last_change_date = process_item(resp_app, 'app', schema_notifications, default_date, last_change_date, date_format)

        if 'Item' in resp_wave:
            last_change_date = process_item(resp_wave, 'wave', schema_notifications, default_date, last_change_date, date_format)

        notifications['notifications'].append(schema_notifications)
        notifications['lastChangeDate'] = last_change_date.isoformat()

        return {'headers': {**default_http_headers},
                'statusCode': 200,
                'body': json.dumps(notifications)
                }
