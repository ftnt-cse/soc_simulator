#!/usr/bin/env python3
# Main: CLI
# FortiSOAR CSE Team
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND
__version__ = "0.201"

import os, sys
os.chdir(sys.path[0])

from simulator_files.artifact_factory import *
from simulator_files.fortisoar_lib import *
from simulator_files.main_lib import *
from simulator_files.fortisiem_lib import *

def main():
	config=read_mainconfig()
	tenant_iri=None
	parser = argparse.ArgumentParser(
	prog='ProgramName',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	epilog=textwrap.dedent('''\
		 SOC Simulator: use config.json to configure FortiSIEM and FortiSOAR IPs and credentials depending on your environment
		 '''))
	parser.add_argument('-f', '--scenario-folder',type=str, required=True, help="Scenario folder exp: ./scenarios/FortiSOAR/Comprmised_Web_Server/")

	parser.add_argument('-j', '--step',type=str, required=False, help="Run a specific step of the scenario and exit")

	parser.add_argument('-t', '--tenant',type=str, required=False, help='Tenant IRI')

	args = parser.parse_args()

	if not os.path.isdir(args.scenario_folder):
		print(bcolors.FAIL+args.scenario_folder+" Doesn't exist, make sure you select the right folder"+bcolors.ENDC)
		exit()

	scenario_data=load_scenario_folder(args.scenario_folder,SCENARIO_FILES)

	if 'fortisoar' in args.scenario_folder.lower():
		headers=fsr_login(config['FORTISOAR_IP'],config['fortisoar_username'],config['fortisoar_password'])

		if args.tenant:
			tenant_iri=lookup_tenant_iri(config['FORTISOAR_IP'],headers,args.tenant)['@id']

		if 'connectors_dependencies' in scenario_data['info.json']:
			check_connectors_prerequisites(config['FORTISOAR_IP'],headers,scenario_data['info.json']['connectors_dependencies'])

		if 'fsr_user_dependencies' in scenario_data['info.json']:
			for user in scenario_data['info.json']['fsr_user_dependencies']:
				fsr_create_user(config['FORTISOAR_IP'],headers,user)


		if getpass.getuser() == 'root':
			print('running as root')
			if 'fsm_events_dependencies' in scenario_data['info.json']:
				for event in scenario_data['info.json']['fsm_events_dependencies']:
					print('sending event to',event['destination_ip'])
					send_fsm_event(event)
					time.sleep(1)

		else:
			if 'fsm_events_dependencies' in scenario_data['info.json'] and len(config['sudo_password']) > 3:
				for event in scenario_data['info.json']['fsm_events_dependencies']:
					print('sending event to',event['destination_ip'])
					unprivileged_send_fsm_event(event,config['sudo_password'])
					time.sleep(1)

		alerts,playbooks_definition=cook_alert(config['FORTISOAR_IP'],headers,scenario_data['scenario.json'],malware_hashes,malicious_urls,malicious_ips,malicious_domains,scenario_data['playbooks.json'])
		#print(json.dumps(playbooks_definition, indent=4, sort_keys=True))
		upload_playbooks(config['FORTISOAR_IP'],headers,playbooks_definition)

		if args.step:
			step=int(args.step) - 1
			#print(step,len(alerts)) 
			if step < 0 or step > len(alerts)-1:
				print(bcolors.FAIL+"The selected step is lower or greater than the current scneario step count, select a step from 1 to "+str(len(alerts))+bcolors.ENDC)
				exit(1)
			print(bcolors.OKGREEN+'Sending alert #: {}'.format(step+1)+bcolors.ENDC)
			fsr_send_alert(config['FORTISOAR_IP'],headers,alerts[step],True,tenant_iri)
			if alerts[step]['data'][0]['demo_message']:
			 	print(bcolors.INST+"Step Instructions: \n"+alerts[step]['data'][0]['demo_message']+bcolors.ENDC)
			exit(0)


		for alert in alerts:
			fsr_send_alert(config['FORTISOAR_IP'],headers,alert,False,tenant_iri)
			if alert['data'][0]['demo_message']:
				print(bcolors.INST+"Step Instructions: \n"+alert['data'][0]['demo_message']+bcolors.ENDC)

	if 'fortisiem' in args.scenario_folder.lower():
		eventCount = 1
		for event in cook_fsm_events(scenario_data['scenario.json']):
			print(bcolors.INST+event['demo_message']+bcolors.ENDC)
			if len(event['destination_ip']) < 7:
				print(bcolors.OKGREEN+'Setting destination IP address to pre-configured FortiSIEM IP:'+bcolors.ENDC,bcolors.MSG+config['FORTISIEM_IP']+bcolors.ENDC)
				event['destination_ip'] = config['FORTISIEM_IP']
			print(bcolors.OKGREEN+'Sending event from'+bcolors.ENDC,bcolors.MSG+str(event['source_ip'])+bcolors.ENDC,bcolors.OKGREEN+'to:'+bcolors.ENDC,bcolors.MSG+str(event['destination_ip'])+bcolors.ENDC)
			send_fsm_event(event)
			if eventCount < len(cook_fsm_events(scenario_data['scenario.json'])):
				if event['sleep'] > 0:
					input(bcolors.MSG+"Sleeping for {} seconds".format(sleep)+bcolors.ENDC)
					time.sleep(event['sleep'])
				else:
					input(bcolors.MSG+"Press Enter key to continue"+bcolors.ENDC)
			eventCount += 1

if __name__ == '__main__':
	main()
