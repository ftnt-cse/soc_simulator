#!/usr/bin/env python3
# Function library to handle FortiSOAR communication
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND

from simulator_files.artifact_factory import *
from simulator_files.main_lib import *

#import pdb;pdb.set_trace()

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
				try:	
					json_data = read_json(data)
					if json_data:
						source_ip=json_data['source_ip']
						destination_ip=json_data['destination_ip']
						payload=json_data['payload']
						if not is_valid_ip(source_ip) or not is_valid_ip(destination_ip):
							print(bcolors.FAIL+source_ip,destination_ip,' not a valid IP address'+bcolors.ENDC)
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

