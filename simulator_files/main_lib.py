#!/usr/bin/env python3
# Function library to handle FortiSOAR communication
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

from .artifact_factory import *
from scapy.all import *


MAINCONFIG_FILE = 'config.json'
PLAYBOOKS_FILE = 'playbooks.json'
FSR_CONFIG_FILE = 'fsr_config.json'
SCENARIO_FILES = ['info.json','infographics.gif',PLAYBOOKS_FILE,'scenario.json']

#TODO
def remote_repo_sync():
# old_git_version=git --git-dir
# status=`git -C $gitDir pull`
# if status != "Already up-to-date.":
# 	git -C $gitDir fetch origin
# 	git -C $gitDir reset --hard origin/master
	return None

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
		logger.error('Sending Event Failed', sys.exc_info()[0])

def read_json(data):
		try:
			json_data=json.loads(data)

		except ValueError:
			logger.error(bcolors.FAIL+"Bad JSON Syntax: "+data+bcolors.ENDC)
			return None
		else:
			return json_data

def load_scenario_folder(scenario_folder_path,scenario_files):
	"""loads the json files within the scenario folder into a single json object"""
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
			logger.error(bcolors.FAIL+"Couldn't open scenario file "+file+", make sure the file exists"+bcolors.ENDC)
			exit()
		except ValueError:
			logger.error(bcolors.FAIL+"Bad Config file: "+file+" syntax"+bcolors.ENDC)
			exit()
		else:
			scenario_data.update({file:file_content})

	return scenario_data


def read_config(config_file=MAINCONFIG_FILE):
	try:
		with open(config_file, 'r') as file:
			config = file.read()
		file.close()
		logger.info('Parsing config file: {0}'.format(config_file))
		config=json.loads(config)
		copyfile(config_file, tmp_config_file)

	except IOError:
		logger.error(bcolors.FAIL+"Couldn't open config file: {0}, make sure the file exists and its JSON syntax is correct".format(config_file)+bcolors.ENDC)
		sys.exit()
	except ValueError:
		logger.error(bcolors.FAIL+"Bad Config file JSON syntax"+bcolors.ENDC)
		sys.exit()
	else:
		return config

def unprivileged_send_fsm_event(event,sudo_password):
	"""To be used when the tool is runs as an unprivileged user"""
	try:
		daemon_status=stat.S_ISFIFO(os.stat(SOCSIM_FIFO).st_mode)
	except FileNotFoundError:
		command = sys.executable + ' ./socsim_daemon.py &'
		exit_status = os.system('echo %s|sudo -S %s' % (sudo_password, command))
		time.sleep(2)
		if exit_status != 0:
			logger.error(bcolors.FAIL+"Couldn't start socsim_daemon, exit status: "+exit_status+bcolors.ENDC)
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
			logger.info(source_ip,destination_ip,' not a valid IP address')
			return None
		send_event(source_ip,destination_ip,payload)
	except:
		logger.error(bcolors.FAIL+"Couldn't send event: "+payload+bcolors.ENDC)
		exit()


def resolve_tags(scenario_json):
	''' Reads json scenario and replaces each tag with its equivalent function output'''
	try:
		template_file = json.dumps(scenario_json)
		tag_list = re.findall('\{\{(.*?)\}\}',template_file)
		for tag in tag_list:
			if ',' in tag and length(tag.split(",")) > 1:
				args_list = tag.split(",")
				tag = args_list[0]
				function_args = args_list[1:]
				template_file=template_file.replace('{{'+tag+'}}',str(function_dictionary[tag](tuple(function_args)))) # use *args as functions input
			else:
				template_file=template_file.replace('{{'+tag+'}}',str(function_dictionary[tag]()))
	except:
		logger.error(bcolors.FAIL+"Couldn't process template,playbooks definition files: "+bcolors.ENDC)
		exit()

	return json.loads(template_file),json.loads(playbooks_definition)	
