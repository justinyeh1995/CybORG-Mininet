import logging
import re
from xml.etree import ElementTree
from typing import List, Dict, Iterator, Pattern
from ipaddress import IPv4Address, IPv4Network

from CybORG.Shared import Observation


def enum_to_boolean(enum_value):
    if enum_value == 'TRUE':
        return True
    elif enum_value == 'FALSE':
        return False
    else:
        return None
    
def parse_nmap_network_scan_v2(nmap_output, target, mapper) -> Observation:
    # Skip the first line if it's not XML
    lines = nmap_output.split('\n')
    xml_start = next(i for i, line in enumerate(lines) if line.strip().startswith('<?xml'))
    xml_content = '\n'.join(lines[xml_start:])
    
    root = ElementTree.fromstring(xml_content)
    address_element_list = root.findall(".//host/address[@addrtype='ipv4']")

    ip_address_list = []
    for address_element in address_element_list:
        ip_address_list.append(address_element.attrib.get("addr"))

    if not ip_address_list:
        return Observation(False)
    obs = Observation(True)
    ip_address_list.sort()
    for ip_addr in ip_address_list:
        hostid = mapper.cyborg_ip_to_host_map.get(str(ip_addr), "")
        if "router" in hostid:
            continue 
        obs.add_interface_info(hostid=hostid, ip_address=ip_addr, subnet=target)
    return obs

def parse_nmap_network_scan(nmap_output, target, mapper) -> Observation:
    subnet = target
    mininet_ip_addresses = re.findall(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', nmap_output)
    # cyborg_ip_addresses = [mapper.mininet_ip_to_cyborg_ip_map[ip] for ip in mininet_ip_addresses if ip in mapper.mininet_ip_to_cyborg_ip_map]
    
    if not mininet_ip_addresses:
        return Observation(False)
    
    obs = Observation()
    obs.set_success(True)
    mininet_ip_addresses.sort()
    for ip_addr in mininet_ip_addresses:
        hostid = mapper.cyborg_ip_to_host_map.get(str(ip_addr), "")
        if "router" in hostid or not hostid:
            continue 
        obs.add_interface_info(hostid=hostid, ip_address=ip_addr, subnet=subnet)
    return obs
    
def parse_nmap_port_scan(nmap_output, target, mapper) -> List:
    res = {'success': True}
    mininet_host = target
    ip = mapper.mininet_host_to_ip_map.get(mininet_host, target)

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

    obs = Observation()
    obs.set_success(True)
    for proc in processes:
        hostid = mapper.cyborg_ip_to_host_map.get(str(ip),"")
        if not hostid:
            logging.warning(f"Host ID not found for IP: {ip}")
            logging.debug(f"Mapper: \n{mapper.cyborg_ip_to_host_map}")
            continue
        obs.add_process(hostid=hostid, local_port=proc["port"], local_address=ip)
        
    return obs

def parse_exploit_action(ssh_action_output, mapper) -> Observation:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    ssh_action_output = ansi_escape.sub('', ssh_action_output)
    
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(ssh_action_output)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    obs = Observation(success_status)
    
    if not success_status or success_status == 'FALSE':
        #@To-Do: Follow wrapper branch??
        pattern_remote_ip = r"Remote IP:\s+(\d+.\d+.\d+.\d+)"
        pattern_client_port = r"Client Port:\s+(\d+)"
        match_remote_ip = re.search(pattern_remote_ip, ssh_action_output)
        match_client_port = re.search(pattern_client_port, ssh_action_output)
         
        formatted_data = {}
        
        ip = match_remote_ip.group(1)
        port = match_client_port.group(1)
        
        formatted_data['1'] ={
            'Interface': [{'IP Address': IPv4Address(ip)}]
        }
        
        formatted_data[ip]= {
            'Interface': [{'IP Address': IPv4Address(ip)}],
            'Processes': [{
                'Connections': [{
                    'Status': 'ProcessState.OPEN',
                    'local_address': IPv4Address(ip),
                    'local_port': port     #To Do: change it to Attacked port
                }],
                'Process Type': 'ProcessType.FEMITTER'
            }]
        }
        
        obs.data.update(formatted_data)
        return obs
    
    # print(ssh_action_output)

    pattern = r"(\d+\.\d+\.\d+\.\d+):(\d+)\s+(\d+\.\d+\.\d+\.\d+):(\d+).*pid=(\d+)"
    
    # Use re.findall() to extract the values
    match = re.search(pattern, ssh_action_output)

    pattern = r"Connection Key is: ([a-zA-Z0-9]*)" # parse connection key
    match_key = re.search(pattern, ssh_action_output)
    conn_key = match_key.group(1) # .groups() returns a tuple, group(1) group(0): Connection Key is: 1C01IZBLD3 group(1): 1C01IZBLD3 group(): Connection Key is: 1C01IZBLD3
    
    data = {}
    if match:
        # local_ip, port, remote_ip, port_for_reverse_shell, pid = match.groups()
        attacked_ip, attacked_port, attacker_ip, attacker_port, pid = match.groups()
        
        attacked_host_name = mapper.cyborg_ip_to_host_map.get(attacked_ip)
        
        attacker_node = attacker_ip #mapper.cyborg_host_to_ip_map.get('User0')
                
        data[attacked_ip] = {
            "Processes": [{
                "Connections": [{
                    "local_port": attacked_port,
                    "remote_port": attacker_port,
                    "local_address": IPv4Address(attacked_ip),
                    "remote_address": IPv4Address(attacker_ip)
                }],
                "Process Type": 'ProcessType.REVERSE_SESSION'
            }, 
            {
                "Connections": [{
                    "local_port": attacked_port,
                    "local_address": IPv4Address(attacked_ip),
                    "Status": 'ProcessState.OPEN'
                }],
                "Process Type": 'ProcessType.FEMITTER' #??
            }],
            "Interface": [{
                "IP Address": IPv4Address(attacked_ip)
            }],
            "Sessions": [{
                "ID": 1,
                'Username':'SYSTEM',
                "Type": 'SessionType.RED_REVERSE_SHELL',
                "Agent": "Red"
            }],
            "System info": {
                "Hostname": attacked_host_name,
                "OSType": 'OperatingSystemType.LINUX'
            }
        }
            
        data[attacker_node]={
            "Processes": [{
                "Connections": [{
                    "local_port": attacker_port,
                    "remote_port": attacked_port,
                    "local_address": IPv4Address(attacker_ip),
                    "remote_address": IPv4Address(attacked_ip)
                }],
                "Process Type": 'ProcessType.REVERSE_SESSION_HANDLER'
            }],
            "Interface": [{
                "IP Address": IPv4Address(attacker_ip)
            }]
        }
        
        data["Additional Info"]= { 
            "Connection Key": conn_key,
            "Attacked IP": attacked_ip,
            "Attacker Port": attacker_port,
        }        

    obs.data.update(data)
    
    return obs

def parse_escalate_action(escalate_action_output, mapper) -> Observation:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    escalate_action_output = ansi_escape.sub('', escalate_action_output)
    
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(escalate_action_output)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    obs = Observation(success_status)
    
    if not success_status:
        return obs
    
    # Parse Escalated Host IP
    pattern1 = r"Remote IP: (\d+\.\d+\.\d+\.\d+)"
    
    # Use re.findall() to extract the values
    matches = re.findall(pattern1, escalate_action_output)
    
    pattern_explored = r"Any new host explored\?: (\d+\.\d+\.\d+\.\d+)"
    match_explored = re.search(pattern_explored, escalate_action_output)
    explored_host_ip = match_explored.group(1) if match_explored else None
        
    data = {}
    if matches:
        remote_ip = matches[0]
        subnet_cidr = mapper.cyborg_ip_to_subnet[remote_ip]
        remote_hostname = mapper.cyborg_ip_to_host_map[remote_ip]
        
        if explored_host_ip:    
            explored_host_name = mapper.cyborg_ip_to_host_map.get(explored_host_ip, "")
            data[explored_host_name] = {     
                'Interface': [{'IP Address': IPv4Address(explored_host_ip)}]
            }

        data[remote_hostname] = {'Interface': [{'IP Address': IPv4Address(remote_ip),
                            'Interface Name': 'eth0',
                            'Subnet': IPv4Network(subnet_cidr)}],
                    'Sessions': [{'Agent': 'Red',
                            'ID': 1,
                            'Type': 'SessionType.SSH: 2',
                            'Username': 'root'}],
                    'System info': {'Hostname': remote_hostname, 'OSType': 'LINUX'}
        }
    '''
    Red Action: PrivilegeEscalate User1
    ----------------------------------------------------------------------------
    data = {'Enterprise1': {'Interface': [{'IP Address': IPv4Address('10.0.74.170')}]},
            'User1': {'Interface': [{'IP Address': IPv4Address('10.0.103.205'),
                            'Interface Name': 'eth0',
                            'Subnet': IPv4Network('10.0.103.192/28')}],
                    'Sessions': [{'Agent': 'Red',
                            'ID': 1,
                            'Type': <SessionType.SSH: 2>,
                            'Username': 'SYSTEM'}]},
            'success': <TrinaryEnum.TRUE: 1>}
    '''
    obs.data.update(data)
    return obs
    