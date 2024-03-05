import re
import traceback 
from typing import List, Dict

def parse_nmap_network_scan(text, target) -> List:
    res = {'success': True}
    subnet = target
    ip_addresses = re.findall(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', text)
    res[subnet] = ip_addresses
    return res
    
def parse_nmap_port_scan(text, target) -> List:
    res = {'success': True}
    ip = target
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
    
class ResultsBundler:
    def bundle(self, target, cyborg_action, isSuccess, mininet_cli_str) -> Dict:
        # @To-Do
        print(isSuccess)
        if not isSuccess:
            return {'success': False}
        
        if cyborg_action == "DiscoverRemoteSystems":
            return parse_nmap_network_scan(mininet_cli_str, target)
            
        elif cyborg_action == "DiscoverRemoteSystems":
            return parse_nmap_port_scan(mininet_cli_str, target)

        return {'success': True}
        