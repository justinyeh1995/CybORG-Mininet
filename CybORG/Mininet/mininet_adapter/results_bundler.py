import re
import traceback 
from pprint import pprint
from typing import List, Dict

from CybORG.Shared import Observation
from CybORG.Emulator.Observations.Velociraptor.DiscoverNetworkServicesObservation import DiscoverNetworkServicesObservation

def enum_to_boolean(enum_value):
    if enum_value == 'TRUE':
        return True
    elif enum_value == 'FALSE':
        return False
    else:
        return None

def parse_nmap_network_scan(nmap_output, target, mapper) -> Observation:
    subnet = target
    mininet_ip_addresses = re.findall(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', nmap_output)
    cyborg_ip_addresses = [mapper.mininet_ip_to_cyborg_ip_map[ip] for ip in mininet_ip_addresses if ip in mapper.mininet_ip_to_cyborg_ip_map]

    obs = Observation()
    obs.set_success(True)
    for ip_addr in cyborg_ip_addresses:
        hostid = mapper.cyborg_ip_to_host_map[str(ip_addr)]
        obs.add_interface_info(hostid=hostid, ip_address=ip_addr, subnet=subnet)
    return obs#.data
    
def parse_nmap_port_scan(nmap_output, target, mapper) -> List:
    res = {'success': True}
    mininet_host = target
    ip = mapper.mininet_host_to_cyborg_ip_map[mininet_host]

    # Regular expression to match the port information
    port_info_regex = re.compile(r'(\d+)/(\w+)\s+open\s+(\w+)\s+(.+)')
    
    # Find all matches
    matches = port_info_regex.findall(nmap_output)
    
    # Process matches
    processes = []
    for match in matches:
        port_number, protocol, service_name, version = match
        processes.append({
            'port': port_number,
            'protocol': protocol,
            'service': service_name,
            'version': version.strip()
        })    
    res[ip] = processes

    obs = Observation()
    obs.set_success(True)
    for proc in processes:
        hostid = mapper.cyborg_ip_to_host_map[str(ip)]
        obs.add_process(hostid=hostid, local_port=proc["port"], local_address=ip)
    return obs#.data

def parse_ssh_action(ssh_action_output) -> Observation:
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(ssh_action_output)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    print(f"Match is: {match} \n")
    
    return Observation(success_status)#.data

def parse_escalate_action(escalate_action_output, mapper) -> Observation:
    return Observation(False)#.data

def parse_decoy_action(decoy_action_output) -> Observation:
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(decoy_action_output)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    print(f"Match is: {match} \n")
    
    return Observation(success_status)#.data
    

class ResultsBundler:
    def bundle(self, target, cyborg_action, isSuccess, mininet_cli_str, mapper) -> Observation: # @ To-Do Should return Observation object instead
        if not isSuccess:
            return Observation(False)#.data
        
        if cyborg_action == "DiscoverRemoteSystems":
            return parse_nmap_network_scan(mininet_cli_str, target, mapper)
            
        elif cyborg_action == "DiscoverNetworkServices":
            return parse_nmap_port_scan(mininet_cli_str, target, mapper)

        elif cyborg_action == "ExploitRemoteService":
            return parse_ssh_action(mininet_cli_str)

        elif cyborg_action.startswith("Decoy"):
            return parse_decoy_action(mininet_cli_str)

        return Observation(False)#.data
        