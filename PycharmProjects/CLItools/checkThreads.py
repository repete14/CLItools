#created by Peter Olson
#tool to quickly monitor threads on an entire installation
#used by calling file and passing it the name of one of it's nodes, and the number of nodes that that installation has.

import sys, os, subprocess, time

RED='\033[0;31m'
GREEN ='\033[0;32m'
NC='\033[0m'

if len(sys.argv) == 1:
	sys.argv.insert(1, "jivesoftware-noc-m2-t-wa01.m1phx1.jivehosted.com")
	sys.argv.insert(2, 2)

instanceExample = sys.argv[1]           #a node used to determine the ssh name for all the nodes
nodeCount = int(sys.argv[2])            #number of nodes in the installation
nodes = []                              #list of node names used during ssh

# determine the text string for each of the nodes and add them to the array
for i in range(1, nodeCount + 1):
	target = instanceExample

	targetParts = target.split('wa0')                                               #splits the name into the isntallation, wa??, and hostname

	target = targetParts[0] + "wa" + str(i).zfill(2) + targetParts[1][1:]           #replaces wa?? with wa[new number of node in list]

	nodes.append(target)

# continuously iterate over the list of nodes and send bash command to ssh and print number of threads
while True:
	print("--------------------------")
	command = '''ssh noc-mgmt1.phx1.jivehosted.com "cd /jmx_watch/ '''
	for i in range(nodeCount):
		command += '; sudo bash /jmx_watch/jmx.sh ' + nodes[i] + ' 6651'
	command += '"'
	os.system(command)

		#print("piping command: " + command)
		#pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

		#print ("sleeping")
		#time.sleep(2)

		#stdout = pipe.communicate()[0]

		#output = stdout.decode("utf-8")
		#print("output: " + output)

		#result = int(output[len(output)-2:])
		#print(nodes[i] + ": " + result)
	print("--------------------------")
	print('*')
