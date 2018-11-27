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
3) Details for the login credentials, and command to be used will be printed out. 
    1) Enter the password when prompted
    2) Then when at the psql prompt, enter the command given
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
3) Details for the PSQL db login credentials will be printed out. 
    1) Enter the password when prompted
4) You will be asked if the customer's SFTP account has already been created
    1) If so type 'y', and When prompted enter the name for the already generated customer account 
    2) If not, type 'n', and enter the name of the account to be created (usually the customer or instance name)
5) Follow along with the output as the files are generated, packaged, and moved to the customer's sftp folders
5) Done!

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
3) Details for the login credentials, and command to be used will be printed out. 
    1) Enter the password when prompted
    2) Perform whatever tasks you intend, while in the psql prompt
    3) Enter "\q" to quit psql prompt, and continue
    
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
