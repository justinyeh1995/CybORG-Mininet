from dataclasses import dataclass
import random 
from typing import Dict
from ipaddress import IPv4Address

from CybORG.Mininet.mininet_adapter.utils.parse_red_results_util import  parse_nmap_network_scan, \
                                                            parse_nmap_port_scan, \
                                                            parse_exploit_action, \
                                                            parse_escalate_action \
                                                            
from CybORG.Mininet.mininet_adapter.utils.parse_blue_results_util import parse_decoy_action, \
                                                            parse_remove_action, \
                                                            parse_reset_action
                                                            
from CybORG.Shared import Observation
from CybORG.Mininet.mininet_adapter.entity import Entity
    
@dataclass
class ResultsBundler(Entity):
    last_blue_observation: Observation = None
    last_red_observation: Observation = None
    
    def bundle(self, target, cyborg_action, isSuccess, mininet_cli_str, mapper) -> Observation:
        """_summary_

        Args:
            target (_type_): this is the hostname inside mininet
            cyborg_action (_type_): _description_
            isSuccess (bool): _description_
            mininet_cli_str (_type_): _description_
            mapper (_type_): _description_

        Returns:
            Observation: _description_
        """
        if not isSuccess:
            return Observation(False)
        
        if cyborg_action == "DiscoverRemoteSystems":
            obs = parse_nmap_network_scan(mininet_cli_str, target, mapper)
            
        elif cyborg_action == "DiscoverNetworkServices":
            obs = parse_nmap_port_scan(mininet_cli_str, target, mapper)

        elif cyborg_action == "ExploitRemoteService":            
            obs = parse_exploit_action(mininet_cli_str, mapper)
        
        elif cyborg_action == "PrivilegeEscalate":
            obs = parse_escalate_action(mininet_cli_str, mapper)

        elif cyborg_action == "Impact":
            if target in self.mininet_adpator.priviledged_hosts:
                obs = Observation(True) # @To-Do
            else:
                obs = Observation(False)
            
        elif cyborg_action.startswith("Decoy"):
            obs = parse_decoy_action(mininet_cli_str)

        elif cyborg_action == "Remove":
            obs = Observation(True) # @To-Do

        elif cyborg_action == "Restore":
            obs = Observation(True) # @To-Do
        
        elif cyborg_action == "Sleep":
            obs = Observation(True)
            
        elif cyborg_action == "Analyse":
            obs = Observation(False) # @To-Do
            
        elif cyborg_action == "Reset":
            obs = parse_reset_action(mininet_cli_str)
            
        else:
            obs = Observation(False)
        
        if cyborg_action in ['DiscoverRemoteSystems', 'DiscoverNetworkServices', \
                             'ExploitRemoteService', 'PrivilegeEscalate', 'Impact']:
            self.last_red_observation = obs
        else:
            self.last_blue_observation = obs
        
        return obs
    
    
    def modify_blue_observation_by_red(self, blue_outcome: Dict, \
                                             red_outcome: Dict, \
                                             last_red_action: str, \
                                             last_red_target: str) -> Dict:
        """_summary_
        Adopted from wrappers branch - cardiff
        
        Args:
            blue_outcome (Dict): The current blue observation data
            red_outcome (Dict): The lastest red observation data
            last_red_action (str): The last red action performed
            last_red_target (str): The target of the last red action

        Returns:
            Dict: The modified blue observation data
        """
        print('-> Blue outcome:',blue_outcome)
        if last_red_action=='DiscoverNetworkServices':
            for key in red_outcome:
                if key in self.mininet_adpator.mapper.cyborg_ip_to_host_map: 
                    red_data = red_outcome[key]
                    host = self.mininet_adpator.mapper.cyborg_ip_to_host_map.get(key)
                    blue_outcome.update({host:red_data})
                    
        elif last_red_action=='ExploitRemoteService':
            #print('%%%%'*100,'In modify of exploit',)
            red_data= red_outcome[last_red_target]
            #print('red data in exploit is:',red_data)
            if red_outcome['success'].name == "TRUE":
                red_to_blue=self.convert_red_exploit_dict(red_data)
                
            elif red_outcome['success'].name in ["FALSE", "UNKNOWN"]:
            # Iterate over all the processes and their connections
                red_to_blue = {'Processes': []}
                for process in red_data['Processes']:
                    for connection in process['Connections']:
                        new_connection1 = {
                            'local_port': connection['local_port'],
                            'remote_port': connection['remote_port'],  # Assuming remote_port is a fixed value ???
                            'local_address': connection['local_address'],
                            'remote_address': connection['remote_address']} #??
                        
                        new_connection2 = {
                            'local_port': connection['local_port'],
                            'local_address': connection['local_address'],
                            'remote_address': connection['remote_address']} #??
                        
                        red_to_blue['Processes'].append({'Connections': [new_connection1]})
                        red_to_blue['Processes'].append({'Connections': [new_connection2]})
                        
            attacked_hostname = self.mininet_adpator.mapper.cyborg_ip_to_host_map.get(last_red_target)
            blue_outcome.update({attacked_hostname : red_to_blue})
        
        return blue_outcome
            
    def convert_red_exploit_dict(self, template_dict):
        """_summary_
        Adopted from wrappers branch - cardiff

        Args:
            template_dict (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Iterate over all the keys of connections to find attacker_ip
        for process in template_dict.get('Processes', []):
            for connection in process.get('Connections', []):
                if 'remote_address' in connection:
                    attacker_ip = connection['remote_address']
                    #print(f"Found remote_address: {attacker_ip}")
                else: attacker_ip=None
                
        converted_dict = {
            'Processes': [],
            'Interface': template_dict.get('Interface', []),
            'System info': {
                'Hostname': template_dict['System info']['Hostname'],
                'OSType': template_dict['System info']['OSType'],
                'OSDistribution': 'OperatingSystemDistribution.UBUNTU',
                'OSVersion': 'OperatingSystemVersion.U18_04_3',
                'Architecture': 'Architecture.x64'
            }
        }

        for process in template_dict['Processes']:
            for connection in process['Connections']:
                new_connection = {
                    'local_port': connection['local_port'],
                    'remote_port': connection.get('remote_port', random.randint(40000,50000)),
                    'local_address': connection['local_address'],
                    'remote_address': connection.get('remote_address', attacker_ip)
                }
                converted_dict['Processes'].append({'Connections': [new_connection]})

        # Adding a sample PID for demonstration
        converted_dict['Processes'][1]['PID'] = 27893

        return converted_dict


   