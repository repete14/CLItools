#!/usr/bin/env python3

import sys, os, subprocess, time
from colorama import Fore, Back, Style


def check_threads():

    instance_example = input("Hostname of any webapp (i.e. jivesoftware-noc-m2-t-wa01.m1phx1.jivehosted.com): ")
    node_count = input("Number of webapps: ")
    node_count = int(node_count)
    nodes = []
    threads = []
    color = []
    timestamp = ""
    output = "\t"

    # determine the text string for each of the nodes and add them to the array
    for i in range(node_count):
        target = instance_example

        # splits the name into the installation, wa??, and hostname
        target_parts = target.split('wa0')

        # replaces wa?? with wa[new number of node in list]
        target = target_parts[0] + "wa" + str(i + 1).zfill(2) + target_parts[1][1:]

        nodes.append(target)
        threads.append(0)
        color.append(Style.RESET_ALL)
        output += "\twa" + str(i + 1).zfill(2)
    print(output)

    # continuously iterate over the list of nodes and send bash command to ssh and print number of threads
    while True:
        # collect the thread values
        for i in range(node_count):
            command = '''ssh noc-mgmt1.phx1.jivehosted.com "cd /jmx_watch/ '''
            command += '; sudo bash /jmx_watch/jmx.sh ' + nodes[i] + ' 6651'
            command += '"'
            threads[i] = str(subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8')).split()[5]

            try:
                number = int(threads[i])
                if number >= 40:
                    color[i] = Fore.RED + Back.RED + Style.BRIGHT
                elif number >= 30:
                    color[i] = Fore.RED
                elif number >= 15:
                    color[i] = Fore.YELLOW
                elif number >= 0:
                    color[i] = Fore.GREEN
                else:
                    color[i] = Back.BLUE + Style.BRIGHT
                    threads[i] = "restrt"
            except ValueError:
                color[i] = Back.BLUE + Style.BRIGHT
                threads[i] = "?"
        timestamp = str(subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8')).split()[1]

        # create the output string
        output = timestamp
        for i in range(node_count):
            # print("--------------------------")
            # print("--------------------------")
            # print('*')
            output += "\t" + color[i] + threads[i] + Style.RESET_ALL
        print (output)


check_threads()