from copy import deepcopy
from pprint import pprint
from prettytable import PrettyTable

import networkx as nx
from networkx import connected_components

from ipaddress import IPv4Network

from CybORG.Shared.Enums import TrinaryEnum
from CybORG.Agents.Wrappers.BaseWrapper import BaseWrapper

class LinkDiagramWrapper(BaseWrapper):
    def __init__(self, env: BaseWrapper = None):
        super().__init__(env)
        # self.hostname_ip_map
        # self.subnet_cidr_map
        # self.environment_controller.state.subnets
        self.env = env
        self.link_diagram = None
        self.connected_components = None
        # builder pattern
        self.add_routers().setup_data_links()

    def add_routers(self):
        # self.env.environment_controller.state.subnets
        return self

    def setup_data_links(self):
        """Sets up the data links object for the initial state."""
        # create the link diagram
        self.link_diagram = nx.Graph()
        
        for lan_name, network in self.env.environment_controller.state.subnet_name_to_cidr:
            router = lan_name + '_router'
            usable_ips = list(network.hosts)
            for ip in self.env.environment_controller.state.subnets[network].ip_addresses:
                usable_ips.remove(ip)
            router_ip = usable_ips[0]
            # self.env.environment_controller.state.hosts.update({router: Host()})
        # add hosts to link diagram
        for hostname in self.env.environment_controller.state.hosts.keys():
            self.link_diagram.add_node(hostname)
        
        # add datalink connections between hosts
        # for hostname, host_info in self.env.environment_controller.state.hosts.items():
        #     for interface in host_info.interfaces:
                # if interface.interface_type == 'wired':
                #     for data_link in interface.data_links:
                #         self.link_diagram.add_edge(hostname, data_link)
        # return self