#!/bin/python3
# Function library to handle FortiSOAR communication
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

#import pdb;pdb.set_trace()

from .artifact_factory import *

def fsr_login(server,username,password):
	body = {
		'credentials': {
			'loginid': username,
			'password': password
		}
	}

	try:
		response = requests.post(
			url='https://'+server+'/auth/authenticate', json=body,
			verify=False
		)
		if response.status_code != 200:
			logger.error('{0}Authentication error{1}'.format(bcolors.FAIL,bcolors.ENDC))
			exit()
		json_response = response.json()
		token = json_response['token']
		headers = {"Authorization": "Bearer " + token}
	except requests.ConnectionError:
		logger.error('{0}Connection error{1}'.format(bcolors.FAIL,bcolors.ENDC))
		exit()
	except requests.ConnectTimeout:
		logger.error('{0}Connection timeout{1}'.format(bcolors.FAIL,bcolors.ENDC))		
		exit()
	else:
		return headers

def lookup_tenant_iri(server,headers,tenant_name):
	try:
		response = requests.get(url='https://'+server+'/api/3/tenants',
			headers=headers,verify=False)

		if response.status_code != 200:
			logger.error('{0}Error retrieving tenants IRI:{1}{2}'.format(bcolors.FAIL,response.text,bcolors.ENDC))
			exit()
		tenants=response.json()
		for tenant in tenants['hydra:member']:
			if tenant_name in tenant['name']:
				return tenant
		else:
			logger.error('{0}Tenant not found{1}'.format(bcolors.FAIL,bcolors.ENDC))
			exit()
	except requests.ConnectionError:
		logger.error('{0}Connection error{1}'.format(bcolors.FAIL,bcolors.ENDC))
		exit()
	except requests.ConnectTimeout:
		logger.error('{0}Connection timeout{1}'.format(bcolors.FAIL,bcolors.ENDC))	
		exit()


def check_connectors_prerequisites(server,headers,connectors_dependencies): # check whether the initial config is done to run the playbooks properly
	try:
		response = requests.get(url='https://'+server+'/api/integration/connectors/?ordering=label&page_size=100&format=json', #search=Connector_name
			headers=headers,verify=False)      

		if response.status_code != 200 or len(response.json()["data"]) < 1:
			logger.error('{0}Error Getting Connectors List: {1}{2}'.format(bcolors.FAIL,response.text,bcolors.ENDC))
			exit()

		for required_connector in connectors_dependencies:
			if not any(connector['name'] == required_connector for connector in response.json()["data"]):
				logger.error('{0}Connector: {1} is not Installed, Install it and try again{2}'.format(bcolors.FAIL,required_connector,bcolors.ENDC))
				exit()
	

		for required_connector in connectors_dependencies:
			for connector in response.json()["data"]:
				if required_connector == connector["name"]:
					if connector["config_count"] < 1:
						logger.error(bcolors.FAIL+'Connector: '+required_connector+' is not Configured, Configure it and try again'+bcolors.ENDC)
						exit()						
		 			# get connector default config:
					config_response = requests.get(url='https://'+server+'/api/integration/connectors/'+connector["name"]+'/'+connector["version"]+'/?format=json',
					headers=headers,verify=False)

					for config in config_response.json()['configuration']:
						if config['default']:
							status_response = requests.get(url='https://'+server+'/api/integration/connectors/healthcheck/'+connector["name"]+'/'+connector["version"]+\
								'/?config='+config['config_id'],headers=headers,verify=False)

							if connector['active'] and status_response.json()['status'] == 'Available':
								logger.info(bcolors.MSG+"Connector: "+connector["name"]+" is properly configured"+bcolors.ENDC)
							else:
								logger.error(bcolors.FAIL+'Missing Prerequisites: Connector '+connector["name"]+' is not properly configured and/or Available'+bcolors.ENDC)
								exit()

							break
					else:
						logger.error(bcolors.FAIL+'Connector '+connector["name"]+' has no default configuration, configure it and try again'+bcolors.ENDC)
						exit()
			
	except requests.ConnectionError:
		logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
		exit()
	except requests.ConnectTimeout:
		logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
		exit()


def lookup_source_data(server,headers):
	try:
		response = requests.get(url='https://'+server+'/api/3/model_metadatas',
			headers=headers,verify=False)

		if response.status_code != 200 or len(response.json()["hydra:member"]) < 1:
			logger.error(bcolors.FAIL+'Error retrieving model_metadatas:'+response.text+bcolors.ENDC)
			exit()

		model_metadatas=response.json()["hydra:member"]
		for model in model_metadatas:
			if model["type"] == "alerts":
				attribute_model_metadata_id = model["@id"]
				break

		response = requests.get(url='https://'+server+attribute_model_metadata_id+'?$relationships=true',
			headers=headers,verify=False)

		if response.status_code != 200:
			logger.error(bcolors.FAIL+'Error retrieving attribute_model_metadata_id:'+response.text+bcolors.ENDC)
			exit()
		
		model_attributes=response.json()["attributes"]

		for attribute in model_attributes:
			if attribute["name"] == "sourceData" or attribute["name"] == "sourcedata":
				return attribute["name"]


	except requests.ConnectionError:
		logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
		exit()
	except requests.ConnectTimeout:
		logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
		exit()


def upload_playbooks(server,headers,playbooks_definition):
	if not playbooks_definition:
		return False

	upload_playbook_json={
		"__data": [{
			"@context": "/api/3/contexts/WorkflowCollection",
			"@type": "WorkflowCollection",
			"name": "00-UNIQUE_COLLECTION_NAME",
			"description": "SIM Playbooks",
			"visible": True,
			"image": None,
			"workflows": [
			],
			"id": 125,
			"createDate": 1588415631,
			"modifyDate": 1588415631
		}],
		"__unique": ["name"],
		"__replace": False
	}
	try:
		# Check if collection and playbooks exist
		upload_playbook_json['__data'][0]['name'] = playbooks_definition['data'][0]['name']
		upload_playbook_json['__data'] = playbooks_definition['data']

		response = requests.get(url='https://'+server+'/api/3/workflow_collections?name='+playbooks_definition['data'][0]['name'],
			headers=headers,verify=False)

		if len(response.json()["hydra:member"]) == 0:
			logger.info(bcolors.MSG+"Uploading Scenario Playbook Collection to FortiSOAR"+bcolors.ENDC)
			response = requests.post(url='https://'+server+'/api/3/bulkupsert/workflow_collections',
			headers=headers,json=upload_playbook_json,verify=False)
			if response.status_code != 200:
				logger.error(bcolors.FAIL+"Could not Upload Playbook Collection: "+response.text+'\nStatus Code:'+str(response.status_code)+bcolors.ENDC)
				exit()
			else:
				logger.info(bcolors.MSG+"Playbook Collection Uploaded Successfully"+bcolors.ENDC)


	except requests.ConnectionError:
		logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
		exit()
	except requests.ConnectTimeout:
		logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
		exit()

def fsr_create_user(server,headers,username):
	if not username:
		return False
	delete_user_json={
						"ids":[]
					 }	
	search_user_json={
					  "sort": [
					    {
					      "field": "modifyDate",
					      "direction": "DESC"
					    }
					  ],
					  "limit": 30,
					  "logic": "AND",
					  "filters": [
					    {
					      "field": "userName",
					      "operator": "like",
					      "_operator": "like",
					      "value": "%"+username+"%",
					      "type": "primitive"
					    }
					  ],
					  "__selectFields": [
					     "userName"
					  ]
					}
	create_user_json={
					"domain": "fortielab.com",
					"securityId": 1,
					"userName": username,
					"recordTags": [
					"/api/3/tags/offender"
					]
					}
	if 'good' in username:
		create_user_json['recordTags']=[]
		create_user_json['securityId']=0
	elif 'bad' in username:
		create_user_json['securityId']=10

	try:
		response = requests.post(url='https://'+server+'/api/query/users?$limit=10',
						headers=headers,json=search_user_json,verify=False)

		if len(response.json()["hydra:member"]) > 0:
			delete_user_json['ids'].append(response.json()["hydra:member"][0]['@id'].split("/")[4])
			response = requests.delete(url='https://'+server+'/api/3/delete/users',
				headers=headers,json=delete_user_json,verify=False)

			if response.status_code != 200:
				logger.error(bcolors.FAIL+"Could not delete: "+username+'\nStatus Code:'+str(response.status_code)+bcolors.ENDC)
				exit()

		response = requests.post(url='https://'+server+'/api/3/users',
			headers=headers,json=create_user_json,verify=False)

		if response.status_code != 201:
			logger.error(bcolors.FAIL+"Could not create user: "+username+'\nStatus Code:'+str(response.status_code)+bcolors.ENDC)
			exit()

		else:
			logger.info(bcolors.MSG+"User: "+username+' created'+bcolors.ENDC)

	except requests.ConnectionError:
		logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
		exit()
	except requests.ConnectTimeout:
		logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
		exit()

def fsr_send_alert(server,headers,body,single_step=False,tenant=None):

	try:
		if tenant:
			body['data'][0]['tenant'] = tenant

		if not single_step:
			sleep=body['data'][0]['sleep']
			if sleep:
				if sleep >= 0:
					logger.info(bcolors.MSG+"Sleeping for {} seconds".format(sleep)+bcolors.ENDC)
					time.sleep(sleep)
				else:
					input(bcolors.MSG+"Type any key to continue"+bcolors.ENDC)

		response = requests.post(url='https://'+server+'/api/3/insert/alerts',
			headers=headers,json=body,verify=False)

		if response.status_code != 200:
			logger.error(bcolors.FAIL+'Error Updating :'+response.text+bcolors.ENDC)
			exit()
		else:
			logger.info(bcolors.OKGREEN+'Alert Sent'+bcolors.ENDC)

	except requests.ConnectionError:
		logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
		exit()
	except requests.ConnectTimeout:
		logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
		exit()
	else:
		return response.json()

def cook_alert(server,headers,scenario_json,playbooks_definition):
	try:

		template_file = json.dumps(scenario_json)
		playbooks_definition=json.dumps(playbooks_definition)

		tag_list = re.findall('\{\{(.*?)\}\}',template_file)
		for tag in tag_list:
			logger.debug('{0}Processing tag: {1} {2}'.format(bcolors.OKGREEN,tag,bcolors.ENDC))
			if ',' in tag:
				function = tag.split(',')[0]
				params = tag.split(',')[1:]
				logger.debug('tag {0} replaced with {1}'.format(tag,str(function_dictionary[function](params))))
				template_file=template_file.replace('{{'+tag+'}}',str(function_dictionary[function](params)))
			else:
				logger.debug('tag {0} replaced with {1}'.format(tag,str(function_dictionary[tag]())))
				template_file=template_file.replace('{{'+tag+'}}',str(function_dictionary[tag]()))
		# Check sourcedata format, fix it if needed
		fortisoar_sourcedata=lookup_source_data(server,headers)
		try:
			template_sourcedata = re.search('\"(source[dD]ata)\"', template_file).group(1)
		except AttributeError:
			logger.error(bcolors.FAIL+"Cannot determine sourcedata format from template"+bcolors.ENDC)
			exit()

		if template_sourcedata != fortisoar_sourcedata:
			template_file=template_file.replace(template_sourcedata,fortisoar_sourcedata)
			playbooks_definition=playbooks_definition.replace(template_sourcedata,fortisoar_sourcedata)



	except Exception as e:
		logger.error("{0}Couldn't process template,playbooks definition files: {1}{2}".format(bcolors.FAIL,e,bcolors.ENDC))
		sys.exit()

	return json.loads(template_file),json.loads(playbooks_definition)
