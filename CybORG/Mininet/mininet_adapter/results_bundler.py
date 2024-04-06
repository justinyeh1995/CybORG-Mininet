import re
import traceback 
from pprint import pprint
from typing import List, Dict

from CybORG.Shared import Observation

def parse_nmap_network_scan(nmap_output, target, mapper) -> List:
    res = {'success': True}
    subnet = target
    mininet_ip_addresses = re.findall(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', nmap_output)
    cyborg_ip_addresses = [mapper.mininet_ip_to_cyborg_ip_map[ip] for ip in mininet_ip_addresses if ip in mapper.mininet_ip_to_cyborg_ip_map]
    res[subnet] = cyborg_ip_addresses
    return res
    
def parse_nmap_port_scan(nmap_output, target, mapper) -> List:
    res = {'success': True}
    mininet_host = target
    ip = mapper.mininet_host_to_cyborg_ip_map[mininet_host]

    # Regular expression to match the port information
    port_info_regex = re.compile(r'(\d+)/(\w+)\s+open\s+(\w+)\s+(.+)')
    
    # Find all matches
    matches = port_info_regex.findall(nmap_output)
    
    # Process matches
    ports = []
    for match in matches:
        port_number, protocol, service_name, version = match
        ports.append({
            'port': port_number,
            'protocol': protocol,
            'service': service_name,
            'version': version.strip()
        })    
    res[ip] = ports    
    return res

def parse_ssh_action(ssh_action_output):
    # To-Do: The parsing logic
    pattern = r"{'success': <TrinaryEnum\.(TRUE|FALSE)"

    # Use re.search to find a match
    match = re.search(pattern, ssh_action_output)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = match.group(1) if match else None
    
    print(success_status)
    
    return Observation(True)

def parse_escalate_action(escalate_action_output, mapper):
    pass

def parse_decoy_action(decoy_action_output):
    # To-Do: The parsing logic
    pattern = r"{'success': <TrinaryEnum\.(TRUE|FALSE)"

    # Use re.search to find a match
    match = re.search(pattern, decoy_action_output)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = match.group(1) if match else None
    
    print(success_status)
    
    return Observation(True)
    

class ResultsBundler:
    def bundle(self, target, cyborg_action, isSuccess, mininet_cli_str, mapper) -> Dict: # @ To-Do Should return Observation object instead
        if not isSuccess:
            return {'success': False} # Observation(False)
        
        if cyborg_action == "DiscoverRemoteSystems":
            return parse_nmap_network_scan(mininet_cli_str, target, mapper)
            
        elif cyborg_action == "DiscoverNetworkServices":
            return parse_nmap_port_scan(mininet_cli_str, target, mapper)

        elif cyborg_action == "ExploitRemoteService":
            return parse_ssh_action(mininet_cli_str)

        elif cyborg_action.startswith("Decoy"):
            return parse_decoy_action(mininet_cli_str)

        return {'success': True} # Observation(True)
        