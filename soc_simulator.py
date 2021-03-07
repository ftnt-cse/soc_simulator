#!/usr/bin/env python3
# Main: CLI
# FortiSOAR CSE Team
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND
# __version__ = "0.202"

import os
import sys
from soc_simulator.artifact_factory import *
from soc_simulator.fortisoar_lib import *
from soc_simulator.main_lib import *


def main():
	tenant_iri = None
	parser = argparse.ArgumentParser(
	prog = 'ProgramName',
	formatter_class = argparse.RawDescriptionHelpFormatter,
	epilog = textwrap.dedent('''\
		 SOC Simulator: use config.json to configure FortiSIEM and FortiSOAR IPs and credentials depending on your environment
		 '''))
	parser.add_argument('-f', '--scenario-folder',type=str, required=True, help="Scenario folder exp: ./scenarios/FortiSOAR/Comprmised_Web_Server/")
	parser.add_argument('-j', '--step',type=str, required=False, help="Run a specific step of the scenario and exit")
	parser.add_argument('-t', '--tenant',type=str, required=False, help='Tenant IRI')
	parser.add_argument('-c', '--config',type=str, required=False, help='configuration file to use, default is config.json')
	args = parser.parse_args()


	if args.config:
		config = read_config(args.config)
	else:
		config = read_config()	


	if not os.path.isdir(args.scenario_folder):
		logger.error("{0}{1}Doesn't exist, make sure you select the right folder{2}"
			.format(bcolors.FAIL,args.scenario_folder,bcolors.ENDC))
		sys.exit()

	scenario_data = load_scenario_folder(args.scenario_folder,SCENARIO_FILES)
	
	if 'fortisoar' in args.scenario_folder.lower():
		headers=fsr_login(config['FORTISOAR_IP'],config['fortisoar_username'],config['fortisoar_password'])

		# TODO : comlete import process
		#fsr_config_file = fsr_import_configuration(config['FORTISOAR_IP'],headers,args.scenario_folder+FSR_CONFIG_FILE)
		
		if args.tenant:
			tenant_iri = lookup_tenant_iri(config['FORTISOAR_IP'],headers,args.tenant)['@id']

		if 'connectors_dependencies' in scenario_data['info.json']:
			check_connectors_prerequisites(config['FORTISOAR_IP'],headers,scenario_data['info.json']['connectors_dependencies'])

		if 'fsr_user_dependencies' in scenario_data['info.json']:
			for user in scenario_data['info.json']['fsr_user_dependencies']:
				fsr_create_user(config['FORTISOAR_IP'],headers,user)

		if 'fsr_picklist_dependencies' in scenario_data['info.json']:
			for entry in scenario_data['info.json']['fsr_picklist_dependencies']:
				fsr_update_picklist(config['FORTISOAR_IP'],headers,entry,scenario_data['info.json']['fsr_picklist_dependencies'][entry])
				
		if os.getuid() == 0:
			logger.info('running as root')
			if 'fsm_events_dependencies' in scenario_data['info.json']:
				for event in scenario_data['info.json']['fsm_events_dependencies']:
					logger.info('sending event to {0}'.format(event['destination_ip']))
					send_fsm_event(event)
					time.sleep(1)

		else:
			logger.info('{0}You need to be "root" to send syslogs{1}'.format(bcolors.OKGREEN,bcolors.ENDC))

		alerts,playbooks_definition=cook_alert(config['FORTISOAR_IP'],headers,scenario_data['scenario.json'],scenario_data['playbooks.json'])
		upload_playbooks(config['FORTISOAR_IP'],headers,playbooks_definition)

		if args.step:
			step=int(args.step) - 1
			if step < 0 or step > len(alerts)-1:
				logger.error('{0}The selected step is lower or greater than the current scneario step count, select a step from 1 to {1}{2}'
					.format(bcolors.FAIL,str(len(alerts)),bcolors.ENDC))
				sys.exit()
			logger.info('{0}Sending alert #: {1}{2}'.format(bcolors.OKGREEN,step+1,bcolors.ENDC))
			fsr_send_alert(config['FORTISOAR_IP'],headers,alerts[step],True,tenant_iri)
			if alerts[step]['data'][0]['demo_message']:
			 	logger.info('{0}\nStep Instructions:\n{1}{2}'.format(bcolors.INST,alerts[step]['data'][0]['demo_message'],bcolors.ENDC))
			sys.exit()



		for alert in alerts:
			fsr_send_alert(config['FORTISOAR_IP'],headers,alert,False,tenant_iri)
			if alert['data'][0]['demo_message']:
				logger.info('{0}\nStep Instructions: \n{1}{2}'.format(bcolors.INST,alert['data'][0]['demo_message'],bcolors.ENDC))

if __name__ == '__main__':
	main()
