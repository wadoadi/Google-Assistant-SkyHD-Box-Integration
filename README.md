# Google-Assistant-SkyHD-Box-Integration
Use Google Assistant to control your SkyHD via a RPi

This project uses Google asistant to control SkyHD box via a Raspberry Pi
It builds upon the work done to control a Samsung TV here https://github.com/StancuFlorin/Google-Assistant-Samsung-Smart-TV-Integration
and the work done by SkyHDControl here https://github.com/dalhundal/sky-remote-cli

Use your Google Home device as a remote for your SkyHD box. 
The basic flow (flow.png) is as below:

![alt text](https://github.com/wadoadi/Google-Assistant-SkyHD-Box-Integration/blob/master/flow.png)

## Requirements ##

- Python 3.4
- install SkyHDControl on the Raspberry Pi "npm install -g sky-remote-cli"

## Installation ##

### CloudAMQP ###
- Create a free account on [CloudAMQP](https://www.cloudamqp.com).
- Create a new instance of the free plan.
- Go to the RabbitMQ Manager.
- Add a new ``exchange``:
	- name: ``google.home.assistant``
	- type: ``direct``
- Add a new ``queue``:
	- name: ``skyhdbox.smart.tv``
	- arguments: ``Message TTL`` with the value of ``30000``. The name of this feature is ``x-message-ttl``
- Go back to the exchange that you created and add a binding to the queue:
	- name: ``skyhdbox.smart.tv``
	- routing key: ``skyhdbox.smart.tv``

### Locally ###

- Check the ``config.ini`` file and add your own details there.
- To enable to comunication with your SkyHD box you will need to put the correct IP in [SkyHDControl] host, check your Sky box network settings for this. Your Sky box should be on the same network as the Pi that will run this script. SkyQ box owners will need to modify the script.
- The CloudAMQP information also needs to be added. 
- Run the script using ``python3 skyhdgooglecontrol.py`` 


### IFTTT ###

- Create a new applet on [IFTTT] https://ifttt.com/ create a new Applet for "Google assistant" 
- "If This" = Google Assistant 
- "Say a phrase with a text ingredient".
- Add a phrase. Use only lower case letters and add the $ where the command will go (ex: sky box $).
- On ``that`` select `"Webhooks" and "Make a web request".
- URL add https://YourDetails@mosquito.rmq.cloudamqp.com/api/exchanges/xhbuefux/google.home.assistant/publish  Change the username, password and the RabbitMQ host with your own the whole url is found at "AMQP URL" at https://customer.cloudamqp.com/instance
- Select ``POST`` method and ``application/json`` as content type.
- for body add  
	
	{ "properties":{ "content-type":"application/json" }, "routing_key":"skyhdbox.smart.tv", "payload":"{\"command\": \"command\", \"value\": \" {{TextField}}\"}", "payload_encoding":"string" }



## Make the script start at startup ##

On your Raspberry Pi to run this script you may want to make it start each time you boot your device. There are several ways how to do it. this how I have it.

"sudo nano /etc/rc.local"

Before "exit 0" put the below line. This will start the script after each reboot.

"nohup /usr/bin/python3 /home/pi/SkyTv/skyhdgooglecontrol.py 2>&1 &>/tmp/sky.log $"

Save the file and exit

Reboot the Pi
"sudo reboot"

