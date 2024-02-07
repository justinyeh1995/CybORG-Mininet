import subprocess
import pexpect
import yaml
import collections
from ipaddress import IPv4Address, IPv4Network

class MininetAdapter:
    def __init__(self):
        self.cyborg = None
        self.ip_map = None
        self.cidr_map = None
        self.cyborg_to_mininet_name_map = None
        self.mininet_process = None

    def set_environment(self, cyborg):
        self.cyborg = cyborg
        self.ip_map = self.cyborg.get_ip_map()
        self.cidr_map = self.cyborg.get_cidr_map()
        self.edge_view = self.cyborg.environment_controller.state.link_diagram.edges
        self.cyborg_to_mininet_name_map = self._set_name_map()

    def _set_name_map(self):
        cyborg_to_mininet_name_map = collections.defaultdict(str)
        cnt = 1
        for lan_name, network in self.cidr_map.items():
                cyborg_to_mininet_name_map[lan_name] = f'lan{cnt}'
                cyborg_to_mininet_name_map[f'{lan_name}_router'] = f'r{cnt}'
                cnt += 1
        return cyborg_to_mininet_name_map

    def _create_yaml(self):
        try:
            # Initialize topology data
            topology_data = {
                'topo': {
                    'routers': [],
                    'lans': [],
                    'links': [],  # Placeholder, add your actual links here
                }
            }        
            # Assume the router names are suffixed with '_router'
            for name, ip in self.ip_map.items():
                if name.endswith('_router'):
                    topology_data['topo']['routers'].append({'router': self.cyborg_to_mininet_name_map[name], 'ip': str(ip)})
            
            # Create LANs based on the networks
            for lan_name, network in self.cidr_map.items():
                hosts = [name for name, ip in self.ip_map.items() if ip in network and not name.endswith('_router')]
                topology_data['topo']['lans'].append({
                    'name': self.cyborg_to_mininet_name_map[lan_name],
                    'router': self.cyborg_to_mininet_name_map[f'{lan_name}_router'],
                    'subnet': str(network),
                    'hosts': len(hosts)
                })

            # Step 1: Identify routers
            routers = {node for edge in self.edge_view for node in edge if node.endswith('_router')}

            # Step 2: Filter for router-to-router links
            router_links = [edge for edge in self.edge_view if all(node in routers for node in edge)]

            # Step 3: Structure the 'links' information
            for i, link in enumerate(router_links):
                ep1, ep2 = link
                # Assuming you have a function or a way to get the subnet for a given link
                subnet = str(IPv4Network(f'10.{50*(i+1)}.1.0/28'))  # Placeholder, replace with your subnet logic
                topology_data['topo']['links'].append({
                    'ep1-router': self.cyborg_to_mininet_name_map[ep1],
                    'ep2-router': self.cyborg_to_mininet_name_map[ep2],
                    'subnet': subnet
                })
                
            # Convert the data structure to YAML format
            yaml_content = yaml.dump(topology_data, default_flow_style=False, sort_keys=False)
            
            # Write the YAML content to a file
            with open('network_topology.yaml', 'w') as file:
                file.write(yaml_content)
            
            print("YAML file 'network_topology.yaml' created.")
            
        except Exception as e:
            print("An error occurred while creating the YAML file:")
            print(e)

    def create_mininet_topo(self):
        try:
            self._create_yaml()
            # Start the Mininet topology creation process with pexpect
            self.mininet_process = pexpect.spawn("sudo python3 mininet-files/custom_net.py -y network_topology.yaml")

            # Set a timeout for responses (adjust as needed)
            self.mininet_process.timeout = 300

            # Wait for the process to complete or for an expected output
            # You can adjust this depending on the expected output of your script
            self.mininet_process.expect("mininet>")

            # Print the output
            print("Mininet Topology Created Successfully:")
            print(self.mininet_process.before.decode())  # Decoding may be necessary

        except Exception as e:
            # Handle exceptions
            print("An error occurred while creating Mininet topology:")
            print(str(e))


    def send_mininet_command(self, command):
        if self.mininet_process and self.mininet_process.isalive():
            # Send the command to Mininet
            self.mininet_process.sendline(command)

            # Wait for the command to be processed and output to be generated
            # The specific pattern to expect might vary based on your command and Mininet's output
            self.mininet_process.expect('mininet>')

            # Retrieve and print the output of the command
            output = self.mininet_process.before.decode()
            print(output)

        else:
            print("Mininet process is not running. Please start the topology first.")

    
    def reset(self):
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
            print(cleanup_process.before.decode())

        except Exception as e:
            print("An error occurred while cleaning up the topology:")
            print(str(e))

        finally:
            if cleanup_process is not None and cleanup_process.isalive():
                cleanup_process.terminate()
        