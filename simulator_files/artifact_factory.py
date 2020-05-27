#!/bin/python3
# function library to generate:
#	-Random artifacts
#	-network related artifact (usernames, network and system devices attributes)
# FortiSOAR CSE Team
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

import requests, argparse, textwrap, json, random, time, os, csv, re, errno, stat, time, sys, getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

templates_path 		= './'
malware_hashes 		= './threat_intelligence/malware_hashes.txt'
malicious_domains	= './threat_intelligence/malicious_domains.txt'
malicious_ips		= './threat_intelligence/malicious_ips.txt'
malicious_urls		= './threat_intelligence/malicious_urls.txt'
SOCSIM_FIFO			= '/tmp/socsim.pipe'


class bcolors:
	OKGREEN = '\033[92m'
	FAIL = '\033[91m'
	MSG = '\033[96m'
	INST = '\033[95m'
	ENDC = '\033[0m'


def get_username():
	usernames=["Morgoth","Lúthien","Glorfindel","Beren","Túrin_turambar","Eärendil","Ancalagon","Manwë","Thingol","Húrin","Melian","Glaurung","Mandos","Maglor","Elendil","Círdan","Finarfin","Ulmo","Morwen","Beleg","Niënor_níniel","Finduilas","Orodreth","Carcharoth","Eöl","Ossë","Yavanna","Anárion","Lalaith","Emeldir","Dorlas","Aerin","Rían"]
	return random.choices(usernames)[0]

def get_fg_mgmt_ip():
	return "10.200.3.1"

def get_fg_dev_name():
	return "FortiGate-Edge"

def get_asset_ip():
	return "10.200.3."+str(random.randint(2, 24))

def get_time_now():
	return int(time.time())

def get_time_past():
	return int(time.time()) - random.randint(86400, 172800)

def get_time_minus_one():
	return int(time.time()) - random.randint(3400, 3800)

def get_time_minus_two():
	return int(time.time()) - random.randint(7200, 86400)

def get_time_minus_tree():
	return int(time.time()) - random.randint(10800, 11000)

def get_time_minus_four():
	return int(time.time()) - random.randint(14400, 14600)

def get_time_minus_five():
	return int(time.time()) - random.randint(18000, 18300)

def get_time_minus_six():
	return int(time.time()) - random.randint(21600, 21900)


def get_random_integer(start=55555,end=99999):
	return random.randint(start, end)

def get_my_public_ip():
	try:
		response = requests.get(url='https://api.ipify.org/?format=txt')
		if response.status_code != 200:
			print(bcolors.FAIL+'Public IP lookup Failed'+bcolors.ENDC)
			exit()
		public_ip=str(response.content, 'utf-8')
		return '.'.join(public_ip.split('.')[:-1])+'.'+str(random.randint(2, 253))

	except requests.ConnectionError:
		print(bcolors.FAIL+"Connection error"+bcolors.ENDC)
		exit()
	except requests.ConnectTimeout:
		print(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
		exit()

def get_malware_hash(malware_hashes_file=malware_hashes):

	if not os.path.exists(os.path.dirname(malware_hashes_file)):
		os.makedirs(os.path.dirname(malware_hashes_file))

	if not os.path.isfile(malware_hashes_file):
		try:
			response = requests.get(url='https://cybercrime-tracker.net/ccamlist.php')
			if response.status_code != 200:
				print(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				exit()
			with open(malware_hashes_file, 'wb') as f:
				f.write(response.content)

		except requests.ConnectionError:
			print(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			print(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()

	lines = open(malware_hashes_file).read().splitlines()

	return(random.choice(lines))


def get_malicious_url(malicious_urls_file=malicious_urls):

	if not os.path.exists(os.path.dirname(malicious_urls_file)):
		os.makedirs(os.path.dirname(malicious_urls_file))

	if not os.path.isfile(malicious_urls_file):
		try:
			response = requests.get(url='https://openphish.com/feed.txt')
			if response.status_code != 200:
				print(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
				exit()
			with open(malicious_urls_file, 'wb') as f:
				f.write(response.content)

		except requests.ConnectionError:
			print(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			print(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()

	lines = open(malicious_urls_file).read().splitlines()

	return(random.choice(lines))


def get_malicious_ip(malicious_ip_file=malicious_ips):
	lines=''
	if not os.path.exists(os.path.dirname(malicious_ip_file)):
		os.makedirs(os.path.dirname(malicious_ip_file))

	if not os.path.isfile(malicious_ip_file):
		try:
			response = requests.get(url='https://malsilo.gitlab.io/feeds/dumps/ip_list.txt')
			if response.status_code != 200:
				print(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
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
			print(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			print(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()


	lines = open(malicious_ip_file).read().splitlines()

	return(random.choice(lines))


def get_malicious_domains(malicious_domains_file=malicious_domains):
	lines=''
	if not os.path.exists(os.path.dirname(malicious_domains_file)):
		os.makedirs(os.path.dirname(malicious_domains_file))

	if not os.path.isfile(malicious_domains_file):
		try:
			response = requests.get(url='https://osint.bambenekconsulting.com/feeds/c2-dommasterlist-high.txt')
			if response.status_code != 200:
				print(bcolors.FAIL+'TI Download Failed'+bcolors.ENDC)
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
			print(bcolors.FAIL+"Connection error"+bcolors.ENDC)
			exit()
		except requests.ConnectTimeout:
			print(bcolors.FAIL+"Connection timeout"+bcolors.ENDC)
			exit()


	lines = open(malicious_domains_file).read().splitlines()

	return(random.choice(lines))

function_dictionary={
"TR_FG_MGMT_IP":get_fg_mgmt_ip,
"TR_FG_DEV_NAME":get_fg_dev_name,
"TR_ASSET_IP":get_asset_ip,
"TR_MALICIOUS_IP":get_malicious_ip,
"TR_NOW":get_time_now,
"TR_PAST":get_time_past,
"TR_RANDOM_INTEGER":get_random_integer,
"TR_MALICIOUS_DOMAIN":get_malicious_domains,
"TR_MALICIOUS_URL":get_malicious_url,
"TR_MALICIOUS_HASH":get_malware_hash,
"TR_PUBLIC_IP":get_my_public_ip,
"TR_USERNAME":get_username,
"TR_T-1":get_time_minus_one,
"TR_T-2":get_time_minus_two,
"TR_T-3":get_time_minus_tree,
"TR_T-4":get_time_minus_four,
"TR_T-5":get_time_minus_five,
"TR_T-6":get_time_minus_six
}


