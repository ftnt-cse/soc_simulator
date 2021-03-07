#!/bin/python3
# function library to generate:
#	-Random artifacts
#	-network related artifact (usernames, network and system devices attributes)
# FortiSOAR CSE Team
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

import logging
import requests
import argparse
import textwrap
import json
import random
import time
import os
import csv
import re
import errno
import stat
import time
import sys
import datetime
import base64
import hashlib
import paramiko
import zipfile
from shutil import copyfile
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


log_formatter = '%(asctime)s [%(levelname)s]: %(message)s'
logging.basicConfig(format=log_formatter, datefmt='%H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger(__name__)


templates_path 			= './'
config_file				= './config.json'
tmp_config_file			= '/tmp/soc_simulator_config.json'
malware_hashes_file		= './threat_intelligence/malware_hashes.txt'
malicious_domains_file	= './threat_intelligence/malicious_domains.txt'
malicious_ip_file		= './threat_intelligence/malicious_ips.txt'
malicious_urls_file		= './threat_intelligence/malicious_urls.txt'
spam_domains_file		= './threat_intelligence/spam_domains.txt'
SOCSIM_FIFO				= '/tmp/socsim.pipe'
MALWARE_FILE 			= '/tmp/malware.pdf'
MALICIOUS_FILE_PASSWD	= 'pass'
MALICIOUS_FILE_PATH		= './threat_intelligence/malware.bin/attachment.pdf.zip'


class bcolors:
	''' Color code cli output '''
	OKGREEN = '\033[92m'
	FAIL = '\033[91m'
	MSG = '\033[96m'
	INST = '\033[95m'
	ENDC = '\033[0m'

def _read_json_file(file):
	try:
		logger.debug('Reading file: {0}'.format(file))
		with open(file, 'r') as file:
			file_content = file.read()
		file.close()
		file_content = json.loads(file_content)

	except IOError:
		logger.error(bcolors.FAIL+"Couldn't open config file: {0}".format(file)+bcolors.ENDC)
		sys.exit()
	except ValueError:
		logger.error(bcolors.FAIL+"Bad JSON syntax"+bcolors.ENDC)
		sys.exit()
	else:
		return file_content

def get_malicious_file(params = None):
	''' Pads a malicious pdf and returns it in base64 encoding and write a binary copy of it under .tmp/'''
	try:
		zip_file = zipfile.ZipFile(MALICIOUS_FILE_PATH, 'r')
		extracted_file = zip_file.namelist()
		zip_file.extractall(path=os.path.dirname(MALICIOUS_FILE_PATH), pwd = bytes(MALICIOUS_FILE_PASSWD, 'utf-8'))
		zip_file.close()
		extracted_file = os.path.join(os.path.dirname(MALICIOUS_FILE_PATH), extracted_file[0])	# only one file expected
		with open(extracted_file,'rb') as f:
			file_content = f.read()
		
		malicious_file = file_content + bytes([random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)])
		with open(MALWARE_FILE, 'wb') as f:
			f.write(malicious_file)

	except IOError as e:
		logger.error("{0}Couldn't open malware file: {1}{2}{3}".format(bcolors.FAIL,MALICIOUS_FILE_PATH,e,bcolors.ENDC))
		sys.exit()
	except Exception as e:
		logger.error("{0}Couldn't process malware files: {1}{2}".format(bcolors.FAIL,e,bcolors.ENDC))
		sys.exit()		
	else:
		return base64.b64encode(malicious_file).decode("utf-8")


def get_malicious_file_md5(params = None):
	'''	Computes the previously created .tmp/malware file md5 if it exists	'''
	if os.path.isfile(MALWARE_FILE):
		return hashlib.md5(open(MALWARE_FILE,'rb').read()).hexdigest()

def get_malicious_file_sha1(params = None):
	'''	Computes the previously created .tmp/malware file sha1 if it exists	'''
	if os.path.isfile(MALWARE_FILE):
		return hashlib.sha1(open(MALWARE_FILE,'rb').read()).hexdigest()

def get_malicious_file_sha256(params = None):
	'''	Computes the previously created .tmp/malware file sha256 if it exists	'''
	if os.path.isfile(MALWARE_FILE):
		return hashlib.sha256(open(MALWARE_FILE,'rb').read()).hexdigest()

def get_formatted_current_time(params = None):
	return datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z")

def get_username():
	usernames=["Morgoth","Lúthien","Glorfindel","Beren","Túrin_turambar","Eärendil","Ancalagon","Manwë","Thingol","Húrin","Melian","Glaurung","Mandos","Maglor","Elendil","Círdan","Finarfin","Ulmo","Morwen","Beleg","Niënor_níniel","Finduilas","Orodreth","Carcharoth","Eöl","Ossë","Yavanna","Anárion","Lalaith","Emeldir","Dorlas","Aerin","Rían"]
	return random.choices(usernames)[0]

def get_fgt_mgmt_ip(params = None):
	'''	Takes config file argument and returns FortiGate Management IP, params = config_file JSON object'''	
	config = _read_json_file(tmp_config_file)
	if 'TR_FG_MGMT_IP' in config:
		return config['TR_FG_MGMT_IP']

def get_fgt_dev_name(params = None):
	'''	Takes config file argument and returns FortiGate Device Name, params = config_file JSON object'''		
	config = _read_json_file(tmp_config_file)
	if 'TR_FG_DEV_NAME' in config:
		return config['TR_FG_DEV_NAME']	

def get_fgt_sn(params = None):
	'''	Takes config file argument and returns FortiGate Serial Number, params = config_file JSON object'''		
	config = _read_json_file(tmp_config_file)
	if 'TR_FGT_SN' in config:
		return config['TR_FGT_SN']


def get_asset_ip(params = None):
	if params and isinstance(params, list) and len(params) == 2:
		return "10.200.3."+str(random.randint(int(params[0]), int(params[1])))
	else:
		return "10.200.3."+str(random.randint(2, 24))

def get_time_now(params = None):
	return int(time.time())

def get_time_past(params = None):
	return int(time.time()) - random.randint(86400, 172800)

def get_time_minus_one(params = None):
	return int(time.time()) - random.randint(3300, 3900)

def get_time_minus_two(params = None):
	return int(time.time()) - random.randint(7100, 7700)

def get_time_minus_tree(params = None):
	return int(time.time()) - random.randint(10600, 11200)

def get_time_minus_four(params = None):
	return int(time.time()) - random.randint(14400, 14800)

def get_time_minus_five(params = None):
	return int(time.time()) - random.randint(18000, 18600)

def get_time_minus_six(params = None):
	return int(time.time()) - random.randint(21400, 22000)

def get_date_now_only(params = None):
	return time.strftime('%Y-%m-%d', time.localtime(time.time()))

def get_time_now_only(params = None):
	return time.strftime('%H:%M:%S', time.localtime(time.time()))

def get_time_x_min_ago(params = None):
	if params and isinstance(params, list) and len(params) == 1:
		return int(time.time()) - random.randint(21600, 21900)
	else:
		return int(time.time()) - int(params[0])


def get_timezone(params = None):
	p = open("config.json", 'r')
	tz_config = p.read()
	tz_config = json.loads(tz_config)
	p.close()
	tz_config = tz_config['TimeZone']
	return tz_config

def get_random_integer(params = None):
	if params and isinstance(params, list) and len(params) == 2:
		return random.randint(int(params[0]), int(params[1]))
	else:
		return random.randint(1, 999999)

def get_my_public_ip(params = None):
	try:
		response = requests.get(url='https://api.ipify.org/?format=txt')
		if response.status_code != 200:
			logger.error(bcolors.FAIL+'Public IP lookup Failed'+bcolors.ENDC)
			exit()
		public_ip=str(response.content, 'utf-8')
		return '.'.join(public_ip.split('.')[:-1])+'.'+str(random.randint(2, 253))

	except requests.ConnectionError:
		logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
		exit()
	except requests.ConnectTimeout:
		logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
		exit()

def get_malware_hash(params = None):

	if not os.path.exists(os.path.dirname(malware_hashes_file)):
		os.makedirs(os.path.dirname(malware_hashes_file))

	if not os.path.isfile(malware_hashes_file):
		try:
			response = requests.get(url='https://cybercrime-tracker.net/ccamlist.php')
			if response.status_code != 200:
				logger.error(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				exit()
			with open(malware_hashes_file, 'wb') as f:
				f.write(response.content)

		except requests.ConnectionError:
			logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()

	lines = open(malware_hashes_file).read().splitlines()

	return(random.choice(lines))


def get_malicious_url(params = None):
	''' returns a malicious URL and download a malicious URL list if it doesn't exist'''
	if not os.path.exists(os.path.dirname(malicious_urls_file)):
		os.makedirs(os.path.dirname(malicious_urls_file))

	if not os.path.isfile(malicious_urls_file):
		try:
			response = requests.get(url='https://openphish.com/feed.txt')
			if response.status_code != 200:
				logger.error(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				exit()
			with open(malicious_urls_file, 'wb') as f:
				f.write(response.content)

		except requests.ConnectionError:
			logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()

	lines = open(malicious_urls_file).read().splitlines()

	return(random.choice(lines))


def get_malicious_ip(params = None):
	lines=''
	if not os.path.exists(os.path.dirname(malicious_ip_file)):
		os.makedirs(os.path.dirname(malicious_ip_file))

	if not os.path.isfile(malicious_ip_file):
		try:
			response = requests.get(url='https://malsilo.gitlab.io/feeds/dumps/ip_list.txt')
			if response.status_code != 200:
				logger.error(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				exit()
			decoded_content = response.content.decode('utf-8')
			cr = csv.reader(decoded_content.splitlines(), delimiter=',')
			for skip in range(16):
				next(cr)
			bad_ips_list = list(cr)
			for row in bad_ips_list:
				lines+=row[2].split(':')[0]+'\n'
			with open(malicious_ip_file, 'w+') as f:
				f.write(lines)

		except requests.ConnectionError:
			logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()


	lines = open(malicious_ip_file).read().splitlines()

	return(random.choice(lines))


def get_malicious_domains(params = None):
	lines=''
	if not os.path.exists(os.path.dirname(malicious_domains_file)):
		os.makedirs(os.path.dirname(malicious_domains_file))

	if not os.path.isfile(malicious_domains_file):
		try:
			response = requests.get(url='https://osint.bambenekconsulting.com/feeds/c2-dommasterlist-high.txt')
			if response.status_code != 200:
				logger.error(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				exit()
			decoded_content = response.content.decode('utf-8')
			cr = csv.reader(decoded_content.splitlines(), delimiter=',')
			for skip in range(16):
				next(cr)
			bad_ips_list = list(cr)
			for row in bad_ips_list:
				lines+=row[0]+'\n'
			with open(malicious_domains_file, 'w+') as f:
				f.write(lines)

		except requests.ConnectionError:
			logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()


	lines = open(malicious_domains_file).read().splitlines()

	return(random.choice(lines))

def get_spam_domains(params = None):
	lines=''
	if not os.path.exists(os.path.dirname(spam_domains_file)):
		os.makedirs(os.path.dirname(malicious_urls_file))

	if not os.path.isfile(spam_domains_file):
		try:
			response = requests.get(url='https://feeds.alphasoc.net/ryuk.txt')
			if response.status_code != 200:
				logger.error(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				sys.exit()
			decoded_content = response.content.decode('utf-8')
			spam_domains = re.findall(r'[0-9A-Za-z,-.]+\.[a-z]+',(decoded_content))
			if len(spam_domains) > 2:
				with open(spam_domains_file,'wt', encoding='utf-8') as f:
					f.write('\n'.join(spam_domains))
			else:
				logger.error(bcolors.FAIL+'Could not download/save spam domains'+bcolors.ENDC)
				sys.exit()	
		except requests.ConnectionError:
			logger.error(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			logger.error(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()

	lines = open(spam_domains_file).read().splitlines()

	return(random.choice(lines))


function_dictionary={
"TR_MALICIOUS_FILE":get_malicious_file,
"TR_MALICIOUS_FILE_MD5":get_malicious_file_md5,
"TR_MALICIOUS_FILE_SHA1":get_malicious_file_sha1,
"TR_MALICIOUS_FILE_SHA256":get_malicious_file_sha256,
"TR_FORMATTED_CURRENT_TIME":get_formatted_current_time,
"TR_FG_MGMT_IP":get_fgt_mgmt_ip,
"TR_FG_DEV_NAME":get_fgt_dev_name,
"TR_FGT_SN":get_fgt_sn,
"TR_ASSET_IP":get_asset_ip,
"TR_MALICIOUS_IP":get_malicious_ip,
"TR_NOW":get_time_now,
"TR_DATE_NOW_ONLY":get_date_now_only,
"TR_TIME_NOW_ONLY":get_time_now_only,
"TR_PAST":get_time_past,
"TR_TIMEZONE":get_timezone,
"TR_RANDOM_INTEGER":get_random_integer,
"TR_MALICIOUS_DOMAIN":get_malicious_domains,
"TR_SPAM_DOMAIN":get_spam_domains,
"TR_MALICIOUS_URL":get_malicious_url,
"TR_MALICIOUS_HASH":get_malware_hash,
"TR_PUBLIC_IP":get_my_public_ip,
"TR_USERNAME":get_username,
"TR_T-1":get_time_minus_one,
"TR_T-2":get_time_minus_two,
"TR_T-3":get_time_minus_tree,
"TR_T-4":get_time_minus_four,
"TR_T-5":get_time_minus_five,
"TR_T-6":get_time_minus_six,
"TR_X_MIN_AGO":get_time_x_min_ago
}


