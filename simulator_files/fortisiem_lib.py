#!/usr/bin/env python3
# Function library to handle FortiSOAR communication
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

from .artifact_factory import *
from .main_lib import *
from scapy.all import *


def send_event(source_ip,destination_ip,payload):
	try:
		spoofed_packet = IP(src=source_ip, dst=destination_ip) / UDP(sport=random.randint(30000, 35000), dport=514) / payload
		send(spoofed_packet)
	except:
		print ('Sending Event Failed', sys.exc_info()[0])

def unprivileged_send_fsm_event(event,sudo_password):
	"""To be used when the tool is runs as an unprivileged user"""
	try:
		daemon_status=stat.S_ISFIFO(os.stat(SOCSIM_FIFO).st_mode)
	except FileNotFoundError:
		command = sys.executable + ' ./socsim_daemon.py &'
		exit_status = os.system('echo %s|sudo -S %s' % (sudo_password, command))
		time.sleep(2)
		if exit_status != 0:
			print(bcolors.FAIL+"Couldn't start socsim_daemon, exit status: "+exit_status+bcolors.ENDC)
			exit()

	# ship the event to socsim_daemon over SOCSIM_FIFO pipe
	raw_event = json.dumps(event).replace('\\"','\\\"')
	event = str.encode((raw_event))

	fifo = os.open(SOCSIM_FIFO, os.O_WRONLY)
	os.write(fifo, event)
	os.close(fifo)

def send_fsm_event(event):
	"""Default FortiSIEM send events while the tool is running as root"""
	try:
		source_ip=event['source_ip']
		destination_ip=event['destination_ip']
		payload=event['payload']
		if not is_valid_ip(source_ip) or not is_valid_ip(destination_ip):
			return source_ip,destination_ip,' not a valid IP address'
		send_event(source_ip,destination_ip,payload)
	except:
		print(bcolors.FAIL+"Couldn't send event: ",source_ip,destination_ip,payload,bcolors.ENDC)
		exit()


def cook_fsm_events(scenario_json):
	try:
		template_file = json.dumps(scenario_json)
		tag_list = re.findall('\{\{(.*?)\}\}',template_file)
		for tag in tag_list:
			template_file=template_file.replace('{{'+tag+'}}',str(function_dictionary[tag]()))

	except:
		print(bcolors.FAIL+"Couldn't process FortiSIEM template file"+bcolors.ENDC)
		exit()

	return json.loads(template_file)
