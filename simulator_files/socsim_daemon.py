#!/usr/bin/env python3
# Function library to handle FortiSOAR communication
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

from artifact_factory import *
#import pdb;pdb.set_trace()
from scapy.all import *


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

def send_event(source_ip,destination_ip,payload):
	try:	
		spoofed_packet = IP(src=source_ip, dst=destination_ip) / UDP(sport=random.randint(30000, 35000), dport=514) / payload
		send(spoofed_packet)
	except:
		print ('Sending Event Failed', sys.exc_info()[0])

def read_json(data):
		try:
			json_data=json.loads(data)

		except ValueError:
			print(bcolors.FAIL+"Bad JSON event syntax: "+data+bcolors.ENDC)
			return None
		else:
			return json_data


try:
	os.mkfifo(SOCSIM_FIFO)
	os.chmod(SOCSIM_FIFO,0o666)
except OSError as oe:
	if oe.errno != errno.EEXIST:
		print('error',oe)
		raise

def main():
	while True:
		with open(SOCSIM_FIFO) as fifo:
			while True:
				data = fifo.read()
				if len(data) == 0:
					#print("Writer closed")
					break
				print(data)	
				try:	
					json_data = read_json(data)
					if json_data:
						source_ip=json_data['source_ip']
						destination_ip=json_data['destination_ip']
						payload=json_data['payload']
						if not is_valid_ip(source_ip) or not is_valid_ip(destination_ip):
							print(source_ip,destination_ip,' not a valid IP address')
							continue
						send_event(source_ip,destination_ip,payload)

				except ValueError:
					print(bcolors.FAIL+"Bad JSON event syntax: "+json_data+bcolors.ENDC)
					exit()							

try:
	main()
except KeyboardInterrupt:
	print("SocSim Daemon Stopping...")
	os.remove(SOCSIM_FIFO)	
	exit()
except:
	print('SocSim Daemon Error')
	os.remove(SOCSIM_FIFO)
	exit()

