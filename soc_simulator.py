#!/usr/bin/env python3
# Main: CLI
# FortiSOAR CSE Team
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

import os, sys
os.chdir(sys.path[0])

from simulator_files.artifact_factory import *
from simulator_files.fortisoar_lib import *
from simulator_files.main_lib import *

def main():
	config=read_mainconfig()

	tenant_iri=None
	parser = argparse.ArgumentParser(
	prog='ProgramName',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	epilog=textwrap.dedent('''\
		 FSR Alert Simulator
		 '''))
	if config and 'server' in config:
		parser.add_argument('-s', '--server',type=str, required=False, default=config['server'],help="FortiSOAR IP Address (wihout http://)")
	else:
		parser.add_argument('-s', '--server',type=str, required=True, help="Fortinet Device IP Address (wihout http://)")

	if config and 'username' in config:
		parser.add_argument('-u', '--username',type=str, required=False, default=config['username'], help="FortiSOAR Username")
	else:
		parser.add_argument('-u', '--username',type=str, required=True, help="FortiSOAR Username")

	if config and 'password' in config:
		parser.add_argument('-p', '--password',type=str, required=False, default=config['password'],help="FortiSOAR Password")
	else:
		parser.add_argument('-p', '--password',type=str, required=True, help="FortiSOAR Password")

	parser.add_argument('-j', '--step',type=str, required=False, help="Run a specific step of the scenario and exit")
	parser.add_argument('-f', '--scenario-folder',type=str, required=True, help="Scenario folder exp: ./templates/soc_analyst/Malware_Lateral_Movement")
	parser.add_argument('-t', '--tenant',type=str, required=False, help='Tenant IRI')

	args = parser.parse_args()

	if not os.path.isdir(args.scenario_folder):
		print(bcolors.FAIL+args.scenario_folder+" Doesn't exist, make sure you select the right folder"+bcolors.ENDC)
		exit()

	scenario_data=load_scenario_folder(args.scenario_folder,SCENARIO_FILES)

	headers=fsr_login(args.server,args.username,args.password)

	if args.tenant:
		tenant_iri=lookup_tenant_iri(args.server,headers,args.tenant)['@id']
	
	# if scenario_data['info.json']['connectors_dependencies']:
	# 	check_connectors_prerequisites(args.server,headers,scenario_data['info.json']['connectors_dependencies'])

	if getpass.getuser() == 'root':
		if scenario_data['info.json']['fsm_events_dependencies']:
			for event in scenario_data['info.json']['fsm_events_dependencies']:
				send_fsm_event(event)
				time.sleep(1)

	else:
		if scenario_data['info.json']['fsm_events_dependencies'] and config['sudo_password']:
			for event in scenario_data['info.json']['fsm_events_dependencies']:
				unprivileged_send_fsm_event(event,config['sudo_password'])
				time.sleep(1)

	alerts,playbooks_definition=cook_alert(args.server,headers,scenario_data['scenario.json'],malware_hashes,malicious_urls,malicious_ips,malicious_domains,scenario_data['playbooks.json'])
	#print(json.dumps(playbooks_definition, indent=4, sort_keys=True))
	upload_playbooks(args.server,headers,playbooks_definition)		

	if args.step:
		step=int(args.step) - 1
		#print(step,len(alerts)) 
		if step < 0 or step > len(alerts)-1:
			print(bcolors.FAIL+"The selected step is lower or greater than the current scneario step count, select a step from 1 to "+str(len(alerts))+bcolors.ENDC)
			exit(1)
		print(bcolors.OKGREEN+'Sending alert #: {}'.format(step+1)+bcolors.ENDC)
		fsr_send_alert(args.server,headers,alerts[step],True,tenant_iri)
		if alerts[step]['data'][0]['demo_message']:
		 	print(bcolors.INST+"Step Instructions: \n"+alerts[step]['data'][0]['demo_message']+bcolors.ENDC)
		exit(0)


	for alert in alerts:
		fsr_send_alert(args.server,headers,alert,False,tenant_iri)
		if alert['data'][0]['demo_message']:
			print(bcolors.INST+"Step Instructions: \n"+alert['data'][0]['demo_message']+bcolors.ENDC)

if __name__ == '__main__':
	main()
