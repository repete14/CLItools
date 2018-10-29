# script created to complete data export for data dump
# Created by Peter Olson
# Version: 0.1.0
# 10/25/18

# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import subprocess


def data_export():
    # get input data to perform operation
    installation_name = input("Installation/file name (i.e. jive-noc-jcx): ")
    namespace_name = input("Namespace (i.e. jcx-inst-4lwsszavbrnnszco5xtghv): ")
    context = input("Context (eu or us): ")

    if installation_name == "test":
        namespace_name = "jcx-inst-4lwsszavbrnnszco5xtghv"
        context = "us"
        installation_name = "jive-noc-jcx"

    if context == "eu":
        context = "jcx-prod-eu"
        bastion_host = "bastion-eu-central-1-jive-microservices-prod.infra.jivehosted.com"
    elif context == "us":
        context = "jcx-prod-us-east"
        bastion_host = "bastion-us-east-1-jive-microservices-prod.infra.jivehosted.com"
    else:
        context = input("you must choose either eu or us: ")
        exit()

    # get the name of a pod
    exec_command = "kubectl get pods --context=" + context + " -n " + namespace_name + " | awk '{print $1}'"
    pod_name = str(subprocess.check_output(exec_command, shell=True).decode('utf-8')).split()[1]
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

    exec_command = "cd /secrets/jive/db/app/;cat host"
    db_host = str(subprocess.check_output(exec_prefix + exec_command + exec_suffix, shell=True).decode('utf-8')).strip()

    dump_command = "pg_dump -v -Fc -O -U " + db_name + " -h " + db_host + " -f " + installation_name + ".dmp " + db_name
    print("use the following to log in: " + db_pass)

    # SSH to bastion, and create a .dmp file in your home directory
    exec_command = "ssh " + bastion_host + " '" + dump_command + "'"
    os.system(exec_command)
    print("creation of " + installation_name + ".dmp on " + bastion_host + ":~/")


data_export()
