# Use Case 1: 
- Objective: Demonstrate Automated Alert Triage (false positive, true positive detection)
- Chronology: 
	- Alert1: 
		- IPS detects a remote exploit attack against Asset A exploiting vulnerability CVE-2020-1350
		- FortiSOAR checks the list of Asset A vulnerabilities where CVE-2020-1350 is included.
		- FortiSOAR then blocks the source IP on FortiGate and escalates the alert to Incident as **True Positive** creating an analyst remediation task for the risk of successful compromise is very high due to the matching CVE

	- Alert2:
		- IPS detects a remote exploit attack against Asset A exploiting vulnerability CVE-2008-XXXX
		- FortiSOAR checks the list of Asset A vulnerabilities where CVE-2008-XXXX is not included
		- FortiSOAR then Closes the alert as **False Positive** for the risk of a successful compromize is null

	- Alert3: 
		- SIEM detects a a successful VPN connection from another country
		- FortiSOAR get the source IP reputation as an additional data to take an action upon, the IP is not malicious
		- FortiSOAR fetches the user details from Active Directory and extract the user's location
		- FortiSOAR resolves the source IP Country and compares it with the country extracted from Active directory data
		- the two countries are the same, the alert is closed as **False Positive**  for the user belongs to the same country the VPN connection came from


	- Alert4:
		- SIEM detects a a successful VPN connection from another country
		- FortiSOAR get the source IP reputation as an additional data to take an action upon, the IP is **malicious**
		- FortiSOAR fetches the user details from Active Directory and extract the user's location
		- FortiSOAR resolves the source IP Country and compares it with the country extracted from Active directory data
		- the two countries are the different and the source IP is malicious, the alert is escalated as a **True Positive** of credentials theft, the analyst is presented with 2 automation response playbooks: Disable user name from Active Directory and Block the source IP on NGFW
		