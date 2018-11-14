# CLItools
collection of Jive tools

##TENANCY RESET SCRIPT: 
######tenancy-rest-aws.py

Prerequisites:
1) Python 3
2) Requests package
   -install with: "python3 -m pip install requests"
3) Awk and grep commands
4) Tested with mac using zsh command line. Could need updating to use on other systems.

To use:
1) Run with "python3 [path to file]\tenancy-reset-aws.py
2) When prompted, enter:
    a) JCX URI/namespace
    b) tenantID/Jive instance ID
    c) the region (either 'us' or 'eu')
3) Details for the login credentials, and command to be used will be printed out. 
    a) enter the password when prompted
    b) then when at the psql prompt, enter the command given
    c) enter "\q" to quit psql prompt, and continue
4) Script will proceed to purging of tenancy data from host, monitor for success.
5) Done!
