# (ftnt) SOC Simulator:

-- Work in Progress --

## Introduction:
A tool meant to be used during demos to simulate a SOAR/SIEM environement by sending a series of alerts with a specific timing according to a template. this creates a scenario to illustrate targeted FortiSOAR/FSM capabilities.
it is written in python so it can run on any machine with python installed including FortiSOAR/FSM. It simulates an Asset network connected to the internet via FortiGate Firewall (FortiGate-Edge) and a set of alert sources including:
-FortiSIEM
-Qradar
-MS Exchange
-Others to come

The Environement requires a FortiGate to be used as a response enforcement point.
## How to use:
```
usage: ProgramName [-h] [-s SERVER] [-u USERNAME] [-p PASSWORD] [-j STEP] -f
                   SCENARIO_FOLDER [-t TENANT]

optional arguments:
  -h, --help            		Show this help message and exit
  -s SERVER, --server 			IP or hostname of the target product (ex: FortiSOAR IP)
  -u USERNAME, --username 		Tagret product USERNAME
  -p PASSWORD, --password 		Target product PASSWORD
  -j STEP, --step STEP  		Run a specific step of the scenario and exit (Optional)
  -f SCENARIO_FOLDER, --scenario-folder SCENARIO_FOLDER 
                        Scenario folder exp: FSOAR_scenarios/Malware_Lateral_Movement
  -t TENANT, --tenant tenant 	Tenant name in case of a multi-tenant instance (Optional)
```
Any of the above parameters can be stored in a config.json file to avoid having to supply it as an cli argument. to use it, edit config.json_sample and rename it to config.json.

Example:
```json
{
	"server":"10.2.2.1",
	"username":"csadmin",
	"password":"password",
	"random":"yes",
	"tenant":"",
	"TR_FG_MGMT_IP":"10.200.3.1",
	"TR_FG_DEV_NAME":"FortiGate-Edge",
	"TR_CUSTOMER_LAN":"10.200.3.0/24"
}
```
TR_* are environment constant attributes to be used in the scenarios, see scenario.json section below

## Components:

- Main script: The main cli
- Modules Directory: Contain various functions libraries
- Templates Directory: Contains the available templates to be used during the demo, each template file represents a scenario. it is a list of dictionary objects.
- SOCSIM_Daemon: implementing functions which require root privileges such as sending spoofed syslogs to FortiSIEM

### Templates:
Each scenario template is a folder containing:
Scenario_Name.pptx 	: A powerpoint describing the scenario
info.json 			: Scenario meta data
infocgraphics.gif 	: Scenario diagram
playbooks.json 		: The FortiSOAR plabook collection containing the required playbooks for the scenario, this collection will be pushed to FortiSOAR at run time.
scenario.json 		: The list of Alerts to be send with their timing/transition configuration

#### info.json
It contains the scenario meta data and dependencies, this file is first read and used in the scenario initiation

| Config attribute | description|
|---|---|
|name | Scneario Descriptive Name, (usualy the same as the folder name where the scenario files are stored)|
| product | fortisoar, fortisiem, This is for the simulator to identify the target product|
| connectors_dependencies| [name_of_the_connectors,] FortiSOAR connector name which must be configured and set to default before running the scneario|
|version | version of the scenario |
|description | high level scenario description|
|category | audience type: analysts, C level...etc|
|publisher | scenario owner|
|infographic | link to the infographic file|

Example:
```json
{
    "name": "Malware Lateral Movement Scenario",
    "product":"fortisoar",
    "category":"soc_analyst",
    "connectors_dependencies":["virustotal"],
    "version": "1.0.0",
    "description": "an infected machine connects to a CnC server, followed by another (false positive), then a third one",
    "category": "soc_analyst",
    "publisher": "CSE-Team",
    "infographic": "https://github.com/ftnt-cse/soc_simulator/raw/master/FSOAR_scenarios/Case_Management_and_Visibility/infocgraphics.gif"
}
```


#### playbooks.json
Typically the playbook collection is created while developing the scenario on FortiSOAR, once completed it has to be exported as playbooks.json so the simulator can upload it to the FortiSOAR unstance where it runs. To make sure the playbooks within this collection are only triggered for the scenario alerts the 'source' value of the scneario.json template file has to be used as a filter all playbooks.json collection playbooks. 

#### scenario.json
A sample template structure:
```json
[
{
"data":[
		{
		"sleep":-1,
		"name": "Traffic to FortiGuard Malware IP List",
		"source":"FSM-INTL-DEMO",
		"sourcedata":{
			 	"incident": {
						"id": 8119518313,
						"xmlId": "Incident@000000000",
						"ruleDesc": "Detects network traffic to FortiGuard Blocked IP List",
						"ruleName": "Traffic to FortiGuard Malware IP List",
						"severity": 9,
						"origDevIp": "{{TR_FG_MGMT_IP}}",
						"srcIpAddr": "{{TR_ASSET_IP}}1",
						"cacheIndex": "<phCustId>2002</phCustId>",
						"destIpAddr": "{{TR_MALICIOUS_IP}}",
						"externalId": 8179,
						"incidentEt": "PH_RULE_TO_FORTIGUARD_MALWARE_IP",
						"origDevName": "{{TR_FG_DEV_NAME}}",
						"severityCat": "HIGH",
						"creationTime": "{{TR_NOW}}",
						"deviceStatus": "Pending",
						"lastModified": "{{TR_NOW}}",
						"lastSeenTime": "{{TR_NOW}}",
						"ticketStatus": "None",
						"firstSeenTime": "{{TR_PAST}}",
						"incidentCount": "{{TR_RANDOM_INTEGER}}",
						"incidentTarget": "destIpAddr:,",
						"incidentCategory": "Security/Command and Control",
						"phIncidentCategory": "Network",
						}
				}
		}
	]
},
{
"data":[
		{
		"sleep":0,
		"name": "Traffic to FortiGuard Malware IP List",
		"source":"FSM-INTL-DEMO",
		"sourcedata":{
			 	"incident": {
						"id": 8119518313,
						"xmlId": "Incident@000000000",
						"ruleDesc": "Detects network traffic to FortiGuard Blocked IP List",
						"ruleName": "Traffic to FortiGuard Malware IP List",
						"severity": 9,
						"origDevIp": "{{TR_FG_MGMT_IP}}",
						"srcIpAddr": "{{TR_ASSET_IP}}2",
						"cacheIndex": "<phCustId>2002</phCustId>",
						"destIpAddr": "{{TR_MALICIOUS_IP}}",
						"externalId": 8179,
						"incidentEt": "PH_RULE_TO_FORTIGUARD_MALWARE_IP",
						"origDevName": "{{TR_FG_DEV_NAME}}",
						"severityCat": "HIGH",
						"creationTime": "{{TR_NOW}}",
						"deviceStatus": "Pending",
						"lastModified": "{{TR_NOW}}",
						"lastSeenTime": "{{TR_NOW}}",
						"ticketStatus": "None",
						"firstSeenTime": "{{TR_PAST}}",
						"incidentCount": "{{TR_RANDOM_INTEGER}}",
						"incidentTarget": "destIpAddr:,",
						"incidentCategory": "Security/Command and Control",
						"phIncidentCategory": "Network",
						}
				}
		}
	]
}
]
```
- __"sleep":__ can take the values : 
- 0 => the alert will be sent immediatly 
- a negative integet => The user will be prompted to press any key to send the alert and continue to the next one
- a positive integer => would indicate the number of seconds to wait before sending the current alert

 Template file contains the static text as sent from the alert source device and a set of variables delimited with {{}}.

All variables will be replaced with their dynamic value at runtime. when a list of alerts is present within the same template you can manipulate variable values by statically concatenating values, example : 

If {{TR_ASSET_IP}} is present in both alerts of the same template it's possible to set the first as: {{TR_ASSET_IP}}1 and {{TR_ASSET_IP}}2 in the second, so the sent alert will have 2 values of {{TR_ASSET_IP}}

The list of available dynamic values (Variables):

|"VARIABLE"|function name|use case|
|:----------|:-------------|:-------------|
|"TR_FG_MGMT_IP"|get_fg_mgmt_ip|get fortigate mgmt IP (according to the topology file)|
|"TR_FG_DEV_NAME"|get_fg_dev_name|get fortigate device name (according to the topology file)|
|"TR_ASSET_IP"|get_asset_ip| get a random local IP|
|"TR_MALICIOUS_IP"|get_malicious_ip| get a malicious IP from CTI|
|"TR_NOW"|get_time_now|get current timestamp|
|"TR_RANDOM_INTEGER"|get_random_integer|get random number between 55555 and 99999|
|"TR_MALICIOUS_DOMAIN"|get_malicious_domains| get a malicious domain name from CTI|
|"TR_MALICIOUS_URL"|get_malicious_url|get a malicious url from CTI|
|"TR_MALICIOUS_HASH"|get_malware_hash|get malicious hash from CTI|
|"TR_PUBLIC_IP"|get_my_public_ip|get your public IP address|
|"TR_PAST"|get_time_past |up to a couple of days ago|
|"TR_T-1"|get_time_minus_one |get timestamp of about one hour ago|
|"TR_T-2"|get_time_minus_two |get timestamp of about two hours ago|
|"TR_T-3"|get_time_minus_tree|get timestamp of about three hours ago|
|"TR_T-4"|get_time_minus_four|get timestamp of about four hours ago|
|"TR_T-5"|get_time_minus_five|get timestamp of about five hours ago|
|"TR_T-6"|get_time_minus_six |get timestamp of about six hours ago)
|"TR_USERNAME"|get_username|a random username|

### SOCSIM_Daemon:
If the scenario includes events to be sent via syslog to FortiSIEM and soc_simulator is running with unprivileged user, the configuration paramter : sudo_password located at config.json will be used to run socsim_dameon.py as root. soc_simulator will then use it to send syslogs via a named pipe.
If soc_simulator is run as root, events are sent directly.