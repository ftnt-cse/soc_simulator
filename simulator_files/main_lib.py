#!/bin/python3
# Function library to handle FortiSOAR communication
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

from .artifact_factory import *
MAINCONFIG_FILE="config.json"
PLAYBOOKS_FILE='playbooks.json'
SCENARIO_FILES=['info.json','infographics.gif',PLAYBOOKS_FILE,'scenario.json']

def load_scenario_folder(scenario_folder_path,scenario_files):
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
