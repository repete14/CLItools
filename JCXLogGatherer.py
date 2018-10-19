# script created to gather logs from Jive JCX instances and download them to your computer, in order to upload them elsewhere
# Created by Peter Olson
# Version: 1.4.0
# 10/18/18

# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import datetime
import subprocess


def collectLogs():

    installationName = input("Installation/file name (i.e. jive-noc-jcx): ")
    namespaceName = input("Namespace (i.e. jcx-inst-4lwsszavbrnnszco5xtghv): ")
    context = input("Context (eu or us): ")
    if context == "eu":
        context = "jcx-prod-eu"
    elif context == "us":
        context = "jcx-prod-us-east"
    else:
        context = "jcx-prod-us-east"
    logsNeeded = input("extra logs to collect (a = All, d = Heap dump, t = Thread dump, h = Histogram)(i.e. dt): ")
    downloadPath = input("Destination path for files (default= ~/Downloads/logs/): ")
    if downloadPath == '':
        downloadPath = "~/Downloads/logs/"

    collecting = True



    while collecting:
        podName = input("Pod name (i.e. webapp-rc-mbcsm): ")

        # setup the base command used for all future commands
        execPrefix = "kubectl exec -c webapp --context=" + context + " -n " + namespaceName + " -it " + podName + ' -- bash -c "'
        execCommand = ''
        execSuffix = '"'

        # setup which logs to gather
        heap = False
        thread = False
        histogram = False

        # determine which extra steps to follow in order to grab your logs
        if "a" in logsNeeded:
            heap = True
            thread = True
            histogram = True
        if "d" in logsNeeded:
            heap = True
        if "t" in logsNeeded:
            thread = True
        if "h" in logsNeeded:
            histogram = True

        # collect the PID number of the java
        if heap or thread or histogram:
            print("\n------------------------------   determine java PID   ---------------------------- ")
            execCommand = "ps -ef | grep jive | awk '{print $1}'"
            pid = str(subprocess.check_output(execPrefix + execCommand + execSuffix, shell=True)).strip().split(" ")
            pid = pid[2]

        # create heapdump file on host at /var/log/jive
        if heap:
            print("\n------------------------------   creating Heap Dump   ---------------------------- ")
            execCommand = "cd /var/log/jive/;jmap -dump:live,format=b,file=heapdump.bin " + pid
            os.system(execPrefix + execCommand + execSuffix)

        # create thread dump file on host at /var/log/jive
        if thread:
            print("\n------------------------------   Creating Thread Dump ---------------------------- ")
            execCommand = "jstack -l " + pid + " > /var/log/jive/threaddumps.txt"
            os.system(execPrefix + execCommand + execSuffix)

        # create histogram file on host at /var/log/jive
        if histogram:
            print("\n------------------------------   Collecting Histogram ---------------------------- ")
            execCommand = "jmap -histo " + pid + " > /var/log/jive/histo.txt"
            os.system(execPrefix + execCommand + execSuffix)

        # compress all the logs in the /var/log/jive folder into a file called [installation]_logs_[date].tar.gz
        print("\n------------------------------   Compressing logs     ---------------------------- ")
        now = datetime.datetime.now()
        archiveName = installationName + "_logs_" + podName + "_" + str(now.month) + "-" + str(now.day) + "-" + str(
            now.year) + ".tar.gz"
        execCommand = "tar -czf /var/log/jive/" + archiveName + " /var/log/jive/"
        os.system(execPrefix + execCommand + execSuffix)

        # download log gz file to local machine where specified earlier
        print("\n------------------------------   Downloading logs ------------------------------ ")
        os.system("kubectl cp -c webapp --context=" + context + " -n " + namespaceName + " " + podName + ":/var/log/jive/" + archiveName + " " + downloadPath + archiveName)

        # delete logs and gz gathered to return to original state.
        print("\n------------------------------   Deleting logs ------------------------------ ")
        if heap:
            execCommand = "rm /var/log/jive/heapdump.bin"
            os.system(execPrefix + execCommand + execSuffix)
        if histogram:
            execCommand = "rm /var/log/jive/histo.txt"
            os.system(execPrefix + execCommand + execSuffix)
        if thread:
            execCommand = "rm /var/log/jive/threaddumps.txt"
            os.system(execPrefix + execCommand + execSuffix)
        execCommand = "rm /var/log/jive/" + archiveName
        os.system(execPrefix + execCommand + execSuffix)

        # allow for user to do process again, but with a different pod. all other information stays the same
        if input("Collect logs from a second webapp of this installation (y/n): ") == "n":
            collecting = False

collectLogs()
