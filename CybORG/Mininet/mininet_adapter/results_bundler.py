import re
import traceback 
from pprint import pprint
from typing import List, Dict
from ipaddress import IPv4Address, IPv4Network

from CybORG.Shared import Observation
from CybORG.Mininet.mininet_adapter.entity import Entity

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
    
    if not cyborg_ip_addresses:
        return Observation(False)
    
    obs = Observation()
    obs.set_success(True)
    for ip_addr in cyborg_ip_addresses:
        hostid = mapper.cyborg_ip_to_host_map[str(ip_addr)]
        if "router" in hostid:
            continue 
        obs.add_interface_info(hostid=hostid, ip_address=ip_addr, subnet=subnet)
    return obs
    
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

    obs = Observation()
    obs.set_success(True)
    for proc in processes:
        hostid = mapper.cyborg_ip_to_host_map[str(ip)]
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
    
    if not success_status:
        #@To-Do: Follow wrapper branch?? 
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
        
        attack_start_ip= 21
        
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


def parse_ssh_action(ssh_action_output, mapper) -> Observation:
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(ssh_action_output)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    obs = Observation(success_status)
    
    if not success_status:
        return obs
    
    # print(ssh_action_output)

    pattern1 = r"Local IP: (\d+\.\d+\.\d+\.\d+)\r\nLocal Port: (\d+)\r\nRemote IP: (\d+\.\d+\.\d+\.\d+)\r\nRemote Port: (\d+)\r\nPID: (\d+)"
    
    # Use re.findall() to extract the values
    matches1 = re.findall(pattern1, ssh_action_output)

    pattern2 = r"Local IP: (\d+\.\d+\.\d+\.\d+)\r\r\nLocal Port: (\d+)\r\r\nRemote IP: (\d+\.\d+\.\d+\.\d+)\r\r\nRemote Port: (\d+)\r\r\nPID: (\d+)"
    
    # Use re.findall() to extract the values
    matches2 = re.findall(pattern2, ssh_action_output)

    matches = matches1 if matches1 else matches2

    data = {}
    if matches:
        local_ip, port, remote_ip, port_for_reverse_shell, pid = matches[0]
        
        alt_name = mapper.mininet_ip_to_cyborg_ip_map.get(remote_ip)
        host_name = mapper.cyborg_ip_to_host_map.get(alt_name)
        
        remote_port_on_attacker = 4444
        attacker_node = mapper.cyborg_host_to_ip_map.get('User0')

        data[alt_name] = {
            'Processes': [
               {
                'Connections': [
                    {
                        'local_port': port_for_reverse_shell,
                        'remote_port': remote_port_on_attacker,
                        'local_address': IPv4Address(alt_name),
                        'remote_address': IPv4Address(attacker_node)
                    }
                ],
                'Process Type': 'ProcessType.REVERSE_SESSION'
               },
               {
                'Connections': [
                    {
                        'local_port': port,
                        'local_address': IPv4Address(alt_name),
                        'Status': 'ProcessState.OPEN'
                    }
                ],
                'Process Type': 'ProcessType.XXX'
               }
            ],
            'Interface': [{'IP Address': IPv4Address(alt_name)}],
            'Sessions': [{'Username':'SYSTEM', 'ID': 1, 'PID': pid, 'Type': 'SessionType.RED_REVERSE_SHELL', 'Agent': 'Red'}],
            'System info': {'Hostname': host_name, 'OSType': 'LINUX'}
        }
            
        data[attacker_node]={
            'Processes': [
                {
                'Connections': [
                    {
                        'local_port': remote_port_on_attacker,
                        'remote_port': port_for_reverse_shell,
                        'local_address': IPv4Address(attacker_node),
                        'remote_address': IPv4Address(alt_name)
                    }
                ],
                'Process Type': 'ProcessType.REVERSE_SESSION'
                }]
        }

    obs.data.update(data)

    return obs

def parse_escalate_action(escalate_action_output, mapper) -> Observation:
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

    # @To-Do
    data = {}
    if matches:
        remote_ip = matches[0]
        subnet_cidr = mapper.cyborg_ip_to_subnet[remote_ip]
        remote_hostname = mapper.cyborg_ip_to_host_map[remote_ip]
        
        enterprise_hostname = 'Enterprise1' # @To-Do bad design hard coded
        enterprise_ip = mapper.cyborg_host_to_ip_map[enterprise_hostname]
        enterprise_subnet = mapper.cyborg_ip_to_subnet[enterprise_ip]
        data[enterprise_hostname] = {'Interface': [{'IP Address': IPv4Address(enterprise_ip),
                                                    'Subnet': IPv4Network(enterprise_subnet)
                                                    }]}

        op_hostname = 'Op_Server0' # @To-Do bad design hard coded
        data[op_hostname] = {'Interface': [{'IP Address': IPv4Address(mapper.cyborg_host_to_ip_map[op_hostname])}]}

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
    
def parse_remove_action(remove_action_string: str) -> Observation:
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(remove_action_string)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    obs = Observation(success_status)
    
    return obs

def parse_decoy_action(decoy_action_output) -> Observation:
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(decoy_action_output)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    # print(f"Match is: {match} \n")
    
    return Observation(success_status)
    

class ResultsBundler(Entity):
    def bundle(self, target, cyborg_action, isSuccess, mininet_cli_str, mapper) -> Observation:
        if not isSuccess:
            return Observation(False)#.data
        
        if cyborg_action == "DiscoverRemoteSystems":
            return parse_nmap_network_scan(mininet_cli_str, target, mapper)
            
        elif cyborg_action == "DiscoverNetworkServices":
            return parse_nmap_port_scan(mininet_cli_str, target, mapper)

        elif cyborg_action == "ExploitRemoteService":            
            return parse_exploit_action(mininet_cli_str, mapper)
        
        elif cyborg_action == "PrivilegeEscalate":
            return parse_escalate_action(mininet_cli_str, mapper)

        elif cyborg_action.startswith("Decoy"):
            return parse_decoy_action(mininet_cli_str)

        elif cyborg_action == "Remove":
            return Observation(True)

        elif cyborg_action == "Restore":
            return Observation(True)
        
        elif cyborg_action == "Sleep":
            return Observation(True)
            
        return Observation(False)
        