import subprocess
import yaml
import collections
from ipaddress import IPv4Address, IPv4Network

class MininetAdapter:
    def __init__(self):
        self.cyborg = None
        self.ip_map = None
        self.cidr_map = None
        self.cyborg_to_mininet_name_map = None

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
            # Run the custom_topo.py script with the generated YAML file
            result = subprocess.run(
                ["sudo","python3", "mininet-files/custom_net.py", "-y", "network_topology.yaml"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Output the result of the subprocess
            print("Mininet Topology Created Successfully:")
            print(result.stdout)
            
        except subprocess.CalledProcessError as e:
            # Handle errors in the subprocess
            print("An error occurred while creating Mininet topology:")
            print(e.stderr)
            
    def reset(self):
        result = subprocess.run(
                ["sudo", "mn", "-c"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        print("Cleaned up the topology") 
        