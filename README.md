# CLItools
A Collection of Jive tools created for personal use in the NOC and HOPS teams, open for use by others

## TENANCY RESET SCRIPT: 
###### tenancy-rest-aws.py
Tool for performing a full tenancy reset on an AWS site; including clearing secrets from the database, as well as the tenancy host, for all services

##### Prerequisites:
1) Python 3
2) Requests package
   -install with: "python3 -m pip install requests"
3) Awk and grep commands
4) properly configured kubectl setup with access to run commands on pods
5) Tested with mac using zsh command line. Could need updating to use on other systems.
6) based on information and methodology in https://aurea.jiveon.com/docs/doc-13084

##### To use:
1) Run with "python3 [path to file]\tenancy-reset-aws.py
2) When prompted, enter:
    1) JCX URI/namespace
    2) TenantID/Jive instance ID
    3) The region (either 'us' or 'eu')
3) Details for the command to be used will be printed out. 
    2) At the psql prompt, enter the command given
    3) Enter "\q" to quit psql prompt, and continue
4) Script will proceed to purging of tenancy data from host, monitor for success.
5) Done!

## AWS DATA DUMP SCRIPT: 
###### dataExportAws.py
Tool for dumping customer database and binstore data onto sftp server from an AWS site.

##### Prerequisites:
1) Python 3
2) Awk and grep commands
3) Tested with mac using zsh command line. Could need updating to use on other systems.
4) properly configured kubectl setup with access to run commands on pods
5) governor credentials to run aws cli tools (see below doc below for setup instructions)
6) personal folder in the binstore sftp directory named after your ldap login
7) based on information and methodology in https://aurea.jiveon.com/docs/DOC-194116

##### To use:
1) Run with "python3 [path to file]\dataExportAws.py
2) When prompted, enter:
    1) Name of Instance/customer (used for filenames)
    2) JCX URI/namespace
    3) TenantID/Jive instance ID
    4) The region (either 'us' or 'eu')
    5) Your personal username on sftp server (usually ldap)
3) You will be asked if the customer's SFTP account has already been created
    1) If so type 'y', and When prompted enter the name for the already generated customer account 
    2) If not, type 'n', and enter the name of the account to be created (usually the customer or instance name)
4) Follow along with the output as the files are generated, packaged, and moved to the customer's sftp folders
5) Done!

## AWS Pod Monitor: 
###### pod_monitor.py
Tool for monitoring the current status of pods as they start up

##### Prerequisites:
1) Python, with the following packages:
    1) kubernetes
    2) pytz
4) properly configured kubectl setup with access to run commands on pods
5) Tested with mac using python 2. Could need updating to use on other systems.

##### To use:
1) Run with "python [path to file]\pod_monitor.py
2) Script will run and show all webapp pods in which the status of the webapp container is in a not ready state (analogous to ready state 1/2)
    1) the top section will show pods that are older than 10 minutes, but younger than 12 hours, i.e. those most likely to need to be stuck and need to be killed
    2) the second section will show all pods that are younger than 10 minutes, i.e. still in the process of starting up
    3) the bottom section will show all pods that are older than 12 hours, most likely part of a dead installation or otherwise can be ignored.
4) The first column shows the namespace of the pods, the second column shows the pod name, and the third is the age of the pod
5) Page will repeat until closed, refreshing every 8 seconds or so, depending on speed of operation.

## AWS Pod Killer: 
###### pod_killer.py
Tool to aid killing of stuck pods

##### Prerequisites:
1) Python 2, with the following packages:
    1) kubernetes
    2) pytz
4) properly configured kubectl setup with access to run commands on pods
5) Tested with mac using python 2. Could need updating to use on other systems.

##### To use:
1) Run with "python [path to file]\pod_killer.py
2) Script will run and show all non functioning webapp pods in a manner identical to the above (pod_watch.py) 
4) The script will then ask for your next action, which can be one of the following:
    1) 'r' will recheck all pods, and update the display/numbering
    2) 'a' will delete all pods listed in the above display
    3) entering any number, or series of numbers (comma separated), will delete those numbered webapps
    4) 'q' will quit the script 
5) Page will report pods deleted, as well as a count of how many pods have been deleted for all namespaces by you so far.

## AWS Database Login: 
###### dbLoginAws.py
script used to simplify the process of logging into an aws site's db, by just entering the namespace and region

##### Prerequisites:
1) Python 3
2) Requests package
   -install with: "python3 -m pip install requests"
3) Awk and grep commands
4) properly configured kubectl setup with access to run commands on pods
5) Tested with mac using zsh command line. Could need updating to use on other systems.

##### To use:
1) Run with "python3 [path to file]\dbLoginAws.py"
2) When prompted, enter the following:
    1) JCX URI/namespace 
    2) The region (either 'us' or 'eu')
3) Perform whatever tasks you intend, while in the psql prompt
4) Enter "\q" to quit psql prompt, and continue
    
## AWS log gathering script: 
###### logGathererAWS.py
Script used to simplify the process of logging into an aws site's db, by just entering the namespace and region

##### Prerequisites:
1) Python 3
2) Awk and grep commands
3) properly configured kubectl setup with access to run commands on pods
4) Tested with mac using zsh command line. Could need updating to use on other systems.
5) based on information and methodology in https://aurea.jiveon.com/docs/DOC-16498

##### To use:
1) Run with "python3 [path to file]\logGathererAWS.py"
2) When prompted, enter the following:
    1) The name of the installation (used for naming of file)
    2) JCX URI/namespace 
    3) The region (either 'us' or 'eu')
    4) Type in codes for any additional logs to be created
        1) d = Heap dump
        2) t for a thread dump
        3) h for a Histogram
        4) a for all of the above
        5) Or some combination thereof (th to get both heap and thread dump, along with normal logs)
    5) The destination for the logs on your local machine (default to ~/Downloads/logs/, for mac). This folder must exist prior to running the script
3) When complete, if you'd like to gather for other webap pods, type in 'y', then when prompted enter the next webapp name. Type in 'n' to exit script
