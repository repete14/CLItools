# Created by Peter Olson
# script to sshs to a node, poll apache logs and report count of entries with the following grep items, grouped by 10 minute intervals, over the specified previous timeframe
# args: target node, number of hours previous to poll, any number of words to grep



import sys, os, subprocess

# set args for debugging purpose
if len(sys.argv) == 1:
	sys.argv.insert(1, "jivesoftware-noc-m2-t-wa01.m1phx1.jivehosted.com")
	sys.argv.insert(2, 8)
	sys.argv.insert(3, "api")
	sys.argv.insert(4, "GET")


# read in arguments and assign to local variables
grepKeyWords = sys.argv
grepKeyWords.pop(0)
targetServer = grepKeyWords.pop(0)
pollingTimeFrame = int(grepKeyWords.pop(0))


# SSH to node and get the current timestamp of the server
command = 'ssh ' + targetServer + ' date +%d/%b/%Y:%H:%M'
pipe = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE).stdout
output = pipe.read().decode("utf-8")
currentTimeStamp = output[0:len(output)-1]
currentDate = output[0:11]
currentHour = int(currentTimeStamp[12:14])
currentMinute = int(currentTimeStamp[15:17])

command2 = 'ssh ' + targetServer + ' "date +%d/%b/%Y:%H:%M -d ' + "'" + str(pollingTimeFrame) + " hours ago'" + '"'
print("command 2: " + command2)
pipe2 = subprocess.Popen(command2,shell=True,stdout=subprocess.PIPE).stdout
output2 = pipe2.read().decode("utf-8")
startTimeStamp = output2[0:len(output2)-1]
startDate = output[0:11]
startHour = int(startTimeStamp[12:14])
startMinute = int(startTimeStamp[15:17])

print("histogram from " + str(startTimeStamp) + " to " + currentTimeStamp)

# get results from terminal
command = 'ssh ' + targetServer + " 'for i in {" + str(startHour).zfill(2) + ".." + str(currentHour).zfill(2) + '};do for j in {0..5}; do printf "${i}:${j}0 - ";cat /usr/local/jive/var/logs/jive-httpd-access.log | grep -v jca-enabled | grep ' + currentDate + ':${i}:${j}'
for i in range(0,len(grepKeyWords)):
	command += " | grep " + grepKeyWords[i]
command += ' | awk "{print $1}" ' + "| grep . -c;done;done'"
# print(command)

pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout
output = pipe.read().decode("utf-8")
# print(output)

# parse results into array
grepResults = output.split("\n")
for i in range(0,len(grepResults)-1):
	grepResults[i] = int(grepResults[i][8:])

x = 0
for i in range(max(startHour,0), currentHour, 1):
	for j in range(0,6,1):
		print(str(i).zfill(2) + ":" + str(j*10).zfill(2) + " - " + str(grepResults[x]))
		x += 1


