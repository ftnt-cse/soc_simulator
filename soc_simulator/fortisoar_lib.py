#!/bin/python3
# Function library to handle FortiSOAR communication
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

#import pdb;pdb.set_trace()

from .artifact_factory import *


class FortiSoarAC(object):
    def __init__(self, config):
        self.maximum_file_size = 200000000
        self.error_msg = {'403': 'Authentication Error, Check your API key',
                          '404': 'The requested URL was not found on this server'}
        self.url = config.get('server').strip('/')
        if not self.url.startswith('https://') and not self.url.startswith('http://'):
            self.url = 'https://' + self.url
        # TODO : implement hmac authentication
        self.username = config['username']
        self.username = config['password']
        self.verify_ssl = config['verify_ssl']
        self.headers = self.fsr_login(self.url, self.username, self.password)

    def fsr_login(server,username,password):
        body = {
            'credentials': {
                'loginid': username,
                'password': password
            }
        }
        try:
            response = requests.post(
                url=server+'/auth/authenticate', json=body,
                verify=False
            )
            logger.debug('\nreq data:\n{0}\n'.format(dump.dump_all(response).decode('utf-8')))
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

    def make_rest_call(self, url, endpoint, headers=None, data=None, method='GET'):
        try:
            url = url + endpoint
            response = requests.request(method, url, headers=headers, data=data, verify=self.verify_ssl)

            if response.ok:
                if 'json' in response.headers.get('Content-Type'):
                    return {'response': json.loads(response.content.decode('utf-8')),
                            'status_code': response.status_code}
                else:
                    return {'response': response.content.decode('utf-8'), 'status_code': response.status_code}

            elif response.status_code == 403:
                raise ConnectorError('Error code: {0}, message: {1}'.format(response.status_code,
                                                                            self.error_msg[str(response.status_code)]))
            else:
                raise ConnectionError('Error code: {0}, message: {1}'.format(response.status_code,
                                                                             self.error_msg.get(
                                                                                 str(response.status_code),
                                                                                 response.text)))
        except Exception as e:
            logger.exception('{0}'.format(e))
            raise ConnectorError('{0}'.format(e))


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
        headers = {"Content-Type":"application/json","Authorization": "Bearer " + token}
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

        if response.status_code != 201:
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


def check_connectors_prerequisites(server,headers,connectors_dependencies): 
    '''Checks whether the initial config is done to run the playbooks properly'''
    try:
        response = requests.get(url='https://'+server+'/api/integration/connectors/?configured=true&ordering=label&page_size=100', #TODO: use : search=Connector_name
            headers=headers,verify=False)
       
        logger.debug('total Items: {}'.format(response.json()['totalItems']))
        if response.status_code != 200 or len(response.json()["data"]) < 1:
            logger.error('{0}Error Getting Connectors List: {1}{2}'.format(bcolors.FAIL,response.text,bcolors.ENDC))
            exit()

        for required_connector in connectors_dependencies:
            if not any(connector['name'] == required_connector for connector in response.json()["data"]):
                logger.error('{0}Connector: {1} is not Installed, Install it and try again{2}'.
                    format(bcolors.FAIL,required_connector,bcolors.ENDC))
                exit()
    
        for required_connector in connectors_dependencies:
            for connector in response.json()["data"]:
                if required_connector == connector["name"]:
                    if connector["config_count"] < 1:
                        logger.error(bcolors.FAIL+'Connector: '+required_connector+' is not Configured, Configure it and try again'+bcolors.ENDC)
                        exit()                      
                    # get connector default config:
                    config_response = requests.post(url='https://'+server+'/api/integration/connectors/'+
                        connector["name"]+'/'+
                        connector["version"]+
                        '/?format=json',
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
    exported_tags_json = {"__unique":["uuid"],"__replace":False,"__data":[]}
    #{"uuid":"placeholder"},{"uuid":"FortiTAG"}
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
            if playbooks_definition['exported_tags'] and len(playbooks_definition['exported_tags']) > 0:
                for tag in playbooks_definition['exported_tags']:
                    exported_tags_json['__data'].append({"uuid":tag})
                response = requests.post(url='https://'+server+'/api/3/bulkupsert/tags',
                headers=headers,json=exported_tags_json,verify=False)                
                if response.status_code != 201:
                    logger.error(bcolors.FAIL+"Could not exported tags: "+response.text+'\nStatus Code:'+str(response.status_code)+bcolors.ENDC)
                    exit()
                else:
                     logger.info(bcolors.MSG+"Exported Tags uploaded: "+", ".join(playbooks_definition['exported_tags'])+bcolors.ENDC)
            logger.info(bcolors.MSG+"Uploading Scenario Playbook Collection to FortiSOAR"+bcolors.ENDC)
            response = requests.post(url='https://'+server+'/api/3/bulkupsert/workflow_collections',
            headers=headers,json=upload_playbook_json,verify=False)
            if response.status_code != 201:
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

            if response.status_code != 201:
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

        body['data'][0]['sourcedata'] = json.dumps(body['data'][0]['sourcedata'])
        response = requests.post(url='https://'+server+'/api/3/insert/alerts',
            headers=headers,json=body,verify=False)

        if response.status_code != 201:
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

def _fsr_get_picklist(server,headers,picklist_name):
    '''Get Picklists'''
    try:
        response = requests.get(url='https://'+server+'/api/3/picklist_names?$export=false&$orderby=name&$limit=100',
            headers=headers,verify=False)

        if response.ok:
            logger.debug('{0}Get Picklists: Success ({1}){2}'.format(bcolors.OKGREEN,response.status_code,bcolors.ENDC))
        else:
            logger.error(bcolors.FAIL+'Error Fetching Picklists:'+response.text+bcolors.ENDC)
            sys.exit()

    except requests.ConnectionError:
        logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
        exit()
    except requests.ConnectTimeout:
        logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
        exit()
    else:
        for item in response.json()['hydra:member']:
            if item['name'] == picklist_name:
                picklist_item = item    
    try:
        response = requests.get(url='https://'+server+picklist_item['@id']+'?$relationships=true',
            headers=headers,verify=False)

        if response.ok:
            logger.debug('{0} Get Picklist Data ({1}): Success{2}'.format(bcolors.OKGREEN,picklist_name,bcolors.ENDC))
            return response.json()
        else:
            logger.error(bcolors.FAIL+'Error Fetching Picklists:'+response.text+bcolors.ENDC)
            sys.exit()

    except requests.ConnectionError:
        logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
        exit()
    except requests.ConnectTimeout:
        logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
        exit()              

def _fsr_update_picklist(server,headers,picklist,new_entries):
    ''' Update picklist with specific item '''

    # check if entry exits
    for entry in picklist['picklists']:
        if entry['itemValue'] in new_entries:
            logger.debug('Picklist item: {0} already exists'.format(entry['itemValue']))
            new_entries.remove(entry['itemValue'])

    if len(new_entries) == 0:
        logger.debug('No New entry to create')
        return True

    for entry in new_entries:
        picklist['picklists'].append({"@type": "Picklist","color": None,"icon": None,"id": 300,"itemValue": entry,"listName": picklist["@id"]})

    picklist_uuid = picklist["@id"].split('/')[-1]
    try:
      response = requests.put(url='https://'+server+'/api/3/picklist_names/'+picklist_uuid+'?$relationships=true',
          headers=headers,json=picklist,verify=False)

      if response.ok:
          logger.info('{0}Items ({1}) updated successfully on Picklist: {2}{3}'.format(bcolors.OKGREEN,','.join(new_entries),picklist['name'],bcolors.ENDC)) 
      else:
          logger.error(bcolors.FAIL+'Error Updating Picklist:'+response.text+bcolors.ENDC)
          sys.exit()
            

    except requests.ConnectionError:
      logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
      exit()
    except requests.ConnectTimeout:
      logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
      exit()
    else:
      return response.json()      

def fsr_update_picklist(server,headers,picklist_name,new_entries):

    picklist = _fsr_get_picklist(server,headers,picklist_name)
    return _fsr_update_picklist(server,headers,picklist,new_entries)


def fsr_upload_file(server,headers,file):
    '''Upload File to FortiSOAR as multipart'''
    try:
        files = {'file': open(file, 'rb')}

    except IOError:
        logger.error("{0}Couldn't open file: {1}, make sure the file exists and its JSON syntax is correct{2}".format(bcolors.FAIL,file,bcolors.ENDC))
        sys.exit()

    try:
        response = requests.post(url='https://'+server+'/api/3/files',
            headers=headers,files=files,verify=False)

        if response.status_code != 201:
            logger.error(bcolors.FAIL+'Error Uploading File :'+response.text+bcolors.ENDC)
            exit()
        else:
            logger.info(bcolors.OKGREEN+'File Uploaded'+bcolors.ENDC)

    except requests.ConnectionError:
        logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
        exit()
    except requests.ConnectTimeout:
        logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
        exit()
    else:
        return response.json()  


def fsr_create_import_jobs(server,headers,file_iri):
    ''' POST uploaded file uuid and creates an import job'''
    import_jobs_json = {
                          "status": "In Progress",
                          "file":file_iri
                       }
    try:
        response = requests.post(url='https://'+server+'/api/3/import_jobs',
            headers=headers,json=import_jobs_json,verify=False)
        logger.debug('Status code: {0}'.format(response.status_code))
        if response.ok:
            logger.info('{0}Job Imported:\n{1}\n{2}'.format(bcolors.OKGREEN,json.dumps(response.json(), indent=4, sort_keys=True),bcolors.ENDC))
        else:
            logger.error(bcolors.FAIL+'Error importing Job:'+response.text+bcolors.ENDC)
            sys.exit()


    except requests.ConnectionError:
        logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
        exit()
    except requests.ConnectTimeout:
        logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
        exit()
    else:
        return response.json()      

def fsr_generate_import_options(server,headers,import_job_uuid):
    ''' Get import job options'''

    try:
        response = requests.get(url='https://'+server+'/api/import/'+import_job_uuid,
            headers=headers,verify=False)

        if response.ok:
            logger.info('{0}Job Imported Options Created\n{1}\n{2}'.format(bcolors.OKGREEN,json.dumps(response.json(), indent=4, sort_keys=True),bcolors.ENDC)) 
        else:
            logger.error(bcolors.FAIL+'Error Creating importing Job Options:'+response.text+bcolors.ENDC)
            sys.exit()

    except requests.ConnectionError:
        logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
        exit()
    except requests.ConnectTimeout:
        logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
        exit()
    else:
        return response.json()


def fsr_trigger_import_job(server,headers,import_job_uuid):
    ''' Trigger import job '''

    try:
        response = requests.put(url='https://'+server+'/api/import/'+import_job_uuid,
            headers=headers,verify=False)

        if response.ok:
            logger.info('{0}Triggered Import Job:\n{1}\n{2}'.format(bcolors.OKGREEN,json.dumps(response.json(), indent=4, sort_keys=True),bcolors.ENDC)) 
        else:
            logger.error(bcolors.FAIL+'Error Creating importing Job Options:'+response.text+bcolors.ENDC)
            sys.exit()
            

    except requests.ConnectionError:
        logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
        exit()
    except requests.ConnectTimeout:
        logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
        exit()
    else:
        return response.json()

def fsr_get_import_job_status(server,headers,import_job_uuid):
    ''' Get import job status'''

    try:
        response = requests.get(url='https://'+server+'/api/3/import_jobs/'+import_job_uuid+'?__selectFields=errorMessage,status,progressPercent,file,currentlyImporting,options',
            headers=headers,verify=False)

        if response.ok:
            logger.info('{0}Import Job Progress:\n{1}\n{2}'.format(bcolors.OKGREEN,json.dumps(response.json(), indent=4, sort_keys=True),bcolors.ENDC))
        else:
            logger.error(bcolors.FAIL+'Error Checking Job Import Progress:'+response.text+bcolors.ENDC)
            sys.exit()

    except requests.ConnectionError:
        logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
        exit()
    except requests.ConnectTimeout:
        logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
        exit()
    else:
        return response.json()

# TODO : complete import process
def fsr_import_configuration(server,headers,file): 
    ''' Import config file to FortiSOAR'''
    file_upload = fsr_upload_file(server,headers,file)
    import_job = fsr_create_import_jobs(server,headers,file_upload["@id"])
    import_job_uuid = import_job["@id"].split("/")[-1]
    # logger.debug(fsr_generate_import_options(server,headers,import_job_uuid))
    # logger.debug(fsr_trigger_import_job(server,headers,import_job_uuid))
    # time.sleep(10)
    # fsr_get_import_job_status(server,headers,import_job_uuid)
