import subprocess
import pexpect
import yaml
import collections
import pprint
import re
from ipaddress import IPv4Address, IPv4Network
from Mininet.utils.util import parse_action, get_all_matches, \
                            translate_discover_remote_systems, \
                            translate_discover_network_services, \
                            translate_exploit_network_services, \
                            translate_restore, translate_remove 
import traceback 
from typing import List, Dict
                          
                            
from Mininet.mininet_utils.custom_utils import IP_components

class MininetAdapter:
    def __init__(self):
        self.cyborg = None
        self.ip_map = None
        self.cidr_map = None
        self.edge_view = None
        
        self.cyborg_ip_to_host_map = None
        self.cyborg_host_to_ip_map = None

        self.mininet_host_to_ip_map = None
        self.mininet_ip_to_host_map = None
         
        self.cyborg_to_mininet_host_map = None
        self.mininet_to_cyborg_host_map = None
        
        self.cyborg_to_mininet_name_map = None
        
        self.routers = None
        self.topology_data = None
        
        self.mininet_process = None


    def __repr__(self) -> str:
        # Utilize pprint for prettier printing of dictionaries
        pp = pprint.PrettyPrinter(indent=4)
        return f"MininetAdapter(\n" \
               f"cyborg={self.cyborg},\n" \
               f"ip_map={pp.pformat(self.ip_map)},\n" \
               f"cidr_map={pp.pformat(self.cidr_map)},\n" \
               f"cyborg_to_mininet_name_map={pp.pformat(self.cyborg_to_mininet_name_map)},\n" \
               f"cyborg_to_mininet_host_map={pp.pformat(self.cyborg_to_mininet_host_map)},\n" \
               f"cyborg_host_to_ip_map={pp.pformat(self.cyborg_host_to_ip_map)},\n" \
               f"mininet_host_to_ip_map={pp.pformat(self.mininet_host_to_ip_map)},\n" \
               f"mininet_ip_to_host_map={pp.pformat(self.mininet_ip_to_host_map)},\n" \
               f"mininet_process={'Running' if self.mininet_process else 'Not running'},\n" \
               f"edge_view={self.edge_view},\n" \
               f"routers={self.routers},\n" \
               f")"

    
    def set_environment(self, cyborg) -> None:
        self.cyborg = cyborg
        self.ip_map = self.cyborg.get_ip_map()
        self.cidr_map = self.cyborg.get_cidr_map()
        self.cyborg_to_mininet_name_map = self._set_name_map()
        self.edge_view = self.cyborg.environment_controller.state.link_diagram.edges
        self.routers = {node for edge in self.edge_view for node in edge if node.endswith('_router')}
        self.cyborg_ip_to_host_map = {str(ip): host for host, ip in self.ip_map.items()}
        self.cyborg_host_to_ip_map = {host: str(ip) for host, ip in self.ip_map.items()}

    
    def _set_name_map(self) -> Dict:
        cyborg_to_mininet_name_map = collections.defaultdict(str)
        
        for cnt, (lan_name, network) in enumerate(self.cidr_map.items()):
                cyborg_to_mininet_name_map[lan_name] = f'lan{cnt+1}'
                cyborg_to_mininet_name_map[f'{lan_name}_router'] = f'r{cnt+1}'
            
        return cyborg_to_mininet_name_map

    
    def _get_routers_info(self) -> List:
        """
        Assume the router names are suffixed with '_router'
        """
        return [{'router': self.cyborg_to_mininet_name_map[name], 
                 'ip': str(ip)} for name, ip in self.ip_map.items() if name.endswith('_router')]

    
    def _get_lans_info(self) -> List:
        lans_info = []
        # Create LANs based on the networks
        for lan_name, network in self.cidr_map.items():
            hosts = [name for name, ip in self.ip_map.items() if ip in network and not name.endswith('_router')]
            hosts_info = { f'h{i+1}': str(self.ip_map[name]) for i, name in enumerate(hosts)}
            lans_info.append({
                'name': self.cyborg_to_mininet_name_map[lan_name],
                'router': self.cyborg_to_mininet_name_map[f'{lan_name}_router'],
                'subnet': str(network),
                'hosts': len(hosts),
                'hosts_info': hosts_info
            })
        return lans_info

    
    def _get_router2router_links(self) -> List:
        """
        Filter only for router-to-router links
        """
        return [edge for edge in self.edge_view if all(node in self.routers for node in edge)]

    
    def _get_links_info(self) -> List:
        router_links = self._get_router2router_links()
        links_info = []
        for i, link in enumerate(router_links):
            ep1, ep2 = link
            # Assuming you have a function or a way to get the subnet for a given link
            subnet = str(IPv4Network(f'10.{50*(i+1)}.1.0/28'))  # Placeholder, replace with your subnet logic # needs fix
            links_info.append({
                'ep1-router': self.cyborg_to_mininet_name_map[ep1],
                'ep2-router': self.cyborg_to_mininet_name_map[ep2],
                'subnet': subnet
            })
        return links_info

    
    def _create_yaml(self) -> None:
        """ 
        Write the topo into a yaml file
        """
        try:
            # Initialize topology data
            self.topology_data = {
                'topo': {
                    'routers': [],
                    'lans': [],
                    'links': [],  # Placeholder, add your actual links here
                }
            }        
            # Structure the 'Routers' information
            self.topology_data['topo']['routers'] = self._get_routers_info()

            # Structure the 'LANs' information
            self.topology_data['topo']['lans'] = self._get_lans_info()

            # Structure the 'Links' information
            self.topology_data['topo']['links'] = self._get_links_info()
            
            # Convert the data structure to YAML format
            yaml_content = yaml.dump(self.topology_data, default_flow_style=False, sort_keys=False)
            
            # Write the YAML content to a file
            with open('network_topology.yaml', 'w') as file:
                file.write(yaml_content)
            
            print("YAML file 'network_topology.yaml' created.")
            
        except Exception as e:
            print("An error occurred while creating the YAML file:")
            print(e)
            traceback.print_exc() 


    def update_mapping(self, output: str) -> None:
        
        matches = get_all_matches(output)
        
        # Create a dictionary to map host names to their IP addresses
        self.mininet_host_to_ip_map = {match.group('host'): match.group('ip') for match in matches}

        self.mininet_ip_to_host_map = {match.group('ip'): match.group('host') for match in matches}

        self.cyborg_to_mininet_host_map = { self.cyborg_ip_to_host_map[match.group('ip')]:
                                           self.mininet_ip_to_host_map[match.group('ip')] for match in matches}

        self.mininet_to_cyborg_host_map = { self.mininet_ip_to_host_map[match.group('ip')]:
                                   self.cyborg_ip_to_host_map[match.group('ip')] for match in matches}
        
        
    def create_mininet_topo(self) -> str:
        try:
            self._create_yaml()
            # Start the Mininet topology creation process with pexpect
            self.mininet_process = pexpect.spawn("sudo python3 Mininet/mininet_utils/custom_net.py -y network_topology.yaml")

            # Set a timeout for responses (adjust as needed)
            self.mininet_process.timeout = 300

            # Wait for the process to complete or for an expected output
            # You can adjust this depending on the expected output of your script
            self.mininet_process.expect("mininet>")

            # Print the output
            print("Mininet Topology Created Successfully:")
            output = self.mininet_process.before.decode()  # Decoding may be necessary
            # print(output)

            return output

        except Exception as e:
            # Handle exceptions
            print("An error occurred while creating Mininet topology:")
            print(str(e))
            traceback.print_exc() 
        
    
    def _parse_last_action(self, agent_type):
        action_str = self.cyborg.get_last_action(agent_type).__str__()
        
        target_host, action_type, isSucess = parse_action(self.cyborg, 
                                                action_str, 
                                                agent_type, 
                                                self.cyborg_ip_to_host_map)
        
        return self.cyborg_to_mininet_host_map.get(target_host, target_host), action_type, isSucess        
        
    
    def build_red_cmd(self, action_type, target_host) -> str:
        if action_type == "DiscoverRemoteSystems":
            print("Red Discover Remote Systems")
        elif action_type == "DiscoverNetworkServices":
            print("Red Discover Network Services")
        elif action_type == "ExploitRemoteService":
            print("Red Exploit Network Services")
        # red host is always user0
        host = self.cyborg_to_mininet_host_map["User0"]
        target = ""
        action = ""
        cmd = f'{host} {action} {target}'
        
        return cmd


    def build_blue_cmd(self, action_type, target_host) -> str:
        # blue host is undecided at the moment
        if action_type == "Remove":
            print("Blue Remove")
        elif action_type == "Restore":
            print("Blue Restore")
        elif action_type == "Monitor":
            print("Blue Monitor")
        host = ""
        action = ""
        cmd = f'{host} {action}'
        
        return cmd


    def send_mininet_command(self, agent_type) -> str:
        try:
            if self.mininet_process and self.mininet_process.isalive():
                # translate the last action of an agent to Linux command?
                target_host, action_type, isSucess = self._parse_last_action(agent_type)
                print((agent_type, action_type, isSucess, target_host))
    
                # command = self.build_red_cmd(action_type, target_host) if agent_type == "Red" else self.build_blue_cmd(action_type, target_host)
                
                # Send the command to Mininet
                # self.mininet_process.sendline(command)
                
                # self.mininet_process.sendline('lan1h1 ping -c 4 lan1h2')
                self.mininet_process.sendline('lan1h1 ls -a')
    
    
                # Wait for the command to be processed and output to be generated
                # The specific pattern to expect might vary based on your command and Mininet's output
                self.mininet_process.expect('mininet>')
    
                # Retrieve and print the output of the command
                output = self.mininet_process.before.decode()
                
                return output

            else:
                print("Mininet process is not running. Please start the topology first.")
                return "Mininet process is not running. Please start the topology first."
                
        except Exception as e:
            # Handle exceptions
            print("An error occurred while sending command to Mininet topology:")
            print(str(e))
            traceback.print_exc() 


    
    def perform_emulation(self):
        for type in ['Blue', 'Red']:
            print(type)
            output = self.send_mininet_command(type)
            # print(output)
            # do something?
    
    
    def clean(self) -> None:
        # First, ensure that the existing Mininet subprocess is terminated
        try:
            # First, check if a Mininet process is running and terminate it
            if self.mininet_process and self.mininet_process.isalive():
                self.mininet_process.terminate()
                self.mininet_process.expect(pexpect.EOF)  # Wait for termination
                print("Terminated the ongoing Mininet topology.")

            # Now, run the Mininet cleanup command
            cleanup_process = pexpect.spawn("sudo mn -c")
            cleanup_process.timeout = 60
            cleanup_process.expect(pexpect.EOF)  # Wait for the end of the process
            print("Cleaned up the topology successfully")
            # print(cleanup_process.before.decode())

        except Exception as e:
            print("An error occurred while cleaning up the topology:")
            print(str(e))

        finally:
            if cleanup_process is not None and cleanup_process.isalive():
                cleanup_process.terminate()

    
    def reset(self) -> None:
        self.clean()
        expect_str = self.create_mininet_topo()
        self.update_mapping(expect_str)


if __name__ == "__main__":
    print("Hello Mininet!")
    
        