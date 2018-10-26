# script created to complete data export for data dump
# Created by Peter Olson
# Version: 0.1.0
# 10/25/18

# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import subprocess

def dataExport():

    # get input data to perform operation
    installationName = input("Installation/file name (i.e. jive-noc-jcx): ")
    namespaceName = input("Namespace (i.e. jcx-inst-4lwsszavbrnnszco5xtghv): ")
    context = input("Context (eu or us): ")
    # namespaceName = "jcx-inst-4lwsszavbrnnszco5xtghv"
    # context = "us"
    # installationName = "jive-noc-jcx"

    if context == "eu":
        context = "jcx-prod-eu"
        bastionHost = "bastion-eu-central-1-jive-microservices-prod.infra.jivehosted.com"
    elif context == "us":
        context = "jcx-prod-us-east"
        bastionHost = "bastion-us-east-1-jive-microservices-prod.infra.jivehosted.com"
    else:
        context = input("you must choose either eu or us: ")
        exit()

    #get the name of a pod
    execCommand = "kubectl get pods --context=" + context + " -n " + namespaceName + " | awk '{print $1}'"
    podName = str(subprocess.check_output(execCommand,shell=True).decode('utf-8')).split()[1]
    print("getting db details from pod: " + podName)

    # setup the base command used for all future commands
    execPrefix = "kubectl exec -c webapp --context=" + context + " -n " + namespaceName + " -it " + podName + ' -- bash -c "'
    execCommand = ''
    execSuffix = '"'

    #get database details
    execCommand = "cd /secrets/jive/db/app/;cat password"
    dbpass = str(subprocess.check_output(execPrefix + execCommand + execSuffix, shell=True).decode('utf-8')).strip()

    execCommand = "cd /secrets/jive/db/app/;cat dbname"
    dbname = str(subprocess.check_output(execPrefix + execCommand + execSuffix, shell=True).decode('utf-8')).strip()

    execCommand = "cd /secrets/jive/db/app/;cat host"
    dbhost = str(subprocess.check_output(execPrefix + execCommand + execSuffix, shell=True).decode('utf-8')).strip()

    pdDumpCommand = "pg_dump -v -Fc -O -U " + dbname + " -h " + dbhost + " -f " + installationName + ".dmp " + dbname
    print("use the following to log in: " + dbpass)

    # SSH to bastion, and create a .dmp file in your home directory
    execCommand = "ssh " + bastionHost + " '" + pdDumpCommand + "'"
    os.system(execCommand)
    print("creation of " + installationName + ".dmp on " + bastionHost + ":~/")

dataExport()