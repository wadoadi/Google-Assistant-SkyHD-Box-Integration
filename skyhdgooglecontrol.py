#!/usr/bin/env python

import configparser, pika, json, time, os, sys, time, datetime
print(datetime.datetime.now() + "SkyHD Google Control script started")
print("path: " + os.path.abspath(os.path.dirname(sys.argv[0])))
time.sleep(1) # delay 1 sec to give time for some of the system processes to load needed if lauching on boot of the Pi

config = configparser.ConfigParser()

#load config from the config file in the same folder as the python file is run from
config.read(os.path.abspath(os.path.dirname(sys.argv[0]))+ "//" + 'config.ini')

params = pika.URLParameters(config['CloudAMQP']['url'])
params.socket_timeout = 5

#the connection may not be ready if this file is being run at reboot of the Pi so lets check and wait for it to be ready.
connection = None
while connection is None:
	try:
		connection = pika.BlockingConnection(params) # Connect to CloudAMQP
	except Exception:
		print("Connection failed")
		time.sleep(2)
		continue

channel = connection.channel() # start a channel
		
def sky_command(strcommand):	
		print("in command " + strcommand)
		strcommand = strcommand.lower().strip()
		#print("command lower cased and stripped: " + strcommand)
		
		if strcommand.isnumeric():
			#print("its a number!")
			#Sky channel numbers are 100 - 999 only
			if int(strcommand) < 100 or int(strcommand) > 999:
				print("Number out of range")
				return
			else:
				#SkyHDControl needs the number spaced out
				strcommand = strcommand[0] + " " + strcommand[1] + " " + strcommand[2]
				#print("Spaced number : " + strcommand)
		
		#list of commands that may need changing
		if strcommand == "fast forward":
			strcommand = "fastforward"
		elif strcommand == "halt" or strcommand == ".":	
			strcommand = "stop"
		elif strcommand == "tv guide":	
			strcommand = "tvguide"	
		elif strcommand == "channel up":	
			strcommand = "channelup"
		elif strcommand == "channel down":				
			strcommand = "channeldown"
		elif strcommand == "eye"  or strcommand == "high":				
			strcommand = "i"
		
		#shortcut list for named channels
		elif strcommand == "itv":
			strcommand = "1 7 8"
		elif strcommand == "bbc one" or strcommand == "bbc 1":
			strcommand = "1 1 5"
		elif strcommand == "bbc 2" or strcommand == "bbc two":
			strcommand = "1 0 2"
		elif strcommand == "sky 1" or strcommand == "sky one":
			strcommand = "1 0 6"
			
		print(datetime.datetime.now() + "Sending : sky-remote-cl " + config['SkyHDControl']['host'] + " " + strcommand)
		os.system ("sky-remote-cli " + config['SkyHDControl']['host'] + " " + strcommand) 
		time.sleep(0.5)
			
# create a function which is called on incoming messages
def callback(ch, method, properties, body):
	#print("in callback")
	str_response = body.decode('utf-8')
	#print(str_response)
	message = json.loads(str_response)
	
	if message['command'] == "command":
		sky_command(message['value'])
	else:
		print ("There is no custom command implemented for", message['command'])
		
# set up subscription on the queue
channel.basic_consume(callback, queue=config['CloudAMQP']['queue'], no_ack=True)

#print "Waiting for commands"
channel.start_consuming() # start consuming (blocks)

connection.close()
