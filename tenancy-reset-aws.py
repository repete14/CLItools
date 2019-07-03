# script created to complete data export for data dump
# Created by Peter Olson
# Version: 0.2.0
# 10/25/18

# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import os
import subprocess
import requests


def tenancy_reset():
    # get input data to perform operation
    namespace_name = input("Namespace (i.e. jcx-inst-4lwsszavbrnnszco5xtghv): ")
    tenant_id = input("Tenant ID (i.e. 27a58e58-b47b-49ff-bd90-8e8040a24212): ")
    region = input("Context (eu or us): ")

    if namespace_name == "test":
        namespace_name = "jcx-inst-4lwsszavbrnnszco5xtghv"
        tenant_id = "27a58e58-b47b-49ff-bd90-8e8040a24212"
        region = "us"

    # performing tenancy purge
    #print("Performing tenancy purge")

    if region == "eu":
        context = "jcx-prod-eu"
        datacenter = "ams"
    elif region == "us":
        context = "jcx-prod-us-east"
        datacenter = "phx"
    else:
        print("you must choose either eu or us")
        exit()

    # get the name of a pod
    exec_command = "kubectl get pods --context=" + context + " -n " + namespace_name + " | awk '{print $1}' | grep webapp"
    pod_name = str(subprocess.check_output(exec_command, shell=True).decode('utf-8')).split()[0]
    if pod_name[0] != 'w':
        print(str(subprocess.check_output(exec_command, shell=True).decode('utf-8')))
        print("webapp could not be found: exiting")
        exit()
    print("getting db details from pod: " + pod_name)

    # setup the base command used for all future commands
    exec_prefix = "kubectl exec -c webapp --context=" + context + " -n " + namespace_name \
                  + " -it " + pod_name + ' -- bash -c "'
    exec_command = ''
    exec_suffix = '"'

    # get database details
    exec_command = "cd /secrets/jive/db/app/;cat password"
    db_pass = str(subprocess.check_output(exec_prefix + exec_command + exec_suffix, shell=True).decode('utf-8')).strip()

    exec_command = "cd /secrets/jive/db/app/;cat dbname"
    db_name = str(subprocess.check_output(exec_prefix + exec_command + exec_suffix, shell=True).decode('utf-8')).strip()

    exec_command = "cd /secrets/jive/db/app/;cat username"
    db_username = str(subprocess.check_output(exec_prefix + exec_command + exec_suffix, shell=True).decode('utf-8')).strip()

    exec_command = "cd /secrets/jive/db/app/;cat port"
    db_port = str(subprocess.check_output(exec_prefix + exec_command + exec_suffix, shell=True).decode('utf-8')).strip()

    exec_command = "cd /secrets/jive/db/app/;cat host"
    db_host = str(subprocess.check_output(exec_prefix + exec_command + exec_suffix, shell=True).decode('utf-8')).strip()

    # log into sql, in order to run delete command
    print("")
    print("\n----------use the following command to finish reset: ")
    print("DELETE FROM jiveProperty where name like 'services.secret.%';")
    print("\n----------exit psql with '\q' when complete, and move on to the next steps")
    print("")
    exec_command = ("export PGPASSWORD=" + db_pass + "; psql --host " + db_host + " --port=" + db_port + " --username=" + db_username + " --dbname=" + db_name)
    os.system(exec_prefix + exec_command + exec_suffix)

    tenancy_secrets_purge(datacenter, tenant_id)


def tenancy_secrets_purge(datacenter, tenant_id):

    services = [
        'activityIngress',
        'antivirus',
        'api-gateway',
        'baas-s3-broker',
        'cloudnotification',
        'content-translation',
        'contentTranslation',
        'core-phrasesubstitution',
        'core-translation',
        'csm-aws',
        'dealroom',
        'digestrecommender',
        'digestrecommender-aws',
        'directory',
        'gala-app-service',
        'identity',
        'if-crm-sfdc',
        'jive-auth-cloud-analytics-aws',
        'jive-cloud-analytics',
        'jive-cloud-analytics-aws',
        'jive-cmr-cloud-analytics',
        'jive-id-auth',
        'jive-id-batphone',
        'jive-id-profile',
        'jive-id-public',
        'jive-id-ui',
        'jive-im-cloud-analytics',
        'jive-im-cloud-analytics-aws',
        'jivewadmin',
        'mitui-cloudalytics',
        'mitui-cloudalytics-aws',
        'mitui-cloudalytics-export',
        'mitui-cloudalytics-insights',
        'mitui-cloudalytics-insights-aws',
        'mitui-comments',
        'mitui-people',
        'mitui-people-aws',
        'mitui-phrases',
        'mitui-phrases-aws',
        'mitui-places',
        'mitui-places-aws',
        'mitui-profile',
        'mitui-profile-aws',
        'mitui-userpanel',
        'mitui-userpanel-aws',
        'mitui-video-browse',
        'mitui-video-create',
        'mitui-video-playback',
        'mitui-videos',
        'mitui-videos-aws',
        'mobile-push-notification',
        'office365',
        'phrase-substitution',
        'realtime-discovery',
        'rebuildSearchIndex',
        'recoactivity',
        'recoactivity-aws',
        'recofollows',
        'recofollows-aws',
        'recommendations',
        'recommendations-aws',
        'reconotify',
        'reconotify-aws',
        'recorealtime',
        'recorealtime-aws',
        'rewards',
        'rewards-recognition',
        'search',
        'search.moreLikeThis',
        'search.query',
        'searchIndexManage',
        'security-notification',
        'spam-prevention',
        'spamprevention',
        'streamonce',
        'unified-admin-aws',
        'urgent-notifications',
        'vid-authorization-perceptive',
        'vid-delete-perceptive',
        'vid-download-perceptive',
        'vid-embed',
        'vid-registration-perceptive',
        'vid-status-perceptive',
        'vid-upload-perceptive',
        'video-authorization-perceptive',
        'video-authorize-perceptive',
        'video-delete-perceptive',
        'video-download-perceptive',
        'video-embed',
        'video-regauth-perceptive',
        'video-register-perceptive',
        'video-registration-perceptive',
        'video-status-perceptive',
        'video-upload-perceptive',
        'zenx',
    ]

    for service in services:
        for i in ("1","2","3"):

            headers = {
                'Content-Type': 'application/json',
            }

            data = '{"customerSecretRequest":{"serviceName":"' + service + '", "systemId":"' + tenant_id + '"},"instanceType":""}'

            response = str(requests.post('http://tenancy-prod-app' + i + '.s1' + datacenter + '1.jivehosted.com:20000/purge/secret/services/tenantSecret/purge', headers=headers, data=data))
            print("purge of tenancy-prod-app" + i + '.s1' + datacenter + " of tenantID " + tenant_id + " for service " + service + ": " + response)


tenancy_reset()
