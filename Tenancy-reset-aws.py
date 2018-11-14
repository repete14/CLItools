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
    namespace_name = input("Namespace (i.e. jcx-inst-rd19ys5fnopufncxqvxwqg): ")
    tenant_id = input("Tenant ID (i.e. 062a3052-5398-4b86-a302-3fd28e68be30): ")
    region = input("Context (eu or us): ")

    if namespace_name == "test":
        namespace_name = "jcx-inst-rd19ys5fnopufncxqvxwqg"
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
    print("----------use the following to log in: ")
    print(db_pass)
    print("\n----------use the following command to finish reset: ")
    print("DELETE FROM jiveProperty where name like 'services.secret.%';")
    print("\n----------exit psql with '\q' when complete, and move on to the next steps")
    print("")
    exec_command = ("psql --host " + db_host + " --port=" + db_port + " --username=" + db_username + " --dbname=" + db_name)
    os.system(exec_prefix + exec_command + exec_suffix)

    tenancy_secrets_purge(datacenter, tenant_id)


def tenancy_secrets_purge(datacenter, tenant_id):

    services = str("activityIngress mitui-video-playback antivirus mitui-videos baas-s3-broker mitui-videos-aws "
                   "cloudnotification office365 content-translation phrase-substitution contentTranslation "
                   "realtime-discovery core-phrasesubstitution rebuildSearchIndex core-translation recoactivity "
                   "csm-aws recoactivity-aws dealroom recofollows digestrecommender recofollows-aws "
                   "digestrecommender-aws recommendations directory recommendations-aws gala-app-service reconotify "
                   "identity reconotify-aws if-crm-sfdc recorealtime jive-auth-cloud-analytics-aws recorealtime-aws "
                   "jive-cloud-analytics rewards jive-cloud-analytics-aws rewards-recognition "
                   "jive-cmr-cloud-analytics search jive-id-auth search.moreLikeThis jive-id-batphone search.query "
                   "jive-id-profile searchIndexManage jive-id-public spam-prevention jive-id-ui spamprevention "
                   "jive-im-cloud-analytics streamonce jive-im-cloud-analytics-aws unified-admin-aws jivewadmin "
                   "vid-authorization-perceptive mitui-cloudalytics vid-delete-perceptive mitui-cloudalytics-aws "
                   "vid-download-perceptive mitui-cloudalytics-export vid-embed mitui-cloudalytics-insights "
                   "vid-registration-perceptive mitui-cloudalytics-insights-aws vid-status-perceptive mitui-comments "
                   "vid-upload-perceptive mitui-people video-authorization-perceptive mitui-people-aws "
                   "video-authorize-perceptive mitui-phrases video-delete-perceptive mitui-phrases-aws "
                   "video-download-perceptive mitui-places video-embed mitui-places-aws video-regauth-perceptive "
                   "mitui-profile video-register-perceptive mitui-profile-aws video-registration-perceptive "
                   "mitui-userpanel video-status-perceptive mitui-userpanel-aws video-upload-perceptive "
                   "mitui-video-browse zenx mitui-video-create").split(" ")
    for service in services:
        for i in ("1","2","3"):

            headers = {
                'Content-Type': 'application/json',
            }

            data = '{"customerSecretRequest":{"serviceName":"' + service + '", "systemId":"' + tenant_id + '"},"instanceType":""}'

            response = str(requests.post('http://tenancy-prod-app' + i + '.s1' + datacenter + '1.jivehosted.com:20000/purge/secret/services/tenantSecret/purge', headers=headers, data=data))
            print("purge of tenancy-prod-app" + i + '.s1' + datacenter + " of tenantID " + tenant_id + " for service " + service + ": " + response)


tenancy_reset()
