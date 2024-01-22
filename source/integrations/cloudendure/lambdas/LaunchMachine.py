#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: Apache-2.0


from __future__ import print_function
import sys
import requests
import datetime
import json
import os
import boto3
import uuid
from boto3.dynamodb.conditions import Key, Attr

application = os.environ['application']
environment = os.environ['environment']
AnonymousUsageData = os.environ['AnonymousUsageData']
s_uuid = os.environ['solutionUUID']
region = os.environ['region']

servers_table_name = '{}-{}-servers'.format(application, environment)
servers_table = boto3.resource('dynamodb').Table(servers_table_name)

REQUESTS_DEFAULT_TIMEOUT = 60


def launch(launchtype, session, headers, endpoint, HOST, project_id, serverlist):
    url = 'https://metrics.awssolutionsbuilder.com/generic'
    m = requests.get(HOST + endpoint.format('projects/{}/machines').format(project_id),
                     headers=headers,
                     cookies=session,
                     timeout=REQUESTS_DEFAULT_TIMEOUT)
    machine_ids = []
    machine_names = []
    for server in serverlist:
        for machine in json.loads(m.text)["items"]:
            if server["server_name"].lower() == machine['sourceProperties']['name'].lower():
                machine_ids.append({"machineId": machine['id']})
                machine_names.append(machine['sourceProperties']['name'])
    if launchtype == "test":
        machine_data = {'items': machine_ids, "launchType": "TEST"}
    elif launchtype == "cutover":
        machine_data = {'items': machine_ids, "launchType": "CUTOVER"}
    else:
        print("ERROR: Invalid Launch Type....")
    print("Machine List: ")
    print(machine_data)
    print("*******************")
    message = ""
    for name in machine_names:
        message = message + name + ","
    message = message[:-1]
    result = requests.post(HOST + endpoint.format('projects/{}/launchMachines').format(project_id),
                           data=json.dumps(machine_data),
                           headers=headers,
                           cookies=session,
                           timeout=REQUESTS_DEFAULT_TIMEOUT)
    # Response code translate to message
    if result.status_code == 202:
        if launchtype == "test":
            # Updating server migration_status, change to tested
            serverids = []
            getserver = scan_dynamodb_server_table()
            servers = sorted(getserver, key=lambda i: i['server_name'])
            for s in servers:
                for name in machine_names:
                    if name.lower() == s["server_name"].lower():
                        serverids.append(s["server_id"])
            for sid in serverids:
                existing_attr = servers_table.get_item(Key={'server_id': sid})
                existing_attr['Item']['migration_status'] = "Test instance launched"
                resp = servers_table.put_item(Item=existing_attr['Item'])
                if AnonymousUsageData == "Yes":
                    usage_data = {"Solution": "SO0097",
                                  "UUID": s_uuid,
                                  "Status": "Migrated",
                                  "TimeStamp": str(datetime.datetime.now()),
                                  "Region": region
                                  }
                    send_anonymous_data = requests.post(url,
                                                        data=json.dumps(usage_data),
                                                        headers={'content-type': 'application/json'},
                                                        timeout=REQUESTS_DEFAULT_TIMEOUT)
                    url_ce = "https://s20a21yvzd.execute-api.us-east-1.amazonaws.com/prod/launch"
                    ce_data = {"UUID": s_uuid}
                    server_migrated = requests.post(url_ce,
                                                    data=json.dumps(ce_data),
                                                    timeout=REQUESTS_DEFAULT_TIMEOUT)
                print(resp)
            return "Test Job created for machine " + message + "...."
        if launchtype == "cutover":
            # Updating server migration_status, change to migrated
            serverids = []
            getserver = scan_dynamodb_server_table()
            servers = sorted(getserver, key=lambda i: i['server_name'])
            for s in servers:
                for name in machine_names:
                    if name.lower() == s["server_name"].lower():
                        serverids.append(s["server_id"])
            for sid in serverids:
                existing_attr = servers_table.get_item(Key={'server_id': sid})
                existing_attr['Item']['migration_status'] = "Cutover instance launched"
                resp = servers_table.put_item(Item=existing_attr['Item'])
                if AnonymousUsageData == "Yes":
                    usage_data = {"Solution": "SO0097",
                                  "UUID": s_uuid,
                                  "Status": "Migrated",
                                  "TimeStamp": str(datetime.datetime.now()),
                                  "Region": region
                                  }
                    send_anonymous_data = requests.post(url,
                                                        data=json.dumps(usage_data),
                                                        headers={'content-type': 'application/json'},
                                                        timeout=REQUESTS_DEFAULT_TIMEOUT)
                    url_ce = "https://s20a21yvzd.execute-api.us-east-1.amazonaws.com/prod/launch"
                    ce_data = {"UUID": s_uuid}
                    server_migrated = requests.post(url_ce,
                                                    data=json.dumps(ce_data),
                                                    timeout=REQUESTS_DEFAULT_TIMEOUT)
                print(resp)
            return "Cutover Job created for machine " + message + "...."
    elif result.status_code == 409:
        return "ERROR: Source machines have job in progress...."
    elif result.status_code == 402:
        return "ERROR: Project license has expired...."
    else:
        return "ERROR: Launch target machine failed...."


# Pagination for server DDB table scan
def scan_dynamodb_server_table():
    response = servers_table.scan(ConsistentRead=True)
    scan_data = response['Items']
    while 'LastEvaluatedKey' in response:
        print("Last Evaluate key for server is   " + str(response['LastEvaluatedKey']))
        response = servers_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'], ConsistentRead=True)
        scan_data.extend(response['Items'])
    return (scan_data)
