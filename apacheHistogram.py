#!/usr/bin/env python3

import sys, os, subprocess, time, pprint, statistics
from colorama import Fore, Back, Style

def apache_histogram():
    # read in arguments and assign to local variables
    instance_example = input("Hostname of any webapp (i.e. jivesoftware-noc-m2-t-wa01.m1phx1.jivehosted.com): ")
    node_count = input("Number of webapps: ")
    polling_time_frame = input("Number of hours back you would like to poll for: ")
    is_filtered = input("Would you like to filter your results by keywords (y/n)? ")
    if is_filtered == "y":
        is_filtered = True
        grep_key_words = input("any keywords you would like to filter by (separated by comma): ").split(",")
    else:
        is_filtered = False
        grep_key_words = []

    # testing values
    if instance_example == "":
        instance_example = "humana-aca-jc-t-wa01.dynphx1.jivehosted.com"
        node_count = "2"
        polling_time_frame = "6"
        is_filtered = True

    node_count = int(node_count)
    polling_time_frame = int(polling_time_frame)
    grep_key_words.append("-v jca-enabled")
    grep_key_words.append('-v "internal dummy connection"')

    node_count = int(node_count)
    node_names = []
    apache_traffic_counts = []
    grep_commands = {}

    # determine the text string for each of the nodes and add them to the array,
    # and fill out all arrays/header based on the number of nodes
    print("----- Determining host names ------------")
    header = "\t"
    for i in range(node_count):
        target = instance_example

        # splits the name into the installation, wa??, and hostname
        target_parts = target.split('wa0')

        # replaces wa?? with wa[new number of node in list]
        target = target_parts[0] + "wa" + str(i + 1).zfill(2) + target_parts[1][1:]

        apache_traffic_counts.append({})
        node_names.append(target)
        header += "\twa" + str(i + 1).zfill(2)
    header += "\tTotal"

    # determine text string for each time slice
    print("----- getting time slices from host -----")
    command = 'ssh ' + instance_example + ' "'
    for hour in range(polling_time_frame):
        for minute in range(0,60,10):
            command += 'date +%d/%b/%Y:%H:%M -d ' + "'" + str(hour) + " hours ago " + str(minute) + " minutes ago';"
    command += '"'
    results = str(subprocess.check_output(command, shell=True).decode('utf-8')).split()
    for result in results:
        apache_traffic_counts[result[0:16]] = 0

    # create lists of grep commands by time slice
    basic_grep_command = ""
    for key_word in grep_key_words:
        basic_grep_command += " | grep " + key_word
    basic_grep_command += " | wc -l;"

    days_back = 0
    apache_log_file = "/usr/local/jive/var/logs/jive-httpd-access.log"
    for time in apache_traffic_counts:
        #check for date change
        if time[12:16] == "23:5":
            days_back += 1
            date_command = 'ssh ' + instance_example + ' "date +%Y%m%d -d ' + "'" + str(days_back - 1) + " day ago'" + '"'
            daycode = str(subprocess.check_output(date_command, shell=True).decode('utf-8')).strip()
            if days_back == 1:
                apache_log_file = "/usr/local/jive/var/logs/jive-httpd-access.log-" + daycode
            elif days_back > 1:
                apache_log_file = "/usr/local/jive/var/logs/jive-httpd-access.log-" + daycode + ".gz"
            print("request goes before " + time + " so checking file: " + apache_log_file)
        grep_commands[time] = "less " + apache_log_file + " | grep " + time + basic_grep_command + ";"

    # count each apache log for all calls matching the timeframe
    print("----- counting results from hosts -------")
    for node in node_names:
        apache_log_file = "/usr/local/jive/var/logs/jive-httpd-access.log"
        days_back = 0
        command = 'ssh ' + node + "'"
        for grep_command in grep_commands
            command += grep_command
        command += "'"
        results = str(subprocess.check_output(command, shell=True).decode('utf-8')).split()
        i = 0
        for time in apache_traffic_counts:
            apache_traffic_counts[time] = apache_traffic_counts[time] + int(results[i])
            i += 1

    # calculate result statistics
    print("----- calculating statistics ------------")
    total = 0
    count = 0
    average = statistics.mean(apache_traffic_counts.values())
    median = statistics.median(apache_traffic_counts.values())
    upper = average * 1.5
    lower = average * 0.5

    # output the results
    x = 0
    print("FINAL OUTPUT:")
    for time,count in apache_traffic_counts.items():
        if count >= upper:
            color = Fore.RED
        elif count <= lower:
            color = Fore.GREEN
        else:
            color = Fore.WHITE

        output = time + "0 --> " + color + str(count)
        output += "\t"
        for i in range(int(round(count/(average/5)))):
            output += u"\u2587"
        output += Style.RESET_ALL
        print(output)
    print("Average: " + str(round(average,2)) + "\tLower bound: " + str(round(lower,2)) + "\tUpper bound: " + str(round(upper,2)))


apache_histogram()