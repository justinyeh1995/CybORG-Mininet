from copy import deepcopy
from pprint import pprint
from prettytable import PrettyTable

import networkx as nx
from networkx import connected_components

from ipaddress import IPv4Network, IPv4Address

from CybORG.Shared.Enums import TrinaryEnum
from CybORG.Agents.Wrappers.BaseWrapper import BaseWrapper

class LinkDiagramWrapper(BaseWrapper):
    def __init__(self, env: BaseWrapper = None):
        super().__init__(env)
        # self.hostname_ip_map = env.
        # self.subnet_cidr_map = env.environment_controller.state.subnet_name_to_cidr
        # self.subnets = env.environment_controller.state.subnets
        # self.hosts = env.environment_controller.state.hosts
        self.env = env
        self.cyborg = env.env.env.env.env.env
        self.link_diagram = None
        self.connected_components = None
        
        # chain of behaviour
        self.add_routers().setup_data_links()

    def add_routers(self):
        # self.env.environment_controller.state.subnets
        return self

    def setup_data_links(self):
        """Sets up the data links object for the initial state."""
        # create the link diagram
        self.link_diagram = nx.Graph()
        
        for lan_name, network in self.cyborg.environment_controller.state.subnet_name_to_cidr.items():
            router = lan_name + '_router'
            usable_ips = list(network.hosts())
            for ip in self.cyborg.environment_controller.state.subnets[network].ip_addresses:
                usable_ips.remove(ip)
            router_ip = usable_ips[0]
            self.cyborg.environment_controller.state.ip_addresses.update({IPv4Address(router_ip): router})
            self.cyborg.environment_controller.hostname_ip_map.update({router: IPv4Address(router_ip)})

        # add hosts to link diagram
        for hostname in self.cyborg.environment_controller.hostname_ip_map.keys():
            self.link_diagram.add_node(hostname)
        
        # Connect routers
        routers = [hostname for hostname in self.cyborg.environment_controller.hostname_ip_map if '_router' in hostname]
        for i in range(len(routers)):
            for j in range(i+1, len(routers)):
                self.link_diagram.add_edge(routers[i], routers[j])
        
        # Connect hosts to their respective routers
        hosts = [hostname for hostname in self.cyborg.environment_controller.hostname_ip_map if '_router' not in hostname]
        for host in hosts:
            host_ip = self.cyborg.environment_controller.hostname_ip_map[host]
            subnet = self.cyborg.environment_controller.state.get_subnet_containing_ip_address(host_ip)
            for router in routers:
                router_ip = self.cyborg.environment_controller.hostname_ip_map[router]
                if  self.cyborg.environment_controller.state.get_subnet_containing_ip_address(router_ip) == subnet:
                    self.link_diagram.add_edge(host, router)
        
        # Bad Design
        self.cyborg.environment_controller.state.link_diagram = self.link_diagram
        