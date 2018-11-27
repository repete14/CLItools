# script created to complete data export for data dump
# Created by Peter Olson
# Version: 1.0.0
# 11/26/18

# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import subprocess


def data_export():
    # get input data to perform operation
    installation_name = input("customer sftp username/installation name (i.e. pwc): ")
    namespace_name = input("Namespace (i.e. jcx-inst-4lwsszavbrnnszco5xtghv): ")
    tenant_id = input("Tenant ID (i.e. 27a58e58-b47b-49ff-bd90-8e8040a24212): ")
    region = input("Context (eu or us): ")
    username = input("Enter your personal username on sftp server (ldap, i.e. polson): ")

    # cascade some data based on input
    if region == "eu":
        context = "jcx-prod-eu"
        bastion_host = "bastion-eu-central-1-jive-microservices-prod.infra.jivehosted.com"
        datacenter = "ams"
        baas_broker = "baas-s3-broker-aws-eu-central-1-prod"
    elif region == "us":
        context = "jcx-prod-us-east"
        bastion_host = "bastion-us-east-1-jive-microservices-prod.infra.jivehosted.com"
        datacenter = "phx"
        baas_broker = "baas-s3-broker-aws-us-east-1-prod"
    else:
        context = input("you must choose either eu or us: ")
        exit()

    binstore_host = "binstore-sftp." + datacenter + "1.jivehosted.com"

    # get the name of a pod
    command = "kubectl get pods --context=" + context + " -n " + namespace_name + " | awk '{print $1}' | grep webapp"
    pod_name = str(subprocess.check_output(command, shell=True).decode('utf-8')).split()[0]
    if pod_name[0] != 'w':
        print(str(subprocess.check_output(command, shell=True).decode('utf-8')))
        print("webapp could not be found: exiting")
        exit()

    # setting up some basic command settings
    command_suffix = "'"
    binstore_prefix = "ssh " + binstore_host + " '"
    binstore_prefix_su = "ssh -t " + binstore_host + " 'sudo "
    bastion_prefix = "ssh " + bastion_host + " '"
    exec_prefix = "kubectl exec -c webapp --context=" + context + " -n " + namespace_name \
                  + " -it " + pod_name + " -- bash -c '"

    # create customer sftp account
    customer_sftp_account = input("Has the customer account already been created? (y/n): ")
    if customer_sftp_account == "y":
        customer_sftp_account = input("Enter account name: ")
    else:
        command = binstore_prefix_su + "/sftp/bin/create_binstore_sftp_user.sh" + command_suffix
        os.system(command)
        customer_sftp_account = installation_name

    # setting up some base file settings
    db_dump_filename = installation_name + "-DB.dmp"
    binstore_dump_filename = installation_name + "-binstore.tar.gz"
    bastion_home_dir = "~/"
    binstore_user_dir = "/sftp/" + username + "/"
    binstore_temp_dir = binstore_user_dir + customer_sftp_account + "/"
    binstore_customer_dir = "/sftp/jail/" + customer_sftp_account + "/storage/"

    print("\n----- getting db details -----")
    print("routing through pod: " + pod_name)
    # get database details
    command = "cd /secrets/jive/db/app/;cat password"
    db_pass = str(subprocess.check_output(exec_prefix + command + command_suffix, shell=True).decode('utf-8')).strip()

    command = "cd /secrets/jive/db/app/;cat dbname"
    db_name = str(subprocess.check_output(exec_prefix + command + command_suffix, shell=True).decode('utf-8')).strip()

    command = "cd /secrets/jive/db/app/;cat host"
    db_host = str(subprocess.check_output(exec_prefix + command + command_suffix, shell=True).decode('utf-8')).strip()

    # SSH to bastion, and create a .dmp file in user's home directory
    print("\n----- creating Db dump on bastion host -----")
    print("use the following to log into the db: " + db_pass)
    command = bastion_prefix + "pg_dump -v -Fc -O -U " + db_name + " -h " + db_host + " -f " + db_dump_filename + " " + db_name + command_suffix
    os.system(command)
    print("creation of " + db_dump_filename + " on " + bastion_host + ":" + bastion_home_dir)

    # move files from bastion to user's sftp home directory
    print("\n----- Moving Db dump to sftp server -----")
    source_file = bastion_host + ":" + bastion_home_dir + db_dump_filename
    destination_file = binstore_user_dir + db_dump_filename
    command = binstore_prefix + "scp " + username + "@" + source_file + " " + destination_file + command_suffix
    os.system(command)

    # move dbDump from sftp home to sftp customer directory
    print("\n----- Moving Db dump to customer sftp directory -----")
    source_file = binstore_user_dir + db_dump_filename
    destination_file = binstore_customer_dir + db_dump_filename
    command = binstore_prefix_su + "mv " + source_file + " " + destination_file + command_suffix
    os.system(command)

    # create binstore dump
    print("\n----- creating binstore dump -----")
    print("Make sure you have your aws CLI tools set up according to https://aurea.jiveon.com/docs/DOC-194116")
    command = binstore_prefix + "mkdir " + binstore_temp_dir + command_suffix
    os.system(command)
    command = binstore_prefix + "aws --profile ms-prod s3 cp s3://" + baas_broker + "/" + tenant_id + "/jiveSBS/ " + binstore_temp_dir + " --recursive" + command_suffix
    os.system(command)
    print("\n----- compressing binstore dump files -----")
    command = binstore_prefix_su + "tar -czvf " + binstore_user_dir + binstore_dump_filename + " " + binstore_temp_dir + "*" + command_suffix
    os.system(command)
    source_file = binstore_user_dir + binstore_dump_filename
    destination_file = binstore_customer_dir + binstore_dump_filename
    print("\n----- Moving binstore dump to customer sftp directory -----")
    command = binstore_prefix_su + "mv " + source_file + " " + destination_file + command_suffix
    os.system(command)

    # setting customer ownership of sftp files
    print("\n----- setting file ownership permissions -----")
    command = binstore_prefix_su + "chown -R " + customer_sftp_account + ":jivesftp " + binstore_customer_dir + command_suffix
    os.system(command)

    # cleaning up leftover files
    print("\n----- cleaning up leftover files and folders -----")
    command = binstore_prefix + "rm -rf " + binstore_temp_dir + command_suffix
    os.system(command)
    command = bastion_prefix + "rm " + bastion_home_dir + db_dump_filename + command_suffix
    os.system(command)

    print("\n----- PROCESS COMPLETE! -----")
    print("Files located at " + binstore_host + binstore_customer_dir + ":")
    command = binstore_prefix_su + "ls -larth " + binstore_customer_dir + command_suffix
    os.system(command)


data_export()
