# Script created to login to an aws site's db to perform queries
# Created by Peter Olson
# Version: 0.2.0
# 11/14/18

# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import subprocess


def awsDbLogin():
    # get input data to perform operation
    namespace_name = input("Namespace (i.e. jcx-inst-4lwsszavbrnnszco5xtghv): ")
    context = input("Context (eu or us): ")

    if namespace_name == "test":
        namespace_name = "jcx-inst-4lwsszavbrnnszco5xtghv"
        context = "us"

    # performing tenancy purge

    if context == "eu":
        context = "jcx-prod-eu"
    elif context == "us":
        context = "jcx-prod-us-east"
    else:
        context = input("you must choose either eu or us: ")
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
    exec_command = ("export PGPASSWORD=" + db_pass + "; psql --host " + db_host + " --port=" + db_port + " --username=" + db_username + " --dbname=" + db_name)
    os.system(exec_prefix + exec_command + exec_suffix)


awsDbLogin()