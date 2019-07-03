# script created to gather logs from Jive JCX instances and download them to your computer, in order to upload them
# elsewhere
# Created by Peter Olson
# Version: 1.4.0
# 11/14/18

# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import os
import datetime
import subprocess


def collect_logs():
    installation_name = input("Installation/file name (i.e. jive-noc-jcx): ")
    namespace_name = input("Namespace (i.e. jcx-inst-4lwsszavbrnnszco5xtghv): ")
    context = input("Region (eu or us): ")
    if context == "eu":
        context = "jcx-prod-eu"
    elif context == "us":
        context = "jcx-prod-us-east"
    else:
        context = "jcx-prod-us-east"
    logs_needed = input("extra logs to collect (a = All, d = Heap dump, t = Thread dump, h = Histogram)(i.e. dt): ")
    download_path = input("Destination path for files (default= ~/Downloads/logs/): ")
    if download_path == '':
        download_path = "~/Downloads/logs/"

    collecting = True

    while collecting:
        pod_name = input("Pod name (i.e. webapp-rc-mbcsm): ")

        # setup the base command used for all future commands
        exec_prefix = "kubectl exec -c webapp --context=" + context + " -n " + namespace_name + " -it " + pod_name + ' -- bash -c "'
        exec_command = ''
        exec_suffix = '"'

        # setup which logs to gather
        heap = False
        thread = False
        histogram = False

        # determine which extra steps to follow in order to grab your logs
        if "a" in logs_needed:
            heap = True
            thread = True
            histogram = True
        if "d" in logs_needed:
            heap = True
        if "t" in logs_needed:
            thread = True
        if "h" in logs_needed:
            histogram = True

        # collect the PID number of the java
        if heap or thread or histogram:
            print("\n------------------------------   determine java PID   ---------------------------- ")
            exec_command = "ps -ef | grep jive | awk '{print $1}'"
            pid = str(subprocess.check_output(exec_prefix + exec_command + exec_suffix, shell=True)).strip().split(" ")
            pid = pid[2]

        # create heapdump file on host at /var/log/jive
        if heap:
            print("\n------------------------------   creating Heap Dump   ---------------------------- ")
            exec_command = "cd /var/log/jive/;jmap -dump:live,format=b,file=heapdump.bin " + pid
            os.system(exec_prefix + exec_command + exec_suffix)

        # create thread dump file on host at /var/log/jive
        if thread:
            print("\n------------------------------   Creating Thread Dump ---------------------------- ")
            exec_command = "jstack -l " + pid + " > /var/log/jive/threaddumps.txt"
            os.system(exec_prefix + exec_command + exec_suffix)

        # create histogram file on host at /var/log/jive
        if histogram:
            print("\n------------------------------   Collecting Histogram ---------------------------- ")
            exec_command = "jmap -histo " + pid + " > /var/log/jive/histo.txt"
            os.system(exec_prefix + exec_command + exec_suffix)

        # compress all the logs in the /var/log/jive folder into a file called [installation]_logs_[date].tar.gz
        print("\n------------------------------   Compressing logs     ---------------------------- ")
        now = datetime.datetime.now()
        archive_name = installation_name + "_logs_" + pod_name + "_" + str(now.month) + "-" + str(now.day) + "-" + str(
            now.year) + ".tar.gz"
        exec_command = "tar -czf " + archive_name + " -C /var/log jive"
        os.system(exec_prefix + exec_command + exec_suffix)

        # download log gz file to local machine where specified earlier
        print("\n------------------------------   Downloading logs ------------------------------ ")
        os.system("kubectl cp -c webapp --context=" + context + " -n " + namespace_name + " " + pod_name + ":/usr/local/jive/" + archive_name + " " + download_path + archive_name)

        # delete logs and gz gathered to return to original state.
        print("\n------------------------------   Deleting logs ------------------------------ ")
        if heap:
            exec_command = "rm /var/log/jive/heapdump.bin"
            os.system(exec_prefix + exec_command + exec_suffix)
        if histogram:
            exec_command = "rm /var/log/jive/histo.txt"
            os.system(exec_prefix + exec_command + exec_suffix)
        if thread:
            exec_command = "rm /var/log/jive/threaddumps.txt"
            os.system(exec_prefix + exec_command + exec_suffix)
        exec_command = "rm /usr/local/jive/" + archive_name
        os.system(exec_prefix + exec_command + exec_suffix)

        # allow for user to do process again, but with a different pod. all other information stays the same
        if input("Collect logs from a second webapp of this installation (y/n): ") == "n":
            collecting = False


collect_logs()
