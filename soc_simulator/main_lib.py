#!/usr/bin/env python3
# Function library to handle FortiSOAR communication
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

from .artifact_factory import *

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
