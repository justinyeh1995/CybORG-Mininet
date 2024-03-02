import collections
from pprint import pprint
import re
import traceback 
from typing import List, Dict
from ipaddress import IPv4Address, IPv4Network
from Mininet.mininet_utils.custom_utils import IP_components
from Mininet.utils.util import parse_action, parse_mininet_ip, \
                            set_name_map, get_routers_info, get_lans_info, \
                            get_links_info, get_nats_info, \
                            build_mininet_host_to_cyborg_ip_map, build_cyborg_ip_to_mininet_host_map, \
                            generate_routing_rules, \
                            translate_discover_remote_systems, \
                            translate_discover_network_services, \
                            translate_exploit_network_services, \
                            translate_restore, translate_remove 

class CybORGMininetMapper:
    def __init__(self):
        self.cyborg_to_mininet_map = {}
        self.mininet_to_cyborg_map = {}

    def init_mapping(self, cyborg) -> None: 
        self.ip_map = cyborg.get_ip_map()
        self.cidr_map = cyborg.get_cidr_map()
        self.cyborg_ip_to_host_map = {str(ip): host for host, ip in self.ip_map.items()}
        self.cyborg_host_to_ip_map = {host: str(ip) for host, ip in self.ip_map.items()}
        
        self.cyborg_to_mininet_name_map = set_name_map(cyborg)

    
    def update_mapping(self, output: str) -> None:
        
        matches = parse_mininet_ip(output)
        
        # Create a dictionary to map host names to their IP addresses
        self.mininet_host_to_ip_map = {match.group('host'): match.group('ip') for match in matches}

        self.mininet_ip_to_host_map = {match.group('ip'): match.group('host') for match in matches}

        self.mininet_host_to_cyborg_ip_map = build_mininet_host_to_cyborg_ip_map(self.topology_data) 

        self.cyborg_ip_to_mininet_host_map = build_cyborg_ip_to_mininet_host_map(self.topology_data)

        self.cyborg_to_mininet_host_map = { 
            self.cyborg_ip_to_host_map[cyborg_ip]:self.cyborg_ip_to_mininet_host_map[cyborg_ip] 
            for cyborg_ip in self.cyborg_ip_to_host_map}

        self.mininet_to_cyborg_host_map = {
            self.cyborg_ip_to_mininet_host_map[cyborg_ip]:self.cyborg_ip_to_host_map[cyborg_ip] 
            for cyborg_ip in self.cyborg_ip_to_host_map}
        
        self.cyborg_ip_to_mininet_ip_map = { 
            self.cyborg_host_to_ip_map[cyborg_h]:self.mininet_host_to_ip_map[mininet_h] 
                for cyborg_h, mininet_h in self.cyborg_to_mininet_host_map.items()}
        
        self.mininet_ip_to_cyborg_ip_map ={
            self.mininet_host_to_ip_map[mininet_h]:self.cyborg_host_to_ip_map[cyborg_h] 
                for cyborg_h, mininet_h in self.cyborg_to_mininet_host_map.items()}

