#!/usr/bin/env python3
# Function library to handle FortiSOAR communication
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

from .artifact_factory import *
from scapy.all import *


MAINCONFIG_FILE="config.json"
PLAYBOOKS_FILE='playbooks.json'
SCENARIO_FILES=['info.json','infographics.gif',PLAYBOOKS_FILE,'scenario.json']

def is_valid_ip(ip):
	ip = ip.split('.')
	if len(ip) != 4:
		return False
	for x in ip:
		if not x.isdigit():
			return False
		i = int(x)
		if i < 0 or i > 255:
			return False
	return True

def send_event(source_ip,destination_ip,payload):
	try:	
		spoofed_packet = IP(src=source_ip, dst=destination_ip) / UDP(sport=random.randint(30000, 35000), dport=514) / payload
		send(spoofed_packet)
	except:
		print ('Sending Event Failed', sys.exc_info()[0])

def read_json(data):
		try:
			json_data=json.loads(data)

		except ValueError:
			print(bcolors.FAIL+"Bad JSON event syntax: "+data+bcolors.ENDC)
			return None
		else:
			return json_data

def load_scenario_folder(scenario_folder_path,scenario_files):
	"""loadss the json files within the scenario folder into a single json object"""
	scenario_data={}

	for file in scenario_files:
		if not 'json' in file:
			continue

		if scenario_folder_path[-1] != '/':
			scenario_folder_path=scenario_folder_path + '/'

		try:
			with open(scenario_folder_path+file, 'r') as f:
				file_content = f.read()
			f.close()
			file_content=json.loads(file_content)

		except IOError:
			if file == PLAYBOOKS_FILE:
				scenario_data.update({PLAYBOOKS_FILE:""})
				continue
			print(bcolors.FAIL+"Couldn't open scenario file "+file+", make sure the file exists"+bcolors.ENDC)
			exit()
		except ValueError:
			print(bcolors.FAIL+"Bad Config file: "+file+" syntax"+bcolors.ENDC)
			exit()		
		else:
			scenario_data.update({file:file_content})

	return scenario_data


def read_mainconfig():
	try:
		with open(MAINCONFIG_FILE, 'r') as f:
			mainconfig_file = f.read()
		f.close()
		mainconfig_file=json.loads(mainconfig_file)

	except IOError:
		print(bcolors.FAIL+"Couldn't open config file, fall back to command arguments"+bcolors.ENDC)
		return None
	except ValueError:
		print(bcolors.FAIL+"Bad Config file syntax, fall back to command arguments"+bcolors.ENDC)
		return None		
	else:
		return mainconfig_file

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
			print(source_ip,destination_ip,' not a valid IP address')
			return None
		send_event(source_ip,destination_ip,payload)
	except:
		print(bcolors.FAIL+"Couldn't send event: "+payload+bcolors.ENDC)
		exit()





