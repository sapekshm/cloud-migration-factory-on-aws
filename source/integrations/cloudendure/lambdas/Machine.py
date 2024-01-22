#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: Apache-2.0


from __future__ import print_function
import sys
import UpdateBlueprint
import CheckMachine
import LaunchMachine
import requests
import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

application = os.environ['application']
environment = os.environ['environment']

servers_table_name = '{}-{}-servers'.format(application, environment)
apps_table_name = '{}-{}-apps'.format(application, environment)

servers_table = boto3.resource('dynamodb').Table(servers_table_name)
apps_table = boto3.resource('dynamodb').Table(apps_table_name)

REQUESTS_DEFAULT_TIMEOUT = 60


def execute(launchtype, session, headers, endpoint, HOST, projectname, dryrun, waveid, relaunch):

    r = requests.get(HOST + endpoint.format('projects'),
                     headers=headers,
                     cookies=session,
                     timeout=REQUESTS_DEFAULT_TIMEOUT)
    if r.status_code != 200:
        return "ERROR: Failed to fetch the project...."
    try:
        # Get Project ID
        projects = json.loads(r.text)["items"]
        project_exist = False
        for project in projects:
            if project["name"] == projectname:
               project_id = project["id"]
               project_exist = True
        if project_exist == False:
            return "ERROR: Project Name does not exist in CloudEndure...."
        
        # Get Machine List from CloudEndure
        m = requests.get(HOST + endpoint.format('projects/{}/machines').format(project_id),
                         headers=headers,
                         cookies=session,
                         timeout=REQUESTS_DEFAULT_TIMEOUT)
        if "sourceProperties" not in m.text:
            return "ERROR: Failed to fetch the machines...."
        machinelist = {}
        print("**************************")
        print("*CloudEndure Machine List*")
        print("**************************")
        for machine in json.loads(m.text)["items"]:
            print('Machine name:{}, Machine ID:{}'.format(machine['sourceProperties']['name'], machine['id']))
            machinelist[machine['id']] = machine['sourceProperties']['name']
        print("")
       
       # Get all Apps and servers from migration factory

        getserver = scan_dynamodb_server_table()
        servers = sorted(getserver, key = lambda i: i['server_name'])

        getapp = scan_dynamodb_app_table()
        apps = sorted(getapp, key = lambda i: i['app_name'])

        # Get App list
        applist = []
        for app in apps:
            if 'wave_id' in app and 'cloudendure_projectname' in app:
                if str(app['wave_id']) == str(waveid) and str(app['cloudendure_projectname']) == str(projectname):
                    applist.append(app['app_id'])
        # Get Server List
        serverlist = []
        for app in applist:
            for server in servers:
                if "app_id" in server:
                    if app == server['app_id']:
                        serverlist.append(server)
        if len(serverlist) == 0:
            return "ERROR: Serverlist for wave " + waveid + " in Migration Factory is empty...."

        
        # Check Target Machines
        print("****************************")
        print("* Checking Target machines *")
        print("****************************")
        r = CheckMachine.status(session, headers, endpoint, HOST, project_id, launchtype, dryrun, serverlist, relaunch)
        if r is not None and "ERROR" in r:
            return r
        
        # Update Machine Blueprint
        print("**********************")
        print("* Updating Blueprint *")
        print("**********************")
    
        r = UpdateBlueprint.update(launchtype, session, headers, endpoint, HOST, project_id, machinelist, dryrun, serverlist)
        print(r)
        if r is not None and "ERROR" in r:
           return r
        if r is not None and "successful" in r:
           return r
        # Launch Target machines
        if dryrun.lower() != "yes":
           print("*****************************")
           print("* Launching target machines *")
           print("*****************************")
           r = LaunchMachine.launch(launchtype, session, headers, endpoint, HOST, project_id, serverlist)
           return r
    except:
        print(sys.exc_info())

# Pagination for server DDB table scan  
def scan_dynamodb_server_table():
    response = servers_table.scan(ConsistentRead=True)
    scan_data = response['Items']
    while 'LastEvaluatedKey' in response:
        print("Last Evaluate key for server is   " + str(response['LastEvaluatedKey']))
        response = servers_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'],ConsistentRead=True)
        scan_data.extend(response['Items'])
    return(scan_data)

#Pagination for app DDB table scan  
def scan_dynamodb_app_table():
    response = apps_table.scan(ConsistentRead=True)
    scan_data = response['Items']
    while 'LastEvaluatedKey' in response:
        print("Last Evaluate key for app is   " + str(response['LastEvaluatedKey']))
        response = apps_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'],ConsistentRead=True)
        scan_data.extend(response['Items'])
    return(scan_data)